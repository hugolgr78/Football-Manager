import os
import re
import csv
import time
import logging
import unicodedata
import argparse
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from pathlib import Path

import requests
from bs4 import BeautifulSoup

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------
OUTPUT_DIR = Path("machine_learning")
OUTPUT_FILE = OUTPUT_DIR / "players.csv"
SOFIFA_LISTING_URL = "https://sofifa.com/?r=260001&set=true&offset=0"

# sofifa version code = 2-digit FIFA year + 4-digit roster-set number.
# Your example (r=120002) uses set "0002", matching the Kaggle sample URLs
# seen earlier (e.g. .../150002/ for FIFA15) - so that's the default here.
# CHECK THIS: browse https://sofifa.com/players once in a browser and look
# at the version dropdown to confirm which set number you actually want per
# year, and how high the year suffix currently goes (branding moved to
# "EA Sports FC" in 2023, but sofifa's own version numbering may have kept
# incrementing - verify the top of the range before running the full list).
SET_NUMBER = "0002"
SEASON_YEAR_SUFFIXES = list(range(12, 27))  # FIFA12 .. FIFA26 - EDIT AS NEEDED

PLAYERS_PER_PAGE = 60
REQUEST_DELAY = 1.5
MAX_PAGES_SAFETY = 500  # hard stop in case total-count parsing fails
DEFAULT_THREADS = 22

SOFIFA_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://sofifa.com/",
}

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)


def log_error(msg):
    with open("errors.txt", "a") as f:
        f.write(msg + "\n")


# ---------------------------------------------------------------------------
# Canonical attribute keys <- accepted label spellings (lowercased)
# ---------------------------------------------------------------------------
ATTRIBUTE_ALIASES = {
    "gk_diving": ["gk diving"],
    "gk_handling": ["gk handling"],
    "gk_kicking": ["gk kicking"],
    "gk_positioning": ["gk positioning"],
    "gk_reflexes": ["gk reflexes"],

    "acceleration": ["acceleration"],
    "agility": ["agility"],
    "balance": ["balance"],
    "jumping": ["jumping"],
    "reactions": ["reactions"],
    "sprint_speed": ["sprint speed"],
    "stamina": ["stamina"],
    "strength": ["strength"],

    "aggression": ["aggression"],
    "attack_position": ["attack position", "attacking position", "positioning"],
    "composure": ["composure"],
    "interceptions": ["interceptions"],
    "vision": ["vision"],

    "ball_control": ["ball control"],
    "crossing": ["crossing"],
    "curve": ["curve"],
    "dribbling": ["dribbling"],
    "free_kick": ["free kick accuracy", "fk accuracy"],
    "finishing": ["finishing"],
    "heading": ["heading accuracy"],
    "long_passing": ["long passing"],
    "long_shots": ["long shots"],
    "penalty": ["penalties"],
    "marking": ["marking", "marking awareness", "def. awareness", "defensive awareness"],
    "short_passing": ["short passing"],
    "shot_power": ["shot power"],
    "tackling_slide": ["sliding tackle"],
    "tackling_stand": ["standing tackle"],
    "volleys": ["volleys"],
}
# label (lowercased) -> canonical key, built once
LABEL_TO_KEY = {
    alias: key
    for key, aliases in ATTRIBUTE_ALIASES.items()
    for alias in aliases
}

IDENTITY_FIELDS = [
    "sofifa_id", "player_url", "season_version",
    "name", "normalized_name",
    "club", "age", "nationality", "preferred_positions",
    "overall", "potential", "is_keeper",
]
OUTPUT_FIELDS = IDENTITY_FIELDS + list(ATTRIBUTE_ALIASES.keys())


def normalize_name(name):
    """Lowercase, strip accents/diacritics, collapse whitespace - makes
    later exact/substring matching against transfermarkt names far easier."""
    if not name:
        return ""
    decomposed = unicodedata.normalize("NFKD", name)
    ascii_only = decomposed.encode("ascii", "ignore").decode("ascii")
    ascii_only = re.sub(r"[^a-z0-9\s]", "", ascii_only.lower())
    return re.sub(r"\s+", " ", ascii_only).strip()


def fetch(url, retries=3, delay=2):
    last_exc = None
    for attempt in range(retries):
        try:
            resp = requests.get(url, headers=SOFIFA_HEADERS, timeout=20)
            resp.raise_for_status()
            return BeautifulSoup(resp.text, "html.parser")
        except requests.RequestException as exc:
            last_exc = exc
            if attempt < retries - 1:
                time.sleep(delay)
    log.warning(f"Failed to fetch {url}: {last_exc}")
    return None


