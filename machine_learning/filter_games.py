"""
filter_games.py

Filters games-transfermarkt.csv down to games that dataset_builder.py can
actually use, so it doesn't waste time scraping lineups for games that would
just get skipped anyway:

  1. season >= 2012 (i.e. the 2012/13 season onwards)
  2. BOTH home_club_formation and away_club_formation are present, AND each
     is a clean "x-x-x" or "x-x-x-x" string - just digits and dashes, 3 or 4
     numbers, nothing else. Formations like "4-3-3 Attacking", "4-4-2 double
     6", "3-5-2 flat", or "Starting Line-up: 4-2-3-1" are rejected - only
     plain shapes like "4-2-3-1" or "4-4-2" pass.

Output: a new CSV (same columns) with only the games that pass both checks.

Usage:
    python filter_games.py --input games-transfermarkt.csv --output games-filtered.csv
"""

import argparse
import csv
import re

MIN_SEASON = 2012

# 3 or 4 numbers (1-2 digits each) separated by single dashes, nothing else -
# fullmatch (anchored both ends) so leading/trailing text is rejected too,
# e.g. "4-3-3 Attacking" or "Starting Line-up: 4-2-3-1" both fail this.
FORMATION_PATTERN = re.compile(r"^\d{1,2}(-\d{1,2}){2,3}$")


def parse_season_start_year(season_value):
    """Games CSV's season is already a plain start year (e.g. "2012" for the
    2012/13 season) - handled directly, with a couple of tolerant fallbacks
    in case the format ever varies."""
    s = str(season_value).strip()
    if not s:
        return None

    m = re.match(r"^(\d{4})", s)
    if m:
        return int(m.group(1))

    m = re.match(r"^(\d{2})", s)
    if m:
        two = int(m.group(1))
        return 2000 + two if two < 50 else 1900 + two

    return None


def get_clean_formation(value):
    if bool(FORMATION_PATTERN.fullmatch(value.strip())):
        return value
    else:
        return value.split(" ")[0]



def filter_games(input_path, output_path, min_season=MIN_SEASON):
    kept = 0
    dropped_season = 0
    dropped_formation = 0
    total = 0

    with open(input_path, newline="", encoding="utf-8") as f_in:
        reader = csv.DictReader(f_in)
        fieldnames = reader.fieldnames

        with open(output_path, "w", newline="", encoding="utf-8") as f_out:
            writer = csv.DictWriter(f_out, fieldnames=fieldnames)
            writer.writeheader()

            for row in reader:
                total += 1

                start_year = parse_season_start_year(row.get("season", ""))
                if start_year is None or start_year < min_season:
                    dropped_season += 1
                    continue

                home_formation = row.get("home_club_formation", "").strip()
                away_formation = row.get("away_club_formation", "").strip()

                if not home_formation or not away_formation:
                    dropped_formation += 1
                    continue

                home_formation = get_clean_formation(home_formation)
                away_formation = get_clean_formation(away_formation)

                row["home_club_formation"] = get_clean_formation(home_formation)
                row["away_club_formation"] = get_clean_formation(away_formation)

                writer.writerow(row)
                kept += 1

    print(f"Total games read:            {total}")
    print(f"Dropped (season < {min_season}):    {dropped_season}")
    print(f"Dropped (missing/messy formation): {dropped_formation}")
    print(f"Kept:                         {kept}")
    print(f"Written to: {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="machine_learning/data/games-transfermarkt.csv", help="Path to the source games CSV")
    parser.add_argument("--output", default="machine_learning/data/games-transfermarkt.csv", help="Path to write the filtered CSV to")
    parser.add_argument("--min-season", type=int, default=MIN_SEASON, help="Minimum season start year to keep")
    args = parser.parse_args()

    filter_games(args.input, args.output, min_season=args.min_season)