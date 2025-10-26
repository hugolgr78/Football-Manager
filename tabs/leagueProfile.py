import customtkinter as ctk
from settings import *
from data.database import *
from data.gamesDatabase import *
from PIL import Image, ImageDraw
import io
from utils.frames import LeagueTable, MatchdayFrame
from utils.playerProfileLink import PlayerProfileLink
from utils.teamLogo import TeamLogo
from utils.util_functions import *

class LeagueProfile(ctk.CTkFrame):
    def __init__(self, parent, league_id = None, changeBackFunction = None, userLeagueProfile = None):
        """
        Class for the League Profile tab in the main menu.
        
        Args:
            parent (ctk.CTkFrame): The parent frame (main menu or other) where the League Profile tab will be placed.
            league_id (str, optional): The ID of the league to display the profile for. If None, displays the user's league. Defaults to None.
            changeBackFunction (function, optional): Function to call when the back button is pressed. Defaults to None.
            userLeagueProfile (LeagueProfile, optional): The user's league profile tab, if applicable. Defaults to None.
        """

        super().__init__(parent, fg_color = TKINTER_BACKGROUND, width = 1000, height = 700, corner_radius = 0)

        self.parent = parent
        self.changeBackFunction = changeBackFunction
        self.userLeagueProfile = userLeagueProfile

        if not league_id:
            # If league_id is not provided, use the user's league
            self.manager_id = Managers.get_all_user_managers()[0].id
            self.team = Teams.get_teams_by_manager(self.manager_id)[0]
            self.leagueTeams = LeagueTeams.get_league_by_team(self.team.id)
            self.league = League.get_league_by_id(self.leagueTeams.league_id)
        else:
            # Otherwise, use the provided league_id
            self.manager_id = None
            self.league_id = league_id
            self.league = League.get_league_by_id(self.league_id)
            self.leagueTeams = LeagueTeams.get_teams_by_league(self.league_id)

        self.leagueAbove = self.league.league_above is not None
        self.leagueBelow = self.league.league_below is not None

        self.profile = Profile(self, self.league)
        self.matchdays = None
        self.graphs = None
        self.stats = None
        self.history = None
        self.news = None
        self.titles = ["Profile", "Matchdays", "Graphs", "Stats", "History", "News"]
        self.tabs = [self.profile, self.matchdays, self.graphs, self.stats, self.history, self.news]
        self.classNames = [Profile, Matchdays, Graphs, Stats, History, News]

        self.activeButton = 0
        self.buttons = []

        self.tabsFrame = ctk.CTkFrame(self, fg_color = TKINTER_BACKGROUND, width = 1000, height = 50, corner_radius = 0)
        self.tabsFrame.pack(expand = True, fill = "both", padx = 10, pady = 10)

        self.createTabs()
        self.profile.pack(expand = True, fill = "both")

    def createTabs(self):
        """
        Creates the tab buttons for the League Profile tab.
        """

        self.buttonHeight = 40
        self.buttonWidth = 140
        self.button_background = TKINTER_BACKGROUND
        self.hover_background = GREY_BACKGROUND
        self.gap = 0.07

        gapCount = 0
        for i in range(len(self.tabs)):
            button = ctk.CTkButton(self.tabsFrame, text = self.titles[i], font = (APP_FONT, 18), fg_color = self.button_background, corner_radius = 0, height = self.buttonHeight, width = self.buttonWidth, hover_color = self.hover_background)
            button.place(relx = self.gap * gapCount, rely = 0, anchor = "nw")
            button.configure(command = lambda i = i: self.changeTab(i))
            
            gapCount += 2
            self.buttons.append(button)
            self.canvas(6, 55, self.gap * gapCount - 0.005)

        self.buttons[self.activeButton].configure(state = "disabled")

        ctk.CTkCanvas(self.tabsFrame, width = 1220, height = 5, bg = APP_BLUE, bd = 0, highlightthickness = 0).place(relx = 0, rely = 0.82, anchor = "w")

        if self.changeBackFunction:
            backButton = ctk.CTkButton(self.tabsFrame, text = "Back", font = (APP_FONT, 20), fg_color = TKINTER_BACKGROUND, corner_radius = 5, height = self.buttonHeight - 10, width = 80, hover_color = CLOSE_RED, command = lambda: self.changeBackFunction())
            backButton.place(relx = 0.94, rely = 0, anchor = "ne")

        self.legendRows = 1
        self.legendRows += 2 if self.leagueAbove else 0
        self.legendRows += 1 if self.leagueBelow else 0

        self.legendFrame = ctk.CTkFrame(self, fg_color = GREY_BACKGROUND, width = 225, height = 30 * self.legendRows, corner_radius = 0, background_corner_colors = [TKINTER_BACKGROUND, TKINTER_BACKGROUND, GREY_BACKGROUND, GREY_BACKGROUND])

        src = Image.open("Images/information.png")
        src.thumbnail((20, 20))
        img = ctk.CTkImage(src, None, (src.width, src.height))
        self.helpButton = ctk.CTkButton(self.tabsFrame, text = "", image = img, fg_color = TKINTER_BACKGROUND, hover_color = TKINTER_BACKGROUND, corner_radius = 5, height = 30, width = 30)
        self.helpButton.place(relx = 0.975, rely = 0, anchor = "ne")
        self.helpButton.bind("<Enter>", lambda e: self.showLegend(e))
        self.helpButton.bind("<Leave>", lambda e: self.legendFrame.place_forget())

        self.legend()

    def showLegend(self, event):
        """
        Shows the legend frame when the help button is hovered over.
        
        Args:
            event: The event that triggered the function.
        """

        self.legendFrame.place(relx = 0.975, rely = 0.1, anchor = "ne")
        self.legendFrame.lift()

    def canvas(self, width, height, relx):
        """
        Creates a canvas for visual separation between tab buttons.
        
        Args:
            width (int): The width of the canvas.
            height (int): The height of the canvas.
            relx (float): The relative x position of the canvas.
        """
        
        canvas = ctk.CTkCanvas(self.tabsFrame, width = width, height = height, bg = GREY_BACKGROUND, bd = 0, highlightthickness = 0)
        canvas.place(relx = relx, rely = 0, anchor = "nw")

    def changeTab(self, index):
        """
        Changes the active tab to the specified index.
        
        Args:
            index (int): The index of the tab to switch to.
        """
        
        self.buttons[self.activeButton].configure(state = "normal")
        self.tabs[self.activeButton].pack_forget()
        
        self.activeButton = index
        self.buttons[self.activeButton].configure(state = "disabled")

        if not self.tabs[self.activeButton]:
            self.tabs[self.activeButton] = globals()[self.classNames[self.activeButton].__name__](self, self.league)

        self.tabs[self.activeButton].pack()

    def legend(self):
        """
        Creates the legend frame for the league profile tab.
        """

        self.legendFrame.grid_rowconfigure(tuple(range(self.legendRows)), weight = 0)
        self.legendFrame.grid_columnconfigure((0), weight = 0)
        self.legendFrame.grid_columnconfigure((1), weight = 1)
        self.legendFrame.grid_propagate(False)

        ctk.CTkLabel(self.legendFrame, text = "Legend", font = (APP_FONT_BOLD, 18), fg_color = GREY_BACKGROUND).grid(row = 0, column = 0, columnspan = 2, pady = (5, 0))

        row = 1
        if self.leagueAbove:
            canvas = ctk.CTkCanvas(self.legendFrame, width = 5, height = 200 / 14.74, bg = PIE_GREEN, bd = 0, highlightthickness = 0)
            canvas.grid(row = row, column = 0, sticky = "w", padx = (8, 0), pady = (0, 2))

            ctk.CTkLabel(self.legendFrame, text = "Promotion", font = (APP_FONT, 12), fg_color = GREY_BACKGROUND).grid(row = row, column = 1, sticky = "w", padx = (8, 0), pady = (0, 2))

            row += 1
            canvas = ctk.CTkCanvas(self.legendFrame, width = 5, height = 200 / 14.74, bg = FRUSTRATED_COLOR, bd = 0, highlightthickness = 0)
            canvas.grid(row = row, column = 0, sticky = "w", padx = (8, 0), pady = (0, 2))

            ctk.CTkLabel(self.legendFrame, text = "Playoffs", font = (APP_FONT, 12), fg_color = GREY_BACKGROUND).grid(row = row, column = 1, sticky = "w", padx = (8, 0), pady = (0, 2))
            row += 1
        
        if self.leagueBelow:
            canvas = ctk.CTkCanvas(self.legendFrame, width = 5, height = 200 / 14.74, bg = PIE_RED, bd = 0, highlightthickness = 0)
            canvas.grid(row = row, column = 0, sticky = "w", padx = (8, 0), pady = (0, 2))

            ctk.CTkLabel(self.legendFrame, text = "Relegation", font = (APP_FONT, 12), fg_color = GREY_BACKGROUND).grid(row = row, column = 1, sticky = "w", padx = (8, 0), pady = (0, 2))

