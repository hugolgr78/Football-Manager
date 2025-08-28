import customtkinter as ctk
from ctypes import windll
from settings import *
from startMenu import StartMenu
from data.gamesDatabase import GamesDatabaseManager
import shutil
import os
import glob
import logging
import sys

# Enable debug mode if "debug" is passed as a command-line argument
DEBUG_MODE = len(sys.argv) > 1 and sys.argv[1].lower() == "debug"

if DEBUG_MODE:
    # Create a dedicated handler for the utils.match logger so DEBUG records show
    match_logger = logging.getLogger("utils.match")
    if not any(isinstance(h, logging.StreamHandler) for h in match_logger.handlers):
        match_handler = logging.StreamHandler(sys.stdout)
        match_handler.setLevel(logging.DEBUG)
        match_handler.setFormatter(logging.Formatter("%(asctime)s %(name)s %(levelname)s: %(message)s"))
        match_logger.addHandler(match_handler)
    match_logger.setLevel(logging.DEBUG)
    # Prevent duplicate propagation to root handlers
    match_logger.propagate = False
else:
    # Silence the logger if not in debug mode
    logging.getLogger("utils.match").setLevel(logging.CRITICAL)

def backup_all_databases(data_dir, backup_dir):
    """Backup all .db files in the data directory"""
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)

    # Find all .db files in the data directory
    db_files = glob.glob(os.path.join(data_dir, "*.db"))
    
    for db_path in db_files:
        # Get the filename without extension
        db_name = os.path.splitext(os.path.basename(db_path))[0]
        backup_path = os.path.join(backup_dir, f"{db_name}.db")
    
        shutil.copy2(db_path, backup_path)

class FootballManager(ctk.CTk):
    def __init__(self):
        super().__init__()

        backup_all_databases("data", "data/backups")

        db_manager = GamesDatabaseManager()
        db_manager.set_database()

        # setup
        windll.shell32.SetCurrentProcessExplicitAppUserModelID('mycompany.myproduct.subproduct.version')
        self.iconbitmap("Images/appLogo.ico")
        self.title("Football Manager")
        ctk.set_appearance_mode("dark")
        self.geometry(str(APP_SIZE[0]) + "x" + str(APP_SIZE[1]))
        self.resizable(False, False)

        self.loginMenu = StartMenu(self)

        self.mainloop()

if __name__ == "__main__":
    FootballManager()
