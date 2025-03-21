from sqlalchemy import Column, Integer, String, BLOB, ForeignKey, Boolean, insert
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, func, case, or_
from sqlalchemy.orm import sessionmaker, aliased, scoped_session
from sqlalchemy.types import Enum
import uuid, json, random
from faker import Faker
from settings import *

Base = declarative_base()

LEAGUE_NAME = "Eclipse League"
FIRST_YEAR = 2024
NUM_TEAMS = 20

TOTAL_STEPS = 1003
PROGRESS = 0

progressBar = None
progressLabel = None
progressFrame = None
percentageLabel = None

class DatabaseManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance.database_name = None
            cls._instance.scoped_session = None
        return cls._instance

    def set_database(self, database_name, create_tables = False):

        self.database_name = database_name
        DATABASE_URL = f"sqlite:///data/{database_name}.db"
        engine = create_engine(DATABASE_URL, connect_args = {"check_same_thread": False})
        session_factory = sessionmaker(autocommit = False, autoflush = False, bind = engine)
        self.scoped_session = scoped_session(session_factory)  # One session per thread

        if create_tables:
            Base.metadata.create_all(bind = engine)

    def get_session(self):
        """Return the shared session per thread."""
        if not self.scoped_session:
            raise ValueError("Database has not been set. Call set_database() first.")
        return self.scoped_session()

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
    date_of_birth = Column(String(128), nullable = False)
    age = Column(Integer, nullable = False)

    @classmethod
    def add_manager(cls, first_name = None, last_name = None, nationality = None, date_of_birth = None, user = False, chosenTeam = None):
        session = DatabaseManager().get_session()
        try:
            if user:
                new_manager  =  Managers(
                    id = str(uuid.uuid4()),
                    first_name = first_name,
                    last_name = last_name,
                    nationality = nationality,
                    user = user,
                    date_of_birth = date_of_birth,
                    age = 2024 - date_of_birth.year
                )
            else:
                selectedContinent = random.choices(list(continentWeights.keys()), weights = list(continentWeights.values()), k = 1)[0]
                country = random.choices(list(COUNTRIES[selectedContinent][1].keys()), weights = list(COUNTRIES[selectedContinent][1].values()), k = 1)[0]
                date_of_birth = Faker().date_of_birth(minimum_age = 32, maximum_age = 65)
                new_manager = Managers(
                    id = str(uuid.uuid4()),
                    first_name = Faker().first_name_male(),
                    last_name = Faker().first_name(),
                    nationality = country,
                    date_of_birth = date_of_birth,
                    age = 2024 - date_of_birth.year,
                    user = user
                )

            with open(f"Images/Countries/{new_manager.nationality.lower()}.png", 'rb') as file:
                new_manager.flag  =  file.read()

            managerID = new_manager.id

            session.add(new_manager)
            session.commit()
            updateProgress(1)

            if user:
                Teams.add_teams(chosenTeam, new_manager.first_name, new_manager.last_name, managerID)
                updateProgress(2)
                Referees.add_referees()
                updateProgress(3)
                League.add_league(LEAGUE_NAME, FIRST_YEAR, 0, 3)
                updateProgress(None)

            return managerID
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
    level = Column(Integer, nullable = False)

    @classmethod
    def add_teams(cls, chosenTeamName, manager_first_name, manager_last_name, manager_id):
        session = DatabaseManager().get_session()
        try:
            with open("data/teams.json", 'r') as file:
                data = json.load(file)

            for team in data:
                name = team['name']
                year_created = team['year_created']
                stadium = team['stadium']
                level = team['level']

                with open(f"Images/Teams/{name}.png", 'rb') as file:
                    logo = file.read()

                if name != chosenTeamName:
                    managerID = Managers.add_manager()
                else:
                    managerID = manager_id 

                new_team = Teams(
                    id = str(uuid.uuid4()),
                    manager_id = managerID,
                    name = name,
                    year_created = year_created,
                    stadium = stadium,
                    level = level,
                    logo = logo
                )

                updateProgress(None)
                Players.add_players(new_team.id)

                session.add(new_team)

            session.commit()
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
            return [team.id for team in teams]
        finally:
            session.close()

    @classmethod
    def update_level(cls, id, level):
        session = DatabaseManager().get_session()
        try:
            team = session.query(Teams).filter(Teams.id == id).first()
            if team:
                team.level = level
                session.commit()
            else:
                return None
        finally:
            session.close()