class Profile(ctk.CTkFrame):
    def __init__(self, parent, league):
        """
        Class for displaying the league profile information.

        Args:
            parent (ctk.CTkFrame): The parent widget (LeagueProfile).
            league (League): The league object containing the profile information.  
        """
        
        super().__init__(parent, fg_color = TKINTER_BACKGROUND, width = 1000, height = 630, corner_radius = 0) 

        self.parent = parent
        self.league = league

        src = Image.open(io.BytesIO(self.league.logo))
        src.thumbnail((100, 100))
        self.logo = ctk.CTkImage(src, None, (src.width, src.height))
        ctk.CTkLabel(self, image = self.logo, text = "", fg_color = TKINTER_BACKGROUND).place(relx = 0.08, rely = 0.1, anchor = "center")

        ctk.CTkLabel(self, text = f"{self.league.name} - {self.league.year}", font = (APP_FONT_BOLD, 30), fg_color = TKINTER_BACKGROUND).place(relx = 0.15, rely = 0.1, anchor = "w")

        self.tableFrame = LeagueTable(self, 480, 600, 0.03, 0.2, GREY_BACKGROUND, "nw", corner_radius = 15, highlightManaged = True)

        if self.parent.manager_id:
            self.tableFrame.defineManager(self.parent.manager_id)
        else:
            # Use any manager from the league
            leagueTeam = LeagueTeams.get_teams_by_league(self.league.id)[0]
            leagueManager = Teams.get_manager_by_team(leagueTeam.team_id)
            self.tableFrame.defineManager(leagueManager, managingLeague = False)

        self.tableFrame.addLeagueTable()

        self.statsFrame = ctk.CTkFrame(self, fg_color = GREY_BACKGROUND, width = 310, height = 480, corner_radius = 15)
        self.statsFrame.place(relx = 0.64, rely = 0.2, anchor = "nw")
        self.pack_propagate(False)

        titleFrame = ctk.CTkFrame(self.statsFrame, fg_color = GREY_BACKGROUND, width = 310, height = 30, corner_radius = 15)
        titleFrame.pack(pady = 5, padx = 5)
        ctk.CTkLabel(titleFrame, text = "Player Stats", font = (APP_FONT_BOLD, 25), fg_color = GREY_BACKGROUND).place(relx = 0.5, rely = 0.55, anchor = "center")

        self.playerStatsFrame = ctk.CTkScrollableFrame(self.statsFrame, fg_color = GREY_BACKGROUND, width = 290, height = 400, corner_radius = 15)
        self.playerStatsFrame.pack(pady = 5, padx = 5)

        if self.parent.leagueAbove or self.parent.leagueBelow and League.get_league_state(self.league.league_below):
            self.upLeagueButton = ctk.CTkButton(self, width = 50, height = 50, text = "⯅", text_color = "white", font = (APP_FONT_BOLD, 30), fg_color = GREY_BACKGROUND, command = lambda: self.loadleague(self.league.league_above))
            self.upLeagueButton.place(relx = 0.963, rely = 0, anchor = "ne")

            self.downLeagueButton = ctk.CTkButton(self, width = 50, height = 50, text = "⯆", text_color = "white", font = (APP_FONT_BOLD, 30), fg_color = GREY_BACKGROUND, command = lambda: self.loadleague(self.league.league_below))
            self.downLeagueButton.place(relx = 0.963, rely = 0.09, anchor = "ne")

            if not self.parent.leagueAbove:
                self.upLeagueButton.configure(state = "disabled")

            if not self.parent.leagueBelow or not League.get_league_state(self.league.league_below):
                self.downLeagueButton.configure(state = "disabled")

        self.addStats()

    def loadleague(self, league_id):
        """
        Loads the league profile for the specified league ID.
        
        Args:
            league_id (str): The ID of the league to load the profile for.
        """
        
        profile = LeagueProfile(self.parent, league_id, getattr(self.parent, 'changeBackFunction', None), getattr(self.parent, 'userLeagueProfile', None))
        profile.place(relx = 0, rely = 0, anchor = "nw")
        append_overlapping_profile(self.parent, profile)

    def addStats(self):
        """
        Adds player statistics to the stats frame.
        """
        
        self.topScorers = MatchEvents.get_all_goals(self.league.id)
        self.topAssisters = MatchEvents.get_all_assists(self.league.id)
        self.topCleanSheets = MatchEvents.get_all_clean_sheets(self.league.id)
        self.mostYellowCards = MatchEvents.get_all_yellow_cards(self.league.id)
        self.bestAverageRatings = TeamLineup.get_all_average_ratings(self.league.id)
    
        self.stats = [self.topScorers, self.topAssisters, self.topCleanSheets, self.mostYellowCards, self.bestAverageRatings]
        self.statNames = ["Top Scorer", "Top Assister", "Most Clean Sheets", "Most Yellow Cards", "Best Average Rating"] + PLAYER_STATS

        for stat in PLAYER_STATS:
            self.stats.append(MatchStats.get_all_players_for_stat(self.league.id, stat))

        expandedImage = Image.open("Images/expand.png")
        expandedImage.thumbnail((30, 30))
        self.expandEnabled = ctk.CTkImage(expandedImage, None, (expandedImage.width, expandedImage.height))

        for stat, statName in zip(self.stats, self.statNames):

            frame = ctk.CTkFrame(self.playerStatsFrame, fg_color = GREY_BACKGROUND, width = 280, height = 75, corner_radius = 15)
            frame.pack(pady = 5, padx = 5)

            expandButton = ctk.CTkButton(frame, text = "", image = self.expandEnabled, fg_color = GREY_BACKGROUND, corner_radius = 0, height = 30, width = 30, hover_color = GREY_BACKGROUND)
            expandButton.place(relx = 0.98, rely = 0.7, anchor = "e")

            if not stat:
                stat = [(0, "N/A", "N/A", 0)]
                expandButton.configure(image = None, state = "disabled")
            else:
                stat = [entry for entry in stat if entry[3] > 0][:20]
                expandButton.configure(command = lambda stat = stat, statName = statName: self.expandStats(stat, statName)) 

            ctk.CTkLabel(frame, text = statName, font = (APP_FONT_BOLD, 25), fg_color = GREY_BACKGROUND).place(relx = 0.05, rely = 0.15, anchor = "w")

            if stat[0][0] == 0:
                ctk.CTkLabel(frame, text = "N/A", font = (APP_FONT, 20), fg_color = GREY_BACKGROUND).place(relx = 0.05, rely = 0.7, anchor = "w")
            else:
                player = Players.get_player_by_id(stat[0][0])
                PlayerProfileLink(frame, player, f"{stat[0][1]} {stat[0][2]}", "white", 0.05, 0.7, "w", GREY_BACKGROUND, self.parent)

            ctk.CTkLabel(frame, text = round(stat[0][3], 2), font = (APP_FONT, 20), fg_color = GREY_BACKGROUND).place(relx = 0.75, rely = 0.7, anchor = "center")

    def expandStats(self, stats, statName):
        """
        Expands the statistics view to show detailed player stats.
        
        Args:
            stats (list): List of player statistics to display.
            statName (str): The name of the statistic being displayed.
        """
        
        for frame in self.statsFrame.winfo_children(): 
            for widget in frame.winfo_children():
                if isinstance(widget, ctk.CTkButton):
                    widget.configure(state = "disabled")

        frame = ctk.CTkFrame(self, fg_color = GREY_BACKGROUND, width = 500, height = 320, corner_radius = 15, background_corner_colors = [GREY_BACKGROUND, GREY_BACKGROUND, GREY_BACKGROUND, GREY_BACKGROUND], border_width = 3, border_color = APP_BLUE)

        headerFrame = ctk.CTkFrame(frame, fg_color = GREY_BACKGROUND, width = 485, height = 50, corner_radius = 15)
        headerFrame.pack(pady = 10, padx = 5)

        ctk.CTkLabel(headerFrame, text = statName, font = (APP_FONT_BOLD, 25), fg_color = GREY_BACKGROUND).place(relx = 0.05, rely = 0.5, anchor = "w")

        backButton = ctk.CTkButton(headerFrame, text = "Back", font = (APP_FONT, 20), fg_color = GREY_BACKGROUND, hover_color = CLOSE_RED, corner_radius = 5, height = 20, width = 20, command = lambda: self.closeStats(frame))
        backButton.place(relx = 0.95, rely = 0.5, anchor = "e")
                         
        if len(stats) <= 5:
            statsFrame = ctk.CTkFrame(frame, fg_color = GREY_BACKGROUND, width = 475, height = 240, corner_radius = 15)
            statsFrame.pack(pady = 10, padx = 5)

            statsFrame.pack_propagate(False)
        else:
            statsFrame = ctk.CTkScrollableFrame(frame, fg_color = GREY_BACKGROUND, width = 475, height = 240, corner_radius = 15)
            statsFrame.pack(pady = 10, padx = 5)

        for stat in stats:
            player_id = stat[0]
            player_name = f"{stat[1]} {stat[2]}"
            stat_value = stat[3]

            player_frame = ctk.CTkFrame(statsFrame, fg_color = GREY_BACKGROUND, width = 450, height = 40)
            player_frame.pack(pady = 5, padx = 5)

            src = Image.open("Images/default_user.png")
            src.thumbnail((30, 30))
            img = ctk.CTkImage(src, None, (src.width, src.height))
            ctk.CTkLabel(player_frame, text = "", image = img, fg_color = GREY_BACKGROUND).place(relx = 0.05, rely = 0.5, anchor = "w")

            player = Players.get_player_by_id(player_id)
            PlayerProfileLink(player_frame, player, player_name, "white", 0.2, 0.5, "w", GREY_BACKGROUND, self.parent)

            ctk.CTkLabel(player_frame, text = round(stat_value, 2), font = (APP_FONT, 20), fg_color = GREY_BACKGROUND).place(relx = 0.9, rely = 0.5, anchor = "center")

        frame.place(relx = 0.5, rely = 0.5, anchor = "center")

    def closeStats(self, frame):
        """
        Closes the expanded statistics view.

        Args:
            frame (ctk.CTkFrame): The frame to close.  
        """
        
        frame.destroy()

        for frame in self.statsFrame.winfo_children():
            for widget in frame.winfo_children():
                if isinstance(widget, ctk.CTkButton):
                    widget.configure(state = "enabled")

