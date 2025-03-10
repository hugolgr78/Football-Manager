import customtkinter as ctk
from settings import *
from data.database import *
from data.gamesDatabase import *
from PIL import Image
import os, datetime, io
from CTkMessagebox import CTkMessagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tabs.mainMenu import MainMenu
from utils.frames import LeagueTable, WinRatePieChart

TOTAL_STEPS = 1003

class StartMenu(ctk.CTkFrame):
    def __init__(self, parent, session):
        super().__init__(parent, fg_color = TKINTER_BACKGROUND)
        self.pack(fill = "both", expand = True)
        
        self.parent = parent
        self.first_name = None
        self.last_name = None
        self.dob = None
        self.selectedCountry = None
        self.last_selected_country = None
        self.selectedTeam = None
        self.last_selected_team = None
        self.session = session
        self.chosenManager = None

        self.createFrame = None
        self.chooseTeamFrame = None
        self.piechart = None

        ## ----------------------------- Menu Frame ----------------------------- ##
        self.menuFrame = ctk.CTkFrame(self, fg_color = DARK_GREY, height = 600, width = 350, corner_radius = 15, border_width = 2, border_color = APP_BLUE)
        self.menuFrame.place(relx = 0.2, rely = 0.5, anchor = "center")
        self.menuFrame.pack_propagate(False)

        ctk.CTkLabel(self.menuFrame, text = "Welcome", font = (APP_FONT_BOLD, 35), bg_color = DARK_GREY).place(relx = 0.5, rely = 0.08, anchor = "center")

        ## ----------------------------- Choose a Manager ----------------------------- ##
        self.chooseFrame = ctk.CTkFrame(self.menuFrame, fg_color = GREY_BACKGROUND, height = 100, width = 300, corner_radius = 15)
        self.chooseFrame.place(relx = 0.5, rely = 0.25, anchor = "center")
        self.chooseFrame.pack_propagate(False)

        ctk.CTkLabel(self.chooseFrame, text = "Choose a Manager", font = (APP_FONT, 20), bg_color = GREY_BACKGROUND).place(relx = 0.05, rely = 0.1, anchor = "nw")

        managers = Game.get_all_games(self.session)
        self.dropDown = ctk.CTkComboBox(self.chooseFrame, font = (APP_FONT, 15), fg_color = GREY_BACKGROUND, corner_radius = 10, dropdown_fg_color = GREY_BACKGROUND, dropdown_hover_color = DARK_GREY, width = 270, height = 30, state = "readonly", command = self.chooseManager)
        self.dropDown.place(relx = 0.05, rely = 0.5, anchor = "nw")

        if not managers:
            values = [""]
            self.dropDown.set("")
            self.dropDown.configure(state = "disabled")
        else:
            values = [f"{manager.first_name} {manager.last_name}" for manager in managers]
            self.dropDown.set("Choose Manager")
            self.dropDown.configure(values = values)

        ## ----------------------------- Format ----------------------------- ##
        canvas = ctk.CTkCanvas(self.menuFrame, width = 160, height = 5, bg = GREY_BACKGROUND, bd = 0, highlightthickness = 0)
        canvas.place(relx = 0.45, rely = 0.365, anchor = "ne")

        ctk.CTkLabel(self.menuFrame, text = "OR", font = (APP_FONT, 15), bg_color = DARK_GREY).place(relx = 0.5, rely = 0.37, anchor = "center")

        canvas = ctk.CTkCanvas(self.menuFrame, width = 160, height = 5, bg = GREY_BACKGROUND, bd = 0, highlightthickness = 0)
        canvas.place(relx = 0.55, rely = 0.365, anchor = "nw")

        ## ----------------------------- Create a Manager ----------------------------- ##
        self.createButton = ctk.CTkButton(self.menuFrame, text = "Create a Manager", font = (APP_FONT, 15), fg_color = GREY_BACKGROUND, corner_radius = 10, width = 200, height = 40, command = self.createManager)
        self.createButton.place(relx = 0.5, rely = 0.45, anchor = "center")

        ## ----------------------------- Logo ----------------------------- ##
        src = Image.open("Images/appLogo.png")
        logo = ctk.CTkImage(src, None, (280, 280))
        ctk.CTkLabel(self.menuFrame, image = logo, text = "", bg_color = DARK_GREY).place(relx = 0.5, rely = 0.75, anchor = "center")

        ## ----------------------------- Choose Frame ----------------------------- ##
        self.showFrame = ctk.CTkFrame(self, fg_color = DARK_GREY, height = 600, width = 700, corner_radius = 15, border_width = 2, border_color = APP_BLUE)

        self.managerNameLabel = ctk.CTkLabel(self.showFrame, text = "", font = (APP_FONT_BOLD, 35), bg_color = DARK_GREY)
        self.managerNameLabel.place(relx = 0.06, rely = 0.05, anchor = "nw")

        self.teamImage = ctk.CTkLabel(self.showFrame, image = None, text = "", bg_color = DARK_GREY)
        self.teamImage.place(relx = 0.81, rely = 0.18, anchor = "center")

        self.tableFrame = LeagueTable(self.showFrame, 480, 420, 0.01, 0.15, DARK_GREY, "nw", highlightManaged = True)

        self.statsFrame = ctk.CTkFrame(self.showFrame, fg_color = GREY_BACKGROUND, height = 300, width = 200, corner_radius = 15)
        self.statsFrame.place(relx = 0.95, rely = 0.35, anchor = "ne")

        ctk.CTkLabel(self.statsFrame, text = "Statistics", font = (APP_FONT_BOLD, 25), bg_color = GREY_BACKGROUND).place(relx = 0.5, rely = 0.08, anchor = "center")

        self.statsGamesPlayed = ctk.CTkLabel(self.statsFrame, text = "Games Played:", font = (APP_FONT, 15), bg_color = GREY_BACKGROUND)
        self.statsGamesPlayed.place(relx = 0.05, rely = 0.2, anchor = "nw")

        self.statsWinRate = ctk.CTkLabel(self.statsFrame, text = "Win Rate:", font = (APP_FONT, 15), bg_color = GREY_BACKGROUND)
        self.statsWinRate.place(relx = 0.05, rely = 0.3, anchor = "nw")

        self.statsTrophies = ctk.CTkLabel(self.statsFrame, text = "Trophies:", font = (APP_FONT, 15), bg_color = GREY_BACKGROUND)
        self.statsTrophies.place(relx = 0.05, rely = 0.4, anchor = "nw")

        self.playButton = ctk.CTkButton(self.showFrame, text = "Play", font = (APP_FONT, 15), fg_color = GREY_BACKGROUND, corner_radius = 10, width = 200, height = 40, command = lambda: self.startGame())
        self.playButton.place(relx = 0.95, rely = 0.95, anchor = "se")

    def chooseManager(self, value):

        if value != self.chosenManager:
            self.chosenManager = value

            ## show the data
            self.showFrame.place(relx = 0.67, rely = 0.5, anchor = "center")
            self.managerNameLabel.configure(text = value)

            first_name = value.split()[0]
            last_name = value.split()[1]

            self.db_manager = DatabaseManager()
            self.db_manager.set_database(f"{first_name}{last_name}")

            manager = Managers.get_manager_by_name(first_name, last_name)
            managedTeam = Teams.get_teams_by_manager(manager.id)
            league = LeagueTeams.get_league_by_team(managedTeam[0].id)

            self.chosenManager_Id = manager.id

            self.tableFrame.defineManager(self.chosenManager_Id)

            logo_blob = managedTeam[0].logo
            image = Image.open(io.BytesIO(logo_blob))
            max_width, max_height = 150, 150 
            image.thumbnail((max_width, max_height))
            ctk_image = ctk.CTkImage(image, None, (image.width, image.height))
            self.teamImage.configure(image = ctk_image)

            self.tableFrame.clearTable()
            self.tableFrame.addLeagueTable()

            if int(manager.games_played) == 0:
                winRate = 0
            else:
                winRate = (int(manager.games_won) / int(manager.games_played)) * 100

            self.statsGamesPlayed.configure(text = f"Games Played: {manager.games_played}")
            self.statsWinRate.configure(text = f"Win Rate: {round(winRate, 2)}%")
            self.statsTrophies.configure(text = f"Trophies: {manager.trophies}")

            self.gamesPieChart(int(manager.games_played), int(manager.games_won), int(manager.games_lost))

    def gamesPieChart(self, gamesPlayed, gamesWon, gamesLost):

        if self.piechart:
            self.piechart.clear()
            self.piechart = None

        self.pieChart = WinRatePieChart(self.statsFrame, gamesPlayed, gamesWon, gamesLost, (3, 1.8), GREY_BACKGROUND, 0.5, 0.72, "center")

    def createManager(self):
            
        self.createFrame = ctk.CTkFrame(self, fg_color = TKINTER_BACKGROUND, height = 600, width = 1150, corner_radius = 15, border_width = 2, border_color = APP_BLUE)
        self.createFrame.place(relx = 0.5, rely = 0.5, anchor = "center")

        ctk.CTkLabel(self.createFrame, text = "Create a Manager", font = (APP_FONT_BOLD, 35), bg_color = TKINTER_BACKGROUND).place(relx = 0.03, rely = 0.08, anchor = "nw")

        self.nextButton = ctk.CTkButton(self.createFrame, text = "Next", font = (APP_FONT, 15), fg_color = GREY_BACKGROUND, corner_radius = 10, width = 100, height = 40, command = self.checkData)
        self.nextButton.place(relx = 0.97, rely = 0.05, anchor = "ne")

        self.backButton = ctk.CTkButton(self.createFrame, text = "Back", font = (APP_FONT, 15), fg_color = GREY_BACKGROUND, corner_radius = 10, width = 100, height = 40, hover_color = CLOSE_RED, command = lambda: self.createFrame.place_forget())
        self.backButton.place(relx = 0.86, rely = 0.05, anchor = "ne")

        ctk.CTkLabel(self.createFrame, text = "First Name", font = (APP_FONT, 20), bg_color = TKINTER_BACKGROUND).place(relx = 0.03, rely = 0.2, anchor = "nw")
        self.first_name_entry = ctk.CTkEntry(self.createFrame, font = (APP_FONT, 15), fg_color = GREY_BACKGROUND, corner_radius = 10, width = 300, height = 45)
        self.first_name_entry.place(relx = 0.03, rely = 0.25, anchor = "nw")

        ctk.CTkLabel(self.createFrame, text = "Last Name", font = (APP_FONT, 20), bg_color = TKINTER_BACKGROUND).place(relx = 0.35, rely = 0.2, anchor = "nw")
        self.last_name_entry = ctk.CTkEntry(self.createFrame, font = (APP_FONT, 15), fg_color = GREY_BACKGROUND, corner_radius = 10, width = 300, height = 45)
        self.last_name_entry.place(relx = 0.35, rely = 0.25, anchor = "nw")

        ctk.CTkLabel(self.createFrame, text = "Date of birth (YYYY/MM/DD)", font = (APP_FONT, 20), bg_color = TKINTER_BACKGROUND).place(relx = 0.67, rely = 0.2, anchor = "nw")
        self.dob_entry = ctk.CTkEntry(self.createFrame, font = (APP_FONT, 15), fg_color = GREY_BACKGROUND, corner_radius = 10, width = 300, height = 45)
        self.dob_entry.place(relx = 0.67, rely = 0.25, anchor = "nw")
        self.dob_entry.bind("<KeyRelease>", self.format_dob)

        ctk.CTkLabel(self.createFrame, text = "Nationality", font = (APP_FONT, 30), bg_color = TKINTER_BACKGROUND).place(relx = 0.03, rely = 0.37, anchor = "nw")

        self.countriesFrame = ctk.CTkFrame(self.createFrame, fg_color = TKINTER_BACKGROUND, height = 330, width = 1050, corner_radius = 15)
        self.countriesFrame.place(relx = 0.5, rely = 0.7, anchor = "center")

        self.countriesFrame.grid_columnconfigure((0, 1, 2 ,3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13), weight = 1)
        self.countriesFrame.grid_rowconfigure((0, 1, 2, 3, 4, 5), weight = 1)
        self.countriesFrame.grid_propagate(False)

        for i, country in enumerate(os.listdir("Images/Countries")):
            path = os.path.join("Images/Countries", country)

            src = Image.open(path)
            src.resize((45, 45))
            image = ctk.CTkImage(src, None, (45, 45))

            button = ctk.CTkButton(self.countriesFrame, image = image, text = "", fg_color = TKINTER_BACKGROUND, width = 70, height = 100, border_width = 2, border_color = TKINTER_BACKGROUND, hover_color = TKINTER_BACKGROUND)
            button.grid(row = i // 14, column = i % 14, padx = 10, pady = 10)
            button.configure(command = lambda b = button, c = country: self.selectCountry(b, c))

            if self.selectedCountry and self.selectedCountry == country:
                button.configure(border_color = APP_BLUE)
                self.last_selected_country = button

    def format_dob(self, event):
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

    def selectCountry(self, button, country):
        country = country.split(".")[0]
        button.configure(border_color = APP_BLUE)
        self.selectedCountry = country

        if self.last_selected_team and self.last_selected_team != button:
            self.last_selected_team.configure(border_color = TKINTER_BACKGROUND)

        self.last_selected_team = button

    def checkData(self):
        self.first_name = self.first_name_entry.get().strip()
        self.last_name = self.last_name_entry.get().strip()
        self.dob = self.dob_entry.get().strip()

        if not self.first_name or not self.last_name or not self.dob or not self.selectedCountry:
            self.nextButton.configure(state = "disabled")
            error = CTkMessagebox(title = "Error", message = "Please fill in all the fields", icon = "cancel")
            self.nextButton.configure(state = "normal")
            return
        
        try:
            self.dob = datetime.datetime.strptime(self.dob, "%Y-%m-%d").date()
        except ValueError:
            self.nextButton.configure(state = "disabled")
            error = CTkMessagebox(title = "Error", message = "Date of birth must be in the format YYYY-MM-DD", icon = "cancel")
            self.nextButton.configure(state = "normal")
            return
        
        self.chooseTeam()
    
    def chooseTeam(self):

        try:
            with open("data/teams.json", "r") as file:
                self.teamsJson = json.load(file)
        except FileNotFoundError:
            self.teamsJson = {}

        self.chooseTeamFrame = ctk.CTkFrame(self, fg_color = TKINTER_BACKGROUND, height = 600, width = 1150, corner_radius = 15, border_width = 2, border_color = APP_BLUE)
        self.chooseTeamFrame.place(relx = 0.5, rely = 0.5, anchor = "center")

        ctk.CTkLabel(self.chooseTeamFrame, text = "Choose a team", font = (APP_FONT_BOLD, 35), bg_color = TKINTER_BACKGROUND).place(relx = 0.03, rely = 0.08, anchor = "nw")

        self.doneButton = ctk.CTkButton(self.chooseTeamFrame, text = "Done", font = (APP_FONT, 15), fg_color = GREY_BACKGROUND, corner_radius = 10, width = 100, height = 45, command = lambda: self.finishCreateManager())
        self.doneButton.place(relx = 0.94, rely = 0.075, anchor = "center")

        self.backButton = ctk.CTkButton(self.chooseTeamFrame, text = "Back", font = (APP_FONT, 15), fg_color = GREY_BACKGROUND, corner_radius = 10, width = 100, height = 45, hover_color = CLOSE_RED, command = lambda: self.chooseTeamFrame.place_forget())
        self.backButton.place(relx = 0.94, rely = 0.165, anchor = "center")

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

        for i, team in enumerate(self.teamsJson):
            path = os.path.join("Images/Teams", team["name"] + ".png")

            src = Image.open(path)
            max_width, max_height = 75, 75 
            src.thumbnail((max_width, max_height))
            ctk_image = ctk.CTkImage(src, None, (src.width, src.height))

            button = ctk.CTkButton(self.teamsFrame, image = ctk_image, text = "", fg_color = TKINTER_BACKGROUND, width = 100, height = 100, border_width = 2, border_color = TKINTER_BACKGROUND, hover_color = TKINTER_BACKGROUND)
            button.grid(row = i // 5, column = i % 5, padx = 10, pady = 10)
            button.configure(command = lambda b = button, t = team: self.selectTeam(b, t))

            if self.selectedTeam and self.selectedTeam == team["name"]:
                self.selectTeam(button, team)

    def selectTeam(self, button, team):
        button.configure(border_color=APP_BLUE)
        self.selectedTeam = team["name"]

        if self.last_selected_team and self.last_selected_team != button:
            self.last_selected_team.configure(border_color = TKINTER_BACKGROUND)

        self.last_selected_team = button

        # Calculate the expected finish
        level = team["level"]
        expected_finish = (200 - level) // 2 + 1
        suffix = self.getSuffix(expected_finish)

        self.teamNameLabel.configure(text = team["name"])
        self.createdLabel.configure(text = "Created: " + str(team["year_created"]))
        self.expectedFinish.configure(text = f"Expected finish: {expected_finish}{suffix}")

    def getSuffix(self, number):
        if 10 <= number % 100 <= 20:
            return "th"
        else:
            return {1: "st", 2: "nd", 3: "rd"}.get(number % 10, "th")

    def finishCreateManager(self):
        
        if not self.selectedTeam:
            self.doneButton.configure(state = "disabled")
            error = CTkMessagebox(title = "Error", message = "Please select a team", icon = "cancel")
            self.doneButton.configure(state = "normal")
            return
        
        self.progressFrame = ctk.CTkFrame(self, fg_color = TKINTER_BACKGROUND, height = 200, width = 500, corner_radius = 15, border_width = 2, border_color = APP_BLUE)
        self.progressFrame.place(relx = 0.5, rely = 0.5, anchor = "center")

        self.progressLabel = ctk.CTkLabel(self.progressFrame, text = "Creating manager...", font = (APP_FONT_BOLD, 30), bg_color = TKINTER_BACKGROUND)
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
        
        self.db_manager = DatabaseManager()
        self.db_manager.set_database(f"{self.first_name}{self.last_name}", create_tables = True)
        manager = Managers.add_manager(self.first_name, self.last_name, self.selectedCountry, self.dob, True, self.selectedTeam)
        self.chosenManager_Id = manager.id
        game = Game.add_game(self.session, self.chosenManager_Id, manager.first_name, manager.last_name, f"sqlite:///data/{self.first_name}{self.last_name}.db")

        self.startGame()

    def startGame(self):
        self.pack_forget()
        MainMenu(self.parent, self.chosenManager_Id)