def render_counter(current, total=None):
    if total:
        sys.stdout.write(f"\rCurrent progress: {current}/{total}")
    else:
        sys.stdout.write(f"\rCurrent progress: {current}")
    sys.stdout.flush()


def finish_counter():
    sys.stdout.write("\n")
    sys.stdout.flush()


def update_query_param(url, key, value):
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    params[key] = [str(value)]
    return urlunparse(parsed._replace(query=urlencode(params, doseq=True)))


def chunk_list(lst, n):
    """Split lst into n contiguous, near-equal chunks (last chunks may get
    one extra item). E.g. chunk_list(list(range(50)), 10) -> 10 chunks of 5."""
    n = max(1, min(n, len(lst))) if lst else 0
    if n == 0:
        return []
    k, m = divmod(len(lst), n)
    return [lst[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n)]


def extract_version_from_url(url):
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    r_value = params.get("r", [""])[0]
    if re.fullmatch(r"\d{6}", r_value):
        return r_value

    match = re.search(r"/player/\d+/[^/?#]+/(\d{6})/", url)
    if match:
        return match.group(1)

    return ""


def extract_player_links(listing_soup):
    """Return [(sofifa_id, slug), ...] for every player row on a listing page."""
    links = []
    seen = set()
    for a in listing_soup.select('a[href^="/player/"]'):
        m = re.search(r"/player/(\d+)/([^/?#]+)", a.get("href", ""))
        if not m:
            continue
        pid, slug = m.group(1), m.group(2)
        if pid not in seen:
            seen.add(pid)
            links.append((pid, slug))
    return links


def parse_total_count(listing_soup):
    """Try to parse 'Showing X to Y of Z' style text to know when to stop paging."""
    text = listing_soup.get_text()
    m = re.search(r"of\s+([\d,]+)", text)
    if not m:
        return None
    try:
        return int(m.group(1).replace(",", ""))
    except ValueError:
        return None


def scrape_player_profile(url):
    soup = fetch(url)
    if soup is None:
        return None

    def t(tag):
        return tag.get_text(strip=True) if tag else ""

    data = {}

    # ── Names ────────────────────────────────────────────────────────────
    h1s = soup.select("h1")
    data["name"] = t(h1s[0]) if h1s else ""
    data["normalized_name"] = normalize_name(data["name"])

    # ── Age ──────────────────────────────────────────────────────────────
    age_m = re.search(r"(\d+)y\.o\.", soup.get_text())
    data["age"] = age_m.group(1) if age_m else ""

    # ── Nationality ──────────────────────────────────────────────────────
    profile_paragraph = soup.select_one("div.profile p")
    nat_link = profile_paragraph.select_one('a[href^="/players?na="]') if profile_paragraph else None
    nat_img = nat_link.find("img") if nat_link else None
    data["nationality"] = nat_img.get("title", "").strip() if nat_img else ""

    # ── Overall / Potential ──────────────────────────────────────────────
    em_tags = soup.select("div.meta span em, p.meta em, .player em")
    nums = [t(e) for e in em_tags if t(e).isdigit()]
    if not nums:
        ov_m = re.search(r"(\d{2})\s+Overall rating", soup.get_text())
        pt_m = re.search(r"(\d{2})\s+Potential", soup.get_text())
        data["overall"] = ov_m.group(1) if ov_m else ""
        data["potential"] = pt_m.group(1) if pt_m else ""
    else:
        data["overall"] = nums[0]
        data["potential"] = nums[1] if len(nums) > 1 else ""

    # ── Club ─────────────────────────────────────────────────────────────
    club_link = soup.find("a", href=re.compile(r"/team/\d+/"))
    data["club"] = t(club_link)

    # ── Preferred positions ─────────────────────────────────────────────
    bp_m = re.search(r"Best position\s+([A-Z]+)", soup.get_text())
    data["preferred_positions"] = bp_m.group(1) if bp_m else ""
    data["is_keeper"] = "GK" in data["preferred_positions"].upper()

    # ── Attributes: capture every label/value pair, then alias-map them ──
    for col in ATTRIBUTE_ALIASES:
        data[col] = "0"

    for block in soup.select("div.grid.attribute p"):
        value_tag = block.find("em")
        if not value_tag:
            continue
        value_text = t(value_tag)
        if not value_text.isdigit():
            value_text = value_tag.get("title", "").strip()
        if not value_text.isdigit():
            continue

        label_tag = block.find("span", attrs={"data-tippy-right-start": True})
        label = t(label_tag).strip().lower()
        if not label:
            continue

        canonical_key = LABEL_TO_KEY.get(label)
        if canonical_key:
            data[canonical_key] = value_text

    return data