class Players(Base):
    __tablename__ = 'players'

    id = Column(String(256), primary_key = True, default = lambda: str(uuid.uuid4()))
    team_id = Column(String(128), ForeignKey('teams.id'))
    first_name = Column(String(128), nullable = False)
    last_name = Column(String(128), nullable = False)
    number = Column(Integer, nullable = False)
    position = Column(Enum("goalkeeper", "defender", "midfielder", "forward"), nullable = False)
    specific_positions = Column(String(128), nullable = False)
    date_of_birth = Column(String(128), nullable = False)
    age = Column(Integer, nullable = False)
    nationality = Column(String(128), nullable = False)
    flag = Column(BLOB)
    morale = Column(Integer, nullable = False, default = 50)
    player_role = Column(Enum("Star player", "Youngster", "Backup", "Rotation", "First Team", "Youth Team"), nullable = False)

    @classmethod
    def add_player_entry(cls, data):
        session = DatabaseManager().get_session()
        try:
            session.add(data)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @classmethod
    def add_player(cls, team_id, position, required_position, role):
        session = DatabaseManager().get_session()
        try:
            selectedContinent = random.choices(list(continentWeights.keys()), weights = list(continentWeights.values()), k = 1)[0]
            _, countryWeights = COUNTRIES[selectedContinent]
            country = random.choices(list(countryWeights.keys()), weights = list(countryWeights.values()), k = 1)[0]

            with open(f"Images/Countries/{country.lower()}.png", 'rb') as file:
                flag = file.read()

            faker = Faker()
            date_of_birth = faker.date_of_birth(minimum_age = 15, maximum_age = 17)
            new_player = Players(
                id = str(uuid.uuid4()),
                team_id = team_id,
                first_name = faker.first_name_male(),
                last_name = faker.last_name(),
                number = random.randint(1, 99),
                position = position,
                date_of_birth = str(date_of_birth),
                age = 2024 - date_of_birth.year,
                nationality = country,
                flag = flag,
                player_role = role,
            )

            existing_numbers = {player.number for player in Players.get_all_players_by_team(team_id)}
            while new_player.number in existing_numbers:
                new_player.number = random.randint(1, 99)

            specific_positions = {
                "goalkeeper": ["GK"],
                "defender": ["RB", "CB", "LB"],
                "midfielder": ["DM", "CM", "RM", "LM"],
                "forward": ["LW", "CF", "RW", "AM"]
            }

            required_code = POSITION_CODES[required_position]
            player_positions = [required_code]

            if position in specific_positions:
                other_positions = specific_positions[position]
                other_positions.remove(required_code)
                if len(other_positions) > 0:
                    num_other_positions = random.randint(1, len(other_positions))
                    player_positions.extend(random.sample(other_positions, num_other_positions))

            new_player.specific_positions = ','.join(player_positions)

            session.add(new_player)
            session.commit()

            return new_player.id
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @classmethod
    def add_players(cls, team_id):
        session = DatabaseManager().get_session()
        try:
            positions = {
                "goalkeeper": 3,
                "defender": 8,
                "midfielder": 8,
                "forward": 6
            }

            specific_positions = {
                "goalkeeper": ["GK"],
                "defender": ["RB", "CB", "LB"],
                "midfielder": ["DM", "CM", "RM", "LM", "AM"],
                "forward": ["LW", "CF", "RW"]
            }

            player_role_counts = {
                "Star player": 4,
                "First Team": 11,
                "Rotation": 8
            }

            numbers = []
            faker = Faker()

            gk_assigned = False

            position_weights = [0.4, 0.3, 0.2, 0.1]

            for overall_position, specific_pos_list in specific_positions.items():
                for specific_pos in specific_pos_list:
                    selectedContinent = random.choices(list(continentWeights.keys()), weights = list(continentWeights.values()), k = 1)[0]
                    _, countryWeights = COUNTRIES[selectedContinent]
                    country = random.choices(list(countryWeights.keys()), weights = list(countryWeights.values()), k = 1)[0]

                    with open(f"Images/Countries/{country.lower()}.png", 'rb') as file:
                        flag = file.read()

                    date_of_birth = faker.date_of_birth(minimum_age = 18, maximum_age = 35)
                    new_player = Players(
                        team_id = team_id,
                        first_name = faker.first_name_male(),
                        last_name = faker.last_name(),
                        number = random.randint(1, 99),
                        position = overall_position,
                        date_of_birth = str(date_of_birth),
                        age = 2024 - date_of_birth.year,
                        nationality = country,
                        flag = flag
                    )

                    num_positions = random.choices(range(1, min(len(specific_pos_list), 4) + 1), weights = position_weights[:min(len(specific_pos_list), 4)])[0]
                    new_player_positions = random.sample(specific_pos_list, k = num_positions)
                    if specific_pos not in new_player_positions:
                        new_player_positions[0] = specific_pos
                    new_player.specific_positions = ','.join(new_player_positions)

                    while new_player.number in numbers:
                        new_player.number = random.randint(1, 99)

                    numbers.append(new_player.number)

                    if new_player.age <= 21:
                        new_player.player_role = "Youngster"
                    elif overall_position == "goalkeeper":
                        if not gk_assigned:
                            new_player.player_role = "First Team"
                            gk_assigned = True
                        else:
                            new_player.player_role = "Backup"
                    else:
                        available_roles = [role for role, count in player_role_counts.items() if count > 0]
                        if available_roles:
                            chosen_role = random.choice(available_roles)
                            new_player.player_role = chosen_role
                            player_role_counts[chosen_role] -= 1

                    session.add(new_player)
                    updateProgress(None)

            for overall_position, count in positions.items():
                for _ in range(count - len(specific_positions[overall_position])):
                    selectedContinent = random.choices(list(continentWeights.keys()), weights = list(continentWeights.values()), k = 1)[0]
                    continent, countryWeights = COUNTRIES[selectedContinent]
                    country = random.choices(list(countryWeights.keys()), weights = list(countryWeights.values()), k = 1)[0]

                    with open(f"Images/Countries/{country.lower()}.png", 'rb') as file:
                        flag = file.read()

                    date_of_birth = faker.date_of_birth(minimum_age = 18, maximum_age = 35)
                    new_player = Players(
                        team_id = team_id,
                        first_name = faker.first_name_male(),
                        last_name = faker.last_name(),
                        number = random.randint(1, 99),
                        position = overall_position,
                        date_of_birth = str(date_of_birth),
                        age = 2024 - date_of_birth.year,
                        nationality = country,
                        flag = flag 
                    )

                    num_positions = random.choices(range(1, min(len(specific_positions[overall_position]), 4) + 1), weights = position_weights[:min(len(specific_positions[overall_position]), 4)])[0]
                    new_player_positions = random.sample(specific_positions[overall_position], k = num_positions)
                    new_player.specific_positions = ','.join(new_player_positions)

                    while new_player.number in numbers:
                        new_player.number = random.randint(1, 99)

                    numbers.append(new_player.number)

                    if new_player.age <= 21:
                        new_player.player_role = "Youngster"
                    elif overall_position == "goalkeeper":
                        if not gk_assigned:
                            new_player.player_role = "First Team"
                            gk_assigned = True
                        else:
                            new_player.player_role = "Backup"
                    else:
                        available_roles = [role for role, count in player_role_counts.items() if count > 0]
                        if available_roles:
                            chosen_role = random.choice(available_roles)
                            new_player.player_role = chosen_role
                            player_role_counts[chosen_role] -= 1

                    session.add(new_player)
                    updateProgress(None)

            session.commit()
        except Exception as e:
            session.rollback()
            raise e
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
    def get_player_manager(cls, id):
        session = DatabaseManager().get_session()
        try:
            player = cls.get_player_by_id(id)
            if not player:
                return None

            team = Teams.get_team_by_id(player.team_id)
            if not team:
                return None

            manager = Managers.get_manager_by_id(team.manager_id)
            return manager
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
                    (Players.position == 'forward', 4)
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
            players = session.query(Players).filter(Players.team_id == team_id, Players.player_role == 'Star player').all()
            return players
        finally:
            session.close()

    @classmethod
    def get_all_youngsters(cls, team_id):
        session = DatabaseManager().get_session()
        try:
            players = session.query(Players).filter(Players.team_id == team_id, Players.player_role == 'Youngster').all()
            return players
        finally:
            session.close()

    @classmethod
    def get_all_defenders(cls, team_id):
        session = DatabaseManager().get_session()
        try:
            role_order = case(
                [(Players.player_role == 'Star player', 1),
                (Players.player_role == 'First Team', 2),
                (Players.player_role == 'Rotation', 3)],
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
                [(Players.player_role == 'Star player', 1),
                (Players.player_role == 'First Team', 2),
                (Players.player_role == 'Rotation', 3)],
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
                [(Players.player_role == 'Star player', 1),
                (Players.player_role == 'First Team', 2),
                (Players.player_role == 'Rotation', 3)],
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
                [(Players.player_role == 'First Team', 1),
                (Players.player_role == 'Backup', 2)],
                else_ = 3
            )

            goalkeepers = session.query(Players).filter(Players.team_id == team_id, Players.position == 'goalkeeper').order_by(role_order).all()
            return goalkeepers
        finally:
            session.close()