class Matchdays(ctk.CTkFrame):
    def __init__(self, parent, league):
        """
        Class for displaying matchdays in the league profile.

        Args:
            parent (ctk.CTkFrame): The parent widget (LeagueProfile).
            league (League): The league object containing matchday information.  
        """
        
        super().__init__(parent, fg_color = TKINTER_BACKGROUND, width = 1000, height = 630, corner_radius = 0) 

        self.parent = parent
        self.league = league
        self.currentMatchday = self.league.current_matchday

        userTeam = Teams.get_teams_by_manager(Managers.get_all_user_managers()[0].id)[0]
        userLeague = LeagueTeams.get_league_by_team(userTeam.id)

        if userLeague.league_id == self.league.id:
            self.parentTab = self.parent
        else:
            self.parentTab = self.parent.parent

        self.frames = []
        self.activeFrame = self.currentMatchday - 1
        self.numMatchdays = 38 if not self.league.league_above else 39

        self.buttonsFrame = ctk.CTkFrame(self, fg_color = TKINTER_BACKGROUND, width = 980, height = 60, corner_radius = 15)
        self.buttonsFrame.place(relx = 0, rely = 0.98, anchor = "sw")

        self.createFrames()
        self.addButtons()

    def createFrames(self):
        """
        Creates frames for each matchday in the league.
        """
        
        for i in range(self.numMatchdays):
            if i == self.currentMatchday - 1:
                matchday = Matches.get_matchday_for_league(self.league.id, self.currentMatchday)
                frame = MatchdayFrame(self, matchday, self.currentMatchday, self.currentMatchday, self, self.parentTab, 980, 550, GREY_BACKGROUND, 0, 0, "nw")
            else:
                frame = None
            
            self.frames.append(frame)

    def addButtons(self):
        """
        Adds navigation buttons for matchdays.
        """
        
        self.back5Button = ctk.CTkButton(self.buttonsFrame, text = "<<", font = (APP_FONT, 20), fg_color = GREY_BACKGROUND, corner_radius = 10, height = 55, width = 90, hover_color = GREY_BACKGROUND, command = lambda: self.changeFrame(-5))
        self.back5Button.place(relx = 0.05, rely = 0.5, anchor = "center")

        self.back1Button = ctk.CTkButton(self.buttonsFrame, text = "<", font = (APP_FONT, 20), fg_color = GREY_BACKGROUND, corner_radius = 10, height = 55, width = 90, hover_color = GREY_BACKGROUND, command = lambda: self.changeFrame(-1))
        self.back1Button.place(relx = 0.15, rely = 0.5, anchor = "center")

        self.currentMatchdayButton = ctk.CTkButton(self.buttonsFrame, text = "Current Matchday", font = (APP_FONT, 20), fg_color = GREY_BACKGROUND, corner_radius = 10, height = 55, width = 580, hover_color = GREY_BACKGROUND, state = "disabled", command = self.goCurrentMatchday)
        self.currentMatchdayButton.place(relx = 0.5, rely = 0.5, anchor = "center")

        self.forward1Button = ctk.CTkButton(self.buttonsFrame, text = ">", font = (APP_FONT, 20), fg_color = GREY_BACKGROUND, corner_radius = 10, height = 55, width = 90, hover_color = GREY_BACKGROUND, command = lambda: self.changeFrame(1))
        self.forward1Button.place(relx = 0.85, rely = 0.5, anchor = "center")

        self.forward5Button = ctk.CTkButton(self.buttonsFrame, text = ">>", font = (APP_FONT, 20), fg_color = GREY_BACKGROUND, corner_radius = 10, height = 55, width = 90, hover_color = GREY_BACKGROUND, command = lambda: self.changeFrame(5))
        self.forward5Button.place(relx = 0.95, rely = 0.5, anchor = "center")

    def changeFrame(self, direction):
        """
        Changes the active matchday frame based on the direction.
        
        Args:
            direction (int): The direction to change the frame. Positive values move forward, negative values move backward.
        """
        
        self.frames[self.activeFrame].place_forget()

        if self.activeFrame + direction > self.numMatchdays - 1:
            self.activeFrame = (direction - (self.numMatchdays - self.activeFrame))
        elif self.activeFrame + direction < 0:
            self.activeFrame = self.numMatchdays - (abs(direction) - self.activeFrame)
        else:
            self.activeFrame += direction

        if self.activeFrame == self.currentMatchday - 1:
            self.currentMatchdayButton.configure(state = "disabled")
        else:
            self.currentMatchdayButton.configure(state = "normal")

        if self.frames[self.activeFrame]:
            self.frames[self.activeFrame].placeFrame()
        else:
            matchday = Matches.get_matchday_for_league(self.league.id, self.activeFrame + 1)
            self.frames[self.activeFrame] = MatchdayFrame(self, matchday, self.activeFrame + 1, self.currentMatchday, self, self.parent, 980, 550, GREY_BACKGROUND, 0, 0, "nw")

    def goCurrentMatchday(self):
        """
        Navigates to the current matchday frame.
        """
        
        self.frames[self.activeFrame].place_forget()

        self.frames[self.currentMatchday - 1].placeFrame()
        self.activeFrame = self.currentMatchday - 1

        self.currentMatchdayButton.configure(state = "disabled")

