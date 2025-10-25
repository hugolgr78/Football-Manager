import customtkinter as ctk
from settings import *
from data.database import *
from data.gamesDatabase import *
from PIL import Image
import os, datetime, io, json, zipfile, threading
from CTkMessagebox import CTkMessagebox
from tkinter import filedialog
from tabs.mainMenu import MainMenu
from utils.frames import LeagueTable, WinRatePieChart, ChoosingLeagueFrame
from utils.util_functions import getSuffix

TOTAL_STEPS = 1003

class StartMenu(ctk.CTkFrame):
    def __init__(self, parent):
        """
        The start menu frame where users can choose or create a manager.
        
        Args:
            parent (ctk.CTk): The parent tkinter window.
        """

        super().__init__(parent, fg_color = TKINTER_BACKGROUND)
        self.pack(fill = "both", expand = True)
        
        self.parent = parent
        self.first_name = None
        self.last_name = None
        self.dob = None
        self.selectedPlanet = None
        self.last_selected_planet = None
        self.selectedTeam = None
        self.last_selected_team = None
        self.chosenManager = None
        self.main = None

        self.createFrame = None
        self.chooseTeamFrame = None
        self.piechart = None
        self.exporting = False
        self.exportingEntryActive = False
        self.renaming = False

        ## ----------------------------- Menu Frame ----------------------------- ##
        self.menuFrame = ctk.CTkFrame(self, fg_color = DARK_GREY, height = 600, width = 350, corner_radius = 15, border_width = 2, border_color = APP_BLUE)
        self.menuFrame.place(relx = 0.2, rely = 0.5, anchor = "center")
        self.menuFrame.pack_propagate(False)

        ctk.CTkLabel(self.menuFrame, text = "Welcome", font = (APP_FONT_BOLD, 35), bg_color = DARK_GREY).place(relx = 0.5, rely = 0.08, anchor = "center")

        ## ----------------------------- Choose a Save ----------------------------- ##
        self.chooseFrame = ctk.CTkFrame(self.menuFrame, fg_color = GREY_BACKGROUND, height = 100, width = 300, corner_radius = 15)
        self.chooseFrame.place(relx = 0.5, rely = 0.25, anchor = "center")
        self.chooseFrame.pack_propagate(False)

        ctk.CTkLabel(self.chooseFrame, text = "Choose a Save", font = (APP_FONT, 20), bg_color = GREY_BACKGROUND).place(relx = 0.05, rely = 0.1, anchor = "nw")

        saves = Game.get_all_games()
        self.dropDown = ctk.CTkComboBox(
            self.chooseFrame,
            font = (APP_FONT, 15),
            fg_color = DARK_GREY,
            border_color = DARK_GREY,
            button_color = DARK_GREY,
            button_hover_color = DARK_GREY,
            corner_radius = 10,
            dropdown_fg_color = DARK_GREY,
            dropdown_hover_color = DARK_GREY,
            width = 270,
            height = 30,
            state = "readonly",
            command = self.chooseManager
        )
        self.dropDown.place(relx = 0.05, rely = 0.5, anchor = "nw")

        if not saves:
            values = [""]
            self.dropDown.set("")
            self.dropDown.configure(state = "disabled")
        else:
            values = [save.save_name for save in saves]
            self.dropDown.set("")
            self.dropDown.configure(values = values)

        ## ----------------------------- Format ----------------------------- ##
        canvas = ctk.CTkCanvas(self.menuFrame, width = 160, height = 5, bg = GREY_BACKGROUND, bd = 0, highlightthickness = 0)
        canvas.place(relx = 0.45, rely = 0.368, anchor = "ne")

        ctk.CTkLabel(self.menuFrame, text = "OR", font = (APP_FONT, 15), bg_color = DARK_GREY).place(relx = 0.5, rely = 0.37, anchor = "center")

        canvas = ctk.CTkCanvas(self.menuFrame, width = 160, height = 5, bg = GREY_BACKGROUND, bd = 0, highlightthickness = 0)
        canvas.place(relx = 0.55, rely = 0.368, anchor = "nw")

        ## ----------------------------- Create a Save ----------------------------- ##
        self.createButton = ctk.CTkButton(self.menuFrame, text = "Create Save", font = (APP_FONT, 15), fg_color = GREY_BACKGROUND, corner_radius = 10, width = 150, height = 40, command = self.createManager)
        self.createButton.place(relx = 0.48, rely = 0.45, anchor = "e")

        self.importButton = ctk.CTkButton(self.menuFrame, text = "Import Save", font = (APP_FONT, 15), fg_color = GREY_BACKGROUND, corner_radius = 10, width = 150, height = 40, command = self.importSave)
        self.importButton.place(relx = 0.52, rely = 0.45, anchor = "w")

        ## ----------------------------- Logo ----------------------------- ##
        src = Image.open("Images/appLogo.png")
        logo = ctk.CTkImage(src, None, (280, 280))
        ctk.CTkLabel(self.menuFrame, image = logo, text = "", bg_color = DARK_GREY).place(relx = 0.5, rely = 0.75, anchor = "center")

        ## ----------------------------- Choose Frame ----------------------------- ##
        self.showFrame = ctk.CTkFrame(self, fg_color = DARK_GREY, height = 600, width = 700, corner_radius = 15, border_width = 2, border_color = APP_BLUE)

        self.managerNameLabel = ctk.CTkLabel(self.showFrame, text = "", font = (APP_FONT_BOLD, 35), bg_color = DARK_GREY)
        self.managerNameLabel.place(relx = 0.06, rely = 0.05, anchor = "nw")

        self.saveRenameEntry = ctk.CTkEntry(self.showFrame, font = (APP_FONT, 15), fg_color = GREY_BACKGROUND, corner_radius = 10, width = 200, height = 40)
        self.saveRenameButton = ctk.CTkButton(self.showFrame, text = "OK", font = (APP_FONT, 15), fg_color = APP_BLUE, corner_radius = 10, width = 40, height = 40, command = self.finishRenameSave)

        self.teamImage = ctk.CTkLabel(self.showFrame, image = None, text = "", bg_color = DARK_GREY)
        self.teamImage.place(relx = 0.81, rely = 0.18, anchor = "center")

        self.tableFrame = LeagueTable(self.showFrame, 480, 420, 0.01, 0.15, DARK_GREY, "nw", highlightManaged = True)
        self.settingsFrame = ctk.CTkFrame(self.showFrame, fg_color = DARK_GREY, height = 480, width = 420, corner_radius = 15)

        self.statsFrame = ctk.CTkFrame(self.showFrame, fg_color = GREY_BACKGROUND, height = 300, width = 200, corner_radius = 15)
        self.statsFrame.place(relx = 0.95, rely = 0.35, anchor = "ne")

        ctk.CTkLabel(self.statsFrame, text = "Statistics", font = (APP_FONT_BOLD, 25), bg_color = GREY_BACKGROUND).place(relx = 0.5, rely = 0.08, anchor = "center")

        self.statsGamesPlayed = ctk.CTkLabel(self.statsFrame, text = "Games Played:", font = (APP_FONT, 15), bg_color = GREY_BACKGROUND)
        self.statsGamesPlayed.place(relx = 0.05, rely = 0.2, anchor = "nw")

        self.statsWinRate = ctk.CTkLabel(self.statsFrame, text = "Win Rate:", font = (APP_FONT, 15), bg_color = GREY_BACKGROUND)
        self.statsWinRate.place(relx = 0.05, rely = 0.3, anchor = "nw")

        self.statsTrophies = ctk.CTkLabel(self.statsFrame, text = "Trophies:", font = (APP_FONT, 15), bg_color = GREY_BACKGROUND)
        self.statsTrophies.place(relx = 0.05, rely = 0.4, anchor = "nw")

        self.playButton = ctk.CTkButton(self.showFrame, text = "Play", font = (APP_FONT, 15), fg_color = APP_BLUE, corner_radius = 10, width = 145, height = 40, command = lambda: self.startGame())
        self.playButton.place(relx = 0.872, rely = 0.95, anchor = "se")

        src = Image.open("Images/settings.png")
        logo = ctk.CTkImage(src, None, (25, 25))
        self.settingsButton = ctk.CTkButton(self.showFrame, text = "", image = logo, fg_color = GREY_BACKGROUND, hover_color = GREY_BACKGROUND, width = 40, height = 40, corner_radius = 8, command = lambda: self.settings())
        self.settingsButton.place(relx = 0.95, rely = 0.95, anchor = "se")

        self.setupSettings()

        ## ----------------------------- Quit button ----------------------------- ##
        src = Image.open("Images/cross.png")
        logo = ctk.CTkImage(src, None, (20, 20))
        ctk.CTkButton(self.menuFrame, text = "", image = logo, fg_color = DARK_GREY, hover_color = CLOSE_RED, width = 10, height = 10, corner_radius = 15, command = lambda: self.parent.on_close()).place(relx = 0.02, rely = 0.01, anchor = "nw")

    def chooseManager(self, value):
        """
        Handles the selection of a manager from the dropdown.
        
        Args:
            value (str): The selected manager's name.
        """

        if value != self.chosenManager:
            self.chosenManager = value

            ## show the data
            self.showFrame.place(relx = 0.67, rely = 0.5, anchor = "center")
            self.settings(forceTable = True)
            self.managerNameLabel.configure(text = value)
            managerID = Game.get_manager_id_by_save_name(value)

            self.db_manager = DatabaseManager()
            self.db_manager.set_database(value)

            manager = Managers.get_manager_by_id(managerID)
            managedTeam = Teams.get_teams_by_manager(managerID)

            self.chosenManagerID = manager.id
            self.tableFrame.defineManager(self.chosenManagerID)

            logo_blob = managedTeam[0].logo
            image = Image.open(io.BytesIO(logo_blob))
            max_width, max_height = 150, 150 
            image.thumbnail((max_width, max_height))
            ctk_image = ctk.CTkImage(image, None, (image.width, image.height))
            self.teamImage.configure(image = ctk_image)

            self.tableFrame.clearTable()
            self.tableFrame.addLeagueTable()

            # Add the manager statistics and pie chart
            if int(manager.games_played) == 0:
                winRate = 0
            else:
                winRate = (int(manager.games_won) / int(manager.games_played)) * 100

            self.statsGamesPlayed.configure(text = f"Games Played: {manager.games_played}")
            self.statsWinRate.configure(text = f"Win Rate: {round(winRate, 2)}%")
            self.statsTrophies.configure(text = f"Trophies: {manager.trophies}")

            self.gamesPieChart(int(manager.games_played), int(manager.games_won), int(manager.games_lost))

    def setupSettings(self):
        """
        Shows the settings frame for a save
        """

        deleteSaveButton = ctk.CTkButton(self.settingsFrame, text = "Delete Save", font = (APP_FONT, 15), fg_color = APP_BLUE, hover_color = CLOSE_RED, corner_radius = 10, width = 150, height = 40, command = self.deleteSave)
        deleteSaveButton.place(relx = 0.5, rely = 0.35, anchor = "center")

        exportSaveButton = ctk.CTkButton(self.settingsFrame, text = "Export Save", font = (APP_FONT, 15), fg_color = APP_BLUE, corner_radius = 10, width = 150, height = 40, command = self.exportSave)
        exportSaveButton.place(relx = 0.5, rely = 0.5, anchor = "center")

        renameSaveButton = ctk.CTkButton(self.settingsFrame, text = "Rename Save", font = (APP_FONT, 15), fg_color = APP_BLUE, corner_radius = 10, width = 150, height = 40, command = self.renameSave)
        renameSaveButton.place(relx = 0.5, rely = 0.65, anchor = "center")
        
        self.exportProgressBar = ctk.CTkSlider(
            self.settingsFrame, 
            fg_color = DARK_GREY, 
            bg_color = DARK_GREY, 
            corner_radius = 10, 
            width = 340, 
            height = 50, 
            orientation = "horizontal", 
            from_ = 0, 
            to = 100, 
            state = "disabled", 
            button_length = 0,
            button_color = APP_BLUE,
            progress_color = APP_BLUE,
            border_width = 0,
            border_color = GREY_BACKGROUND
        )        

        self.exportProgressLabel = ctk.CTkLabel(self.settingsFrame, text = "0.0%", font = (APP_FONT, 15), bg_color = DARK_GREY)
        
        self.exportNameEntry = ctk.CTkEntry(self.settingsFrame, font = (APP_FONT, 15), fg_color = GREY_BACKGROUND, corner_radius = 10, width = 200, height = 40)
        self.exportNameButton = ctk.CTkButton(self.settingsFrame, text = "OK", font = (APP_FONT, 15), fg_color = APP_BLUE, corner_radius = 10, width = 40, height = 40, command = self.runExportSave)

    def runImport(self, file_path):
        """
        Imports a save from a .fmsave file.
        
        Args:
            file_path (str): The path to the .fmsave file.
        """
        
        try:
            # Open and extract
            with zipfile.ZipFile(file_path, 'r') as zipf:
                # Read metadata first (to get save name)
                meta_file = [f for f in zipf.namelist() if f.endswith("_metadata.json")]
                if not meta_file:
                    raise ValueError("No metadata found in save file.")

                metadata = json.loads(zipf.read(meta_file[0]).decode("utf-8"))
                save_name = metadata["save_name"]
                manager_id = metadata["manager_id"]
                game_date = metadata["current_date"]

                existing_games = Game.get_all_games()   
                if existing_games:
                    for game in existing_games:
                        if game.save_name.lower() == save_name.lower():
                            CTkMessagebox(title = "Error", message = "This save already exists. Please choose a different file or rename the existing save.", icon = "cancel")
                            return

                # Extract manager’s DB into /data/
                db_files = [f for f in zipf.namelist() if f.endswith(".db") and f != "games.db"]
                if not db_files:
                    raise ValueError("No manager database found in save file.")

                original_db_name = db_files[0]
                os.makedirs("data", exist_ok=True)
                dest_path = os.path.join("data", f"{save_name}.db")

                with open(dest_path, "wb") as f:
                    f.write(zipf.read(original_db_name))

                Game.add_game_back(manager_id, save_name, game_date)
                self.parent.after(0, lambda: self.importComplete(save_name))

        except Exception as e:
            print(f"Error importing save: {e}")

    def importSave(self):
        """
        Imports a save from a .fmsave file using a thread.
        """
        
        # Let user choose a file
        file_path = filedialog.askopenfilename(
            title = "Select Save File",
            filetypes = [("Football Manager Save", "*.fmsave")]
        )

        if not file_path:
            return

        self.disableWidgets()
        threading.Thread(target = self.runImport, args = (file_path,), daemon = True).start()
            
    def importComplete(self, save_name):
        """
        Re-enables widgets and updates the dropdown after import.
        
        Args:
            save_name (str): The name of the imported save.
        """
        
        saves = Game.get_all_games()
        values = [save.save_name for save in saves]
        self.enableWidgets()
        self.dropDown.configure(values = values, state = "normal")
        self.dropDown.set(save_name)

        self.chooseManager(save_name)
        self.settings(forceTable = True)


    def renameSave(self):
        """
        Prompts the user to rename the current save.
        """

        if self.renaming:
            return
        
        self.renaming = True
        self.managerNameLabel.place_forget()
        self.saveRenameEntry.place(relx = 0.06, rely = 0.05, anchor = "nw")
        self.saveRenameEntry.delete(0, "end")
        self.saveRenameEntry.insert(0, self.chosenManager)
        self.saveRenameEntry.focus()

        self.saveRenameButton.place(relx = 0.38, rely = 0.05, anchor = "nw")

    def finishRenameSave(self):
        """
        Finishes the renaming process by updating the save name.
        """

        new_name = self.saveRenameEntry.get().strip()
        if new_name:
            Game.rename_game(self.chosenManager, new_name)
            self.chosenManager = new_name
            self.managerNameLabel.configure(text = new_name)

            saves = Game.get_all_games()
            values = [save.save_name for save in saves]
            self.dropDown.configure(values = values)
            self.dropDown.set(new_name)

        self.managerNameLabel.place(relx = 0.06, rely = 0.05, anchor = "nw")
        self.saveRenameEntry.place_forget()
        self.saveRenameButton.place_forget()
        self.renaming = False

    def deleteSave(self):
        """
        Deletes the current save after confirmation.
        """

        response = CTkMessagebox(
            title="Delete Save",
            message="Are you sure you want to delete this save? This action cannot be undone.",
            icon="warning",
            option_1="Delete",
            option_2="Cancel",
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

        if response.get() == "Delete":
            Game.delete_game_by_save_name(self.chosenManager)
            self.showFrame.place_forget()
            self.chosenManager = None
            self.dropDown.set("")
            saves = Game.get_all_games()
            if not saves:
                values = [""]
                self.dropDown.set("")
                self.dropDown.configure(state = "disabled")
            else:
                values = [save.save_name for save in saves]
                self.dropDown.set("")
                self.dropDown.configure(values = values)

    def showProgress(self, done, total):
        """
        Updates the export progress bar.
       
        Args:
            done (int): The number of bytes processed.
            total (int): The total number of bytes to process.
        """
        
        progress = done / total
        self.parent.after(0, lambda: [
            self.exportProgressBar.set(progress * 100),
            self.exportProgressLabel.configure(text = f"{progress * 100:.1f}%")
        ])

    def exportSave(self):
        """
        Prompts the user to enter a save name for the export
        """

        if self.exportingEntryActive:
            return

        self.exportingEntryActive = True
        self.exportNameEntry.place(relx = 0.05, rely = 0.9, anchor = "w")
        self.exportNameEntry.delete(0, "end")
        self.exportNameEntry.insert(0, self.chosenManager)
        self.exportNameEntry.focus()

        self.exportNameButton.place(relx = 0.55, rely = 0.9, anchor = "w")

    def runExportSave(self):
        """
        Exports the current save (manager database + shared game data)
        into a single .fmsave file with live progress.
        """

        # --- Step 1: Disable GUI + show export frame ---
        self.exportingEntryActive = False
        self.disableWidgets()
        self.exportNameEntry.place_forget()
        self.exportNameButton.place_forget()
        self.exportProgressBar.place(relx = 0.05, rely = 0.9, anchor = "w")
        self.exportProgressLabel.place(relx = 0.89, rely = 0.9, anchor = "w")
        
        os.makedirs("exports", exist_ok = True)

        saveName = self.exportNameEntry.get().strip()
        safeName = "".join(c for c in saveName if c.isalnum() or c in ("_", "-")).rstrip()
        database = os.path.join("data", f"{self.chosenManager}.db")
        gamesDatabase = os.path.join("data", "games.db")
        exportPath = f"exports/{safeName}.fmsave"

        total_size = os.path.getsize(database) + os.path.getsize(gamesDatabase)
        self.exportProgressBar.configure(number_of_steps = total_size)
        self.progress_done = 0

        gameDate = Game.get_game_date(self.chosenManagerID)
        metadata = {
            "save_name": saveName,
            "manager_id": self.chosenManagerID,
            "current_date": str(gameDate),
            "exported_at": datetime.datetime.now().isoformat()[:19],
            "version": 1
        }
        metadata_bytes = json.dumps(metadata, indent = 4).encode("utf-8")

        # --- Step 2: Run the export in a thread ---
        def runExport():
            try:
                with zipfile.ZipFile(exportPath, "w", compression=zipfile.ZIP_DEFLATED) as zipf:
                    add_file_with_progress(zipf, database, os.path.basename(database), self.showProgress)
                    add_file_with_progress(zipf, gamesDatabase, os.path.basename(gamesDatabase), self.showProgress)
                    zipf.writestr(f"{saveName}_metadata.json", metadata_bytes)
            except Exception as e:
                print(f"Error exporting save: {e}")
            finally:
                self.parent.after(0, self.exportComplete)

        threading.Thread(target = runExport, daemon = True).start()

    def exportComplete(self):
        """
        Hides the progress UI and re-enables widgets.
        """

        self.exportProgressBar.place_forget()
        self.exportProgressLabel.place_forget()
        self.enableWidgets()  # Re-enable after export
        self.exporting = False

    def disableWidgets(self):
        """
        Disables all interactive widgets in the start menu.
        """

        def recurse_disable(widget):
            if isinstance(widget, (ctk.CTkButton, ctk.CTkComboBox)):
                widget.configure(state = "disabled")
            elif isinstance(widget, ctk.CTkFrame):
                for child in widget.winfo_children():
                    recurse_disable(child)

        for child in self.winfo_children():
            recurse_disable(child)
    
    def enableWidgets(self):
        """
        Enables all interactive widgets in the start menu.
        """

        def recurse_enable(widget):
            if isinstance(widget, (ctk.CTkButton, ctk.CTkComboBox)):
                widget.configure(state = "normal")
            elif isinstance(widget, ctk.CTkFrame):
                for child in widget.winfo_children():
                    recurse_enable(child)

        for child in self.winfo_children():
            recurse_enable(child)

    def settings(self, forceTable = False):
        """
        Toggles between the league table and settings frame.

        Args:
            forceTable (bool): If True, forces the display of the table frame.
        """

        if self.settingsFrame.winfo_ismapped() or forceTable:

            if self.renaming:
                self.managerNameLabel.place(relx = 0.06, rely = 0.05, anchor = "nw")
                self.saveRenameEntry.place_forget()
                self.saveRenameButton.place_forget()
                self.renaming = False

            if self.exportingEntryActive:
                self.exportNameEntry.place_forget()
                self.exportNameButton.place_forget()
                self.exportingEntryActive = False

            self.settingsFrame.place_forget()
            self.tableFrame.place(relx = 0.01, rely = 0.15, anchor = "nw")
        else:
            self.tableFrame.place_forget()
            self.settingsFrame.place(relx = 0.01, rely = 0.15, anchor = "nw")

    def gamesPieChart(self, gamesPlayed, gamesWon, gamesLost):
        """
        Creates or updates the win rate pie chart in the stats frame.

        Args:
            gamesPlayed (int): The total number of games played.
            gamesWon (int): The number of games won.
            gamesLost (int): The number of games lost.
        """

        if self.piechart:
            self.piechart.clear()
            self.piechart = None

        self.pieChart = WinRatePieChart(self.statsFrame, gamesPlayed, gamesWon, gamesLost, (3, 1.8), GREY_BACKGROUND, 0.5, 0.72, "center")

    def createManager(self):
        """
        Opens the create manager frame.
        """

        self.createFrame = ctk.CTkFrame(self, fg_color = TKINTER_BACKGROUND, height = 600, width = 1150, corner_radius = 15, border_width = 2, border_color = APP_BLUE)
        self.createFrame.place(relx = 0.5, rely = 0.5, anchor = "center")

        ctk.CTkLabel(self.createFrame, text = "Manager profile", font = (APP_FONT_BOLD, 35), bg_color = TKINTER_BACKGROUND).place(relx = 0.03, rely = 0.08, anchor = "nw")

        self.nextButton = ctk.CTkButton(self.createFrame, text = "Leagues >", font = (APP_FONT, 15), fg_color = GREY_BACKGROUND, corner_radius = 10, width = 100, height = 40, command = self.checkData)
        self.nextButton.place(relx = 0.97, rely = 0.05, anchor = "ne")

        backButton = ctk.CTkButton(self.createFrame, text = "Quit", font = (APP_FONT, 15), fg_color = GREY_BACKGROUND, corner_radius = 10, width = 100, height = 40, hover_color = CLOSE_RED, command = lambda: self.createFrame.place_forget())
        backButton.place(relx = 0.86, rely = 0.05, anchor = "ne")

        ctk.CTkLabel(self.createFrame, text = "Save Name", font = (APP_FONT, 20), bg_color = TKINTER_BACKGROUND).place(relx = 0.03, rely = 0.2, anchor = "nw")
        self.saveNameEntry = ctk.CTkEntry(self.createFrame, font = (APP_FONT, 15), fg_color = GREY_BACKGROUND, corner_radius = 10, width = 300, height = 45)
        self.saveNameEntry.place(relx = 0.03, rely = 0.25, anchor = "nw")

        ctk.CTkLabel(self.createFrame, text = "First Name", font = (APP_FONT, 20), bg_color = TKINTER_BACKGROUND).place(relx = 0.03, rely = 0.37, anchor = "nw")
        self.first_name_entry = ctk.CTkEntry(self.createFrame, font = (APP_FONT, 15), fg_color = GREY_BACKGROUND, corner_radius = 10, width = 300, height = 45)
        self.first_name_entry.place(relx = 0.03, rely = 0.42, anchor = "nw")

        ctk.CTkLabel(self.createFrame, text = "Last Name", font = (APP_FONT, 20), bg_color = TKINTER_BACKGROUND).place(relx = 0.03, rely = 0.54, anchor = "nw")
        self.last_name_entry = ctk.CTkEntry(self.createFrame, font = (APP_FONT, 15), fg_color = GREY_BACKGROUND, corner_radius = 10, width = 300, height = 45)
        self.last_name_entry.place(relx = 0.03, rely = 0.59, anchor = "nw")

        ctk.CTkLabel(self.createFrame, text = "Date of birth (YYYY/MM/DD)", font = (APP_FONT, 20), bg_color = TKINTER_BACKGROUND).place(relx = 0.03, rely = 0.71, anchor = "nw")
        self.dob_entry = ctk.CTkEntry(self.createFrame, font = (APP_FONT, 15), fg_color = GREY_BACKGROUND, corner_radius = 10, width = 300, height = 45)
        self.dob_entry.place(relx = 0.03, rely = 0.76, anchor = "nw")
        self.dob_entry.bind("<KeyRelease>", self.format_dob)

        self.natLabel = ctk.CTkLabel(self.createFrame, text = "Nationality", font = (APP_FONT, 30), bg_color = TKINTER_BACKGROUND)
        self.natLabel.place(relx = 0.65, rely = 0.22, anchor = "center")

        self.countriesFrame = ctk.CTkFrame(self.createFrame, fg_color = TKINTER_BACKGROUND, height = 250, width = 800, corner_radius = 15)
        self.countriesFrame.place(relx = 0.3, rely = 0.25, anchor = "nw")

        self.countriesFrame.grid_columnconfigure((0, 1, 2 ,3, 4, 5, 6, 7), weight = 1)
        self.countriesFrame.grid_rowconfigure((0, 1, 2), weight = 1)
        self.countriesFrame.grid_propagate(False)

        # Add the planet buttons
        for i, planet in enumerate(os.listdir("Images/Planets")):
            path = os.path.join("Images/Planets", planet)

            src = Image.open(path)
            src.thumbnail((75, 75))
            image = ctk.CTkImage(src, None, (src.width, src.height))

            button = ctk.CTkButton(self.countriesFrame, image = image, text = "", fg_color = TKINTER_BACKGROUND, width = 80, height = 80, border_width = 2, border_color = TKINTER_BACKGROUND, hover_color = TKINTER_BACKGROUND)
            button.grid(row = i // 8, column = i % 8, padx = 10, pady = 10)
            button.configure(command = lambda b = button, c = planet: self.selectPlanet(b, c))

            if self.selectedPlanet and self.selectedPlanet == planet:
                button.configure(border_color = APP_BLUE)
                self.last_selected_planet = button

    def format_dob(self, event):
        """
        Formats the date of birth entry to the YYYY-MM-DD format.
        
        Args:
            event: The key release event.
        """

        text = self.dob_entry.get().replace("-", "")
        formatted_text = ""

        if len(text) > 4:
            formatted_text = text[:4] + "-"
            if len(text) > 6:
                formatted_text += text[4:6] + "-"
                formatted_text += text[6:]
            else:
                formatted_text += text[4:]
        else:
            formatted_text = text

        self.dob_entry.delete(0, "end")
        self.dob_entry.insert(0, formatted_text)

    def selectPlanet(self, button, planet):
        """
        Handles the selection of a planet
        
        Args:
            button (ctk.CTkButton): The button representing the planet.
            planet (str): The selected planet's filename.
        """

        planet = planet.split(".")[0]
        button.configure(border_color = APP_BLUE)
        self.selectedPlanet = planet

        self.natLabel.place_forget()
        self.natLabel.configure(text = f"Nationality: {planet}")
        self.natLabel.place(relx = 0.65, rely = 0.22, anchor = "center")

        if self.last_selected_team and self.last_selected_team != button:
            self.last_selected_team.configure(border_color = TKINTER_BACKGROUND)

        self.last_selected_team = button

    def checkData(self):
        """
        Validates the input data before proceeding to league selection.
        """

        self.first_name = self.first_name_entry.get().strip()
        self.last_name = self.last_name_entry.get().strip()
        self.dob = self.dob_entry.get().strip()
        self.saveName = self.saveNameEntry.get().strip()

        # If any of the three text fields exceed 20 characters, show an error
        if len(self.first_name) > 20 or len(self.last_name) > 20 or len(self.saveName) > 20:
            self.nextButton.configure(state = "disabled")
            CTkMessagebox(title = "Error", message = "Save name, first name and last name must not exceed 20 characters", icon = "cancel")
            self.nextButton.configure(state = "normal")
            return

        if not self.first_name or not self.last_name or not self.dob or not self.selectedPlanet:
            self.nextButton.configure(state = "disabled")
            CTkMessagebox(title = "Error", message = "Please fill in all the fields", icon = "cancel")
            self.nextButton.configure(state = "normal")
            return
        
        try:
            self.dob = datetime.datetime.strptime(self.dob, "%Y-%m-%d").date()
        except ValueError:
            self.nextButton.configure(state = "disabled")
            CTkMessagebox(title = "Error", message = "Date of birth must be in the format YYYY-MM-DD", icon = "cancel")
            self.nextButton.configure(state = "normal")
            return
        
        if not self.saveName:
            self.nextButton.configure(state = "disabled")
            CTkMessagebox(title = "Error", message = "Please enter a save name", icon = "cancel")
            self.nextButton.configure(state = "normal")
            return
        else:
            existing_games = Game.get_all_games()   

            if existing_games:
                for game in existing_games:
                    if game.save_name.lower() == self.saveName.lower():
                        self.nextButton.configure(state = "disabled")
                        CTkMessagebox(title = "Error", message = "Save name already exists. Please choose a different one.", icon = "cancel")
                        self.nextButton.configure(state = "normal")
                        return
        
        self.selectLeagues()
        
    def selectLeagues(self):
        """
        Opens the league selection frame.
        """

        self.choosingLeaguesFrame = ChoosingLeagueFrame(self, TKINTER_BACKGROUND, 1150, 600, 15, 2, APP_BLUE, self.chooseTeam)
        self.choosingLeaguesFrame.place(relx = 0.5, rely = 0.5, anchor = "center")
    
    def chooseTeam(self):

        """
        Creates the team selection frame.
        """

        try:
            with open("data/teams.json", "r") as file:
                self.teamsJson = json.load(file)
        except FileNotFoundError:
            self.teamsJson = {}

        self.chooseTeamFrame = ctk.CTkFrame(self, fg_color = TKINTER_BACKGROUND, height = 600, width = 1150, corner_radius = 15, border_width = 2, border_color = APP_BLUE)
        self.chooseTeamFrame.place(relx = 0.5, rely = 0.5, anchor = "center")

        ctk.CTkLabel(self.chooseTeamFrame, text = "Choose a team", font = (APP_FONT_BOLD, 35), bg_color = TKINTER_BACKGROUND).place(relx = 0.03, rely = 0.08, anchor = "nw")

        self.doneButton = ctk.CTkButton(self.chooseTeamFrame, text = "Finish", font = (APP_FONT, 15), fg_color = GREY_BACKGROUND, corner_radius = 10, width = 100, height = 45, command = lambda: self.finishCreateManager())
        self.doneButton.place(relx = 0.94, rely = 0.075, anchor = "center")

        backButton = ctk.CTkButton(self.chooseTeamFrame, text = "< Leagues", font = (APP_FONT, 15), fg_color = GREY_BACKGROUND, corner_radius = 10, width = 100, height = 45, hover_color = CLOSE_RED, command = lambda: self.chooseTeamFrame.place_forget())
        backButton.place(relx = 0.94, rely = 0.165, anchor = "center")

        self.teamInfoFrame = ctk.CTkFrame(self.chooseTeamFrame, fg_color = GREY_BACKGROUND, height = 100, width = 570, corner_radius = 15)
        self.teamInfoFrame.place(relx = 0.63, rely = 0.12, anchor = "center")

        self.teamNameLabel = ctk.CTkLabel(self.teamInfoFrame, text = "", font = (APP_FONT_BOLD, 30), bg_color = GREY_BACKGROUND)
        self.teamNameLabel.place(relx = 0.05, rely = 0.3, anchor = "nw")

        self.createdLabel = ctk.CTkLabel(self.teamInfoFrame, text = "Created: ", font = (APP_FONT, 20), bg_color = GREY_BACKGROUND)
        self.createdLabel.place(relx = 0.65, rely = 0.2, anchor = "nw")

        self.expectedFinish = ctk.CTkLabel(self.teamInfoFrame, text = "Expected finish: ", font = (APP_FONT, 20), bg_color = GREY_BACKGROUND)
        self.expectedFinish.place(relx = 0.65, rely = 0.5, anchor = "nw")

        self.teamsFrame = ctk.CTkFrame(self.chooseTeamFrame, fg_color = TKINTER_BACKGROUND, height = 420, width = 1050, corner_radius = 15)
        self.teamsFrame.place(relx = 0.5, rely = 0.63, anchor = "center")
        self.teamsFrame.grid_columnconfigure((0, 1, 2 ,3, 4), weight = 1)
        self.teamsFrame.grid_rowconfigure((0, 1, 2, 3), weight = 1)
        self.teamsFrame.grid_propagate(False)

        self.planetDropDown = ctk.CTkComboBox(self.chooseTeamFrame,
            font = (APP_FONT, 15),
            fg_color = DARK_GREY,
            border_color = DARK_GREY,
            button_color = DARK_GREY,
            button_hover_color = DARK_GREY,
            corner_radius = 10,
            dropdown_fg_color = DARK_GREY,
            dropdown_hover_color = DARK_GREY,
            width = 150,
            height = 30,
            state = "readonly",
            command = self.choosePlanet)
        self.planetDropDown.place(relx = 0.03, rely = 0.18, anchor = "nw")

        # Populates the planet dropdown based on the chosen leagues
        values = []
        for planet, leagues in PLANET_LEAGUES.items():
            addPlanet = False
            for league in leagues:
                if self.choosingLeaguesFrame.loadedLeagues[league] == 1:
                    addPlanet = True
                    break
            
            if addPlanet:
                values.append(planet)

        self.planetDropDown.configure(values = values)
        
        self.leagueDropDown = ctk.CTkComboBox(self.chooseTeamFrame,
            font = (APP_FONT, 13),
            fg_color = DARK_GREY,
            border_color = DARK_GREY,
            button_color = DARK_GREY,
            button_hover_color = DARK_GREY,
            corner_radius = 10,
            dropdown_fg_color = DARK_GREY,
            dropdown_hover_color = DARK_GREY,
            width = 150,
            height = 30,
            state = "readonly",
            command = self.chooseLeague)
        self.leagueDropDown.place(relx = 0.18, rely = 0.18, anchor = "nw")

    def choosePlanet(self, planet):
        """
        Populates the league dropdown based on the chosen planet.
        """
        
        values = []
        for league, val in self.choosingLeaguesFrame.loadedLeagues.items():
            if league in PLANET_LEAGUES[planet] and val == 1:
                values.append(league)

        self.leagueDropDown.configure(values = values)

    def chooseLeague(self, league):
        """
        Handles the selection of a league and displays the corresponding teams.

        Args:
            league (str): The selected league.
        """

        count = 0
        self.currentTeams = []

        for child in self.teamsFrame.winfo_children():
            child.destroy()

        for team in self.teamsJson:

            if team["league"] != league:
                continue

            self.currentTeams.append(team)
            path = team["logo"]

            src = Image.open(path)
            max_width, max_height = 75, 75 
            src.thumbnail((max_width, max_height))
            ctk_image = ctk.CTkImage(src, None, (src.width, src.height))

            button = ctk.CTkButton(self.teamsFrame, image = ctk_image, text = "", fg_color = TKINTER_BACKGROUND, width = 100, height = 100, border_width = 2, border_color = TKINTER_BACKGROUND, hover_color = TKINTER_BACKGROUND)
            button.grid(row = count // 5, column = count % 5, padx = 10, pady = 10)
            button.configure(command = lambda b = button, t = team: self.selectTeam(b, t))

            if self.selectedTeam and self.selectedTeam == team["name"]:
                self.selectTeam(button, team)

            count += 1

    def selectTeam(self, button, team):
        """
        Handles the selection of a team.

        Args:
            button (ctk.CTkButton): The button representing the team.
            team (dict): The selected team's data.
        """

        button.configure(border_color=APP_BLUE)
        self.selectedTeam = team["name"]

        if self.last_selected_team and self.last_selected_team != button:
            self.last_selected_team.configure(border_color = TKINTER_BACKGROUND)

        self.last_selected_team = button

        # Calculate the expected finish
        teamStrengths = [(t["name"], t["strength"]) for t in self.currentTeams]
        expectedFinish = expected_finish(team["name"], teamStrengths)
        suffix = getSuffix(expectedFinish)

        self.teamNameLabel.configure(text = team["name"])
        self.createdLabel.configure(text = "Created: " + str(team["year_created"]))
        self.expectedFinish.configure(text = f"Expected finish: {expectedFinish}{suffix}")

    def finishCreateManager(self):
        """
        Finalizes the manager creation process and starts the game.
        """
        
        if not self.selectedTeam:
            self.doneButton.configure(state = "disabled")
            CTkMessagebox(title = "Error", message = "Please select a team", icon = "cancel")
            self.doneButton.configure(state = "normal")
            return
        
        self.progressFrame = ctk.CTkFrame(self, fg_color = TKINTER_BACKGROUND, height = 200, width = 500, corner_radius = 15, border_width = 2, border_color = APP_BLUE)
        self.progressFrame.place(relx = 0.5, rely = 0.5, anchor = "center")

        self.progressLabel = ctk.CTkLabel(self.progressFrame, text = "Creating Managers...", font = (APP_FONT_BOLD, 30), bg_color = TKINTER_BACKGROUND)
        self.progressLabel.place(relx = 0.5, rely = 0.2, anchor = "center")

        self.progressBar = ctk.CTkSlider(
            self.progressFrame, 
            fg_color = GREY_BACKGROUND, 
            bg_color = TKINTER_BACKGROUND, 
            corner_radius = 10, 
            width = 400, 
            height = 50, 
            orientation = "horizontal", 
            from_ = 0, 
            to = 100, 
            state = "disabled", 
            number_of_steps = TOTAL_STEPS,
            button_length = 0,
            button_color = APP_BLUE,
            progress_color = APP_BLUE,
            border_width = 0,
            border_color = GREY_BACKGROUND
        )
        
        self.progressBar.place(relx = 0.5, rely = 0.52, anchor = "center")
        self.progressBar.set(0)

        self.percentageLabel = ctk.CTkLabel(self.progressFrame, text = "0%", font = (APP_FONT, 20), bg_color = TKINTER_BACKGROUND)  
        self.percentageLabel.place(relx = 0.5, rely = 0.76, anchor = "center")

        ctk.CTkLabel(self.progressFrame, text = "This might take a few minutes", font = (APP_FONT, 10), bg_color = TKINTER_BACKGROUND).place(relx = 0.5, rely = 0.9, anchor = "center")

        setUpProgressBar(self.progressBar, self.progressLabel, self.progressFrame, self.percentageLabel)
        
        # Create the database and copy it to add the data
        self.parent.creatingManager = True
        self.db_manager = DatabaseManager()
        self.db_manager.set_database(self.saveName, create_tables = True)
        self.db_manager.start_copy()

        # Add the data to the database
        self.chosenManagerID = Managers.add_managers(self.first_name, self.last_name, self.selectedPlanet, self.dob, self.selectedTeam, self.choosingLeaguesFrame.loadedLeagues)

        # Add the game to the games database
        Game.add_game(self.chosenManagerID, self.saveName)
        self.parent.creatingManager = False

        self.startGame(created = True)

    def startGame(self, created = False):
        """
        Starts the main game menu.
        """
        
        self.pack_forget()
        self.main = MainMenu(self.parent, self.chosenManagerID, created)