class Matches(Base):
    __tablename__ = 'matches'
    
    id = Column(String(256), primary_key = True, default = lambda: str(uuid.uuid4()))
    league_id = Column(String(128), ForeignKey('leagues.id'))
    home_id = Column(String(128), ForeignKey('teams.id'))
    away_id = Column(String(128), ForeignKey('teams.id'))
    time = Column(String(128), nullable = False)
    referee_id = Column(String(128), ForeignKey('referees.id'))
    score_home = Column(Integer, nullable = False, default = 0)
    score_away = Column(Integer, nullable = False, default = 0)
    matchday = Column(Integer, nullable = False)

    @classmethod
    def add_match(cls, league_id, home_id, away_id, referee_id, matchday):
        session = DatabaseManager().get_session()
        try:
            times = ["12:30", "13:00", "14:00", "15:00", "17:00", "19:00", "20:00"]

            new_match = Matches(
                league_id = league_id,
                home_id = home_id,
                away_id = away_id,
                time = random.choices(times, k = 1)[0],
                referee_id = referee_id,
                matchday = matchday
            )

            session.add(new_match)
            session.commit()
            updateProgress(None)

            return new_match
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
    def get_team_next_match(cls, team_id, league_id):
        session = DatabaseManager().get_session()
        try:
            current_matchday = session.query(League).filter(League.id == league_id).first().current_matchday
            match = session.query(Matches).filter(
                (Matches.home_id == team_id) | (Matches.away_id == team_id),
                Matches.matchday == current_matchday
            ).first()
            return match
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
            match = session.query(Matches).filter(
                (Matches.home_id == team_id) | (Matches.away_id == team_id),
                Matches.matchday == 1
            ).first()
            return match
        finally:
            session.close()

    @classmethod
    def get_team_last_match(cls, team_id, league_id):
        session = DatabaseManager().get_session()
        try:
            current_matchday = session.query(League).filter(League.id == league_id).first().current_matchday
            match = session.query(Matches).join(TeamLineup, TeamLineup.match_id == Matches.id).filter(
                (Matches.home_id == team_id) | (Matches.away_id == team_id),
                Matches.matchday == current_matchday - 1
            ).first()
            return match
        finally:
            session.close()

    @classmethod
    def get_team_last_match_from_matchday(cls, team_id, matchday):
        session = DatabaseManager().get_session()
        try:
            match = session.query(Matches).join(TeamLineup, TeamLineup.match_id == Matches.id).filter(
                (Matches.home_id == team_id) | (Matches.away_id == team_id),
                Matches.matchday == matchday - 1
            ).first()
            return match
        finally:
            session.close()

    @classmethod
    def get_team_next_5_matches(cls, team_id, league_id):
        session = DatabaseManager().get_session()
        try:
            current_matchday = session.query(League).filter(League.id == league_id).first().current_matchday
            matches = session.query(Matches).filter(
                (Matches.home_id == team_id) | (Matches.away_id == team_id),
                Matches.matchday >= current_matchday,
                Matches.matchday < current_matchday + 5
            ).all()
            return matches
        finally:
            session.close()

    @classmethod
    def get_team_last_5_matches(cls, team_id, league_id):
        session = DatabaseManager().get_session()
        try:
            current_matchday = session.query(League).filter(League.id == league_id).first().current_matchday
            matches = session.query(Matches).join(TeamLineup, TeamLineup.match_id == Matches.id).filter(
                (Matches.home_id == team_id) | (Matches.away_id == team_id),
                Matches.matchday >= current_matchday - 5,
                Matches.matchday < current_matchday
            ).all()
            return matches
        finally:
            session.close()

    @classmethod
    def get_team_last_5_matches_from_matchday(cls, team_id, matchday):
        session = DatabaseManager().get_session()
        try:
            matches = session.query(Matches).join(TeamLineup, TeamLineup.match_id == Matches.id).filter(
                (Matches.home_id == team_id) | (Matches.away_id == team_id),
                Matches.matchday >= matchday - 5,
                Matches.matchday < matchday
            ).all()
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
            ).order_by(Matches.time).all()  # Sort by time
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
            ).order_by(Matches.matchday.desc()).first()
            return match
        finally:
            session.close()
        
    @classmethod
    def get_last_encounter_from_matchday(cls, team_1, team_2, matchday):
        session = DatabaseManager().get_session()
        try:
            match = session.query(Matches).join(TeamLineup, TeamLineup.match_id == Matches.id).filter(
                ((Matches.home_id == team_1) & (Matches.away_id == team_2)) |
                ((Matches.home_id == team_2) & (Matches.away_id == team_1)),
                Matches.matchday < matchday
            ).order_by(Matches.matchday.desc()).first()
            return match
        finally:
            session.close()

