import customtkinter as ctk
from ctypes import windll
from settings import *
from startMenu import StartMenu
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import shutil
import os

def backup_database(db_path, backup_dir):
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    backup_path = os.path.join(backup_dir, f"JohnLocke.db")
    
    shutil.copy2(db_path, backup_path)
    print(f"Database backed up to {backup_path}")

class FootballManager(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Games database set up
        DATABASE_URL = "sqlite:///data/games.db" 
        
        db_path = "data/JohnLocke.db"
        backup_dir = "data/backups"
        backup_database(db_path, backup_dir)

        # Create an engine and a session
        engine = create_engine(DATABASE_URL)
        SessionLocal = sessionmaker(autocommit = False, autoflush = False, bind = engine)
        session = SessionLocal()

        # setup
        windll.shell32.SetCurrentProcessExplicitAppUserModelID('mycompany.myproduct.subproduct.version')
        self.iconbitmap("Images/appLogo.ico")
        self.title("Football Manager")
        ctk.set_appearance_mode("dark")
        self.geometry(str(APP_SIZE[0]) + "x" + str(APP_SIZE[1]))
        self.resizable(False, False)

        self.loginMenu = StartMenu(self, session)

        self.mainloop()

if __name__ == "__main__":
    FootballManager()