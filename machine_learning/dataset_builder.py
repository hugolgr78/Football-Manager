# Plan:
# For each game in the games-transfermarkt csv (SKIP NATIONAL TEAM GAMES, THEY MAKE UP .7% OF THE CSV), get the url and scrape transfermartk for the lineups as before
# For each player, mark if they are a keeper (first position in returned lineup per side) and check if they exist in the players csv for the current season.
# If yes, find them and add attributes
# If no, use google search library to search the player name + club + sofifa + season
# Check: first URL is Sofifa, and in English and on the correct page (with the attributes)
# Scrape the first url for the attributes as before and add them to the dataset (id, name, club, season and attributes)
# Add new game to the final_dataset.
# All games that are added should be removed from the dataset and when pressing Control+C, the games dataset should be replaced by the new one, made up of all games not done yet with the ones that gave an error.

import os, time, requests, re, sys, csv
from bs4 import BeautifulSoup
# import googlesearch
# from googlesearch import search 
from pathlib import Path
from duckduckgo_search import DDGS
from difflib import SequenceMatcher

KEEPER_MAP = {
    "gk_diving": "GK diving",
    "gk_reflexes": "GK reflexes",
    "gk_handling": "GK handling",
    "gk_kicking": "GK kicking",
}

MENTAL_MAP = {
    "composure": "Composure",
    "stamina": "Stamina",
    "pace": "Sprint speed",
    "jumping": "Jumping",
    "strength": "Strength",
    "aggression": "Aggression",
    "acceleration": "Acceleration",
    "balance": "Balance",
}

OUTFIELD_MAP = {
    "crossing": "Crossing",
    "dribbling": "Dribbling",
    "finishing": "Finishing",
    "free_kick": "Free kick accuracy",
    "heading": "Heading accuracy",
    "long_shots": "Long shots",
    "marking": "Marking",
    "passing": "Short passing",
    "penalty": "Penalties",
    "positioning": "Positioning",
    "tackling_stand": "Standing tackle",
    "tackling_slide": "Sliding tackle",
    "vision": "Vision"
}

USER_KEEPER_ATTRS = KEEPER_MAP.keys()
USER_MENTAL_ATTRS = MENTAL_MAP.keys()
USER_OUTFIELD_ATTRS = OUTFIELD_MAP.keys()

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

POS_LABELS = [
    "CAM", "CB", "CDM", "CF", "CM",
    "LAM", "LB", "LCB", "LCM", "LDM", "LF", "LM", "LS", "LW", "LWB",
    "RAM", "RB", "RCB", "RCM", "RDM", "RF", "RM", "RS", "RW", "RWB", "ST",
]

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

COLUMNS = [
    "Crossing",
    "Finishing",
    "Heading accuracy",
    "Short passing",
    "Volleys",
    "Dribbling",
    "Curve",
    "FK Accuracy",
    "Long passing",
    "Ball control",
    "Acceleration",
    "Sprint speed",
    "Agility",
    "Reactions",
    "Balance",
    "Shot power",
    "Jumping",
    "Stamina",
    "Strength",
    "Long shots",
    "Aggression",
    "Interceptions",
    "Attack position",
    "Vision",
    "Penalties"
    "Composure",
    "Marking",
    "Standing tackle",
    "Sliding tackle",
    "GK Diving",
    "GK Handling",
    "GK Kicking",
    "GK Positioning",
    "GK Reflexes"
]
INDEX_COLUMN = COLUMNS[0]

def load_columns(csv_path):
    path = Path(csv_path)
    if path.exists():
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            headers = next(reader, None)
            if headers:
                return headers
    return DEFAULT_COLUMNS

def log_error(msg):
    with open("errors.txt", "a") as f:
        f.write(msg + "\n")