class Graphs(ctk.CTkFrame):
    def __init__(self, parent, league):
        """
        Class for displaying graphs in the league profile.
        
        Args:
            parent (ctk.CTkFrame): The parent widget (LeagueProfile).
            league (League): The league object containing graph information.
        """
        
        super().__init__(parent, fg_color = TKINTER_BACKGROUND, width = 1000, height = 630, corner_radius = 0) 

        self.parent = parent
        self.league = league
        self.leagueTeams = LeagueTeams.get_teams_by_position(self.league.id)
        self.numTeams = len(self.leagueTeams)

        self.columns = (self.numTeams * 2) - 3
        self.canvasWidth = 945
        self.canvasHeight = 680
        
        self.graph = "positions"

        self.tableFrame = ctk.CTkFrame(self, fg_color = TKINTER_BACKGROUND, width = 200, height = 620, corner_radius = 15)
        self.tableFrame.place(relx = 0, rely = 0, anchor = "nw")
        self.tableFrame.pack_propagate(False)
    
        self.addTeams()

        canvas = ctk.CTkCanvas(self, width = 5, height = 750, bg = GREY_BACKGROUND, bd = 0, highlightthickness = 0)
        canvas.place(relx = 0.2, rely = 0.48, anchor = "center")

        self.buttonsFrame = ctk.CTkFrame(self, fg_color = TKINTER_BACKGROUND, width = 760, height = 60, corner_radius = 15)
        self.buttonsFrame.place(relx = 0.98, rely = 0.98, anchor = "se")

        self.addButtons()

        self.positionsCanvas = ctk.CTkCanvas(self, width = self.canvasWidth, height = self.canvasHeight, bg = TKINTER_BACKGROUND, bd = 0, highlightthickness = 0)
        self.positionsCanvas.place(relx = 0.98, rely = 0, anchor = "ne")

        self.pointsCanvas = ctk.CTkCanvas(self, width = self.canvasWidth, height = self.canvasHeight, bg = TKINTER_BACKGROUND, bd = 0, highlightthickness = 0)

        self.drawGrid(self.positionsCanvas, self.numTeams - 1, "positions")
        self.drawGrid(self.pointsCanvas, max(15, self.leagueTeams[0].points), "points")  

        # Add the graphs
        for i, team in enumerate(self.leagueTeams):
            team = Teams.get_team_by_id(team.team_id)

            positions_result = TeamHistory.get_positions_by_team(team.id)
            if positions_result:
                positions = [pos[0] for pos in positions_result]  # Convert tuple to list
                self.createGraphs(positions, i, self.numTeams - 1, "positions", self.positionsCanvas)

            points_result = TeamHistory.get_points_by_team(team.id)
            if points_result:
                points = [poi[0] for poi in points_result]  # Convert tuple to list
                self.createGraphs(points, i, max(15, self.leagueTeams[0].points), "points", self.pointsCanvas)

    def addTeams(self):
        """
        Adds the teams to the league table frame (side of the graph).
        """

        for i, team in enumerate(self.leagueTeams):
            teamData = Teams.get_team_by_id(team.team_id)

            frame = ctk.CTkFrame(self.tableFrame, fg_color = TKINTER_BACKGROUND, width = 200, height = 21)
            frame.pack(fill = "both", pady = 5, padx = 5)

            src = Image.open(io.BytesIO(teamData.logo))
            src.thumbnail((20, 20))
            logo = ctk.CTkImage(src, None, (src.width, src.height))

            imageLabel = ctk.CTkLabel(frame, image = logo, text = "", fg_color = TKINTER_BACKGROUND)
            imageLabel.place(relx = 0.95, rely = 0.5, anchor = "e")
            nameLabel = ctk.CTkLabel(frame, text = teamData.name, font = (APP_FONT, 15), fg_color = TKINTER_BACKGROUND)
            nameLabel.place(relx = 0.8, rely = 0.5, anchor = "e")
            
            frame.bind("<Enter>", lambda event, f = frame, i = imageLabel, n = nameLabel: self.onFrameHover(event, f, i, n))
            frame.bind("<Leave>", lambda event, f = frame, i = imageLabel, n = nameLabel: self.onFrameLeave(event, f, i, n))
            imageLabel.bind("<Enter>", lambda event, f = frame, i = imageLabel, n = nameLabel: self.onFrameHover(event, f, i, n))
            imageLabel.bind("<Leave>", lambda event, f = frame, i = imageLabel, n = nameLabel: self.onFrameLeave(event, f, i, n))
            nameLabel.bind("<Enter>", lambda event, f = frame, i = imageLabel, n = nameLabel: self.onFrameHover(event, f, i, n))
            nameLabel.bind("<Leave>", lambda event, f = frame, i = imageLabel, n = nameLabel: self.onFrameLeave(event, f, i, n))

            frame.bind("<Button-1>", lambda event, team_id = teamData.id, i = i, f = frame, im = imageLabel, n = nameLabel: self.selectTeam(team_id, i, f, im, n))
            imageLabel.bind("<Button-1>", lambda event, team_id = teamData.id, i = i, f = frame, im = imageLabel, n = nameLabel: self.selectTeam(team_id, i, f, im, n))
            nameLabel.bind("<Button-1>", lambda event, team_id = teamData.id, i = i, f = frame, im = imageLabel, n = nameLabel: self.selectTeam(team_id, i, f, im, n))
            
    def onFrameHover(self, event, frame, img, name):
        """
        Changes the frame color on hover.
        
        Args:
            event: The event that triggered the function.
            frame (ctk.CTkFrame): The frame to change color.
            img (ctk.CTkLabel): The image label to change color.
            name (ctk.CTkLabel): The name label to change color.
        """

        frame.configure(fg_color = GREY_BACKGROUND)
        img.configure(fg_color = GREY_BACKGROUND)
        name.configure(fg_color = GREY_BACKGROUND)

    def onFrameLeave(self, event, frame, img, name):
        """
        Resets the frame color on hover leave.
        
        Args:
            event: The event that triggered the function.
            frame (ctk.CTkFrame): The frame to reset color.
            img (ctk.CTkLabel): The image label to reset color.
            name (ctk.CTkLabel): The name label to reset color.
        """

        frame.configure(fg_color = TKINTER_BACKGROUND)
        img.configure(fg_color = TKINTER_BACKGROUND)
        name.configure(fg_color = TKINTER_BACKGROUND)

    def createGraphs(self, positions, index, rows, graph, canvas, first = True, delete = False):
        """
        Creates the graphs on the canvas.
        
        Args:
            positions (list): List of positions or points for the team.
            index (int): The index of the team.
            rows (int): The number of rows in the graph.
            graph (str): The type of graph ("positions" or "points").
            canvas (ctk.CTkCanvas): The canvas to draw the graph on.
            first (bool): Whether this is the first time drawing the graph.
            delete (bool): Whether to delete the graph.
        """

        canvas = self.positionsCanvas if graph == "positions" else self.pointsCanvas

        if delete:
            canvas.delete("non_image")
        elif not first and not delete:
            canvas.delete("line" + str(index))
            return

        # Calculate the size of each cell
        cellWidth = (self.canvasWidth - 50) / self.columns
        cellHeight = (self.canvasHeight - 40) / rows

        # Store the coordinates of each point
        points = []

        # Draw a point on each row
        for i, position in enumerate(positions):
            x = 20 + i * cellWidth  # Place the point on the grid line

            if graph == "positions":
                y = 20 + (int(position) - 1) * cellHeight  # Place the point on the grid line
            else:
                y = 20 + (rows - int(position)) * cellHeight

            # Add the coordinates of the point to the list
            points.append(x)
            points.append(y)

        if len(points) >= 4:
            # Draw a line connecting all points with a wider line
            if not delete and first:
                canvas.create_line(*points, fill = TABLE_COLOURS[index], width = 2, tags = "non_image")
            elif not first and delete:
                canvas.create_line(*points, fill = TABLE_COLOURS[index], width = 2, tags = "line" + str(index))
        else:
            if not delete and first:
                canvas.create_oval(points[0] - 2, points[1] - 2, points[0] + 2, points[1] + 2, fill=TABLE_COLOURS[index], tags="non_image")
            elif not first and delete:
                canvas.create_oval(points[0] - 2, points[1] - 2, points[0] + 2, points[1] + 2, fill=TABLE_COLOURS[index], tags="line" + str(index))

    def drawGrid(self, canvas, rows, graph):
        """
        Draws the grid on the canvas.
        
        Args:
            canvas (ctk.CTkCanvas): The canvas to draw the grid on.
            rows (int): The number of rows in the grid.
            graph (str): The type of graph ("positions" or "points").
        """
        
        # Calculate the size of each cell
        cellWidth = (self.canvasWidth - 50) / self.columns  # Subtract 50 to add a space of 20 pixels on the left and 30 on the right
        cellHeight = (self.canvasHeight - 40) / rows  # Subtract 40 to add a space of 20 pixels on the top and bottom

        # Draw vertical lines
        for i in range(self.columns):
            x = i * cellWidth + 20  # Add 20 to move the grid 20 pixels to the right
            if i == 0:
                canvas.create_line(x, 20, x, self.canvasHeight - 20, fill = "white")  # Solid white line for the leftmost vertical line
            else:
                canvas.create_line(x, 20, x, self.canvasHeight - 20, fill = GREY_BACKGROUND, dash = (4, 2))  # Dashed line for other vertical lines

            # Add matchDays at the bottom of each column
            if i == 0 or (i + 1) % 5 == 0:
                canvas.create_text(x, self.canvasHeight - 12, text = str(i + 1), anchor = "n", fill = "white")  # Subtract 10 to move the text up 10 pixels at the bottom

        # Draw the last vertical line
        canvas.create_line(self.canvasWidth - 30, 20, self.canvasWidth - 30, self.canvasHeight - 20, fill = GREY_BACKGROUND, dash = (4, 2))  # Dashed line for the last vertical line

        # Add the last matchDay at the bottom
        canvas.create_text(self.canvasWidth - 30, self.canvasHeight - 12, text = str(self.columns + 1), anchor = "n", fill = "white")  # Subtract 30 to move the text 30 pixels to the left and subtract 10 to move it up 10 pixels at the bottom

        # Draw horizontal lines
        for i in range(rows):
            y = i * cellHeight + 20  # Add 20 to move the lines down 20 pixels
            if i == rows:
                canvas.create_line(20, y, self.canvasWidth - 30, y, fill = "white")  # Solid white line for the bottom horizontal line
            else:
                canvas.create_line(25, y, self.canvasWidth - 30, y, fill = GREY_BACKGROUND, dash = (4, 2))  # Dashed line for other horizontal lines

            # Add row number at the top of the row
            if graph == "positions":
                canvas.create_text(10, y - 8, text = str(i + 1), anchor = "n", fill = "white")  # Move the text 10 pixels to the left
            else:
                if i == 0 or (rows - i) % 5 == 0:
                    canvas.create_text(10, y - 8, text = str(rows - i), anchor = "n", fill = "white")

        # Draw the last horizontal line
        canvas.create_line(20, self.canvasHeight - 20, self.canvasWidth - 30, self.canvasHeight - 20, fill = "white")  # Solid white line for the bottom horizontal line

        # Add the last row number
        if graph == "positions":
            canvas.create_text(10, self.canvasHeight - 28, text = self.numTeams, anchor = "n", fill = "white")  # Move the text 10 pixels to the left and subtract 20 to move it up 20 pixels at the bottom
        else:
            canvas.create_text(10, self.canvasHeight - 28, text = "0", anchor = "n", fill = "white")

    def addButtons(self):
        """
        Adds buttons to switch between graphs and reset the graph.
        """
        
        self.positionsButton = ctk.CTkButton(self.buttonsFrame, text = "Positions", font = (APP_FONT, 20), fg_color = GREY_BACKGROUND, corner_radius = 10, height = 55, width = 300, hover_color = GREY_BACKGROUND, state = "disabled", command = lambda: self.changeGraph("positions"))
        self.positionsButton.place(relx = 0.2, rely = 0.5, anchor = "center")

        self.pointsButton = ctk.CTkButton(self.buttonsFrame, text = "Points", font = (APP_FONT, 20), fg_color = GREY_BACKGROUND, corner_radius = 10, height = 55, width = 300, hover_color = GREY_BACKGROUND, command = lambda: self.changeGraph("points"))
        self.pointsButton.place(relx = 0.6, rely = 0.5, anchor = "center")

        self.resetButton = ctk.CTkButton(self.buttonsFrame, text = "Reset", font = (APP_FONT, 20), fg_color = GREY_BACKGROUND, corner_radius = 10, height = 55, width = 150, hover_color = GREY_BACKGROUND, state = "disabled", command = self.resetGraph)
        self.resetButton.place(relx = 0.9, rely = 0.5, anchor = "center")

    def changeGraph(self, graph):
        """
        Changes the graph type between positions and points.
        
        Args:
            graph (str): The type of graph to display ("positions" or "points").
        """
        
        self.resetGraph()
        if graph == "points":
            self.graph = "points"
            self.positionsCanvas.place_forget()
            self.pointsCanvas.place(relx = 0.98, rely = 0, anchor = "ne")
            self.positionsButton.configure(state = "normal")
            self.pointsButton.configure(state = "disabled")

        else:
            self.graph = "positions"
            self.pointsCanvas.place_forget()
            self.positionsCanvas.place(relx = 0.98, rely = 0, anchor = "ne")
            self.positionsButton.configure(state = "disabled")
            self.pointsButton.configure(state = "normal")

    def resetGraph(self):
        """
        Resets the graph to show all teams.
        """
        
        if self.graph == "positions":
            self.positionsCanvas.delete("all")

            self.drawGrid(self.positionsCanvas, self.numTeams - 1, "positions")

            for i, team in enumerate(self.leagueTeams):
                team = Teams.get_team_by_id(team.team_id)

                positions_result = TeamHistory.get_positions_by_team(team.id)
                if positions_result:
                    positions = [pos[0] for pos in positions_result]  # Convert tuple to list
                    self.createGraphs(positions, i, self.numTeams - 1, "positions", self.positionsCanvas)

        else:
            self.pointsCanvas.delete("all")

            self.drawGrid(self.pointsCanvas, max(15, self.leagueTeams[0].points), "points")

            for i, team in enumerate(self.leagueTeams):
                team = Teams.get_team_by_id(team.team_id)

                points_result = TeamHistory.get_points_by_team(team.id)
                if points_result:
                    points = [poi[0] for poi in points_result]  # Convert tuple to list
                    self.createGraphs(points, i, max(15, self.leagueTeams[0].points), "points", self.pointsCanvas)

        self.resetButton.configure(state = "disabled")

        for i, widget in enumerate(self.tableFrame.winfo_children()):
            img = widget.winfo_children()[0]
            name = widget.winfo_children()[1]

            team = Teams.get_team_by_name(name.cget("text"))

            widget.unbind("<Button-1>")
            img.unbind("<Button-1>")
            name.unbind("<Button-1>")

            widget.bind("<Button-1>", lambda event, team_id = team.id, i = i, f = widget, im = img, n = name: self.selectTeam(team_id, i, f, im, n))
            img.bind("<Button-1>", lambda event, team_id = team.id, i = i, f = widget, im = img, n = name: self.selectTeam(team_id, i, f, im, n))
            name.bind("<Button-1>", lambda event, team_id = team.id, i = i, f = widget, im = img, n = name: self.selectTeam(team_id, i, f, im, n))

    def selectTeam(self, team_id, index, frame, img, name):
        """
        Highlights the selected team's graph.
        
        Args:
            team_id (str): The ID of the selected team.
            index (int): The index of the selected team.
            frame (ctk.CTkFrame): The frame of the selected team.
            img (ctk.CTkLabel): The image label of the selected team.
            name (ctk.CTkLabel): The name label of the selected team.
        """
        
        if self.graph == "positions":
            positions_result = TeamHistory.get_positions_by_team(team_id)
            if positions_result:
                positions = [pos[0] for pos in positions_result]
                self.createGraphs(positions, index, self.numTeams - 1, "positions", self.positionsCanvas, False, True)
        else:
            points_result = TeamHistory.get_points_by_team(team_id)
            if points_result:
                points = [poi[0] for poi in points_result]
                self.createGraphs(points, index, max(15, self.leagueTeams[0].points), "points", self.pointsCanvas, False, True)

        self.resetButton.configure(state = "normal")

        frame.unbind("<Button-1>")
        img.unbind("<Button-1>")
        name.unbind("<Button-1>")
        frame.bind("<Button-1>", lambda event, team_id = team_id, i = index, f = frame, im = img, n = name: self.deselectTeam(team_id, i, f, im, n))
        img.bind("<Button-1>", lambda event, team_id = team_id, i = index, f = frame, im = img, n = name: self.deselectTeam(team_id, i, f, im, n))
        name.bind("<Button-1>", lambda event, team_id = team_id, i = index, f = frame, im = img, n = name: self.deselectTeam(team_id, i, f, im, n))

    def deselectTeam(self, team_id, index, frame, img, name):
        """
        Removes the highlight from the selected team's graph.
        
        Args:
            team_id (str): The ID of the selected team.
            index (int): The index of the selected team.
            frame (ctk.CTkFrame): The frame of the selected team.
            img (ctk.CTkLabel): The image label of the selected team.
            name (ctk.CTkLabel): The name label of the selected team.
        """
        
        if self.graph == "positions":
            positions_result = TeamHistory.get_positions_by_team(team_id)
            if positions_result:
                positions = [pos[0] for pos in positions_result]
                self.createGraphs(positions, index, self.numTeams - 1, "positions", self.positionsCanvas, False, False)
        else:
            points_result = TeamHistory.get_points_by_team(team_id)
            if points_result:
                points = [poi[0] for poi in pointsResult]
                self.createGraphs(points, index, max(15, self.leagueTeams[0].points), "points", self.pointsCanvas, False, False)

        self.resetButton.configure(state = "disabled")

        frame.unbind("<Button-1>")
        img.unbind("<Button-1>")
        name.unbind("<Button-1>")
        frame.bind("<Button-1>", lambda event, team_id = team_id, i = index, f = frame, im = img, n = name: self.selectTeam(team_id, i, f, im, n))
        img.bind("<Button-1>", lambda event, team_id = team_id, i = index, f = frame, im = img, n = name: self.selectTeam(team_id, i, f, im, n))
        name.bind("<Button-1>", lambda event, team_id = team_id, i = index, f = frame, im = img, n = name: self.selectTeam(team_id, i, f, im, n))

