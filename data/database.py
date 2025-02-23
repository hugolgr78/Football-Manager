from sqlalchemy import Column, Integer, String, BLOB, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, func, case
from sqlalchemy.orm import sessionmaker, aliased
from sqlalchemy.types import Enum
import uuid, json, random
from faker import Faker
from settings import *

Base = declarative_base()

LEAGUE_NAME = "Eclipse League"
FIRST_YEAR = 2024
NUM_TEAMS = 20

## Testing ##
TOTAL_STEPS = 1003
PROGRESS = 0

progressBar = None
progressLabel = None
progressFrame = None
percentageLabel = None

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
    def add_manager(cls, session, first_name = None, last_name = None, nationality = None, date_of_birth = None, user = False, chosenTeam = None):
        
        if user:
            new_manager = Managers(
                first_name = first_name,
                last_name = last_name,
                nationality = nationality,
                user = user,
                date_of_birth = date_of_birth,
                age = 2024 - date_of_birth.year
            )
        else:
            selectedContinent = random.choices(list(continentWeights.keys()), weights = list(continentWeights.values()), k = 1)[0]
            continent, countryWeights = COUNTRIES[selectedContinent]
            country = random.choices(list(countryWeights.keys()), weights = list(countryWeights.values()), k = 1)[0]
            
            date_of_birth = Faker().date_of_birth(minimum_age = 32, maximum_age = 65)
            new_manager = Managers(
                first_name = Faker().first_name_male(),
                last_name = Faker().first_name(),
                nationality = country,
                date_of_birth = date_of_birth,
                age = 2024 - date_of_birth.year,
                user = user
            )
        
        with open(f"Images/Countries/{new_manager.nationality.lower()}.png", 'rb') as file:
            new_manager.flag = file.read()

        session.add(new_manager)
        session.commit()
        updateProgress(1)

        if user:
            Teams.add_teams(session, chosenTeam, new_manager.first_name, new_manager.last_name)
            updateProgress(2)
            Referees().add_referees(session)
            updateProgress(3)
            League.add_league(session, LEAGUE_NAME, FIRST_YEAR, 0, 3)
            
            updateProgress(None)

        return new_manager

    @classmethod
    def get_manager_by_id(cls, session, id):
        manager = session.query(Managers).filter(Managers.id == id).first()
        if manager:
            return manager
        else:
            return None

    @classmethod
    def get_manager_by_name(cls, session, first_name, last_name):
        manager = session.query(Managers).filter(
            Managers.first_name == first_name.strip(),
            Managers.last_name == last_name.strip()
        ).first()

        if manager:
            return manager
        else:
            return None

    @classmethod
    def update_name(cls, session, id, first_name, last_name):
        manager = session.query(Managers).filter(Managers.id == id).first()

        if manager:
            manager.first_name = first_name
            manager.last_name = last_name
            session.commit()
        else:
            return None
    
    @classmethod
    def update_games(cls, session, id, games_won, games_lost):
        manager = session.query(Managers).filter(Managers.id == id).first()

        if manager:
            manager.games_played += 1
            manager.games_won += games_won
            manager.games_lost += games_lost
            session.commit()
        else:
            return None
        
    @classmethod
    def update_trophies(cls, session, id):
        manager = session.query(Managers).filter(Managers.id == id).first()

        if manager:
            manager.trophies += 1
            session.commit()
        else:
            return None
        
    @classmethod
    def delete_manager(cls, session, id):
        manager = session.query(Managers).filter(Managers.id == id).first()

        if manager:
            session.delete(manager)
            session.commit()
        else:
            return None

    @classmethod
    def get_all_user_managers(cls, session):
        managers = session.query(Managers).filter(Managers.user == True).all()

        if managers:
            return managers
        else:
            return None

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
    def add_teams(cls, session, chosenTeamName, manager_first_name, manager_last_name):
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
                manager = Managers().add_manager(session)
            else:
                manager = Managers().get_manager_by_name(session, manager_first_name, manager_last_name)

            new_team = Teams(
                id = str(uuid.uuid4()),
                manager_id = manager.id,
                name = name,
                year_created = year_created,
                stadium = stadium,
                level = level,
                logo = logo
            )

            updateProgress(None)
            Players().add_players(session, new_team.id)

            session.add(new_team)
        
        session.commit()

    @classmethod
    def get_team_by_id(cls, session, id):
        team = session.query(Teams).filter(Teams.id == id).first()

        if team:
            return team
        else:
            return None

    @classmethod
    def get_teams_by_manager(cls, session, manager_id):
        teams = session.query(Teams).filter(Teams.manager_id == manager_id).all()

        if teams:
            return teams
        else:
            return None

    @classmethod
    def get_team_by_name(cls, session, name):
        team = session.query(Teams).filter(Teams.name == name).first()

        if team:
            return team
        else:
            return None

    @classmethod
    def get_all_teams(cls, session):
        teams = session.query(Teams).all()

        if teams:
            return teams
        else:
            return None

    @classmethod
    def update_level(cls, session, id, level):
        team = session.query(Teams).filter(Teams.id == id).first()

        if team:
            team.level = level
            session.commit()
        else:
            return None

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
    def add_player_entry(cls, session, data):
        session.add(data)
        session.commit()

    @classmethod
    def add_player(cls, session, team_id, position, required_position, role, commit = False):
        
        selectedContinent = random.choices(list(continentWeights.keys()), weights = list(continentWeights.values()), k = 1)[0]
        _, countryWeights = COUNTRIES[selectedContinent]
        country = random.choices(list(countryWeights.keys()), weights = list(countryWeights.values()), k = 1)[0]

        with open(f"Images/Countries/{country.lower()}.png", 'rb') as file:
            flag = file.read()
        
        faker = Faker()
        date_of_birth = faker.date_of_birth(minimum_age = 15, maximum_age = 17)
        new_player = Players(
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

        existing_numbers = {player.number for player in Players.get_all_players_by_team(session, team_id)}
        while new_player.number in existing_numbers:
            new_player.number = random.randint(1, 99)

        # Define specific positions based on the main position
        specific_positions = {
            "goalkeeper": ["GK"],
            "defender": ["RB", "CB", "LB"],
            "midfielder": ["DM", "CM", "RM", "LM"],
            "forward": ["LW", "CF", "RW", "AM"]
        }

        # Ensure the player has the required position
        required_code = POSITION_CODES[required_position]
        player_positions = [required_code]

        # Add a random number of other positions based on the main position
        if position in specific_positions:
            other_positions = specific_positions[position]
            other_positions.remove(required_code)
            if len(other_positions) > 0:    
                num_other_positions = random.randint(1, len(other_positions))
                player_positions.extend(random.sample(other_positions, num_other_positions))

        new_player.specific_positions = ','.join(player_positions)

        if commit:
            session.add(new_player)
            session.commit()
            
        return new_player

    @classmethod
    def add_players(cls, session, team_id):
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

        # Define weights for the number of specific positions
        position_weights = [0.4, 0.3, 0.2, 0.1]  # Weights for 1, 2, 3, and 4+ positions

        # Ensure at least one player for each specific position
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

                # Assign multiple specific positions
                num_positions = random.choices(range(1, min(len(specific_pos_list), 4) + 1), weights = position_weights[:min(len(specific_pos_list), 4)])[0]
                new_player_positions = random.sample(specific_pos_list, k = num_positions)
                if specific_pos not in new_player_positions:
                    new_player_positions[0] = specific_pos  # Ensure specific_pos is included
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

        # Assign remaining players
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

                # Assign multiple specific positions
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
    
    @classmethod
    def get_player_by_id(cls, session, id):
        player = session.query(Players).filter(Players.id == id).first()

        if player:
            return player
        else:
            return None
    
    @classmethod
    def get_player_by_name(cls, session, first_name, last_name):
        player = session.query(Players).filter(Players.first_name == first_name, Players.last_name == last_name).first()

        if player:
            return player
        else:
            return None
    
    @classmethod
    def get_player_manager(cls, session, id):
        player = cls.get_player_by_id(session, id)

        if not player:
            return None

        team = Teams().get_team_by_id(session, player.team_id)
        if not team:
            return None

        manager = Managers().get_manager_by_id(session, team.manager_id)
        return manager
        
    @classmethod
    def update_age(session, id, age):
        player = session.query(Players).filter(Players.id == id).first()

        if player:
            player.age = age
            session.commit()
        else:
            return None

    @classmethod
    def update_morale(session, id, morale):
        player = session.query(Players).filter(Players.id == id).first()

        if player:
            player.morale = morale
            session.commit()
        else:
            return None

    @classmethod
    def get_all_players_by_team(cls, session, team_id, youths = True):
        position_order = case(
            [
                (Players.position == 'goalkeeper', 1),
                (Players.position == 'defender', 2),
                (Players.position == 'midfielder', 3),
                (Players.position == 'forward', 4)
            ],
            else_=5
        )

        query = session.query(Players).filter(Players.team_id == team_id)

        if not youths:
            query = query.filter(Players.player_role != 'Youth Team')

        players = query.order_by(position_order).all()

        if players:
            return players
        else:
            return None
        
    @classmethod
    def get_all_star_players(cls, session, team_id):
        players = session.query(Players).filter(Players.team_id == team_id, Players.player_role == 'Star player').all()

        if players:
            return players
        else:
            return None
        
    @classmethod
    def get_all_youngsters(cls, session, team_id):
        players = session.query(Players).filter(Players.team_id == team_id, Players.player_role == 'Youngster').all()

        if players:
            return players
        else:
            return None

    @classmethod
    def get_all_defenders(cls, session, team_id):
        role_order = case(
            [(Players.player_role == 'Star player', 1),
            (Players.player_role == 'First Team', 2),
            (Players.player_role == 'Rotation', 3)],
            else_ = 4
        )

        defenders = session.query(Players).filter(Players.team_id == team_id, Players.position == 'defender').order_by(role_order).all()

        if defenders:
            return defenders
        else:
            return None
        
    @classmethod
    def get_all_midfielders(cls, session, team_id):
        role_order = case(
            [(Players.player_role == 'Star player', 1),
            (Players.player_role == 'First Team', 2),
            (Players.player_role == 'Rotation', 3)],
            else_ = 4
        )

        midfielders = session.query(Players).filter(Players.team_id == team_id, Players.position == 'midfielder').order_by(role_order).all()

        if midfielders:
            return midfielders
        else:
            return None
        
    @classmethod
    def get_all_forwards(cls, session, team_id):
        role_order = case(
            [(Players.player_role == 'Star player', 1),
            (Players.player_role == 'First Team', 2),
            (Players.player_role == 'Rotation', 3)],
            else_ = 4
        )

        forwards = session.query(Players).filter(Players.team_id == team_id, Players.position == 'forward').order_by(role_order).all()

        if forwards:
            return forwards
        else:
            return None

    @classmethod
    def get_all_goalkeepers(cls, session, team_id):
        role_order = case(
            [(Players.player_role == 'First Team', 1),
            (Players.player_role == 'Backup', 2)],
            else_ = 3
        )

        goalkeepers = session.query(Players).filter(Players.team_id == team_id, Players.position == 'goalkeeper').order_by(role_order).all()

        if goalkeepers:
            return goalkeepers
        else:
            return None
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
    def add_match(cls, session, league_id, home_id, away_id, referee_id, matchday):
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
    
    @classmethod
    def get_match_by_id(cls, session, id):
        match = session.query(Matches).filter(Matches.id == id).first()

        if match:
            return match
        else:
            return None
        
    @classmethod
    def get_match_by_teams(cls, session, home_id, away_id):
        match = session.query(Matches).filter(
            ((Matches.home_id == home_id) & (Matches.away_id == away_id)) |
            ((Matches.home_id == away_id) & (Matches.away_id == home_id))
        ).first()

        if match:
            return match
        else:
            return None
        
    @classmethod
    def get_team_next_match(cls, session, team_id, league_id):
        current_matchday = session.query(League).filter(League.id == league_id).first().current_matchday
        match = session.query(Matches).filter(
            (Matches.home_id == team_id) | (Matches.away_id == team_id),
            Matches.matchday == current_matchday
        ).first()

        if match:
            return match
        else:
            return None
        
    @classmethod
    def get_team_matchday_match(cls, session, team_id, league_id, matchday):
        match = session.query(Matches).filter(
            ((Matches.home_id == team_id) | (Matches.away_id == team_id)),
            Matches.league_id == league_id,
            Matches.matchday == matchday
        ).first()

        if match:
            return match
        else:
            return None

    @classmethod
    def get_team_first_match(cls, session, team_id):
        match = session.query(Matches).filter(
            (Matches.home_id == team_id) | (Matches.away_id == team_id),
            Matches.matchday == 1
        ).first()

        if match:
            return match
        else:
            return None

    @classmethod
    def get_team_last_match(cls, session, team_id, league_id):
        current_matchday = session.query(League).filter(League.id == league_id).first().current_matchday
        match = session.query(Matches).join(TeamLineup, TeamLineup.match_id == Matches.id).filter(
            (Matches.home_id == team_id) | (Matches.away_id == team_id),
            Matches.matchday == current_matchday - 1
        ).first()

        if match:
            return match
        else:
            return None

    @classmethod
    def get_team_last_match_from_matchday(cls, session, team_id, matchday):
        match = session.query(Matches).join(TeamLineup, TeamLineup.match_id == Matches.id).filter(
            (Matches.home_id == team_id) | (Matches.away_id == team_id),
            Matches.matchday == matchday - 1
        ).first()

        if match:
            return match
        else:
            return None

    @classmethod
    def get_team_next_5_matches(cls, session, team_id, league_id):
        current_matchday = session.query(League).filter(League.id == league_id).first().current_matchday
        matches = session.query(Matches).filter(
            (Matches.home_id == team_id) | (Matches.away_id == team_id),
            Matches.matchday >= current_matchday,
            Matches.matchday < current_matchday + 5
        ).all()

        if matches:
            return matches
        else:
            return None

    @classmethod
    def get_team_last_5_matches(cls, session, team_id, league_id):
        current_matchday = session.query(League).filter(League.id == league_id).first().current_matchday
        matches = session.query(Matches).join(TeamLineup, TeamLineup.match_id == Matches.id).filter(
            (Matches.home_id == team_id) | (Matches.away_id == team_id),
            Matches.matchday >= current_matchday - 5,
            Matches.matchday < current_matchday
        ).all()

        if matches:
            return matches
        else:
            return None

    @classmethod
    def get_team_last_5_matches_from_matchday(cls, session, team_id, matchday):
        matches = session.query(Matches).join(TeamLineup, TeamLineup.match_id == Matches.id).filter(
            (Matches.home_id == team_id) | (Matches.away_id == team_id),
            Matches.matchday >= matchday - 5,
            Matches.matchday < matchday
        ).all()

        if matches:
            return matches
        else:
            return None

    @classmethod
    def update_score(cls, session, id, score_home, score_away):
        match = session.query(Matches).filter(Matches.id == id).first()

        if match:
            match.score_home = score_home
            match.score_away = score_away
            session.commit()
        else:
            return None

    @classmethod
    def get_all_matches_by_matchday(cls, session, matchday):
        matches = session.query(Matches).filter(Matches.matchday == matchday).all()

        if matches:
            return matches
        else:
            return None

    @classmethod
    def get_all_matches_by_team(cls, session, team_id):
        matches = session.query(Matches).filter((Matches.home_id == team_id) | (Matches.away_id == team_id)).all()

        if matches:
            return matches
        else:
            return None

    @classmethod
    def get_all_matches_by_league(cls, session, league_id):
        matches = session.query(Matches).filter(Matches.league_id == league_id).all()

        if matches:
            return matches
        else:
            return None
    
    @classmethod
    def get_all_matches_by_referee(cls, session, referee_id):
        matches = session.query(Matches).filter(Matches.referee_id == referee_id).all()

        if matches:
            return matches
        else:
            return None

    @classmethod
    def get_matchday_for_league(cls, session, league_id, matchday):
        matches = session.query(Matches).filter(
            Matches.league_id == league_id,
            Matches.matchday == matchday
        ).order_by(Matches.time).all()  # Sort by time

        if matches:
            return matches
        else:
            return None
        
    @classmethod
    def get_last_encounter(cls, session, team_1, team_2):
        match = session.query(Matches).join(TeamLineup, TeamLineup.match_id == Matches.id).filter(
            ((Matches.home_id == team_1) & (Matches.away_id == team_2)) |
            ((Matches.home_id == team_2) & (Matches.away_id == team_1))
        ).order_by(Matches.matchday.desc()).first()

        if match:
            return match
        else:
            return None
        
    @classmethod
    def get_last_encounter_from_matchday(cls, session, team_1, team_2, matchday):
        match = session.query(Matches).join(TeamLineup, TeamLineup.match_id == Matches.id).filter(
            ((Matches.home_id == team_1) & (Matches.away_id == team_2)) |
            ((Matches.home_id == team_2) & (Matches.away_id == team_1)),
            Matches.matchday < matchday
        ).order_by(Matches.matchday.desc()).first()

        if match:
            return match
        else:
            return None

class TeamLineup(Base):
    __tablename__ = 'team_lineup'
    
    id = Column(String(256), primary_key = True, default = lambda: str(uuid.uuid4()))
    match_id = Column(String(128), ForeignKey('matches.id'))
    player_id = Column(String(128), ForeignKey('players.id'))
    position = Column(String(128), nullable = False)
    rating = Column(Integer, nullable = False, default = 0)

    @classmethod
    def add_lineup_multiple(cls, session, match_id, players, positions):
        for player, position in zip(players, positions):
            new_player = TeamLineup(
                match_id = match_id,
                player_id = player.id,
                position = position
            )

            session.add(new_player)
            session.commit()

        return new_player
    
    @classmethod
    def add_lineup_single(cls, session, match_id, player_id, position, rating):
        new_player = TeamLineup(
            match_id = match_id,
            player_id = player_id,
            position = position,
            rating = rating
        )

        session.add(new_player)
        session.commit()

        return new_player

    @classmethod
    def get_lineup_by_id(cls, session, id):
        player = session.query(TeamLineup).filter(TeamLineup.id == id).first()

        if player:
            return player
        else:
            return None
        
    @classmethod
    def get_lineup_by_match(cls, session, match_id):
        players = session.query(TeamLineup).filter(TeamLineup.match_id == match_id).all()

        if players:
            return players
        else:
            return None
        
    @classmethod
    def get_lineup_by_match_and_team(cls, session, match_id, team_id):
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

        if players:
            return players
        else:
            return None

    @classmethod
    def get_number_matches_by_player(cls, session, player_id, league_id):
        matches = session.query(TeamLineup).join(Matches).filter(
            TeamLineup.player_id == player_id,
            Matches.league_id == league_id
        ).count()

        if matches:
            return matches
        else:
            return 0

    @classmethod
    def get_player_average_rating(cls, session, player_id, league_id):
        rating = session.query(func.avg(TeamLineup.rating)).join(Matches).filter(
            TeamLineup.player_id == player_id,
            Matches.league_id == league_id
        ).scalar()

        if rating:
            return rating
        else:
            return "N/A"

    @classmethod
    def get_all_average_ratings(cls, session, league_id):
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

        if ratings:
            return ratings
        else:
            return None

    @classmethod
    def get_player_OTM(cls, session, match_id):
        rating = session.query(
            TeamLineup
        ).filter(
            TeamLineup.match_id == match_id
        ).order_by(
            TeamLineup.rating.desc()
        ).first()

        if rating:
            return rating
        else:
            return None

class MatchEvents(Base):
    __tablename__ = 'match_events'

    id = Column(String(256), primary_key = True, default = lambda: str(uuid.uuid4()))
    match_id = Column(String(128), ForeignKey('matches.id'))
    event_type = Column(Enum("goal", "assist", "yellow_card", "red_card", "own_goal", "penalty_goal", "penalty_miss", "penalty_saved", "clean_sheet", "injury", "sub_on", "sub_off"), nullable = False)
    time = Column(String(128), nullable = False)
    player_id = Column(String(128), ForeignKey('players.id'))

    @classmethod
    def add_event(cls, session, match_id, event_type, time, player_id):
        new_event = MatchEvents(
            match_id = match_id,
            event_type = event_type,
            time = time,
            player_id = player_id
        )

        session.add(new_event)
        session.commit()

        return new_event

    @classmethod
    def get_event_by_id(cls, session, id):
        event = session.query(MatchEvents).filter(MatchEvents.id == id).first()

        if event:
            return event
        else:
            return None
    
    @classmethod
    def get_events_by_match(cls, session, match_id):
        events = session.query(MatchEvents).filter(MatchEvents.match_id == match_id).all()

        if events:
            return events
        else:
            return None

    @classmethod
    def get_event_by_player(cls, session, player_id):
        events = session.query(MatchEvents).filter(MatchEvents.player_id == player_id).all()

        if events:
            return events
        else:
            return None
        
    @classmethod
    def get_event_by_type(cls, session, event_type):
        events = session.query(MatchEvents).filter(MatchEvents.event_type == event_type).all()

        if events:
            return events
        else:
            return None
        
    @classmethod
    def get_event_by_time(cls, session, time):
        events = session.query(MatchEvents).filter(MatchEvents.time == time).all()

        if events:
            return events
        else:
            return None
        
    @classmethod
    def get_event_by_player_and_type(cls, session, player_id, event_type):
        events = session.query(MatchEvents).filter(MatchEvents.player_id == player_id, MatchEvents.event_type == event_type).all()

        if events:
            return events
        else:
            return None
    
    @classmethod
    def get_goals_by_player(cls, session, player_id):
        goals = session.query(MatchEvents).filter(MatchEvents.player_id == player_id, MatchEvents.event_type == "goal").count()

        if goals:
            return goals
        else:
            return 0
        
    @classmethod
    def get_events_by_match_and_player(cls, session, match_id, player_id):
        events = session.query(MatchEvents).filter(MatchEvents.match_id == match_id, MatchEvents.player_id == player_id).all()

        if events:
            return events
        else:
            return None
        
    @classmethod
    def get_all_goals(cls, session, league_id):
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
            MatchEvents.event_type == "goal",
            MatchAlias.league_id == league_id
        ).group_by(
            MatchEvents.player_id,
            PlayerAlias.first_name,
            PlayerAlias.last_name
        ).order_by(
            func.count(MatchEvents.id).desc()
        ).all()

        if goals:
            return goals
        else:
            return None
        
    @classmethod
    def get_assists_by_player(cls, session, player_id):
        assists = session.query(MatchEvents).filter(MatchEvents.player_id == player_id, MatchEvents.event_type == "assist").count()

        if assists:
            return assists
        else:
            return 0
    
    @classmethod
    def get_all_assists(cls, session, league_id):
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

        if assists:
            return assists
        else:
            return None

    @classmethod
    def get_yellow_cards_by_player(cls, session, player_id):
        yellow_cards = session.query(MatchEvents).filter(MatchEvents.player_id == player_id, MatchEvents.event_type == "yellow_card").count()

        if yellow_cards:
            return yellow_cards
        else:
            return 0

    @classmethod
    def check_yellow_card_ban(cls, session, player_id, comp_id, ban_threshold):
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
                PlayerBans.add_player_ban(session, player_id, comp_id, ban_length = 1, ban_type = "yellow_cards")
                Emails.add_email(session, "player_ban", None, player_id, 1, comp_id)

    @classmethod
    def get_all_yellow_cards(cls, session, league_id):
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

        if yellow_cards:
            return yellow_cards
        else:
            return None

    @classmethod
    def get_red_cards_by_player(cls, session, player_id):
        red_cards = session.query(MatchEvents).filter(MatchEvents.player_id == player_id, MatchEvents.event_type == "red_card").count()

        if red_cards:
            return red_cards
        else:
            return 0
        
    @classmethod
    def get_all_red_cards(cls, session, league_id):
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

        if red_cards:
            return red_cards
        else:
            return None
        
    @classmethod
    def get_own_goals_by_player(cls, session, player_id):
        own_goals = session.query(MatchEvents).filter(MatchEvents.player_id == player_id, MatchEvents.event_type == "own_goal").count()

        if own_goals:
            return own_goals
        else:
            return 0
        
    @classmethod
    def get_all_own_goals(cls, session, league_id):
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

        if own_goals:
            return own_goals
        else:
            return None

    @classmethod
    def get_penalty_goals_by_player(cls, session, player_id):
        penalty_goals = session.query(MatchEvents).filter(MatchEvents.player_id == player_id, MatchEvents.event_type == "penalty_goal").count()

        if penalty_goals:
            return penalty_goals
        else:
            return 0
        
    @classmethod
    def get_all_penalty_goals(cls, session, league_id):
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

        if penalty_goals:
            return penalty_goals
        else:
            return None
        
    @classmethod
    def get_penalty_saves_by_player(cls, session, player_id):
        penalty_saves = session.query(MatchEvents).filter(MatchEvents.player_id == player_id, MatchEvents.event_type == "penalty_save").count()

        if penalty_saves:
            return penalty_saves
        else:
            return 0
        
    @classmethod
    def get_all_penalty_saves(cls, session, league_id):
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
            MatchEvents.event_type == "penalty_save",
            MatchAlias.league_id == league_id
        ).group_by(
            MatchEvents.player_id,
            PlayerAlias.first_name,
            PlayerAlias.last_name
        ).order_by(
            func.count(MatchEvents.id).desc()
        ).all()

        if penalty_saves:
            return penalty_saves
        else:
            return None

    @classmethod
    def get_clean_sheets_by_player(cls, session, player_id):
        clean_sheets = session.query(MatchEvents).filter(MatchEvents.player_id == player_id, MatchEvents.event_type == "clean_sheet").count()

        if clean_sheets:
            return clean_sheets
        else:
            return 0
    
    @classmethod
    def get_all_clean_sheets(cls, session, league_id):
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

        if clean_sheets:
            return clean_sheets
        else:
            return None

    @classmethod
    def get_player_game_time(cls, session, player_id, match_id):
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