class DatasetBuilder:
    def __init__(self, games_csv_path, players_csv_path, output_path):
        self.games_path = games_csv_path
        self.players_path = players_csv_path
        self.output_path = output_path
        self.rows_to_add = []
        self.rows_added = 0
        self.delay = 1.5
        self.error_game_ids = []          # game IDs that failed during processing
        self.processed_game_ids = set()   # game IDs successfully completed
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "en-GB,en;q=0.9",
        }

    def process_games(self):
        # For each row in the games dataset, get the season and the URL.
        # Then call scrape_lineup with the URL.
        # Lineup returned -> call build_match_row
        # Row finished -> Add to self.rows_to_add and update progress

        with open(self.games_path, newline = "", encoding = "utf-8") as f:
            reader = csv.DictReader(f)
            all_rows = list(reader)

        # Filter out national-team games upfront (~0.7% of the dataset)
        club_rows = [r for r in all_rows if r.get("competition_type", "").strip() != "national_team_competition"]
        total = len(club_rows)

        print(f"Processing {total} club games (national-team games skipped).")

        try:
            for idx, row in enumerate(club_rows, start=1):
                game_id   = row["game_id"].strip()
                season    = row["season"].strip()
                url       = row["url"].strip()
                home_team = row["home_club_name"].strip()
                away_team = row["away_club_name"].strip()
                score     = f"{row['home_club_goals'].strip()}:{row['away_club_goals'].strip()}"

                self.print_progress(idx, total, prefix = "Games", suffix = f"{home_team} vs {away_team}")

                lineup = self.scrape_lineup(url)
                if lineup is None:
                    log_error(f"[{game_id}] Failed to scrape lineup: {url}")
                    self.error_game_ids.append(game_id)
                    continue

                match_row = self.build_match_row(
                    lineup["home"], lineup["away"],
                    home_team, away_team,
                    score, season,
                )
                if match_row is None:
                    log_error(f"[{game_id}] Failed to build match row: {home_team} vs {away_team}")
                    self.error_game_ids.append(game_id)
                    continue

                self.rows_to_add.append(match_row)
                self.processed_game_ids.add(game_id)
                self.rows_added += 1

                # Flush to disk periodically (every 10 games) to reduce data loss on crash
                if self.rows_added % 10 == 0:
                    self._flush_output()

        except KeyboardInterrupt:
            print("\nInterrupted — saving progress…")
            self.exit_()
            sys.exit(0)

        # Final flush
        self._flush_output()
        self.exit_()
        print(f"\nDone. {self.rows_added} games added; {len(self.error_game_ids)} errors.")

    def _flush_output(self):
        # Append any pending rows to the output CSV.

        if not self.rows_to_add:
            return
        path = Path(self.output_path)
        write_header = not path.exists() or path.stat().st_size == 0
        with open(path, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if write_header:
                writer.writerow(["score"])   # extend with real column names if needed
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
                        lineups[side].append(p_name)

                # Fallback: formation-player-list-tabel (Stoke-style — graphic has no player links)
                if len(lineups[side]) < 11:
                    lineups[side] = []
                    table = container.find('table', class_ = 'formation-player-list-tabel')
                    if table:
                        for a in table.find_all('a', href = re.compile(r'/profil/spieler/\d+')):
                            title = a.get('title', '').strip()
                            if title:
                                lineups[side].append(title)
                            if len(lineups[side]) == 11:
                                break

            if len(lineups['home']) != 11 or len(lineups['away']) != 11:
                log_error(f"Not enough players found for lineup: {len(lineups['home'])}, {len(lineups['away'])}.")
                return None
            return lineups
        except: return None

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

    def build_match_row(self, home_lineup, away_lineup, home_team, away_team, score, season):
        row = []
        for lineup, team_name in [(home_lineup, home_team), (away_lineup, away_team)]:
            players_data = []
            for p_name in lineup:
                p_attr = self.get_player_attributes(p_name, team_name, season)
                if not p_attr: return None
                players_data.append(p_attr)
            
            keepers = [p for p in players_data if p['is_keeper']]
            outfield = [p for p in players_data if not p['is_keeper']]
            
            if len(keepers) != 1 or len(outfield) != 10:
                log_error(f"\nKeepers & outfield error for **{team_name}** in {home_team} vs {away_team}: Numbers: {len(keepers)} and {len(outfield)}.")
                return None

            for k in keepers:
                for attr in USER_KEEPER_ATTRS: row.append(k[attr])
                for attr in USER_MENTAL_ATTRS: row.append(k[attr])
            for o in outfield:
                for attr in USER_OUTFIELD_ATTRS: row.append(o[attr])
                for attr in USER_MENTAL_ATTRS: row.append(o[attr])

        row.append(score)
        return row
    
    def get_player_attributes(self, player_name, team_name, season, is_keeper=False):
        # Call find_player to attempt to find the player in the players.csv by finding a row
        # with the exact name, club and season.
        # If none, call find_sofifa_link.
        # Use the returned attributes to return the correct ones using the MAPS.

        raw = self.find_player(player_name, team_name, season)

        if raw is None:
            raw = self.find_sofifa_link(player_name, team_name, season)

        if raw is None:
            log_error(f"Could not find attributes for {player_name} ({team_name}, {season})")
            return None

        # Determine whether this player is a keeper from the scraped/found data.
        # The caller passes is_keeper=False by default; we refine via Preferred Positions.
        preferred_pos = str(raw.get("Preferred Positions", "")).upper()
        player_is_keeper = "GK" in preferred_pos or is_keeper

        attrs = {"is_keeper": player_is_keeper}

        # Always add mental/physical attributes
        for key, col in MENTAL_MAP.items():
            attrs[key] = raw.get(col, "")

        if player_is_keeper:
            for key, col in KEEPER_MAP.items():
                attrs[key] = raw.get(col, "")
        else:
            for key, col in OUTFIELD_MAP.items():
                attrs[key] = raw.get(col, "")

        return attrs

    def find_player(self, player_name, team_name, season):
        # Attempt to find the player in the players.csv by finding a row with the exact
        # name, club and season. Return the attributes as a dict, or None if not found.
        path = Path(self.players_path)
        if not path.exists() or path.stat().st_size == 0:
            return None

        player_name_lower = player_name.strip().lower()
        team_name_lower   = team_name.strip().lower()
        season_str        = str(season).strip()

        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                row_name   = row.get("Name",   "").strip().lower()
                row_club   = row.get("Club",   "").strip().lower()
                row_season = row.get("Season", row.get("season", "")).strip()

                if (row_name == player_name_lower
                        and row_club == team_name_lower
                        and row_season == season_str):
                    return dict(row)

        return None

    def find_sofifa_link(self, player_name, team_name, season):
        # Use google to search player_name + team_name + "sofifa" + season.
        # Check the first link is sofifa, is in English, is the correct player/season,
        # and is on the attributes page. Adjust the URL if necessary.
        # Call scrape_sofifa with the url.
        # Call add_player_to_csv to add the player to the csv.
        # Return the raw attributes dict (unfiltered by keeper/outfield).

        query = f"{player_name} {team_name} sofifa {season}"
        with DDGS() as ddgs:
            results = [r["href"] for r in ddgs.text(query, max_results=5)]

        # SoFIFA encodes the FIFA edition in a path version segment like /120001/
        # where the first two digits = FIFA year (e.g. 12 -> FIFA 12 -> season 2012)
        # and the last four digits are always 0001 for the base roster.
        # season value from the games CSV is the *start* year of the season
        # (e.g. 2012 for the 2012/13 season), which maps to FIFA 13 (season+1).
        fifa_year = (int(season)) % 100  # e.g. 2012 -> 13
        version   = f"{fifa_year:02d}0001"   # e.g. '130001'

        sofifa_url = None
        for url in results:
            if "sofifa.com" not in url:
                continue

            # Strip non-English locale prefix (e.g. /fr/, /de/)
            url = re.sub(r"sofifa\.com/[a-z]{2}/", "sofifa.com/", url)

            # Must be a player page
            m = re.search(r"sofifa\.com/player/(\d+)", url)
            if not m:
                continue

            player_id = m.group(1)

            # Extract player name slug from the URL if present, otherwise leave blank
            slug_match = re.search(rf"player/{player_id}/([^/?#]+)", url)
            slug = slug_match.group(1).rstrip('/') if slug_match else player_name.lower().replace(' ', '-')

            # Build canonical URL with the correct version path segment
            sofifa_url = f"https://sofifa.com/player/{player_id}/{slug}/{version}/"
            break

        if sofifa_url is None:
            log_error(f"No valid SoFIFA URL found for {player_name} ({team_name}, {season})")
            return None

        time.sleep(self.delay)
        data = self.scrape_sofifa(sofifa_url)

        if data is None:
            return None

        # Sanity-check: scraped name should roughly match the searched name
        scraped_name = data.get("Name", "").lower()
        if SequenceMatcher(None, scraped_name, player_name.lower()) < 0.8:
            log_error(
                f"Name mismatch for {player_name}: got '{data.get('Name')}' from {sofifa_url}"
            )
            return None

        # Persist so we don't need to scrape again
        self.add_player_to_csv(data)

        return data

    def scrape_sofifa(self, player_url):
        def fetch_page(url):
            resp = requests.get(url, headers = SOFIFA_HEADERS, timeout=20)
            resp.raise_for_status()
            return BeautifulSoup(resp.text, "html.parser")
        
        def t(tag):
            return tag.get_text(strip=True) if tag else ""

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
        
        def scrape(url):
            soup = fetch_page(url)
            data = {col: "" for col in COLUMNS}
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
                if not val_text or label not in COLUMNS:
                    continue
                attrs[label] = val_text

            for col_name in COLUMNS:
                data[col_name] = attrs.get(col_name, "")

            total = sum(int(v) for v in attrs.values() if v.isdigit())
            data["Special"] = str(total) if total else ""

            return data
        
        try:
            data = scrape(player_url)
        except requests.HTTPError as e:
            print(f"HTTP error: {e}", file=sys.stderr)
            sys.exit(1)

        return data

    def add_player_to_csv(self, data):
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

        # Add the data to the players.csv file as a new entry, incrementing the id by 1 everytime.
        path = Path(self.players_path)
        data[INDEX_COLUMN] = str(next_row_number(path))
        with open(path, "a", newline = "", encoding = "utf-8") as f:
            writer = csv.DictWriter(f, fieldnames = COLUMNS, extrasaction = "ignore")
            writer.writerow(data)

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