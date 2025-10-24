import customtkinter as ctk
from ctypes import windll
from settings import *
from startMenu import StartMenu
from data.gamesDatabase import GamesDatabaseManager
from data.database import DatabaseManager
import sys, signal, logging, os, glob, shutil
from CTkMessagebox import CTkMessagebox
from datetime import datetime

# Enable debug mode if "debug" is passed as a command-line argument
DEBUG_MODE = len(sys.argv) > 1 and sys.argv[1].lower() == "debug"

# Create a logs directory if it doesn't exist
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Log file path (rotates per run, timestamped)
log_filename = os.path.join(LOG_DIR, f"fm_log_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log")

# Configure root logging once at startup
log_level = logging.DEBUG if DEBUG_MODE else logging.WARNING
handlers = [logging.StreamHandler(sys.stdout)]
if DEBUG_MODE:
    # Only write logs to file when debug mode is explicitly enabled
    handlers.append(logging.FileHandler(log_filename, encoding="utf-8"))

logging.basicConfig(
    level=log_level,
    format="%(asctime)s %(name)s %(levelname)s: %(message)s",
    handlers=handlers
)

# Keep custom behaviour for the heavy "utils.match" logger
match_logger = logging.getLogger("utils.match")
if DEBUG_MODE:
    # ensure it emits debug records to stdout (file writing is handled by root handlers when DEBUG_MODE)
    if not any(isinstance(h, logging.StreamHandler) for h in match_logger.handlers):
        match_handler = logging.StreamHandler(sys.stdout)
        match_handler.setLevel(logging.DEBUG)
        match_handler.setFormatter(logging.Formatter("%(asctime)s %(name)s %(levelname)s: %(message)s"))
        match_logger.addHandler(match_handler)

    match_logger.setLevel(logging.DEBUG)
    match_logger.propagate = True
else:
    match_logger.setLevel(logging.CRITICAL)
    match_logger.propagate = True

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

        self.creatingManager = False
        self.loginMenu = StartMenu(self)

        self.mainloop()

    def on_close(self, *args):

        if self.creatingManager:
            return
        elif hasattr(self.loginMenu, "main") and self.loginMenu.main and self.loginMenu.main.movingDate:
            return
        elif self.loginMenu.exporting:
            return

        # List all files in the data folder ending with _copy.db
        copy_files = [f for f in os.listdir("data") if f.endswith("_copy.db")]

        # Step 1: Always ask if the user is sure they want to quit
        response = CTkMessagebox(
            title="Exit",
            message="Are you sure you want to quit?",
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

        if response.get() != "Yes":
            return  # user cancelled quitting

        # Step 2: If there are unsaved changes, ask if they want to save
        if copy_files:
            save_response = CTkMessagebox(
                title="Save Changes",
                message="You have unsaved changes. Would you like to save before quitting?",
                icon="question",
                option_1="Yes",
                option_2="No",
                button_color=(APP_BLUE, CLOSE_RED),
                button_hover_color=(APP_BLUE, CLOSE_RED)
            )
            try:
                if hasattr(save_response, "button_1"):
                    save_response.button_1.configure(hover_color=APP_BLUE)
                if hasattr(save_response, "button_2"):
                    save_response.button_2.configure(hover_color=CLOSE_RED)
            except Exception:
                pass

            db = DatabaseManager()
            if save_response.get() == "Yes":
                if self.loginMenu.main and self.loginMenu.main.tabs[4]:
                    self.loginMenu.main.tabs[4].saveLineup()

                db.commit_copy()
            else:
                db.discard_copy()

        # Finally, quit the app
        self.quit()
        
if __name__ == "__main__":
    FootballManager()