def append_row(path, row):
    write_header = not path.exists() or path.stat().st_size == 0
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_FIELDS, extrasaction="ignore")
        if write_header:
            writer.writeheader()
        writer.writerow(row)


def load_existing_ids(path):
    if not path.exists():
        return set()
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return {
            f"{(row.get('season_version', '') or '')[:2]}:{row.get('sofifa_id', '')}"
            for row in reader
            if row.get("sofifa_id") and row.get("season_version")
        }


def scrape_page_range(version, season_suffix, page_offsets, existing_ids, ids_lock,
                       output_path, delay, max_players, counter_state, counter_lock, stop_event):
    """Worker: sequentially scrape a contiguous set of listing pages (given as
    a list of offsets) and every player found on them. Safe to run in
    parallel with other calls of this function against the SAME shared
    existing_ids/counter_state, as long as each call gets a disjoint set of
    page_offsets (which is how scrape_players_from_listing_url splits them)."""
    for offset in page_offsets:
        if stop_event.is_set():
            return

        page_url = f"https://sofifa.com/?r={version}&set=true&offset={offset}"
        soup = fetch(page_url)
        if soup is None:
            log_error(f"Failed to fetch listing page: {page_url}")
            continue

        player_links = extract_player_links(soup)

        for pid, slug in player_links:
            if stop_event.is_set():
                return

            row_key = f"{season_suffix}:{pid}"
            with ids_lock:
                if row_key in existing_ids:
                    continue
                existing_ids.add(row_key)  # reserve now so no other thread re-scrapes it

            profile_url = f"https://sofifa.com/player/{pid}/{slug}/{version}/"
            time.sleep(delay)
            data = scrape_player_profile(profile_url)

            if data is None:
                log_error(f"Failed to scrape player {pid} ({profile_url})")
                continue

            data["sofifa_id"] = pid
            data["player_url"] = profile_url
            data["season_version"] = season_suffix

            with ids_lock:
                append_row(output_path, data)

            with counter_lock:
                counter_state["count"] += 1
                render_counter(counter_state["count"], max_players)
                if max_players is not None and counter_state["count"] >= max_players:
                    stop_event.set()
                    return


