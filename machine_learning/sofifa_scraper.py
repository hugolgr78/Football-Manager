"""
sofifa_scraper.py
=================
Scrapes a SoFIFA player page and appends a row to an existing CSV dataset.

Set CSV_PATH and URL below, then run:
    python sofifa_scraper.py

Dependencies:
    pip install requests beautifulsoup4
"""

import csv
import re
import sys
from pathlib import Path

import requests
from bs4 import BeautifulSoup

# ── CONFIGURE THESE ───────────────────────────────────────────────────────────
CSV_PATH = Path(__file__).with_name("CompleteDataset2.csv")
URL = "https://sofifa.com/player/227936/robert-mazan/180051/"
# ─────────────────────────────────────────────────────────────────────────────

DEFAULT_COLUMNS = [
    "Unnamed: 0", "Name", "Age", "Photo", "Nationality", "Flag", "Overall", "Potential",
    "Club", "Club Logo", "Value", "Wage", "Special",
    "Acceleration", "Aggression", "Agility", "Balance", "Ball control",
    "Composure", "Crossing", "Curve", "Dribbling", "Finishing",
    "Free kick accuracy", "GK diving", "GK handling", "GK kicking",
    "GK positioning", "GK reflexes", "Heading accuracy", "Interceptions",
    "Jumping", "Long passing", "Long shots", "Marking", "Penalties",
    "Positioning", "Reactions", "Short passing", "Shot power",
    "Sliding tackle", "Sprint speed", "Stamina", "Standing tackle",
    "Strength", "Vision", "Volleys",
    "CAM", "CB", "CDM", "CF", "CM", "ID",
    "LAM", "LB", "LCB", "LCM", "LDM", "LF", "LM", "LS", "LW", "LWB",
    "Preferred Positions",
    "RAM", "RB", "RCB", "RCM", "RDM", "RF", "RM", "RS", "RW", "RWB", "ST",
]


def load_columns(csv_path):
    path = Path(csv_path)
    if path.exists():
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            headers = next(reader, None)
            if headers:
                return headers
    return DEFAULT_COLUMNS


COLUMNS = load_columns(CSV_PATH)
INDEX_COLUMN = COLUMNS[0] if COLUMNS else "Unnamed: 0"

# Map label text on page → column name in CSV
ATTR_MAP = {
    "Crossing":          "Crossing",
    "Finishing":         "Finishing",
    "Heading accuracy":  "Heading accuracy",
    "Short passing":     "Short passing",
    "Volleys":           "Volleys",
    "Dribbling":         "Dribbling",
    "Curve":             "Curve",
    "FK Accuracy":       "Free kick accuracy",
    "Long passing":      "Long passing",
    "Ball control":      "Ball control",
    "Acceleration":      "Acceleration",
    "Sprint speed":      "Sprint speed",
    "Agility":           "Agility",
    "Reactions":         "Reactions",
    "Balance":           "Balance",
    "Shot power":        "Shot power",
    "Jumping":           "Jumping",
    "Stamina":           "Stamina",
    "Strength":          "Strength",
    "Long shots":        "Long shots",
    "Aggression":        "Aggression",
    "Interceptions":     "Interceptions",
    "Attack position":   "Positioning",
    "Vision":            "Vision",
    "Penalties":         "Penalties",
    "Composure":         "Composure",
    "Marking":           "Marking",
    "Standing tackle":   "Standing tackle",
    "Sliding tackle":    "Sliding tackle",
    "GK Diving":         "GK diving",
    "GK Handling":       "GK handling",
    "GK Kicking":        "GK kicking",
    "GK Positioning":    "GK positioning",
    "GK Reflexes":       "GK reflexes",
}

POS_LABELS = [
    "CAM", "CB", "CDM", "CF", "CM",
    "LAM", "LB", "LCB", "LCM", "LDM", "LF", "LM", "LS", "LW", "LWB",
    "RAM", "RB", "RCB", "RCM", "RDM", "RF", "RM", "RS", "RW", "RWB", "ST",
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://sofifa.com/",
}


