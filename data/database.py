import re, datetime, os, shutil, time, gc, logging
from sqlalchemy import Column, Integer, String, BLOB, ForeignKey, Boolean, insert, or_, and_, Float, DateTime, Date, extract
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, func, or_, case
from sqlalchemy.orm import sessionmaker, aliased, scoped_session
from sqlalchemy.types import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict
import uuid, json, random
from faker import Faker
from settings import *
from utils.util_functions import *

Base = declarative_base()

logger = logging.getLogger(__name__)

progressBar = None
progressLabel = None
progressFrame = None
percentageLabel = None

def _wrapped_commit(session, db_manager):
    if not db_manager.copy_active:
        db_manager.start_copy()

        # Rebind and migrate
        old_objs = list(session)
        session.close()
        session = db_manager.get_session()
        for obj in old_objs:
            session.merge(obj)

    return session._real_commit()

class DatabaseManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance.database_name = None
            cls._instance.engine = None
            cls._instance.session_factory = None
            cls._instance.scoped_session = None
            cls._instance.original_path = None
            cls._instance.copy_path = None
            cls._instance.copy_active = False

            # game db paths
            cls._instance.game_original = "data/games.db"
            cls._instance.game_copy = "data/games_copy.db"
        return cls._instance

    def set_database(self, database_name, create_tables = False):
        self.database_name = database_name
        self.original_path = f"data/{database_name}.db"
        self.copy_path = f"data/{database_name}_copy.db"
        self._connect(self.original_path, create_tables)

    def _connect(self, db_path, create_tables = False):
        DATABASE_URL = f"sqlite:///{db_path}"
        self.engine = create_engine(DATABASE_URL, connect_args = {"check_same_thread": False})
        self.session_factory = sessionmaker(autocommit = False, autoflush = False, bind = self.engine)
        self.scoped_session = scoped_session(self.session_factory)

        if create_tables:
            Base.metadata.create_all(bind = self.engine)

    def start_copy(self):
        """Create working copies of BOTH player DB and games DB, then switch connections to player copy."""

        if self.copy_active:
            return

        shutil.copy(self.original_path, self.copy_path)
        if os.path.exists(self.game_original):
            shutil.copy(self.game_original, self.game_copy)
        self._connect(self.copy_path)
        self.copy_active = True

    def commit_copy(self):
        if self.copy_active:
            if self.scoped_session:
                self.scoped_session.remove()
            if self.engine:
                self.engine.dispose()

            gc.collect()  # force cleanup of lingering connections

            def _safe_replace(src, dst):
                attempts = 10
                for i in range(attempts):
                    try:
                        os.replace(src, dst)
                        return True
                    except PermissionError:
                        time.sleep(0.1)
                # fallback
                shutil.copy2(src, dst)
                os.remove(src)
                return True

            _safe_replace(self.copy_path, self.original_path)
            if os.path.exists(self.game_copy):
                _safe_replace(self.game_copy, self.game_original)

            self._connect(self.original_path)
            self.copy_active = False

    def discard_copy(self):
        """Delete copies of BOTH DBs and reconnect to originals."""
        if self.copy_active:
            # Ensure sessions/engines are cleaned up
            try:
                if self.scoped_session:
                    self.scoped_session.remove()
            except Exception:
                pass
            try:
                if self.engine:
                    self.engine.dispose()
            except Exception:
                pass

            # Try to delete copies, but don't crash if locked
            for path in (self.copy_path, self.game_copy):
                if os.path.exists(path):
                    try:
                        os.remove(path)
                    except PermissionError as e:
                        logger.debug("[DB DEBUG] Could not delete %s: %s", path, e)

            # Reconnect to the original
            self._connect(self.original_path)
            self.copy_active = False

    def get_session(self):
        if not self.scoped_session:
            raise ValueError("Database has not been set. Call set_database() first.")
        session = self.scoped_session()

        # Monkey-patch only once
        if not hasattr(session, "_real_commit"):
            session._real_commit = session.commit
            session.commit = lambda: _wrapped_commit(session, self)

        return session

    def has_unsaved_changes(self):
         return os.path.exists(self.copy_path) or os.path.exists(self.game_copy)

class Managers(Base):
    __tablename__ = 'managers'

    id = Column(String(256), primary_key = True, default = lambda: str(uuid.uuid4()))
    first_name = Column(String(128), nullable = False)
    last_name = Column(String(128), nullable = False)
    nationality = Column(String(128), nullable = False)
    flag = Column(BLOB)
    games_played = Column(Integer, default = 0)
    games_won = Column(Integer, default = 0)
    games_lost = Column(Integer, default = 0)
    trophies = Column(Integer, default = 0)
    user = Column(Boolean, nullable = False)
    date_of_birth = Column(Date, nullable = False)
    age = Column(Integer, nullable = False)

    @classmethod
    def add_managers(cls, first_name, last_name, nationality, date_of_birth, chosenTeam, loadedLeagues):
        session = DatabaseManager().get_session()
        try:

            non_loaded = len([v for v in loadedLeagues.values() if v == 0])
            cls.total_steps = TOTAL_STEPS - non_loaded

            faker = Faker()
            flags = {}
            for planet in ALL_PLANETS:
                with open(f"Images/Planets/{planet}.png", "rb") as file:
                    flags[planet] = file.read()

            userManagerID = str(uuid.uuid4())
            managers_dicts = [
                {
                    "id": userManagerID,
                    "first_name": first_name,
                    "last_name": last_name,
                    "nationality": nationality,
                    "flag": flags[nationality.capitalize()],
                    "user": True,
                    "date_of_birth": date_of_birth,
                    "age": 2024 - date_of_birth.year
                }
            ]
            updateProgress(None)
            for _ in range(699):
                planet = random.choice(ALL_PLANETS)
                date_of_birth = faker.date_of_birth(minimum_age = 32, maximum_age = 65)

                managers_dicts.append(
                    {
                        "id": str(uuid.uuid4()),
                        "first_name": Faker().first_name_male(),
                        "last_name": Faker().first_name(),
                        "nationality": planet,
                        "flag": flags[planet],
                        "date_of_birth": date_of_birth,
                        "user": False,
                        "age": 2024 - date_of_birth.year,
                    }
                )
                updateProgress(None)

            session.bulk_insert_mappings(Managers, managers_dicts)
            session.commit()

            updateProgress(1)
            names_id_mapping = Teams.add_teams(chosenTeam, userManagerID)
            updateProgress(3)
            League.add_leagues(loadedLeagues)

            leagues = League.get_all_leagues()
            LeagueTeams.add_league_teams(names_id_mapping, leagues)
            updateProgress(4)
            Referees.add_referees(leagues, flags)
            Matches.add_all_matches(leagues)

            updateProgress(2)
            Players.add_players(flags)

            updateProgress(5)
            Emails.add_emails(userManagerID)
            updateProgress(None)
            CalendarEvents.add_travel_events(userManagerID)
            updateProgress(None)
            Settings.add_settings()
            updateProgress(None)

            return userManagerID
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @classmethod
    def get_manager_by_id(cls, id):
        session = DatabaseManager().get_session()
        try:
            return session.query(Managers).filter(Managers.id == id).first()
        finally:
            session.close()

    @classmethod
    def get_all_non_user_managers(cls):
        session = DatabaseManager().get_session()
        try:
            managers = session.query(Managers).filter(Managers.user == False).all()
            return managers
        finally:
            session.close()

    @classmethod
    def get_manager_by_name(cls, first_name, last_name):
        session = DatabaseManager().get_session()
        try:
            manager = session.query(Managers).filter(
                Managers.first_name == first_name.strip(),
                Managers.last_name == last_name.strip()
            ).first()
            return manager
        finally:
            session.close()

    @classmethod
    def update_name(cls, id, first_name, last_name):
        session = DatabaseManager().get_session()
        try:
            manager = session.query(Managers).filter(Managers.id == id).first()
            if manager:
                manager.first_name = first_name
                manager.last_name = last_name
                session.commit()
            else:
                return None
        finally:
            session.close()

    @classmethod
    def update_games(cls, id, games_won, games_lost):
        session = DatabaseManager().get_session()
        try:
            manager = session.query(Managers).filter(Managers.id == id).first()
            if manager:
                manager.games_played += 1
                manager.games_won += games_won
                manager.games_lost += games_lost
                session.commit()
            else:
                return None
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @classmethod
    def batch_update_managers(cls, updates):
        session = DatabaseManager().get_session()
        try:
            for update in updates:
                entry = session.query(Managers).filter(Managers.id == update[0]).first()

                if entry:
                    entry.games_played += 1
                    entry.games_won += update[1]
                    entry.games_lost += update[2]

            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @classmethod
    def update_trophies(cls, id):
        session = DatabaseManager().get_session()
        try:
            manager = session.query(Managers).filter(Managers.id == id).first()
            if manager:
                manager.trophies += 1
                session.commit()
            else:
                return None
        finally:
            session.close()

    @classmethod
    def delete_manager(cls, id):
        session = DatabaseManager().get_session()
        try:
            manager = session.query(Managers).filter(Managers.id == id).first()
            if manager:
                session.delete(manager)
                session.commit()
            else:
                return None
        finally:
            session.close()

    @classmethod
    def get_all_user_managers(cls):
        session = DatabaseManager().get_session()
        try:
            managers = session.query(Managers).filter(Managers.user == True).all()
            return managers
        finally:
            session.close()

class Teams(Base):
    __tablename__ = 'teams'

    id = Column(String(256), primary_key = True, default = lambda: str(uuid.uuid4()))
    manager_id = Column(String(128), ForeignKey('managers.id'))
    name = Column(String(128), nullable = False)
    logo = Column(BLOB)
    year_created = Column(Integer, nullable = False)
    stadium = Column(String(128), nullable = False)
    strength = Column(Float, nullable = False)

    @classmethod
    def add_teams(cls, chosenTeamName, manager_id):
        session = DatabaseManager().get_session()
        try:
            with open("data/teams.json", 'r') as file:
                data = json.load(file)

            teams_dict = []
            names_ids_mapping = {}
            non_user_managers = Managers.get_all_non_user_managers()

            for team in data:

                with open(team["logo"], 'rb') as file:
                    logo = file.read()

                if team["name"] == chosenTeamName:
                    managerID = manager_id
                else:
                    manager = random.choice(non_user_managers)
                    managerID = manager.id
                    non_user_managers.remove(manager)

                teamID = str(uuid.uuid4())
                teams_dict.append({
                    "id": teamID,
                    "manager_id": managerID,
                    "name": team["name"],
                    "logo": logo,
                    "year_created": team["year_created"],
                    "stadium": team["stadium"],
                    "strength": team["strength"]
                })

                names_ids_mapping[team["name"]] = teamID
                updateProgress(None)

            session.bulk_insert_mappings(Teams, teams_dict)
            session.commit()

            return names_ids_mapping
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @classmethod
    def get_team_by_id(cls, id):
        session = DatabaseManager().get_session()
        try:
            team = session.query(Teams).filter(Teams.id == id).first()
            return team
        finally:
            session.close()

    @classmethod
    def get_teams_by_manager(cls, manager_id):
        session = DatabaseManager().get_session()
        try:
            teams = session.query(Teams).filter(Teams.manager_id == manager_id).all()
            return teams
        finally:
            session.close()

    @classmethod
    def get_team_by_name(cls, name):
        session = DatabaseManager().get_session()
        try:
            team = session.query(Teams).filter(Teams.name == name).first()
            return team
        finally:
            session.close()

    @classmethod
    def get_all_teams(cls):
        session = DatabaseManager().get_session()
        try:
            teams = session.query(Teams).all()
            return teams
        finally:
            session.close()

    @classmethod
    def get_average_current_ability_per_team(cls, league_id = None):
        """
        Return a mapping of team_id -> {"name": team_name, "avg_ca": float, "count": int}.
        If league_id is provided, only teams participating in that league are considered.
        """
        session = DatabaseManager().get_session()
        try:
            # Base query: Teams joined with Players to compute average CA per team
            query = (
                session.query(
                    Teams.id.label("team_id"),
                    Teams.name.label("team_name"),
                    func.avg(Players.current_ability).label("avg_ca"),
                    func.count(Players.id).label("player_count"),
                )
                .join(Players, Players.team_id == Teams.id)
            )
            # Optionally filter to teams in a specific league
            if league_id is not None:
                query = query.join(LeagueTeams, Teams.id == LeagueTeams.team_id).filter(LeagueTeams.league_id == league_id)

            query = query.group_by(Teams.id)

            rows = query.all()

            # Build result dict
            results = {}
            for team_id, team_name, avg_ca, player_count in rows:
                # avg_ca can be Decimal/DecimalProxy depending on DB; convert to float safely
                try:
                    avg_val = float(avg_ca) if avg_ca is not None else 0.0
                except Exception:
                    avg_val = float(avg_ca or 0.0)

                results[team_id] = {
                    "name": team_name,
                    "avg_ca": round(avg_val, 2),
                    "count": int(player_count),
                }

            return results
        finally:
            session.close()

    @classmethod
    def get_team_average_current_ability(cls, team_id):
        session = DatabaseManager().get_session()
        try:
            avg_ca = session.query(func.avg(Players.current_ability)).filter(Players.team_id == team_id).scalar()
            return round(float(avg_ca) if avg_ca is not None else 0.0, 2)
        finally:
            session.close()

    @classmethod
    def get_team_strengths(cls, league_id):
        session = DatabaseManager().get_session()
        try:
            rows = (
                session.query(Teams.name, Teams.strength)
                .join(LeagueTeams, Teams.id == LeagueTeams.team_id)
                .filter(LeagueTeams.league_id == league_id)
                .all()
            )

            return [(name, strength) for name, strength in rows]
        finally:
            session.close()

    @classmethod
    def get_manager_by_team(cls, team_id):
        session = DatabaseManager().get_session()
        try:
            team = session.query(Teams).filter(Teams.id == team_id).first()
            return team.manager_id
        finally:
            session.close()
            
