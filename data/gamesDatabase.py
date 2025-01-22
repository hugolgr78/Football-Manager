from sqlalchemy import Column, String, BLOB, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from settings import *
import uuid
from data.database import Managers

Base = declarative_base()

class Game(Base):
    __tablename__ = "games"

    id = Column(String(256), primary_key = True, default = lambda: str(uuid.uuid4()))
    # manager_id = Column(String(256), ForeignKey(Managers.id), nullable = False)
    manager_id = Column(String(256), nullable = False)
    first_name = Column(String(128), nullable = False)
    last_name = Column(String(128), nullable = False)
    manager_database_link = Column(String(256), nullable = False)

    @classmethod
    def add_game(cls, session, manager_id, first_name, last_name, manager_database_link):
        new_game = Game(
            manager_id = manager_id,
            first_name = first_name,
            last_name = last_name,
            manager_database_link = manager_database_link)
        
        session.add(new_game)
        session.commit()

        return new_game

    @classmethod
    def get_games_by_manager_id(cls, session, manager_id):
        game = session.query(Game).filter(Game.manager_id == manager_id).all()

        if game:
            return game
        else:
            return None
        
    @classmethod
    def get_all_games(cls, session):
        games = session.query(Game).all()

        if games:
            return games
        else:
            return None

def get_session():
    DATABASE_URL = "sqlite:///data/games.db"
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit = False, autoflush = False, bind = engine)
    return SessionLocal()

def main():
    session = get_session()
    Base.metadata.create_all(bind = session.bind)

if __name__ == "__main__":
    main()