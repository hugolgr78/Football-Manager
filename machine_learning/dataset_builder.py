# Plan:
# Loop through every game in the games-transfermarkt.csv, and for each game, scrape the lineup on transfermartk.
# = Do not use the game if either team does not have their formations (i.e. if either formation is blank, skip)
# = If lineup cannot be scraped, skip and add the match to the errors.txt
# For each player, find them in players.csv based on season, name, club and nat  (all except season will not be exact matches, use fuzzy or sequence matcher)
# = If player cannot be found, skip and add the match and player name to the errors.txt
# For all skipped games (except formation skip), add the row to a list.
# Then add the repesctive attr (keeper or not) to the list
# Repeat for each player
# Add the formaqtion home, formation away, score home and score away at the end (score is observed data)
# Row should be keeper_1 attr, outfield_attrs, keeper_2 attr, outfield_attrs, formation_H, formation_A, score_H, score_A
# Once finished, update the csv with the skipped rows so that all that remains is the skipped games in the new csv.
#
# NOTE: players.csv (built separately by scrape_sofifa_players.py) only has name, club,
# and season_version columns to match against - no nationality. scrape_lineup (reused
# unchanged below) also only returns player names, not nationality. So matching here is
# done on name + club only, via SequenceMatcher. If you want nat-based matching too,
# scrape_lineup would need extending to pull a flag/nationality per lineup entry - let me
# know if that's wanted.

import os, time, requests, re, sys, csv
import unicodedata
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup
from pathlib import Path
from rapidfuzz import fuzz, process

# Attribute groups, in row order: GK (1st block, keeper only), mental (2nd,
# both keeper & outfield), physical (3rd, both), technical (4th, outfield
# only). Keys here match players.csv's actual column names directly, so no
# alias/translation step is needed when reading rows (unlike the old
# KEEPER_MAP/MENTAL_MAP/OUTFIELD_MAP, which mapped to Title-Case sofifa
# labels and needed a separate PLAYERS_CSV_COLUMN_ALIASES patch for 3 of
# them - not needed anymore since these are already the real column names).
GK_ALIASES = {
    "gk_diving": ["gk diving"],
    "gk_handling": ["gk handling"],
    "gk_kicking": ["gk kicking"],
    "gk_positioning": ["gk positioning"],
    "gk_reflexes": ["gk reflexes"],
}

MENTAL_ALIASES = {
    "aggression": ["aggression"],
    "attack_position": ["attack position", "attacking position", "positioning"],
    "composure": ["composure"],
    "interceptions": ["interceptions"],
    "vision": ["vision"],
}

PHYSICAL_ALIASES = {
    "acceleration": ["acceleration"],
    "agility": ["agility"],
    "balance": ["balance"],
    "jumping": ["jumping"],
    "reactions": ["reactions"],
    "sprint_speed": ["sprint speed"],
    "stamina": ["stamina"],
    "strength": ["strength"],
}

