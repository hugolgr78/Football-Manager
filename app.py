import customtkinter as ctk
from ctypes import windll
from settings import *
from startMenu import StartMenu
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class FootballManager(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Games database set up
        DATABASE_URL = "sqlite:///data/games.db"

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