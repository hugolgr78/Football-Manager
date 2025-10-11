import customtkinter as ctk
from settings import *
from data.database import *
from data.gamesDatabase import *
from PIL import Image
import io

from utils.frames import MatchFrame, PlayerFrame, next5Matches, TrophiesFrame, CalendarFrame
from utils.managerProfileLink import ManagerProfileLink
from utils.leagueProfileLink import LeagueProfileLabel
from utils.util_functions import *

class TeamProfile(ctk.CTkFrame):
    def __init__(self, parent, manager_id = None, parentTab = None, changeBackFunction = None):
        super().__init__(parent, fg_color = TKINTER_BACKGROUND, width = 1000, height = 700, corner_radius = 0)

        self.parent = parent
        self.changeBackFunction = changeBackFunction

        if not manager_id:
            self.manager_id = Managers.get_all_user_managers()[0].id
        else:
            self.manager_id = manager_id

        if not parentTab:
            self.parentTab = self.parent
        else:
            self.parentTab = parentTab

        self.manager = Managers.get_manager_by_id(self.manager_id)
        self.team = Teams.get_teams_by_manager(self.manager_id)[0]
        self.leagueData = LeagueTeams.get_league_by_team(self.team.id)
        self.leagueId = self.leagueData.league_id

        self.profile = Profile(self, self.manager_id)

        self.history = None
        if self.manager.user == 1:
            self.titles = ["Profile", "History"]
            self.tabs = [self.profile, self.history]
            self.classNames = [Profile, History]
        else:
            self.squad = None
            self.schedule = None
            self.titles = ["Profile", "Squad", "Schedule", "History"]
            self.tabs = [self.profile, self.squad, self.schedule, self.history]
            self.classNames = [Profile, Squad, Schedule, History]

        self.activeButton = 0
        self.buttons = []

        self.team = Teams.get_teams_by_manager(self.manager_id)[0]
        self.league = LeagueTeams.get_league_by_team(self.team.id)

        self.tabsFrame = ctk.CTkFrame(self, fg_color = TKINTER_BACKGROUND, width = 1000, height = 50, corner_radius = 0)
        self.tabsFrame.pack(expand = True, fill = "both", padx = 10, pady = 10)

        self.createTabs()
        self.profile.pack(expand = True, fill = "both")

    def createTabs(self):

        self.buttonHeight = 40
        self.buttonWidth = 200
        self.button_background = TKINTER_BACKGROUND
        self.hover_background = GREY_BACKGROUND
        self.gap = 0.102

        gapCount = 0
        for i in range(len(self.tabs)):
            button = ctk.CTkButton(self.tabsFrame, text = self.titles[i], font = (APP_FONT, 20), fg_color = self.button_background, corner_radius = 0, height = self.buttonHeight, width = self.buttonWidth, hover_color = self.hover_background)
            button.place(relx = self.gap * gapCount, rely = 0, anchor = "nw")
            button.configure(command = lambda i = i: self.changeTab(i))
            
            gapCount += 2
            self.buttons.append(button)
            self.canvas(6, 55, self.gap * gapCount - 0.005)

        self.buttons[self.activeButton].configure(state = "disabled")

        ctk.CTkCanvas(self.tabsFrame, width = 1220, height = 5, bg = APP_BLUE, bd = 0, highlightthickness = 0).place(relx = 0, rely = 0.82, anchor = "w")

        if self.manager.user == 0:
            backButton = ctk.CTkButton(self.tabsFrame, text = "Back", font = (APP_FONT, 20), fg_color = TKINTER_BACKGROUND, corner_radius = 5, height = self.buttonHeight - 10, width = 100, hover_color = CLOSE_RED, command = lambda: self.changeBackFunction())
            backButton.place(relx = 0.975, rely = 0, anchor = "ne")

    def canvas(self, width, height, relx):
        canvas = ctk.CTkCanvas(self.tabsFrame, width = width, height = height, bg = GREY_BACKGROUND, bd = 0, highlightthickness = 0)
        canvas.place(relx = relx, rely = 0, anchor = "nw")

    def changeTab(self, index):
        self.buttons[self.activeButton].configure(state = "normal")
        self.tabs[self.activeButton].pack_forget()
        
        self.activeButton = index
        self.buttons[self.activeButton].configure(state = "disabled")

        if not self.tabs[self.activeButton]:
            self.tabs[self.activeButton] = globals()[self.classNames[self.activeButton].__name__](self, self.manager_id)

        self.tabs[self.activeButton].pack()