class Stats(ctk.CTkFrame):
    def __init__(self, parent, league):
        """
        Class for displaying statistics in the league profile.
        
        Args:
            parent (ctk.CTkFrame): The parent widget (LeagueProfile).
            league (League): The league object containing statistics information.
        """
        
        super().__init__(parent, fg_color = TKINTER_BACKGROUND, width = 1000, height = 630, corner_radius = 0) 

        self.parent = parent
        self.league = league
        self.managedTeam = Teams.get_teams_by_manager(self.parent.manager_id)[0] if self.parent.manager_id else None
        self.leagueTeams = LeagueTeams.get_teams_by_league(self.league.id)

        self.statsFrames = [None] * (len(STAT_FUNCTIONS) + len(self.leagueTeams))

        self.currentStat = None
        self.currentFrame = None

        self.statsFrame = ctk.CTkScrollableFrame(self, fg_color = GREY_BACKGROUND, width = 200, height = 590, corner_radius = 15)
        self.statsFrame.place(relx = 0, rely = 0, anchor = "nw")

        self.leagueTeams = LeagueTeams.get_teams_by_league(self.league.id)

        for cat in TEAM_STATS:
            ctk.CTkLabel(self.statsFrame, text = cat[0], font = (APP_FONT_BOLD, 20), fg_color = GREY_BACKGROUND, height = 10).pack(pady = 5)
            canvas = ctk.CTkCanvas(self.statsFrame, width = 200, height = 5, bg = APP_BLUE, bd = 0, highlightthickness = 0)
            canvas.pack(pady = 5)

            for stat in cat[1:]:
                fontSize = 15 if len(stat) < 25 else 14
                button = ctk.CTkButton(self.statsFrame, text = stat, font = (APP_FONT, fontSize), fg_color = GREY_BACKGROUND, border_color = APP_BLUE, border_width = 0, corner_radius = 5, height = 30, width = 300, hover_color = DARK_GREY, anchor = "w")
                button.pack(pady = 5)
                button.configure(command = lambda statName = stat, b = button: self.getStat(statName, b))

        ctk.CTkLabel(self.statsFrame, text = "Teams", font = (APP_FONT_BOLD, 20), fg_color = GREY_BACKGROUND, height = 10).pack(pady = 5)
        canvas = ctk.CTkCanvas(self.statsFrame, width = 200, height = 5, bg = APP_BLUE, bd = 0, highlightthickness = 0)
        canvas.pack(pady = 5)

        for team in self.leagueTeams:
            teamData = Teams.get_team_by_id(team.team_id)
            fontSize = 15 if len(teamData.name) < 25 else 14

            frame = ctk.CTkFrame(self.statsFrame, fg_color = GREY_BACKGROUND, width = 300, height = 30, border_color = APP_BLUE, border_width = 0, cursor = "hand2")

            src = Image.open(io.BytesIO(teamData.logo))
            src.thumbnail((20, 20))
            img = ctk.CTkImage(src, None, (src.width, src.height))
            imgLabel = ctk.CTkLabel(frame, text = "", image = img, fg_color = GREY_BACKGROUND, cursor = "hand2")
            imgLabel.place(relx = 0.05, rely = 0.5, anchor = "w")
            textLabel = ctk.CTkLabel(frame, text = teamData.name, font = (APP_FONT, fontSize), fg_color = GREY_BACKGROUND, cursor = "hand2")
            textLabel.place(relx = 0.2, rely = 0.5, anchor = "w")

            frame.bind("<Enter>", lambda e, f = frame, i = imgLabel, t = textLabel: self.onFrameHover(e, f, i, t))
            frame.bind("<Leave>", lambda e, f = frame, i = imgLabel, t = textLabel: self.onFrameLeave(e, f, i, t))
            frame.bind("<Button-1>", lambda event, teamData = teamData, f = frame: self.getTeamStats(teamData, f))

            imgLabel.bind("<Enter>", lambda e, f = frame, i = imgLabel, t = textLabel: self.onFrameHover(e, f, i, t))
            imgLabel.bind("<Button-1>", lambda event, teamData = teamData, f = frame: self.getTeamStats(teamData, f))
            textLabel.bind("<Enter>", lambda e, f = frame, i = imgLabel, t = textLabel: self.onFrameHover(e, f, i, t))
            textLabel.bind("<Button-1>", lambda event, teamData = teamData, f = frame: self.getTeamStats(teamData, f))

            frame.pack(pady = 5)

    def onFrameHover(self, event, frame, img, name):
        """
        Changes the frame color on hover.
        
        Args:
            event: The event that triggered the function.
            frame (ctk.CTkFrame): The frame to change color.
            img (ctk.CTkLabel): The image label to change color.
            name (ctk.CTkLabel): The name label to change color.
        """
        
        frame.configure(fg_color = DARK_GREY)
        img.configure(fg_color = DARK_GREY)
        name.configure(fg_color = DARK_GREY)

    def onFrameLeave(self, event, frame, img, name):
        """
        Resets the frame color on hover leave.
        
        Args:
            event: The event that triggered the function.
            frame (ctk.CTkFrame): The frame to reset color.
            img (ctk.CTkLabel): The image label to reset color.
            name (ctk.CTkLabel): The name label to reset color.
        """
        
        frame.configure(fg_color = GREY_BACKGROUND)
        img.configure(fg_color = GREY_BACKGROUND)
        name.configure(fg_color = GREY_BACKGROUND)
    
    def getTeamStats(self, teamData, frame):
        """
        Displays the statistics for a specific team.
        
        Args:
            teamData (Team): The team object containing statistics information.
            frame (ctk.CTkFrame): The frame of the selected team.
        """
        
        if self.currentStat == teamData.name:
            return

        if self.currentFrame:
            self.currentFrame.place_forget()

        for widget in self.statsFrame.winfo_children():
            if isinstance(widget, ctk.CTkButton) or isinstance(widget, ctk.CTkFrame):
                widget.configure(border_width = 0)

        for i, team in enumerate(self.leagueTeams):
            if teamData.id == team.team_id:
                team_index = i
                break

        stat_index = len(STAT_FUNCTIONS) + team_index
        if self.statsFrames[stat_index]:
            # If the frame already exists, just show it
            self.statsFrames[stat_index].place(relx = 0.98, rely = 0, anchor = "ne")
            self.currentFrame = self.statsFrames[stat_index]
            self.currentStat = teamData.name

            frame.configure(border_width = 1)
        else:
            # Otherwise, create the frame and populate it with data
            statsFrame = ctk.CTkScrollableFrame(self, fg_color = GREY_BACKGROUND, width = 700, height = 590, corner_radius = 15)
            statsFrame.place(relx = 0.98, rely = 0, anchor = "ne")

            self.statsFrames[stat_index] = statsFrame
            self.currentFrame = self.statsFrames[stat_index]
            self.currentStat = teamData.name

            frame.configure(border_width = 1)

            stats = StatsManager.get_team_stats(teamData.id, self.league.id, self.leagueTeams, STAT_FUNCTIONS)

            frame = ctk.CTkFrame(statsFrame, fg_color = GREY_BACKGROUND, width = 690, height = 40)
            frame.pack(pady = 5)

            ctk.CTkLabel(frame, text = "Statistic", font = (APP_FONT_BOLD, 20), fg_color = GREY_BACKGROUND).place(relx = 0.05, rely = 0.5, anchor = "w")
            ctk.CTkLabel(frame, text = "Value", font = (APP_FONT_BOLD, 20), fg_color = GREY_BACKGROUND).place(relx = 0.8, rely = 0.5, anchor = "center")
            ctk.CTkLabel(frame, text = "Rank", font = (APP_FONT_BOLD, 20), fg_color = GREY_BACKGROUND).place(relx = 0.9, rely = 0.5, anchor = "center")

            for stat in stats:
                frame = ctk.CTkFrame(statsFrame, fg_color = GREY_BACKGROUND, width = 690, height = 40)
                frame.pack(pady = 5)

                ctk.CTkLabel(frame, text = stat[0], font = (APP_FONT, 20), fg_color = GREY_BACKGROUND).place(relx = 0.05, rely = 0.5, anchor = "w")
                ctk.CTkLabel(frame, text = stat[1], font = (APP_FONT, 20), fg_color = GREY_BACKGROUND).place(relx = 0.8, rely = 0.5, anchor = "center")
                ctk.CTkLabel(frame, text = stat[2], font = (APP_FONT, 20), fg_color = GREY_BACKGROUND).place(relx = 0.9, rely = 0.5, anchor = "center")

    def getStat(self, statName, button):
        """
        Displays the statistics for a specific statistic category.
        
        Args:
            statName (str): The name of the statistic category. 
            button (ctk.CTkButton): The button that was clicked to select the statistic category.
        """

        if self.currentStat == statName:
            return

        if self.currentFrame:
            self.currentFrame.place_forget()

        for widget in self.statsFrame.winfo_children():
            if isinstance(widget, ctk.CTkButton) or isinstance(widget, ctk.CTkFrame):
                widget.configure(border_width = 0)
        
        stat_index = list(STAT_FUNCTIONS.keys()).index(statName)
        if self.statsFrames[stat_index]:
            # If the frame already exists, just show it
            self.statsFrames[stat_index].place(relx = 0.98, rely = 0, anchor = "ne")
            self.currentFrame = self.statsFrames[stat_index]
            self.currentStat = statName

            button.configure(border_width = 1)

        else:
            # Otherwise, create the frame and populate it with data
            statsFrame = ctk.CTkScrollableFrame(self, fg_color = GREY_BACKGROUND, width = 700, height = 590, corner_radius = 15)
            statsFrame.place(relx = 0.98, rely = 0, anchor = "ne")

            self.statsFrames[stat_index] = statsFrame
            self.currentFrame = self.statsFrames[stat_index]
            self.currentStat = statName

            button.configure(border_width = 1)

            stats = STAT_FUNCTIONS[statName](self.leagueTeams, self.league.id)
            
            for i, statsData in enumerate(stats):
                frame = ctk.CTkFrame(statsFrame, fg_color = GREY_BACKGROUND, width = 690, height = 40)
                frame.pack(pady = 5)

                team = Teams.get_team_by_id(statsData[0])

                src = Image.open(io.BytesIO(team.logo))
                src.thumbnail((30, 30))
                TeamLogo(frame, src, team, GREY_BACKGROUND, 0.15, 0.5, "center", self.parent)

                if self.managedTeam and self.managedTeam.name == team.name:
                    font = (APP_FONT_BOLD, 20)
                else:
                    font = (APP_FONT, 20)

                ctk.CTkLabel(frame, text = f"{i + 1}.", font = font, fg_color = GREY_BACKGROUND).place(relx = 0.05, rely = 0.5, anchor = "w")

                ctk.CTkLabel(frame, text = team.name, font = font, fg_color = GREY_BACKGROUND).place(relx = 0.2, rely = 0.5, anchor = "w")

                ctk.CTkLabel(frame, text = statsData[1], font = font, fg_color = GREY_BACKGROUND).place(relx = 0.9, rely = 0.5, anchor = "center")