class League(Base):
    __tablename__ = 'leagues'
    
    id = Column(String(256), primary_key = True, default = lambda: str(uuid.uuid4()))
    name = Column(String(128), nullable = False)
    year = Column(Integer, nullable = False)
    logo = Column(BLOB)
    current_matchday = Column(Integer, nullable = False, default = 1) # the matchday stored has not yet been simualted (once one is, this value is incremented)
    promotion = Column(Integer, nullable = False)
    relegation = Column(Integer, nullable = False)

    @classmethod
    def add_league(cls, session, name, year, promotion, relagation):

        with open(f"Images/{name}.png", 'rb') as file:
            logo = file.read()

        new_league = League(
            id = str(uuid.uuid4()),
            name = name,
            year = year,
            logo = logo,
            promotion = promotion,
            relegation = relagation
        )

        session.add(new_league)
        session.commit()

        updateProgress(None)

        teams = Teams().get_all_teams(session)

        for i, team in enumerate(teams):
            LeagueTeams().add_team(session, new_league.id, team.id, i + 1)
            updateProgress(None)

        updateProgress(4)

        cls.generate_schedule(session, teams, new_league.id)

        return new_league

    @classmethod
    def generate_schedule(cls, session, teams, leagueId):
        teamIDs = [team.id for team in teams]
        schedule = []

        # Generate the first round of matches
        num_teams = len(teamIDs)
        for round in range(num_teams - 1):
            round_matches = []
            for i in range(num_teams // 2):
                home = teamIDs[i]
                away = teamIDs[num_teams - 1 - i]
                if round % 2 == 0:
                    round_matches.append((home, away))
                else:
                    round_matches.append((away, home))
            schedule.append(round_matches)
            teamIDs.insert(1, teamIDs.pop())  # Rotate the list

        random.shuffle(schedule)

        second_round = [[(away, home) for home, away in round] for round in schedule]
        random.shuffle(second_round)
        schedule.extend(second_round)

        # Add matches to the database
        for i, matchday in enumerate(schedule):
            for home_id, away_id in matchday:
                referee = Referees().get_referee_by_id(session, random.choice([referee.id for referee in session.query(Referees).all()]))
                Matches().add_match(session, leagueId, home_id, away_id, referee.id, i + 1)

            updateProgress(None)
    
    @classmethod
    def get_league_by_id(cls, session, league_id):
        league = session.query(League).filter(League.id == league_id).first()

        if league:
            return league
        else:
            return None

    @classmethod
    def get_league_by_name(cls, session, name):
        league = session.query(League).filter(League.name == name).first()

        if league:
            return league
        else:
            return None
        
    @classmethod
    def get_league_by_year(cls, session, year):
        league = session.query(League).filter(League.year == year).first()

        if league:
            return league
        else:
            return None
        
    @classmethod
    def update_current_matchday(cls, session, league_id):
        league = session.query(League).filter(League.id == league_id).first()

        if league:
            league.current_matchday += 1
            session.commit()
        else:
            return None

# update record after match
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
    def add_team(cls, session, league_id, team_id, position):
        new_team = LeagueTeams(
            league_id = league_id,
            team_id = team_id,
            position = position
        )

        session.add(new_team)
        session.commit()

        return new_team
    
    @classmethod
    def get_team_by_id(cls, session, id):
        team = session.query(LeagueTeams).filter(LeagueTeams.id == id).first()

        if team:
            return team
        else:
            return None

    @classmethod
    def get_league_by_team(cls, session, team_id):
        league = session.query(LeagueTeams).filter(LeagueTeams.team_id == team_id).first()

        if league:
            return league
        else:
            return None   

    @classmethod
    def get_teams_by_league(cls, session, league_id):
        teams = session.query(LeagueTeams).filter(LeagueTeams.league_id == league_id).all()

        if teams:
            return teams
        else:
            return None

    @classmethod
    def get_teams_by_position(cls, session, league_id):
        teams = session.query(LeagueTeams).filter(LeagueTeams.league_id == league_id).order_by(LeagueTeams.position).all()

        if teams:
            return teams
        else:
            return None
        
    @classmethod
    def get_teams_by_points(cls, session, league_id):
        teams = session.query(LeagueTeams).filter(LeagueTeams.league_id == league_id).order_by(LeagueTeams.points).all()

        if teams:
            return teams
        else:
            return
        
    @classmethod
    def update_team(cls, session, team_id, points, games_won, games_drawn, games_lost, goals_scored, goals_conceded):
        team = session.query(LeagueTeams).filter(LeagueTeams.team_id == team_id).first()

        if team:
            team.points += points
            team.games_won += games_won
            team.games_drawn += games_drawn
            team.games_lost += games_lost
            team.goals_scored += goals_scored
            team.goals_conceded += goals_conceded
            session.commit()

    @classmethod
    def update_team_positions(cls, session, league_id):
        teams = session.query(LeagueTeams).filter(LeagueTeams.league_id == league_id).all()

        if teams:
            teams.sort(key = lambda x: (x.points, x.goals_scored - x.goals_conceded, x.goals_scored, -x.goals_conceded), reverse = True)

            for index, team in enumerate(teams):
                team.position = index + 1
                
            session.commit()
        else:
            return None

    @classmethod
    def get_num_teams_league(cls, session, league_id):
        num_teams = session.query(LeagueTeams).filter(LeagueTeams.league_id == league_id).count()

        if num_teams:
            return num_teams
        else:
            return 0

# create new record after match
class TeamHistory(Base):
    __tablename__ = 'team_history'
    
    id = Column(String(256), primary_key = True, default = lambda: str(uuid.uuid4()))
    matchday = Column(Integer, nullable = False)
    team_id = Column(String(128), ForeignKey('teams.id'))
    position = Column(Integer, nullable = False, default = 0)
    points = Column(Integer, nullable = False, default = 0)

    @classmethod
    def add_team(cls, session, matchday, team_id, position, points):
        new_team = TeamHistory(
            matchday = matchday,
            team_id = team_id,
            position = position,
            points = points
        )

        session.add(new_team)
        session.commit()

        return new_team

    @classmethod
    def update_team(cls, session, match_id, team_id, position, points):
        new_team = TeamHistory(
            match_id = match_id,
            team_id = team_id,
            position = position,
            points = points
        )

        session.add(new_team)
        session.commit()

        return new_team

    @classmethod
    def get_positions_by_team(cls, session, team_id):
        positions = session.query(TeamHistory.position).filter(TeamHistory.team_id == team_id).order_by(TeamHistory.matchday).all()

        if positions:
            return positions
        else:
            return None
        
    @classmethod
    def get_points_by_team(cls, session, team_id):
        points = session.query(TeamHistory.points).filter(TeamHistory.team_id == team_id).order_by(TeamHistory.matchday).all()

        if points:
            return points
        else:
            return None
        
    @classmethod
    def get_team_data_matchday(cls, session, team_id, matchday):
        team = session.query(TeamHistory).filter(TeamHistory.team_id == team_id, TeamHistory.matchday == matchday).first()

        if team:
            return team
        else:
            return None

    @classmethod
    def get_team_data_position(cls, session, position, matchday):
        team = session.query(TeamHistory).filter(TeamHistory.position == position, TeamHistory.matchday == matchday).first()

        if team:
            return team
        else:
            return None

class Referees(Base):
    __tablename__ = 'referees'
    
    id = Column(String(256), primary_key = True, default = lambda: str(uuid.uuid4()))
    first_name = Column(String(128), nullable = False)
    last_name = Column(String(128), nullable = False)
    severity = Column(Enum("low", "medium", "high"), nullable = False)

    @classmethod
    def add_referee(cls, session):
        new_referee = Referees(
            first_name = Faker().first_name_male(),
            last_name = Faker().last_name(),
            severity = random.choices(["low", "medium", "high"], k = 1)[0]
        )

        session.add(new_referee)
        session.commit()

        return new_referee
    
    @classmethod
    def add_referees(cls, session):
        for _ in range(NUM_TEAMS * 2):
            new_referee = Referees(
                first_name = Faker().first_name_male(),
                last_name = Faker().last_name_male(),
                severity = random.choices(["low", "medium", "high"], k = 1)[0]
            )

            session.add(new_referee)

            updateProgress(None)

        session.commit()

    @classmethod
    def get_referee_by_id(cls, session, id):
        referee = session.query(Referees).filter(Referees.id == id).first()

        if referee:
            return referee
        else:
            return None
        
    @classmethod
    def get_referee_by_name(cls, session, first_name, last_name):
        referee = session.query(Referees).filter(Referees.first_name == first_name, Referees.last_name == last_name).first()

        if referee:
            return referee
        else:
            return None

class Trophies(Base):
    __tablename__ = 'trophies'

    id = Column(String(256), primary_key = True, default = lambda: str(uuid.uuid4()))
    team_id = Column(String(128), ForeignKey('teams.id'))
    manager_id = Column(String(128), ForeignKey('managers.id'))
    competition_id = Column(String(128), ForeignKey('leagues.id'))
    year = Column(Integer, nullable = False)

    @classmethod
    def get_all_trophies_by_team(cls, session, team_id):
        throphies = session.query(Trophies).filter(Trophies.team_id == team_id).all()

        if throphies:
            return throphies
        else:
            return None

    @classmethod
    def get_all_trophies_by_manager(cls, session, manager_id):
        throphies = session.query(Trophies).filter(Trophies.manager_id == manager_id).all()

        if throphies:
            return throphies
        else:
            return None

class Emails(Base):
    __tablename__ = 'emails'

    id = Column(String(256), primary_key = True, default = lambda: str(uuid.uuid4()))
    email_type = Column(Enum("welcome", "matchday_review", "matchday_preview", "player_games_issue", "season_review", "season_preview", "player_injury", "player_ban"), nullable = False)
    matchday = Column(Integer)
    player_id = Column(String(128), ForeignKey('players.id'))
    ban_length = Column(Integer)
    comp_id = Column(String(128))

    @classmethod
    def add_email(cls, session, email_type, matchday, player_id, ban_length, comp_id):
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
    
    @classmethod
    def get_email_by_id(cls, session, id):
        email = session.query(Emails).filter(Emails.id == id).first()

        if email:
            return email
        else:
            return None
        
    @classmethod
    def get_emails_by_type(cls, session, email_type):
        emails = session.query(Emails).filter(Emails.email_type == email_type).all()

        if emails:
            return emails
        else:
            return None
        
    @classmethod
    def get_emails_by_matchday(cls, session, matchday):
        emails = session.query(Emails).filter(Emails.matchday == matchday).all()

        if emails:
            return emails
        else:
            return None
        
    @classmethod
    def get_email_by_matchday_and_type(cls, session, matchday, email_type):
        email = session.query(Emails).filter(Emails.matchday == matchday, Emails.email_type == email_type).first()

        if email:
            return True
        else:
            return False
    
    @classmethod
    def get_all_emails(cls, session):
        emails = session.query(Emails).all()

        if emails:
            return emails
        else:
            return None
        
class PlayerBans(Base):
    __tablename__ = 'player_bans'

    id = Column(String(256), primary_key = True, default = lambda: str(uuid.uuid4()))
    player_id = Column(String(128), ForeignKey('players.id'))
    competition_id = Column(String(128))
    ban_length = Column(Integer, nullable = False)
    ban_type = Column(Enum("red_card", "injury", "yellow_cards"), nullable = False)

    @classmethod
    def add_player_ban(cls, session, player_id, competition_id, ban_length, ban_type):
        new_ban = PlayerBans(
            player_id = player_id,
            competition_id = competition_id,
            ban_length = ban_length,
            ban_type = ban_type
        )

        session.add(new_ban)
        session.commit()

        return new_ban

    @classmethod
    def reduce_all_player_bans_for_team(cls, session, team_id, competition_id):
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

    @classmethod
    def check_bans_for_player(cls, session, player_id, competition_id):
        bans = session.query(PlayerBans).join(Players).filter(Players.id == player_id).all()
        is_banned = False

        for ban in bans:
            if ban.ban_type == "injury" or ban.competition_id == competition_id:
                is_banned = True
        
        return is_banned
    
    @classmethod
    def get_bans_for_player(cls, session, player_id):
        bans = session.query(PlayerBans).join(Players).filter(Players.id == player_id).all()

        return bans if bans else []

    @classmethod
    def get_all_non_banned_players_for_comp(cls, session, team_id, competition_id):
        all_players = Players.get_all_players_by_team(session, team_id)
        non_banned_players = []

        for player in all_players:
            is_banned = PlayerBans.check_bans_for_player(session, player.id, competition_id)

            if not is_banned and player.player_role != "Youth Team":
                non_banned_players.append(player)

        return non_banned_players
    
    @classmethod 
    def get_all_non_banned_youth_players_for_comp(cls, session, team_id, competition_id):
        all_players = Players.get_all_players_by_team(session, team_id)
        non_banned_players = []

        for player in all_players:
            is_banned = PlayerBans.check_bans_for_player(session, player.id, competition_id)

            if not is_banned and player.player_role == "Youth Team":
                non_banned_players.append(player)

        return non_banned_players

def create_tables(database_name):
    DATABASE_URL = f"sqlite:///data/{database_name}.db"

    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit = False, autoflush = False, bind = engine)
    Base.metadata.create_all(bind = engine)

    return SessionLocal

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
