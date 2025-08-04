import customtkinter as ctk
from settings import *
from data.database import searchResults, Teams, LeagueTeams, League, Players, Managers, Referees
from utils.util_functions import getSuffix

class Search(ctk.CTkFrame):
    def __init__(self, parent, manager_id):
        super().__init__(parent, fg_color = TKINTER_BACKGROUND, width = 1000, height = 700, corner_radius = 0)

        self.parent = parent
        self.manager_id = manager_id
        self.manager_Team = Teams.get_teams_by_manager(self.manager_id)[0]
        self.team_league_id = LeagueTeams.get_team_by_id(self.manager_Team.id).league_id

        self.search_timer = None  # Add timer variable

        self.searchFrame = ctk.CTkFrame(self, fg_color = TKINTER_BACKGROUND, width = 1000, height = 50)
        self.searchVar = ctk.StringVar()
        self.searchVar.trace_add("write", self.search)  # Detect changes
        self.searchBox = ctk.CTkEntry(self.searchFrame, width = 800, height = 40, border_color = APP_BLUE, border_width = 2, corner_radius = 10, textvariable = self.searchVar)
        self.searchBox.place(relx = 0.11, rely = 0.5, anchor = "w")

        ctk.CTkLabel(self.searchFrame, text = "Search:", font = (APP_FONT_BOLD, 20), text_color = "white", fg_color = TKINTER_BACKGROUND).place(relx = 0.02, rely = 0.5, anchor = "w")
        
        self.clearButton = ctk.CTkButton(self.searchFrame, text = "X", font = (APP_FONT_BOLD, 18), text_color = "white", command = self.reset, hover_color = PIE_RED, fg_color = TKINTER_BACKGROUND, width = 40, corner_radius = 5, height = 40)
        self.clearButton.place(relx = 0.98, rely = 0.5, anchor = "e")

        self.searchFrame.place(relx = 0, rely = 0.01, anchor = "nw")

        canvas = ctk.CTkCanvas(self, width = 1300, height = 5, bg = GREY_BACKGROUND, bd = 0, highlightthickness = 0)
        canvas.place(relx = 0, rely = 0.1, anchor = "nw")

        self.resultsFrame = ctk.CTkFrame(self, fg_color = TKINTER_BACKGROUND, width = 1000, height = 620, corner_radius = 0)
        self.resultsFrame.place(relx = 0, rely = 0.105, anchor = "nw")

    def search(self, *args):

        currSearch = self.searchVar.get().strip()

        # Cancel any existing timer
        if self.search_timer:
            self.after_cancel(self.search_timer)
            self.search_timer = None

        if len(currSearch) == 0:
            # Clear results immediately when search is empty
            for widget in self.resultsFrame.winfo_children():
                widget.destroy()
            return
        
        # Set a new timer to execute search after 0.2 second
        self.search_timer = self.after(200, lambda: self.performSearch(currSearch))

    def performSearch(self, search_text):
        
        # Clear previous results
        for widget in self.resultsFrame.winfo_children():
            widget.destroy()

        self.results = searchResults(search_text)

        startY = 0
        gap = (50 / 620)

        firstDataX = 0.03
        secondDataX = 0.45
        thirdDataX = 0.83

        for i, result in enumerate(self.results):
            resultFrame = ctk.CTkFrame(self.resultsFrame, fg_color = TKINTER_BACKGROUND, width = 1000, height = 50, corner_radius = 0)
            resultFrame.place(relx = 0, rely = startY + gap * i, anchor = "nw")

            resultData = result["data"]

            match result["type"]:
                case "team":
                    ctk.CTkLabel(resultFrame, text = f"{resultData.name}", font = (APP_FONT_BOLD, 18), text_color = "white", fg_color = TKINTER_BACKGROUND).place(relx = firstDataX, rely = 0.5, anchor = "w")

                    teamData = LeagueTeams.get_team_by_id(resultData.id)
                    league = League.get_league_by_id(teamData.league_id)
                    ctk.CTkLabel(resultFrame, text = f"{teamData.position}{getSuffix(teamData.position)} in {league.name}", font = (APP_FONT, 16), text_color = GREY, fg_color = TKINTER_BACKGROUND).place(relx = secondDataX, rely = 0.5, anchor = "w")

                    onClickCommand = self.openTeamProfile
                case "player":
                    ctk.CTkLabel(resultFrame, text = f"{resultData.first_name} {resultData.last_name}", font = (APP_FONT_BOLD, 18), text_color = "white", fg_color = TKINTER_BACKGROUND).place(relx = firstDataX, rely = 0.5, anchor = "w")
                    ctk.CTkLabel(resultFrame, text = f"{resultData.position.capitalize()} ", font = (APP_FONT, 16), text_color = GREY, fg_color = TKINTER_BACKGROUND).place(relx = secondDataX, rely = 0.5, anchor = "w")

                    team = Teams.get_team_by_id(resultData.team_id)
                    ctk.CTkLabel(resultFrame, text = f"{team.name}", font = (APP_FONT, 16), text_color = GREY, fg_color = TKINTER_BACKGROUND).place(relx = thirdDataX, rely = 0.5, anchor = "w")

                    onClickCommand = self.openPlayerProfile
                case "manager":
                    ctk.CTkLabel(resultFrame, text = f"{resultData.first_name} {resultData.last_name}", font = (APP_FONT_BOLD, 18), text_color = "white", fg_color = TKINTER_BACKGROUND).place(relx = firstDataX, rely = 0.5, anchor = "w")
                    ctk.CTkLabel(resultFrame, text = "Manager", font = (APP_FONT, 16), text_color = GREY, fg_color = TKINTER_BACKGROUND).place(relx = secondDataX, rely = 0.5, anchor = "w")

                    team = Teams.get_teams_by_manager(resultData.id)[0]
                    ctk.CTkLabel(resultFrame, text = f"{team.name}", font = (APP_FONT, 16), text_color = GREY, fg_color = TKINTER_BACKGROUND).place(relx = thirdDataX, rely = 0.5, anchor = "w")

                    onClickCommand = self.openManagerProfile
                case "league":
                    ctk.CTkLabel(resultFrame, text = f"{resultData.name}", font = (APP_FONT_BOLD, 18), text_color = "white", fg_color = TKINTER_BACKGROUND).place(relx = firstDataX, rely = 0.5, anchor = "w")
                    ctk.CTkLabel(resultFrame, text = "Country", font = (APP_FONT, 16), text_color = GREY, fg_color = TKINTER_BACKGROUND).place(relx = secondDataX, rely = 0.5, anchor = "w")

                    onClickCommand = self.openLeagueProfile
                case "referee":
                    ctk.CTkLabel(resultFrame, text = f"{resultData.first_name} {resultData.last_name}", font = (APP_FONT_BOLD, 18), text_color = "white", fg_color = TKINTER_BACKGROUND).place(relx = firstDataX, rely = 0.5, anchor = "w")
                    ctk.CTkLabel(resultFrame, text = "Referee", font = (APP_FONT, 16), text_color = GREY, fg_color = TKINTER_BACKGROUND).place(relx = secondDataX, rely = 0.5, anchor = "w")

                    onClickCommand = self.openRefereeProfile

            resultFrame.bind("<Enter>", lambda e, f = resultFrame: self.onFrameHover(f))
            resultFrame.bind("<Leave>", lambda e, f = resultFrame: self.onFrameLeave(f))
            resultFrame.bind("<Button-1>", lambda e, cmd = onClickCommand, r = result: cmd(r["data"].id))

            for child in resultFrame.winfo_children():
                child.bind("<Enter>", lambda e, f = resultFrame: self.onFrameHover(f))
                child.bind("<Button-1>", lambda e, cmd = onClickCommand, r = result: cmd(r["data"].id))
            
    def onFrameHover(self, frame):
        frame.configure(fg_color = GREY_BACKGROUND)

        for widget in frame.winfo_children():
            widget.configure(fg_color = GREY_BACKGROUND)

    def onFrameLeave(self, frame):
        frame.configure(fg_color = TKINTER_BACKGROUND)

        for widget in frame.winfo_children():
            widget.configure(fg_color = TKINTER_BACKGROUND)

    def reset(self):
        # Cancel any pending search
        if self.search_timer:
            self.after_cancel(self.search_timer)
            self.search_timer = None
            
        self.searchVar.set("")

        for widget in self.resultsFrame.winfo_children():
            widget.destroy()

    def openTeamProfile(self, team_id):
        team = Teams.get_team_by_id(team_id)
        if team.id == self.manager_Team.id:
            self.parent.changeTab(5)
        else:
            from tabs.teamProfile import TeamProfile

            self.profile = TeamProfile(self, team.manager_id, parentTab = self, changeBackFunction = self.changeBack)
            self.profile.place(x = 0, y = 0, anchor = "nw")
            self.parent.overlappingProfiles.append(self.profile)

    def openPlayerProfile(self, player_id):
        from tabs.playerProfile import PlayerProfile

        player = Players.get_player_by_id(player_id)
        self.profile = PlayerProfile(self, player, changeBackFunction = self.changeBack)
        self.profile.place(x = 0, y = 0, anchor = "nw")
        self.parent.overlappingProfiles.append(self.profile)

    def openManagerProfile(self, manager_id):
        from tabs.managerProfile import ManagerProfile

        manager = Managers.get_manager_by_id(manager_id)
        if manager.user != 1:
            self.profile = ManagerProfile(self, manager_id, changeBackFunction = self.changeBack)
            self.profile.place(x = 0, y = 0, anchor = "nw")
            self.parent.overlappingProfiles.append(self.profile)
        else:
            self.parent.changeTab(7)

    def openLeagueProfile(self, league_id):
        from tabs.leagueProfile import LeagueProfile

        if league_id != self.team_league_id:
            self.profile = LeagueProfile(self, league_id, changeBackFunction = self.changeBack)
            self.profile.place(x = 0, y = 0, anchor = "nw")
            self.parent.overlappingProfiles.append(self.profile)
        else:
            self.parent.changeTab(6)

    def openRefereeProfile(self, referee_id):
        from tabs.refereeProfile import RefereeProfile

        referee = Referees.get_referee_by_id(referee_id)
        self.profile = RefereeProfile(self, referee, changeBackFunction = self.changeBack)
        self.profile.place(x = 0, y = 0, anchor = "nw")
        self.parent.overlappingProfiles.append(self.profile)

    def changeBack(self):
        self.profile.place_forget()