TECHNICAL_ALIASES = {
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

GK_ATTRS = list(GK_ALIASES.keys())
MENTAL_ATTRS = list(MENTAL_ALIASES.keys())
PHYSICAL_ATTRS = list(PHYSICAL_ALIASES.keys())
TECHNICAL_ATTRS = list(TECHNICAL_ALIASES.keys())

# Combined name+club match score (0-1) below which a candidate is rejected,
# for names that aren't confident enough to stand alone (see below).
NAME_MATCH_THRESHOLD = 0.72
# A name match at or above this (0-100, rapidfuzz's native scale) is accepted
# on its own, even with zero club corroboration - club data in players.csv
# can be stale around transfer windows, and a near-exact full-name match is
# already strong evidence on its own.
HIGH_CONFIDENCE_NAME_THRESHOLD = 90
# How many top name candidates (by rapidfuzz score) to pull from the full
# season pool before scoring club similarity - keeps the club-scoring step
# cheap without needing a club pre-filter that risks excluding the right row.
TOP_NAME_CANDIDATES = 5

# Base URL for resolving relative player-profile hrefs found in lineup pages.
TRANSFERMARKT_BASE = "https://www.transfermarkt.co.uk"


def normalize_name(name):
    """Lowercase, strip accents/diacritics, collapse whitespace - matches the
    normalization already used to build players.csv's `normalized_name` column,
    so comparisons here are apples-to-apples."""
    if not name:
        return ""
    decomposed = unicodedata.normalize("NFKD", name)
    ascii_only = decomposed.encode("ascii", "ignore").decode("ascii")
    ascii_only = re.sub(r"[^a-z0-9\s]", "", ascii_only.lower())
    return re.sub(r"\s+", " ", ascii_only).strip()


def log_error(msg):
    # encoding="utf-8" explicitly - without it, Windows opens this in the
    # system codepage instead of UTF-8, which breaks on accented player names.
    with open("errors.txt", "a", encoding="utf-8") as f:
        f.write(msg + "\n")


def chunk_list(lst, n):
    """Split lst into n contiguous, near-equal chunks (last chunks may get one
    extra item). E.g. chunk_list(list(range(300)), 30) -> 30 chunks of 10."""
    n = max(1, min(n, len(lst))) if lst else 0
    if n == 0:
        return []
    k, m = divmod(len(lst), n)
    return [lst[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n)]


def build_output_header():
    """Column names matching build_match_row's row layout: per side, one
    keeper block (gk + mental + physical) then ten outfield-player blocks
    (mental + physical + technical), then formations + scores."""
    header = []
    for side in ("home", "away"):
        # Keeper slot: gk (1st), mental (2nd), physical (3rd) - no technical.
        for attr in GK_ATTRS:
            header.append(f"{side}_gk_{attr}")
        for attr in MENTAL_ATTRS:
            header.append(f"{side}_gk_{attr}")
        for attr in PHYSICAL_ATTRS:
            header.append(f"{side}_gk_{attr}")
        # Outfield slots: mental (2nd), physical (3rd), technical (4th) - no gk.
        for i in range(1, 11):
            for attr in MENTAL_ATTRS:
                header.append(f"{side}_of{i}_{attr}")
            for attr in PHYSICAL_ATTRS:
                header.append(f"{side}_of{i}_{attr}")
            for attr in TECHNICAL_ATTRS:
                header.append(f"{side}_of{i}_{attr}")
    header += ["home_formation", "away_formation", "home_score", "away_score"]
    return header

class DatasetBuilder:
    def __init__(self, games_csv_path, players_csv_path, output_path):
        self.games_path = games_csv_path
        self.players_path = players_csv_path
        self.output_path = output_path
        self.rows_to_add = []
        self.rows_added = 0
        self.delay = 1.5
        self.error_game_ids = []          # game IDs that failed during processing (retried next run)
        self.processed_game_ids = set()   # game IDs done - either succeeded, or permanently skipped (formation)
        self.formation_skip_count = 0
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "en-GB,en;q=0.9",
        }

        # players.csv is loaded lazily, once, and bucketed by season_version so
        # find_player() doesn't re-scan the whole file for every single player.
        self._players_loaded = False
        self._players_by_version = {}
        # Precomputed parallel lists (same order as _players_by_version[v]) so
        # find_player doesn't rebuild a 14k-item list on every single lookup.
        self._club_names_by_version = {}
        self._name_norms_by_version = {}
        self._long_name_norms_by_version = {}
        self._players_lock = threading.Lock()  # guards the lazy-load below across threads
        # Caches find_player results - the same player/club/season combo
        # recurs across many games in a real season, so this avoids redundant
        # fuzzy searches entirely on repeat lookups. A benign race (two
        # threads computing the same miss concurrently) just means a little
        # redundant work, not incorrect results, so no lock needed here.
        self._find_player_cache = {}
        # Caches scrape_player_names results per profile_url - the fallback
        # fetch only happens on a miss, but the same player can miss across
        # many games in a season, so this avoids re-fetching their profile
        # page every time. Same benign-race reasoning as _find_player_cache.
        self._profile_name_cache = {}

        # Manual name-alias table (see name_aliases.csv / load_name_aliases)
        # for players whose transfermarkt name has nothing in common with
        # sofifa's name (nicknames, e.g. "Vitinha" vs "Vitor Machado
        # Ferreira") - fuzzy matching can't bridge that, so these are looked
        # up by exact override instead. Checked before fuzzy matching.
        self.aliases_path = "name_aliases.csv"
        self._aliases_loaded = False
        self._aliases = {}  # (normalized transfermarkt name, club lower) -> sofifa search name
        self._aliases_lock = threading.Lock()

        # Guards all shared mutable state (rows_to_add, rows_added, error/processed
        # game ids, formation_skip_count, output file writes) when running with
        # multiple threads in process_games.
        self._state_lock = threading.Lock()
        self._progress_lock = threading.Lock()
        self._stop_event = threading.Event()
        self._done_count = 0

    def process_games(self, threads=50):
        # Load every game, split into `threads` contiguous chunks, and run each
        # chunk on its own thread via _process_chunk. Each chunk handles its
        # games sequentially (formation-skip check -> scrape_lineup ->
        # build_match_row), the same logic as before - just spread across
        # threads instead of one big loop.

        with open(self.games_path, newline = "", encoding = "utf-8") as f:
            reader = csv.DictReader(f)
            all_rows = list(reader)

        # Filter out national-team games upfront (~0.7% of the dataset)
        club_rows = [r for r in all_rows if r.get("competition_type", "").strip() != "national_team_competition"]
        total = len(club_rows)

        print(f"Processing {total} club games (national-team games skipped) across up to {threads} threads.")

        chunks = [c for c in chunk_list(club_rows, threads) if c]
        self._done_count = 0

        try:
            with ThreadPoolExecutor(max_workers=len(chunks)) as executor:
                futures = [executor.submit(self._process_chunk, chunk, total) for chunk in chunks]
                for future in as_completed(futures):
                    future.result()  # re-raise any worker exception
        except KeyboardInterrupt:
            print("\nInterrupted — signalling threads to stop and saving progress…")
            self._stop_event.set()
            # ThreadPoolExecutor's context manager above already waits for
            # in-flight work to notice _stop_event and return before continuing.
            self._flush_output()
            self.exit_()
            sys.exit(0)

        # Final flush
        self._flush_output()
        self.exit_()
        print(
            f"\nDone. {self.rows_added} games added; {len(self.error_game_ids)} errors; "
            f"{self.formation_skip_count} skipped for missing formation."
        )

    def _process_chunk(self, rows, total):
        for row in rows:
            if self._stop_event.is_set():
                return

            game_id         = row["game_id"].strip()
            season          = row["season"].strip()
            url             = row["url"].strip()
            home_team       = row["home_club_name"].strip()
            away_team       = row["away_club_name"].strip()
            home_formation  = row.get("home_club_formation", "").strip()
            away_formation  = row.get("away_club_formation", "").strip()
            score_home      = row["home_club_goals"].strip()
            score_away      = row["away_club_goals"].strip()

            # Formation missing on either side -> permanently skip. Marking the
            # game_id as processed (without an error) means exit_() below drops
            # it from the games CSV for good, instead of queuing a retry.
            if not home_formation or not away_formation:
                with self._state_lock:
                    self.formation_skip_count += 1
                    self.processed_game_ids.add(game_id)
                self._tick(total, f"{home_team} vs {away_team}")
                continue

            lineup = self.scrape_lineup(url)
            if lineup is None:
                log_error(f"[{game_id}] Failed to scrape lineup: {url}")
                with self._state_lock:
                    self.error_game_ids.append(game_id)
                self._tick(total, f"{home_team} vs {away_team}")
                continue

            match_row = self.build_match_row(
                lineup["home"], lineup["away"],
                home_team, away_team,
                home_formation, away_formation,
                score_home, score_away,
                season, game_id,
            )
            if match_row is None:
                log_error(f"[{game_id}] Failed to build match row: {home_team} vs {away_team}")
                with self._state_lock:
                    self.error_game_ids.append(game_id)
                self._tick(total, f"{home_team} vs {away_team}")
                continue

            with self._state_lock:
                self.rows_to_add.append(match_row)
                self.processed_game_ids.add(game_id)
                self.rows_added += 1
                # Flush to disk periodically (every 10 games) to reduce data loss on crash
                if self.rows_added % 10 == 0:
                    self._flush_output()

            self._tick(total, f"{home_team} vs {away_team}")

    def _tick(self, total, suffix):
        with self._progress_lock:
            self._done_count += 1
            self.print_progress(self._done_count, total, prefix="Games", suffix=suffix)

    def _flush_output(self):
        # Append any pending rows to the output CSV.

        if not self.rows_to_add:
            return
        path = Path(self.output_path)
        write_header = not path.exists() or path.stat().st_size == 0
        with open(path, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if write_header:
                writer.writerow(build_output_header())
            writer.writerows(self.rows_to_add)
        self.rows_to_add = []

    def scrape_lineup(self, game_url):
        try:
            time.sleep(self.delay)
            response = self.fetch_with_retries(game_url, self.headers, timeout=30, retries=3, delay=2)
            if response.status_code != 200: return None
            soup = BeautifulSoup(response.content, 'html.parser')
            lineup_box = next((b for b in soup.find_all('div', class_ = 'box') if b.find('h2') and 'Line-Ups' in b.find('h2').text), None)
            if not lineup_box: return None

            lineups = {'home': [], 'away': []}
            team_containers = lineup_box.find_all('div', class_ = re.compile(r'large-6 columns'))
            if len(team_containers) < 2: return None

            for i, side in enumerate(['home', 'away']):
                container = team_containers[i]

                # Primary: graphic formation players (Liverpool-style)
                formation_players = container.find_all('div', class_='formation-player-container')
                for fp in formation_players:
                    player_link = fp.find('a', href = re.compile(r'/profil/spieler/\d+'))
                    if player_link:
                        pl = str(player_link)
                        r1 = pl[10:]
                        r2 = r1.split("/")[0]
                        p_name = r2.replace("-", " ")
                        href = player_link.get("href", "")
                        profile_url = TRANSFERMARKT_BASE + href if href.startswith("/") else href
                        lineups[side].append({"name": p_name, "profile_url": profile_url})

                # Fallback: formation-player-list-tabel (Stoke-style — graphic has no player links)
                if len(lineups[side]) < 11:
                    lineups[side] = []
                    table = container.find('table', class_ = 'formation-player-list-tabel')
                    if table:
                        for a in table.find_all('a', href = re.compile(r'/profil/spieler/\d+')):
                            title = a.get('title', '').strip()
                            if title:
                                href = a.get("href", "")
                                profile_url = TRANSFERMARKT_BASE + href if href.startswith("/") else href
                                lineups[side].append({"name": title, "profile_url": profile_url})
                            if len(lineups[side]) == 11:
                                break

            if len(lineups['home']) != 11 or len(lineups['away']) != 11:
                log_error(f"Not enough players found for lineup: {len(lineups['home'])}, {len(lineups['away'])}.")
                return None
            return lineups
        except: return None

    def scrape_player_names(self, profile_url):
        """
        Fetch a transfermarkt player profile page and extract alternate name
        fields ("Full name", "Name in home country") from its info-table
        blocks, for use as a fallback when the lineup's display name doesn't
        match anything in players.csv. Cached per profile_url, since the same
        player's page may otherwise be re-fetched across many games.

        Returns a dict like {"full_name": "...", "home_country_name": "..."}
        - either value may be missing/empty if that field isn't on the page.
        Returns {} on any fetch/parse failure (caller just falls through to
        treating the player as unmatched, same as before this fallback existed).
        """
        if profile_url in self._profile_name_cache:
            return self._profile_name_cache[profile_url]

        result = {}
        try:
            time.sleep(self.delay)
            response = self.fetch_with_retries(profile_url, self.headers, timeout=30, retries=3, delay=2)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                for block in soup.find_all('div', class_=re.compile(r'\binfo-table\b')):
                    label_tag = block.find('span', class_=re.compile(r'info-table__content--regular'))
                    value_tag = block.find('span', class_=re.compile(r'info-table__content--bold'))
                    if not label_tag or not value_tag:
                        continue
                    label = label_tag.get_text(strip=True).rstrip(':').strip().lower()
                    value = value_tag.get_text(strip=True)
                    if not value:
                        continue
                    if label == "full name":
                        result["full_name"] = value
                    elif label == "name in home country":
                        result["home_country_name"] = value
        except Exception as exc:
            log_error(f"Failed to fetch player profile for alternate name: {profile_url}: {exc}")
            result = {}

        self._profile_name_cache[profile_url] = result
        return result

    def fetch_with_retries(self, url, headers, timeout = 30, retries = 3, delay = 2):
        last_error = None
        for attempt in range(retries):
            try:
                return requests.get(url, headers = headers, timeout = timeout)
            except requests.exceptions.RequestException as exc:
                last_error = exc
                if attempt < retries - 1:
                    time.sleep(delay)
        raise last_error

    def build_match_row(self, home_lineup, away_lineup, home_team, away_team,
                         home_formation, away_formation, score_home, score_away,
                         season, game_id=None):
        row = []
        for lineup, team_name in [(home_lineup, home_team), (away_lineup, away_team)]:
            players_data = []
            for player in lineup:
                p_name = player["name"]
                profile_url = player.get("profile_url")
                p_attr = self.get_player_attributes(p_name, team_name, season, game_id=game_id, profile_url=profile_url)
                if not p_attr: return None
                players_data.append(p_attr)

            keepers = [p for p in players_data if p['is_keeper']]
            outfield = [p for p in players_data if not p['is_keeper']]

            if len(keepers) != 1 or len(outfield) != 10:
                log_error(f"\nKeepers & outfield error for **{team_name}** in {home_team} vs {away_team}: Numbers: {len(keepers)} and {len(outfield)}.")
                return None

            for k in keepers:
                for attr in GK_ATTRS: row.append(k[attr])
                for attr in MENTAL_ATTRS: row.append(k[attr])
                for attr in PHYSICAL_ATTRS: row.append(k[attr])
            for o in outfield:
                for attr in MENTAL_ATTRS: row.append(o[attr])
                for attr in PHYSICAL_ATTRS: row.append(o[attr])
                for attr in TECHNICAL_ATTRS: row.append(o[attr])

        row.extend([home_formation, away_formation, score_home, score_away])
        return row

    def get_player_attributes(self, player_name, team_name, season, is_keeper=False, game_id=None, profile_url=None):
        # Find the player in players.csv via fuzzy name+club match (see find_player).
        # No google/sofifa fallback - players.csv is the sole source now.

        raw = self.find_player(player_name, team_name, season)

        # If the lineup's display name didn't match anything (common for
        # nicknames, e.g. "Vitinha" vs sofifa's "Vitor Machado Ferreira"),
        # fetch the player's own transfermarkt profile page for their
        # "Full name" / "Name in home country" and retry with those - only
        # done on an actual miss, and cached per profile_url, so this doesn't
        # add cost to players who already match on their lineup name.
        used_name = player_name
        if raw is None and profile_url:
            alt_names = self.scrape_player_names(profile_url)
            for alt_name in (alt_names.get("full_name"), alt_names.get("home_country_name")):
                if not alt_name:
                    continue
                raw = self.find_player(alt_name, team_name, season)
                if raw is not None:
                    used_name = alt_name
                    break

        if raw is None:
            tag = f"[{game_id}] " if game_id else ""
            log_error(f"{tag}Could not find attributes for {player_name} ({team_name}, {season})")
            return None

        # players.csv already carries an explicit is_keeper column (from the
        # sofifa scrape); fall back to preferred_positions just in case.
        preferred_pos = str(raw.get("preferred_positions", "")).upper()
        raw_is_keeper = str(raw.get("is_keeper", "")).strip().lower() == "true"
        player_is_keeper = raw_is_keeper or "GK" in preferred_pos or is_keeper

        attrs = {"is_keeper": player_is_keeper}

        # Mental and physical attributes apply to every player, keeper or not.
        # These keys already match players.csv's actual column names directly
        # (no alias/translation step needed, unlike the old MENTAL_MAP setup).
        for key in MENTAL_ATTRS:
            attrs[key] = raw.get(key, "")
        for key in PHYSICAL_ATTRS:
            attrs[key] = raw.get(key, "")

        if player_is_keeper:
            for key in GK_ATTRS:
                attrs[key] = raw.get(key, "")
        else:
            for key in TECHNICAL_ATTRS:
                attrs[key] = raw.get(key, "")

        return attrs

    def _season_to_version_suffix(self, season):
        # season = start year of the season from games-transfermarkt.csv
        # (e.g. "2012" for the 2012/13 season). players.csv's season_version
        # is the two-digit FIFA year. Established convention from earlier in
        # this project: FIFA year = season + 1 (e.g. 2012/13 -> FIFA 13 ->
        # season_version "13"). CHECK this matches how you actually scraped
        # machine_learning players.csv - adjust here if your versions were
        # scraped under a different year convention.
        try:
            start_year = int(str(season).strip()[:4])
        except ValueError:
            return None
        return str((start_year + 1) % 100).zfill(2)

    def _ensure_players_loaded(self):
        # Load players.csv once, bucketed by season_version, so find_player()
        # below doesn't re-scan the whole file for every single lookup.
        # Double-checked locking: cheap unlocked check first (fast path once
        # loaded), then a locked, re-checked load - this was previously
        # unguarded and would race/corrupt _players_by_version when multiple
        # threads hit it for the first time simultaneously.
        if self._players_loaded:
            return

        with self._players_lock:
            if self._players_loaded:  # another thread may have loaded it while we waited
                return

            path = Path(self.players_path)
            if path.exists() and path.stat().st_size > 0:
                with open(path, newline="", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        version = row.get("season_version", "").strip().zfill(2)
                        self._players_by_version.setdefault(version, []).append(row)

                # Precompute the lowercased club / normalized-name lists once
                # per version, so find_player reuses them on every lookup
                # instead of rebuilding a 14k-item list each time. Both short
                # `name` and `long_name` are checked - sofifa's short display
                # name isn't always what you'd expect either.
                for version, rows in self._players_by_version.items():
                    self._club_names_by_version[version] = [
                        row.get("club", "").strip().lower() for row in rows
                    ]
                    self._name_norms_by_version[version] = [
                        row.get("normalized_name", "").strip() for row in rows
                    ]
                    self._long_name_norms_by_version[version] = [
                        row.get("normalized_long_name", "").strip() for row in rows
                    ]

            self._players_loaded = True

    def _ensure_aliases_loaded(self):
        # Manual overrides for names fuzzy matching can't bridge (nicknames
        # like "Vitinha" vs sofifa's "Vitor Machado Ferreira"). File format:
        # three columns, transfermarkt_name,club,sofifa_name - header row
        # required. Club is part of the key (not just for reference) so two
        # different players who happen to share a transfermarkt display name
        # don't collide. Rows with an empty sofifa_name are unresolved
        # placeholders (see review_missing_players.py) and are skipped here -
        # they don't do anything until you fill sofifa_name in yourself.
        # Missing file is fine (just means no aliases yet).
        if self._aliases_loaded:
            return

        with self._aliases_lock:
            if self._aliases_loaded:
                return

            path = Path(self.aliases_path)
            if path.exists() and path.stat().st_size > 0:
                with open(path, newline="", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        tm_name = row.get("transfermarkt_name", "").strip()
                        club = row.get("club", "").strip()
                        sofifa_name = row.get("sofifa_name", "").strip()
                        if tm_name and club and sofifa_name:
                            key = (normalize_name(tm_name), club.lower())
                            self._aliases[key] = sofifa_name

            self._aliases_loaded = True

    def find_player(self, player_name, team_name, season):
        # Find the player in players.csv: season_version must match exactly;
        # name and club are fuzzy-matched via rapidfuzz (C-implemented - far
        # faster than difflib.SequenceMatcher at this scale, which matters a
        # lot once you're running many threads over thousands of candidates).
        # NOTE: players.csv has no nationality column, and scrape_lineup (reused
        # unchanged) doesn't return nationality either - so unlike the original
        # plan comment, matching here uses name + club only, not nat.
        cache_key = (player_name, team_name, season)
        if cache_key in self._find_player_cache:
            return self._find_player_cache[cache_key]

        result = self._find_player_uncached(player_name, team_name, season)
        self._find_player_cache[cache_key] = result
        return result

    def _find_player_uncached(self, player_name, team_name, season):
        self._ensure_players_loaded()
        self._ensure_aliases_loaded()

        version_suffix = self._season_to_version_suffix(season)
        if version_suffix is None:
            return None

        candidates = self._players_by_version.get(version_suffix, [])
        if not candidates:
            return None

        name_norms = self._name_norms_by_version.get(version_suffix, [])
        long_name_norms = self._long_name_norms_by_version.get(version_suffix, [])

        # Alias override (e.g. "Vitinha" -> "Vitor Machado Ferreira") takes
        # priority - fuzzy matching can't bridge a nickname to an unrelated
        # real name, so if this transfermarkt name has a known override, use
        # that as the query instead of the original.
        query_club_lower = team_name.strip().lower()
        alias_target = self._aliases.get((normalize_name(player_name), query_club_lower))
        query_name_norm = normalize_name(alias_target if alias_target else player_name)

        # Search the FULL season pool by name directly - no club pre-filter.
        # We used to narrow by club first, but club data in players.csv can
        # be stale (a player's transfermarkt club and sofifa's snapshot club
        # disagree around transfer windows) or fuzzy-match too loosely on
        # short/generic club-name tokens (e.g. "1919", "FC"), producing
        # dozens of false-positive clubs. Either way, pre-filtering by club
        # can silently exclude the correct row before name matching even
        # runs. Full-pool search is only ~8ms even over an 18k-row season
        # (rapidfuzz's batched C scan), so there's no real speed reason to
        # pre-filter - club is used below only as a secondary confidence
        # signal, not as an elimination filter.
        short_matches = process.extract(query_name_norm, name_norms, scorer=fuzz.WRatio, limit=TOP_NAME_CANDIDATES)
        long_matches = process.extract(query_name_norm, long_name_norms, scorer=fuzz.WRatio, limit=TOP_NAME_CANDIDATES)

        best_name_score_by_row = {}
        for _, score, idx in short_matches:
            best_name_score_by_row[idx] = max(best_name_score_by_row.get(idx, 0), score)
        for _, score, idx in long_matches:
            best_name_score_by_row[idx] = max(best_name_score_by_row.get(idx, 0), score)

        if not best_name_score_by_row:
            return None

        # Among the top name candidates, accept the first one whose name
        # match is strong enough to stand alone (near-exact full name -
        # collisions this precise within one season are rare), otherwise
        # fall back to requiring club corroboration too.
        ranked = sorted(best_name_score_by_row.items(), key=lambda kv: kv[1], reverse=True)[:TOP_NAME_CANDIDATES]

        best_row = None
        best_combined = -1.0
        for idx, name_score in ranked:
            row = candidates[idx]

            if name_score >= HIGH_CONFIDENCE_NAME_THRESHOLD:
                return row  # name alone is confident enough - club may be stale, ignore it

            club_score = fuzz.WRatio(query_club_lower, row.get("club", "").strip().lower())
            combined = 0.7 * (name_score / 100.0) + 0.3 * (club_score / 100.0)
            if combined > best_combined:
                best_combined = combined
                best_row = row

        if best_row is None or best_combined < NAME_MATCH_THRESHOLD:
            return None

        return best_row

    def print_progress(self, current, total, prefix = '', suffix = '', length = 50, fill = '█'):
        percent = ("{0:.1f}").format(100 * (current / float(total)))
        filled_length = int(length * current // total)
        bar = fill * filled_length + '-' * (length - filled_length)
        sys.stdout.write(f'\r{prefix} |{bar}| {percent}% {suffix}')
        sys.stdout.flush()
        if current == total: sys.stdout.write('\n')

    def exit_(self):
        # Call this function if Control+C is pressed and reset the games_csv_path to include
        # the games that were not processed or gave an error.

        # Flush any pending successfully-built rows first
        self._flush_output()

        path = Path(self.games_path)
        if not path.exists():
            return

        # Read all original rows preserving the header
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            all_rows = list(reader)

        # Keep rows that were never processed OR that produced an error,
        # i.e. remove only the rows that were successfully completed.
        remaining = [
            row for row in all_rows
            if row.get("game_id", "").strip() not in self.processed_game_ids
               or row.get("game_id", "").strip() in self.error_game_ids
        ]

        # Overwrite the games CSV with the remaining work (header preserved)
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(remaining)

        print(
            f"Games CSV updated: {len(remaining)} rows remaining "
            f"({len(self.error_game_ids)} errors re-queued)."
        )

if __name__ == "__main__":
    games_csv_path = os.path.join(".", "machine_learning", "games-test.csv")
    players_csv_path = os.path.join(".", "machine_learning", "players.csv")
    output_path = os.path.join(".", "machine_learning", "final_dataset.csv")
    
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir): os.makedirs(output_dir)

    builder = DatasetBuilder(games_csv_path, players_csv_path, output_path)
    builder.process_games()