class History(ctk.CTkScrollableFrame):
    def __init__(self, parent, league):
        """
        Class for displaying league history in the league profile.

        Args:
            parent (ctk.CTk): The parent widget (leagueProfile).
            league (League): The league object containing history information.
        """
        
        super().__init__(parent, fg_color = TKINTER_BACKGROUND, width = 965, height = 630, corner_radius = 0) 

        self.parent = parent
        self.league = league

class News(ctk.CTkFrame):
    def __init__(self, parent, league):
        """
        Class for displaying league news in the league profile.

        Args:
            parent (ctk.CTk): The parent widget (leagueProfile).
            league (League): The league object containing news information.
        """
        
        super().__init__(parent, fg_color = TKINTER_BACKGROUND, width = 1000, height = 630, corner_radius = 0)  

        self.parent = parent
        self.league = league

        self.mainNewsFrame = ctk.CTkFrame(self, fg_color = TKINTER_BACKGROUND, width = 620, height = 613)
        self.mainNewsFrame.place(relx = 0, rely = 0, anchor = "nw")

        self.injuriesFrame = ctk.CTkFrame(self, fg_color = GREY_BACKGROUND, width = 350, height = 140, corner_radius = 15)
        self.injuriesFrame.place(relx = 0.98, rely = 0, anchor = "ne")

        self.suspensionsFrame = ctk.CTkFrame(self, fg_color = GREY_BACKGROUND, width = 350, height = 140, corner_radius = 15)
        self.suspensionsFrame.place(relx = 0.98, rely = 0.25, anchor = "ne")

        self.transfersFrame = ctk.CTkFrame(self, fg_color = GREY_BACKGROUND, width = 350, height = 140, corner_radius = 15)
        self.transfersFrame.place(relx = 0.98, rely = 0.5, anchor = "ne")  

        self.teamOTWFrame = ctk.CTkFrame(self, fg_color = GREY_BACKGROUND, width = 350, height = 140, corner_radius = 15)
        self.teamOTWFrame.place(relx = 0.98, rely = 0.75, anchor = "ne")

        self.mainNews()
        self.injuries()
        self.suspensions()
        self.transfers()
        self.team_of_the_week() 

    def mainNews(self):
        """
        Populates the main news frame with league news.
        """

        src = Image.open("Images/news_backdrop.png")
        src = src.resize((620, 613))

        # Add transparency (alpha) directly to src
        if src.mode != "RGBA":
            src = src.convert("RGBA")
        alpha = src.split()[-1]
        alpha = alpha.point(lambda p: int(p * 0.6))  # 0.45 = 45% opacity
        src.putalpha(alpha)

        rounded = Image.new("RGBA", src.size, TKINTER_BACKGROUND)  # fill the new image with a background color
        mask = Image.new("L", src.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle((0, 0, src.width, src.height), 25, fill = 255)

        # Paste transparent src where the mask allows it
        rounded.paste(src, (0, 0), mask)

        img = ctk.CTkImage(rounded, None, (src.width, src.height))
        ctk.CTkLabel(self.mainNewsFrame, image = img, text = "", fg_color = GREY_BACKGROUND).place(relx = 0.5, rely = 0.5, anchor = "center")

    def injuries(self):
        """
        Populates the injuries frame with injury news.
        """

        src = Image.open("Images/injury.png")
        src.thumbnail((25, 25))
        img = ctk.CTkImage(src, None, (src.width, src.height))
        ctk.CTkLabel(self.injuriesFrame, image = img, text = "", fg_color = GREY_BACKGROUND).place(relx = 0.05, rely = 0.2, anchor = "w")
        ctk.CTkLabel(self.injuriesFrame, text = "Injuries", text_color = "white", font = (APP_FONT_BOLD, 22)).place(relx = 0.15, rely = 0.2, anchor = "w")

        ctk.CTkLabel(self.injuriesFrame, text = "Find out which players are currently injured in the league.", font = (APP_FONT, 14), wraplength = 300, text_color = ("gray80", "gray70")).place(relx = 0.5, rely = 0.6, anchor = "center")

        src = Image.open("Images/expand.png")
        src = src.resize((25, 25))
        img = ctk.CTkImage(src, None, (src.width, src.height))
        ctk.CTkLabel(self.injuriesFrame, image = img, text = "", fg_color = GREY_BACKGROUND).place(relx = 0.95, rely = 0.9, anchor = "se")

    def suspensions(self):
        """
        Populates the suspensions frame with suspension news.
        """

        src = Image.open("Images/redCard.png")
        src.thumbnail((25, 25))
        img = ctk.CTkImage(src, None, (src.width, src.height))
        ctk.CTkLabel(self.suspensionsFrame, image = img, text = "", fg_color = GREY_BACKGROUND).place(relx = 0.05, rely = 0.2, anchor = "w")
        ctk.CTkLabel(self.suspensionsFrame, text = "Suspensions", text_color = "white", font = (APP_FONT_BOLD, 22)).place(relx = 0.15, rely = 0.2, anchor = "w")

        ctk.CTkLabel(self.suspensionsFrame, text = "Discover which players are currently suspended in the league.", font = (APP_FONT, 14), wraplength = 300, text_color = ("gray80", "gray70")).place(relx = 0.5, rely = 0.6, anchor = "center")

        src = Image.open("Images/expand.png")
        src = src.resize((25, 25))
        img = ctk.CTkImage(src, None, (src.width, src.height))
        ctk.CTkLabel(self.suspensionsFrame, image = img, text = "", fg_color = GREY_BACKGROUND).place(relx = 0.95, rely = 0.9, anchor = "se")

    def transfers(self):
        """
        Populates the transfers frame with transfer news.
        """

        src = Image.open("Images/contract.png")
        src.thumbnail((25, 25))
        img = ctk.CTkImage(src, None, (src.width, src.height))
        ctk.CTkLabel(self.transfersFrame, image = img, text = "", fg_color = GREY_BACKGROUND).place(relx = 0.05, rely = 0.2, anchor = "w")
        ctk.CTkLabel(self.transfersFrame, text = "Transfers", text_color = "white", font = (APP_FONT_BOLD, 22)).place(relx = 0.15, rely = 0.2, anchor = "w")

        ctk.CTkLabel(self.transfersFrame, text = "Find out about the latest transfers in the league.", font = (APP_FONT, 14), wraplength = 300, text_color = ("gray80", "gray70")).place(relx = 0.5, rely = 0.6, anchor = "center")

        src = Image.open("Images/expand.png")
        src = src.resize((25, 25))
        img = ctk.CTkImage(src, None, (src.width, src.height))
        ctk.CTkLabel(self.transfersFrame, image = img, text = "", fg_color = GREY_BACKGROUND).place(relx = 0.95, rely = 0.9, anchor = "se")

    def team_of_the_week(self):
        """
        Populates the team of the week frame with team news.
        """

        src = Image.open("Images/pitch.png")
        src.thumbnail((25, 25))
        img = ctk.CTkImage(src, None, (src.width, src.height))
        ctk.CTkLabel(self.teamOTWFrame, image = img, text = "", fg_color = GREY_BACKGROUND).place(relx = 0.05, rely = 0.2, anchor = "w")
        ctk.CTkLabel(self.teamOTWFrame, text = "Team of the Week", text_color = "white", font = (APP_FONT_BOLD, 22)).place(relx = 0.15, rely = 0.2, anchor = "w")

        ctk.CTkLabel(self.teamOTWFrame, text = "Discover all team of the weeks for the league up till the last matchday.", font = (APP_FONT, 14), wraplength = 300, text_color = ("gray80", "gray70")).place(relx = 0.5, rely = 0.6, anchor = "center")

        src = Image.open("Images/expand.png")
        src = src.resize((25, 25))
        img = ctk.CTkImage(src, None, (src.width, src.height))
        ctk.CTkLabel(self.teamOTWFrame, image = img, text = "", fg_color = GREY_BACKGROUND).place(relx = 0.95, rely = 0.9, anchor = "se")