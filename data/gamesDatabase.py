from sqlalchemy import Column, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from settings import *
import uuid, datetime

Base = declarative_base()

class GamesDatabaseManager:
    """Singleton manager for this module's local games database."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GamesDatabaseManager, cls).__new__(cls)
            cls._instance.scoped_session = None
        return cls._instance

    def set_database(self):

        DATABASE_URL = "sqlite:///data/games.db" 
        engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
        session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        self.scoped_session = scoped_session(session_factory)

    def get_session(self):
        if not self.scoped_session:
            self.set_database()
        return self.scoped_session()

class Game(Base):
    __tablename__ = "games"

    id = Column(String(256), primary_key = True, default = lambda: str(uuid.uuid4()))
    manager_id = Column(String(256), nullable = False)
    first_name = Column(String(128), nullable = False)
    last_name = Column(String(128), nullable = False)
    curr_date = Column(DateTime, nullable = False, default = datetime.datetime(2025, 8, 15))

    @classmethod
    def add_game(cls, manager_id, first_name, last_name):
        session = GamesDatabaseManager().get_session()
        try:
            new_game = Game(
                manager_id = manager_id,
                first_name = first_name,
                last_name = last_name
            )

            session.add(new_game)
            session.commit()

            return new_game
        except Exception:
            if session is not None:
                session.rollback()
            raise
        finally:
            if session is not None:
                session.close()

    @classmethod
    def get_games_by_manager_id(cls, manager_id):
        session = GamesDatabaseManager().get_session()
        try:
            games = session.query(Game).filter(Game.manager_id == manager_id).all()
            return games if games else None
        finally:
            session.close()
        
    @classmethod
    def get_all_games(cls):
        session = GamesDatabaseManager().get_session()
        try:
            games = session.query(Game).all()
            return games if games else None
        finally:
            session.close()

    @classmethod
    def get_game_date(cls, manager_id):
        session = GamesDatabaseManager().get_session()
        try:
            game = session.query(Game).filter(Game.manager_id == manager_id).first()
            return game.curr_date if game else None
        finally:
            session.close()
    
    @classmethod
    def increment_game_date(cls, manager_id, days):
        session = GamesDatabaseManager().get_session()
        try:
            game = session.query(Game).filter(Game.manager_id == manager_id).first()
            if game:
                game.curr_date += datetime.timedelta(days = days)
                session.commit()
        finally:
            session.close()