class Players(Base):
    __tablename__ = 'players'

    id = Column(String(256), primary_key = True, default = lambda: str(uuid.uuid4()))
    team_id = Column(String(128), ForeignKey('teams.id'))
    first_name = Column(String(128), nullable = False)
    last_name = Column(String(128), nullable = False)
    current_ability = Column(Integer, nullable = False)
    potential_ability = Column(Integer, nullable = False)
    number = Column(Integer, nullable = False)
    position = Column(Enum("goalkeeper", "defender", "midfielder", "forward"), nullable = False)
    specific_positions = Column(String(128), nullable = False)
    date_of_birth = Column(Date, nullable = False)
    age = Column(Integer, nullable = False)
    nationality = Column(String(128), nullable = False)
    flag = Column(BLOB)
    morale = Column(Integer, nullable = False, default = 50)
    fitness = Column(Integer, nullable = False, default = 100)
    sharpness = Column(Integer, nullable = False, default = 50)
    player_role = Column(Enum("Star Player", "Backup", "Rotation", "First Team", "Youth Team"), nullable = False)
    talked_to = Column(Boolean, default = False)

    @classmethod
    def create_youth_player(cls, team_id, position, required_code, flags, numbers, league_planet):
        if random.random() < 0.8:
            planet = league_planet
        else:
            planet = random.choice(ALL_PLANETS)
            while planet == league_planet:
                planet = random.choice(ALL_PLANETS)

        faker = Faker()
        date_of_birth = faker.date_of_birth(minimum_age = 15, maximum_age = 17)
        playerCA = generate_youth_player_level()
        playerPA = calculate_potential_ability(SEASON_START_DATE.year - date_of_birth.year, playerCA)

        dict_ = {
            "id": str(uuid.uuid4()),
            "team_id": team_id,
            "first_name": faker.first_name_male(),
            "last_name": faker.last_name(),
            "number": random.randint(1, 99),
            "position": position,
            "date_of_birth": date_of_birth,
            "age": SEASON_START_DATE.year - date_of_birth.year,
            "nationality": planet,
            "flag": flags[planet],
            "current_ability": playerCA,
            "potential_ability": playerPA,
            "player_role": "Youth Team"
        }

        while dict_["number"] in numbers:
            dict_["number"] = random.randint(1, 99)
        numbers.append(dict_["number"])

        specific_positions = {
            "goalkeeper": ["GK"],
            "defender": ["RB", "CB", "LB"],
            "midfielder": ["DM", "CM", "RM", "LM", "AM"],
            "forward": ["LW", "CF", "RW"]
        }

        player_positions = [required_code]

        if position in specific_positions:
            other_positions = specific_positions[position][:]
            if required_code in other_positions:
                other_positions.remove(required_code)

            if len(other_positions) > 0:
                num_other_positions = random.choices([0, 1, 2], weights = [0.7, 0.25, 0.05])[0]
                player_positions.extend(random.sample(other_positions, num_other_positions))

        dict_["specific_positions"] = ','.join(player_positions or [required_code])

        return dict_

    @classmethod
    def add_players(cls, flags):
        session = DatabaseManager().get_session()
        teams = Teams.get_all_teams()

        players_dict = []
        try:
            for team in teams:
                league_ID = LeagueTeams.get_league_by_team(team.id).league_id
                league_name = League.get_league_by_id(league_ID).name
                league_depth = League.calculate_league_depth(league_ID)
                min_CA_level = 150 - (league_depth * 50) 
                player_nationality_percentage = get_planet_percentage(league_depth)

                for planet, leagues in PLANET_LEAGUES.items():
                    if league_name in leagues:
                        league_planet = planet
                        break

                team_players = []
                team_id = team.id

                base_positions = {
                    "goalkeeper": 3,
                    "defender": 8,
                    "midfielder": 8,
                    "forward": 6
                }

                positions = {
                    pos: random.randint(val, val + (1 if pos == "goalkeeper" else 2))
                    for pos, val in base_positions.items()
                }

                specific_positions = {
                    "goalkeeper": ["GK"],
                    "defender": ["RB", "CB", "LB"],
                    "midfielder": ["DM", "CM", "RM", "LM", "AM"],
                    "forward": ["LW", "CF", "RW"]
                }

                numbers = []
                faker = Faker()
                position_weights = [0.4, 0.3, 0.2, 0.1]

                # --- Generate all players without assigning roles ---
                for overall_position, specific_pos_list in specific_positions.items():
                    # Minimum players for each specific position
                    for specific_pos in specific_pos_list:
                        if random.random() < player_nationality_percentage:
                            planet = league_planet
                        else:
                            planet = random.choice(ALL_PLANETS)
                            while planet == league_planet:
                                planet = random.choice(ALL_PLANETS)

                        date_of_birth = faker.date_of_birth(minimum_age = 18, maximum_age = 35)
                        player_number = random.randint(1, 99)
                        while player_number in numbers:
                            player_number = random.randint(1, 99)
                        numbers.append(player_number)

                        num_positions = random.choices(range(1, min(len(specific_pos_list), 4) + 1), weights = position_weights[:min(len(specific_pos_list), 4)])[0]
                        new_player_positions = random.sample(specific_pos_list, k = num_positions)
                        if specific_pos not in new_player_positions:
                            new_player_positions[0] = specific_pos

                        playerCA = generate_CA(SEASON_START_DATE.year - date_of_birth.year, team.strength, min_level = min_CA_level)
                        playerPA = calculate_potential_ability(SEASON_START_DATE.year - date_of_birth.year, playerCA)

                        team_players.append({
                            "id": str(uuid.uuid4()),
                            "team_id": team_id,
                            "first_name": faker.first_name_male(),
                            "last_name": faker.last_name(),
                            "number": player_number,
                            "position": overall_position,
                            "date_of_birth": date_of_birth,
                            "age": SEASON_START_DATE.year - date_of_birth.year,
                            "nationality": planet,
                            "flag": flags[planet],
                            "specific_positions": ','.join(new_player_positions),
                            "current_ability": playerCA,
                            "potential_ability": playerPA
                        })

                    # Add extra players to reach desired count
                    for _ in range(positions[overall_position] - len(specific_pos_list)):
                        if random.random() < player_nationality_percentage:
                            planet = league_planet
                        else:
                            planet = random.choice(ALL_PLANETS)
                            while planet == league_planet:
                                planet = random.choice(ALL_PLANETS)

                        date_of_birth = faker.date_of_birth(minimum_age=18, maximum_age=35)
                        player_number = random.randint(1, 99)
                        while player_number in numbers:
                            player_number = random.randint(1, 99)
                        numbers.append(player_number)

                        num_positions = random.choices(range(1, min(len(specific_pos_list), 4) + 1),
                                                    weights=position_weights[:min(len(specific_pos_list), 4)])[0]
                        new_player_positions = random.sample(specific_pos_list, k=num_positions)

                        playerCA = generate_CA(SEASON_START_DATE.year - date_of_birth.year, team.strength, min_level = min_CA_level)
                        playerPA = calculate_potential_ability(SEASON_START_DATE.year - date_of_birth.year, playerCA)

                        team_players.append({
                            "id": str(uuid.uuid4()),
                            "team_id": team_id,
                            "first_name": faker.first_name_male(),
                            "last_name": faker.last_name(),
                            "number": player_number,
                            "position": overall_position,
                            "date_of_birth": date_of_birth,
                            "age": SEASON_START_DATE.year - date_of_birth.year,
                            "nationality": planet,
                            "flag": flags[planet],
                            "specific_positions": ','.join(new_player_positions),
                            "current_ability": playerCA,
                            "potential_ability": playerPA
                        })

                # 1. Star Players: top 4 in the team
                team_players.sort(key = lambda p: p["current_ability"], reverse = True)

                starKeeperPicked = False
                count = 0

                for player in team_players:
                    if count < 4:
                        if player["position"] == "GK":
                            if not starKeeperPicked:
                                player["player_role"] = "Star Player"
                                starKeeperPicked = True
                                count += 1
                            else:
                                player["player_role"] = None
                        else:
                            player["player_role"] = "Star Player"
                            count += 1
                    else:
                        player["player_role"] = None

                # Tie-break for Star Player limit
                for i in range(4, len(team_players)):
                    if team_players[i]["current_ability"] == team_players[3]["current_ability"]:
                        team_players[i]["current_ability"] -= 5

                # 2. First team and Rotation per position (Backup only for goalkeepers)
                positions = ["goalkeeper", "defender", "midfielder", "forward"]
                max_top_per_position = {"goalkeeper": 1, "defender": 4, "midfielder": 4, "forward": 4}

                for pos in positions:
                    pos_players = [p for p in team_players if p["position"] == pos and p["player_role"] is None]
                    pos_players.sort(key=lambda p: p["current_ability"], reverse=True)

                    # Count existing Star Players in this position
                    sp_count = sum(1 for p in team_players if p["position"] == pos and p["player_role"] == "Star Player")
                    remaining_top_slots = max(0, max_top_per_position[pos] - sp_count)

                    # Assign First Team up to remaining slots
                    for i in range(min(remaining_top_slots, len(pos_players))):
                        pos_players[i]["player_role"] = "First Team"

                    # Tie-break for First Team limit
                    if len(pos_players) > remaining_top_slots:
                        if remaining_top_slots > 0:
                            limit_CA = pos_players[remaining_top_slots - 1]["current_ability"]
                            for player in pos_players[remaining_top_slots:]:
                                if player["current_ability"] == limit_CA:
                                    player["current_ability"] -= 5

                    # Assign Rotation or Backup
                    for player in pos_players[remaining_top_slots:]:
                        if pos == "goalkeeper":
                            player["player_role"] = "Backup"
                        else:
                            player["player_role"] = "Rotation"

                # 1) Ensure at least one youth for each specific position
                for overall_position, specific_pos_list in specific_positions.items():
                    for specific_pos in specific_pos_list:
                        team_players.append(Players.create_youth_player(team_id, overall_position, specific_pos, flags, numbers, league_planet))

                # 2) Ensure at least base_positions youths for each overall position
                for overall_position, minimum in base_positions.items():
                    curr_count = sum(1 for p in team_players if p["position"] == overall_position and p["player_role"] == "Youth Team")

                    while curr_count < minimum:
                        specific_pos = random.choice(specific_positions[overall_position])
                        team_players.append(Players.create_youth_player(team_id, overall_position, specific_pos, flags, numbers, league_planet))
                        curr_count += 1

                players_dict.extend(team_players)
                updateProgress(None)

            session.bulk_insert_mappings(Players, players_dict)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @classmethod
    def get_players_star_ratings(cls, players, league_id, CA=True):
        """
        Return star ratings for a list of players in a league.
        Output: {player_id: stars, ...}
        """
        session = DatabaseManager().get_session()
        player_ids = [p.id for p in players]
        try:
            # Fetch all players in league with their abilities + positions
            league_players = (
                session.query(
                    Players.id,
                    Players.position,
                    Players.current_ability,
                    Players.potential_ability,
                )
                .join(LeagueTeams, Players.team_id == LeagueTeams.team_id)
                .filter(LeagueTeams.league_id == league_id)
                .all()
            )
            if not league_players:
                return {pid: 3.0 for pid in player_ids}

            # Group players by position
            pos_groups = {}
            for pid, pos, ca, pa in league_players:
                pos_groups.setdefault(pos, []).append((pid, ca, pa))

            def percentile_to_stars(p):
                if p >= 0.95: return 5.0
                if p >= 0.85: return 4.5
                if p >= 0.70: return 4.0
                if p >= 0.50: return 3.5
                if p >= 0.30: return 3.0
                if p >= 0.15: return 2.5
                if p >= 0.05: return 2.0
                return 1.5

            results = {}
            for pid in player_ids:
                # Find the player
                player = next((p for p in league_players if p[0] == pid), None)
                if not player:
                    results[pid] = 3.0
                    continue

                _, pos, ca, pa = player
                # Use each teammate's ability (c/p) — previous code mistakenly used the
                # target player's ca/pa for every entry, producing identical values.
                abilities = [c if CA else p for _, c, p in pos_groups[pos]]
                abilities_sorted = sorted(abilities)

                player_val = ca if CA else pa
                # Handle duplicates safely with bisect (better than index)
                import bisect
                rank = bisect.bisect_right(abilities_sorted, player_val)
                percentile = rank / len(abilities_sorted)

                stars = percentile_to_stars(percentile)

                # Ensure PA >= CA
                if not CA:
                    ca_abilities = sorted([c for _, c, _ in pos_groups[pos]])
                    ca_rank = bisect.bisect_right(ca_abilities, ca)
                    ca_percentile = ca_rank / len(ca_abilities)
                    ca_stars = percentile_to_stars(ca_percentile)
                    stars = max(stars, ca_stars)

                results[pid] = stars

            return results
        finally:
            session.close()

    @classmethod
    def get_player_by_id(cls, id):
        session = DatabaseManager().get_session()
        try:
            player = session.query(Players).filter(Players.id == id).first()
            return player
        finally:
            session.close()

    @classmethod
    def get_players_by_ids(cls, ids):
        session = DatabaseManager().get_session()
        try:
            players = session.query(Players).filter(Players.id.in_(ids)).all()
            return players
        finally:
            session.close()

    @classmethod
    def get_player_by_name(cls, first_name, last_name, team_id):
        session = DatabaseManager().get_session()
        try:
            player = session.query(Players).filter(Players.first_name == first_name, Players.last_name == last_name, Players.team_id == team_id).first()
            return player
        finally:
            session.close()

    @classmethod
    def update_age(cls, id, age):
        session = DatabaseManager().get_session()
        try:
            player = session.query(Players).filter(Players.id == id).first()
            if player:
                player.age = age
                session.commit()
            else:
                return None
        finally:
            session.close()

    @classmethod
    def update_morale(cls, id, morale):
        session = DatabaseManager().get_session()
        try:
            player = session.query(Players).filter(Players.id == id).first()
            if player:
                player.morale += morale
                player.morale = min(100, max(0, player.morale))

                session.commit()
            else:
                return None
        finally:
            session.close()

    @classmethod
    def batch_update_player_stats(cls, playerFitnesses, playerSharpnesses, playerMorales):
        """
        Bulk update fitness, sharpness, and morale in a single call.

        Parameters:
        - playerFitnesses: dict {player_id: [fitness, injured_flag]}
        - playerSharpnesses: dict {player_id: sharpness}
        - playerMorales: dict {player_id: morale}
        """
        session = DatabaseManager().get_session()
        try:
            # Build a single list of mappings for all players
            player_ids = set(playerFitnesses) | set(playerSharpnesses) | set(playerMorales)
            mappings = []
            for pid in player_ids:
                mapping = {"id": pid}
                if pid in playerFitnesses:
                    mapping["fitness"] = playerFitnesses[pid][0]  # take the fitness value
                if pid in playerSharpnesses:
                    mapping["sharpness"] = playerSharpnesses[pid]
                if pid in playerMorales:
                    mapping["morale"] = playerMorales[pid]
                mappings.append(mapping)

            # Single bulk update call
            session.bulk_update_mappings(Players, mappings)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.exception("[DB ERROR] Bulk update of player stats failed")
            raise e
        finally:
            session.close()


    @classmethod
    def batch_update_morales(cls, morales):
        session = DatabaseManager().get_session()
        try:
            for morale in morales:
                player = session.query(Players).filter(Players.id == morale[0]).first()
                if player:
                    player.morale += morale[1]
                    player.morale = min(100, max(0, player.morale))

            session.commit()
        except Exception as e:
            session.rollback()
            logger.exception("[DB ERROR] Batch update morales failed")
            raise e
        finally:
            session.close()

    @classmethod
    def batch_update_sharpnesses(cls, sharpnesses):
        session = DatabaseManager().get_session()
        try:
            for sharpness in sharpnesses:
                player = session.query(Players).filter(Players.id == sharpness[0]).first()
                if player:
                    player.sharpness += sharpness[1]
                    player.sharpness = min(100, max(MIN_SHARPNESS, player.sharpness))

            session.commit()
        except Exception as e:
            session.rollback()
            logger.exception("[DB ERROR] Batch update sharpnesses failed")
            raise e
        finally:
            session.close()

    @classmethod
    def get_all_players_by_team(cls, team_id, youths = True):
        session = DatabaseManager().get_session()
        try:
            position_order = case(
                [
                    (Players.position == 'goalkeeper', 1),
                    (Players.position == 'defender', 2),
                    (Players.position == 'midfielder', 3),
                    (Players.position == 'forward', 4),
                ],
                else_ = 5
            )

            query = session.query(Players).filter(Players.team_id == team_id)

            if not youths:
                query = query.filter(Players.player_role != 'Youth Team')

            players = query.order_by(position_order).all()
            return players
        finally:
            session.close()

    @classmethod
    def get_all_star_players(cls, team_id):
        session = DatabaseManager().get_session()
        try:
            players = session.query(Players).filter(Players.team_id == team_id, Players.player_role == 'Star Player').all()
            return players
        finally:
            session.close()

    @classmethod
    def get_all_youth_players(cls, team_id):
        session = DatabaseManager().get_session()
        try:
            position_order = case(
                [
                    (Players.position == 'goalkeeper', 1),
                    (Players.position == 'defender', 2),
                    (Players.position == 'midfielder', 3),
                    (Players.position == 'forward', 4),
                ],
                else_ = 5
            )

            query = session.query(Players).filter(Players.team_id == team_id, Players.player_role == 'Youth Team')
            players = query.order_by(position_order).all()
            
            return players
        finally:
            session.close()

    @classmethod
    def get_all_defenders(cls, team_id):
        session = DatabaseManager().get_session()
        try:
            role_order = case(
                [ 
                    (Players.player_role == 'Star Player', 1),
                    (Players.player_role == 'First Team', 2),
                    (Players.player_role == 'Rotation', 3),
                ],
                else_ = 4
            )

            defenders = session.query(Players).filter(Players.team_id == team_id, Players.position == 'defender').order_by(role_order).all()
            return defenders
        finally:
            session.close()

    @classmethod
    def get_all_midfielders(cls, team_id):
        session = DatabaseManager().get_session()
        try:
            role_order = case(
                [
                    (Players.player_role == 'Star Player', 1),
                    (Players.player_role == 'First Team', 2),
                    (Players.player_role == 'Rotation', 3),
                ],
                else_ = 4
            )

            midfielders = session.query(Players).filter(Players.team_id == team_id, Players.position == 'midfielder').order_by(role_order).all()
            return midfielders
        finally:
            session.close()

    @classmethod
    def get_all_forwards(cls, team_id):
        session = DatabaseManager().get_session()
        try:
            role_order = case(
                [
                    (Players.player_role == 'Star Player', 1),
                    (Players.player_role == 'First Team', 2),
                    (Players.player_role == 'Rotation', 3),
                ],
                else_ = 4
            )

            forwards = session.query(Players).filter(Players.team_id == team_id, Players.position == 'forward').order_by(role_order).all()
            return forwards
        finally:
            session.close()

    @classmethod
    def get_all_goalkeepers(cls, team_id):
        session = DatabaseManager().get_session()
        try:
            role_order = case(
                [
                    (Players.player_role == 'First Team', 1),
                    (Players.player_role == 'Backup', 2),
                ],
                else_ = 3
            )

            goalkeepers = session.query(Players).filter(Players.team_id == team_id, Players.position == 'goalkeeper').order_by(role_order).all()
            return goalkeepers
        finally:
            session.close()

    @classmethod
    def reduce_morale_to_25(cls, player_id):
        session = DatabaseManager().get_session()
        try:
            player = session.query(Players).filter(Players.id == player_id).first()

            if not player or player.morale <= 25:
                return

            player.morale = 25
            session.commit()
        finally:
            session.close()

    @classmethod
    def batch_reduce_morales_to_25(cls, player_ids):
        session = DatabaseManager().get_session()
        try:
            players = session.query(Players).filter(Players.id.in_(player_ids), Players.morale > 25).all()

            for player in players:
                player.morale = 25

            session.commit()
        except Exception as e:
            session.rollback()
            logger.exception("[DB ERROR] Batch reduce morales to 25 failed")
            raise e
        finally:
            session.close()

    @classmethod
    def batch_update_fitness(cls, fitness_data):
        session = DatabaseManager().get_session()
        try:
            for player_id, fitness in fitness_data:
                player = session.query(Players).filter(Players.id == player_id).first()
                if player:
                    player.fitness = fitness
            session.commit()
        except Exception as e:
            session.rollback()
            logger.exception("[DB ERROR] Batch update fitness failed")
            raise e
        finally:
            session.close()

    @classmethod
    def update_sharpness_and_fitness(cls, time_in_between, team_id):
        session = DatabaseManager().get_session()
        try:
            # Players eligible for fitness updates (exclude injury bans)
            fitness_players = (
                session.query(Players)
                .outerjoin(
                    PlayerBans,
                    and_(
                        PlayerBans.player_id == Players.id,
                        PlayerBans.ban_type == 'injury'
                    )
                )
                .filter(PlayerBans.id.is_(None))
                .filter(Players.team_id == team_id)
                .all()
            )

            # All players from this team
            all_players = (
                session.query(Players)
                .filter(Players.team_id == team_id)
                .all()
            )
            fitness_ids = {p.id for p in fitness_players}

            hours = int(time_in_between.total_seconds() // 3600)

            if hours > 0:
                hourly_rate = DAILY_SHARPNESS_DECAY / 24.0

                for player in all_players:
                    # sharpness exponential decay
                    decay_factor = (1 - hourly_rate) ** hours
                    player.sharpness *= decay_factor

                    # clamp and round sharpness
                    if player.sharpness < MIN_SHARPNESS:
                        player.sharpness = MIN_SHARPNESS
                    player.sharpness = int(round(player.sharpness))

                    # fitness recovery only for non-injured players
                    if player.id in fitness_ids:
                        recovery_factor = (1 - DAILY_FITNESS_RECOVERY_RATE) ** hours
                        new_fitness = 100 - (100 - player.fitness) * recovery_factor
                        player.fitness = int(math.ceil(min(100, new_fitness)))

            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @classmethod
    def update_sharpness_and_fitness_with_values(cls, team_id, fitness_value, sharpness_value):
        session = DatabaseManager().get_session()
        try:
            players = session.query(Players).filter(Players.team_id == team_id).all()

            for player in players:
                player.fitness += fitness_value
                player.sharpness += sharpness_value

                player.fitness = min(100, max(0, player.fitness))
                player.sharpness = min(100, max(MIN_SHARPNESS, player.sharpness))

            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
        
    @classmethod
    def update_talked_to(cls, player_id):
        session = DatabaseManager().get_session()
        try:
            player = session.query(Players).filter(Players.id == player_id).first()
            if player:
                player.talked_to = True
                session.commit()
        finally:
            session.close()

    @classmethod
    def reset_talked_to(cls):
        session = DatabaseManager().get_session()
        try:
            session.query(Players).update({Players.talked_to: False})
            session.commit()
        finally:
            session.close()

class Matches(Base):
    __tablename__ = 'matches'
    
    id = Column(String(256), primary_key = True, default = lambda: str(uuid.uuid4()))
    league_id = Column(String(128), ForeignKey('leagues.id'))
    home_id = Column(String(128), ForeignKey('teams.id'))
    away_id = Column(String(128), ForeignKey('teams.id'))
    referee_id = Column(String(128), ForeignKey('referees.id'))
    score_home = Column(Integer, nullable = False, default = 0)
    score_away = Column(Integer, nullable = False, default = 0)
    matchday = Column(Integer, nullable = False)
    date = Column(DateTime, nullable = False)

    @classmethod
    def add_all_matches(cls, leagues):
        def assign_times_for_day(games, time_slots):
            for game in games:
                chosen_time = random.choice(time_slots)
                yield game, chosen_time  

        session = DatabaseManager().get_session()
        try:
            matches_dict = []
            links_dict = []

            for league in leagues:

                if not league.loaded:
                    continue

                schedule = []
                referees = Referees.get_all_referees_by_league(league.id)
                team_ids = [t.team_id for t in LeagueTeams.get_teams_by_league(league.id)]
                league_id = league.id

                # --- Generate the first round of matches ---
                num_teams = len(team_ids)
                for round_ in range(num_teams - 1):
                    round_matches = []
                    for i in range(num_teams // 2):
                        home = team_ids[i]
                        away = team_ids[num_teams - 1 - i]
                        if round_ % 2 == 0:
                            round_matches.append((home, away))
                        else:
                            round_matches.append((away, home))
                    schedule.append(round_matches)
                    team_ids.insert(1, team_ids.pop())  # Rotate the list

                random.shuffle(schedule)

                # --- Second round (reverse fixtures) ---
                second_round = [[(away, home) for home, away in round] for round in schedule]
                random.shuffle(second_round)
                schedule.extend(second_round)

                # --- Generate weekend dates for 38 matchdays ---
                start_date = SEASON_START_DATE
                matchdays_dates = []
                current = start_date

                while len(matchdays_dates) < 38:
                    saturday = current + datetime.timedelta(days = (5 - current.weekday()) % 7)
                    sunday = saturday + datetime.timedelta(days = 1)

                    sat_date = saturday.date()
                    sun_date = sunday.date()

                    # Skip Christmas week (Dec 24 - Jan 1)
                    if not (datetime.date(sat_date.year, 12, 24) <= sat_date <= datetime.date(sat_date.year, 12, 31) or
                            sun_date == datetime.date(sun_date.year, 1, 1)):
                        matchdays_dates.append((saturday, sunday))

                    current = saturday + datetime.timedelta(days = 7)

                # --- Allowed kickoff times (strings) ---
                time_slots = ["12:00", "15:00", "18:00", "21:00"]

                # --- Add matches to the database ---
                for i, (matchday, (saturday, sunday)) in enumerate(zip(schedule, matchdays_dates)):
                    assigned_referees = set()
                    random.shuffle(matchday)  # Shuffle order so Sat/Sun split is fair
                    half = len(matchday) // 2
                    sat_games = matchday[:half]
                    sun_games = matchday[half:]

                    # --- Assign Saturday games ---
                    for (home_id, away_id), kickoff_time in assign_times_for_day(sat_games, time_slots):
                        available_referees = [r for r in referees if r not in assigned_referees]

                        if not available_referees:
                            raise ValueError("Not enough referees to cover all matches for this matchday.")

                        referee_id = random.choice(available_referees).id
                        assigned_referees.add(referee_id)

                        # Combine date and time into a datetime object
                        kickoff_datetime = datetime.datetime.combine(saturday, datetime.datetime.strptime(kickoff_time, "%H:%M").time())

                        matches_dict.append({
                            "id": str(uuid.uuid4()),
                            "league_id": league_id,
                            "home_id": home_id,
                            "away_id": away_id,
                            "referee_id": referee_id,
                            "matchday": i + 1,
                            "date": kickoff_datetime,
                        })

                    # --- Assign Sunday games ---
                    for (home_id, away_id), kickoff_time in assign_times_for_day(sun_games, time_slots):
                        available_referees = [r for r in referees if r not in assigned_referees]

                        if not available_referees:
                            raise ValueError("Not enough referees to cover all matches for this matchday.")

                        referee_id = random.choice(available_referees).id
                        assigned_referees.add(referee_id)

                        kickoff_datetime = datetime.datetime.combine(sunday, datetime.datetime.strptime(kickoff_time, "%H:%M").time())

                        matches_dict.append({
                            "id": str(uuid.uuid4()),
                            "league_id": league_id,
                            "home_id": home_id,
                            "away_id": away_id,
                            "referee_id": referee_id,
                            "matchday": i + 1,
                            "date": kickoff_datetime,
                        })
                
                # --- Playoffs ---
                if league.league_above is not None:
                    last_match_saturday, _ = matchdays_dates[-1]
                    first_playoff_saturday = last_match_saturday + datetime.timedelta(weeks = 2)
                    final_playoff_sunday = first_playoff_saturday + datetime.timedelta(days = 8)

                    # Two semi-finals on the same Saturday, different times
                    playoff_dates = [
                        (first_playoff_saturday, "15:00"),  # Semi-final 1
                        (first_playoff_saturday, "15:00"),  # Semi-final 2
                        (final_playoff_sunday, "15:00"),    # Final
                    ]

                    assigned_referees = set()
                    ids = []

                    for i, (date, time_str) in enumerate(playoff_dates):
                        available_referees = [r for r in referees if r.id not in assigned_referees]

                        if not available_referees:
                            available_referees = referees
                            assigned_referees.clear()

                        referee = random.choice(available_referees)
                        assigned_referees.add(referee.id)

                        kickoff_datetime = datetime.datetime.combine(
                            date,
                            datetime.datetime.strptime(time_str, "%H:%M").time()
                        )

                        matchID = str(uuid.uuid4())
                        ids.append(matchID)
                        matches_dict.append({
                            "id": matchID,
                            "league_id": league_id,
                            "home_id": None,
                            "away_id": None,
                            "referee_id": referee.id,
                            "matchday": 39,
                            "date": kickoff_datetime,
                        })

                        if i == 2:
                            links_dict.append((matchID, ids[0]))
                            links_dict.append((matchID, ids[1]))

                updateProgress(None)

            LinkedMatches.batch_add_links(links_dict)
            session.bulk_insert_mappings(Matches, matches_dict)
            session.commit()

        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    @classmethod
    def get_match_by_id(cls, id):
        session = DatabaseManager().get_session()
        try:
            match = session.query(Matches).filter(Matches.id == id).first()
            return match
        finally:
            session.close()
        
    @classmethod
    def get_match_by_teams(cls, home_id, away_id):
        session = DatabaseManager().get_session()
        try:
            match = session.query(Matches).filter(
                ((Matches.home_id == home_id) & (Matches.away_id == away_id)) |
                ((Matches.home_id == away_id) & (Matches.away_id == home_id))
            ).first()
            return match
        finally:
            session.close()
        
    @classmethod
    def get_team_next_match(cls, team_id, curr_date):
        session = DatabaseManager().get_session()
        try:
            match = session.query(Matches).filter(
                ((Matches.home_id == team_id) | (Matches.away_id == team_id)),
                Matches.date > curr_date
            ).order_by(Matches.date.asc()).first()
            return match
        finally:
            session.close()

    @classmethod
    def get_match_by_team_and_date(cls, team_id, date):
        session = DatabaseManager().get_session()
        try:
            match = session.query(Matches).filter(
                ((Matches.home_id == team_id) | (Matches.away_id == team_id)),
                Matches.date == date
            ).first()
            return match
        finally:
            session.close()

    @classmethod
    def get_match_by_team_and_date_range(cls, team_id, start_date, end_date):
        session = DatabaseManager().get_session()
        try:
            matches = session.query(Matches).filter(
                ((Matches.home_id == team_id) | (Matches.away_id == team_id)),
                Matches.date >= start_date,
                Matches.date <= end_date
            ).all()
            return matches
        finally:
            session.close()
        
    @classmethod
    def get_team_matchday_match(cls, team_id, league_id, matchday):
        session = DatabaseManager().get_session()
        try:
            match = session.query(Matches).filter(
                ((Matches.home_id == team_id) | (Matches.away_id == team_id)),
                Matches.league_id == league_id,
                Matches.matchday == matchday
            ).first()
            return match
        finally:
            session.close()

    @classmethod
    def get_team_first_match(cls, team_id):
        session = DatabaseManager().get_session()
        try:
            # Return the earliest match for the team by date
            match = (
                session.query(Matches)
                .filter((Matches.home_id == team_id) | (Matches.away_id == team_id))
                .order_by(Matches.date.asc())
                .first()
            )
            return match
        finally:
            session.close()

    @classmethod
    def get_team_last_match(cls, team_id, curr_date):
        session = DatabaseManager().get_session()
        try:
            match = session.query(Matches).join(
                TeamLineup, TeamLineup.match_id == Matches.id
            ).filter(
                (Matches.home_id == team_id) | (Matches.away_id == team_id),
                Matches.date < curr_date
            ).order_by(Matches.date.desc()).first()  # Get the latest previous match
            return match
        finally:
            session.close()

    @classmethod
    def get_team_next_5_matches(cls, team_id, curr_date):
        session = DatabaseManager().get_session()
        try:
            matches = session.query(Matches).filter(
                (Matches.home_id == team_id) | (Matches.away_id == team_id),
                Matches.date >= curr_date
            ).order_by(Matches.date.asc()).limit(5).all()
            return matches
        finally:
            session.close()

    @classmethod
    def get_team_last_5_matches(cls, team_id, curr_date):
        session = DatabaseManager().get_session()
        try:
            matches = session.query(Matches).filter(
                (Matches.home_id == team_id) | (Matches.away_id == team_id),
                Matches.date < curr_date
            ).order_by(Matches.date.desc()).limit(5).all()
            return matches
        finally:
            session.close()

    @classmethod
    def update_score(cls, id, score_home, score_away):
        session = DatabaseManager().get_session()
        try:
            match = session.query(Matches).filter(Matches.id == id).first()
            if match:
                match.score_home = score_home
                match.score_away = score_away
                session.commit()
            else:
                return None
        except Exception as e:
            session.rollback()
            logger.exception("[DB ERROR] Update match score failed")
            raise e
        finally:
            session.close()

    @classmethod
    def batch_update_scores(cls, scores):
        session = DatabaseManager().get_session()
        try:
            for score in scores:
                entry = session.query(Matches).filter(Matches.id == score[0]).first()
                if entry:
                    entry.score_home = score[1]
                    entry.score_away = score[2]

            session.commit()
        except Exception as e:
            session.rollback()
            logger.exception("[DB ERROR] Batch update of match scores failed")
            raise e
        finally:
            session.close()

    @classmethod
    def get_all_matches_by_matchday(cls, matchday):
        session = DatabaseManager().get_session()
        try:
            matches = session.query(Matches).filter(Matches.matchday == matchday).all()
            return matches
        finally:
            session.close()

    @classmethod
    def get_all_matches_by_team(cls, team_id):
        session = DatabaseManager().get_session()
        try:
            matches = session.query(Matches).filter((Matches.home_id == team_id) | (Matches.away_id == team_id)).all()
            return matches
        finally:
            session.close()

    @classmethod
    def get_all_matches_by_team_and_comp(cls, team_id, comp_id):
        session = DatabaseManager().get_session()
        try:
            matches = session.query(Matches).filter(
                ((Matches.home_id == team_id) | (Matches.away_id == team_id)),
                Matches.league_id == comp_id
            ).all()
            return matches
        finally:
            session.close()
            
    @classmethod
    def get_all_played_matches_by_team_and_comp(cls, team_id, comp_id):
        session = DatabaseManager().get_session()
        try:
            matches = session.query(Matches).join(TeamLineup, TeamLineup.match_id == Matches.id).filter(
                ((Matches.home_id == team_id) | (Matches.away_id == team_id)),
                Matches.league_id == comp_id
            ).distinct().all()
            return matches
        finally:
            session.close()

    @classmethod
    def get_all_played_matches_by_team(cls, team_id, currDate):
        session = DatabaseManager().get_session()
        try:
            matches = session.query(Matches).join(TeamLineup, TeamLineup.match_id == Matches.id).filter(
                ((Matches.home_id == team_id) | (Matches.away_id == team_id)),
                Matches.date < currDate
            ).distinct().all()
            return matches
        finally:
            session.close()

    @classmethod
    def get_all_matches_by_league(cls, league_id):
        session = DatabaseManager().get_session()
        try:
            matches = session.query(Matches).filter(Matches.league_id == league_id).all()
            return matches
        finally:
            session.close()
    
    @classmethod
    def get_all_matches_by_referee(cls, referee_id):
        session = DatabaseManager().get_session()
        try:
            matches = session.query(Matches).filter(Matches.referee_id == referee_id).all()
            return matches
        finally:
            session.close()

    @classmethod
    def get_all_played_referee_matches(cls, referee_id):
        session = DatabaseManager().get_session()
        try:
            matches = (
                session.query(Matches)
                .join(TeamLineup, TeamLineup.match_id == Matches.id)
                .filter(Matches.referee_id == referee_id)
                .distinct()
                .all()
            )
            return matches
        finally:
            session.close()

    @classmethod
    def get_matchday_for_league(cls, league_id, matchday):
        session = DatabaseManager().get_session()
        try:
            matches = session.query(Matches).filter(
                Matches.league_id == league_id,
                Matches.matchday == matchday
            ).order_by(Matches.date).all()
            return matches
        finally:
            session.close()
        
    @classmethod
    def get_last_encounter(cls, team_1, team_2):
        session = DatabaseManager().get_session()
        try:
            match = session.query(Matches).join(TeamLineup, TeamLineup.match_id == Matches.id).filter(
                ((Matches.home_id == team_1) & (Matches.away_id == team_2)) |
                ((Matches.home_id == team_2) & (Matches.away_id == team_1))
            ).order_by(Matches.matchday.desc()).all()
            return match
        finally:
            session.close()
        
    @classmethod
    def get_all_player_matches(cls, player_id):
        session = DatabaseManager().get_session()
        try:
            matches = (
                session.query(Matches)
                .join(TeamLineup, TeamLineup.match_id == Matches.id)
                .filter(TeamLineup.player_id == player_id, TeamLineup.reason.is_(None))
                .distinct()
                .all()
            )
            return matches
        finally:
            session.close()

    @classmethod
    def check_if_game_time(cls, team_id, game_time):
        session = DatabaseManager().get_session()
        try:
            match = session.query(Matches).filter(
                ((Matches.home_id == team_id) | (Matches.away_id == team_id)),
                Matches.date == game_time
            ).order_by(Matches.date.asc()).first()
            return match is not None
        finally:
            session.close()

    @classmethod
    def get_matches_time_frame(cls, start, end, exclude_leagues = []):
        session = DatabaseManager().get_session()
        try:
            subquery = session.query(TeamLineup.match_id).distinct().subquery()

            matches = session.query(Matches).filter(
                Matches.date >= start - timedelta(hours = 2), # Checks for any games that started within 2 hours before the start time
                Matches.date <= end - timedelta(hours = 2), # Doesnt select games that start within 2 hours of the end time
                Matches.league_id.notin_(exclude_leagues),
                ~Matches.id.in_(subquery)
            ).order_by(Matches.date.asc()).all()
            return matches
        finally:
            session.close()

    @classmethod
    def check_game_played(cls, match, curr_date):
        session = DatabaseManager().get_session()
        try:
            played = session.query(Matches).filter(
                Matches.id == match.id,
                Matches.date <= curr_date - timedelta(hours = 2)
            ).first()
            return played is not None
        finally:
            session.close()

    @classmethod
    def finished_matchday(cls, curr_date, league_id):
        session = DatabaseManager().get_session()
        try:
            saturday = curr_date - timedelta(days = (curr_date.weekday() - 5) % 7 + 2)  # last Sat
            sunday   = saturday + timedelta(days = 1)

            # Query matches that happened on Sat or Sun for this league
            finished = session.query(Matches).filter(
                Matches.league_id == league_id,
                Matches.date >= saturday,
                Matches.date <= sunday
            ).first()

            return finished is not None
        finally:
            session.close()

    @classmethod
    def check_if_game_date(cls, team_id, game_date):
        session = DatabaseManager().get_session()
        try:
            match = session.query(Matches).filter(
                ((Matches.home_id == team_id) | (Matches.away_id == team_id)),
                func.date(Matches.date) == game_date.date()
            ).order_by(Matches.date.asc()).first()
            return match is not None
        finally:
            session.close()

    @classmethod
    def get_team_match_no_time(cls, team_id, date):
        session = DatabaseManager().get_session()
        try:
            match = session.query(Matches).filter(
                ((Matches.home_id == team_id) | (Matches.away_id == team_id)),
                func.date(Matches.date) == date.date()
            ).order_by(Matches.date.asc()).first()
            return match
        finally:
            session.close()

class LinkedMatches(Base):
    __tablename__ = 'linked_matches'

    id = Column(String(256), primary_key = True, default = lambda: str(uuid.uuid4()))
    next_match_id = Column(String(256), ForeignKey('matches.id'))
    prev_match_id = Column(String(256), ForeignKey('matches.id'))

    @classmethod
    def batch_add_links(cls, links):
        session = DatabaseManager().get_session()
        try:
            links_dict = [{
                    "id": str(uuid.uuid4()),
                    "next_match_id": link[0],
                    "prev_match_id": link[1],
                }
                for link in links
            ]

            session.bulk_insert_mappings(LinkedMatches, links_dict)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.exception("Error in batch_add_links: %s", e)
            raise e
        finally:
            session.close()

class TeamLineup(Base):
    __tablename__ = 'team_lineup'
    
    id = Column(String(256), primary_key = True, default = lambda: str(uuid.uuid4()))
    match_id = Column(String(128), ForeignKey('matches.id'))
    player_id = Column(String(128), ForeignKey('players.id'))
    start_position = Column(String(128))
    end_position = Column(String(128))
    rating = Column(Integer)
    reason = Column(String(256))

    @classmethod
    def batch_add_lineups(cls, lineups):
        session = DatabaseManager().get_session()
        try:
            # Create a list of dictionaries representing each lineup
            lineup_dicts = [
                {
                    "id": str(uuid.uuid4()),
                    "match_id": lineup[0],
                    "player_id": lineup[1],
                    "start_position": lineup[2],
                    "end_position": lineup[3],
                    "rating": lineup[4],
                    "reason": lineup[5]
                }
                for lineup in lineups
            ]

            # Use the list of dictionaries to add the lineups
            session.bulk_insert_mappings(TeamLineup, lineup_dicts)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.exception("Error in batch_add_lineups: %s", e)
            raise e
        finally:
            session.close()
    
    @classmethod
    def add_lineup_single(cls, match_id, player_id, start_position, end_position, rating, reason):
        session = DatabaseManager().get_session()
        try:
            new_player = TeamLineup(
                match_id = match_id,
                player_id = player_id,
                start_position = start_position,
                end_position = end_position,
                rating = rating,
                reason = reason
            )
            session.add(new_player)
            session.commit()
            return new_player
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @classmethod
    def get_lineup_by_id(cls, id):
        session = DatabaseManager().get_session()
        try:
            player = session.query(TeamLineup).filter(TeamLineup.id == id).first()
            return player
        finally:
            session.close()
        
    @classmethod
    def get_lineup_by_match(cls, match_id):
        session = DatabaseManager().get_session()
        try:
            players = session.query(TeamLineup).filter(
                TeamLineup.match_id == match_id,
                TeamLineup.rating.isnot(None)
            ).all()
            return players
        finally:
            session.close()
        
    @classmethod
    def get_lineup_by_match_and_team(cls, match_id, team_id):
        session = DatabaseManager().get_session()
        try:
            players = session.query(TeamLineup).join(Players).filter(
                TeamLineup.match_id == match_id,
                Players.team_id == team_id,
                TeamLineup.rating.isnot(None)
            ).order_by(
                case(
                    [
                        (Players.position == "goalkeeper", 1),
                        (Players.position == "defender", 2),
                        (Players.position == "midfielder", 3),
                        (Players.position == "forward", 4),
                    ],
                    else_ = 5
                )
            ).all()
            return players
        finally:
            session.close()

    @classmethod
    def get_number_matches_by_player(cls, player_id, league_id):
        session = DatabaseManager().get_session()
        try:
            matches = session.query(TeamLineup).join(Matches).filter(
                TeamLineup.player_id == player_id,
                Matches.league_id == league_id,
                TeamLineup.rating.isnot(None)
            ).count()
            return matches
        finally:
            session.close()

    @classmethod
    def get_player_average_rating(cls, player_id, league_id):
        session = DatabaseManager().get_session()
        try:
            rating = session.query(func.avg(TeamLineup.rating)).join(Matches).filter(
                TeamLineup.player_id == player_id,
                Matches.league_id == league_id,
                TeamLineup.rating.isnot(None)
            ).scalar()
            return rating if rating else "N/A"
        finally:
            session.close()

    @classmethod
    def get_player_rating(cls, player_id, match_id):
        session = DatabaseManager().get_session()
        try:
            rating = session.query(TeamLineup).filter(
                TeamLineup.player_id == player_id,
                TeamLineup.match_id == match_id
            ).first()

            if rating:
                return rating.rating
            else:
                return None
        finally:
            session.close()

    @classmethod
    def get_all_average_ratings(cls, league_id):
        session = DatabaseManager().get_session()
        try:
            PlayerAlias = aliased(Players)
            MatchAlias = aliased(Matches)
            ratings = session.query(
                TeamLineup.player_id,
                PlayerAlias.first_name,
                PlayerAlias.last_name,
                func.avg(TeamLineup.rating).label('average_rating')
            ).join(
                PlayerAlias, TeamLineup.player_id == PlayerAlias.id
            ).join(
                MatchAlias, TeamLineup.match_id == MatchAlias.id
            ).filter(
                MatchAlias.league_id == league_id,
                TeamLineup.rating.isnot(None)
            ).group_by(
                TeamLineup.player_id,
                PlayerAlias.first_name,
                PlayerAlias.last_name
            ).order_by(
                func.avg(TeamLineup.rating).desc()
            ).all()
            return ratings
        finally:
            session.close()

    @classmethod
    def get_player_OTM(cls, match_id):
        session = DatabaseManager().get_session()
        try:
            rating = session.query(
                TeamLineup
            ).filter(
                TeamLineup.match_id == match_id,
                TeamLineup.rating.isnot(None)
            ).order_by(
                TeamLineup.rating.desc()
            ).first()
            return rating
        finally:
            session.close()

    @classmethod
    def get_player_potm_awards(cls, player_id):
        session = DatabaseManager().get_session()
        try:
            # Subquery: for each match_id compute the maximum rating
            max_per_match = (
                session.query(
                    TeamLineup.match_id.label('match_id'),
                    func.max(TeamLineup.rating).label('max_rating')
                )
                .group_by(TeamLineup.match_id)
                .subquery()
            )

            # Join player's rows to the subquery and count where player's rating == match max
            potm_count = (
                session.query(func.count(TeamLineup.id))
                .join(max_per_match, TeamLineup.match_id == max_per_match.c.match_id)
                .filter(TeamLineup.player_id == player_id)
                .filter(TeamLineup.rating == max_per_match.c.max_rating)
                .scalar()
            )

            return int(potm_count or 0)
        finally:
            session.close()

    @classmethod
    def check_player_availability(cls, player_id, match_id):
        session = DatabaseManager().get_session()
        try:
            availability = session.query(TeamLineup).filter(
                TeamLineup.player_id == player_id,
                TeamLineup.match_id == match_id,
                TeamLineup.reason == "unavailable"
            ).first()
            return availability is not None
        finally:
            session.close()

    @classmethod
    def check_player_benched(cls, player_id, match_id):
        session = DatabaseManager().get_session()
        try:
            availability = session.query(TeamLineup).filter(
                TeamLineup.player_id == player_id,
                TeamLineup.match_id == match_id,
                TeamLineup.reason == "benched" or TeamLineup.reason == "not_in_squad"
            ).first()
            return availability is not None
        finally:
            session.close()

    @classmethod
    def check_game_played(cls, match_id):
        session = DatabaseManager().get_session()
        try:
            played = session.query(TeamLineup).filter(
                TeamLineup.match_id == match_id
            ).first()
            return played is not None
        finally:
            session.close()

class MatchEvents(Base):
    __tablename__ = 'match_events'

    id = Column(String(256), primary_key = True, default = lambda: str(uuid.uuid4()))
    match_id = Column(String(128), ForeignKey('matches.id'))
    event_type = Column(Enum("goal", "assist", "yellow_card", "red_card", "own_goal", "penalty_goal", "penalty_miss", "penalty_saved", "clean_sheet", "injury", "sub_on", "sub_off"), nullable = False)
    time = Column(String(128), nullable = False)
    player_id = Column(String(128), ForeignKey('players.id'))

    @classmethod
    def add_event(cls, match_id, event_type, time, player_id):
        session = DatabaseManager().get_session()
        try:
            new_event = MatchEvents(
                match_id = match_id,
                event_type = event_type,
                time = time,
                player_id = player_id
            )
            session.add(new_event)
            session.commit()
            return new_event
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @classmethod
    def batch_add_events(cls, events):
        session = DatabaseManager().get_session()
        try:
            # Create a list of dictionaries representing each event
            event_dicts = [
                {
                    "id": str(uuid.uuid4()),
                    "match_id": event[0],
                    "event_type": event[1],
                    "time": event[2],
                    "player_id": event[3]
                }
                for event in events
            ]

            # Use session.execute with an insert statement
            session.execute(insert(MatchEvents), event_dicts)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.exception("Error in batch_add_events: %s", e)
            raise e
        finally:
            session.close()

    @classmethod
    def get_event_by_id(cls, id):
        session = DatabaseManager().get_session()
        try:
            event = session.query(MatchEvents).filter(MatchEvents.id == id).first()
            return event
        finally:
            session.close()
    
    @classmethod
    def get_events_by_match(cls, match_id):
        session = DatabaseManager().get_session()
        try:
            events = session.query(MatchEvents).filter(MatchEvents.match_id == match_id).all()
            return events
        finally:
            session.close()

    @classmethod
    def get_event_by_player(cls, player_id):
        session = DatabaseManager().get_session()
        try:
            events = session.query(MatchEvents).filter(MatchEvents.player_id == player_id).all()
            return events
        finally:
            session.close()

    @classmethod
    def get_events_by_team(cls, team_id, league_id):
        session = DatabaseManager().get_session()
        try:
            matches = session.query(Matches).filter(
                or_(Matches.home_id == team_id, Matches.away_id == team_id),
                Matches.league_id == league_id
            ).all()

            all_events = []
            for match in matches:
                events = cls.get_events_by_match_and_team(team_id, match.id)
                all_events.extend(events)

            return all_events
        finally:
            session.close()
        
    @classmethod
    def get_events_by_match_and_team(cls, team_id, match_id):
        session = DatabaseManager().get_session()
        try:
            events = session.query(MatchEvents).join(Players).filter(
                MatchEvents.match_id == match_id,
                Players.team_id == team_id
            ).all()
            return events
        finally:
            session.close()
        
    @classmethod
    def get_event_by_type(cls, event_type):
        session = DatabaseManager().get_session()
        try:
            events = session.query(MatchEvents).filter(MatchEvents.event_type == event_type).all()
            return events
        finally:
            session.close()

    @classmethod
    def get_event_by_type_and_match(cls, event_type, match_id):
        session = DatabaseManager().get_session()
        try:
            events = session.query(MatchEvents).filter(MatchEvents.event_type == event_type, MatchEvents.match_id == match_id).all()
            return events
        finally:
            session.close()
        
    @classmethod
    def get_event_by_time(cls, time):
        session = DatabaseManager().get_session()
        try:
            events = session.query(MatchEvents).filter(MatchEvents.time == time).all()
            return events
        finally:
            session.close()
        
    @classmethod
    def get_event_by_player_and_type(cls, player_id, event_type):
        session = DatabaseManager().get_session()
        try:
            events = session.query(MatchEvents).filter(MatchEvents.player_id == player_id, MatchEvents.event_type == event_type).all()
            return events
        finally:
            session.close()
    
    @classmethod
    def get_goals_by_player(cls, player_id):
        session = DatabaseManager().get_session()
        try:
            goals = session.query(MatchEvents).filter(MatchEvents.player_id == player_id, MatchEvents.event_type == "goal").count()
            return goals
        finally:
            session.close()

    @classmethod
    def get_goals_and_pens_by_player(cls, player_id):
        session = DatabaseManager().get_session()
        try:
            goals = session.query(MatchEvents).filter(
                MatchEvents.player_id == player_id,
                or_(MatchEvents.event_type == "goal", MatchEvents.event_type == "penalty_goal")
            ).count()
            return goals
        finally:
            session.close()
        
    @classmethod
    def get_events_by_match_and_player(cls, match_id, player_id):
        session = DatabaseManager().get_session()
        try:
            events = session.query(MatchEvents).filter(MatchEvents.match_id == match_id, MatchEvents.player_id == player_id).all()
            return events
        finally:
            session.close()
        
    @classmethod
    def get_all_goals(cls, league_id):
        session = DatabaseManager().get_session()
        try:
            PlayerAlias = aliased(Players)
            MatchAlias = aliased(Matches)
            goals = session.query(
                MatchEvents.player_id,
                PlayerAlias.first_name,
                PlayerAlias.last_name,
                func.count(MatchEvents.id).label('goal_count')
            ).join(
                PlayerAlias, MatchEvents.player_id == PlayerAlias.id
            ).join(
                MatchAlias, MatchEvents.match_id == MatchAlias.id
            ).filter(
                or_(MatchEvents.event_type == "goal", MatchEvents.event_type == "penalty_goal"),
                MatchAlias.league_id == league_id
            ).group_by(
                MatchEvents.player_id,
                PlayerAlias.first_name,
                PlayerAlias.last_name
            ).order_by(
                func.count(MatchEvents.id).desc()
            ).all()
            return goals
        finally:
            session.close()
        
    @classmethod
    def get_assists_by_player(cls, player_id):
        session = DatabaseManager().get_session()
        try:
            assists = session.query(MatchEvents).filter(MatchEvents.player_id == player_id, MatchEvents.event_type == "assist").count()
            return assists
        finally:
            session.close()
    
    @classmethod
    def get_all_assists(cls, league_id):
        session = DatabaseManager().get_session()
        try:
            PlayerAlias = aliased(Players)
            MatchAlias = aliased(Matches)
            assists = session.query(
                MatchEvents.player_id,
                PlayerAlias.first_name,
                PlayerAlias.last_name,
                func.count(MatchEvents.id).label('assist_count')
            ).join(
                PlayerAlias, MatchEvents.player_id == PlayerAlias.id
            ).join(
                MatchAlias, MatchEvents.match_id == MatchAlias.id
            ).filter(
                MatchEvents.event_type == "assist",
                MatchAlias.league_id == league_id
            ).group_by(
                MatchEvents.player_id,
                PlayerAlias.first_name,
                PlayerAlias.last_name
            ).order_by(
                func.count(MatchEvents.id).desc()
            ).all()
            return assists
        finally:
            session.close()

    @classmethod
    def get_yellow_cards_by_player(cls, player_id):
        session = DatabaseManager().get_session()
        try:
            yellow_cards = session.query(MatchEvents).filter(MatchEvents.player_id == player_id, MatchEvents.event_type == "yellow_card").count()
            return yellow_cards
        finally:
            session.close()

    @classmethod
    def check_yellow_card_ban(cls, player_id, comp_id, ban_threshold, currDate):
        session = DatabaseManager().get_session()
        try:
            yellow_cards = session.query(MatchEvents).join(Matches).filter(
                MatchEvents.player_id == player_id,
                MatchEvents.event_type == "yellow_card",
                Matches.league_id == comp_id
            ).count()

            yellow_cards += 1

            if yellow_cards and yellow_cards % ban_threshold == 0:
                PlayerBans.add_player_ban(player_id, comp_id, 1, "yellow_cards", currDate)

                player_team = Teams.get_team_by_id(Players.get_player_by_id(player_id).team_id)
                user_manager = Managers.get_manager_by_id(player_team.manager_id).user

                if user_manager:
                    date = (currDate + timedelta(days = 1)).replace(hour = 8, minute = 0, second = 0, microsecond = 0)
                    Emails.add_email("player_ban", None, player_id, 1, comp_id, date)
        finally:
            session.close()

    @classmethod
    def get_all_yellow_cards(cls, league_id):
        session = DatabaseManager().get_session()
        try:
            PlayerAlias = aliased(Players)
            MatchAlias = aliased(Matches)
            yellow_cards = session.query(
                MatchEvents.player_id,
                PlayerAlias.first_name,
                PlayerAlias.last_name,
                func.count(MatchEvents.id).label('yellow_card_count')
            ).join(
                PlayerAlias, MatchEvents.player_id == PlayerAlias.id
            ).join(
                MatchAlias, MatchEvents.match_id == MatchAlias.id
            ).filter(
                MatchEvents.event_type == "yellow_card",
                MatchAlias.league_id == league_id
            ).group_by(
                MatchEvents.player_id,
                PlayerAlias.first_name,
                PlayerAlias.last_name
            ).order_by(
                func.count(MatchEvents.id).desc()
            ).all()
            return yellow_cards
        finally:
            session.close()

    @classmethod
    def get_red_cards_by_player(cls, player_id):
        session = DatabaseManager().get_session()
        try:
            red_cards = session.query(MatchEvents).filter(MatchEvents.player_id == player_id, MatchEvents.event_type == "red_card").count()
            return red_cards
        finally:
            session.close()
        
    @classmethod
    def get_all_red_cards(cls, league_id):
        session = DatabaseManager().get_session()
        try:
            PlayerAlias = aliased(Players)
            MatchAlias = aliased(Matches)
            red_cards = session.query(
                MatchEvents.player_id,
                PlayerAlias.first_name,
                PlayerAlias.last_name,
                func.count(MatchEvents.id).label('red_card_count')
            ).join(
                PlayerAlias, MatchEvents.player_id == PlayerAlias.id
            ).join(
                MatchAlias, MatchEvents.match_id == MatchAlias.id
            ).filter(
                MatchEvents.event_type == "red_card",
                MatchAlias.league_id == league_id
            ).group_by(
                MatchEvents.player_id,
                PlayerAlias.first_name,
                PlayerAlias.last_name
            ).order_by(
                func.count(MatchEvents.id).desc()
            ).all()
            return red_cards
        finally:
            session.close()
        
    @classmethod
    def get_own_goals_by_player(cls, player_id):
        session = DatabaseManager().get_session()
        try:
            own_goals = session.query(MatchEvents).filter(MatchEvents.player_id == player_id, MatchEvents.event_type == "own_goal").count()
            return own_goals
        finally:
            session.close()
        
    @classmethod
    def get_all_own_goals(cls, league_id):
        session = DatabaseManager().get_session()
        try:
            PlayerAlias = aliased(Players)
            MatchAlias = aliased(Matches)
            own_goals = session.query(
                MatchEvents.player_id,
                PlayerAlias.first_name,
                PlayerAlias.last_name,
                func.count(MatchEvents.id).label('own_goal_count')
            ).join(
                PlayerAlias, MatchEvents.player_id == PlayerAlias.id
            ).join(
                MatchAlias, MatchEvents.match_id == MatchAlias.id
            ).filter(
                MatchEvents.event_type == "own_goal",
                MatchAlias.league_id == league_id
            ).group_by(
                MatchEvents.player_id,
                PlayerAlias.first_name,
                PlayerAlias.last_name
            ).order_by(
                func.count(MatchEvents.id).desc()
            ).all()
            return own_goals
        finally:
            session.close()

    @classmethod
    def get_penalty_goals_by_player(cls, player_id):
        session = DatabaseManager().get_session()
        try:
            penalty_goals = session.query(MatchEvents).filter(MatchEvents.player_id == player_id, MatchEvents.event_type == "penalty_goal").count()
            return penalty_goals
        finally:
            session.close()
        
    @classmethod
    def get_all_penalty_goals(cls, league_id):
        session = DatabaseManager().get_session()
        try:
            PlayerAlias = aliased(Players)
            MatchAlias = aliased(Matches)
            penalty_goals = session.query(
                MatchEvents.player_id,
                PlayerAlias.first_name,
                PlayerAlias.last_name,
                func.count(MatchEvents.id).label('penalty_goal_count')
            ).join(
                PlayerAlias, MatchEvents.player_id == PlayerAlias.id
            ).join(
                MatchAlias, MatchEvents.match_id == MatchAlias.id
            ).filter(
                MatchEvents.event_type == "penalty_goal",
                MatchAlias.league_id == league_id
            ).group_by(
                MatchEvents.player_id,
                PlayerAlias.first_name,
                PlayerAlias.last_name
            ).order_by(
                func.count(MatchEvents.id).desc()
            ).all()
            return penalty_goals
        finally:
            session.close()
        
    @classmethod
    def get_penalty_saves_by_player(cls, player_id):
        session = DatabaseManager().get_session()
        try:
            penalty_saves = session.query(MatchEvents).filter(MatchEvents.player_id == player_id, MatchEvents.event_type == "penalty_saved").count()
            return penalty_saves
        finally:
            session.close()
        
    @classmethod
    def get_all_penalty_saves(cls, league_id):
        session = DatabaseManager().get_session()
        try:
            PlayerAlias = aliased(Players)
            MatchAlias = aliased(Matches)
            penalty_saves = session.query(
                MatchEvents.player_id,
                PlayerAlias.first_name,
                PlayerAlias.last_name,
                func.count(MatchEvents.id).label('penalty_save_count')
            ).join(
                PlayerAlias, MatchEvents.player_id == PlayerAlias.id
            ).join(
                MatchAlias, MatchEvents.match_id == MatchAlias.id
            ).filter(
                MatchEvents.event_type == "penalty_saved",
                MatchAlias.league_id == league_id
            ).group_by(
                MatchEvents.player_id,
                PlayerAlias.first_name,
                PlayerAlias.last_name
            ).order_by(
                func.count(MatchEvents.id).desc()
            ).all()
            return penalty_saves
        finally:
            session.close()

    @classmethod
    def get_clean_sheets_by_player(cls, player_id):
        session = DatabaseManager().get_session()
        try:
            clean_sheets = session.query(MatchEvents).filter(MatchEvents.player_id == player_id, MatchEvents.event_type == "clean_sheet").count()
            return clean_sheets
        finally:
            session.close()
    
    @classmethod
    def get_all_clean_sheets(cls, league_id):
        session = DatabaseManager().get_session()
        try:
            PlayerAlias = aliased(Players)
            MatchAlias = aliased(Matches)
            clean_sheets = session.query(
                MatchEvents.player_id,
                PlayerAlias.first_name,
                PlayerAlias.last_name,
                func.count(MatchEvents.id).label('clean_sheet_count')
            ).join(
                PlayerAlias, MatchEvents.player_id == PlayerAlias.id
            ).join(
                MatchAlias, MatchEvents.match_id == MatchAlias.id
            ).filter(
                MatchEvents.event_type == "clean_sheet",
                MatchAlias.league_id == league_id
            ).group_by(
                MatchEvents.player_id,
                PlayerAlias.first_name,
                PlayerAlias.last_name
            ).order_by(
                func.count(MatchEvents.id).desc()
            ).all()
            return clean_sheets
        finally:
            session.close()

    @classmethod
    def get_player_game_time(cls, player_id, match_id):
        session = DatabaseManager().get_session()
        try:

            if TeamLineup.check_player_benched(player_id, match_id):
                return 0

            sub_on_event = session.query(MatchEvents).filter(
                MatchEvents.player_id == player_id,
                MatchEvents.match_id == match_id,
                MatchEvents.event_type == "sub_on"
            ).first()

            sub_off_event = session.query(MatchEvents).filter(
                MatchEvents.player_id == player_id,
                MatchEvents.match_id == match_id,
                MatchEvents.event_type == "sub_off"
            ).first()

            red_card_event = session.query(MatchEvents).filter(
                MatchEvents.player_id == player_id,
                MatchEvents.match_id == match_id,
                MatchEvents.event_type == "red_card"
            ).first()

            injury_event = session.query(MatchEvents).filter(
                MatchEvents.player_id == player_id,
                MatchEvents.match_id == match_id,
                MatchEvents.event_type == "injury"
            ).first()

            subOnTime = parse_time(sub_on_event.time) if sub_on_event else None
            subOffTime = parse_time(sub_off_event.time) if sub_off_event else None
            redCardTime = parse_time(red_card_event.time) if red_card_event else None
            injuryTime = parse_time(injury_event.time) if injury_event else None

            if not redCardTime and not injuryTime:
                if subOnTime and subOffTime:
                    game_time = subOffTime - subOnTime
                elif subOnTime:
                    game_time = 90 - subOnTime
                elif subOffTime:
                    game_time = subOffTime
                else:
                    game_time = 90
            elif redCardTime and not injuryTime:
                if subOnTime:
                    game_time = redCardTime - subOnTime
                else:
                    game_time = redCardTime
            else:
                if subOnTime:
                    game_time = injuryTime - subOnTime
                else:
                    game_time = injuryTime

            return game_time
        finally:
            session.close()

class MatchStats(Base):
    __tablename__ = 'match_stats'

    id = Column(String(256), primary_key = True, default = lambda: str(uuid.uuid4()))
    match_id = Column(String(128), ForeignKey('matches.id'))
    stat_type = Column(Enum(*SAVED_STATS), nullable = False)
    value = Column(Integer, nullable = False)
    player_id = Column(String(128), ForeignKey('players.id'))
    team_id = Column(String(128), ForeignKey('teams.id'))

    @classmethod
    def add_stat(cls, match_id, stat_type, value, player_id = None, team_id = None):
        session = DatabaseManager().get_session()
        try:
            new_stat = MatchStats(
                match_id = match_id,
                stat_type = stat_type,
                value = value,
                player_id = player_id,
                team_id = team_id
            )
            session.add(new_stat)
            session.commit()
            return new_stat
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    @classmethod
    def batch_add_stats(cls, stats):
        session = DatabaseManager().get_session()
        try:
            # Create a list of dictionaries representing each stat
            stat_dicts = [
                {
                    "id": str(uuid.uuid4()),
                    "match_id": stat[0],
                    "stat_type": stat[1],
                    "value": stat[2],
                    "player_id": stat[3],
                    "team_id": stat[4]
                }
                for stat in stats
            ]

            # Use session.execute with an insert statement
            session.execute(insert(MatchStats), stat_dicts)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.exception("Error in batch_add_stats: %s", e)
            raise e
        finally:
            session.close()

    @classmethod
    def get_stat_by_id(cls, id):
        session = DatabaseManager().get_session()
        try:
            stat = session.query(MatchStats).filter(MatchStats.id == id).first()
            return stat
        finally:
            session.close()

    @classmethod
    def get_stats_by_match(cls, match_id):
        session = DatabaseManager().get_session()
        try:
            stats = session.query(MatchStats).filter(MatchStats.match_id == match_id).all()
            return stats
        finally:
            session.close()
    
    @classmethod
    def get_stats_by_player(cls, player_id):
        session = DatabaseManager().get_session()
        try:
            stats = session.query(MatchStats).filter(MatchStats.player_id == player_id).all()
            return stats
        finally:
            session.close()

    @classmethod
    def get_stat_by_players(cls, league_id, stat_type):
        session = DatabaseManager().get_session()
        try:
            MatchAlias = aliased(Matches)
            stats = (
                session.query(
                    MatchStats.player_id,
                    func.sum(MatchStats.value).label('stat_count')
                )
                .join(MatchAlias, MatchStats.match_id == MatchAlias.id)
                .filter(
                    MatchAlias.league_id == league_id,
                    MatchStats.stat_type == stat_type
                )
                .group_by(MatchStats.player_id)
                .having(func.sum(MatchStats.value) > 0)
                .order_by(func.sum(MatchStats.value).desc())
                .all()
            )
            return stats
        finally:
            session.close()

    @classmethod
    def get_team_stats_in_match(cls, match_id, team_id):
        session = DatabaseManager().get_session()
        try:
            # Read team-level stats directly (there should be at most one stored value per stat_type)
            team_agg = (
                session.query(
                    MatchStats.stat_type,
                    MatchStats.value
                )
                .filter(
                    MatchStats.match_id == match_id,
                    MatchStats.team_id == team_id,
                    MatchStats.player_id == None
                )
                .all()
            )

            # Aggregate player-level stats per stat_type for players who belong to this team
            # and actually participated in the match (i.e., appear in TeamLineup for the match).
            player_agg = (
                session.query(
                    MatchStats.stat_type,
                    func.coalesce(func.sum(MatchStats.value), 0).label('total')
                )
                .join(Players, MatchStats.player_id == Players.id)
                .join(TeamLineup, TeamLineup.player_id == MatchStats.player_id)
                .filter(
                    MatchStats.match_id == match_id,
                    TeamLineup.match_id == match_id,
                    Players.team_id == team_id,
                    MatchStats.player_id != None
                )
                .group_by(MatchStats.stat_type)
                .all()
            )

            # Combine both aggregations into a dict { stat_type: total }
            # One stat ("xG") is a float while the rest are integers. Keep types consistent
            totals = defaultdict(int)
            for s_type, value in team_agg:
                if s_type == "xG":
                    totals[s_type] = round(float(value or 0.0), 2)
                else:
                    totals[s_type] = int(value or 0)

            for s_type, total in player_agg:
                totals[s_type] += int(total or 0)

            # Ensure all known saved stats are present with a zero default for predictable UI ordering
            for s in SAVED_STATS:
                if s == "xG":
                    totals.setdefault(s, 0.0)
                else:
                    totals.setdefault(s, 0)

            return dict(totals)
        finally:
            session.close()

    @classmethod
    def get_all_players_for_stat(cls, league_id, stat_type):
        session = DatabaseManager().get_session()
        try:
            PlayerAlias = aliased(Players)
            MatchAlias = aliased(Matches)
            # Sum the stored stat values for each player (some stats may be stored per-row)
            rows = session.query(
                MatchStats.player_id,
                PlayerAlias.first_name,
                PlayerAlias.last_name,
                func.coalesce(func.sum(MatchStats.value), 0).label('total')
            ).join(
                PlayerAlias, MatchStats.player_id == PlayerAlias.id
            ).join(
                MatchAlias, MatchStats.match_id == MatchAlias.id
            ).filter(
                MatchStats.stat_type == stat_type,
                MatchAlias.league_id == league_id
            ).group_by(
                MatchStats.player_id,
                PlayerAlias.first_name,
                PlayerAlias.last_name
            ).having(
                func.sum(MatchStats.value) > 0
            ).order_by(
                func.sum(MatchStats.value).desc()
            ).all()
            return rows
        finally:
            session.close()

    @classmethod
    def get_team_stat_in_match(cls, match_id, team_id, stat_type):
        session = DatabaseManager().get_session()
        try:
            # Sum team-level stats for the specific stat_type (team entries where player_id is NULL)
            team_total = (
                session.query(MatchStats)
                .filter(
                    MatchStats.match_id == match_id,
                    MatchStats.team_id == team_id,
                    MatchStats.player_id == None,
                    MatchStats.stat_type == stat_type
                ).first()
            )

            return team_total
        finally:
            session.close()

class League(Base):
    __tablename__ = 'leagues'
    
    id = Column(String(256), primary_key = True, default = lambda: str(uuid.uuid4()))
    name = Column(String(128), nullable = False)
    year = Column(Integer, nullable = False)
    logo = Column(BLOB)
    current_matchday = Column(Integer, nullable = False, default = 1) # the matchday stored has not yet been simulated (once one is, this value is incremented)
    promotion = Column(Integer, nullable = False)
    relegation = Column(Integer, nullable = False)
    league_above = Column(String(256))
    league_below = Column(String(256))
    loaded = Column(Boolean, nullable = False)
    to_be_loaded = Column(Boolean, nullable = False)

    @classmethod
    def add_leagues(cls, loadedLeagues):
        session = DatabaseManager().get_session()
        try:
            with open("data/leagues.json", 'r') as file:
                data = json.load(file)

            leagues_dict = []
            league_ids = {}

            for league in data:

                with open(league["logo"], 'rb') as file:
                    logo = file.read()

                leagueID = str(uuid.uuid4())
                league_ids[league["name"]] = leagueID

                leagues_dict.append({
                    "id": leagueID,
                    "name": league["name"],
                    "year": 2024,
                    "logo": logo,
                    "promotion": league["promotion"],
                    "relegation": league["relegation"],
                    "loaded": loadedLeagues[league["name"]] == 1,
                    "to_be_loaded": loadedLeagues[league["name"]] == 1
                })

            # Populate the league above and below with the corresponding ids
            for league_entry, league_json in zip(leagues_dict, data):
                if league_json.get("league_above"):
                    league_entry["league_above"] = league_ids.get(league_json["league_above"])
                if league_json.get("league_below"):
                    league_entry["league_below"] = league_ids.get(league_json["league_below"])
                
            updateProgress(None)

            session.bulk_insert_mappings(League, leagues_dict)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    @classmethod
    def get_league_by_id(cls, league_id):
        session = DatabaseManager().get_session()
        try:
            league = session.query(League).filter(League.id == league_id).first()
            return league
        finally:
            session.close()

    @classmethod
    def get_league_by_name(cls, name):
        session = DatabaseManager().get_session()
        try:
            league = session.query(League).filter(League.name == name).first()
            return league
        finally:
            session.close()
        
    @classmethod
    def update_current_matchday(cls, league_id):
        session = DatabaseManager().get_session()
        try:
            league = session.query(League).filter(League.id == league_id).first()
            if league:
                league.current_matchday += 1
                session.commit()
            else:
                return None
        finally:
            session.close()

    @classmethod
    def get_all_leagues(cls):
        session = DatabaseManager().get_session()
        try:
            leagues = session.query(League).all()
            return leagues
        finally:
            session.close()

    @classmethod
    def check_all_matches_complete(cls, league_id, currDate):
        session = DatabaseManager().get_session()
        try:
            league = session.query(League).filter(League.id == league_id).first()
            if not league:
                return False

            matchday = league.current_matchday

            # Step 2: get all matches for this matchday
            matches = session.query(Matches).filter(
                Matches.league_id == league_id,
                Matches.matchday == matchday
            ).all()

            if not matches:
                return False  # no matches found (shouldn't normally happen)

            # Step 3: check if all match dates are before currDate
            all_complete = all(TeamLineup.check_game_played(match.id) for match in matches)

            return all_complete
        finally:
            session.close()

    @classmethod
    def get_current_matchday(cls, league_id):
        session = DatabaseManager().get_session()
        try:
            league = session.query(League).filter(League.id == league_id).first()
            if league:
                return league.current_matchday
            return None
        finally:
            session.close()
    
    @classmethod
    def calculate_league_depth(cls, league_id):
        session = DatabaseManager().get_session()
        try:
            depth = 0
            league = session.query(League).filter(League.id == league_id).first()
            
            while league and league.league_above:
                depth += 1
                league = session.query(League).filter(League.id == league.league_above).first()

            return depth
        finally:
            session.close()

    @classmethod
    def get_league_state(cls, league_id):
        session = DatabaseManager().get_session()
        try:
            league = session.query(League).filter(League.id == league_id).first()
            if league:
                return league.loaded
            return None
        finally:
            session.close()

    @classmethod
    def update_loaded_leagues(cls, loaded_leagues):
        session = DatabaseManager().get_session()
        try:
            for league_name, is_loaded in loaded_leagues.items():
                league = session.query(League).filter(League.name == league_name).first()
                if league:
                    league.to_be_loaded = is_loaded
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
            
class LeagueTeams(Base):
    __tablename__ = 'league_teams'
    
    id = Column(String(256), primary_key = True, default = lambda: str(uuid.uuid4()))
    league_id = Column(String(128), ForeignKey('leagues.id'))
    team_id = Column(String(128), ForeignKey('teams.id'))
    position = Column(Integer, nullable = False)
    points = Column(Integer, nullable = False, default = 0)
    games_won = Column(Integer, nullable = False, default = 0)
    games_drawn = Column(Integer, nullable = False, default = 0)
    games_lost = Column(Integer, nullable = False, default = 0)
    goals_scored = Column(Integer, nullable = False, default = 0)
    goals_conceded = Column(Integer, nullable = False, default = 0)

    @classmethod
    def add_league_teams(cls, names_ids_mapping, leagues):
        session = DatabaseManager().get_session()
        try:
            league_teams_dict = []

            with open("data/teams.json", 'r') as file:
                data = json.load(file)

            for league in leagues:
                teams = get_all_league_teams(data, league.name)
                teams.sort(key = lambda x: x["name"])

                for i, team in enumerate(teams):
                    league_teams_dict.append({
                        "id": str(uuid.uuid4()),
                        "league_id": league.id,
                        "team_id": names_ids_mapping[team["name"]],
                        "position": i + 1
                    })
                updateProgress(None)

            session.bulk_insert_mappings(LeagueTeams, league_teams_dict)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    @classmethod
    def add_team(cls, league_id, team_id, position):
        session = DatabaseManager().get_session()
        try:
            new_team = LeagueTeams(
                league_id = league_id,
                team_id = team_id,
                position = position
            )

            session.add(new_team)
            session.commit()

            return new_team
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    @classmethod
    def get_team_by_id(cls, id):
        session = DatabaseManager().get_session()
        try:
            team = session.query(LeagueTeams).filter(LeagueTeams.team_id == id).first()
            return team
        finally:
            session.close()

    @classmethod
    def get_league_by_team(cls, team_id):
        session = DatabaseManager().get_session()
        try:
            league = session.query(LeagueTeams).filter(LeagueTeams.team_id == team_id).first()
            return league
        finally:
            session.close()

    @classmethod
    def get_teams_by_league(cls, league_id):
        session = DatabaseManager().get_session()
        try:
            teams = session.query(LeagueTeams).filter(LeagueTeams.league_id == league_id).all()
            return teams
        finally:
            session.close()

    @classmethod
    def get_teams_by_position(cls, league_id):
        session = DatabaseManager().get_session()
        try:
            teams = session.query(LeagueTeams).filter(LeagueTeams.league_id == league_id).order_by(LeagueTeams.position).all()
            return teams
        finally:
            session.close()
        
    @classmethod
    def get_teams_by_points(cls, league_id):
        session = DatabaseManager().get_session()
        try:
            teams = session.query(LeagueTeams).filter(LeagueTeams.league_id == league_id).order_by(LeagueTeams.points).all()
            return teams
        finally:
            session.close()
        
    @classmethod
    def update_team(cls, team_id, points, games_won, games_drawn, games_lost, goals_scored, goals_conceded):
        session = DatabaseManager().get_session()
        try:
            team = session.query(LeagueTeams).filter(LeagueTeams.team_id == team_id).first()
            if team:
                team.points += points
                team.games_won += games_won
                team.games_drawn += games_drawn
                team.games_lost += games_lost
                team.goals_scored += goals_scored
                team.goals_conceded += goals_conceded
                session.commit()
            else:
                return None
        except Exception as e:
            session.rollback()
            logger.exception("Error in update_team: %s", e)
            raise e
        finally:
            session.close()

    @classmethod
    def batch_update_teams(cls, updates):
        session = DatabaseManager().get_session()
        try:
            for update in updates:

                entry = session.query(LeagueTeams).filter(LeagueTeams.team_id == update[0]).first()

                if entry:
                    entry.points += update[1]
                    entry.games_won += update[2]
                    entry.games_drawn += update[3]
                    entry.games_lost += update[4]
                    entry.goals_scored += update[5]
                    entry.goals_conceded += update[6]
                
            session.commit()
        except Exception as e:
            session.rollback()
            logger.exception("Error in batch_update_teams: %s", e)
            raise e
        finally:
            session.close()

    @classmethod
    def update_team_positions(cls, league_id):
        session = DatabaseManager().get_session()
        try:
            teams = session.query(LeagueTeams).filter(LeagueTeams.league_id == league_id).all()
            if teams:
                teams.sort(key = lambda x: (x.points, x.goals_scored - x.goals_conceded, x.goals_scored, -x.goals_conceded), reverse = True)
                for index, team in enumerate(teams):
                    team.position = index + 1
                session.commit()
            else:
                return None
        finally:
            session.close()

    @classmethod
    def get_num_teams_league(cls, league_id):
        session = DatabaseManager().get_session()
        try:
            num_teams = session.query(LeagueTeams).filter(LeagueTeams.league_id == league_id).count()
            return num_teams if num_teams else 0
        finally:
            session.close()

class TeamHistory(Base):
    __tablename__ = 'team_history'
    
    id = Column(String(256), primary_key = True, default = lambda: str(uuid.uuid4()))
    matchday = Column(Integer, nullable = False)
    team_id = Column(String(128), ForeignKey('teams.id'))
    position = Column(Integer, nullable = False, default = 0)
    points = Column(Integer, nullable = False, default = 0)

    @classmethod
    def add_team(cls, matchday, team_id, position, points):
        session = DatabaseManager().get_session()
        try:
            new_team = TeamHistory(
                matchday = matchday,
                team_id = team_id,
                position = position,
                points = points
            )

            session.add(new_team)
            session.commit()

            return new_team
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @classmethod
    def update_team(cls, match_id, team_id, position, points):
        session = DatabaseManager().get_session()
        try:
            team = session.query(TeamHistory).filter(TeamHistory.match_id == match_id, TeamHistory.team_id == team_id).first()
            if team:
                team.position = position
                team.points = points
                session.commit()
                return team
            else:
                return None
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @classmethod
    def get_positions_by_team(cls, team_id):
        session = DatabaseManager().get_session()
        try:
            positions = session.query(TeamHistory.position).filter(TeamHistory.team_id == team_id).order_by(TeamHistory.matchday).all()
            return positions
        finally:
            session.close()
        
    @classmethod
    def get_points_by_team(cls, team_id):
        session = DatabaseManager().get_session()
        try:
            points = session.query(TeamHistory.points).filter(TeamHistory.team_id == team_id).order_by(TeamHistory.matchday).all()
            return points
        finally:
            session.close()
        
    @classmethod
    def get_team_data_matchday(cls, team_id, matchday):
        session = DatabaseManager().get_session()
        try:
            team = session.query(TeamHistory).filter(TeamHistory.team_id == team_id, TeamHistory.matchday == matchday).first()
            return team
        finally:
            session.close()

    @classmethod
    def get_team_data_position(cls, position, matchday):
        session = DatabaseManager().get_session()
        try:
            team = session.query(TeamHistory).filter(TeamHistory.position == position, TeamHistory.matchday == matchday).first()
            return team
        finally:
            session.close()

class Referees(Base):
    __tablename__ = 'referees'
    
    id = Column(String(256), primary_key = True, default = lambda: str(uuid.uuid4()))
    first_name = Column(String(128), nullable = False)
    last_name = Column(String(128), nullable = False)
    league_id = Column(String(256), ForeignKey('leagues.id'))
    severity = Column(Enum("low", "medium", "high"), nullable = False)
    flag = Column(BLOB)
    nationality = Column(String(128), nullable = False)
    age = Column(Integer, nullable = False)
    date_of_birth = Column(Date, nullable = False)
    
    @classmethod
    def add_referees(cls, leagues, flags):
        session = DatabaseManager().get_session()
        try:
            referees_dict = []

            faker = Faker()
            for league in leagues:

                for planet, leagues in PLANET_LEAGUES.items():
                    if league.name in leagues:
                        league_planet = planet
                        break

                for _ in range(random.randint(35, 45)):
                    date_of_birth = faker.date_of_birth(minimum_age = 30, maximum_age = 65)

                    referees_dict.append({
                        "id": str(uuid.uuid4()),
                        "first_name": faker.first_name_male(),
                        "last_name": faker.last_name_male(),
                        "league_id": league.id,
                        "severity": random.choices(["low", "medium", "high"], k = 1)[0],
                        "flag": flags[league_planet],
                        "nationality": league_planet,
                        "age": 2024 - date_of_birth.year,
                        "date_of_birth": date_of_birth
                    })
                updateProgress(None)

            session.bulk_insert_mappings(Referees, referees_dict)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @classmethod
    def get_all_referees_by_league(cls, league_id):
        session = DatabaseManager().get_session()
        try:
            referee = session.query(Referees).filter(Referees.league_id == league_id).all()
            return referee
        finally:
            session.close()

    @classmethod
    def get_referee_by_id(cls, id):
        session = DatabaseManager().get_session()
        try:
            referee = session.query(Referees).filter(Referees.id == id).first()
            return referee
        finally:
            session.close()
        
    @classmethod
    def get_referee_by_name(cls, first_name, last_name):
        session = DatabaseManager().get_session()
        try:
            referee = session.query(Referees).filter(Referees.first_name == first_name, Referees.last_name == last_name).first()
            return referee
        finally:
            session.close()

class Trophies(Base):
    __tablename__ = 'trophies'

    id = Column(String(256), primary_key = True, default = lambda: str(uuid.uuid4()))
    team_id = Column(String(128), ForeignKey('teams.id'))
    manager_id = Column(String(128), ForeignKey('managers.id'))
    competition_id = Column(String(128), ForeignKey('leagues.id'))
    year = Column(Integer, nullable = False)

    @classmethod
    def get_all_trophies_by_team(cls, team_id):
        session = DatabaseManager().get_session()
        try:
            trophies = session.query(Trophies).filter(Trophies.team_id == team_id).all()
            return trophies
        finally:
            session.close()

    @classmethod
    def get_all_trophies_by_manager(cls, manager_id):
        session = DatabaseManager().get_session()
        try:
            trophies = session.query(Trophies).filter(Trophies.manager_id == manager_id).all()
            return trophies
        finally:
            session.close()

class Emails(Base):
    __tablename__ = 'emails'

    id = Column(String(256), primary_key = True, default = lambda: str(uuid.uuid4()))
    email_type = Column(Enum("welcome", "matchday_review", "matchday_preview", "player_games_issue", "season_review", "season_preview", "player_injury", "player_ban", "player_birthday", "calendar_events"), nullable = False)
    matchday = Column(Integer)
    date = Column(DateTime, nullable = False)
    player_id = Column(String(128), ForeignKey('players.id'))
    suspension = Column(Integer)
    injury = Column(DateTime)
    comp_id = Column(String(128))
    action_complete = Column(Boolean, default = False)
    send = Column(Boolean, default = True)
    read = Column(Boolean, default = False)
    important = Column(Boolean, default = False)

    @classmethod
    def add_emails(cls, manager_id):
        session = DatabaseManager().get_session()
        try:
            emails = []

            # Add welcome email at season start
            welcome_email_date = SEASON_START_DATE
            emails.append(("welcome", None, None, None, None, welcome_email_date))

            team = session.query(Teams).filter(Teams.manager_id == manager_id).first()
            matches = Matches.get_all_matches_by_team(team.id)

            league = LeagueTeams.get_league_by_team(team.id)

            for match in matches:
                # Create preview email (2 days before at 8am)
                preview_email_date = (match.date - datetime.timedelta(days = 2)).replace(hour = 8, minute = 0, second = 0, microsecond = 0)
                emails.append(("matchday_preview", match.matchday, None, None, league.league_id, preview_email_date))

                # Create review email (next Monday at 8am)
                email_date = get_next_monday(match.date)
                review_email_date = email_date.replace(hour = 8, minute = 0, second = 0, microsecond = 0)
                emails.append(("matchday_review", match.matchday, None, None, league.league_id, review_email_date))

            players = Players.get_all_players_by_team(team.id, youths = False)

            # curr_year = Game.get_game_date(Managers.get_all_user_managers()[0].id).year
            curr_year = SEASON_START_DATE.year

            for player in players:
                dob = player.date_of_birth

                email_date = datetime.datetime(dob.year, dob.month, dob.day, 8)

                target_year = curr_year + 1 if dob.month < 8 else curr_year

                # handle Feb 29 -> Feb 28 if not a leap year
                try:
                    email_date = email_date.replace(year = target_year)
                except ValueError:
                    if dob.month == 2 and dob.day == 29:
                        email_date = datetime.datetime(target_year, 2, 28, 8)
                    else:
                        raise

                if email_date >= SEASON_START_DATE:
                    birthday_email = ("player_birthday", None, player.id, None, None, email_date)
                    emails.append(birthday_email)

            # Create calendar events email (every monday at 8am)
            calendar_date = SEASON_START_DATE
            while calendar_date.weekday() != 0:
                calendar_date += datetime.timedelta(days = 1)

            season_end = SEASON_START_DATE.replace(year = SEASON_START_DATE.year + 1)

            while calendar_date < season_end:
                calendar_email = ("calendar_events", None, None, None, None, calendar_date.replace(hour = 8, minute = 0, second = 0, microsecond = 0))
                emails.append(calendar_email)
                calendar_date += datetime.timedelta(weeks = 1)

            cls.batch_add_emails(emails)
        finally:
            session.close()

    @classmethod
    def add_email(cls, email_type, matchday, player_id, ban_length, comp_id, date, important = False):
        session = DatabaseManager().get_session()
        try:
            new_email = Emails(
                email_type = email_type,
                matchday = matchday,
                player_id = player_id,
                comp_id = comp_id,
                date = date,
                important = important
            )

            if email_type == "player_ban":
                new_email.suspension = ban_length
                new_email.injury = None
            elif email_type == "player_injury":
                new_email.injury = ban_length
                new_email.suspension = None

            session.add(new_email)
            session.commit()

            return new_email
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @classmethod
    def batch_add_emails(cls, emails):
        session = DatabaseManager().get_session()
        try:
            # Prepare list of dicts for bulk insert
            email_dicts = []
            for email in emails:
                email_type = email[0]
                matchday = email[1]
                player_id = email[2]
                ban_length = email[3]  # assuming 4th element is ban/injury length
                comp_id = email[4]
                date = email[5]

                email_dict = {
                    "id": str(uuid.uuid4()),
                    "email_type": email_type,
                    "matchday": matchday,
                    "player_id": player_id,
                    "comp_id": comp_id,
                    "date": date,
                    "suspension": ban_length if email_type == "player_ban" else None,
                    "injury": ban_length if email_type == "player_injury" else None,
                }

                email_dicts.append(email_dict)

            # Bulk insert using session.execute
            session.execute(insert(Emails), email_dicts)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @classmethod
    def increment_ban(cls, email_id, num):
        session = DatabaseManager().get_session()
        try:
            email = session.query(Emails).filter(Emails.id == email_id).first()
            if email and email.suspension is not None:
                email.suspension += num
                session.commit()
                return email
            else:
                return None
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @classmethod 
    def get_email_by_type_and_date(cls, type, date):
        session = DatabaseManager().get_session()
        try:
            email = session.query(Emails).filter(Emails.email_type == type, Emails.date == date).first()
            return email
        finally:
            session.close()

    @classmethod
    def get_email_by_id(cls, id):
        session = DatabaseManager().get_session()
        try:
            email = session.query(Emails).filter(Emails.id == id).first()
            return email
        finally:
            session.close()
        
    @classmethod
    def get_emails_by_type(cls, email_type):
        session = DatabaseManager().get_session()
        try:
            emails = session.query(Emails).filter(Emails.email_type == email_type).all()
            return emails
        finally:
            session.close()
        
    @classmethod
    def get_emails_by_matchday(cls, matchday):
        session = DatabaseManager().get_session()
        try:
            emails = session.query(Emails).filter(Emails.matchday == matchday).all()
            return emails
        finally:
            session.close()
        
    @classmethod
    def get_email_by_matchday_and_type(cls, matchday, email_type):
        session = DatabaseManager().get_session()
        try:
            email = session.query(Emails).filter(Emails.matchday == matchday, Emails.email_type == email_type).first()
            return email
        finally:
            session.close()
    
    @classmethod
    def get_all_emails(cls, curr_date):
        session = DatabaseManager().get_session()
        try:
            emails = session.query(Emails).filter(Emails.date <= curr_date, Emails.send == True).order_by(Emails.date.desc()).all()
            return emails
        finally:
            session.close()  

    @classmethod
    def get_next_email(cls, curr_date):
        session = DatabaseManager().get_session()
        try:
            email = session.query(Emails).filter(Emails.date > curr_date).order_by(Emails.date.asc()).first()
            return email
        finally:
            session.close()

    @classmethod
    def check_email_sent(cls, email_type, matchday, curr_date):
        session = DatabaseManager().get_session()
        try:
            email = session.query(Emails).filter(Emails.email_type == email_type, Emails.matchday == matchday, Emails.date <= curr_date).first()
            return email is not None
        finally:
            session.close()

    @classmethod
    def update_action(cls, email_id):
        session = DatabaseManager().get_session()
        try:
            email = session.query(Emails).filter(Emails.id == email_id).first()
            if email:
                email.action_complete = True
                session.commit()
        finally:
            session.close()

    @classmethod
    def toggle_send_calendar_emails(cls, date):
        session = DatabaseManager().get_session()
        try:
            current_setting = session.query(Emails).filter(Emails.email_type == "calendar_events", Emails.date > date).first()
            if current_setting:
                new_send_value = not current_setting.send
                session.query(Emails).filter(Emails.email_type == "calendar_events", Emails.date > date).update({Emails.send: new_send_value})
                session.commit()
                return new_send_value
            else:
                return None
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @classmethod
    def mark_email_as_read(cls, email_id):
        session = DatabaseManager().get_session()
        try:
            email = session.query(Emails).filter(Emails.id == email_id).first()
            if email:
                email.read = True
                session.commit()
        finally:
            session.close()

class PlayerBans(Base):
    __tablename__ = 'player_bans'

    id = Column(String(256), primary_key = True, default = lambda: str(uuid.uuid4()))
    player_id = Column(String(128), ForeignKey('players.id'))
    competition_id = Column(String(128))
    suspension = Column(Integer)
    injury = Column(DateTime)
    ban_type = Column(Enum("red_card", "injury", "yellow_cards"), nullable = False)

    @classmethod
    def add_player_ban(cls, player_id, competition_id, ban_length, ban_type, currDate):
        session = DatabaseManager().get_session()
        try:

            # If the player got a yellow card accumulation ban in the same game, add to the suspension. 
            existing_ban = (
                session.query(PlayerBans)
                .filter_by(player_id = player_id, competition_id = competition_id)
                .first()
            )

            # This only happens if the player gets a yellow accu and a red card in the same game
            if existing_ban and existing_ban.ban_type == "yellow_cards":

                player_team = Teams.get_team_by_id(Players.get_player_by_id(player_id).team_id)
                user_manager = Managers.get_manager_by_id(player_team.manager_id).user

                if user_manager:
                    date = (currDate + timedelta(days = 1)).replace(hour = 8, minute = 0, second = 0, microsecond = 0)
                    email = Emails.get_email_by_type_and_date("player_ban", date)
                    Emails.increment_ban(email.id, ban_length)
                
                existing_ban = session.merge(existing_ban)
                existing_ban.suspension += ban_length
                existing_ban.ban_type = "red_card"

                session.commit()
                return False
            else:

                new_ban = PlayerBans(
                    player_id = player_id,
                    competition_id = competition_id,
                    ban_type = ban_type
                )

                if ban_type == "red_card" or ban_type == "yellow_cards":
                    new_ban.suspension = ban_length
                    new_ban.injury = None
                elif ban_type == "injury":
                    new_ban.injury = ban_length
                    new_ban.suspension = None

                session.add(new_ban)
                session.commit()

                return True
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @classmethod
    def batch_add_bans(cls, bans):
        session = DatabaseManager().get_session()
        try:
            ban_dicts = []
            for ban in bans:
                player_id, competition_id, ban_length, ban_type, date = ban

                entry = {
                    "id": str(uuid.uuid4()),
                    "player_id": player_id,
                    "competition_id": competition_id,
                    "ban_type": ban_type,
                }

                if ban_type in ("red_card", "yellow_cards"):
                    entry["suspension"] = ban_length
                    entry["injury"] = None
                elif ban_type == "injury":
                    entry["injury"] = ban_length
                    entry["suspension"] = None

                ban_dicts.append(entry)

            session.execute(insert(PlayerBans), ban_dicts)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @classmethod
    def reduce_suspensions_for_team(cls, team_id, competition_id):
        session = DatabaseManager().get_session()
        try:
            bans = session.query(PlayerBans).join(Players).filter(Players.team_id == team_id).all()

            for ban in bans:
                if ban.competition_id == competition_id and ban.ban_type in ["red_card", "yellow_cards"]:
                    ban.suspension -= 1

                if ban.suspension == 0:
                    session.delete(ban)

            session.commit()

            return bans
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @classmethod
    def reduce_suspensions_for_teams(cls, teams):
        session = DatabaseManager().get_session()

        try:
            for league_id, teams in teams.items():
                for team_id in teams:
                    bans = session.query(PlayerBans).join(Players).filter(Players.team_id == team_id).all()

                    for ban in bans:
                        if ban.ban_type in ["red_card", "yellow_cards"] and ban.competition_id == league_id:
                            ban.suspension -= 1

                        if ban.suspension == 0:
                            session.delete(ban)

        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @classmethod
    def reduce_injuries(cls, time, stopDate):
        session = DatabaseManager().get_session()
        try:
            bans = session.query(PlayerBans).filter(PlayerBans.ban_type == "injury").all()

            for ban in bans:
                if ban.injury <= stopDate:
                    session.delete(ban)
                else:
                    ban.injury -= time

            session.commit()

            return bans
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @classmethod
    def reduce_injuries_for_team(cls, time, stopDate, teamID):
        session = DatabaseManager().get_session()
        try:
            # Use the teamID parameter passed into the method (was using undefined team_id)
            bans = session.query(PlayerBans).join(Players).filter(
                PlayerBans.ban_type == "injury",
                Players.team_id == teamID
            ).all()

            for ban in bans:
                if ban.injury <= stopDate:
                    session.delete(ban)
                else:
                    ban.injury -= time

            session.commit()

            return bans
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @classmethod
    def batch_reduce_injuries(cls, time, stopDate):
        session = DatabaseManager().get_session()
        try:
            bans = session.query(PlayerBans).filter(PlayerBans.ban_type == "injury").all()

            for ban in bans:
                if ban.injury <= stopDate:
                    session.delete(ban)
                else:
                    ban.injury -= time

            session.commit()

            return bans
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @classmethod
    def remove_ban(cls, ban_id):
        session = DatabaseManager().get_session()
        try:
            ban = session.query(PlayerBans).filter(PlayerBans.id == ban_id).first()
            if ban:
                session.delete(ban)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @classmethod
    def check_bans_for_player(cls, player_id, competition_id):
        session = DatabaseManager().get_session()
        try:
            bans = session.query(PlayerBans).join(Players).filter(Players.id == player_id).all()
            is_banned = False

            for ban in bans:
                if ban.ban_type == "injury" or ban.competition_id == competition_id:
                    is_banned = True

            return is_banned
        finally:
            session.close()

    @classmethod
    def get_bans_for_player(cls, player_id):
        session = DatabaseManager().get_session()
        try:
            bans = session.query(PlayerBans).join(Players).filter(Players.id == player_id).all()
            return bans if bans else []
        finally:
            session.close()

    @classmethod
    def get_player_injured(cls, player_id):
        session = DatabaseManager().get_session()
        try:
            bans = session.query(PlayerBans).join(Players).filter(Players.id == player_id).all()
            is_injured = False

            for ban in bans:
                if ban.ban_type == "injury":
                    is_injured = True

            return is_injured
        finally:
            session.close()

    @classmethod
    def get_team_injured_player_ids(cls, team_id):
        session = DatabaseManager().get_session()
        try:
            # Get all player IDs in the team
            player_ids = [p.id for p in Players.get_all_players_by_team(team_id, youths=False)]

            # Fetch all injury bans for these players
            bans = (
                session.query(PlayerBans.player_id)
                .filter(PlayerBans.player_id.in_(player_ids))
                .filter(PlayerBans.ban_type == "injury")
                .all()
            )

            # Return as a set of IDs
            return {ban.player_id for ban in bans}
        finally:
            session.close()


    @classmethod
    def get_all_non_banned_players_for_comp(cls, team_id, competition_id):
        session = DatabaseManager().get_session()
        try:
            all_players = Players.get_all_players_by_team(team_id)
            non_banned_players = []

            for player in all_players:
                is_banned = PlayerBans.check_bans_for_player(player.id, competition_id)

                if not is_banned and player.player_role != "Youth Team":
                    non_banned_players.append(player)

            return non_banned_players
        finally:
            session.close()

    @classmethod
    def get_all_non_banned_youth_players_for_comp(cls, team_id, competition_id):
        session = DatabaseManager().get_session()
        try:
            all_players = Players.get_all_players_by_team(team_id)
            non_banned_players = []

            for player in all_players:
                is_banned = PlayerBans.check_bans_for_player(player.id, competition_id)

                if not is_banned and player.player_role == "Youth Team":
                    non_banned_players.append(player)

            return non_banned_players
        finally:
            session.close()

    @classmethod
    def get_injuries_dates(cls, start_date, end_date):
        session = DatabaseManager().get_session()
        try:
            bans = session.query(PlayerBans).filter(
                PlayerBans.ban_type == "injury",
                PlayerBans.injury >= start_date,
                PlayerBans.injury <= end_date
            ).all()
            return bans
        finally:
            session.close()

class SavedLineups(Base):
    __tablename__ = 'saved_lineups'

    id = Column(String(256), primary_key = True, default = lambda: str(uuid.uuid4()))
    lineup_name = Column(String(128), nullable = False)
    player_id = Column(String(128), ForeignKey('players.id'))
    position = Column(String(128), nullable = False)
    current_lineup = Column(Boolean, default = False)

    @classmethod
    def add_lineup(cls, lineup_name, lineup):
        session = DatabaseManager().get_session()
        try:
            for position, player_id in lineup.items():
                lineup_entry = SavedLineups(
                    lineup_name = lineup_name,
                    player_id = player_id,
                    position = position
                )
                session.add(lineup_entry)

            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @classmethod
    def add_current_lineup(cls, lineup):
        session = DatabaseManager().get_session()
        try:
            for position, player_id in lineup.items():
                lineup_entry = SavedLineups(
                    lineup_name = str(uuid.uuid4()),
                    player_id = player_id,
                    position = position,
                    current_lineup = True
                )
                session.add(lineup_entry)

            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @classmethod
    def has_current_lineup(cls):
        session = DatabaseManager().get_session()
        try:
            lineup = session.query(SavedLineups).filter(SavedLineups.current_lineup == True).first()
            return lineup is not None
        finally:
            session.close()
        
    @classmethod
    def get_current_lineup(cls):
        session = DatabaseManager().get_session()
        try:
            lineup_entries = session.query(SavedLineups).filter(SavedLineups.current_lineup == True).all()
            lineup = {entry.position: Players.get_player_by_id(entry.player_id) for entry in lineup_entries}
            return lineup
        finally:
            session.close()

    @classmethod
    def delete_current_lineup(cls):
        session = DatabaseManager().get_session()
        try:
            session.query(SavedLineups).filter(SavedLineups.current_lineup.is_(True)).delete()
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @classmethod
    def get_lineup_by_name(cls, name):
        session = DatabaseManager().get_session()
        try:
            lineup = session.query(SavedLineups).filter(SavedLineups.lineup_name == name).all()
            return lineup
        finally:
            session.close()

    @classmethod
    def get_all_lineup_names(cls):
        session = DatabaseManager().get_session()
        try:
            # Query only lineup_name and exclude any entries marked as current_lineup.
            # Some DB rows may have current_lineup NULL, treat that as not-current.
            lineups = (
                session.query(SavedLineups.lineup_name)
                .filter(or_(SavedLineups.current_lineup.is_(False), SavedLineups.current_lineup.is_(None)))
                .distinct()
                .all()
            )
            return [l[0] for l in lineups]
        finally:
            session.close()

class CalendarEvents(Base):
    __tablename__ = 'calendar_events'

    id = Column(String(256), primary_key = True, default = lambda: str(uuid.uuid4()))
    event_type = Column(Enum("Light Training", "Medium Training", "Intense Training", "Team Building", "Recovery", "Match Preparation", "Match Review", "Travel"))
    team_id = Column(String(128), ForeignKey('teams.id'))
    start_date = Column(DateTime, nullable = False)
    end_date = Column(DateTime, nullable = False)
    finished = Column(Boolean, default = False)
    unchangable = Column(Boolean, default = False)

    @classmethod
    def add_event(cls, team_id, event_type, start_date, end_date, unchangable = False):
        session = DatabaseManager().get_session()
        try:
            # Check if an event with the same start & end exists
            existing_event = session.query(CalendarEvents).filter_by(
                team_id = team_id,
                start_date = start_date,
                end_date = end_date
            ).first()

            if existing_event:
                # Update the event type
                existing_event.event_type = event_type
            else:
                # Otherwise create a new one
                event = CalendarEvents(
                    team_id = team_id,
                    event_type = event_type,
                    start_date = start_date,
                    end_date = end_date,
                    unchangable = unchangable
                )
                session.add(event)

            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @classmethod
    def batch_add_events(cls, events):
        session = DatabaseManager().get_session()
        try:
            event_dicts = []
            for event in events:
                team_id, event_type, start_date, end_date, unchangable = event

                entry = {
                    "id": str(uuid.uuid4()),
                    "team_id": team_id,
                    "event_type": event_type,
                    "start_date": start_date,
                    "end_date": end_date,
                    "unchangable": unchangable
                }

                event_dicts.append(entry)

            session.execute(insert(CalendarEvents), event_dicts)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @classmethod
    def add_travel_events(cls, manager_id):
        session = DatabaseManager().get_session()
        try:
            team = session.query(Teams).filter(Teams.manager_id == manager_id).first()
            matches = Matches.get_all_matches_by_team(team.id)
            events = []

            for match in matches:

                if match.home_id == team.id:
                    continue

                event_date = match.date - timedelta(days = 1)
                start_date = event_date.replace(hour = AFTERNOON_EVENT_TIMES[0], minute = 0, second = 0, microsecond = 0)
                end_date = event_date.replace(hour = AFTERNOON_EVENT_TIMES[1], minute = 0, second = 0, microsecond = 0)

                events.append((team.id, "Travel", start_date, end_date, True))

                event_date = match.date + timedelta(days = 1)
                start_date = event_date.replace(hour = MORNING_EVENT_TIMES[0], minute = 0, second = 0, microsecond = 0)
                end_date = event_date.replace(hour = MORNING_EVENT_TIMES[1], minute = 0, second = 0, microsecond = 0)

                events.append((team.id, "Travel", start_date, end_date, True))
            
            if events:
                cls.batch_add_events(events)

        finally:
            session.close()

    @classmethod
    def remove_event(cls, event_id):
        session = DatabaseManager().get_session()
        try:
            session.query(CalendarEvents).filter(CalendarEvents.id == event_id).delete()
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @classmethod
    def get_event_by_id(cls, event_id):
        session = DatabaseManager().get_session()
        try:
            event = session.query(CalendarEvents).filter(CalendarEvents.id == event_id).first()
            return event
        finally:
            session.close()

    @classmethod
    def get_events_dates(cls, team_id, start_date, end_date, get_finished = False):
        session = DatabaseManager().get_session()
        try:
            events = session.query(CalendarEvents).filter(
                CalendarEvents.start_date < end_date,
                CalendarEvents.end_date > start_date,
                CalendarEvents.team_id == team_id
            ).all()

            if not get_finished:
                events = [event for event in events if not event.finished]

            return events
        finally:
            session.close()

    @classmethod
    def get_events_dates_all(cls, start_date, end_date):
        session = DatabaseManager().get_session()
        try:
            events = session.query(CalendarEvents).filter(
                CalendarEvents.start_date < end_date,
                CalendarEvents.end_date > start_date,
                CalendarEvents.finished == False
            ).all()

            return events
        finally:
            session.close()

    @classmethod
    def update_event(cls, event_id):
        session = DatabaseManager().get_session()
        try:
            event = session.query(CalendarEvents).filter(CalendarEvents.id == event_id).first()
            event.finished = True
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @classmethod
    def batch_update_events(cls, event_ids):
        if not event_ids:
            return

        session = DatabaseManager().get_session()
        try:
            events = (
                session.query(CalendarEvents)
                .filter(CalendarEvents.id.in_(event_ids))
                .all()
            )

            for event in events:
                event.finished = True

            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @classmethod
    def get_events_week(cls, date, team_id):
        session = DatabaseManager().get_session()
        try:
            start_of_week = date - timedelta(days = date.weekday())
            end_of_week = start_of_week + timedelta(days = 7)

            # Aggregate counts per event_type for events overlapping the week
            rows = (
                session.query(CalendarEvents.event_type, func.count(CalendarEvents.id))
                .filter(
                    CalendarEvents.start_date < end_of_week,
                    CalendarEvents.end_date >= start_of_week,
                    CalendarEvents.team_id == team_id,
                    CalendarEvents.event_type != "Travel"
                )
                .group_by(CalendarEvents.event_type)
                .all()
            )

            # If no events for this team/week, return empty dict
            if not rows:
                return {}

            counts = {etype: int(cnt) for etype, cnt in rows}

            # Ensure all possible event types are present with zero if missing
            all_types = ["Light Training", "Medium Training", "Intense Training", "Team Building", "Recovery", "Match Preparation", "Match Review"]
            result = {t: counts.get(t, 0) for t in all_types}

            return result
        finally:
            session.close()
    
    @classmethod
    def get_event_by_time(cls, team_id, start, end):
        session = DatabaseManager().get_session()
        try:
            event = session.query(CalendarEvents).filter(
                CalendarEvents.team_id == team_id,
                CalendarEvents.start_date == start,
                CalendarEvents.end_date == end
            ).first()
            return event
        finally:
            session.close()

    @classmethod
    def delete_events_for_team_in_date_range(cls, team_id, start_date, end_date):
        session = DatabaseManager().get_session()
        try:
            session.query(CalendarEvents).filter(
                CalendarEvents.team_id == team_id,
                CalendarEvents.start_date >= start_date,
                CalendarEvents.end_date <= end_date,
            ).delete(synchronize_session = False)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

class Settings(Base):
    __tablename__ = 'settings'

    id = Column(String(256), primary_key = True, default = lambda: str(uuid.uuid4()))
    setting_name = Column(String(128), nullable = False, unique = True)
    setting_value = Column(String(256), nullable = False)

    @classmethod
    def add_settings(cls):
        session = DatabaseManager().get_session()
        try:
            # store booleans as '1' or '0' strings for consistency
            setting = Settings(
                setting_name = "events_delegated",
                setting_value = '0'
            )
            
            session.add(setting)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @classmethod
    def get_setting(cls, name):
        session = DatabaseManager().get_session()
        try:
            setting = session.query(Settings).filter(Settings.setting_name == name).first()
            if not setting:
                return None

            val = setting.setting_value
            # Normalize common boolean representations
            if isinstance(val, str):
                v = val.strip().lower()
                if v in ('1', 'true', 'yes', 'on'):
                    return True
                if v in ('0', 'false', 'no', 'off'):
                    return False
                # try integer
                try:
                    return int(v)
                except Exception:
                    return val
            return val
        finally:
            session.close()

    @classmethod
    def set_setting(cls, name, value):
        session = DatabaseManager().get_session()
        try:
            setting = session.query(Settings).filter(Settings.setting_name == name).first()
            # Normalize booleans to '1'/'0' strings to keep storage consistent
            if isinstance(value, bool):
                setting.setting_value = '1' if value else '0'
            else:
                setting.setting_value = str(value)
        
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

class StatsManager:
    @staticmethod
    def get_goals_scored(leagueTeams, league_id):
        session = DatabaseManager().get_session()
        try:
            # Get all team IDs in this league
            team_ids = [team.team_id for team in leagueTeams]
            # Query LeagueTeams table for goals_scored
            results = session.query(
                LeagueTeams.team_id,
                LeagueTeams.goals_scored
            ).filter(
                LeagueTeams.league_id == league_id,
                LeagueTeams.team_id.in_(team_ids)
            ).all()
            # Sort by goals scored descending
            results = sorted(results, key=lambda x: x[1], reverse=True)
            return results
        finally:
            session.close()

    @staticmethod
    def get_penalties_scored(leagueTeams, league_id):
        session = DatabaseManager().get_session()
        try:
            team_ids = [team.team_id for team in leagueTeams]
            # Get all matches in league
            matches = session.query(Matches.id, Matches.home_id, Matches.away_id).filter(
                Matches.league_id == league_id
            ).all()
            match_ids = [m.id for m in matches]

            # Get all penalty_goal and penalty_miss events in league
            events = session.query(
                MatchEvents.match_id,
                MatchEvents.event_type,
                Players.team_id
            ).join(Players, MatchEvents.player_id == Players.id).filter(
                MatchEvents.match_id.in_(match_ids),
                MatchEvents.event_type.in_(["penalty_goal", "penalty_miss"])
            ).all()

            # Count per team
            team_stats = {tid: {"scored": 0, "taken": 0} for tid in team_ids}
            for match_id, event_type, team_id in events:
                if team_id in team_stats:
                    team_stats[team_id]["taken"] += 1
                    if event_type == "penalty_goal":
                        team_stats[team_id]["scored"] += 1

            results = []
            for tid in team_ids:
                scored = team_stats[tid]["scored"]
                taken = team_stats[tid]["taken"]
                pct = scored / taken if taken > 0 else 0
                results.append((tid, f"{scored}/{taken}", pct, taken))
            results.sort(key=lambda x: (x[2], -x[3] if x[2] == 0 else x[3]), reverse=True)
            return results
        finally:
            session.close()

    @staticmethod
    def get_goals_scored_in_first_15(leagueTeams, league_id):
        session = DatabaseManager().get_session()
        try:
            team_ids = [team.team_id for team in leagueTeams]
            matches = session.query(Matches.id).filter(Matches.league_id == league_id).all()
            match_ids = [m.id for m in matches]

            # Get all goals in first 15 minutes
            events = session.query(
                MatchEvents.match_id,
                MatchEvents.event_type,
                MatchEvents.time,
                Players.team_id
            ).join(Players, MatchEvents.player_id == Players.id).filter(
                MatchEvents.match_id.in_(match_ids),
                MatchEvents.event_type.in_(["goal", "penalty_goal"])
            ).all()

            team_goals = {tid: 0 for tid in team_ids}
            for match_id, event_type, time, team_id in events:
                try:
                    minute = int(time.split("+")[0])
                except Exception:
                    continue
                if minute <= 15 and team_id in team_goals:
                    team_goals[team_id] += 1

            results = [(tid, team_goals[tid]) for tid in team_ids]
            results.sort(key=lambda x: x[1], reverse=True)
            return results
        finally:
            session.close()

    @staticmethod
    def get_goals_scored_in_last_15(leagueTeams, league_id):
        session = DatabaseManager().get_session()
        try:
            team_ids = [team.team_id for team in leagueTeams]
            matches = session.query(Matches.id).filter(Matches.league_id == league_id).all()
            match_ids = [m.id for m in matches]

            # Get all goals in last 15 minutes
            events = session.query(
                MatchEvents.match_id,
                MatchEvents.event_type,
                MatchEvents.time,
                Players.team_id
            ).join(Players, MatchEvents.player_id == Players.id).filter(
                MatchEvents.match_id.in_(match_ids),
                MatchEvents.event_type.in_(["goal", "penalty_goal"])
            ).all()

            team_goals = {tid: 0 for tid in team_ids}
            for match_id, event_type, time, team_id in events:
                try:
                    minute = int(time.split("+")[0])
                except Exception:
                    continue
                if minute >= 75 and team_id in team_goals:
                    team_goals[team_id] += 1

            results = [(tid, team_goals[tid]) for tid in team_ids]
            results.sort(key=lambda x: x[1], reverse=True)
            return results
        finally:
            session.close()

    @staticmethod
    def get_goals_by_substitutes(leagueTeams, league_id):
        session = DatabaseManager().get_session()
        try:
            team_ids = [team.team_id for team in leagueTeams]
            matches = session.query(Matches.id).filter(Matches.league_id == league_id).all()
            match_ids = [m.id for m in matches]

            # Find all sub_on events (subs) in league
            sub_on = session.query(
                MatchEvents.player_id,
                MatchEvents.match_id
            ).filter(
                MatchEvents.match_id.in_(match_ids),
                MatchEvents.event_type == "sub_on"
            ).all()
            sub_players = set((player_id, match_id) for player_id, match_id in sub_on)

            # Find all goals in league
            goals = session.query(
                MatchEvents.player_id,
                MatchEvents.match_id,
                Players.team_id
            ).join(Players, MatchEvents.player_id == Players.id).filter(
                MatchEvents.match_id.in_(match_ids),
                MatchEvents.event_type.in_(["goal", "penalty_goal"])
            ).all()

            team_sub_goals = {tid: 0 for tid in team_ids}
            for player_id, match_id, team_id in goals:
                if (player_id, match_id) in sub_players and team_id in team_sub_goals:
                    team_sub_goals[team_id] += 1

            results = [(tid, team_sub_goals[tid]) for tid in team_ids]
            results.sort(key=lambda x: x[1], reverse=True)
            return results
        finally:
            session.close()

    @staticmethod
    def get_fastest_goal_scored(leagueTeams, league_id):
        session = DatabaseManager().get_session()
        try:
            team_ids = [team.team_id for team in leagueTeams]
            matches = session.query(Matches.id).filter(Matches.league_id == league_id).all()
            match_ids = [m.id for m in matches]

            # Get all goals in league
            events = session.query(
                MatchEvents.time,
                Players.team_id
            ).join(Players, MatchEvents.player_id == Players.id).filter(
                MatchEvents.match_id.in_(match_ids),
                MatchEvents.event_type.in_(["goal", "penalty_goal"])
            ).all()

            # Find the fastest goal for each team
            team_fastest = {tid: None for tid in team_ids}
            for time, team_id in events:
                try:
                    minute = int(time.split("+")[0])
                except Exception:
                    continue
                if team_id in team_fastest:
                    if team_fastest[team_id] is None or minute < team_fastest[team_id]:
                        team_fastest[team_id] = minute

            results = []
            for tid in team_ids:
                val = f"{team_fastest[tid]}'" if team_fastest[tid] is not None else "N/A"
                results.append((tid, val))
            # Sort by fastest (lowest minute)
            results.sort(key=lambda x: (999 if x[1] == "N/A" else int(x[1].replace("'", ""))))
            return results
        finally:
            session.close()

    @staticmethod
    def get_latest_goal_scored(leagueTeams, league_id):
        session = DatabaseManager().get_session()
        try:
            team_ids = [team.team_id for team in leagueTeams]
            matches = session.query(Matches.id).filter(Matches.league_id == league_id).all()
            match_ids = [m.id for m in matches]

            # Get all goals in league
            events = session.query(
                MatchEvents.time,
                Players.team_id
            ).join(Players, MatchEvents.player_id == Players.id).filter(
                MatchEvents.match_id.in_(match_ids),
                MatchEvents.event_type.in_(["goal", "penalty_goal"])
            ).all()

            # Find the latest goal for each team
            team_latest = {tid: None for tid in team_ids}
            for time, team_id in events:
                try:
                    minute = int(time.split("+")[0])
                except Exception:
                    continue
                if team_id in team_latest:
                    if team_latest[team_id] is None or minute > team_latest[team_id]:
                        team_latest[team_id] = minute

            results = []
            for tid in team_ids:
                val = f"{team_latest[tid]}'" if team_latest[tid] is not None else "N/A"
                results.append((tid, val))
            # Sort by latest (highest minute)
            results.sort(key=lambda x: (0 if x[1] == "N/A" else -int(x[1].replace("'", ""))))
            return results
        finally:
            session.close()

    @staticmethod
    def get_goals_conceded(leagueTeams, league_id):
        session = DatabaseManager().get_session()
        try:
            team_ids = [team.team_id for team in leagueTeams]
            # Query LeagueTeams table for goals_conceded
            results = session.query(
                LeagueTeams.team_id,
                LeagueTeams.goals_conceded
            ).filter(
                LeagueTeams.league_id == league_id,
                LeagueTeams.team_id.in_(team_ids)
            ).all()
            # Sort by goals conceded ascending (fewest is best)
            results = sorted(results, key=lambda x: x[1])
            return results
        finally:
            session.close()

    @staticmethod
    def get_clean_sheets(leagueTeams, league_id):
        session = DatabaseManager().get_session()
        try:
            team_ids = [team.team_id for team in leagueTeams]
            matches = session.query(Matches.id).filter(Matches.league_id == league_id).all()
            match_ids = [m.id for m in matches]

            # Get all clean_sheet events in league
            events = session.query(
                MatchEvents.match_id,
                Players.team_id
            ).join(Players, MatchEvents.player_id == Players.id).filter(
                MatchEvents.match_id.in_(match_ids),
                MatchEvents.event_type == "clean_sheet"
            ).all()

            team_clean_sheets = {tid: 0 for tid in team_ids}
            for match_id, team_id in events:
                if team_id in team_clean_sheets:
                    team_clean_sheets[team_id] += 1

            results = [(tid, team_clean_sheets[tid]) for tid in team_ids]
            results.sort(key=lambda x: x[1], reverse=True)
            return results
        finally:
            session.close()

    @staticmethod
    def get_yellow_cards(leagueTeams, league_id):
        session = DatabaseManager().get_session()
        try:
            team_ids = [team.team_id for team in leagueTeams]
            matches = session.query(Matches.id).filter(Matches.league_id == league_id).all()
            match_ids = [m.id for m in matches]

            # Get all yellow card events in league
            events = session.query(
                Players.team_id
            ).join(MatchEvents, MatchEvents.player_id == Players.id).filter(
                MatchEvents.match_id.in_(match_ids),
                MatchEvents.event_type == "yellow_card"
            ).all()

            team_yellow_cards = {tid: 0 for tid in team_ids}
            for (team_id,) in events:
                if team_id in team_yellow_cards:
                    team_yellow_cards[team_id] += 1

            results = [(tid, team_yellow_cards[tid]) for tid in team_ids]
            results.sort(key=lambda x: x[1], reverse=True)
            return results
        finally:
            session.close()

    @staticmethod
    def get_red_cards(leagueTeams, league_id):
        session = DatabaseManager().get_session()
        try:
            team_ids = [team.team_id for team in leagueTeams]
            matches = session.query(Matches.id).filter(Matches.league_id == league_id).all()
            match_ids = [m.id for m in matches]

            # Get all red card events in league
            events = session.query(
                Players.team_id
            ).join(MatchEvents, MatchEvents.player_id == Players.id).filter(
                MatchEvents.match_id.in_(match_ids),
                MatchEvents.event_type == "red_card"
            ).all()

            team_red_cards = {tid: 0 for tid in team_ids}
            for (team_id,) in events:
                if team_id in team_red_cards:
                    team_red_cards[team_id] += 1

            results = [(tid, team_red_cards[tid]) for tid in team_ids]
            results.sort(key=lambda x: x[1], reverse=True)
            return results
        finally:
            session.close()

    @staticmethod
    def get_own_goals(leagueTeams, league_id):
        session = DatabaseManager().get_session()
        try:
            team_ids = [team.team_id for team in leagueTeams]
            matches = session.query(Matches.id).filter(Matches.league_id == league_id).all()
            match_ids = [m.id for m in matches]

            # Get all own goal events in league
            events = session.query(
                Players.team_id
            ).join(MatchEvents, MatchEvents.player_id == Players.id).filter(
                MatchEvents.match_id.in_(match_ids),
                MatchEvents.event_type == "own_goal"
            ).all()

            team_own_goals = {tid: 0 for tid in team_ids}
            for (team_id,) in events:
                if team_id in team_own_goals:
                    team_own_goals[team_id] += 1

            results = [(tid, team_own_goals[tid]) for tid in team_ids]
            results.sort(key=lambda x: x[1], reverse=True)
            return results
        finally:
            session.close()

    @staticmethod
    def get_penalties_saved(leagueTeams, league_id):
        session = DatabaseManager().get_session()
        try:
            team_ids = [team.team_id for team in leagueTeams]
            matches = session.query(Matches.id).filter(Matches.league_id == league_id).all()
            match_ids = [m.id for m in matches]

            # Get all penalty_saved events in league
            events = session.query(
                Players.team_id
            ).join(MatchEvents, MatchEvents.player_id == Players.id).filter(
                MatchEvents.match_id.in_(match_ids),
                MatchEvents.event_type == "penalty_saved"
            ).all()

            team_pen_saves = {tid: 0 for tid in team_ids}
            for (team_id,) in events:
                if team_id in team_pen_saves:
                    team_pen_saves[team_id] += 1

            results = [(tid, team_pen_saves[tid]) for tid in team_ids]
            results.sort(key=lambda x: x[1], reverse=True)
            return results
        finally:
            session.close()

    @staticmethod
    def get_goals_conceded_in_first_15(leagueTeams, league_id):
        session = DatabaseManager().get_session()
        try:
            team_ids = [team.team_id for team in leagueTeams]
            matches = session.query(Matches.id).filter(Matches.league_id == league_id).all()
            match_ids = [m.id for m in matches]

            # Get all goals in first 15 minutes (including own goals)
            events = session.query(
                MatchEvents.match_id,
                MatchEvents.event_type,
                MatchEvents.time,
                Players.team_id
            ).join(Players, MatchEvents.player_id == Players.id).filter(
                MatchEvents.match_id.in_(match_ids),
                MatchEvents.event_type.in_(["goal", "penalty_goal", "own_goal"])
            ).all()

            team_conceded = {tid: 0 for tid in team_ids}
            for match_id, event_type, time, team_id in events:
                try:
                    minute = int(time.split("+")[0])
                except Exception:
                    continue
                if minute <= 15:
                    # Find opponent team for this match
                    match = session.query(Matches).filter(Matches.id == match_id).first()
                    if not match:
                        continue
                    # If own goal, the team that scored is the conceding team
                    if event_type == "own_goal":
                        if team_id in team_conceded:
                            team_conceded[team_id] += 1
                    else:
                        # Normal goal: increment for the opponent
                        if match.home_id == team_id and match.away_id in team_conceded:
                            team_conceded[match.away_id] += 1
                        elif match.away_id == team_id and match.home_id in team_conceded:
                            team_conceded[match.home_id] += 1

            results = [(tid, team_conceded[tid]) for tid in team_ids]
            results.sort(key=lambda x: x[1], reverse=True)
            return results
        finally:
            session.close()

    @staticmethod
    def get_goals_conceded_in_last_15(leagueTeams, league_id):
        session = DatabaseManager().get_session()
        try:
            team_ids = [team.team_id for team in leagueTeams]
            matches = session.query(Matches.id).filter(Matches.league_id == league_id).all()
            match_ids = [m.id for m in matches]

            # Get all goals in last 15 minutes (including own goals)
            events = session.query(
                MatchEvents.match_id,
                MatchEvents.event_type,
                MatchEvents.time,
                Players.team_id
            ).join(Players, MatchEvents.player_id == Players.id).filter(
                MatchEvents.match_id.in_(match_ids),
                MatchEvents.event_type.in_(["goal", "penalty_goal", "own_goal"])
            ).all()

            team_conceded = {tid: 0 for tid in team_ids}
            for match_id, event_type, time, team_id in events:
                try:
                    minute = int(time.split("+")[0])
                except Exception:
                    continue
                if minute >= 75:
                    match = session.query(Matches).filter(Matches.id == match_id).first()
                    if not match:
                        continue
                    if event_type == "own_goal":
                        if team_id in team_conceded:
                            team_conceded[team_id] += 1
                    else:
                        if match.home_id == team_id and match.away_id in team_conceded:
                            team_conceded[match.away_id] += 1
                        elif match.away_id == team_id and match.home_id in team_conceded:
                            team_conceded[match.home_id] += 1

            results = [(tid, team_conceded[tid]) for tid in team_ids]
            results.sort(key=lambda x: x[1], reverse=True)
            return results
        finally:
            session.close()

    @staticmethod
    def get_fastest_goal_conceded(leagueTeams, league_id):
        session = DatabaseManager().get_session()
        try:
            team_ids = [team.team_id for team in leagueTeams]
            matches = session.query(Matches.id, Matches.home_id, Matches.away_id).filter(Matches.league_id == league_id).all()
            match_map = {m.id: (m.home_id, m.away_id) for m in matches}
            match_ids = list(match_map.keys())

            events = session.query(
                MatchEvents.match_id,
                MatchEvents.event_type,
                MatchEvents.time,
                Players.team_id
            ).join(Players, MatchEvents.player_id == Players.id).filter(
                MatchEvents.match_id.in_(match_ids),
                MatchEvents.event_type.in_(["goal", "penalty_goal", "own_goal"])
            ).all()

            team_fastest = {tid: None for tid in team_ids}
            for match_id, event_type, time, team_id in events:
                try:
                    minute = int(time.split("+")[0])
                except Exception:
                    continue
                match = match_map.get(match_id)
                if not match:
                    continue
                # Own goal: conceding team is the scorer's team
                if event_type == "own_goal":
                    if team_id in team_fastest:
                        if team_fastest[team_id] is None or minute < team_fastest[team_id]:
                            team_fastest[team_id] = minute
                else:
                    # Normal goal: conceding team is the opponent
                    if match[0] == team_id and (match[1] in team_fastest):
                        if team_fastest[match[1]] is None or minute < team_fastest[match[1]]:
                            team_fastest[match[1]] = minute
                    elif match[1] == team_id and (match[0] in team_fastest):
                        if team_fastest[match[0]] is None or minute < team_fastest[match[0]]:
                            team_fastest[match[0]] = minute

            results = []
            for tid in team_ids:
                val = f"{team_fastest[tid]}'" if team_fastest[tid] is not None else "N/A"
                results.append((tid, val))
            results.sort(key=lambda x: (999 if x[1] == "N/A" else int(x[1].replace("'", ""))))
            return results
        finally:
            session.close()
        
    @staticmethod
    def get_latest_goal_conceded(leagueTeams, league_id):
        session = DatabaseManager().get_session()
        try:
            team_ids = [team.team_id for team in leagueTeams]
            matches = session.query(Matches.id, Matches.home_id, Matches.away_id).filter(Matches.league_id == league_id).all()
            match_map = {m.id: (m.home_id, m.away_id) for m in matches}
            match_ids = list(match_map.keys())

            events = session.query(
                MatchEvents.match_id,
                MatchEvents.event_type,
                MatchEvents.time,
                Players.team_id
            ).join(Players, MatchEvents.player_id == Players.id).filter(
                MatchEvents.match_id.in_(match_ids),
                MatchEvents.event_type.in_(["goal", "penalty_goal", "own_goal"])
            ).all()

            team_latest = {tid: None for tid in team_ids}
            for match_id, event_type, time, team_id in events:
                try:
                    minute = int(time.split("+")[0])
                except Exception:
                    continue
                match = match_map.get(match_id)
                if not match:
                    continue
                if event_type == "own_goal":
                    if team_id in team_latest:
                        if team_latest[team_id] is None or minute > team_latest[team_id]:
                            team_latest[team_id] = minute
                else:
                    if match[0] == team_id and (match[1] in team_latest):
                        if team_latest[match[1]] is None or minute > team_latest[match[1]]:
                            team_latest[match[1]] = minute
                    elif match[1] == team_id and (match[0] in team_latest):
                        if team_latest[match[0]] is None or minute > team_latest[match[0]]:
                            team_latest[match[0]] = minute

            results = []
            for tid in team_ids:
                val = f"{team_latest[tid]}'" if team_latest[tid] is not None else "N/A"
                results.append((tid, val))
            results.sort(key=lambda x: (0 if x[1] == "N/A" else -int(x[1].replace("'", ""))))
            return results
        finally:
            session.close()

    @staticmethod
    def get_goal_difference(leagueTeams, league_id):
        session = DatabaseManager().get_session()
        try:
            team_ids = [team.team_id for team in leagueTeams]
            # Query LeagueTeams table for goals_scored and goals_conceded, and compute difference in SQL
            results = session.query(
                LeagueTeams.team_id,
                (LeagueTeams.goals_scored - LeagueTeams.goals_conceded).label("goal_difference")
            ).filter(
                LeagueTeams.league_id == league_id,
                LeagueTeams.team_id.in_(team_ids)
            ).order_by(
                (LeagueTeams.goals_scored - LeagueTeams.goals_conceded).desc()
            ).all()
            return results
        finally:
            session.close()

    @staticmethod
    def get_winning_from_losing_position(leagueTeams, league_id):
        """Fetch the number of wins from losing positions for each team using multithreading."""
        
        def fetch_team_wins_from_losing(team):
            matches = Matches.get_all_played_matches_by_team_and_comp(team.team_id, league_id)
            wins = 0
            for match in matches:
                events = MatchEvents.get_events_by_match(match.id)
                goals = [event for event in events if event.event_type in ["goal", "penalty_goal"] and Players.get_player_by_id(event.player_id).team_id == team.team_id]
                opp_goals = [event for event in events if event.event_type in ["goal", "penalty_goal"] and Players.get_player_by_id(event.player_id).team_id != team.team_id]
                own_goals = [event for event in events if event.event_type == "own_goal"]

                for own_goal in own_goals:
                    player = Players.get_player_by_id(own_goal.player_id)
                    if player.team_id == team.team_id:
                        opp_goals.append(own_goal)
                    else:
                        goals.append(own_goal)

                if len(goals) == 0 or len(opp_goals) == 0 or len(goals) == len(opp_goals) or len(goals) < len(opp_goals):
                    continue

                if StatsManager._get_comeback_win(goals, opp_goals):
                    wins += 1
            return team.team_id, wins

        results = []
        with ThreadPoolExecutor(max_workers=len(leagueTeams)) as executor:
            futures = {executor.submit(fetch_team_wins_from_losing, team): team for team in leagueTeams}
            for future in futures:
                results.append(future.result())

        results.sort(key=lambda x: x[1], reverse=True)
        return results

    @staticmethod
    def get_losing_from_winning_position(leagueTeams, league_id):
        """Fetch the number of losses from winning positions for each team using multithreading."""
        
        def fetch_team_losses_from_winning(team):
            matches = Matches.get_all_played_matches_by_team_and_comp(team.team_id, league_id)
            losses = 0
            for match in matches:
                events = MatchEvents.get_events_by_match(match.id)
                goals = [event for event in events if event.event_type in ["goal", "penalty_goal"] and Players.get_player_by_id(event.player_id).team_id == team.team_id]
                opp_goals = [event for event in events if event.event_type in ["goal", "penalty_goal"] and Players.get_player_by_id(event.player_id).team_id != team.team_id]
                own_goals = [event for event in events if event.event_type == "own_goal"]

                for own_goal in own_goals:
                    player = Players.get_player_by_id(own_goal.player_id)
                    if player.team_id == team.team_id:
                        opp_goals.append(own_goal)
                    else:
                        goals.append(own_goal)

                if len(goals) == 0 or len(opp_goals) == 0 or len(goals) == len(opp_goals) or len(goals) > len(opp_goals):
                    continue

                if StatsManager._get_choke_loss(goals, opp_goals):
                    losses += 1
            return team.team_id, losses

        results = []
        with ThreadPoolExecutor(max_workers=len(leagueTeams)) as executor:
            futures = {executor.submit(fetch_team_losses_from_winning, team): team for team in leagueTeams}
            for future in futures:
                results.append(future.result())

        results.sort(key=lambda x: x[1], reverse=True)
        return results

    @staticmethod
    def _get_comeback_win(team_goals, opp_goals):
        """Helper function to determine if a team won from a losing position."""
        team_goals = sorted(team_goals, key=lambda x: parse_time(x.time))
        opp_goals = sorted(opp_goals, key=lambda x: parse_time(x.time))

        team_score = 0
        opp_score = 0
        was_losing = False

        all_events = sorted(team_goals + opp_goals, key=lambda x: parse_time(x.time))
        for event in all_events:
            if event in team_goals:
                team_score += 1
            elif event in opp_goals:
                opp_score += 1

            if team_score < opp_score:
                was_losing = True

        return was_losing and team_score > opp_score

    @staticmethod
    def _get_choke_loss(team_goals, opp_goals):
        """Helper function to determine if a team lost from a winning position."""
        team_goals = sorted(team_goals, key=lambda x: parse_time(x.time))
        opp_goals = sorted(opp_goals, key=lambda x: parse_time(x.time))

        team_score = 0
        opp_score = 0
        was_winning = False

        all_events = sorted(team_goals + opp_goals, key=lambda x: parse_time(x.time))
        for event in all_events:
            if event in team_goals:
                team_score += 1
            elif event in opp_goals:
                opp_score += 1

            if team_score > opp_score:
                was_winning = True

        return was_winning and team_score < opp_score
        
    @staticmethod
    def get_biggest_win(leagueTeams, league_id):
        results = []
        for team in leagueTeams:
            matches = Matches.get_all_played_matches_by_team_and_comp(team.team_id, league_id)
            biggest_win = 0
            match_result = "N/A"
            goals_scored = 0
            for match in matches:
                if match.home_id == team.team_id:
                    goals = match.score_home
                    opp_goals = match.score_away
                else:
                    goals = match.score_away
                    opp_goals = match.score_home

                goal_difference = goals - opp_goals
                if goal_difference > biggest_win or (goal_difference == biggest_win and goals > goals_scored):
                    biggest_win = goal_difference
                    match_result = f"{goals} - {opp_goals}"
                    goals_scored = goals

            if biggest_win == 0:
                results.append((team.team_id, "N/A", 0, 0))
            else:
                results.append((team.team_id, match_result, biggest_win, goals_scored))

        results.sort(key=lambda x: (x[2], x[3]), reverse=True)
        return results

    @staticmethod
    def get_biggest_loss(leagueTeams, league_id):
        results = []
        for team in leagueTeams:
            matches = Matches.get_all_played_matches_by_team_and_comp(team.team_id, league_id)
            biggest_loss = 0
            match_result = "N/A"
            goals_conceded = 0
            for match in matches:
                if match.home_id == team.team_id:
                    goals = match.score_home
                    opp_goals = match.score_away
                else:
                    goals = match.score_away
                    opp_goals = match.score_home

                goal_difference = opp_goals - goals
                if goal_difference > biggest_loss or (goal_difference == biggest_loss and opp_goals > goals_conceded):
                    biggest_loss = goal_difference
                    match_result = f"{goals} - {opp_goals}"
                    goals_conceded = opp_goals

            if biggest_loss == 0:
                results.append((team.team_id, "N/A", 0, 0))
            else:
                results.append((team.team_id, match_result, biggest_loss, goals_conceded))

        results.sort(key=lambda x: (x[2], x[3]), reverse=True)
        return results

    @staticmethod
    def get_home_performance(leagueTeams, league_id):
        results = []
        for team in leagueTeams:
            matches = Matches.get_all_played_matches_by_team_and_comp(team.team_id, league_id)
            points = 0
            available_points = 0
            for match in matches:
                if match.home_id != team.team_id:
                    continue
                if match.score_home > match.score_away:
                    points += 3
                elif match.score_home == match.score_away:
                    points += 1
                available_points += 3
            percentage = 0 if available_points == 0 else points / available_points
            results.append((team.team_id, f"{points}/{available_points}", percentage, available_points))
        results.sort(key=lambda x: (x[2], -x[3] if x[2] == 0 else x[3]), reverse=True)
        return results

    @staticmethod
    def get_away_performance(leagueTeams, league_id):
        results = []
        for team in leagueTeams:
            matches = Matches.get_all_played_matches_by_team_and_comp(team.team_id, league_id)
            points = 0
            available_points = 0
            for match in matches:
                if match.home_id == team.team_id:
                    continue
                if match.score_home < match.score_away:
                    points += 3
                elif match.score_home == match.score_away:
                    points += 1
                available_points += 3
            percentage = 0 if available_points == 0 else points / available_points
            results.append((team.team_id, f"{points}/{available_points}", percentage, available_points))
        results.sort(key=lambda x: (x[2], -x[3] if x[2] == 0 else x[3]), reverse=True)
        return results

    @staticmethod
    def get_longest_unbeaten_run(leagueTeams, league_id):
        results = []
        for team in leagueTeams:
            matches = Matches.get_all_played_matches_by_team_and_comp(team.team_id, league_id)
            unbeaten_run = 0
            current_run = 0
            for match in matches:
                if match.score_home == match.score_away:
                    current_run += 1
                elif match.home_id == team.team_id and match.score_home > match.score_away:
                    current_run += 1
                elif match.away_id == team.team_id and match.score_away > match.score_home:
                    current_run += 1
                else:
                    if current_run > unbeaten_run:
                        unbeaten_run = current_run
                    current_run = 0
            if current_run > unbeaten_run:
                unbeaten_run = current_run
            results.append((team.team_id, unbeaten_run))
        results.sort(key=lambda x: x[1], reverse=True)
        return results

    @staticmethod
    def get_longest_winning_streak(leagueTeams, league_id):
        results = []
        for team in leagueTeams:
            matches = Matches.get_all_played_matches_by_team_and_comp(team.team_id, league_id)
            winning_streak = 0
            current_streak = 0
            for match in matches:
                if match.home_id == team.team_id and match.score_home > match.score_away:
                    current_streak += 1
                elif match.away_id == team.team_id and match.score_away > match.score_home:
                    current_streak += 1
                else:
                    if current_streak > winning_streak:
                        winning_streak = current_streak
                    current_streak = 0
            if current_streak > winning_streak:
                winning_streak = current_streak
            results.append((team.team_id, winning_streak))
        results.sort(key=lambda x: x[1], reverse=True)
        return results

    @staticmethod
    def get_longest_losing_streak(leagueTeams, league_id):
        results = []
        for team in leagueTeams:
            matches = Matches.get_all_played_matches_by_team_and_comp(team.team_id, league_id)
            losing_streak = 0
            current_streak = 0
            for match in matches:
                if match.home_id == team.team_id and match.score_home < match.score_away:
                    current_streak += 1
                elif match.away_id == team.team_id and match.score_away < match.score_home:
                    current_streak += 1
                else:
                    if current_streak > losing_streak:
                        losing_streak = current_streak
                    current_streak = 0
            if current_streak > losing_streak:
                losing_streak = current_streak
            results.append((team.team_id, losing_streak))
        results.sort(key=lambda x: x[1], reverse=True)
        return results

    @staticmethod
    def get_longest_winless_streak(leagueTeams, league_id):
        results = []
        for team in leagueTeams:
            matches = Matches.get_all_played_matches_by_team_and_comp(team.team_id, league_id)
            winless_streak = 0
            current_streak = 0
            for match in matches:
                if match.score_home == match.score_away:
                    current_streak += 1
                elif match.home_id == team.team_id and match.score_home < match.score_away:
                    current_streak += 1
                elif match.away_id == team.team_id and match.score_away < match.score_home:
                    current_streak += 1
                else:
                    if current_streak > winless_streak:
                        winless_streak = current_streak
                    current_streak = 0
            if current_streak > winless_streak:
                winless_streak = current_streak
            results.append((team.team_id, winless_streak))
        results.sort(key=lambda x: x[1], reverse=True)
        return results

    @staticmethod
    def get_longest_scoring_streak(leagueTeams, league_id):
        results = []
        for team in leagueTeams:
            matches = Matches.get_all_played_matches_by_team_and_comp(team.team_id, league_id)
            scoring_streak = 0
            current_streak = 0
            for match in matches:
                if match.home_id == team.team_id and match.score_home > 0:
                    current_streak += 1
                elif match.away_id == team.team_id and match.score_away > 0:
                    current_streak += 1
                else:
                    if current_streak > scoring_streak:
                        scoring_streak = current_streak
                    current_streak = 0
            if current_streak > scoring_streak:
                scoring_streak = current_streak
            results.append((team.team_id, scoring_streak))
        results.sort(key=lambda x: x[1], reverse=True)
        return results

    @staticmethod
    def get_longest_scoreless_streak(leagueTeams, league_id):
        results = []
        for team in leagueTeams:
            matches = Matches.get_all_played_matches_by_team_and_comp(team.team_id, league_id)
            scoreless_streak = 0
            current_streak = 0
            for match in matches:
                if match.home_id == team.team_id and match.score_home == 0:
                    current_streak += 1
                elif match.away_id == team.team_id and match.score_away == 0:
                    current_streak += 1
                else:
                    if current_streak > scoreless_streak:
                        scoreless_streak = current_streak
                    current_streak = 0
            if current_streak > scoreless_streak:
                scoreless_streak = current_streak
            results.append((team.team_id, scoreless_streak))
        results.sort(key=lambda x: x[1], reverse=True)
        return results

    @staticmethod
    def get_highest_possession(leagueTeams, league_id):
        results = []
        for team in leagueTeams:
            matches = Matches.get_all_played_matches_by_team_and_comp(team.team_id, league_id)
            highest_possession = 0
            for match in matches:
                possession_stat = (
                    MatchStats.get_team_stat_in_match(match.id, team.team_id, "Possession")
                )
                if possession_stat:
                    highest_possession = max(highest_possession, possession_stat.value)
            results.append((team.team_id, highest_possession))
        results.sort(key=lambda x: x[1], reverse=True)
        return results

    @staticmethod
    def get_lowest_possession(leagueTeams, league_id):
        results = []
        for team in leagueTeams:
            matches = Matches.get_all_played_matches_by_team_and_comp(team.team_id, league_id)
            lowest_possession = 100
            for match in matches:
                possession_stat = (
                    MatchStats.get_team_stat_in_match(match.id, team.team_id, "Possession")
                )
                if possession_stat:
                    lowest_possession = min(lowest_possession, possession_stat.value)
            if lowest_possession == 100:
                lowest_possession = 0
            results.append((team.team_id, lowest_possession))
        results.sort(key=lambda x: x[1])
        return results

    @staticmethod
    def get_highest_xg(leagueTeams, league_id):
        results = []
        for team in leagueTeams:
            matches = Matches.get_all_played_matches_by_team_and_comp(team.team_id, league_id)
            highest_xg = 0
            for match in matches:
                xg_stat = (
                    MatchStats.get_team_stat_in_match(match.id, team.team_id, "xG")
                )
                if xg_stat:
                    highest_xg = max(highest_xg, xg_stat.value)
            results.append((team.team_id, highest_xg))
        results.sort(key=lambda x: x[1], reverse=True)
        return results

    @staticmethod
    def get_lowest_xg(leagueTeams, league_id):
        results = []
        for team in leagueTeams:
            matches = Matches.get_all_played_matches_by_team_and_comp(team.team_id, league_id)
            lowest_xg = float('inf')
            for match in matches:
                xg_stat = (
                    MatchStats.get_team_stat_in_match(match.id, team.team_id, "xG")
                )
                if xg_stat:
                    lowest_xg = min(lowest_xg, xg_stat.value)
            if lowest_xg == float('inf'):
                lowest_xg = 0
            results.append((team.team_id, lowest_xg))
        results.sort(key=lambda x: x[1])
        return results

    @staticmethod
    def get_team_stats(teamID, league_id, leagueTeams, functions):

        def get_prefix(rank):
            if rank % 10 == 1 and rank % 100 != 11:
                return "st"
            elif rank % 10 == 2 and rank % 100 != 12:
                return "nd"
            elif rank % 10 == 3 and rank % 100 != 13:
                return "rd"
            else:
                return "th"


        stats_result = []
        # Separate slow stats
        slow_stats = ["Winning from losing position", "Losing from winning position"]
        fast_items = [(k, v) for k, v in functions.items() if k not in slow_stats]
        # slow_items = [(k, v) for k, v in functions.items() if k in slow_stats]

        # Run fast stats in parallel
        try:
            with ThreadPoolExecutor() as executor:
                future_to_stat = {
                    executor.submit(stat_func, leagueTeams, league_id): stat_name
                    for stat_name, stat_func in fast_items
                }
                stat_results = {}
                for future in as_completed(future_to_stat):
                    stat_name = future_to_stat[future]
                    try:
                        results = future.result()
                        stat_results[stat_name] = results
                    except Exception:
                        stat_results[stat_name] = None
        except Exception as e:
            logger.exception("Error running stat threads: %s", e)

        # # Run slow stats (each in its own thread, but sequentially after fast stats)
        # for stat_name, stat_func in slow_items:
        #     with ThreadPoolExecutor(max_workers=1) as executor:
        #         future = executor.submit(stat_func, leagueTeams, league_id)
        #         try:
        #             results = future.result()
        #             stat_results[stat_name] = results
        #         except Exception:
        #             stat_results[stat_name] = None

        # Combine results in original order
        for stat_name in functions.keys():
            results = stat_results.get(stat_name)
            if results is None:
                # stats_result.append([stat_name, "N/A", "N/A"])
                continue
            for idx, entry in enumerate(results):
                if entry[0] == teamID:
                    value = entry[1]
                    rank = idx + 1
                    prefix = get_prefix(rank)
                    stats_result.append([stat_name, value, f"{rank}{prefix}"])
                    break
            else:
                stats_result.append([stat_name, "N/A", "N/A"])

        return stats_result

    @staticmethod
    def get_team_top_stats(teamID, num):
        """
        Get the top N players for each statistic (goals, assists, clean sheets, etc.)
        Returns a dictionary with each stat category containing a list of tuples (player_id, stat_value)
        sorted in descending order and limited to the top N players
        """

        # Create a dict of all players with entries for goals, assists, clean sheets, yellow and red cards
        player_stats = defaultdict(lambda: {"goal": 0, "assist": 0, "cleanSheet": 0, "yellowCard": 0, "redCard": 0})
        
        session = DatabaseManager().get_session()
        try:
            # Get team's players
            team_players = session.query(Players.id).filter(Players.team_id == teamID).all()
            team_player_ids = [p.id for p in team_players]

            # Get all matches played by the team
            matches = session.query(Matches.id).filter(
                or_(Matches.home_id == teamID, Matches.away_id == teamID)
            ).all()
            match_ids = [m.id for m in matches]

            # Get events for these matches but only for players in the team
            events = session.query(
                MatchEvents.player_id,
                MatchEvents.event_type
            ).filter(
                MatchEvents.match_id.in_(match_ids),
                MatchEvents.player_id.in_(team_player_ids)
            ).all()

            # Process all events
            for player_id, event_type in events:
                if event_type in ["goal", "penalty_goal"]:
                    player_stats[player_id]["goal"] += 1
                elif event_type == "assist":
                    player_stats[player_id]["assist"] += 1
                elif event_type == "clean_sheet":
                    player_stats[player_id]["cleanSheet"] += 1
                elif event_type == "yellow_card":
                    player_stats[player_id]["yellowCard"] += 1
                elif event_type == "red_card":
                    player_stats[player_id]["redCard"] += 1

            # Convert to dictionary of lists sorted by each stat value
            result = {
                "goal": [],
                "assist": [],
                "cleanSheet": [],
                "yellowCard": [],
                "redCard": []
            }

            # For each stat category, get the top N players
            for stat in result.keys():
                # Sort players by the stat value in descending order
                top_players = sorted(
                    [(pid, stats[stat]) for pid, stats in player_stats.items()],
                    key = lambda x: x[1],
                    reverse = True
                )
                # Take only the top N players with non-zero stats
                result[stat] = [(pid, val) for pid, val in top_players[:num] if val > 0]

            return result
        finally:
            session.close()


def updateProgress(textIndex):
    global progressBar, progressLabel, progressFrame, percentageLabel, PROGRESS
    PROGRESS += 1

    textLabels = [
        "Creating Managers...",
        "Creating Teams...",
        "Creating Players...",
        "Creating Leagues...",
        "Creating Matches...",
        "Finishing up...",
    ]

    if textIndex:
        progressLabel.configure(text = textLabels[textIndex])

        if textIndex == 5:
            progressBar.set(1)

        percentageLabel.configure(text = "100%")
    else:
        percentage = PROGRESS / Managers.total_steps * 100
        progressBar.set(percentage)

        percentageLabel.configure(text = f"{round(percentage)}%")

        
        progressFrame.update_idletasks()

def setUpProgressBar(progressB, progressL, progressF, percentageL):
    global progressBar, progressLabel, progressFrame, percentageLabel

    progressBar = progressB
    progressLabel = progressL
    progressFrame = progressF
    percentageLabel = percentageL

def searchResults(search, limit = SEARCH_LIMIT):
    session = DatabaseManager().get_session()

    try:
        terms = [term.strip().lower() for term in search.split() if term.strip()]
        if not terms:
            return []

        def build_name_filter(cls):

            if hasattr(cls, 'first_name') and hasattr(cls, 'last_name'):
                # If the table is Players, Managers, or Referees, we can use first_name and last_name
                if len(terms) == 1:
                    # If only one term in the search, match either first or last name
                    term = terms[0]
                    return or_(
                        cls.first_name.ilike(f"%{term}%"),
                        cls.last_name.ilike(f"%{term}%")
                    )
                elif len(terms) >= 2:
                    # Otherwise, match both first and last names
                    t1, t2 = terms[0], terms[1]
                    return or_(
                        and_(cls.first_name.ilike(f"%{t1}%"), cls.last_name.ilike(f"%{t2}%")),
                    )
            elif hasattr(cls, 'name'):
                # For the Leagues and Teams, we can use the name field, and match all terms
                return and_(*[cls.name.ilike(f"%{term}%") for term in terms])
            elif cls.__name__.lower() == 'matches':
                team_ids_list = []

                # Try to match the whole query as one team name first
                full_query = " ".join(terms)
                full_match_teams = session.query(Teams).filter(Teams.name.ilike(f"%{full_query}%")).all()
                if full_match_teams:
                    team_ids_list.append([t.id for t in full_match_teams])

                # Also match each individual term to teams
                for term in terms:
                    teams_found = session.query(Teams).filter(Teams.name.ilike(f"%{term}%")).all()
                    if teams_found:
                        team_ids_list.append([t.id for t in teams_found])

                # Remove duplicates
                team_ids_list = [list(set(ids)) for ids in team_ids_list if ids]

                if not team_ids_list:
                    return None

                if len(team_ids_list) != 1:
                    # Multiple possible teams matched
                    all_filters = []
                    for i in range(len(team_ids_list)):
                        for j in range(len(team_ids_list)):
                            if i != j:
                                all_filters.append(
                                    and_(
                                        cls.home_id.in_(team_ids_list[i]),
                                        cls.away_id.in_(team_ids_list[j])
                                    )
                                )
                    return or_(*all_filters)
            
            return None

        def query_players():
            return session.query(Players).filter(
                build_name_filter(Players)
            ).limit(limit).all()

        def query_managers():
            return session.query(Managers).filter(
                build_name_filter(Managers)
            ).limit(limit).all()

        def query_teams():
            return session.query(Teams).filter(
                build_name_filter(Teams)
            ).limit(limit).all()

        def query_leagues():
            return session.query(League).filter(
                build_name_filter(League)
            ).limit(limit).all()

        def query_referees():
            return session.query(Referees).filter(
                build_name_filter(Referees)
            ).limit(limit).all()
        
        def query_matches():
            return session.query(Matches).filter(
                build_name_filter(Matches)
            ).limit(limit).all()

        with ThreadPoolExecutor(max_workers = 5) as executor:
            future_to_type = {
                executor.submit(query_players): 'players',
                executor.submit(query_managers): 'managers',
                executor.submit(query_teams): 'teams',
                executor.submit(query_leagues): 'leagues',
                executor.submit(query_referees): 'referees',
                executor.submit(query_matches): 'matches'
            }

            query_results = {}
            for future in as_completed(future_to_type):
                query_type = future_to_type[future]
                try:
                    query_results[query_type] = future.result()
                except Exception:
                    query_results[query_type] = []

        # Process results
        player_results = [{
            "type": "player",
            "data": p,
            "sort_key": f"{p.first_name or ''} {p.last_name or ''}".strip()
        } for p in query_results['players']]

        manager_results = [{
            "type": "manager",
            "data": m,
            "sort_key": f"{m.first_name or ''} {m.last_name or ''}".strip()
        } for m in query_results['managers']]

        team_results = [{
            "type": "team",
            "data": t,
            "sort_key": t.name or ""
        } for t in query_results['teams']]

        league_results = []
        for l in query_results['leagues']:
            if l.loaded:
                league_results.append({
                    "type": "league",
                    "data": l,
                    "sort_key": l.name or ""
                })

        referee_results = [{
            "type": "referee",
            "data": r, 
            "sort_key": f"{r.first_name or ''} {r.last_name or ''}".strip()
        } for r in query_results['referees']]

        match_results = []
        for m in query_results['matches']:
            league = League.get_league_by_id(m.league_id)
            if league and m.matchday < league.current_matchday:
                match_results.append({
                    "type": "match",
                    "data": m,
                    "sort_key": f"{Teams.get_team_by_id(m.home_id).name} vs {Teams.get_team_by_id(m.away_id).name}"
                })

        combined = (
            player_results + manager_results + team_results +
            league_results + referee_results + match_results
        )
        combined.sort(key = lambda x: x["sort_key"].lower())
        return combined[:limit]

    finally:
        session.close()

def getDefaultLineup(players, youths):
    bestLineup = None
    bestScore = 0

    sortedPlayers = sorted(players, key = lambda p: effective_ability(p), reverse = True)

    for _, positions in FORMATIONS_POSITIONS.items():
        _, _, lineup = score_formation(sortedPlayers, positions, youths)
        formationScore = sum(effective_ability(p) for p in sortedPlayers if p.id in lineup.values())
        if formationScore > bestScore:
            bestScore = formationScore
            bestLineup = lineup

    return bestLineup

def getPredictedLineup(opponent_id, currDate):
    session = DatabaseManager().get_session()
    team = Teams.get_team_by_id(opponent_id)
    league = LeagueTeams.get_league_by_team(team.id)
    matches = Matches.get_team_last_5_matches(team.id, currDate)

    available_players = PlayerBans.get_all_non_banned_players_for_comp(team.id, league.league_id)
    youths = PlayerBans.get_all_non_banned_youth_players_for_comp(team.id, league.league_id)

    if len(matches) == 0:
        bestLineup = getDefaultLineup(available_players, youths)
        return bestLineup

    # Step 1: Find the most used formation
    formation_counts = defaultdict(int)
    most_used_formation = None
    for match in matches:
        lineup = TeamLineup.get_lineup_by_match_and_team(match.id, team.id)
        if lineup:
            positions = [entry.start_position for entry in lineup if entry.start_position is not None]

            if not positions or len(positions) < 11:
                continue

            formation = next(form for form, pos in FORMATIONS_POSITIONS.items() if set(pos) == set(positions))
            formation_counts[formation] += 1

    most_used_formation = max(formation_counts.items(), key = lambda x: x[1])[0] if formation_counts else None
    if not most_used_formation:
        bestLineup = getDefaultLineup(available_players, youths)
        return bestLineup
    
    # Step 3: For each position in the formation, find most started player
    predicted_lineup = {}
    positions = FORMATIONS_POSITIONS[most_used_formation]

    for position in positions:
        # Find players who can play in this position
        position_players = []
        for player in available_players:
            if POSITION_CODES[position] in player.specific_positions.split(","):
                position_players.append(player)

        if not position_players:
            # Get a youth player if no senior players are available
            youth = getYouthPlayer(position, predicted_lineup.values(), youths)
            if youth:
                predicted_lineup[position] = youth
        else:
            # Count starts in this position
            player_starts = defaultdict(int)
            for match in matches:
                lineup = TeamLineup.get_lineup_by_match_and_team(match.id, team.id)
                if lineup:
                    for entry in lineup:
                        if entry.start_position == position and entry.player_id in [p.id for p in position_players]:
                            player_starts[entry.player_id] += 1

            # Select most started player
            if player_starts:
                most_started_id = max(player_starts.items(), key = lambda x: x[1])[0]
                selected_player = next(p for p in position_players if p.id == most_started_id)
            else:
                # Choose by effective ability first
                selected_player = max(position_players, key = lambda p: effective_ability(p))

            predicted_lineup[position] = selected_player.id

    session.close()

    return predicted_lineup

def getProposedLineup(team_id, opponent_id, comp_id, currDate, players = None, youths = None):
    if not players:
        players = PlayerBans.get_all_non_banned_players_for_comp(team_id, comp_id)
    
    if not youths:
        youths = PlayerBans.get_all_non_banned_youth_players_for_comp(team_id, comp_id)

    predictedLineup = getPredictedLineup(opponent_id, currDate)

    attackingScore = 0
    defendingScore = 0

    for position, playerID in predictedLineup.items():
        player = Players.get_player_by_id(playerID)
        if position in DEFENSIVE_POSITIONS:
            defendingScore += effective_ability(player)
        elif position in ATTACKING_POSITIONS:
            attackingScore += effective_ability(player)

    sortedPlayers = sorted(players, key = lambda p: effective_ability(p), reverse = True)

    bestLineup = None
    bestTotalScore = -1
    lineupPositions = None

    for _, positions in FORMATIONS_POSITIONS.items():
        aScore, dScore, lineup = score_formation(sortedPlayers, positions, youths)
        if not lineup:
            continue  # skip incomplete formations

        buffer = 0.2 * attackingScore
        if aScore + buffer < attackingScore or dScore + buffer < defendingScore:
            continue

        # Total ability including midfielders
        totalScore = sum(effective_ability(p) for p in sortedPlayers if p.id in lineup.values())

        if totalScore > bestTotalScore:
            bestTotalScore = totalScore
            bestLineup = lineup
            lineupPositions = positions

    if not bestLineup:
        bestScore = -1
        for _, positions in FORMATIONS_POSITIONS.items():
            _, _, lineup = score_formation(sortedPlayers, positions, youths)
            formationScore = sum(effective_ability(p) for p in sortedPlayers if p.id in lineup.values())
            if formationScore > bestScore:
                bestScore = formationScore
                bestLineup = lineup
                lineupPositions = positions

    ordered_lineup = {pos: bestLineup[pos] for pos in lineupPositions if pos in bestLineup}
    return ordered_lineup

def parse_formation_key(key: str):
    # extract first 3 numbers (defenders-midfielders-attackers)
    nums = re.findall(r"\d+", key)
    if len(nums) >= 3:
        defenders, mids, attackers = map(int, nums[:3])
    else:
        raise ValueError(f"Formation key {key} doesn't match expected format")

    return defenders, mids, attackers

def score_formation(sortedPlayers, positions, youths):
    lineup = {}
    used = set()

    # Count how many players can fill each slot
    position_candidates = {}
    for pos in positions:
        position_candidates[pos] = [p for p in sortedPlayers if POSITION_CODES[pos] in p.specific_positions.split(",")]

    # Sort positions by "scarcity" (fewest candidates first)
    ordered_positions = sorted(positions, key = lambda pos: len(position_candidates[pos]))

    attackingScore = 0
    defendingScore = 0

    # Assign players greedily starting with scarce positions
    for pos in ordered_positions:
        candidates = [p for p in position_candidates[pos] if p.id not in used]
        
        if not candidates:
            youthID = getYouthPlayer(pos, lineup.values(), youths)

            if not youthID:
                return -1, {}

            lineup[pos] = youthID
            used.add(youthID)
            chosen = Players.get_player_by_id(youthID)
        else:
            # Find candidates that are "specialists" for this position, given the rest of the lineup
            specialists = []
            for p in candidates:
                playable_positions = p.specific_positions.split(",")
                
                other_positions = [
                    pos_code for pos_code in playable_positions
                    if pos_code != POSITION_CODES[pos] 
                    and pos_code in [POSITION_CODES[x] for x in ordered_positions if x not in lineup]
                ]
                
                # If any other position this player can play is still unassigned, they're "flexible"
                if not any(other_pos in [POSITION_CODES[x] for x in ordered_positions if x not in lineup] for other_pos in other_positions):
                    specialists.append(p)

            # If there are specialists, pick the best one; otherwise, pick the best overall (already sorted)
            if specialists:
                chosen = specialists[0]
            else:
                chosen = candidates[0]

            lineup[pos] = chosen.id
            used.add(chosen.id)

        if pos in ATTACKING_POSITIONS:
            attackingScore += effective_ability(chosen)
        elif pos in DEFENSIVE_POSITIONS:
            defendingScore += effective_ability(chosen)

    # Check if all positions are filled
    if len(lineup) != len(positions):
        return -1, {}  # incomplete formation, skip

    return attackingScore, defendingScore, lineup

def getYouthPlayer(position, players, youthPlayers):
    available_youths = []

    if youthPlayers:
        for player in youthPlayers:
            if POSITION_CODES[position] in player.specific_positions and player.id not in players:
                available_youths.append(player)

    available_youths.sort(key = effective_ability, reverse = True)
    return available_youths[0].id if available_youths else None

def getSubstitutes(teamID, lineup, compID, allPlayers, allYouths):
    if not allPlayers:
        allPlayers = PlayerBans.get_all_non_banned_players_for_comp(teamID, compID)

    if not allYouths:
        allYouths = PlayerBans.get_all_non_banned_youth_players_for_comp(teamID, compID)

    usedPlayers = set(lineup.values())
    substitutes = []

    # positions already covered (from lineup and subs)
    covered_positions = set(lineup.keys())

    # helper to pick a sub for a given general position
    def pick_sub(players, count, position_pool):
        nonlocal covered_positions
        added = 0
        for p in players:
            if p.id in usedPlayers or p.id in substitutes:
                continue

            # find sub positions not already covered
            sub_positions = [REVERSE_POSITION_CODES[code][0] for code in p.specific_positions.split(",")]
            available_positions = [pos for pos in sub_positions if pos not in covered_positions and pos in position_pool]

            if available_positions:
                substitutes.append(p.id)
                covered_positions.add(available_positions[0])
                added += 1
                if added >= count:
                    break
        return added

    # --- Split players by general position ---
    goalkeepers = [p for p in allPlayers if p.position == "goalkeeper"]
    defenders   = [p for p in allPlayers if p.position == "defender"]
    midfielders = [p for p in allPlayers if p.position == "midfielder"]
    attackers   = [p for p in allPlayers if p.position == "forward"]

    # Order by effective ability
    goalkeepers.sort(key=effective_ability, reverse=True)
    defenders.sort(key=effective_ability, reverse=True)
    midfielders.sort(key=effective_ability, reverse=True)
    attackers.sort(key=effective_ability, reverse=True)

    # --- Pick subs as we go ---
    if pick_sub(goalkeepers, 1, DEFENSIVE_POSITIONS) < 1:
        youthID = getYouthPlayer("Goalkeeper", substitutes, allYouths)
        if youthID:
            substitutes.append(youthID)
            covered_positions.add("Goalkeeper")

    if pick_sub(defenders, 2, DEFENDER_POSITIONS) < 2:
        for _ in range(2 - len([s for s in substitutes if s in [p.id for p in defenders]])):
            uncovered_positions = [p for p in DEFENDER_POSITIONS if p not in covered_positions]
            if uncovered_positions:
                specific_position = random.choice(uncovered_positions)
                youthID = getYouthPlayer(specific_position, substitutes, allYouths)
                if youthID:
                    substitutes.append(youthID)
                    covered_positions.add(specific_position)

    if pick_sub(midfielders, 2, MIDFIELD_POSITIONS) < 2:
        for _ in range(2 - len([s for s in substitutes if s in [p.id for p in midfielders]])):
            uncovered_positions = [p for p in MIDFIELD_POSITIONS if p not in covered_positions]
            if uncovered_positions:
                specific_position = random.choice(uncovered_positions)
                youthID = getYouthPlayer(specific_position, substitutes, allYouths)
                if youthID:
                    substitutes.append(youthID)
                    covered_positions.add(specific_position)

    if pick_sub(attackers, 2, FORWARD_POSITIONS) < 2:
        for _ in range(2 - len([s for s in substitutes if s in [p.id for p in attackers]])):
            uncovered_positions = [p for p in FORWARD_POSITIONS if p not in covered_positions]
            if uncovered_positions:
                specific_position = random.choice(uncovered_positions)
                youthID = getYouthPlayer(specific_position, substitutes, allYouths)
                if youthID:
                    substitutes.append(youthID)
                    covered_positions.add(specific_position)

    # --- SAFETY NET: Fill remaining subs if fewer than 7 ---
    all_available = [p for p in allPlayers if p.id not in usedPlayers and p.id not in substitutes]
    all_available.sort(key = effective_ability, reverse = True)
    while len(substitutes) < 7 and all_available:
        sub = all_available.pop(0)
        substitutes.append(sub.id)

    # Final fallback: fill remaining slots with youth players if still not full
    while len(substitutes) < 7:
        pos_choice = random.choice(DEFENSIVE_POSITIONS + MIDFIELD_POSITIONS + FORWARD_POSITIONS)
        youthID = getYouthPlayer(pos_choice, substitutes, allYouths)
        if youthID:
            substitutes.append(youthID)
        else:
            break  # can't fill more

    return substitutes

def update_ages(start_date, end_date):
    session = DatabaseManager().get_session()
    try:
        # Ensure we work with date objects (if datetimes were passed)
        start = start_date.date() if hasattr(start_date, 'date') else start_date
        end = end_date.date() if hasattr(end_date, 'date') else end_date

        # Build set of (month, day) pairs in [start, end) (exclusive end)
        curr = start
        md_pairs = set()
        while True:
            md_pairs.add((curr.month, curr.day))
            if curr == end:
                break
            curr = curr + datetime.timedelta(days = 1)

        def get_conditions(cls_table):
            return [
                and_(
                    extract('month', cls_table.date_of_birth) == m,
                    extract('day', cls_table.date_of_birth) == d
                )
                for (m, d) in md_pairs
            ]

        # Helper to update a table
        def update_table(cls_table):
            conditions = get_conditions(cls_table)
            if conditions:
                people = session.query(cls_table).filter(or_(*conditions)).all()
                for person in people:
                    correct_age = calculate_age(person.date_of_birth, end)
                    if person.age < correct_age:
                        person.age = correct_age

        # Update all relevant tables
        for table in [Players, Managers, Referees]:
            update_table(table)

        session.commit()
    finally:
        session.close()

def check_player_games_happy(teamID, currDate):
    
    payload = {
        "players_to_update": [],
        "emails_to_send": []
    }

    players = Players.get_all_players_by_team(teamID, youths = False)
    players = [p for p in players if p.player_role != "Backup" and p.morale > 25]
    matches = Matches.get_all_played_matches_by_team(teamID, currDate)
    user = Managers.get_all_user_managers()[0]
    managed_team = Teams.get_teams_by_manager(user.id)[0]

    for player in players:

        matchesToCheck = MATCHES_ROLES[player.player_role]
        matches = [m for m in matches if not TeamLineup.check_player_availability(player.id, m.id)]

        if len(matches) < matchesToCheck:
            continue

        last_matches = matches[-matchesToCheck:]  # last n matches
        avg_minutes = sum(MatchEvents.get_player_game_time(player.id, match.id) for match in last_matches) / matchesToCheck

        if player_gametime(avg_minutes, player):
            # reduced = Players.reduce_morale_to_25(player.id)
            payload["players_to_update"].append(player.id)

            if teamID == managed_team.id:
                email_date = currDate + timedelta(days = 1)
                payload["emails_to_send"].append(("player_games_issue", None, player.id, None, None, email_date.replace(hour = 8, minute = 0, second = 0, microsecond = 0)))
                # Emails.add_email("player_games_issue", None, player.id, None, None, email_date.replace(hour = 8, minute = 0, second = 0, microsecond = 0))

    return payload

def create_events_for_other_teams(team_id, start_date, managing_team):
    end_date = start_date + timedelta(days=7)
    matches = Matches.get_match_by_team_and_date_range(team_id, start_date, end_date)

    match_days = {getDayIndex(match.date) for match in matches}
    weekly_usage = {event: 0 for event in MAX_EVENTS}
    planned_events = defaultdict(list)  # store per day

    if managing_team:
        CalendarEvents.delete_events_for_team_in_date_range(team_id, start_date, end_date)

    current_date = start_date
    while current_date.date() < end_date.date():
        events = []

        templates = [TEMPLATES_2.copy(), TEMPLATES_3.copy()]

        is_prep = getDayIndex(current_date + timedelta(days=1)) in match_days
        is_match = getDayIndex(current_date) in match_days

        if getDayIndex(current_date) == 0:
            is_review = Matches.check_if_game_date(team_id, current_date - timedelta(days=1))
        else:
            is_review = getDayIndex(current_date - timedelta(days=1)) in match_days

        if not is_match:
            if is_review or is_prep:
                date_check = current_date - timedelta(days=1) if is_review else current_date + timedelta(days=1)
                is_home = Matches.get_team_match_no_time(team_id, date_check).home_id == team_id

                if is_home:
                    possible = [e for e in MAX_EVENTS if weekly_usage[e] < MAX_EVENTS[e] and e != "Recovery"]
                    event = random.choice(possible) if possible else None

                    if is_review:
                        events = ["Match Review", "Recovery"] + ([event] if event else [])
                    elif is_prep:
                        events = ([event] if event else []) + ["Recovery", "Match Preparation"]

                        weekly_usage["Recovery"] += 1
                else:
                    if is_review:
                        events = ["Travel", "Match Review", "Recovery"]
                    elif is_prep:
                        events = ["Recovery", "Travel", "Match Preparation"]
                    
                        weekly_usage["Recovery"] += 1
            else:
                template_group = random.choice(templates)

                if len(template_group) == 0:
                    template_group = templates[0] if templates[0] != template_group else templates[1]
                if len(template_group) == 0:
                    current_date += timedelta(days=1)
                    continue

                template = random.choice(template_group)
                for t_event in template:
                    if weekly_usage[t_event] < MAX_EVENTS[t_event]:
                        events.append(t_event)
                        weekly_usage[t_event] += 1
                template_group.remove(template)

            planned_events[current_date.date()] = events[:3]

        current_date += timedelta(days=1)

    # === SECOND PASS: fill in recoveries and insert ===
    return_events = []
    recoveries_needed = max(0, 2 - weekly_usage["Recovery"])
    if recoveries_needed > 0:
        sorted_days = sorted(planned_events.keys(), reverse = True)
        for day in sorted_days:
            if recoveries_needed == 0:
                break

            events = planned_events[day]

            # Replace last event if possible
            if events and "Recovery" not in events and events[-1] not in ("Travel", "Match Preparation"):
                weekly_usage[events[-1]] -= 1
                events[-1] = "Recovery"
                weekly_usage["Recovery"] += 1
                recoveries_needed -= 1
            elif not events:
                planned_events[day].append("Recovery")
                weekly_usage["Recovery"] += 1
                recoveries_needed -= 1

    for day, events in planned_events.items():
        eventsToAdd = []
        for i, event in enumerate(events):
            startHour, endHour = EVENT_TIMES[i]
            startDate = datetime.datetime.combine(day, datetime.datetime.min.time()).replace(hour=startHour)
            endDate = datetime.datetime.combine(day, datetime.datetime.min.time()).replace(hour=endHour)

            eventsToAdd.append(
                (team_id, event, startDate, endDate, True if event == "Travel" else False)
            )

        if len(eventsToAdd) != 0:
            return_events.extend(eventsToAdd)

    return return_events

def teamStrength(playerIDs, role, playerOBJs):
    if not playerIDs:
        return 0

    abilities = [playerOBJs[pid].current_ability for pid in playerIDs]
    if role == "attack":
        abilities = [a ** 1.05 for a in abilities]

    geom_mean = math.exp(sum(math.log(a + 1e-9) for a in abilities) / len(abilities))
    return geom_mean * (1 + 0.1 * math.log(len(abilities) + 1))

def process_payload(payload):
    try: 
        call_if_not_empty(payload["team_updates"], LeagueTeams.batch_update_teams)
        call_if_not_empty(payload["manager_updates"], Managers.batch_update_managers)
        call_if_not_empty(payload["match_events"], MatchEvents.batch_add_events)
        call_if_not_empty(payload["score_updates"], Matches.batch_update_scores)
        call_if_not_empty(payload["fitness_updates"], Players.batch_update_fitness)
        call_if_not_empty(payload["sharpness_updates"], Players.batch_update_sharpnesses)
        call_if_not_empty(payload["morale_updates"], Players.batch_update_morales)
        call_if_not_empty(payload["lineup_updates"], TeamLineup.batch_add_lineups)
        call_if_not_empty(payload["stats_updates"], MatchStats.batch_add_stats)

        if "players_to_update" in payload:
            call_if_not_empty(payload["players_to_update"], Players.batch_reduce_morales_to_25)
            call_if_not_empty(payload["emails_to_send"], Emails.batch_add_emails)

        for ban in payload["player_bans"]:

            player_id, competition_id, ban_length, ban_type, date = ban

            sendEmail = PlayerBans.add_player_ban(player_id, competition_id, ban_length, ban_type, date)
            player = Players.get_player_by_id(player_id)
            userTeam = Teams.get_teams_by_manager(Managers.get_all_user_managers()[0].id)[0]

            if player.team_id == userTeam.id and sendEmail:
                emailDate = date + timedelta(days = 1)
                if ban_type == "injury":
                    Emails.add_email("player_injury", None, player_id, ban_length, None, emailDate.replace(hour = 8, minute = 0, second = 0, microsecond = 0))
                else:
                    Emails.add_email("player_ban", None, player_id, ban_length, competition_id, emailDate.replace(hour = 8, minute = 0, second = 0, microsecond = 0))

        for check in payload["yellow_card_checks"]:

            player_id, competition_id, threshold, date = check
            MatchEvents.check_yellow_card_ban(player_id, competition_id, threshold, date)

    except Exception as e:
        print(f"Error updating teams: {e}")

def call_if_not_empty(data, func):
    if data:
        func(data)