class TeamLineup(Base):
    __tablename__ = 'team_lineup'
    
    id = Column(String(256), primary_key = True, default = lambda: str(uuid.uuid4()))
    match_id = Column(String(128), ForeignKey('matches.id'))
    player_id = Column(String(128), ForeignKey('players.id'))
    position = Column(String(128), nullable = False)
    rating = Column(Integer, nullable = False, default = 0)

    @classmethod
    def add_lineup_multiple(cls, match_id, players, positions):
        session = DatabaseManager().get_session()
        try:
            for player, position in zip(players, positions):
                new_player = TeamLineup(
                    match_id = match_id,
                    player_id = player.id,
                    position = position
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
    def batch_add_lineups(cls, lineups):
        session = DatabaseManager().get_session()
        try:
            # Create a list of dictionaries representing each lineup
            lineup_dicts = [
                {
                    "id": str(uuid.uuid4()),
                    "match_id": lineup[0],
                    "player_id": lineup[1],
                    "position": lineup[2],
                    "rating": lineup[3]
                }
                for lineup in lineups
            ]

            # Use the list of dictionaries to add the lineups
            session.bulk_insert_mappings(TeamLineup, lineup_dicts)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    @classmethod
    def add_lineup_single(cls, match_id, player_id, position, rating):
        session = DatabaseManager().get_session()
        try:
            new_player = TeamLineup(
                match_id = match_id,
                player_id = player_id,
                position = position,
                rating = rating
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
            players = session.query(TeamLineup).filter(TeamLineup.match_id == match_id).all()
            return players
        finally:
            session.close()
        
    @classmethod
    def get_lineup_by_match_and_team(cls, match_id, team_id):
        session = DatabaseManager().get_session()
        try:
            players = session.query(TeamLineup).join(Players).filter(
                TeamLineup.match_id == match_id,
                Players.team_id == team_id
            ).order_by(
                case(
                    [(Players.position == "goalkeeper", 1),
                    (Players.position == "defender", 2),
                    (Players.position == "midfielder", 3),
                    (Players.position == "forward", 4)],
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
                Matches.league_id == league_id
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
                Matches.league_id == league_id
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
                MatchAlias.league_id == league_id
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
                TeamLineup.match_id == match_id
            ).order_by(
                TeamLineup.rating.desc()
            ).first()
            return rating
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
    def check_yellow_card_ban(cls, player_id, comp_id, ban_threshold):
        session = DatabaseManager().get_session()
        try:
            yellow_cards = session.query(MatchEvents).join(Matches).filter(
                MatchEvents.player_id == player_id,
                MatchEvents.event_type == "yellow_card",
                Matches.league_id == comp_id
            ).count()

            if yellow_cards and yellow_cards % ban_threshold == 0:
                red_card_ban = session.query(PlayerBans).filter(
                    PlayerBans.player_id == player_id,
                    PlayerBans.ban_type == "red_card",
                    PlayerBans.ban_length > 0
                ).first()

                if red_card_ban:
                    red_card_ban.ban_length += 1
                    session.commit()
                else:
                    PlayerBans.add_player_ban(player_id, comp_id, ban_length = 1, ban_type = "yellow_cards")
                    Emails.add_email("player_ban", None, player_id, 1, comp_id)
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

            if sub_on_event:
                game_time = 90 - int(sub_on_event.time)
            elif sub_off_event:
                game_time = int(sub_off_event.time)
            else:
                game_time = 90

            return game_time
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

    @classmethod
    def add_league(cls, name, year, promotion, relegation):
        session = DatabaseManager().get_session()
        try:
            with open(f"Images/{name}.png", 'rb') as file:
                logo = file.read()

            new_league = League(
                id = str(uuid.uuid4()),
                name = name,
                year = year,
                logo = logo,
                promotion = promotion,
                relegation = relegation
            )

            leagueID = new_league.id

            session.add(new_league)
            session.commit()

            updateProgress(None)

            teams = Teams.get_all_teams()

            for i, teamID in enumerate(teams):
                LeagueTeams.add_team(leagueID, teamID, i + 1)
                updateProgress(None)

            updateProgress(4)

            cls.generate_schedule(teams, leagueID)

            return new_league
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @classmethod
    def generate_schedule(cls, team_ids, league_id):
        session = DatabaseManager().get_session()
        try:
            schedule = []

            # Generate the first round of matches
            num_teams = len(team_ids)
            for round in range(num_teams - 1):
                round_matches = []
                for i in range(num_teams // 2):
                    home = team_ids[i]
                    away = team_ids[num_teams - 1 - i]
                    if round % 2 == 0:
                        round_matches.append((home, away))
                    else:
                        round_matches.append((away, home))
                schedule.append(round_matches)
                team_ids.insert(1, team_ids.pop())  # Rotate the list

            random.shuffle(schedule)

            second_round = [[(away, home) for home, away in round] for round in schedule]
            random.shuffle(second_round)
            schedule.extend(second_round)

            # Add matches to the database
            for i, matchday in enumerate(schedule):
                assigned_referees = set()  # Keep track of referees assigned for this matchday
                for home_id, away_id in matchday:
                    available_referees = [
                        referee.id for referee in session.query(Referees).all()
                        if referee.id not in assigned_referees
                    ]
                    if not available_referees:
                        raise ValueError("Not enough referees to cover all matches for this matchday.")

                    referee_id = random.choice(available_referees)
                    assigned_referees.add(referee_id)

                    Matches.add_match(league_id, home_id, away_id, referee_id, i + 1)

                updateProgress(None)
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
    def get_league_by_year(cls, year):
        session = DatabaseManager().get_session()
        try:
            league = session.query(League).filter(League.year == year).first()
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

class LeagueTeams(Base):
    __tablename__ = 'league_teams'
    
    id = Column(String(256), primary_key = True, default = lambda: str(uuid.uuid4()))
    league_id = Column(String(128), ForeignKey('leagues.id'))
    team_id = Column(String(128), ForeignKey('teams.id'))
    position = Column(Integer, nullable = False, default = 0)
    points = Column(Integer, nullable = False, default = 0)
    games_won = Column(Integer, nullable = False, default = 0)
    games_drawn = Column(Integer, nullable = False, default = 0)
    games_lost = Column(Integer, nullable = False, default = 0)
    goals_scored = Column(Integer, nullable = False, default = 0)
    goals_conceded = Column(Integer, nullable = False, default = 0)

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
            team = session.query(LeagueTeams).filter(LeagueTeams.id == id).first()
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
    severity = Column(Enum("low", "medium", "high"), nullable = False)
    flag = Column(BLOB)
    nationality = Column(String(128), nullable = False)
    age = Column(Integer, nullable = False)
    date_of_birth = Column(String(128), nullable = False)

    @classmethod
    def add_referee(cls):
        session = DatabaseManager().get_session()
        try:
            selectedContinent = random.choices(list(continentWeights.keys()), weights = list(continentWeights.values()), k = 1)[0]
            _, countryWeights = COUNTRIES[selectedContinent]
            country = random.choices(list(countryWeights.keys()), weights = list(countryWeights.values()), k = 1)[0]

            with open(f"Images/Countries/{country.lower()}.png", 'rb') as file:
                flag = file.read()

            faker = Faker()
            date_of_birth = faker.date_of_birth(minimum_age = 15, maximum_age = 17)
            new_referee = Referees(
                first_name = faker.first_name_male(),
                last_name = faker.last_name(),
                severity = random.choices(["low", "medium", "high"], k = 1)[0],
                flag = flag,
                nationality = country,
                age = 2024 - date_of_birth.year,
                date_of_birth = str(date_of_birth)
            )

            session.add(new_referee)
            session.commit()

            return new_referee
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    @classmethod
    def add_referees(cls):
        session = DatabaseManager().get_session()
        try:
            for _ in range(NUM_TEAMS * 2):
                selectedContinent = random.choices(list(continentWeights.keys()), weights = list(continentWeights.values()), k = 1)[0]
                _, countryWeights = COUNTRIES[selectedContinent]
                country = random.choices(list(countryWeights.keys()), weights = list(countryWeights.values()), k = 1)[0]

                with open(f"Images/Countries/{country.lower()}.png", 'rb') as file:
                    flag = file.read()

                faker = Faker()
                date_of_birth = faker.date_of_birth(minimum_age = 30, maximum_age = 65)
                new_referee = Referees(
                    first_name = faker.first_name_male(),
                    last_name = faker.last_name_male(),
                    severity = random.choices(["low", "medium", "high"], k = 1)[0],
                    flag = flag,
                    nationality = country,
                    age = 2024 - date_of_birth.year,
                    date_of_birth = str(date_of_birth)
                )

                session.add(new_referee)

                updateProgress(None)

            session.commit()
        except Exception as e:
            session.rollback()
            raise e
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
    email_type = Column(Enum("welcome", "matchday_review", "matchday_preview", "player_games_issue", "season_review", "season_preview", "player_injury", "player_ban"), nullable = False)
    matchday = Column(Integer)
    player_id = Column(String(128), ForeignKey('players.id'))
    ban_length = Column(Integer)
    comp_id = Column(String(128))

    @classmethod
    def add_email(cls, email_type, matchday, player_id, ban_length, comp_id):
        session = DatabaseManager().get_session()
        try:
            new_email = Emails(
                email_type = email_type,
                matchday = matchday,
                player_id = player_id,
                ban_length = ban_length,
                comp_id = comp_id
            )

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
            # Create a list of dictionaries representing each email
            email_dicts = [
                {
                    "id": str(uuid.uuid4()),
                    "email_type": email[0],
                    "matchday": email[1],
                    "player_id": email[2],
                    "ban_length": email[3],
                    "comp_id": email[4]
                }
                for email in emails
            ]

            # Use session.execute with an insert statement
            session.execute(insert(Emails), email_dicts)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
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
    def get_all_emails(cls):
        session = DatabaseManager().get_session()
        try:
            emails = session.query(Emails).all()
            return emails
        finally:
            session.close()      

class PlayerBans(Base):
    __tablename__ = 'player_bans'

    id = Column(String(256), primary_key = True, default = lambda: str(uuid.uuid4()))
    player_id = Column(String(128), ForeignKey('players.id'))
    competition_id = Column(String(128))
    ban_length = Column(Integer, nullable = False)
    ban_type = Column(Enum("red_card", "injury", "yellow_cards"), nullable = False)

    @classmethod
    def add_player_ban(cls, player_id, competition_id, ban_length, ban_type):
        session = DatabaseManager().get_session()
        try:
            new_ban = PlayerBans(
                player_id = player_id,
                competition_id = competition_id,
                ban_length = ban_length,
                ban_type = ban_type
            )

            session.add(new_ban)
            session.commit()

            return new_ban
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @classmethod
    def batch_add_bans(cls, bans):
        session = DatabaseManager().get_session()
        try:
            # Create a list of dictionaries representing each ban
            ban_dicts = [
                {
                    "id": str(uuid.uuid4()),
                    "player_id": ban[0],
                    "competition_id": ban[1],
                    "ban_length": ban[2],
                    "ban_type": ban[3]
                }
                for ban in bans
            ]

            # Use session.execute with an insert statement
            session.execute(insert(PlayerBans), ban_dicts)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @classmethod
    def reduce_all_player_bans_for_team(cls, team_id, competition_id):
        session = DatabaseManager().get_session()
        try:
            bans = session.query(PlayerBans).join(Players).filter(Players.team_id == team_id).all()

            for ban in bans:
                if ban.ban_type == "injury":
                    ban.ban_length -= 1
                elif ban.competition_id == competition_id:
                    ban.ban_length -= 1

                if ban.ban_length == 0:
                    session.delete(ban)

            session.commit()

            return bans
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

def updateProgress(textIndex):
    global progressBar, progressLabel, progressFrame, percentageLabel, PROGRESS
    PROGRESS += 1

    textLabels = [
        "Creating manager...",
        "Adding Teams and Players...",
        "Adding the Refeeres",
        "Creating the League...",
        "Creating the Matches...",
    ]

    percentage = PROGRESS / TOTAL_STEPS * 100
    progressBar.set(percentage)

    percentageLabel.configure(text = f"{round(percentage)}%")

    if textIndex:
        progressLabel.configure(text = textLabels[textIndex])
    
    progressFrame.update_idletasks()

def setUpProgressBar(progressB, progressL, progressF, percentageL):
    global progressBar, progressLabel, progressFrame, percentageLabel

    progressBar = progressB
    progressLabel = progressL
    progressFrame = progressF
    percentageLabel = percentageL