def scrape_players_from_listing_url(listing_url, delay=REQUEST_DELAY, max_players=None, threads=DEFAULT_THREADS, player_link=None):
    """
    NOTE on max_players + threads: with threads > 1, max_players is an
    approximate/soft cap, not exact. Several threads can already be
    mid-request when the shared counter hits the limit, so you may end up
    with a handful more rows than requested (up to roughly `threads` extra).
    For an exact small test run (e.g. "just scrape 5 players"), use
    threads=1; use threads>1 once you're scraping for real and an
    approximate cap doesn't matter.
    """

    output_path = OUTPUT_FILE
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if player_link:
        profile_url = str(player_link)
        m = re.search(r"/player/(\d+)", profile_url)
        pid = m.group(1) if m else str(player_link)

        # Try to extract a 6-digit SoFIFA version code from the URL itself
        ver_m = re.search(r"/player/\d+/[^/?#]+/(\d{6})/?$", profile_url)
        if not ver_m:
            ver_m = re.search(r"(\d{6})/?$", profile_url)

        version = ver_m.group(1) if ver_m else None

        # If not found in the URL, try to find the version code in links on the profile page
        if not version:
            soup = fetch(profile_url)
            if soup:
                for a in soup.find_all("a", href=True):
                    m2 = re.search(r"/player/\d+/[^/?#]+/(\d{6})/", a["href"])
                    if m2:
                        version = m2.group(1)
                        break

        season_suffix = version[:2] if version else ""

        data = scrape_player_profile(profile_url)
        if data is None:
            log_error(f"Failed to scrape player {pid} ({profile_url})")
            return

        data["sofifa_id"] = pid
        data["player_url"] = profile_url
        data["season_version"] = season_suffix

        append_row(output_path, data)
        log.info(f"Added player {pid} to {output_path}; exiting.")
        sys.exit(0)

    # Determine SoFIFA version / season now (used for single-player mode)
    version = extract_version_from_url(listing_url)
    if not version:
        raise ValueError(f"Could not detect a SoFIFA version from URL: {listing_url}")
    season_suffix = version[:2]

    existing_ids = load_existing_ids(output_path)
    log.info(f"[season {season_suffix}] {len(existing_ids)} players already scraped")

    parsed = urlparse(listing_url)
    params = parse_qs(parsed.query)
    start_offset = int(params.get("offset", [0])[0] or 0)

    # Discover how many listing pages exist by paging through them (cheap -
    # these are just the 60-per-page listing pages, no profile scraping yet)
    # until an empty page shows up. This avoids relying on parsing sofifa's
    # "Showing X of Y" text, which may not match the page's actual wording.
    log.info(f"[season {season_suffix}] discovering pages, starting at offset {start_offset}...")
    page_offsets = []
    offset = start_offset
    page_num = 0
    while page_num < MAX_PAGES_SAFETY:
        page_url = f"https://sofifa.com/?r={version}&set=true&offset={offset}"
        soup = fetch(page_url)
        if soup is None:
            log_error(f"Failed to fetch listing page during discovery: {page_url}")
            break
        if not extract_player_links(soup):
            break
        page_offsets.append(offset)
        offset += PLAYERS_PER_PAGE
        page_num += 1
        time.sleep(delay)

    if not page_offsets:
        log.warning(f"[season {season_suffix}] no player pages found starting at offset {start_offset}")
        return

    log.info(f"[season {season_suffix}] found {len(page_offsets)} pages "
              f"(offsets {page_offsets[0]}-{page_offsets[-1]})")

    ids_lock = threading.Lock()
    counter_lock = threading.Lock()
    stop_event = threading.Event()
    counter_state = {"count": 0}

    render_counter(0, max_players)

    try:
        if threads > 1:
            chunks = [c for c in chunk_list(page_offsets, threads) if c]
            log.info(f"[season {season_suffix}] {len(page_offsets)} pages split across {len(chunks)} threads")
            with ThreadPoolExecutor(max_workers=len(chunks)) as executor:
                futures = [
                    executor.submit(
                        scrape_page_range, version, season_suffix, chunk, existing_ids, ids_lock,
                        output_path, delay, max_players, counter_state, counter_lock, stop_event,
                    )
                    for chunk in chunks
                ]
                for future in as_completed(futures):
                    future.result()  # re-raise any worker exception
        else:
            scrape_page_range(
                version, season_suffix, page_offsets, existing_ids, ids_lock,
                output_path, delay, max_players, counter_state, counter_lock, stop_event,
            )
    finally:
        finish_counter()

    log.info(f"[season {season_suffix}] done - {counter_state['count']} new players added to {output_path}")


def scrape_season(year_suffix, set_number=SET_NUMBER, delay=REQUEST_DELAY, max_players=None, threads=DEFAULT_THREADS):
    version = f"{year_suffix:02d}{set_number}"
    listing_url = f"https://sofifa.com/?r={version}&set=true&offset=0"
    scrape_players_from_listing_url(listing_url, delay=delay, max_players=max_players, threads=threads)


def scrape_all_seasons(year_suffixes=SEASON_YEAR_SUFFIXES, threads=DEFAULT_THREADS):
    for year_suffix in year_suffixes:
        try:
            scrape_season(year_suffix, threads=threads)
        except KeyboardInterrupt:
            print("\nInterrupted - progress so far is already saved (output written incrementally).")
            raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--url",
        default=SOFIFA_LISTING_URL,
        help="SoFIFA players listing URL to scrape, for example https://sofifa.com/?r=120002&set=true",
    )
    parser.add_argument(
        "--max-players",
        type=int,
        default=None,  # Change this to a player cap (like 5) for testing.
        help="Optional limit for test runs; leave unset to scrape everything",
    )
    parser.add_argument(
        "--threads",
        type=int,
        default=DEFAULT_THREADS,
        help="Number of pages to scrape in parallel.",
    )
    parser.add_argument(
        "--player",
        default=None,
        help="Player link to scrape individually.",
    )
    args = parser.parse_args()

    try:
        scrape_players_from_listing_url(args.url, max_players=args.max_players, threads=args.threads, player_link=args.player)
    except KeyboardInterrupt:
        print("\nInterrupted. Rows already written stay in machine_learning/players.csv.") 