class Profile(ctk.CTkFrame):
    def __init__(self, parent, manager_id):
        super().__init__(parent, fg_color = TKINTER_BACKGROUND, width = 1000, height = 630, corner_radius = 0) 

        self.parent = parent
        self.manager_id = manager_id

        manager = Managers.get_manager_by_id(self.manager_id)

        self.league = League.get_league_by_id(self.parent.leagueData.league_id)

        src = Image.open(io.BytesIO(self.parent.team.logo))
        src.thumbnail((200, 200))
        logo = ctk.CTkImage(src, None, (src.width, src.height))
        ctk.CTkLabel(self, image = logo, text = "", fg_color = TKINTER_BACKGROUND).place(relx = 0.1, rely = 0.2, anchor = "center")

        ctk.CTkLabel(self, text = self.parent.team.name, font = (APP_FONT_BOLD, 30), fg_color = TKINTER_BACKGROUND).place(relx = 0.22, rely = 0.18, anchor = "w")
        position = self.parent.leagueData.position

        if self.league.loaded:
            leagueLabel = LeagueProfileLabel(self, self.manager_id, self.league.name, f"{position}{getSuffix(position)} in ", "", 0, 0, self.parent)
            leagueLabel.place(relx = 0.22, rely = 0.23, anchor = "w")
        else:
            ctk.CTkLabel(self, text = f"{position}{getSuffix(position)} in {self.league.name}", font = (APP_FONT, 20), bg_color = TKINTER_BACKGROUND, text_color = "white").place(relx = 0.22, rely = 0.23, anchor = "w")

        canvas = ctk.CTkCanvas(self, width = 5, height = 300, bg = GREY_BACKGROUND, bd = 0, highlightthickness = 0)
        canvas.place(relx = 0.55, rely = 0.2, anchor = "center")

        ctk.CTkLabel(self, text = f"Founded: {self.parent.team.year_created}", font = (APP_FONT, 20), fg_color = TKINTER_BACKGROUND, text_color = "white").place(relx = 0.6, rely = 0.1, anchor = "w")
        ctk.CTkLabel(self, text = f"Stadium: {self.parent.team.stadium}", font = (APP_FONT, 20), fg_color = TKINTER_BACKGROUND, text_color = "white").place(relx = 0.6, rely = 0.15, anchor = "w")
        ctk.CTkLabel(self, text = f"Manager: ", font = (APP_FONT, 20), fg_color = TKINTER_BACKGROUND, text_color = "white").place(relx = 0.6, rely = 0.2, anchor = "w")
        self.managerLink = ManagerProfileLink(self, self.parent.manager_id, f"{self.parent.manager.first_name} {self.parent.manager.last_name}", "white", 0.69, 0.2, "w", TKINTER_BACKGROUND, self.parent)

        self.players = Players.get_all_players_by_team(self.parent.team.id, youths = False)
        ctk.CTkLabel(self, text = f"Average Age: {round(sum(player.age for player in self.players) / len(self.players))}", font = (APP_FONT, 20), fg_color = TKINTER_BACKGROUND, text_color = "white").place(relx = 0.6, rely = 0.25, anchor = "w")

        self.trophiesFrame = TrophiesFrame(self, self.parent.team.id, GREY_BACKGROUND, 460, 360, 15, 0.02, 0.4, "nw")

        parentTab = self.parent if manager.user == 1 else self.parent.parent

        self.next5 = next5Matches(self, self.manager_id, GREY_BACKGROUND, 460, 360, 60, 0.51, 0.4, "nw", 0.3, parentTab, corner_radius = 15)
        self.next5.showNext5Matches()

