import customtkinter as ctk
from settings import *
from data.database import *
from data.gamesDatabase import *
from PIL import Image
import io

from utils.frames import MatchFrame, PlayerFrame, next5Matches, TrophiesFrame
from utils.managerProfileLink import ManagerProfileLink

class TeamProfile(ctk.CTkFrame):
    def __init__(self, parent, manager_id, parentTab = None, changeBackFunction = None):
        super().__init__(parent, fg_color = TKINTER_BACKGROUND, width = 1000, height = 700, corner_radius = 0)

        self.parent = parent
        self.manager_id = manager_id
        self.changeBackFunction = changeBackFunction

        if not parentTab:
            self.parentTab = self.parent
        else:
            self.parentTab = parentTab

        self.manager = Managers.get_manager_by_id(manager_id)
        self.team = Teams.get_teams_by_manager(manager_id)[0]
        self.leagueData = LeagueTeams.get_league_by_team(self.team.id)

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

        ctk.CTkLabel(self, text = self.parent.team.name, font = (APP_FONT_BOLD, 30), fg_color = TKINTER_BACKGROUND).place(relx = 0.2, rely = 0.18, anchor = "w")
        position = self.parent.leagueData.position
        ctk.CTkLabel(self, text = f"{position}{self.getSuffix(position)} in {self.league.name}", font = (APP_FONT, 20), fg_color = TKINTER_BACKGROUND).place(relx = 0.2, rely = 0.23, anchor = "w")

        canvas = ctk.CTkCanvas(self, width = 5, height = 300, bg = GREY_BACKGROUND, bd = 0, highlightthickness = 0)
        canvas.place(relx = 0.55, rely = 0.2, anchor = "center")

        ctk.CTkLabel(self, text = f"Founded: {self.parent.team.year_created}", font = (APP_FONT, 20), fg_color = TKINTER_BACKGROUND, text_color = "white").place(relx = 0.6, rely = 0.1, anchor = "w")
        ctk.CTkLabel(self, text = f"Stadium: {self.parent.team.stadium}", font = (APP_FONT, 20), fg_color = TKINTER_BACKGROUND, text_color = "white").place(relx = 0.6, rely = 0.15, anchor = "w")
        ctk.CTkLabel(self, text = f"Manager: ", font = (APP_FONT, 20), fg_color = TKINTER_BACKGROUND, text_color = "white").place(relx = 0.6, rely = 0.2, anchor = "w")
        self.managerLink = ManagerProfileLink(self, self.parent.manager_id, f"{self.parent.manager.first_name} {self.parent.manager.last_name}", "white", 0.69, 0.2, "w", TKINTER_BACKGROUND, self.parent)

        self.players = Players.get_all_players_by_team(self.parent.team.id)
        ctk.CTkLabel(self, text = f"Average Age: {self.averageAge(self.players)}", font = (APP_FONT, 20), fg_color = TKINTER_BACKGROUND, text_color = "white").place(relx = 0.6, rely = 0.25, anchor = "w")

        self.trophiesFrame = TrophiesFrame(self, self.parent.team.id, GREY_BACKGROUND, 460, 360, 15, 0.02, 0.4, "nw")

        parentTab = self.parent if manager.user == 1 else self.parent.parent

        self.next5 = next5Matches(self, self.manager_id, GREY_BACKGROUND, 460, 360, 60, 0.51, 0.4, "nw", 0.3, parentTab, corner_radius = 15)
        self.next5.showNext5Matches()

    def averageAge(self, players):
        
        totalAge = 0
        for player in players:
            totalAge += player.age

        return round(totalAge // len(players))

    def getSuffix(self, number):
        if 10 <= number % 100 <= 20:
            return "th"
        else:
            return {1: "st", 2: "nd", 3: "rd"}.get(number % 10, "th")

class Squad(ctk.CTkFrame):
    def __init__(self, parent, manager_id):
        super().__init__(parent, fg_color = TKINTER_BACKGROUND, width = 1000, height = 630, corner_radius = 0) 

        self.parent = parent
        self.manager_id = manager_id

        self.players = Players.get_all_players_by_team(self.parent.team.id)

        self.infoFrame = ctk.CTkFrame(self, fg_color = TKINTER_BACKGROUND, width = 1000, height = 40, corner_radius = 0)
        self.infoFrame.pack()

        ctk.CTkLabel(self.infoFrame, text = "Number", font = (APP_FONT_BOLD, 20), fg_color = TKINTER_BACKGROUND).place(relx = 0.07, rely = 0.5, anchor = "center")
        ctk.CTkLabel(self.infoFrame, text = "Name", font = (APP_FONT_BOLD, 20), fg_color = TKINTER_BACKGROUND).place(relx = 0.165, rely = 0.5, anchor = "w")
        ctk.CTkLabel(self.infoFrame, text = "Age", font = (APP_FONT_BOLD, 20), fg_color = TKINTER_BACKGROUND).place(relx = 0.46, rely = 0.5, anchor = "center")
        ctk.CTkLabel(self.infoFrame, text = "Positions", font = (APP_FONT_BOLD, 20), fg_color = TKINTER_BACKGROUND).place(relx = 0.59, rely = 0.5, anchor = "center")
        ctk.CTkLabel(self.infoFrame, text = "Nat", font = (APP_FONT_BOLD, 20), fg_color = TKINTER_BACKGROUND).place(relx = 0.685, rely = 0.5, anchor = "center")
        ctk.CTkLabel(self.infoFrame, text = "Morale", font = (APP_FONT_BOLD, 20), fg_color = TKINTER_BACKGROUND).place(relx = 0.795, rely = 0.5, anchor = "center")

        self.playersFrame = ctk.CTkScrollableFrame(self, fg_color = TKINTER_BACKGROUND, width = 965, height = 590, corner_radius = 0)
        self.playersFrame.pack()

        for player in self.players:
            if player.player_role != "Youth Team":
                PlayerFrame(self.parent, self.manager_id, player, self.playersFrame, teamSquad = False)

class Schedule(ctk.CTkFrame):
    def __init__(self, parent, manager_id):
        super().__init__(parent, fg_color = TKINTER_BACKGROUND, width = 1000, height = 630, corner_radius = 0) 

        self.parent = parent
        self.manager_id = manager_id
        self.team = self.parent.team

        self.matches = Matches.get_all_matches_by_team(self.parent.team.id)
        self.league = League.get_league_by_id(self.matches[0].league_id)

        self.matchesFrame = ctk.CTkScrollableFrame(self, fg_color = TKINTER_BACKGROUND, width = 650, height = 590, corner_radius = 0)
        self.matchesFrame.place(relx = 0.02, rely = 0.05, anchor = "nw")

        self.matchInfoFrame = ctk.CTkFrame(self, fg_color = GREY_BACKGROUND, width = 280, height = 590, corner_radius = 15)
        self.matchInfoFrame.place(relx = 0.98, rely = 0.05, anchor = "ne")

        self.frames = []

        for match in self.matches:
            frame = MatchFrame(self, self.manager_id, match, self.matchesFrame, self.matchInfoFrame, self.parent.parentTab)
            self.frames.append(frame)

class History(ctk.CTkScrollableFrame):
    def __init__(self, parent, manager_id):
        super().__init__(parent, fg_color = TKINTER_BACKGROUND, width = 965, height = 630, corner_radius = 0) 

        self.parent = parent
        self.manager_id = manager_id