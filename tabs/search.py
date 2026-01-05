import customtkinter as ctk
from settings import *
from data.database import Matches, searchResults, Teams, LeagueTeams, League, Players, Managers, Referees
from utils.util_functions import getSuffix, append_overlapping_profile

class Search(ctk.CTkFrame):
    def __init__(self, parent):
        """
        Initialize the Search frame for searching teams, players, managers, leagues, referees, and matches.
        
        Args:
            parent (ctk.CTkFrame): The parent frame (main menu).
        """
        
        super().__init__(parent, fg_color = TKINTER_BACKGROUND, width = 1000, height = 700, corner_radius = 0)

        self.parent = parent
        self.manager_id = Managers.get_all_user_managers()[0].id
        self.manager_Team = Teams.get_teams_by_manager(self.manager_id)[0]
        self.team_league_id = LeagueTeams.get_team_by_id(self.manager_Team.id).league_id

        self.search_timer = None  # Add timer variable

        self.searchFrame = ctk.CTkFrame(self, fg_color = TKINTER_BACKGROUND, width = 1000, height = 50)
        self.searchVar = ctk.StringVar()
        self.searchVar.trace_add("write", self.search)  # Detect changes
        self.searchBox = ctk.CTkEntry(self.searchFrame, width = 800, height = 40, border_color = APP_BLUE, border_width = 2, corner_radius = 10, textvariable = self.searchVar)
        self.searchBox.place(relx = 0.11, rely = 0.5, anchor = "w")

        # Put focus on search box
        self.searchBox.focus()

        ctk.CTkLabel(self.searchFrame, text = "Search:", font = (APP_FONT_BOLD, 20), text_color = "white", fg_color = TKINTER_BACKGROUND).place(relx = 0.02, rely = 0.5, anchor = "w")
        
        self.clearButton = ctk.CTkButton(self.searchFrame, text = "X", font = (APP_FONT_BOLD, 18), text_color = "white", command = self.reset, hover_color = PIE_RED, fg_color = TKINTER_BACKGROUND, width = 40, corner_radius = 5, height = 40)
        self.clearButton.place(relx = 0.98, rely = 0.5, anchor = "e")

        self.searchFrame.place(relx = 0, rely = 0.01, anchor = "nw")

        canvas = ctk.CTkCanvas(self, width = 1300, height = 5, bg = GREY_BACKGROUND, bd = 0, highlightthickness = 0)
        canvas.place(relx = 0, rely = 0.1, anchor = "nw")

        self.resultsFrame = ctk.CTkFrame(self, fg_color = TKINTER_BACKGROUND, width = 1000, height = 620, corner_radius = 0)
        self.resultsFrame.place(relx = 0, rely = 0.105, anchor = "nw")

    def search(self, *args):
        """
        Handle search input changes with a delay to optimize performance.
        
        Args:
            *args: Additional arguments (not used).
        """

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
        """
        Perform the search and update the results display.
        
        Args:
            search_text (str): The text to search for.
        """
        
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

                    team = Teams.get_teams_by_manager(resultData.id)

                    if team:
                        ctk.CTkLabel(resultFrame, text = f"{team[0].name}", font = (APP_FONT, 16), text_color = GREY, fg_color = TKINTER_BACKGROUND).place(relx = thirdDataX, rely = 0.5, anchor = "w")

                    onClickCommand = self.openManagerProfile
                case "league":
                    ctk.CTkLabel(resultFrame, text = f"{resultData.name}", font = (APP_FONT_BOLD, 18), text_color = "white", fg_color = TKINTER_BACKGROUND).place(relx = firstDataX, rely = 0.5, anchor = "w")
                    ctk.CTkLabel(resultFrame, text = "League", font = (APP_FONT, 16), text_color = GREY, fg_color = TKINTER_BACKGROUND).place(relx = secondDataX, rely = 0.5, anchor = "w")

                    onClickCommand = self.openLeagueProfile
                case "cup":
                    ctk.CTkLabel(resultFrame, text = f"{resultData.name}", font = (APP_FONT_BOLD, 18), text_color = "white", fg_color = TKINTER_BACKGROUND).place(relx = firstDataX, rely = 0.5, anchor = "w")
                    ctk.CTkLabel(resultFrame, text = "Cup", font = (APP_FONT, 16), text_color = GREY, fg_color = TKINTER_BACKGROUND).place(relx = secondDataX, rely = 0.5, anchor = "w")

                    onClickCommand = self.openCupProfile
                case "referee":
                    league = League.get_league_by_id(resultData.league_id)
                    ctk.CTkLabel(resultFrame, text = f"{resultData.first_name} {resultData.last_name}", font = (APP_FONT_BOLD, 18), text_color = "white", fg_color = TKINTER_BACKGROUND).place(relx = firstDataX, rely = 0.5, anchor = "w")
                    ctk.CTkLabel(resultFrame, text = "Referee", font = (APP_FONT, 16), text_color = GREY, fg_color = TKINTER_BACKGROUND).place(relx = secondDataX, rely = 0.5, anchor = "w")
                    ctk.CTkLabel(resultFrame, text = league.name, font = (APP_FONT, 16), text_color = GREY, fg_color = TKINTER_BACKGROUND).place(relx = thirdDataX, rely = 0.5, anchor = "w")

                    onClickCommand = self.openRefereeProfile
                case "match":
                    league = League.get_league_by_id(resultData.league_id)
                    ctk.CTkLabel(resultFrame, text = f"{Teams.get_team_by_id(resultData.home_id).name} vs {Teams.get_team_by_id(resultData.away_id).name}", font = (APP_FONT_BOLD, 18), text_color = "white", fg_color = TKINTER_BACKGROUND).place(relx = firstDataX, rely = 0.5, anchor = "w")
                    ctk.CTkLabel(resultFrame, text = f"{resultData.score_home} - {resultData.score_away}", font = (APP_FONT, 16), text_color = GREY, fg_color = TKINTER_BACKGROUND).place(relx = secondDataX, rely = 0.5, anchor = "w")
                    ctk.CTkLabel(resultFrame, text = f"{league.name} Matchday {resultData.matchday}", font = (APP_FONT, 16), text_color = GREY, fg_color = TKINTER_BACKGROUND).place(relx = thirdDataX - 0.1, rely = 0.5, anchor = "w")

                    onClickCommand = self.openMatchProfile

            resultFrame.bind("<Enter>", lambda e, f = resultFrame: self.onFrameHover(f))
            resultFrame.bind("<Leave>", lambda e, f = resultFrame: self.onFrameLeave(f))
            resultFrame.bind("<Button-1>", lambda e, cmd = onClickCommand, r = result: cmd(r["data"].id))

            for child in resultFrame.winfo_children():
                child.bind("<Enter>", lambda e, f = resultFrame: self.onFrameHover(f))
                child.bind("<Button-1>", lambda e, cmd = onClickCommand, r = result: cmd(r["data"].id))
            
    def onFrameHover(self, frame):
        """
        Handle hover effect on result frames.
        
        Args:
            frame (ctk.CTkFrame): The frame being hovered over.
        """
        
        frame.configure(fg_color = GREY_BACKGROUND)

        for widget in frame.winfo_children():
            widget.configure(fg_color = GREY_BACKGROUND)

    def onFrameLeave(self, frame):
        """
        Handle hover leave effect on result frames.
        
        Args:
            frame (ctk.CTkFrame): The frame being left.
        """
        
        frame.configure(fg_color = TKINTER_BACKGROUND)

        for widget in frame.winfo_children():
            widget.configure(fg_color = TKINTER_BACKGROUND)

    def reset(self):
        """
        Reset the search input and clear results.
        """
        
        if self.search_timer:
            self.after_cancel(self.search_timer)
            self.search_timer = None
            
        self.searchVar.set("")

        for widget in self.resultsFrame.winfo_children():
            widget.destroy()

    def openTeamProfile(self, team_id):
        """
        Open the team profile for the specified team ID.
        
        Args:
            team_id (str): The ID of the team to open the profile for.
        """
        
        team = Teams.get_team_by_id(team_id)
        if team.id == self.manager_Team.id:
            self.parent.changeTab(5)
        else:
            from tabs.teamProfile import TeamProfile

            self.profile = TeamProfile(self, manager_id = team.manager_id, parentTab = self, changeBackFunction = self.changeBack)
            self.profile.place(x = 0, y = 0, anchor = "nw")
            append_overlapping_profile(self, self.profile)

    def openPlayerProfile(self, player_id):
        """
        Open the player profile for the specified player ID.
        
        Args:
            player_id (str): The ID of the player to open the profile for.
        """
        
        from tabs.playerProfile import PlayerProfile

        player = Players.get_player_by_id(player_id)
        self.profile = PlayerProfile(self, player, changeBackFunction = self.changeBack)
        self.profile.place(x = 0, y = 0, anchor = "nw")
        append_overlapping_profile(self, self.profile)

    def openManagerProfile(self, manager_id):
        """
        Open the manager profile for the specified manager ID.

        Args:
            manager_id (str): The ID of the manager to open the profile for.
        """
        
        from tabs.managerProfile import ManagerProfile

        manager = Managers.get_manager_by_id(manager_id)
        if manager.user != 1:
            self.profile = ManagerProfile(self, manager_id = manager_id, changeBackFunction = self.changeBack)
            self.profile.place(x = 0, y = 0, anchor = "nw")
            append_overlapping_profile(self, self.profile)
        else:
            self.parent.changeTab(7)

    def openLeagueProfile(self, league_id):
        """
        Open the league profile for the specified league ID.
        
        Args:
            league_id (str): The ID of the league to open the profile for.
        """
        
        from tabs.leagueProfile import LeagueProfile

        if league_id != self.team_league_id:
            self.profile = LeagueProfile(self, league_id = league_id, changeBackFunction = self.changeBack)
            self.profile.place(x = 0, y = 0, anchor = "nw")
            append_overlapping_profile(self, self.profile)
        else:
            self.parent.changeTab(6)

    def openCupProfile(self, cup_id):
        """
        Open the cup profile for the specified cup ID.
        
        Args:
            cup_id (str): The ID of the cup to open the profile for.
        """
        
        from tabs.cupProfile import CupProfile

        self.profile = CupProfile(self, cup_id = cup_id, changeBackFunction = self.changeBack)
        self.profile.place(x = 0, y = 0, anchor = "nw")
        append_overlapping_profile(self, self.profile)

    def openRefereeProfile(self, referee_id):
        """
        Open the referee profile for the specified referee ID.
        
        Args:
            referee_id (str): The ID of the referee to open the profile for.
        """
        
        from tabs.refereeProfile import RefereeProfile

        referee = Referees.get_referee_by_id(referee_id)
        self.profile = RefereeProfile(self, referee, changeBackFunction = self.changeBack)
        self.profile.place(x = 0, y = 0, anchor = "nw")
        append_overlapping_profile(self, self.profile)

    def openMatchProfile(self, match_id):
        """
        Open the match profile for the specified match ID.
        
        Args:
            match_id (str): The ID of the match to open the profile for.
        """
        
        from tabs.matchProfile import MatchProfile

        match = Matches.get_match_by_id(match_id)
        self.profile = MatchProfile(self, match, self, changeBackFunction = self.changeBack)
        self.profile.place(x = 0, y = 0, anchor = "nw")
        append_overlapping_profile(self, self.profile)

    def changeBack(self):
        """
        Handle the back action to return to the search results.
        """
        
        self.profile.place_forget()