class Squad(ctk.CTkFrame):
    def __init__(self, parent, manager_id):
        super().__init__(parent, fg_color = TKINTER_BACKGROUND, width = 1000, height = 630, corner_radius = 0) 

        self.parent = parent
        self.manager_id = manager_id
        self.playerFrames = []
        self.currentStat = "Current ability"

        self.players = Players.get_all_players_by_team(self.parent.team.id, youths = False)

        self.infoFrame = ctk.CTkFrame(self, fg_color = TKINTER_BACKGROUND, width = 1000, height = 40, corner_radius = 0)
        self.infoFrame.pack()

        ctk.CTkLabel(self.infoFrame, text = "Number", font = (APP_FONT_BOLD, 20), fg_color = TKINTER_BACKGROUND).place(relx = 0.07, rely = 0.5, anchor = "center")
        ctk.CTkLabel(self.infoFrame, text = "Name", font = (APP_FONT_BOLD, 20), fg_color = TKINTER_BACKGROUND).place(relx = 0.135, rely = 0.5, anchor = "w")
        ctk.CTkLabel(self.infoFrame, text = "Age", font = (APP_FONT_BOLD, 20), fg_color = TKINTER_BACKGROUND).place(relx = 0.505, rely = 0.5, anchor = "center")
        ctk.CTkLabel(self.infoFrame, text = "Positions", font = (APP_FONT_BOLD, 20), fg_color = TKINTER_BACKGROUND).place(relx = 0.59, rely = 0.5, anchor = "center")
        ctk.CTkLabel(self.infoFrame, text = "Nat", font = (APP_FONT_BOLD, 20), fg_color = TKINTER_BACKGROUND).place(relx = 0.685, rely = 0.5, anchor = "center")
        ctk.CTkLabel(self.infoFrame, text = "Morale", font = (APP_FONT_BOLD, 20), fg_color = TKINTER_BACKGROUND).place(relx = 0.795, rely = 0.5, anchor = "center")

        self.dropDown = ctk.CTkComboBox(
            self.infoFrame,
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
            command = self.changeStat
        )
        self.dropDown.place(relx = 0.4, rely = 0.5, anchor = "center")
        self.dropDown.set("Current ability")

        stats = ["Current ability", "Potential ability", "Form", "Fitness", "Match sharpness", "Goals / Assists", "Yellows / Reds", "POTM Awards"]
        self.dropDown.configure(values = stats)

        self.playersFrame = ctk.CTkScrollableFrame(self, fg_color = TKINTER_BACKGROUND, width = 965, height = 590, corner_radius = 0)
        self.playersFrame.pack()

        caStarRatings = Players.get_players_star_ratings(self.players, self.parent.leagueId)
        paStarRatings = Players.get_players_star_ratings(self.players, self.parent.leagueId, CA = False)

        for player in self.players:
            frame = PlayerFrame(self.parent, self.manager_id, player, self.playersFrame, caStarRatings[player.id], paStarRatings[player.id], teamSquad = False)
            self.playerFrames.append(frame)

    def changeStat(self, value):

        if value == self.currentStat:
            return

        self.currentStat = value
        
        for frame in self.playerFrames:
            frame.stat = value
            frame.addStat()

class Schedule(ctk.CTkFrame):
    def __init__(self, parent, manager_id):
        super().__init__(parent, fg_color = TKINTER_BACKGROUND, width = 1000, height = 630, corner_radius = 0) 

        self.parent = parent
        self.manager_id = manager_id
        self.team = self.parent.team

        self.matches = Matches.get_all_matches_by_team(self.parent.team.id)
        self.league = League.get_league_by_id(self.matches[0].league_id)

        self.matchesFrame = ctk.CTkScrollableFrame(self, fg_color = TKINTER_BACKGROUND, width = 650, height = 590, corner_radius = 0)
        self.matchesFrame.place(relx = 0.01, rely = 0.05, anchor = "nw")

        self.matchInfoFrame = ctk.CTkFrame(self, fg_color = GREY_BACKGROUND, width = 280, height = 560, corner_radius = 15)
        self.matchInfoFrame.place(relx = 0.98, rely = 0.05, anchor = "ne")

        self.calendarFrame = CalendarFrame(self, self.matches, self, self.parent.parentTab, self.matchInfoFrame, self.team.id)

        self.switchButton = ctk.CTkButton(self, text = "List", fg_color = GREY_BACKGROUND, command = self.switchFrames, width = 280, height = 15)
        self.switchButton.place(relx = 0.98, rely = 0.985, anchor = "se")

        self.frames = []

        currentMonth = ""
        for match in self.matches:

            _, text, _ = format_datetime_split(match.date)
            month = text.split(" ")[1]

            if month != currentMonth:
                currentMonth = month
                frame = ctk.CTkFrame(self.matchesFrame, fg_color = TKINTER_BACKGROUND, width = 640, height = 50, corner_radius = 0)
                frame.pack(expand = True, fill = "both", padx = 10, pady = (0, 10))

                ctk.CTkLabel(frame, text = month, font = (APP_FONT_BOLD, 25), fg_color = TKINTER_BACKGROUND).place(relx = 0, rely = 0.5, anchor = "w")

            frame = MatchFrame(self, self.manager_id, match, self.matchesFrame, self.matchInfoFrame, self.parent.parentTab)
            self.frames.append(frame)
            
    def switchFrames(self):
        if self.matchesFrame.winfo_ismapped():
            self.matchesFrame.place_forget()
            self.calendarFrame.place(relx = 0.01, rely = 0.05, anchor = "nw")
            self.switchButton.configure(text = "List")
        else:
            self.calendarFrame.place_forget()
            self.matchesFrame.place(relx = 0.01, rely = 0.05, anchor = "nw")
            self.switchButton.configure(text = "Calendar")

class History(ctk.CTkScrollableFrame):
    def __init__(self, parent, manager_id):
        super().__init__(parent, fg_color = TKINTER_BACKGROUND, width = 965, height = 630, corner_radius = 0) 

        self.parent = parent
        self.manager_id = manager_id