def fetch_page(url):
    resp = requests.get(url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")


def t(tag):
    return tag.get_text(strip=True) if tag else ""


def extract_player_id(url):
    m = re.search(r"/player/(\d+)/", url)
    return m.group(1) if m else ""


def extract_attribute_value(block):
    value_tag = block.find("em")
    if not value_tag:
        return "", ""

    value_text = t(value_tag)
    if not value_text.isdigit():
        value_text = value_tag.get("title", "").strip()
    if not value_text.isdigit():
        return "", ""

    label_tag = block.find("span", attrs={"data-tippy-right-start": True})
    label_text = t(label_tag)
    return value_text, label_text


def next_row_number(csv_path):
    path = Path(csv_path)
    if not path.exists():
        return 0

    last_row = None
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            if row:
                last_row = row

    if not last_row:
        return 0

    try:
        return int(last_row[0]) + 1
    except (ValueError, IndexError):
        return 0


def scrape(url):
    soup = fetch_page(url)
    data = {col: "" for col in COLUMNS}

    player_id = extract_player_id(url)
    data[INDEX_COLUMN] = ""

    # ── Name ──────────────────────────────────────────────────────────────────
    # The short name is in the first <h1>, full name in the second
    h1s = soup.select("h1")
    data["Name"] = t(h1s[0]) if h1s else ""

    # ── Photo ─────────────────────────────────────────────────────────────────
    # The current SoFIFA layout stores the player image in the profile block.
    photo = (
        soup.select_one("div.profile img[data-type='player']")
        or soup.find("img", class_="player-image")
        or soup.find("img", src=re.compile(r"/players/\d+\.png"))
    )
    data["Photo"] = (photo.get("data-src") or photo.get("src")) if photo else ""

    # ── Age ───────────────────────────────────────────────────────────────────
    # Page shows "29y.o. (Jun 1, 1988)"
    age_m = re.search(r"(\d+)y\.o\.", soup.get_text())
    data["Age"] = age_m.group(1) if age_m else ""

    # ── Nationality & Flag ────────────────────────────────────────────────────
    # The country is shown in the player profile paragraph next to the flag.
    profile_paragraph = soup.select_one("div.profile p")
    nat_link = profile_paragraph.select_one('a[href^="/players?na="]') if profile_paragraph else None
    flag_img = nat_link.find("img") if nat_link else None
    data["Nationality"] = flag_img.get("title", "").strip() if flag_img else ""
    if not flag_img:
        flag_img = soup.find("img", src=re.compile(r"/flags/\d+\.png"))
    data["Flag"] = (flag_img.get("data-src") or flag_img.get("src")) if flag_img else ""

    # ── Overall & Potential ───────────────────────────────────────────────────
    # "79 Overall rating" and "79 Potential" appear as <em> inside the meta block
    # Reliable selector: the two <em> tags inside the player meta/profile section
    em_tags = soup.select("div.meta span em, p.meta em, .player em")
    nums = [t(e) for e in em_tags if t(e).isdigit()]
    if not nums:
        # fallback: look for "XX Overall rating" and "XX Potential" in text
        ov_m = re.search(r"(\d{2})\s+Overall rating", soup.get_text())
        pt_m = re.search(r"(\d{2})\s+Potential", soup.get_text())
        data["Overall"] = ov_m.group(1) if ov_m else ""
        data["Potential"] = pt_m.group(1) if pt_m else ""
    else:
        data["Overall"] = nums[0]
        data["Potential"] = nums[1] if len(nums) > 1 else ""

    # ── Value & Wage ──────────────────────────────────────────────────────────
    # "€12.5MValue" and "€120KWage" in the page text
    val_m = re.search(r"(€[\d.,]+[KMB]?)Value", soup.get_text())
    wag_m = re.search(r"(€[\d.,]+[KMB]?)Wage", soup.get_text())
    data["Value"] = val_m.group(1) if val_m else ""
    data["Wage"] = wag_m.group(1) if wag_m else ""

    # ── Club & Club Logo ──────────────────────────────────────────────────────
    club_link = soup.find("a", href=re.compile(r"/team/\d+/"))
    data["Club"] = t(club_link)
    club_logo_img = club_link.find("img") if club_link else None
    data["Club Logo"] = (club_logo_img.get("data-src") or club_logo_img.get("src")) if club_logo_img else ""

    # ── Preferred Positions ───────────────────────────────────────────────────
    # "Best position ST" in the text; also listed under profile
    bp_m = re.search(r"Best position\s+([A-Z]+)", soup.get_text())
    data["Preferred Positions"] = bp_m.group(1) if bp_m else ""

    # ── Attributes ───────────────────────────────────────────────────────────
    # SoFIFA renders the stats inside div.grid.attribute blocks with one <p>
    # per attribute. Each block contains <em>VALUE</em> and a label span.
    attrs = {}
    for block in soup.select("div.grid.attribute p"):
        val_text, label = extract_attribute_value(block)
        if not val_text or label not in ATTR_MAP:
            continue
        attrs[ATTR_MAP[label]] = val_text

    for col_name in ATTR_MAP.values():
        data[col_name] = attrs.get(col_name, "")

    total = sum(int(v) for v in attrs.values() if v.isdigit())
    data["Special"] = str(total) if total else ""

    return data


def append_to_csv(data, csv_path):
    path = Path(csv_path)
    data[INDEX_COLUMN] = str(next_row_number(path))
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS, extrasaction="ignore")
        writer.writerow(data)
    print(f"✓ Appended '{data.get('Name', '?')}' (ID {data.get('ID', '?')}) to {csv_path}")


if __name__ == "__main__":
    print(f"Scraping: {URL}")
    try:
        data = scrape(URL)
    except requests.HTTPError as e:
        print(f"HTTP error: {e}", file=sys.stderr)
        sys.exit(1)

    print("\nExtracted fields:")
    for k, v in data.items():
        if v:
            print(f"  {k}: {v}")

    append_to_csv(data, CSV_PATH)