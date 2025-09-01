import customtkinter as ctk
from ctypes import windll
from settings import *
from startMenu import StartMenu
from data.gamesDatabase import GamesDatabaseManager
from data.database import DatabaseManager
import sys, signal, logging, os, glob, shutil
from CTkMessagebox import CTkMessagebox

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

        # If the games DB file doesn't exist, create it and its tables.
        db_path = os.path.join("data", "games.db")
        if not os.path.exists(db_path):
            db_manager.set_database(create_tables = True)
        else:
            db_manager.set_database()

        # setup
        windll.shell32.SetCurrentProcessExplicitAppUserModelID('mycompany.myproduct.subproduct.version')
        self.iconbitmap("Images/appLogo.ico")
        self.title("Football Manager")
        ctk.set_appearance_mode("dark")
        self.geometry(str(APP_SIZE[0]) + "x" + str(APP_SIZE[1]))
        self.resizable(False, False)

        self.protocol("WM_DELETE_WINDOW", self.on_close)
        signal.signal(signal.SIGINT, self.on_close)
        self.loginMenu = StartMenu(self)

        self.mainloop()

    def on_close(self, *args):
        # List all files in the data folder ending with _copy.db
        copy_files = [f for f in os.listdir("data") if f.endswith("_copy.db")]

        if copy_files:
            # There are unsaved changes
            response = CTkMessagebox(
                title="Exit",
                message="Would you like to save before quitting?",
                icon="question",
                option_1="Yes",
                option_2="No",
                button_color=(CLOSE_RED, APP_BLUE),
                button_hover_color=(CLOSE_RED, APP_BLUE)
            )
            try:
                if hasattr(response, "button_1"):
                    response.button_1.configure(hover_color=CLOSE_RED)
                if hasattr(response, "button_2"):
                    response.button_2.configure(hover_color=APP_BLUE)
            except Exception:
                pass

            if response.get() == "Yes":
                db = DatabaseManager()
                db.commit_copy()
                self.quit()
        else:
            # No unsaved changes, just confirm exit
            response = CTkMessagebox(
                title="Exit",
                message="Are you sure you want to exit?",
                icon="question",
                option_1="Yes",
                option_2="No",
                button_color=(CLOSE_RED, APP_BLUE),
                button_hover_color=(CLOSE_RED, APP_BLUE)
            )
            try:
                if hasattr(response, "button_1"):
                    response.button_1.configure(hover_color=CLOSE_RED)
                if hasattr(response, "button_2"):
                    response.button_2.configure(hover_color=APP_BLUE)
            except Exception:
                pass

            if response.get() == "Yes":
                self.quit()

if __name__ == "__main__":
    FootballManager()
