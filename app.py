import customtkinter as ctk
from ctypes import windll
from settings import *
from startMenu import StartMenu
from data.gamesDatabase import GamesDatabaseManager
import shutil
import os
import glob

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
        
        try:
            shutil.copy2(db_path, backup_path)
            print(f"Database backed up: {db_name}.db -> {backup_path}")
        except Exception as e:
            print(f"Failed to backup {db_name}.db: {e}")

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