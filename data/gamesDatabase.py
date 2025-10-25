from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from settings import *
import uuid, datetime, os

Base = declarative_base()

class GamesDatabaseManager:
    """Singleton manager for the local games database."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GamesDatabaseManager, cls).__new__(cls)
            cls._instance.scoped_session = None
            cls._instance.engine = None
            cls._instance.original_path = "data/games.db"
            cls._instance.copy_path = "data/games_copy.db"
        return cls._instance

    def set_database(self, create_tables = False):
        db_path = self.copy_path if os.path.exists(self.copy_path) else self.original_path
        self._connect(db_path, create_tables)

    def _connect(self, db_path, create_tables = False):
        DATABASE_URL = f"sqlite:///{db_path}"
        self.engine = create_engine(DATABASE_URL, connect_args = {"check_same_thread": False})
        session_factory = sessionmaker(autocommit = False, autoflush = False, bind = self.engine)
        self.scoped_session = scoped_session(session_factory)

        if create_tables:
            Base.metadata.create_all(bind = self.engine)

    def get_session(self):
        if not self.scoped_session:
            self.set_database()
        else:
            # Check if a copy has appeared since last connection
            current_db = str(self.engine.url).replace("sqlite:///", "")
            if os.path.exists(self.copy_path) and current_db != self.copy_path:
                # Switch to copy
                self._connect(self.copy_path)
            elif not os.path.exists(self.copy_path) and current_db != self.original_path:
                # Copy was discarded → switch back to original
                self._connect(self.original_path)

        return self.scoped_session()
    
class Game(Base):
    __tablename__ = "games"

    id = Column(String(256), primary_key = True, default = lambda: str(uuid.uuid4()))
    manager_id = Column(String(256), nullable = False)
    save_name = Column(String(128), nullable = False)
    curr_date = Column(DateTime, nullable = False, default = SEASON_START_DATE)

    @classmethod
    def add_game(cls, manager_id, save_name):
        session = GamesDatabaseManager().get_session()
        try:
            new_game = Game(
                manager_id = manager_id,
                save_name = save_name,
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
    def add_game_back(cls, manager_id, save_name, curr_date):
        session = GamesDatabaseManager().get_session()
        try:
            new_game = Game(
                manager_id = manager_id,
                save_name = save_name,
                curr_date = datetime.datetime.fromisoformat(curr_date)
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
    def increment_game_date(cls, manager_id, time):
        session = GamesDatabaseManager().get_session()
        try:
            game = session.query(Game).filter(Game.manager_id == manager_id).first()
            if game:
                game.curr_date += time
                session.commit()
        finally:
            session.close()

    @classmethod
    def get_manager_id_by_save_name(cls, save_name):
        session = GamesDatabaseManager().get_session()
        try:
            game = session.query(Game).filter(Game.save_name == save_name).first()
            return game.manager_id if game else None
        finally:
            session.close()

    @classmethod
    def delete_game_by_save_name(cls, save_name):
        session = GamesDatabaseManager().get_session()
        try:
            game = session.query(Game).filter(Game.save_name == save_name).first()
            if game:
                session.delete(game)
                session.commit()

            # Remove the database file if it exists
            db_path = os.path.join("data", f"{save_name}.db")
            if os.path.exists(db_path):
                os.remove(db_path)
        finally:
            session.close()
    
    @classmethod
    def rename_game(cls, old_save_name, new_save_name):
        session = GamesDatabaseManager().get_session()
        try:
            game = session.query(Game).filter(Game.save_name == old_save_name).first()
            if game:
                game.save_name = new_save_name
                session.commit()

                # Rename the database file if it exists
                old_db_path = os.path.join("data", f"{old_save_name}.db")
                new_db_path = os.path.join("data", f"{new_save_name}.db")
                if os.path.exists(old_db_path):
                    os.rename(old_db_path, new_db_path)
        finally:
            session.close()