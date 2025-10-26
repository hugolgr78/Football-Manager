import customtkinter as ctk
from settings import *
from data.database import *
from data.gamesDatabase import *
from utils.frames import MatchDayMatchFrame, FootballPitchMatchDay, FootballPitchLineup, LineupPlayerFrame, SubstitutePlayer, FormGraph, InGamePlayerFrame, InGameStatFrame
from utils.shouts import ShoutFrame
from utils.util_functions import *
import threading, time, logging, math, io
from PIL import Image, ImageTk

class MatchDay(ctk.CTkFrame):
    def __init__(self, parent, teamLineup, teamSubstitutes, team, players):
        """
        A tab to display the matchday view for a team.
        
        Args:
            parent (ctk.CTkFrame): The parent frame (main menu).
            teamLineup (dict): The lineup of the team (position: player_id).
            teamSubstitutes (list): The list of substitute player IDs.
            team (Team): The team object.
            players (list): The list of player objects for the team.
        """
        
        super().__init__(parent, width = APP_SIZE[0], height = APP_SIZE[1], fg_color = TKINTER_BACKGROUND)
        self.pack(fill = "both", expand = True)

        self.parent = parent
        self.teamLineup = teamLineup
        self.teamSubstitutes = teamSubstitutes
        self.startSubs = teamSubstitutes.copy()
        self.team = team
        self.players = players
        self.teamMatch = None
        self.home = True

        self.halfTime = False
        self.halfTimeEnded = False
        self.fullTime = False
        self.fullTimeEnded = False
        self.maxExtraTimeHalf = 0
        self.maxExtraTimeFull = 100

        self.speed = 1 / 120

        self.completedSubs = 0
        self.redCardPlayers = []

        self.lastShout = 0

        self.leagueTeams = LeagueTeams.get_league_by_team(self.team.id)
        self.league = League.get_league_by_id(self.leagueTeams.league_id)
        self.currentMatchDay = self.league.current_matchday
        self.matchDay = Matches.get_matchday_for_league(self.league.id, self.currentMatchDay)
        self.caStars = Players.get_players_star_ratings(self.players, self.league.id)

        self.teamMatchFrame = ctk.CTkFrame(self, width = APP_SIZE[0] - 300, height = APP_SIZE[1], fg_color = TKINTER_BACKGROUND)
        self.teamMatchFrame.place(relx = 0, rely = 0.5, anchor = "w")

        self.otherMatchesFrame = ctk.CTkFrame(self, width = 300, height = APP_SIZE[1] - 135, fg_color = TKINTER_BACKGROUND)
        self.otherMatchesFrame.place(relx = 1, rely = 0, anchor = "ne")

        self.timeFrame = ctk.CTkFrame(self, width = 300, height = 135, fg_color = TKINTER_BACKGROUND)
        self.timeFrame.place(relx = 1, rely = 1, anchor = "se")

        ctk.CTkCanvas(self, width = 5, height = 1000, bg = APP_BLUE, bd = 0, highlightthickness = 0).place(relx = 0.75, rely = 0, anchor = "n")
        ctk.CTkCanvas(self, width = 500, height = 5, bg = APP_BLUE, bd = 0, highlightthickness = 0).place(relx = 0.75, rely = 0.81, anchor = "w")

        self.addMatches()
        self.addTime()

        self.homeLineupPitch = FootballPitchMatchDay(self.teamMatchFrame, 270, 570, 0.02, 0.06, "nw", TKINTER_BACKGROUND, GREY_BACKGROUND)
        self.awayLineupPitch = FootballPitchMatchDay(self.teamMatchFrame, 270, 570, 0.98, 0.06, "ne", TKINTER_BACKGROUND, GREY_BACKGROUND)

        self.homeCurrFrame = self.homeLineupPitch
        self.awayCurrFrame = self.awayLineupPitch

        self.homeDropDown = ctk.CTkComboBox(
            self.teamMatchFrame,
            font = (APP_FONT, 15),
            fg_color = DARK_GREY,
            border_color = DARK_GREY,
            button_color = DARK_GREY,
            button_hover_color = DARK_GREY,
            corner_radius = 10,
            dropdown_fg_color = DARK_GREY,
            dropdown_hover_color = DARK_GREY,
            width = 220,
            height = 30,
            state = "readonly",
            command = lambda selection: self.changeData("home", selection),
            values = ["Lineup", "Players", "Stats"]
        )
        self.homeDropDown.place(relx = 0.02, rely = 0.01, anchor = "nw")
        self.homeDropDown.set("Lineup")

        self.homePlayersFrame = ctk.CTkFrame(self.teamMatchFrame, width = 220, height = 460, fg_color = GREY_BACKGROUND)
        self.homePlayersFrame.pack_propagate(False)
        self.homeStatsFrame = ctk.CTkFrame(self.teamMatchFrame, width = 220, height = 460, fg_color = GREY_BACKGROUND)
        self.homeStatsFrame.pack_propagate(False)

        self.awayDropDown = ctk.CTkComboBox(
            self.teamMatchFrame,
            font = (APP_FONT, 15),
            fg_color = DARK_GREY,
            border_color = DARK_GREY,
            button_color = DARK_GREY,
            button_hover_color = DARK_GREY,
            corner_radius = 10,
            dropdown_fg_color = DARK_GREY,
            dropdown_hover_color = DARK_GREY,
            width = 220,
            height = 30,
            state = "readonly",
            command = lambda selection: self.changeData("away", selection),
            values = ["Lineup", "Players", "Stats"]
        )
        self.awayDropDown.place(relx = 0.98, rely = 0.01, anchor = "ne")
        self.awayDropDown.set("Lineup")

        self.awayPlayersFrame = ctk.CTkFrame(self.teamMatchFrame, width = 220, height = 460, fg_color = GREY_BACKGROUND)
        self.awayPlayersFrame.pack_propagate(False)
        self.awayStatsFrame = ctk.CTkFrame(self.teamMatchFrame, width = 220, height = 460, fg_color = GREY_BACKGROUND)
        self.awayStatsFrame.pack_propagate(False)

        self.homeSubstituteFrame = ctk.CTkFrame(self.teamMatchFrame, width = 220, height = 180, fg_color = GREY_BACKGROUND)
        self.homeSubstituteFrame.place(relx = 0.02, rely = 0.73, anchor = "nw")
        self.awaySubstituteFrame = ctk.CTkFrame(self.teamMatchFrame, width = 220, height = 180, fg_color = GREY_BACKGROUND)
        self.awaySubstituteFrame.place(relx = 0.98, rely = 0.73, anchor = "ne")

        ctk.CTkLabel(self.homeSubstituteFrame, text = "Substitutes", font = (APP_FONT, 20), fg_color = GREY_BACKGROUND).place(relx = 0.5, rely = 0.03, anchor = "n")
        ctk.CTkLabel(self.awaySubstituteFrame, text = "Substitutes", font = (APP_FONT, 20), fg_color = GREY_BACKGROUND).place(relx = 0.5, rely = 0.03, anchor = "n")

        self.addLineups()

        self.substitutionButton = ctk.CTkButton(self.teamMatchFrame, text = "Make Substitution", width = 400, height = 65, font = (APP_FONT, 20), fg_color = APP_BLUE, bg_color = TKINTER_BACKGROUND, state = "disabled", command = self.substitution)
        self.substitutionButton.place(relx = 0.5, rely = 0.73, anchor = "n")
        self.shoutsButton = ctk.CTkButton(self.teamMatchFrame, text = "Shouts", width = 400, height = 65, font = (APP_FONT, 20), fg_color = APP_BLUE, bg_color = TKINTER_BACKGROUND, state = "disabled", command = self.shouts)
        self.shoutsButton.place(relx = 0.5, rely = 0.92, anchor = "s")
        self.speedButtonsFrame = ctk.CTkFrame(self.teamMatchFrame, width = 400, height = 40, fg_color = TKINTER_BACKGROUND)
        self.speedButtonsFrame.place(relx = 0.5, rely = 0.98, anchor = "s")

        self.addSpeedButtons()
        self.createPlayerFrame(self.homePlayersFrame)
        self.createPlayerFrame(self.awayPlayersFrame)
        self.createStatsFrame(self.homeStatsFrame)
        self.createStatsFrame(self.awayStatsFrame)
        
    def addSpeedButtons(self):
        """
        Add speed control buttons to the matchday view.
        """
        
        veryFast = ctk.CTkButton(self.speedButtonsFrame, text = "Very Fast", width = 75, height = 40, font = (APP_FONT, 10), fg_color = APP_BLUE, bg_color = TKINTER_BACKGROUND, command = lambda: self.setSpeed(1 / 120))
        veryFast.place(relx = 0, rely = 0.5, anchor = "w")

        fast = ctk.CTkButton(self.speedButtonsFrame, text = "Fast", width = 75, height = 40, font = (APP_FONT, 10), fg_color = APP_BLUE, bg_color = TKINTER_BACKGROUND, command = lambda: self.setSpeed(1 / 60))
        fast.place(relx = 0.203125, rely = 0.5, anchor = "w")

        normal = ctk.CTkButton(self.speedButtonsFrame, text = "Normal", width = 75, height = 40, font = (APP_FONT, 10), fg_color = APP_BLUE, bg_color = TKINTER_BACKGROUND, command = lambda: self.setSpeed(3 / 60))
        normal.place(relx = 0.40625, rely = 0.5, anchor = "w")

        slow = ctk.CTkButton(self.speedButtonsFrame, text = "Slow", width = 75, height = 40, font = (APP_FONT, 10), fg_color = APP_BLUE, bg_color = TKINTER_BACKGROUND, command = lambda: self.setSpeed(5 / 60))
        slow.place(relx = 0.609375, rely = 0.5, anchor = "w")

        verySlow = ctk.CTkButton(self.speedButtonsFrame, text = "Very Slow", width = 75, height = 40, font = (APP_FONT, 10), fg_color = APP_BLUE, bg_color = TKINTER_BACKGROUND, command = lambda: self.setSpeed(8 / 60))
        verySlow.place(relx = 0.8125, rely = 0.5, anchor = "w")
    
    def setSpeed(self, speed):
        """
        Set the speed of the match simulation.
        
        Args:
            speed (float): The speed multiplier for the match simulation.
        """
        
        self.timerThread_running = False
        self.speed = speed
        self.timerThread_running = True

    def createPlayerFrame(self, frame):
        """
        Create player frames for the given frame (home or away players).
        
        Args:
            frame (ctk.CTkFrame): The frame to add player frames to.
        """

        lineup = self.matchFrame.matchInstance.homeCurrentLineup if frame == self.homePlayersFrame else self.matchFrame.matchInstance.awayCurrentLineup

        for playerID in lineup.values():
            InGamePlayerFrame(frame, playerID, 220, 18, GREY_BACKGROUND)

    def createStatsFrame(self, frame):
        """
        Create stats frames for the given frame (home or away stats).
        
        Args:
            frame (ctk.CTkFrame): The frame to add stats frames to.
        """
        
        stats = self.matchFrame.matchInstance.homeStats if frame == self.homeStatsFrame else self.matchFrame.matchInstance.awayStats

        for stat in stats.keys():
            InGameStatFrame(frame, stat, 220, 17, GREY_BACKGROUND)

    def changeData(self, side, selection):
        """
        Change the data displayed for the given side (home or away) based on the selection.
        
        Args:
            side (str): "home" or "away" to indicate which side to change.
            selection (str): The type of data to display ("Lineup", "Players", or "Stats").
        """

        if side == "home":
            self.homeCurrFrame.place_forget()
            if selection == "Lineup":
                self.homeCurrFrame = self.homeLineupPitch
                self.homeLineupPitch.place(relx = 0.02, rely = 0.06, anchor = "nw")
            elif selection == "Players":
                self.homeCurrFrame = self.homePlayersFrame
                self.homePlayersFrame.place(relx = 0.02, rely = 0.06, anchor = "nw")
                
                for playerID in self.matchFrame.matchInstance.homeCurrentLineup.values():
                    frame = [f for f in self.homePlayersFrame.winfo_children() if f.playerID == playerID]

                    if len(frame) == 0:
                        frame = InGamePlayerFrame(self.homePlayersFrame, playerID, 220, 18, GREY_BACKGROUND)
                    else:
                        frame = frame[0]
                        fitness = self.matchFrame.matchInstance.homeFitness[playerID]
                        frame.updateFitness(fitness)

            elif selection == "Stats":
                self.homeCurrFrame = self.homeStatsFrame
                self.homeStatsFrame.place(relx = 0.02, rely = 0.06, anchor = "nw")
        
        else:
            self.awayCurrFrame.place_forget()
            if selection == "Lineup":
                self.awayCurrFrame = self.awayLineupPitch
                self.awayLineupPitch.place(relx = 0.98, rely = 0.06, anchor = "ne")
            elif selection == "Players":
                self.awayCurrFrame = self.awayPlayersFrame
                self.awayPlayersFrame.place(relx = 0.98, rely = 0.06, anchor = "ne")

                for playerID in self.matchFrame.matchInstance.awayCurrentLineup.values():
                    frame = [f for f in self.awayPlayersFrame.winfo_children() if f.playerID == playerID]

                    if len(frame) == 0:
                        frame = InGamePlayerFrame(self.awayPlayersFrame, playerID, 220, 18, GREY_BACKGROUND)
                    else:
                        frame = frame[0]
                        fitness = self.matchFrame.matchInstance.awayFitness[playerID]
                        frame.updateFitness(fitness)

            elif selection == "Stats":
                self.awayCurrFrame = self.awayStatsFrame
                self.awayStatsFrame.place(relx = 0.98, rely = 0.06, anchor = "ne")

    def addMatches(self):
        """
        Add match frames for the current matchday, including the team match and other matches.
        """
        
        for match in self.matchDay:
            if match.home_id == self.team.id or match.away_id == self.team.id:
                # TEAM MATCH
                self.teamMatch = match
                self.matchFrame = MatchDayMatchFrame(self.teamMatchFrame, match, TKINTER_BACKGROUND, 150, 400, imageSize = 70, relx =  0.5, rely =  0.03, anchor = "n", border_width = 3, border_color = GREY_BACKGROUND, pack = False)
                
                self.matchDataFrame = ctk.CTkScrollableFrame(self.teamMatchFrame, width = 370, height = 300, fg_color = TKINTER_BACKGROUND, border_width = 3, border_color = GREY_BACKGROUND)
                self.matchDataFrame.place(relx = 0.5, rely = 0.27, anchor = "n")
                self.matchDataFrame._scrollbar.grid_configure(padx = 5)

                self.opposition = Teams.get_team_by_id(match.away_id if match.home_id == self.team.id else match.home_id)

                # Set the match instance lineups and fitness
                if match.home_id != self.team.id:
                    self.home = False
                    self.matchFrame.matchInstance.awayCurrentLineup = self.teamLineup
                    self.matchFrame.matchInstance.awayCurrentSubs = self.teamSubstitutes
                    self.matchFrame.matchInstance.awayStartLineup = self.teamLineup.copy()
                    self.matchFrame.matchInstance.awayFitness = {playerID: Players.get_player_by_id(playerID).fitness for playerID in list(self.teamLineup.values()) + self.teamSubstitutes}
                else:
                    self.matchFrame.matchInstance.homeCurrentLineup = self.teamLineup
                    self.matchFrame.matchInstance.homeCurrentSubs = self.teamSubstitutes
                    self.matchFrame.matchInstance.homeStartLineup = self.teamLineup.copy()
                    self.matchFrame.matchInstance.homeFitness = {playerID: Players.get_player_by_id(playerID).fitness for playerID in list(self.teamLineup.values()) + self.teamSubstitutes}
            else:
                # OTHER MATCHES
                MatchDayMatchFrame(self.otherMatchesFrame, match, TKINTER_BACKGROUND, 60, 300)

    def addTime(self):
        """
        Add the time display and control buttons to the matchday view.
        """
        
        self.timeLabel = ctk.CTkLabel(self.timeFrame, text = "00:00", font = (APP_FONT_BOLD, 50), fg_color = TKINTER_BACKGROUND)
        self.timeLabel.place(relx = 0.5, rely = 0.4, anchor = "center")

        self.extraTimeLabel = ctk.CTkLabel(self.timeFrame, text = "ET", font = (APP_FONT, 18), fg_color = TKINTER_BACKGROUND)

        self.pauseButton = ctk.CTkButton(self.timeFrame, text = "Kick-Off", font = (APP_FONT, 20), fg_color = APP_BLUE, bg_color = TKINTER_BACKGROUND, command = self.simulateMatch)
        self.pauseButton.place(relx = 0.5, rely = 0.8, anchor = "center")

    def addLineups(self):
        """
        Add the team and opposition lineups to the matchday view.
        """
        
        teamPitch = self.homeLineupPitch if self.home else self.awayLineupPitch
        teamSubFrame = self.homeSubstituteFrame if self.home else self.awaySubstituteFrame
        oppPitch = self.awayLineupPitch if self.home else self.homeLineupPitch
        oppSubFrame = self.awaySubstituteFrame if self.home else self.homeSubstituteFrame
        oppTeamID = self.opposition.id

        self.matchFrame.matchInstance.createTeamLineup(oppTeamID, not self.home)
        self.oppositionLineup = self.matchFrame.matchInstance.awayCurrentLineup if self.home else self.matchFrame.matchInstance.homeCurrentLineup
        oppositionSubstitutes = self.matchFrame.matchInstance.awayCurrentSubs if self.home else self.matchFrame.matchInstance.homeCurrentSubs

        self.matchFrame.matchInstance.setUpRatings()

        for position, playerID, in self.teamLineup.items():
            player = Players.get_player_by_id(playerID)
            teamPitch.addPlayer(position, player.last_name, matchday = True)

        for i, playerID in enumerate(self.teamSubstitutes):
            player = Players.get_player_by_id(playerID)
            ctk.CTkLabel(teamSubFrame, text = player.first_name + " " + player.last_name, font = (APP_FONT, 10), fg_color = GREY_BACKGROUND).place(relx = 0.1, rely = 0.25 + 0.11 * i, anchor = "w")
            ctk.CTkLabel(teamSubFrame, text = player.specific_positions, font = (APP_FONT, 10), fg_color = GREY_BACKGROUND).place(relx = 0.9, rely = 0.25 + 0.11 * i, anchor = "e")

        for position, playerID in self.oppositionLineup.items():
            player = Players.get_player_by_id(playerID)
            oppPitch.addPlayer(position, player.last_name, matchday = True)

        for i, playerID in enumerate(oppositionSubstitutes):
            player = Players.get_player_by_id(playerID)
            ctk.CTkLabel(oppSubFrame, text = player.first_name + " " + player.last_name, font = (APP_FONT, 10), fg_color = GREY_BACKGROUND).place(relx = 0.1, rely = 0.25 + 0.11 * i, anchor = "w")
            ctk.CTkLabel(oppSubFrame, text = player.specific_positions, font = (APP_FONT, 10), fg_color = GREY_BACKGROUND).place(relx = 0.9, rely = 0.25 + 0.11 * i, anchor = "e")

    def addPlayerFrame(self, frame, playerID):
        """
        Add a player frame for the given player ID to the specified frame.
        
        Args:
            frame (ctk.CTkFrame): The frame to add the player frame to.
            playerID (str): The ID of the player.
        """
        
        frame = InGamePlayerFrame(frame, playerID, 220, 18, GREY_BACKGROUND)
        return frame

    def updateSubFrame(self, home, playerOnID, playerOffID):
        """
        Update the substitute frame after a substitution.
        
        Args:
            home (bool): True if the substitution is for the home team, False for the away team.
            playerOnID (str): The ID of the player coming on.
            playerOffID (str): The ID of the player going off.
        """

        playerOn = Players.get_player_by_id(playerOnID)
        playerOff = Players.get_player_by_id(playerOffID)

        subFrame = self.homeSubstituteFrame if home else self.awaySubstituteFrame

        for i, widget in enumerate(subFrame.winfo_children()):
            if widget.cget("text") == playerOn.first_name + " " + playerOn.last_name:
                widget.configure(text = playerOff.first_name + " " + playerOff.last_name, text_color = "grey")

                subFrame.winfo_children()[i + 1].place_forget()

    def simulateMatch(self):
        """
        Start the match simulation.
        """
        
        self.pauseButton.configure(text = "Pause", command = self.pauseMatch)
        self.substitutionButton.configure(state = "normal") 
        self.shoutsButton.configure(state = "normal")

        self.timerThread_running = True
        self.timerThread = threading.Thread(target = self.gameLoop)
        self.timerThread.daemon = True
        self.timerThread.start()

    def pauseMatch(self):
        """
        Pause the match simulation.
        """
        
        self.pauseButton.configure(text = "Resume", command = self.resumeMatch)
        self.timerThread_running = False

    def resumeMatch(self, halfTime = False):
        """
        Resume the match simulation.

        Args:
            halfTime (bool): True if resuming after half-time, False otherwise.
        """

        if halfTime:
            self.halfTimeFrame.pack_forget()   

        self.pauseButton.configure(text = "Pause", command = self.pauseMatch)
        self.timerThread_running = True
        self.timerThread = threading.Thread(target = self.gameLoop)
        self.timerThread.daemon = True
        self.timerThread.start()

    def gameLoop(self):
        """
        The main game loop that updates the match time, player fitness, and handles match events.
        """
        
        while self.timerThread_running:
            
            currTime = self.timeLabel.cget("text")

            """
            HALF TIME - After Half time, once the player hits the "Resume" button.
            - Reset the time to 45:00
            - Reset all the score labels to what they were before HT
            - Allow shouts and substitutions again
            """
            if currTime == "HT":
                minutes = 45
                seconds = 0

                for frame in self.otherMatchesFrame.winfo_children():
                    if frame.matchInstance:
                        frame.HTLabel(place = False)
                        frame.matchInstance.halfTime = False

                self.matchFrame.HTLabel(place = False)
                self.matchFrame.matchInstance.halfTime = False

                self.shoutsButton.configure(state = "normal")
                self.substitutionButton.configure(state = "normal")
            else:
                currTime = currTime.split(":")
                minutes = int(currTime[0])
                seconds = int(currTime[1])

            """
            TIMER - Update the time every tick based on the speed selected
            """
            if seconds == 59:
                minutes += 1
                seconds = 0
            else:
                seconds += 1

            """
            SHOUTS - Reset the shout button to enabled 10 minutes after the last shout
            """
            if minutes == self.lastShout + 10 and seconds == 0:
                self.shoutsButton.configure(state = "normal")

            """
            SUBSTITUTIONS - Remove substitution button a minute before the end of the match
            """
            if minutes == 89 + self.maxExtraTimeFull and seconds == 0:
                self.substitutionButton.configure(state = "disabled")

            """
            FITNESS - Every 90 seconds, reduce the fitness of every player on the pitch
            - Reduce fitness of players who are currently on the pitch for team game as well as other matches
            - Reduce fitness based on player's fitness attribute and current fitness level (lower fitness = lower drop)
            - Update the fitness icon and text in the player frames if the players frame is currently being shown
            """
            total_seconds = minutes * 60 + seconds
            if total_seconds % 90 == 0:
                for frame in self.otherMatchesFrame.winfo_children():
                    if frame.matchInstance:
                        for playerID, fitness in frame.matchInstance.homeFitness.items():
                            if fitness > 0 and playerID in frame.matchInstance.homeCurrentLineup.values():
                                frame.matchInstance.homeFitness[playerID] = fitness - getFitnessDrop(Players.get_player_by_id(playerID), fitness)

                                if frame.matchInstance.homeFitness[playerID] < 0:
                                    frame.matchInstance.homeFitness[playerID] = 0

                        for playerID, fitness in frame.matchInstance.awayFitness.items():
                            if fitness > 0 and playerID in frame.matchInstance.awayCurrentLineup.values():
                                frame.matchInstance.awayFitness[playerID] = fitness - getFitnessDrop(Players.get_player_by_id(playerID), fitness)

                                if frame.matchInstance.awayFitness[playerID] < 0:
                                    frame.matchInstance.awayFitness[playerID] = 0

                for playerID, fitness in self.matchFrame.matchInstance.homeFitness.items():
                    if fitness > 0 and playerID in self.matchFrame.matchInstance.homeCurrentLineup.values():
                        self.matchFrame.matchInstance.homeFitness[playerID] = fitness - getFitnessDrop(Players.get_player_by_id(playerID), fitness)

                        if self.matchFrame.matchInstance.homeFitness[playerID] < 0:
                            self.matchFrame.matchInstance.homeFitness[playerID] = 0

                for playerID, fitness in self.matchFrame.matchInstance.awayFitness.items():
                    if fitness > 0 and playerID in self.matchFrame.matchInstance.awayCurrentLineup.values():
                        self.matchFrame.matchInstance.awayFitness[playerID] = fitness - getFitnessDrop(Players.get_player_by_id(playerID), fitness)

                        if self.matchFrame.matchInstance.awayFitness[playerID] < 0:
                            self.matchFrame.matchInstance.awayFitness[playerID] = 0

                if self.homePlayersFrame.winfo_ismapped():
                    for playerID in self.matchFrame.matchInstance.homeCurrentLineup.values():
                        frame = [f for f in self.homePlayersFrame.winfo_children() if f.playerID == playerID]

                        if len(frame) == 0:
                            frame = InGamePlayerFrame(self.homePlayersFrame, playerID, 220, 18, GREY_BACKGROUND)
                        else:
                            frame = frame[0]
                            fitness = self.matchFrame.matchInstance.homeFitness[playerID]
                            frame.updateFitness(fitness)

                if self.awayPlayersFrame.winfo_ismapped():
                    for playerID in self.matchFrame.matchInstance.awayCurrentLineup.values():
                        frame = [f for f in self.awayPlayersFrame.winfo_children() if f.playerID == playerID]

                        if len(frame) == 0:
                            frame = InGamePlayerFrame(self.awayPlayersFrame, playerID, 220, 18, GREY_BACKGROUND)
                        else:
                            frame = frame[0]
                            fitness = self.matchFrame.matchInstance.awayFitness[playerID]
                            frame.updateFitness(fitness)

            """
            HALF TIME - First Half time procedure
            - Calculate extra time for every match based on events that have happened (team match and other matches)
            - Get the maximum extra time from all matches and set that as the extra time for the first half
            - Display the extra time label in the time frame
            """
            if minutes == 45 and seconds == 0:

                ## extra time
                self.halfTime = True
                self.matchFrame.matchInstance.halfTime = True
                self.maxExtraTimeHalf = 0
                for frame in self.otherMatchesFrame.winfo_children():
                    if frame.matchInstance:
                        frame.matchInstance.halfTime = True
                        eventsExtraTime = 0
                        maxMinute = 0
                        firstHalfEvents = 0
                        combined_events = {**frame.matchInstance.homeEvents, **frame.matchInstance.awayEvents}
                        for event_time, event_details in list(combined_events.items()):
                            minute = int(event_time.split(":")[0])
                            if event_details["extra"] and minute < 90: # first half extra time events
                                eventsExtraTime += 1
                                
                                if minute + 1 > maxMinute:
                                    maxMinute = minute + 1

                            elif minute < 45 and event_details["type"] != "substitution":
                                firstHalfEvents += 1

                        if maxMinute - 45 < firstHalfEvents:
                            extraTime = min(firstHalfEvents, 5)
                        else:
                            extraTime = maxMinute - 45

                        if extraTime > self.maxExtraTimeHalf:
                            self.maxExtraTimeHalf = extraTime

                        frame.matchInstance.extraTimeHalf = extraTime

                eventsExtraTime = 0
                maxMinute = 0
                firstHalfEvents = 0
                combined_events = {**self.matchFrame.matchInstance.homeEvents, **self.matchFrame.matchInstance.awayEvents}
                for event_time, event_details in list(combined_events.items()):
                    minute = int(event_time.split(":")[0])
                    if event_details["extra"] and minute < 90: # first hald extra time events
                        eventsExtraTime += 1
                        
                        if minute + 1 > maxMinute:
                            maxMinute = minute + 1

                    elif minute < 45 and event_details["type"] != "susbtitution":
                        firstHalfEvents += 1
                
                if maxMinute - 45 < firstHalfEvents:
                    extraTime = min(firstHalfEvents, 5)
                else:
                    extraTime = maxMinute - 45

                if extraTime > self.maxExtraTimeHalf:
                    self.maxExtraTimeHalf = extraTime

                self.matchFrame.matchInstance.extraTimeHalf = extraTime

                frame = ctk.CTkFrame(self.matchDataFrame, width = 370, height = 30, fg_color = TKINTER_BACKGROUND)
                frame.pack(expand = True, fill = "both")
                ctk.CTkLabel(frame, text = f"+{self.matchFrame.matchInstance.extraTimeHalf} minute(s) added", font = (APP_FONT, 15), fg_color = TKINTER_BACKGROUND).place(relx = 0.5, rely = 0.5, anchor = "center")

                self.matchDataFrame.update_idletasks()
                self.matchDataFrame._parent_canvas.yview_moveto(1)

            """
            HALF TIME - Second Half time procedure
            - Display the extra time label in the time frame
            - Call the half time talks function to display the half time frame
            - If the max time is reached, set half time to false and stop the timer
            - Add HT labels to every match if not already there
            - Remove the extra time label from the time frame
            """
            if self.halfTime:
                self.extraTimeLabel.place(relx = 0.76, rely = 0.48, anchor = "center")
                if minutes == 45 + self.maxExtraTimeHalf and seconds == 0:
                    self.timerThread_running = False
                    self.halfTimeTalks()

                    for frame in self.otherMatchesFrame.winfo_children():
                        if not frame.halfTimeLabel.winfo_ismapped() and frame.matchInstance:
                            frame.HTLabel()

                    if not self.matchFrame.halfTimeLabel.winfo_ismapped():
                        self.matchFrame.HTLabel() 

                    self.extraTimeLabel.place_forget()

                    self.halfTime = False
                    self.halfTimeEnded = True

            """
            FULL TIME - First Full time procedure
            - Calculate extra time for every match based on events that have happened (team match and other matches)
            - Get the maximum extra time from all matches and set that as the extra time for the full time
            - Display the extra time label in the time frame
            """
            if minutes == 90 and seconds == 0:
               
                self.fullTime = True
                self.matchFrame.matchInstance.fullTime = True
                self.maxExtraTimeFull = 0

                for frame in self.otherMatchesFrame.winfo_children():
                    if frame.matchInstance:
                        frame.matchInstance.fullTime = True
                        eventsExtraTime = 0
                        maxMinute = 0
                        secondHalfEvents = 0
                        combined_events = {**frame.matchInstance.homeEvents, **frame.matchInstance.awayEvents}
                        for event_time, event_details in list(combined_events.items()):
                            minute = int(event_time.split(":")[0])
                            if event_details["extra"] and minute > 90: # second half extra time events
                                eventsExtraTime += 1
                                
                                if minute + 1 > maxMinute:
                                    maxMinute = minute + 1

                            elif minute > 45 and not event_details["extra"] and event_details["type"] != "substitution":
                                secondHalfEvents += 1

                        if maxMinute - 90 < secondHalfEvents:
                            extraTime = min(secondHalfEvents, 5)
                        else:
                            extraTime = maxMinute - 90

                        if extraTime > self.maxExtraTimeFull:
                            self.maxExtraTimeFull = extraTime

                        frame.matchInstance.extraTimeFull = extraTime

                eventsExtraTime = 0
                maxMinute = 0
                secondHalfEvents = 0
                combined_events = {**self.matchFrame.matchInstance.homeEvents, **self.matchFrame.matchInstance.awayEvents}
                for event_time, event_details in list(combined_events.items()):
                    minute = int(event_time.split(":")[0])
                    if event_details["extra"] and minute > 90: # first hald extra time events
                        eventsExtraTime += 1
                        
                        if minute + 1 > maxMinute:
                            maxMinute = minute + 1

                    elif minute > 45 and not event_details["extra"] and event_details["type"] != "susbtitution":
                        secondHalfEvents += 1

                if maxMinute - 90 < secondHalfEvents:
                    extraTime = min(secondHalfEvents, 5)
                else:
                    extraTime = maxMinute - 90

                if extraTime > self.maxExtraTimeFull:
                    self.maxExtraTimeFull = extraTime

                self.matchFrame.matchInstance.extraTimeFull = extraTime

                frame = ctk.CTkFrame(self.matchDataFrame, width = 370, height = 30, fg_color = TKINTER_BACKGROUND)
                frame.pack(expand = True, fill = "both")
                ctk.CTkLabel(frame, text = f"+{self.matchFrame.matchInstance.extraTimeFull} minute(s) added", font = (APP_FONT, 15), fg_color = TKINTER_BACKGROUND).place(relx = 0.5, rely = 0.5, anchor = "center")

                self.matchDataFrame.update_idletasks()
                self.matchDataFrame._parent_canvas.yview_moveto(1)

            """
            FULL TIME - Second Full time procedure
            - Display the extra time label in the time frame
            - If the max time is reached, set full time to false and stop the timer
            - Add FT labels to every match if not already there
            - Remove the extra time label from the time frame
            - Ensure the Full Time label is placed at the end of the match data frame
            """
            if self.fullTime:
                self.extraTimeLabel.place(relx = 0.76, rely = 0.48, anchor = "center")
                if minutes == 90 + self.maxExtraTimeFull and seconds == 0:
                    self.timerThread_running = False
                    self.pauseButton.configure(text = "Save", command = self.endSimulation)
                    self.fullTime = False
                    self.fullTimeEnded = True

                    for frame in self.otherMatchesFrame.winfo_children():
                        if not frame.fullTimeLabel.winfo_ismapped() and frame.matchInstance:
                            frame.FTLabel()

                    if not self.matchFrame.fullTimeLabel.winfo_ismapped():
                        self.matchFrame.FTLabel()
                    
                    self.extraTimeLabel.place_forget()
                
                    if self.matchFrame.matchInstance.extraTimeFull == 5:
                        self.shoutsButton.configure(state = "disabled")
                        frame = ctk.CTkFrame(self.matchDataFrame, width = 370, height = 30, fg_color = TKINTER_BACKGROUND)
                        frame.pack(expand = True, fill = "both")
                        ctk.CTkLabel(frame, text = "------------------ Full Time ------------------", font = (APP_FONT, 15), fg_color = TKINTER_BACKGROUND).place(relx = 0.5, rely = 0.5, anchor = "center")

                        self.matchDataFrame.update_idletasks()
                        self.matchDataFrame._parent_canvas.yview_moveto(1)

            """
            EVENTS - Other matches
            - Add the HT and FT labels at the correct times
            - Check every match for events that need to be processed at the current time
            - If goal, update the score label
            """
            for frame in self.otherMatchesFrame.winfo_children():
                
                if not frame.matchInstance:
                    continue

                if minutes == 45 + frame.matchInstance.extraTimeHalf and self.halfTime and seconds == 0:
                    frame.HTLabel()

                if minutes == 90 + frame.matchInstance.extraTimeFull and self.fullTime and seconds == 0:
                    frame.FTLabel()
                
                for event_time, event_details in list(frame.matchInstance.homeEvents.items()):
                    if event_time == str(minutes) + ":" + str(seconds) and event_time not in frame.matchInstance.homeProcessedEvents:
                        if event_details["extra"]:
                            if self.halfTime or self.fullTime:
                                if event_details["type"] in ["own_goal", "goal", "penalty_goal"]:
                                    frame.updateScoreLabel()
                                frame.matchInstance.getEventPlayer(event_details, True, event_time)
                                frame.matchInstance.homeProcessedEvents[event_time] = event_details
                        else:
                            if not (self.halfTime or self.fullTime):
                                if event_details["type"] in ["own_goal", "goal", "penalty_goal"]:
                                    frame.updateScoreLabel()
                                frame.matchInstance.getEventPlayer(event_details, True, event_time)
                                frame.matchInstance.homeProcessedEvents[event_time] = event_details
                
                for event_time, event_details in list(frame.matchInstance.awayEvents.items()):
                    if event_time == str(minutes) + ":" + str(seconds) and event_time not in frame.matchInstance.awayProcessedEvents:
                        if event_details["extra"]:
                            if self.halfTime or self.fullTime:
                                if event_details["type"] in ["own_goal", "goal", "penalty_goal"]:
                                    frame.updateScoreLabel(home = False)
                                frame.matchInstance.getEventPlayer(event_details, False, event_time)
                                frame.matchInstance.awayProcessedEvents[event_time] = event_details
                        else:
                            if not (self.halfTime or self.fullTime):
                                if event_details["type"] in ["own_goal", "goal", "penalty_goal"]:
                                    frame.updateScoreLabel(home = False)

                                frame.matchInstance.getEventPlayer(event_details, False, event_time)
                                frame.matchInstance.awayProcessedEvents[event_time] = event_details

            """
            HALF TIME - your team match has reached its half time
            - Disable shouts and substitutions
            - Add the HT label
            - Add a half time separator in the match data frame
            """
            if minutes == 45 + self.matchFrame.matchInstance.extraTimeHalf and self.halfTime and seconds == 0:
                self.shoutsButton.configure(state = "disabled")
                self.substitutionButton.configure(state = "disabled")
                self.matchFrame.HTLabel()

                frame = ctk.CTkFrame(self.matchDataFrame, width = 370, height = 30, fg_color = TKINTER_BACKGROUND)
                ctk.CTkLabel(frame, text = "------------------ Half Time ------------------", font = (APP_FONT, 15), fg_color = TKINTER_BACKGROUND).place(relx = 0.5, rely = 0.5, anchor = "center")
                frame.pack(expand = True, fill = "both")

                self.matchDataFrame.update_idletasks()
                self.matchDataFrame._parent_canvas.yview_moveto(1)
            
            """
            FULL TIME - your team match has reached its full time
            - Disable shouts and substitutions
            - Add the FT label
            - Add a full time separator in the match data frame
            """
            if minutes == 90 + self.matchFrame.matchInstance.extraTimeFull and self.fullTime and seconds == 0:
                self.shoutsButton.configure(state = "disabled")
                self.substitutionButton.configure(state = "disabled")
                self.matchFrame.FTLabel()

                frame = ctk.CTkFrame(self.matchDataFrame, width = 370, height = 30, fg_color = TKINTER_BACKGROUND)
                ctk.CTkLabel(frame, text = "------------------ Full Time ------------------", font = (APP_FONT, 15), fg_color = TKINTER_BACKGROUND).place(relx = 0.5, rely = 0.5, anchor = "center")
                frame.pack(expand = True, fill = "both")

                self.matchDataFrame.update_idletasks()
                self.matchDataFrame._parent_canvas.yview_moveto(1)

            """
            TICK - Every 30 seconds, generate events and statistics for every match
            - Generate events and stats for both teams in your match
            - Get the passes and possession stats for your match
            - Update the stats frames with the new stats
            - Get the events, stats and passes and possession for other matches
            """
            if total_seconds % TICK == 0 and self.timeLabel.cget("text") != "HT":
                self.generateEvents("home", matchInstance = self.matchFrame.matchInstance, teamMatch = True)
                self.generateEvents("away", matchInstance = self.matchFrame.matchInstance, teamMatch = True)
                passesAndPossession(matchInstance = self.matchFrame.matchInstance)

                for stat in MATCH_STATS:
                    homeStats = self.matchFrame.matchInstance.homeStats
                    awayStats = self.matchFrame.matchInstance.awayStats

                    # Update stats frames
                    if stat == "Possession":
                        valueH, valueA = homeStats[stat], awayStats[stat]
                        textH, textA = f"{valueH}%", f"{valueA}%"
                    elif stat == "Passes":
                        valueH, valueA = getStatNum(homeStats[stat]), getStatNum(awayStats[stat])
                        textH, textA = f"{valueH} ({self.matchFrame.matchInstance.homePassesAttempted})", f"{valueA} ({self.matchFrame.matchInstance.awayPassesAttempted})"
                    elif stat in PLAYER_STATS:
                        valueH, valueA = getStatNum(homeStats[stat]), getStatNum(awayStats[stat])
                        textH, textA = f"{valueH}", f"{valueA}"
                    else:
                        valueH, valueA = homeStats[stat], awayStats[stat]
                        textH, textA = f"{valueH}", f"{valueA}"

                    for frame in self.homeStatsFrame.winfo_children():
                        if frame.statName == stat:
                            if stat in NEGATIVE_STATS:
                                color = False if valueH > valueA else True if valueA > valueH else None
                            else:
                                color = True if valueH > valueA else False if valueA > valueH else None
                            frame.updateValue(textH, color)

                    for frame in self.awayStatsFrame.winfo_children():
                        if frame.statName == stat:
                            if stat in NEGATIVE_STATS:
                                color = False if valueA > valueH else True if valueH > valueA else None
                            else:
                                color = True if valueA > valueH else False if valueH > valueA else None
                            frame.updateValue(textA, color)

                for frame in self.otherMatchesFrame.winfo_children():
                    if frame.matchInstance:
                        self.generateEvents("home", matchInstance = frame.matchInstance)
                        self.generateEvents("away", matchInstance = frame.matchInstance)

                        passesAndPossession(matchInstance = frame.matchInstance)

            """
            EVENTS - Home team events
            - Check for events that need to be processed at the current time
            - If an event is marked as extra time, only process it if half time or full
            - If an event is not marked as extra time, only process it if not half time or full
            - Update the match data frame with the new event
            - If goal, update the score label
            - If injury or red card and your team is the home team, make a substitution
            """
            for event_time, event_details in list(self.matchFrame.matchInstance.homeEvents.items()):
                if event_time == str(minutes) + ":" + str(seconds) and event_time not in self.matchFrame.matchInstance.homeProcessedEvents:
                    if event_details["extra"]:
                        if self.halfTime or self.fullTime:
                            if event_details["type"] in ["own_goal", "goal", "penalty_goal"]:
                                self.matchFrame.updateScoreLabel()

                            newEvent = self.matchFrame.matchInstance.getEventPlayer(event_details, True, event_time, teamMatch = self, managing_team = True if self.home else False)
                            self.matchFrame.matchInstance.homeProcessedEvents[event_time] = event_details

                            if self.home and event_details["type"] == "injury":
                                self.substitution(forceSub = True, injuredPlayer = newEvent["player"])
                            if self.home and event_details["type"] == "red_card":
                                self.substitution(redCardPlayer = newEvent["player"], redCardPosition = newEvent["position"])

                            self.after(0, self.updateMatchDataFrame, newEvent, event_time, True)
                    else:
                        if not (self.halfTime or self.fullTime):
                            if event_details["type"] in ["own_goal", "goal", "penalty_goal"]:
                                self.matchFrame.updateScoreLabel()
                            newEvent = self.matchFrame.matchInstance.getEventPlayer(event_details, True, event_time, teamMatch = self, managing_team = True if self.home else False)
                            self.matchFrame.matchInstance.homeProcessedEvents[event_time] = event_details

                            if self.home and event_details["type"] == "injury":
                                self.substitution(forceSub = True, injuredPlayer = newEvent["player"])
                            if self.home and event_details["type"] == "red_card":
                                self.substitution(redCardPlayer = newEvent["player"], redCardPosition = newEvent["position"])

                            self.after(0, self.updateMatchDataFrame, newEvent, event_time, True)

            """
            EVENTS - Away team events
            - Check for events that need to be processed at the current time
            - If an event is marked as extra time, only process it if half time or full
            - If an event is not marked as extra time, only process it if not half time or full
            - Update the match data frame with the new event
            - If goal, update the score label
            - If injury or red card and your team is the away team, make a substitution
            """
            for event_time, event_details in list(self.matchFrame.matchInstance.awayEvents.items()):
                if event_time == str(minutes) + ":" + str(seconds) and event_time not in self.matchFrame.matchInstance.awayProcessedEvents:
                    if event_details["extra"]:
                        if self.halfTime or self.fullTime:
                            if event_details["type"] in ["own_goal", "goal", "penalty_goal"]:
                                self.matchFrame.updateScoreLabel(home = False)
                            newEvent = self.matchFrame.matchInstance.getEventPlayer(event_details, False, event_time, teamMatch = self, managing_team = True if not self.home else False)
                            self.matchFrame.matchInstance.awayProcessedEvents[event_time] = event_details

                            if not self.home and event_details["type"] == "injury":
                                self.substitution(forceSub = True, injuredPlayer = event_details["player"])
                            if not self.home and event_details["type"] == "red_card":
                                self.substitution(redCardPlayer = event_details["player"], redCardPosition = event_details["position"])

                            self.after(0, self.updateMatchDataFrame, event_details, event_time, False)
                    else:
                        if not (self.halfTime or self.fullTime):
                            if event_details["type"] in ["own_goal", "goal", "penalty_goal"]:
                                self.matchFrame.updateScoreLabel(home = False)
                            newEvent = self.matchFrame.matchInstance.getEventPlayer(event_details, False, event_time, teamMatch = self, managing_team = True if not self.home else False)
                            self.matchFrame.matchInstance.awayProcessedEvents[event_time] = event_details

                            if not self.home and event_details["type"] == "injury":
                                self.substitution(forceSub = True, injuredPlayer = event_details["player"])
                            if not self.home and event_details["type"] == "red_card":
                                self.substitution(redCardPlayer = event_details["player"], redCardPosition = event_details["position"])

                            self.after(0, self.updateMatchDataFrame, event_details, event_time, False)

            """
            TIMER - Configure the time label based on the current time
            - If half time has just ended, set the label to HT
            - If full time has just ended, set the label to FT
            - Otherwise, update the label with the current time
            """
            if self.halfTimeEnded:
                self.timeLabel.configure(text = "HT")
                self.halfTimeEnded = False
            elif self.fullTimeEnded:
                self.timeLabel.configure(text = "FT")
            else:
                self.after(0, self.updateTimeLabel, minutes, seconds)

            time.sleep(self.speed)

    def generateEvents(self, side, matchInstance = None, teamMatch = False):
        """
        Generate match events and statistics for a given side (home or away)
        
        Args:
            side (str): "home" or "away" indicating which team's events to generate
            matchInstance (Match, optional): The match instance to generate events for. Defaults to None.
            teamMatch (bool, optional): Whether the match is a team match. Defaults to False.
        """
        
        eventsToAdd = []
        statsToAdd = []

        lineup = matchInstance.homeCurrentLineup if side == "home" else matchInstance.awayCurrentLineup
        oppLineup = matchInstance.awayCurrentLineup if side == "home" else matchInstance.homeCurrentLineup
        matchEvents = matchInstance.homeEvents if side == "home" else matchInstance.awayEvents
        fitness = matchInstance.homeFitness if side == "home" else matchInstance.awayFitness
        subsCount = matchInstance.homeSubs if side == "home" else matchInstance.awaySubs
        stats = matchInstance.homeStats if side == "home" else matchInstance.awayStats
        oppStats = matchInstance.awayStats if side == "home" else matchInstance.homeStats
        subs = matchInstance.homeCurrentSubs if side == "home" else matchInstance.awayCurrentSubs
        events = matchInstance.homeProcessedEvents if side == "home" else matchInstance.awayProcessedEvents
        ratings = matchInstance.homeRatings if side == "home" else matchInstance.awayRatings
        oppRatings = matchInstance.awayRatings if side == "home" else matchInstance.homeRatings

        playerOBJs = matchInstance.homePlayersOBJ if side == "home" else matchInstance.awayPlayersOBJ 
        oppPlayersOBJ = matchInstance.awayPlayersOBJ if side == "home" else matchInstance.homePlayersOBJ

        if teamMatch:
            pitch = self.homeLineupPitch if side == "home" else self.awayLineupPitch
            oppPitch = self.awayLineupPitch if side == "home" else self.homeLineupPitch

        # ------------------ STATS CALCULATION ------------------
        sharpness = [playerOBJs[playerID].sharpness for playerID in lineup.values()]
        avgSharpnessWthKeeper = sum(sharpness) / len(sharpness)

        if "Goalkeeper" in lineup:
            avgSharpness = (sum(sharpness) - playerOBJs[lineup["Goalkeeper"]].sharpness) / (len(sharpness) - 1)
        else:
            avgSharpness = avgSharpnessWthKeeper

        avgFitness = sum(fitness[playerID] for playerID in lineup.values()) / len(lineup)

        morale = [playerOBJs[playerID].morale for pos, playerID in lineup.items() if pos != "Goalkeeper"]
        avgMorale = sum(morale) / len(morale)

        oppKeeper = oppPlayersOBJ[oppLineup["Goalkeeper"]] if "Goalkeeper" in oppLineup else None

        attackingPlayers = [playerID for pos, playerID in lineup.items() if pos in ATTACKING_POSITIONS]
        defendingPlayers = [playerID for pos, playerID in oppLineup.items() if pos in DEFENSIVE_POSITIONS]

        attackingLevel = teamStrength(attackingPlayers, "attack", playerOBJs)
        defendingLevel = teamStrength(defendingPlayers, "defend", oppPlayersOBJ)

        # ------------------ GOAL ------------------
        event = goalChances(attackingLevel, defendingLevel, avgSharpness, avgMorale, oppKeeper)

        if event == "goal":

            goalType = random.choices(list(GOAL_TYPE_CHANCES.keys()), weights = list(GOAL_TYPE_CHANCES.values()), k = 1)[0]

            if goalType == "penalty":
                if random.random() < PENALTY_SCORE_CHANCE or "Goalkeeper" not in oppLineup:
                    goalType = "penalty_goal"
                    matchInstance.appendScore(1, True if side == "home" else False)
                else:
                    goalType = "penalty_miss"
            else:
                matchInstance.appendScore(1, True if side == "home" else False)
            
            eventsToAdd.append(goalType)

            if random.random() < GOAL_BIG_CHANCE:
                statsToAdd.append("Big chances created")
        elif event != "nothing":
            statsToAdd.append(event)

        # ------------------ FOUL ------------------
        event = foulChances(avgSharpnessWthKeeper, matchInstance.referee.severity)

        if event in ["yellow_card", "red_card"]:
            eventsToAdd.append(event)
        elif event == "Fouls":
            statsToAdd.append(event)
        else:
            # If nothing, get tackles and interceptions
            tacklesInterceptions = random.choices(population = list(DEFENSIVE_ACTIONS_CHANCES.keys()), weights = list(DEFENSIVE_ACTIONS_CHANCES.values()), k = 1)[0]

            if tacklesInterceptions != "nothing":
                statsToAdd.append(tacklesInterceptions)

        # ------------------ INJURY ------------------
        event = injuryChances(avgFitness)

        if event == "injury":
            eventsToAdd.append(event)

        # ------------------ SUBSTITUTIONS ------------------
        if not teamMatch:
            subsChosen = substitutionChances(lineup, subsCount, subs.copy(), events, int(self.timeLabel.cget("text").split(":")[0]), fitness, playerOBJs, ratings)
            for _ in range(len(subsChosen)):
                eventsToAdd.append("substitution")

        else:
            if (self.home and side == "away") or (not self.home and side == "home"):
                subsChosen = substitutionChances(lineup, subsCount, subs.copy(), events, int(self.timeLabel.cget("text").split(":")[0]), fitness, playerOBJs, ratings)
                for _ in range(len(subsChosen)):
                    eventsToAdd.append("substitution")

        # ------------------ TIMES and ADDING ------------------
        currMin, currSec = map(int, self.timeLabel.cget("text").split(":"))
        extraTime = self.halfTime or self.fullTime
        
        currTotalSecs = currMin * 60 + currSec
        futureTotalSecs = currTotalSecs + 30

        if extraTime:
            # Get the max total seconds including extra time
            maxMinute = matchInstance.extraTimeHalf if self.halfTime else matchInstance.extraTimeFull
            finalMinute = 45 if self.halfTime else 90
            maxTotalSecs = (finalMinute + maxMinute) * 60
        else:
            # otherwise, max is normal time
            maxMinute = 45 if self.halfTime else 90
            maxTotalSecs = maxMinute * 60

        endTotalSecs = min(futureTotalSecs, maxTotalSecs)

        subsChosenCount = 0
        for event in eventsToAdd:
            try:
                eventTotalSecs = random.randint(currTotalSecs + 10, endTotalSecs)
            except ValueError:
                break

            # Convert back to mm:ss
            eventMin = eventTotalSecs // 60
            eventSec = eventTotalSecs % 60
            eventTime = f"{eventMin}:{eventSec:02d}"

            if event == "substitution":
                # substitution event needs entries such as player off/on and positions
                matchEvents[eventTime] = {"type": "substitution", "extra": extraTime, "player_off": subsChosen[subsChosenCount][0], "player_on": subsChosen[subsChosenCount][2], "old_position": subsChosen[subsChosenCount][1], "new_position": subsChosen[subsChosenCount][3], "injury": False}
                subsChosenCount += 1
            elif event == "penalty_miss":
                # penalty miss needs to know the opponent keeper
                matchEvents[eventTime] = {"type": event, "extra": extraTime, "keeper": oppLineup["Goalkeeper"] if "Goalkeeper" in oppLineup else None}
            else:
                matchEvents[eventTime] = {"type": event, "extra": extraTime}

        for stat in statsToAdd:

            if stat in PLAYER_STATS:
                # Get the player associated with the stat
                playerID, rating = getStatPlayer(stat, lineup, playerOBJs)
                ratings[playerID] = min(10, max(0, round(ratings.get(playerID, 0) + rating, 2)))
            
                if teamMatch:
                    self.updateRatingOval(pitch, playerID, lineup, ratings)

                if not playerID:
                    continue

                if not playerID in stats[stat]:
                    stats[stat][playerID] = 0

                stats[stat][playerID] += 1

                match stat:
                    case "Shots":
                        # For shots, get the direction, outcome, xG and big chance created/missed

                        shotDirection = random.choices(population = list(SHOT_DIRECTION_CHANCES.keys()), weights = list(SHOT_DIRECTION_CHANCES.values()), k = 1)[0]
                        if not playerID in stats[shotDirection]:
                            stats[shotDirection][playerID] = 0

                        stats[shotDirection][playerID] += 1

                        shotOutcome = random.choices(population = list(SHOT_CHANCES.keys()), weights = list(SHOT_CHANCES.values()), k = 1)[0]
                        if shotOutcome != "wide":
                            stats[shotOutcome] += 1

                        if random.random() < SHOT_BIG_CHANCE:
                            if not playerID in stats["Big chances missed"]:
                                stats["Big chances missed"][playerID] = 0

                            stats["Big chances missed"][playerID] += 1

                            playerID, rating = getStatPlayer("Big chances created", lineup, playerOBJs)
                            ratings[playerID] = min(10, max(0, round(ratings.get(playerID, 0) + rating, 2)))

                            if teamMatch:
                                self.updateRatingOval(pitch, playerID, lineup, ratings)
                    
                            if not playerID in stats["Big chances created"]:
                                stats["Big chances created"][playerID] = 0

                            stats["Big chances created"][playerID] += 1

                        stats["xG"] += round(random.uniform(0.02, MAX_XG), 2)
                        stats["xG"] = round(stats["xG"], 2)
                    case "Shots on target":
                        # For shots on target, add to shots, xG, big chance created/missed, and add a save to opponent keeper stats

                        if playerID not in stats["Shots"]:
                            stats["Shots"][playerID] = 0
                        
                        stats["Shots"][playerID] += 1

                        shotDirection = random.choices(population = list(SHOT_DIRECTION_CHANCES.keys()), weights = list(SHOT_DIRECTION_CHANCES.values()), k = 1)[0]
                        if not playerID in stats[shotDirection]:
                            stats[shotDirection][playerID] = 0
                        
                        stats[shotDirection][playerID] += 1

                        if random.random() < SHOT_BIG_CHANCE:
                            if not playerID in stats["Big chances missed"]:
                                stats["Big chances missed"][playerID] = 0

                            stats["Big chances missed"][playerID] += 1

                            playerID, rating = getStatPlayer("Big chances created", lineup, playerOBJs)
                            ratings[playerID] = min(10, max(0, round(ratings.get(playerID, 0) + rating, 2)))

                            if teamMatch:
                                self.updateRatingOval(pitch, playerID, lineup, ratings)

                            if not playerID in stats["Big chances created"]:
                                stats["Big chances created"][playerID] = 0

                            stats["Big chances created"][playerID] += 1

                        playerID, rating = getStatPlayer("Saves", oppLineup, oppPlayersOBJ)
                        if playerID:
                            if playerID not in oppStats["Saves"]:
                                oppStats["Saves"][playerID] = 0
                            oppStats["Saves"][playerID] += 1

                            oppRatings[playerID] = min(10, max(0, round(oppRatings.get(playerID, 0) + rating, 2)))

                            if teamMatch:
                                self.updateRatingOval(oppPitch, playerID, oppLineup, oppRatings)

                        stats["xG"] += round(random.uniform(0.02, MAX_XG), 2)
                        stats["xG"] = round(stats["xG"], 2)
            else:
                stats[stat] += 1

    def shouts(self):
        """
        Open the shouts frame to allow the user to make a shout during the match.
        """

        self.currMin = int(self.timeLabel.cget("text").split(":")[0])
        if self.currMin - self.lastShout < 10 and self.lastShout != 0:
            return
        
        self.shoutMade = False

        self.pauseMatch()
        self.pauseButton.configure(state = "disabled")
        self.substitutionButton.configure(state = "disabled")
        self.shoutsButton.configure(state = "disabled")

        self.shoutsFrame = ctk.CTkFrame(self, width = 400, height = 300, fg_color = TKINTER_BACKGROUND, border_color = APP_BLUE, border_width = 2)
        self.shoutsFrame.place(relx = 0.5, rely = 0.5, anchor = "center")
        self.shoutsFrame.pack_propagate(False)

        for i in range(len(SHOUTS)):
            ShoutFrame(self.shoutsFrame, 400, 30, 0, TKINTER_BACKGROUND, SHOUTS[i], self.matchFrame, self.home, self.currMin, self.setShoutMade, self.closeShouts)

        closeButton = ctk.CTkButton(self.shoutsFrame, text = "Close", width = 100, height = 30, font = (APP_FONT, 15), fg_color = APP_BLUE, bg_color = TKINTER_BACKGROUND, command = self.closeShouts)
        closeButton.pack(pady = 10)

    def setShoutMade(self):
        """
        Set the shoutMade flag to True and disable the shouts button.
        """

        self.shoutMade = True
        self.shoutsButton.configure(state = "disabled")

    def closeShouts(self):
        """
        Close the shouts frame and resume the match.
        """

        if self.shoutMade:
            self.lastShout = self.currMin + 1 if self.currMin == 0 else self.currMin
        else:
            self.shoutsButton.configure(state = "normal")

        self.shoutsFrame.place_forget()
        self.pauseButton.configure(state = "normal")
        self.substitutionButton.configure(state = "normal")
        self.resumeMatch()

    def substitution(self, forceSub = False, injuredPlayer = None, redCardPlayer = None, redCardPosition = None):
        """
        Open the substitution frame to allow the user to make substitutions during the match.
        
        Args:
            forceSub (bool, optional): Whether the substitution is forced due to injury. Defaults to False.
            injuredPlayer (int, optional): The ID of the injured player. Defaults to None.
            redCardPlayer (int, optional): The ID of the player who received a red card. Defaults to None.
            redCardPosition (str, optional): The position of the player who received a red card. Defaults to None.
        """
        
        self.startTeamLineup = self.matchFrame.matchInstance.homeCurrentLineup.copy() if self.home else self.matchFrame.matchInstance.awayCurrentLineup.copy()
        self.startTeamSubstitutes = self.matchFrame.matchInstance.homeCurrentSubs.copy() if self.home else self.matchFrame.matchInstance.awayCurrentSubs.copy()
        self.teamLineup = self.startTeamLineup.copy()
        self.teamSubstitutes = self.startTeamSubstitutes.copy()

        self.playersOn = {}
        self.playersOff = {}
        self.freePositions = []

        self.forceSub = forceSub
        self.injuredPlayer = Players.get_player_by_id(injuredPlayer) if injuredPlayer else None
        self.redCardPlayer = Players.get_player_by_id(redCardPlayer) if redCardPlayer else None
        self.redCardPosition = redCardPosition if redCardPosition else None

        self.redCardPlayers.append(self.redCardPlayer.id) if self.redCardPlayer else None

        self.currentSubs = 0

        self.values = list(POSITION_CODES.keys())

        self.pauseMatch()

        self.substitutionFrame = ctk.CTkFrame(self, width = APP_SIZE[0], height = APP_SIZE[1], fg_color = TKINTER_BACKGROUND)
        self.substitutionFrame.place(relx = 0, rely = 0, anchor = "nw")

        self.lineupPitch = FootballPitchLineup(self.substitutionFrame, 450, 750, 0, 0, "nw", TKINTER_BACKGROUND, "green")

        self.addFrame = ctk.CTkFrame(self.substitutionFrame, fg_color = GREY_BACKGROUND, width = 370, height = 50, corner_radius = 10)
        self.addFrame.place(relx = 0.01, rely = 0.98, anchor = "sw")

        ctk.CTkLabel(self.addFrame, text = "Add Substitute:", font = (APP_FONT, 18), text_color = "white", fg_color = GREY_BACKGROUND).place(relx = 0.05, rely = 0.5, anchor = "w")

        self.dropDown = ctk.CTkComboBox(self.addFrame, font = (APP_FONT, 15), fg_color = DARK_GREY, border_color = DARK_GREY, button_color = DARK_GREY, button_hover_color = DARK_GREY, dropdown_fg_color = DARK_GREY, corner_radius = 10, dropdown_hover_color = DARK_GREY, width = 210, height = 30, state = "disabled", command = self.choosePlayer)
        self.dropDown.place(relx = 0.4, rely = 0.5, anchor = "w")
        self.dropDown.set("Choose Position")

        self.substitutesFrame = ctk.CTkScrollableFrame(self.substitutionFrame, width = 500, height = 590, fg_color = DARK_GREY, corner_radius = 10)
        self.substitutesFrame.place(relx = 0.33, rely = 0.02, anchor = "nw")

        self.confirmButton = ctk.CTkButton(self.substitutionFrame, text = "Confirm", width = 255, height = 50, font = (APP_FONT, 20), fg_color = APP_BLUE, bg_color = TKINTER_BACKGROUND, corner_radius = 10, command = self.finishSubstitution)
        self.confirmButton.place(relx = 0.33, rely = 0.98, anchor = "sw")

        self.cancelButton = ctk.CTkButton(self.substitutionFrame, text = "Cancel", width = 255, height = 50, font = (APP_FONT, 20), fg_color = CLOSE_RED, bg_color = TKINTER_BACKGROUND, corner_radius = 10, command = self.stopSubstitution)
        self.cancelButton.place(relx = 0.763, rely = 0.98, anchor = "se")

        self.playerStatsFrame = ctk.CTkFrame(self.substitutionFrame, width = 260, height = 670, fg_color = DARK_GREY, corner_radius = 10)
        self.playerStatsFrame.place(relx = 0.99, rely = 0.02, anchor = "ne")

        # Add the lineup on the pitch
        for position, playerID in self.startTeamLineup.items():
            player = Players.get_player_by_id(playerID)
            positionCode = POSITION_CODES[position]

            subbed_on = False
            if player.id in self.startSubs and player.id in self.teamLineup.values():
                subbed_on = True

            if self.injuredPlayer and self.injuredPlayer.id == player.id:
                self.injuredPosition = position
                if self.completedSubs != MAX_SUBS:
                    playerFrame = LineupPlayerFrame(self.lineupPitch,
                                    POSITIONS_PITCH_POSITIONS[position][0],
                                    POSITIONS_PITCH_POSITIONS[position][1],
                                    "center",
                                    INJURY_RED,
                                    65,
                                    65,
                                    playerID,
                                    positionCode,
                                    position,
                                    self.removePlayer,
                                    self.updateLineup,
                                    self.substitutesFrame,
                                    self.swapLineupPositions,
                                    self.caStars[playerID],
                                    xDisabled = True
                                )
                
                    # Check if there are any players available who can play in the injured player's position
                    injured_position_code = POSITION_CODES[self.injuredPosition]

                    # If no subs can play the injured player's position, then the position is free to everyone
                    hasPosssibleSubs = any(
                        injured_position_code in Players.get_player_by_id(player_id).specific_positions.split(",")
                        for player_id in self.teamSubstitutes
                    )

                    if not hasPosssibleSubs:
                        self.freePositions.append(self.injuredPosition) 
                else:
                    self.freePositions.append(self.injuredPosition)
            else:
                playerFrame = LineupPlayerFrame(self.lineupPitch,
                                POSITIONS_PITCH_POSITIONS[position][0],
                                POSITIONS_PITCH_POSITIONS[position][1],
                                "center",
                                GREY_BACKGROUND,
                                65,
                                65,
                                playerID,
                                positionCode,
                                position,
                                self.removePlayer,
                                self.updateLineup,
                                self.substitutesFrame,
                                self.swapLineupPositions,
                                self.caStars[playerID],
                                xDisabled = True
                            )
                
                if subbed_on:
                    playerFrame.showBorder()
            
            if self.injuredPlayer and self.completedSubs != MAX_SUBS:
                self.values.remove(position)
            elif not self.injuredPlayer and position in self.values:
                self.values.remove(position)

        if self.redCardPlayer:
            self.teamSubstitutes.append(self.redCardPlayer.id)
            self.freePositions.append(self.redCardPosition)

        for playerFrame in self.lineupPitch.winfo_children():
            if isinstance(playerFrame, LineupPlayerFrame):
                playerFrame.additionalPositions = self.freePositions.copy()

        self.choosePlayerFrame = ctk.CTkFrame(self, fg_color = GREY_BACKGROUND, width = 400, height = 50, corner_radius = 0, border_color = APP_BLUE, border_width = 2)

        self.backButton = ctk.CTkButton(self.choosePlayerFrame, text = "Back", font = (APP_FONT, 15), fg_color = DARK_GREY, corner_radius = 10, height = 30, width = 100, hover_color = CLOSE_RED, command = self.stopChoosePlayer)
        self.backButton.place(relx = 0.95, rely = 0.5, anchor = "e")

        self.playerDropDown = ctk.CTkComboBox(self.choosePlayerFrame, font = (APP_FONT, 15), fg_color = DARK_GREY, border_color = DARK_GREY, button_color = DARK_GREY, button_hover_color = DARK_GREY, dropdown_fg_color = DARK_GREY, dropdown_hover_color = DARK_GREY, corner_radius = 10, width = 220, height = 30, state = "readonly", command = self.choosePosition)
        self.playerDropDown.place(relx = 0.05, rely = 0.5, anchor = "w")
        self.playerDropDown.set("Choose Player")

        if self.forceSub: 
            if self.completedSubs == MAX_SUBS: # if injury occurs after making all 5 substitutions
                self.forceSub = False

                lineup = self.matchFrame.matchInstance.homeCurrentLineup if self.home else self.matchFrame.matchInstance.awayCurrentLineup
                finalLineup = self.matchFrame.matchInstance.homeFinalLineup if self.home else self.matchFrame.matchInstance.awayFinalLineup
                pitch = self.homeLineupPitch if self.home else self.awayLineupPitch
                playersFrame = self.homePlayersFrame if self.home else self.awayPlayersFrame

                pitch.removePlayer(self.injuredPosition, Players.get_player_by_id(self.injuredPlayer.id).last_name)
                lineup.pop(self.injuredPosition)
                self.teamSubstitutes.append(self.injuredPlayer.id)
                finalLineup.append((self.injuredPosition, self.injuredPlayer.id))

                frame = [f for f in playersFrame.winfo_children() if f.playerID == self.injuredPlayer.id][0]
                frame.removeFitness()

            else:
                self.confirmButton.configure(state = "disabled")
                self.cancelButton.configure(state = "disabled")

        self.addSubstitutePlayers()

        for frame in self.lineupPitch.winfo_children():
            if isinstance(frame, LineupPlayerFrame):
                frame.removeButton.configure(state = "enabled")
    
    def addSubstitutePlayers(self):
        """
        Populate the substitutes frame with the available substitute players.
        """
        
        for widget in self.substitutesFrame.winfo_children():
            widget.destroy()

        ctk.CTkLabel(self.substitutesFrame, text = "Substitutes", font = (APP_FONT_BOLD, 20), fg_color = DARK_GREY).pack(pady = 5)
        self.changesCompletedLabel = ctk.CTkLabel(self.substitutesFrame, text = f"{MAX_SUBS - self.completedSubs - self.currentSubs} changes left", font = (APP_FONT, 17), fg_color = DARK_GREY)
        self.changesCompletedLabel.place(relx = 0.01, rely = 0.005, anchor = "nw")

        players_per_row = 5

        # Define position groups and their display names
        position_groups = [
            ("goalkeeper", "Goalkeepers"),
            ("defender", "Defenders"),
            ("midfielder", "Midfielders"),
            ("forward", "Forwards"),
        ]

        playerIDs = self.teamSubstitutes.copy()
        playersList = [Players.get_player_by_id(pid) for pid in playerIDs]
        playersList.sort(key = lambda x: (POSITION_ORDER.get(x.position, 99), x.last_name))

        for pos_key, heading in position_groups:
            group_players = [p for p in playersList if p.position == pos_key]
            num_players = len(group_players)

            if num_players == 0:
                continue

            frame = ctk.CTkFrame(self.substitutesFrame, fg_color = DARK_GREY, width = 500, height = 100 * max(1, math.ceil(num_players / players_per_row)))
            frame.grid_columnconfigure(players_per_row, weight = 1)
            frame.grid_rowconfigure(1 + math.ceil(num_players / 4), weight = 1)
            ctk.CTkLabel(frame, text = heading, font = (APP_FONT_BOLD, 20), fg_color = DARK_GREY).grid(row = 0, column = 0, padx = 5, pady = 5, sticky = "w", columnspan = 4)

            count = 0
            for player in group_players:

                row = 1 + count // players_per_row
                col = count % players_per_row

                if self.injuredPlayer and player.id == self.injuredPlayer.id:
                    subFrame = SubstitutePlayer(frame, GREY_BACKGROUND, 100, 100, player, self, self.league.id, row, col, self.caStars[player.id], unavailable = True, ingame = True, ingameFunction = self.showPlayerStats)
                    subFrame.showBorder()
                elif self.redCardPlayer and player.id in self.redCardPlayers:
                    subFrame = SubstitutePlayer(frame, GREY_BACKGROUND, 100, 100, player, self, self.league.id, row, col, self.caStars[player.id], unavailable = True, ingame = True, ingameFunction = self.showPlayerStats)
                    subFrame.showBorder()
                else:
                    subFrame = SubstitutePlayer(frame, GREY_BACKGROUND, 100, 100, player, self, self.league.id, row, col, self.caStars[player.id], ingame = True, ingameFunction = self.showPlayerStats)

                if player.id in self.playersOff.values():
                    subFrame.showBorder()

                count += 1

            frame.pack(fill = "x", padx = 10, pady = 5)

    def showPlayerStats(self, player):
        """
        Display the statistics of a selected player in the player stats frame.

        Args:
            player (Player): The player whose statistics are to be displayed.   
        """

        for widget in self.playerStatsFrame.winfo_children():
            widget.destroy()

        ctk.CTkLabel(self.playerStatsFrame, text = f"{player.first_name} {player.last_name}", font = (APP_FONT_BOLD, 23), fg_color = DARK_GREY).place(relx = 0.5, rely = 0.05, anchor = "n")
        ctk.CTkLabel(self.playerStatsFrame, text = f"Last 5 games", font = (APP_FONT, 15), fg_color = DARK_GREY).place(relx = 0.5, rely = 0.1, anchor = "n")

        ctk.CTkLabel(self.playerStatsFrame, text = "Form", font = (APP_FONT_BOLD, 18), fg_color = DARK_GREY).place(relx = 0.05, rely = 0.2, anchor = "w")
        ctk.CTkLabel(self.playerStatsFrame, text = f"Stats", font = (APP_FONT_BOLD, 18), fg_color = DARK_GREY).place(relx = 0.05, rely = 0.48, anchor = "w")

        formFrame = ctk.CTkFrame(self.playerStatsFrame, width = 248, height = 130, fg_color = GREY, corner_radius = 5)
        formFrame.place(relx = 0.02, rely = 0.23, anchor = "nw")

        graph = FormGraph(formFrame, player, 290, 160, 0.02, 0.05, "nw", GREY)
        playerEvents = graph.last5Events
        playerRatings = graph.ratings

        averageRating = round(sum(playerRatings) / len(playerRatings), 2) if playerRatings else 0

        # Mids and Fwds stats
        goals = 0
        assists = 0
        yellowCards = 0
        redCards = 0

        # Gks stats
        cleanSheets = 0
        ownGoals = 0

        # All for a defender

        if len(playerEvents) > 0:
            for match in playerEvents:
                for event in match:
                    if event.event_type == "goal" or event.event_type == "penalty_goal":
                        goals += 1
                    elif event.event_type == "assist":
                        assists += 1
                    elif event.event_type == "yellow_card":
                        yellowCards += 1
                    elif event.event_type == "red_card":
                        redCards += 1
                    elif event.event_type == "own_goal":
                        ownGoals += 1
                    elif event.event_type == "clean_sheet":
                        cleanSheets += 1

            img_relx = 0.05
            relx = 0.15
            rely = 0.53

            if player.position in ["goalkeeper"]:
                src = Image.open("Images/cleanSheet.png")
                src.thumbnail((20, 20))
                img = ctk.CTkImage(src, None, (src.width, src.height))
                ctk.CTkLabel(self.playerStatsFrame, image = img, text = "", fg_color = DARK_GREY).place(relx = img_relx, rely = rely, anchor = "w")
                ctk.CTkLabel(self.playerStatsFrame, text = f"Clean Sheets: {cleanSheets}", font = (APP_FONT, 15), fg_color = DARK_GREY).place(relx = relx, rely = rely, anchor = "w")

                src = Image.open("Images/ownGoal.png")
                src.thumbnail((20, 20))
                img = ctk.CTkImage(src, None, (src.width, src.height))
                ctk.CTkLabel(self.playerStatsFrame, image = img, text = "", fg_color = DARK_GREY).place(relx = img_relx, rely = rely + 0.05, anchor = "w")
                ctk.CTkLabel(self.playerStatsFrame, text = f"Own Goals: {ownGoals}", font = (APP_FONT, 15), fg_color = DARK_GREY).place(relx = relx, rely = rely + 0.05, anchor = "w")

                src = Image.open("Images/averageRating.png")
                src.thumbnail((20, 20))
                img = ctk.CTkImage(src, None, (src.width, src.height))
                ctk.CTkLabel(self.playerStatsFrame, image = img, text = "", fg_color = DARK_GREY).place(relx = img_relx, rely = rely + 0.1, anchor = "w")
                ctk.CTkLabel(self.playerStatsFrame, text = f"Average Rating: {averageRating}", font = (APP_FONT, 15), fg_color = DARK_GREY).place(relx = relx, rely = rely + 0.1, anchor = "w")
            elif player.position in ["midfielder", "forward"]:
                src = Image.open("Images/goal.png")
                src.thumbnail((20, 20))
                img = ctk.CTkImage(src, None, (src.width, src.height))
                ctk.CTkLabel(self.playerStatsFrame, image = img, text = "", fg_color = DARK_GREY).place(relx = img_relx, rely = rely, anchor = "w")
                ctk.CTkLabel(self.playerStatsFrame, text = f"Goals: {goals}", font = (APP_FONT, 15), fg_color = DARK_GREY).place(relx = relx, rely = rely, anchor = "w")

                src = Image.open("Images/assist.png")
                src.thumbnail((20, 20))
                img = ctk.CTkImage(src, None, (src.width, src.height))
                ctk.CTkLabel(self.playerStatsFrame, image = img, text = "", fg_color = DARK_GREY).place(relx = img_relx, rely = rely + 0.05, anchor = "w")
                ctk.CTkLabel(self.playerStatsFrame, text = f"Assists: {assists}", font = (APP_FONT, 15), fg_color = DARK_GREY).place(relx = relx, rely = rely + 0.05, anchor = "w")

                src = Image.open("Images/yellowCard.png")
                src.thumbnail((20, 20))
                img = ctk.CTkImage(src, None, (src.width, src.height))
                ctk.CTkLabel(self.playerStatsFrame, image = img, text = "", fg_color = DARK_GREY).place(relx = img_relx, rely = rely + 0.1, anchor = "w")
                ctk.CTkLabel(self.playerStatsFrame, text = f"Yellow Cards: {yellowCards}", font = (APP_FONT, 15), fg_color = DARK_GREY).place(relx = relx, rely = rely + 0.1, anchor = "w")

                src = Image.open("Images/redCard.png")
                src.thumbnail((20, 20))
                img = ctk.CTkImage(src, None, (src.width, src.height))
                ctk.CTkLabel(self.playerStatsFrame, image = img, text = "", fg_color = DARK_GREY).place(relx = img_relx, rely = rely + 0.15, anchor = "w")
                ctk.CTkLabel(self.playerStatsFrame, text = f"Red Cards: {redCards}", font = (APP_FONT, 15), fg_color = DARK_GREY).place(relx = relx, rely = rely + 0.15, anchor = "w")

                src = Image.open("Images/averageRating.png")
                src.thumbnail((20, 20))
                img = ctk.CTkImage(src, None, (src.width, src.height))
                ctk.CTkLabel(self.playerStatsFrame, image = img, text = "", fg_color = DARK_GREY).place(relx = img_relx, rely = rely + 0.2, anchor = "w")
                ctk.CTkLabel(self.playerStatsFrame, text = f"Average Rating: {averageRating}", font = (APP_FONT, 15), fg_color = DARK_GREY).place(relx = relx, rely = rely + 0.2, anchor = "w")
            else:
                src = Image.open("Images/cleanSheet.png")
                src.thumbnail((20, 20))
                img = ctk.CTkImage(src, None, (src.width, src.height))
                ctk.CTkLabel(self.playerStatsFrame, image = img, text = "", fg_color = DARK_GREY).place(relx = img_relx, rely = rely, anchor = "w")
                ctk.CTkLabel(self.playerStatsFrame, text = f"Clean Sheets: {cleanSheets}", font = (APP_FONT, 15), fg_color = DARK_GREY).place(relx = relx, rely = rely, anchor = "w")

                src = Image.open("Images/ownGoal.png")
                src.thumbnail((20, 20))
                img = ctk.CTkImage(src, None, (src.width, src.height))
                ctk.CTkLabel(self.playerStatsFrame, image = img, text = "", fg_color = DARK_GREY).place(relx = img_relx, rely = rely + 0.05, anchor = "w")
                ctk.CTkLabel(self.playerStatsFrame, text = f"Own Goals: {ownGoals}", font = (APP_FONT, 15), fg_color = DARK_GREY).place(relx = relx, rely = rely + 0.05, anchor = "w")

                src = Image.open("Images/yellowCard.png")
                src.thumbnail((20, 20))
                img = ctk.CTkImage(src, None, (src.width, src.height))
                ctk.CTkLabel(self.playerStatsFrame, image = img, text = "", fg_color = DARK_GREY).place(relx = img_relx, rely = rely + 0.1, anchor = "w")
                ctk.CTkLabel(self.playerStatsFrame, text = f"Yellow Cards: {yellowCards}", font = (APP_FONT, 15), fg_color = DARK_GREY).place(relx = relx, rely = rely + 0.1, anchor = "w")

                src = Image.open("Images/redCard.png")
                src.thumbnail((20, 20))
                img = ctk.CTkImage(src, None, (src.width, src.height))
                ctk.CTkLabel(self.playerStatsFrame, image = img, text = "", fg_color = DARK_GREY).place(relx = img_relx, rely = rely + 0.15, anchor = "w")
                ctk.CTkLabel(self.playerStatsFrame, text = f"Red Cards: {redCards}", font = (APP_FONT, 15), fg_color = DARK_GREY).place(relx = relx, rely = rely + 0.15, anchor = "w")

                src = Image.open("Images/goal.png")
                src.thumbnail((20, 20))
                img = ctk.CTkImage(src, None, (src.width, src.height))
                ctk.CTkLabel(self.playerStatsFrame, image = img, text = "", fg_color = DARK_GREY).place(relx = img_relx, rely = rely + 0.2, anchor = "w")
                ctk.CTkLabel(self.playerStatsFrame, text = f"Goals: {goals}", font = (APP_FONT, 15), fg_color = DARK_GREY).place(relx = relx, rely = rely + 0.2, anchor = "w")

                src = Image.open("Images/assist.png")
                src.thumbnail((20, 20))
                img = ctk.CTkImage(src, None, (src.width, src.height))
                ctk.CTkLabel(self.playerStatsFrame, image = img, text = "", fg_color = DARK_GREY).place(relx = img_relx, rely = rely + 0.25, anchor = "w")
                ctk.CTkLabel(self.playerStatsFrame, text = f"Assists: {assists}", font = (APP_FONT, 15), fg_color = DARK_GREY).place(relx = relx, rely = rely + 0.25, anchor = "w")

                src = Image.open("Images/averageRating.png")
                src.thumbnail((20, 20))
                img = ctk.CTkImage(src, None, (src.width, src.height))
                ctk.CTkLabel(self.playerStatsFrame, image = img, text = "", fg_color = DARK_GREY).place(relx = img_relx, rely = rely + 0.3, anchor = "w")
                ctk.CTkLabel(self.playerStatsFrame, text = f"Average Rating: {averageRating}", font = (APP_FONT, 15), fg_color = DARK_GREY).place(relx = relx, rely = rely + 0.3, anchor = "w")

    def swapLineupPositions(self, position_1, position_2):
        """
        Swap the players in the two given positions in the lineup.

        Args:
            position_1 (str): The first position to swap.
            position_2 (str): The second position to swap.
        """

        temp = self.teamLineup[position_1]
        self.teamLineup[position_1] = self.teamLineup[position_2]
        self.teamLineup[position_2] = temp

    def removePlayer(self, frame, playerName, playerPosition): 
        """
        Remove a player from the lineup and update the substitutes and lineup accordingly.
        
        Args:
            frame (LineupPlayerFrame): The frame of the player to be removed.
            playerName (str): The name of the player to be removed.
            playerPosition (str): The position of the player to be removed.
        """
    
        frame.place_forget()

        playerData = Players.get_player_by_name(playerName.split(" ")[0], playerName.split(" ")[1], self.team.id)
        if playerData.id in self.startTeamLineup.values():
            # If the player was in the lineup, add them to the playersOff
            self.playersOff[playerPosition] = playerData.id
        else:
            # Otherwise, remove from the playersOn
            del self.playersOn[playerPosition]
            self.currentSubs -= 1
        
        # Changes to lists
        self.teamSubstitutes.append(playerData.id)
        self.teamLineup.pop(playerPosition)

        # Reset the substitutes frame
        self.addSubstitutePlayers()

        self.dropDown.configure(state = "readonly")
        new_values = reset_available_positions(self.teamLineup)
        self.dropDown.configure(values = new_values)

        for frame in self.lineupPitch.winfo_children():
            if isinstance(frame, LineupPlayerFrame):
                frame.removeButton.configure(state = "disabled")

        self.confirmButton.configure(state = "disabled")

    def updateLineup(self, player, old_position, new_position):
        """
        Update the lineup when a player is moved to a new position.
        
        Args:
            player (Player): The player being moved.
            old_position (str): The old position of the player.
            new_position (str): The new position of the player.
        """

        if old_position in self.teamLineup:
            del self.teamLineup[old_position]

        self.teamLineup[new_position] = player.id

        new_values = reset_available_positions(self.teamLineup)
        self.dropDown.configure(values = new_values)

    def choosePlayer(self, selected_position):
        """
        Open the choose player frame to allow the user to select a player for the given position.
        
        Args:
            selected_position (str): The position for which a player is to be chosen.
        """
        
        self.selected_position = selected_position
        self.dropDown.configure(state = "disabled")
        self.confirmButton.configure(state = "disabled")

        self.choosePlayerFrame.place(relx = 0.225, rely = 0.5, anchor = "center")

        values = []
        original_positions = {v: k for k, v in self.startTeamLineup.items()}

        for frame in self.substitutesFrame.winfo_children():
            for widget in frame.winfo_children():
                if isinstance(widget, SubstitutePlayer):
                    player = widget.player
                    playerName = player.first_name + " " + player.last_name
                    positions = player.specific_positions
                    
                    # Determine if player is a valid substitution candidate
                    can_substitute = self.currentSubs < MAX_SUBS - self.completedSubs
                    player_in_starting_lineup = player.id in self.startTeamLineup.values()
                    player_on_pitch = player.id in self.teamLineup.values()
                    player_available = not widget.unavailable
                    can_play_selected_position = POSITION_CODES[selected_position] in positions.split(",")

                    started_in_selected_position = (
                        player_in_starting_lineup and
                        original_positions.get(player.id) == selected_position
                    )

                    eligible = False
                    if not can_substitute:
                        if player_in_starting_lineup and not player_on_pitch and player_available:
                            if (
                                (self.freePositions and selected_position in self.freePositions)
                                or can_play_selected_position
                                or started_in_selected_position
                            ):
                                eligible = True
                    else:
                        if not player_on_pitch and player_available:
                            if (
                                (self.freePositions and selected_position in self.freePositions)
                                or can_play_selected_position
                                or started_in_selected_position
                            ):
                                eligible = True

                    if eligible:
                        values.append(playerName)

        if len(values) == 0:
            self.playerDropDown.set("No available players")
            self.playerDropDown.configure(state = "disabled")
        else:
            self.playerDropDown.set("Choose Player")
            self.playerDropDown.configure(values = values)
            self.playerDropDown.configure(state = "normal")

    def stopChoosePlayer(self):
        """
        Close the choose player frame and reset the dropdown and confirm button.
        """
        
        self.choosePlayerFrame.place_forget()
        self.dropDown.configure(state = "normal")
        self.playerDropDown.set("Choose Player")
        self.confirmButton.configure(state = "normal")

    def choosePosition(self, selected_player):
        """
        Add the selected player to the lineup at the selected position.
        
        Args:
            selected_player (str): The name of the player to be added.
        """
        
        self.stopChoosePlayer()

        playerData = Players.get_player_by_name(selected_player.split(" ")[0], selected_player.split(" ")[1], self.team.id)
        if playerData.id in self.startTeamLineup.values():
            # If adding a player that was already in the lineup (before any subs were made), remove from the playersOff
            for position, playerID in list(self.playersOff.items()):
                if playerID == playerData.id:
                    del self.playersOff[position]
                    break

        else:
            # Otherwise, add to the playersOn
            self.playersOn[self.selected_position] = playerData.id
            self.currentSubs += 1

        # Add the player to the lineup
        self.teamLineup[self.selected_position] = playerData.id

        # Remove the player from the substitutes
        for playerID in self.teamSubstitutes:
            if playerID == playerData.id:
                self.teamSubstitutes.remove(playerID)

        # Reset the substitutes frame
        self.addSubstitutePlayers()

        color = GREY_BACKGROUND
        if self.injuredPlayer:
            injured_player_name = self.injuredPlayer.first_name + " " + self.injuredPlayer.last_name
            if selected_player == injured_player_name:
                color = INJURY_RED

        # Create a frame for the player in the lineup pitch
        playerFrame = LineupPlayerFrame(self.lineupPitch, 
                            POSITIONS_PITCH_POSITIONS[self.selected_position][0], 
                            POSITIONS_PITCH_POSITIONS[self.selected_position][1], 
                            "center", 
                            color,
                            65, 
                            65, 
                            playerData.id,
                            POSITION_CODES[self.selected_position],
                            self.selected_position,
                            self.removePlayer,
                            self.updateLineup,
                            self.substitutesFrame,
                            self.swapLineupPositions,
                            self.caStars[playerData.id]
                        )

        if playerData.id in self.playersOn.values():
            playerFrame.showBorder()
        
        # Reset the dropdown
        self.dropDown.configure(state = "disabled")
        new_values = reset_available_positions(self.teamLineup)
        self.dropDown.configure(values = new_values)

        # Reset all the remove buttons in the lineup pitch
        for frame in self.lineupPitch.winfo_children():
            if isinstance(frame, LineupPlayerFrame):
                frame.removeButton.configure(state = "normal")

        if self.forceSub:
            if self.injuredPlayer.id in self.playersOff.values():
                self.confirmButton.configure(state = "normal")
            elif self.injuredPlayer.id not in self.playersOn.values():
                self.confirmButton.configure(state = "disabled")
        else:
            self.confirmButton.configure(state = "normal")

    def finishSubstitution(self):
        """
        Finalize the substitutions made and update the lineup, pitch, and events accordingly.
        """
        
        lineup = self.matchFrame.matchInstance.homeCurrentLineup if self.home else self.matchFrame.matchInstance.awayCurrentLineup
        finalLineup = self.matchFrame.matchInstance.homeFinalLineup if self.home else self.matchFrame.matchInstance.awayFinalLineup
        subs = self.matchFrame.matchInstance.homeCurrentSubs if self.home else self.matchFrame.matchInstance.awayCurrentSubs
        events = self.matchFrame.matchInstance.homeEvents if self.home else self.matchFrame.matchInstance.awayEvents
        pitch = self.homeLineupPitch if self.home else self.awayLineupPitch

        ## Adding / removing players from the lineup and lineup pitch (checking differences between startTeamLineup and teamLineup)
        for position, playerID in list(self.startTeamLineup.items()):
            if position in self.teamLineup:
                newPlayerID = self.teamLineup[position]

                if playerID != newPlayerID:
                    # Case 1: Player swap (position change)
                    if newPlayerID in self.startTeamLineup.values():
                        # Swapping positions
                        oldPosition = [pos for pos, pid in self.startTeamLineup.items() if pid == newPlayerID][0]
                        lineupPlayer = Players.get_player_by_id(newPlayerID)
                        pitch.movePlayer(oldPosition, position, lineupPlayer.last_name)

                        lineup[position] = newPlayerID
                    else:
                        # Case 2: Old player removed, new player added
                        oldPlayer = Players.get_player_by_id(playerID)
                        pitch.removePlayer(position, oldPlayer.last_name)
                        lineup.pop(position)

                        newPlayer = Players.get_player_by_id(newPlayerID)
                        pitch.addPlayer(position, newPlayer.last_name)
                        lineup[position] = newPlayerID
            else:
                # Case 3: Player removed or moved elsewhere
                if playerID in self.teamLineup.values():
                    # Player moved to another position
                    newPosition = [pos for pos, pid in self.teamLineup.items() if pid == playerID][0]
                    lineupPlayer = Players.get_player_by_id(playerID)
                    pitch.movePlayer(position, newPosition, lineupPlayer.last_name)

                    lineup.pop(position)
                    lineup[newPosition] = playerID
                else:
                    # Player taken off the pitch
                    lineupPlayer = Players.get_player_by_id(playerID)
                    pitch.removePlayer(position, lineupPlayer.last_name)
                    lineup.pop(position)

        # Handle brand new players
        for position, playerID in self.teamLineup.items():
            if position not in self.startTeamLineup and playerID not in self.startTeamLineup.values():
                # Case 4: New player added
                player = Players.get_player_by_id(playerID)
                pitch.addPlayer(position, player.last_name)
                lineup[position] = playerID


        if self.currentSubs != 0:
            times = []
            for i in range(1, self.currentSubs + 1):
                currMinute = int(self.timeLabel.cget("text").split(":")[0]) if self.timeLabel.cget("text") != "HT" else 45
                currSeconds = int(self.timeLabel.cget("text").split(":")[1]) if self.timeLabel.cget("text") != "HT" else 0

                if currSeconds + (i * 2) > 60:
                    eventSeconds = (currSeconds + (i * 2)) - 60
                    eventMinute = currMinute + 1
                else:
                    eventSeconds = currSeconds + (i * 2)
                    eventMinute = currMinute

                eventTime = str(eventMinute) + ":" + str(eventSeconds)
                eventTime = self.checkEventTime(events, eventTime)
                eventTime = self.checkEventTime(times, eventTime)
                times.append(eventTime)

                events[eventTime] = {
                    "type": "substitution",
                    "player": None,
                    "player_off": None,
                    "player_on": None,
                    "extra": True if self.halfTime else False
                }

            ## Populating the events with the correct players
            for i, (positionOff, playerOffID) in enumerate(list(self.playersOff.items()), 1):
                event = events[times[i - 1]]
                finalLineup.append((positionOff, playerOffID))
                
                # Find the player in playersOn that suits the position of playerOff the most
                for positionOn, playerOnID in list(self.playersOn.items()):
                    if positionOn == positionOff:
                        self.matchFrame.matchInstance.addPlayerToLineup(playerOnID, playerOffID, positionOn, positionOff, subs, lineup, self, self.home, managing_event = event)
                        del self.playersOn[positionOn]
                        break
                else:
                    # Find the player in playersOn that has the same overall position as playerOff
                    for positionOn, playerOnID in list(self.playersOn.items()):
                        playerOn = Players.get_player_by_id(playerOnID)
                        playerOff = Players.get_player_by_id(playerOffID)
                        if playerOn.position == playerOff.position:
                            self.matchFrame.matchInstance.addPlayerToLineup(playerOnID, playerOffID, positionOn, positionOff, subs, lineup, self, self.home, managing_event = event)
                            del self.playersOn[positionOn]
                            break
                    else:
                        # Use a random player from the playersOn
                        positionOn, playerOnID = random.choice(list(self.playersOn.items()))
                        self.matchFrame.matchInstance.addPlayerToLineup(playerOnID, playerOffID, positionOn, positionOff, subs, lineup, self, self.home, managing_event = event)
                        del self.playersOn[positionOn]

        self.substitutionFrame.place_forget()

        if self.timeLabel.cget("text") != "HT":
            self.resumeMatch()

        self.completedSubs += self.currentSubs
        self.currentSubs = 0

    def stopSubstitution(self):
        """
        Cancel the substitution process and reset the lineup and substitutes.
        """
        
        self.substitutionFrame.place_forget()

        if self.timeLabel.cget("text") != "HT":
            self.resumeMatch()

    def checkEventTime(self, events, time):
        """
        Ensure that the event time is unique by adjusting seconds if necessary.
        
        Args:
            events (dict): The existing events with their times.
            time (str): The proposed time for the new event in "MM:SS" format.
        """
        
        # Check if the time already exists in the events
        while time in events:
            # If it does, increment the seconds by 1 until a unique time is found
            minute, second = map(int, time.split(":"))
            second += 1
            if second >= 60:
                second = 0
                minute += 1
            time = f"{minute}:{second:02d}"
        return time

    def halfTimeTalks(self):
        """
        Display the half-time talks frame with options to resume the game or make substitutions.
        """

        ## Create frames
        self.halfTimeFrame = ctk.CTkFrame(self, width = APP_SIZE[0], height = APP_SIZE[1], fg_color = TKINTER_BACKGROUND)
        self.halfTimeFrame.pack(fill = "both", expand = True)

        self.HTbuttonsFrame = ctk.CTkFrame(self.halfTimeFrame, width = APP_SIZE[0] - 20, height = 120, fg_color = TKINTER_BACKGROUND, corner_radius = 10)
        self.HTbuttonsFrame.place(relx = 0.99, rely = 0.99, anchor = "se")

        self.HTresumeButton = ctk.CTkButton(self.HTbuttonsFrame, text = "Resume Game >>", width = 400, height = 55, font = (APP_FONT, 15), fg_color = APP_BLUE, corner_radius = 10, bg_color = TKINTER_BACKGROUND, command = lambda: self.resumeMatch(halfTime = True))
        self.HTresumeButton.place(relx = 1, rely = 1, anchor = "se")

        self.HTsubsButton = ctk.CTkButton(self.HTbuttonsFrame, text = "Substitutions", width = 400, height = 55, font = (APP_FONT, 15), fg_color = APP_BLUE, corner_radius = 10, bg_color = TKINTER_BACKGROUND, command = self.substitution)
        self.HTsubsButton.place(relx = 1, rely = 0, anchor = "ne")

        self.HTscoreDataFrame = ctk.CTkFrame(self.HTbuttonsFrame, width = 765, height = 120, fg_color = GREY_BACKGROUND, corner_radius = 10)
        self.HTscoreDataFrame.place(relx = 0, rely = 0, anchor = "nw")

        self.HTpromptsFrame = ctk.CTkFrame(self.halfTimeFrame, width = 670, height = 550, fg_color = GREY_BACKGROUND, corner_radius = 10)

        self.HTplayersFrame = ctk.CTkFrame(self.halfTimeFrame, width = 520, height = 550, fg_color = GREY_BACKGROUND, corner_radius = 10)

        ## Half time score data frame
        src = Image.open(io.BytesIO(self.team.logo))
        src.thumbnail((75, 75))
        teamImage = ctk.CTkImage(src, None, (src.width, src.height))

        src = Image.open(io.BytesIO(self.opposition.logo))
        src.thumbnail((75, 75))
        opponentImage = ctk.CTkImage(src, None, (src.width, src.height))
        
        if self.home:
            fontSize = 25 if len(self.team.name) <= 18 else 20
            ctk.CTkLabel(self.HTscoreDataFrame, text = self.team.name, font = (APP_FONT, fontSize), fg_color = GREY_BACKGROUND).place(relx = 0.3, rely = 0.5, anchor = "e")
            ctk.CTkLabel(self.HTscoreDataFrame, text = "", image = teamImage, fg_color = GREY_BACKGROUND).place(relx = 0.4, rely = 0.5, anchor = "e")     
            
            fontSize = 25 if len(self.opposition.name) <= 18 else 20
            ctk.CTkLabel(self.HTscoreDataFrame, text = "", image = opponentImage, fg_color = GREY_BACKGROUND).place(relx = 0.6, rely = 0.5, anchor = "w")     
            ctk.CTkLabel(self.HTscoreDataFrame, text = self.opposition.name, font = (APP_FONT, fontSize), fg_color = GREY_BACKGROUND).place(relx = 0.7, rely = 0.5, anchor = "w")   
        else:
            fontSize = 25 if len(self.opposition.name) <= 18 else 20
            ctk.CTkLabel(self.HTscoreDataFrame, text = self.opposition.name, font = (APP_FONT, fontSize), fg_color = GREY_BACKGROUND).place(relx = 0.3, rely = 0.5, anchor = "e")
            ctk.CTkLabel(self.HTscoreDataFrame, text = "", image = opponentImage, fg_color = GREY_BACKGROUND).place(relx = 0.4, rely = 0.5, anchor = "e")     
            
            fontSize = 25 if len(self.team.name) <= 18 else 20
            ctk.CTkLabel(self.HTscoreDataFrame, text = "", image = teamImage, fg_color = GREY_BACKGROUND).place(relx = 0.6, rely = 0.5, anchor = "w")
            ctk.CTkLabel(self.HTscoreDataFrame, text = self.team.name, font = (APP_FONT, fontSize), fg_color = GREY_BACKGROUND).place(relx = 0.7, rely = 0.5, anchor = "w")   
        
        ctk.CTkLabel(self.HTscoreDataFrame, text = self.matchFrame.score, font = (APP_FONT_BOLD, 30), fg_color = GREY_BACKGROUND).place(relx = 0.5, rely = 0.5, anchor = "center")

        ## Half time players frame
        self.HTplayersFrame.grid_rowconfigure((0, 1, 2, 3, 4), weight = 1)
        self.HTplayersFrame.grid_columnconfigure((0, 1, 2, 3), weight = 1)
        self.HTplayersFrame.grid_propagate(False)

        matchInstance = self.matchFrame.matchInstance
        lineup = matchInstance.homeCurrentLineup if self.home else matchInstance.awayCurrentLineup
        substitutes = matchInstance.homeCurrentSubs if self.home else matchInstance.awayCurrentSubs
        currentEvents = matchInstance.homeProcessedEvents if self.home else matchInstance.awayProcessedEvents

        homeScore = int(self.matchFrame.score.split("-")[0])
        awayScore = int(self.matchFrame.score.split("-")[1])

        row, column = 0, 0
        for _, playerID in lineup.items():
            player = Players.get_player_by_id(playerID)
            frame = ctk.CTkFrame(self.HTplayersFrame, width = 120, height = 100, fg_color = TKINTER_BACKGROUND)
            frame.grid(row = row, column = column, padx = 5, pady = 5)
            ctk.CTkLabel(frame, text = player.first_name, font = (APP_FONT, 12), fg_color = TKINTER_BACKGROUND).place(relx = 0.5, rely = 0.2, anchor = "center")
            ctk.CTkLabel(frame, text = player.last_name,  font = (APP_FONT_BOLD, 15), fg_color = TKINTER_BACKGROUND).place(relx = 0.5, rely = 0.4, anchor = "center")
            
            player_events = [ev for ev in currentEvents.values() if ev["player"] == playerID]
            score = player_reaction(homeScore if self.home else awayScore, awayScore if self.home else homeScore, player_events)

            frame.score = score
            frame.reactionLabel = ctk.CTkLabel(frame, text = get_reaction_text(score), font = (APP_FONT_BOLD, 15), width = 100, height = 35, fg_color = get_reaction_colour(score), corner_radius = 15)
            frame.reactionLabel.place(relx = 0.5, rely = 0.75, anchor = "center")

            column += 1

            if column == 4:
                row += 1
                column = 0

        for playerID in substitutes:
            player = Players.get_player_by_id(playerID)
            frame = ctk.CTkFrame(self.HTplayersFrame, width = 120, height = 100, fg_color = TKINTER_BACKGROUND)
            frame.grid(row = row, column = column, padx = 5, pady = 5)
            ctk.CTkLabel(frame, text = player.first_name, font = (APP_FONT, 12), fg_color = TKINTER_BACKGROUND).place(relx = 0.5, rely = 0.2, anchor = "center")
            ctk.CTkLabel(frame, text = player.last_name,  font = (APP_FONT_BOLD, 15), fg_color = TKINTER_BACKGROUND).place(relx = 0.5, rely = 0.4, anchor = "center")
            
            player_events = [ev for ev in currentEvents.values() if ev["player"] == playerID]
            score = player_reaction(homeScore if self.home else awayScore, awayScore if self.home else homeScore, player_events)

            frame.score = score
            frame.reactionLabel = ctk.CTkLabel(frame, text = get_reaction_text(score), font = (APP_FONT_BOLD, 15), width = 100, height = 35, fg_color = get_reaction_colour(score), corner_radius = 15)
            frame.reactionLabel.place(relx = 0.5, rely = 0.75, anchor = "center")

            column += 1

            if column == 4:
                row += 1
                column = 0

        self.HTplayersFrame.place(relx = 0.99, rely = 0.01, anchor = "ne")

        ## Half time prompts frame
        for prompt, promptTuple in HALF_TIME_PROMPTS.items():

            ctk.CTkLabel(self.HTpromptsFrame, text = prompt, font = (APP_FONT_BOLD, 18), fg_color = GREY_BACKGROUND, width = 50, height = 30).pack(pady = 2, padx = 10, anchor = "w")

            for promptText in promptTuple:
                frame = ctk.CTkFrame(self.HTpromptsFrame, width = 620, height = 30, fg_color = GREY_BACKGROUND, corner_radius = 10)
                frame.pack(padx = (10, 0), anchor = "w")

                ctk.CTkButton(frame, text = promptText, font = (APP_FONT, 15), fg_color = GREY_BACKGROUND, hover_color = DARK_GREY, width = 10, height = 25, command = lambda p = prompt: self.halfTimePrompt(p, matchInstance), anchor = "w").pack()

        self.HTpromptsFrame.place(relx = 0.01, rely = 0.01, anchor = "nw")
        self.HTpromptsFrame.pack_propagate(False)

    def halfTimePrompt(self, prompt, matchInstance):
        """
        Handle the selection of a half-time prompt and update player reactions and potential goals.
        
        Args:
            prompt (str): The selected half-time prompt.
            matchInstance (Match): The current match instance.
        """

        def addGoal(home):
            """
            Add a goal to the match for the specified team (home or away).
            """
            
            events = matchInstance.homeEvents if home else matchInstance.awayEvents
            addEvent = True
            for event_time, event_data in events.items():
                eventMinute = int(event_time.split(":")[0])
                if eventMinute < 55 and eventMinute > 45 and (event_data["type"] == "goal" or event_data["type"] == "penalty_goal" or event_data["type"] == "own_goal") and not event_data["extra"]:
                    addEvent = False
                    break

            if addEvent:
                type_ = random.choices(list(GOAL_TYPE_CHANCES.keys()), weights = [GOAL_TYPE_CHANCES[goalType] for goalType in GOAL_TYPE_CHANCES])[0]
                if type_ == "penalty":
                    type_ = "penalty_goal"

                minute = 45 + random.randint(1, 10)
                second = random.randint(0, 59)

                extra = False
                if minute >= 90:
                    extra = True

                events[str(minute) + ":" + str(second)] = {"type": type_, "extra": extra}
                matchInstance.score.appendScore(1, home)

        homeScore = int(self.matchFrame.score.split("-")[0])
        awayScore = int(self.matchFrame.score.split("-")[1])

        reaction = get_prompt_reaction(prompt, homeScore if self.home else awayScore, awayScore if self.home else homeScore)

        for frame in self.HTplayersFrame.winfo_children():
            frame.score += reaction
            frame.reactionLabel.configure(text = get_reaction_text(frame.score), fg_color = get_reaction_colour(frame.score))

        for frame in self.HTpromptsFrame.winfo_children():
            for child in frame.winfo_children():
                if isinstance(child, ctk.CTkButton):
                    child.configure(state = "disabled")

        if reaction == 1 and random.random() < 0.1:
            addGoal(self.home)
        elif reaction == -1 and random.random() < 0.1:
            addGoal(not self.home)
        elif reaction == -2 and random.random() < 0.25:
            addGoal(not self.home)
    
    def updateTimeLabel(self, minutes, seconds):
        """
        Update the time label with the current match time.
        
        Args:
            minutes (int): The current minutes of the match.
            seconds (int): The current seconds of the match.
        """
        
        self.timeLabel.configure(text = f"{str(minutes).zfill(2)}:{str(seconds).zfill(2)}")

    def updateMatchDataFrame(self, event, time, home = True):
        """
        Update the match data frame with a new event.
        
        Args:
            event (dict): The event data containing type, player IDs, and extra time info.
            time (str): The time of the event in "MM:SS" format.
            home (bool): Whether the event is for the home team or away team.
        """

        frame = ctk.CTkFrame(self.matchDataFrame, width = 370, height = 50, fg_color = TKINTER_BACKGROUND)
        frame.pack(expand = True, fill = "both")

        minute = int(time.split(":")[0]) + 1

        if event["extra"]:
            if minute <= 50:
                extraTime = minute - 45
                minuteText = f"45 + {extraTime}'"
            else:
                extraTime = minute - 90
                minuteText = f"90 + {extraTime}'"
            minuteFont = 13
        else:
            minuteText = str(minute) + "'"
            minuteFont = 15
        
        if event["type"] != "substitution":
            player = Players.get_player_by_id(event["player"])
            text = player.last_name
        else:
            player_off = Players.get_player_by_id(event["player_off"])
            player_on = Players.get_player_by_id(event["player_on"])
            text = player_on.last_name
            subText = player_off.last_name

        if event["type"] == "goal" or event["type"] == "penalty_goal":
            src = Image.open("Images/goal.png")
            srcWB = Image.open("Images/goal_wb.png")
            srcWB2 = Image.open("Images/assist_wb.png") if "assister" in event else None
            subText = Players.get_player_by_id(event["assister"]).last_name if "assister" in event else "Penalty"
        elif event["type"] == "own_goal":
            src = Image.open("Images/ownGoal.png")
            srcWB = Image.open("Images/ownGoal_wb.png")
            subText = "Own Goal"
        elif event["type"] == "yellow_card":
            src = Image.open("Images/yellowCard.png")
            srcWB = Image.open("Images/yellowCard_wb.png")
            subText = "Yellow Card"
        elif event["type"] == "red_card":
            src = Image.open("Images/redCard.png")
            subText = "Red Card"
        elif event["type"] == "penalty_miss":
            src = Image.open("Images/missed_penalty.png")
            srcWB = Image.open("Images/missed_penalty_wb.png")
            srcWB2 = Image.open("Images/saved_penalty_wb.png")
            subText = "Missed Penalty"
        elif event["type"] == "injury":
            src = Image.open("Images/injury.png")
            subText = "Injury"
        elif event["type"] == "substitution":
            if home:
                src = Image.open("Images/substitution_home.png")
            else:
                src = Image.open("Images/substitution_away.png")

            srcWB = Image.open("Images/subbed_on_wb.png")

        src.thumbnail((40, 40))
        image = ctk.CTkImage(src, None, (src.width, src.height))
        
        if home:
            ctk.CTkLabel(frame, text = minuteText, font = (APP_FONT, minuteFont), fg_color = TKINTER_BACKGROUND).place(relx = 0.07, rely = 0.5, anchor = "center")
            ctk.CTkLabel(frame, text = "", image = image, fg_color = TKINTER_BACKGROUND).place(relx = 0.15, rely = 0.5, anchor = "w")
            ctk.CTkLabel(frame, text = text, font = (APP_FONT_BOLD, 18), fg_color = TKINTER_BACKGROUND).place(relx = 0.3, rely = 0.3, anchor = "w")
            ctk.CTkLabel(frame, text = subText, font = (APP_FONT, 12), fg_color = TKINTER_BACKGROUND, height = 10).place(relx = 0.3, rely = 0.7, anchor = "w")
        else:
            ctk.CTkLabel(frame, text = minuteText, font = (APP_FONT, minuteFont), fg_color = TKINTER_BACKGROUND).place(relx = 0.93, rely = 0.5, anchor = "center")
            ctk.CTkLabel(frame, text = "", image = image, fg_color = TKINTER_BACKGROUND).place(relx = 0.85, rely = 0.5, anchor = "e")
            ctk.CTkLabel(frame, text = text, font = (APP_FONT_BOLD, 18), fg_color = TKINTER_BACKGROUND).place(relx = 0.7, rely = 0.3, anchor = "e")
            ctk.CTkLabel(frame, text = subText, font = (APP_FONT, 12), fg_color = TKINTER_BACKGROUND, height = 10).place(relx = 0.7, rely = 0.7, anchor = "e")

        self.matchDataFrame.update_idletasks()
        self.matchDataFrame._parent_canvas.yview_moveto(1)

        if event["type"] != "injury" and event["type"] != "red_card":

            if event["type"] == "own_goal":
                pitch = self.awayLineupPitch if home else self.homeLineupPitch
                lineup = self.matchFrame.matchInstance.awayCurrentLineup if home else self.matchFrame.matchInstance.homeCurrentLineup
            else:
                pitch = self.homeLineupPitch if home else self.awayLineupPitch
                lineup = self.matchFrame.matchInstance.homeCurrentLineup if home else self.matchFrame.matchInstance.awayCurrentLineup
            
            events = self.matchFrame.matchInstance.homeProcessedEvents if home else self.matchFrame.matchInstance.awayProcessedEvents
            playerID = event["player"] if event["type"] != "substitution" else event["player_on"]
            playerData = Players.get_player_by_id(playerID)

            # Find the player (value) position (key) from the lineup
            position = list(lineup.keys())[list(lineup.values()).index(playerID)]

            srcWB.thumbnail((12, 12))
            image = ImageTk.PhotoImage(srcWB)
            num = self.countPlayerEvents(playerID, events, event["type"])
            pitch.addIcon(EVENTS_TO_ICONS[event["type"]], image, position, playerData.last_name, num)

            if event["type"] == "goal":
                playerID = event["assister"]
                playerData = Players.get_player_by_id(playerID)
                position = list(lineup.keys())[list(lineup.values()).index(playerID)]

                srcWB2.thumbnail((12, 12))
                image = ImageTk.PhotoImage(srcWB2)
                num = self.countPlayerEvents(playerID, events, "assister")
                pitch.addIcon(EVENTS_TO_ICONS["assist"], image, position, playerData.last_name, num)
            elif event["type"] == "penalty_miss":
                pitch = self.awayLineupPitch if home else self.homeLineupPitch
                playerID = event["keeper"]
                playerData = Players.get_player_by_id(playerID)

                srcWB2.thumbnail((12, 12))
                image = ImageTk.PhotoImage(srcWB2)
                num = self.countPlayerEvents(playerID, events, event["type"])
                pitch.addIcon(EVENTS_TO_ICONS[event["type"]], image, "Goalkeeper", playerData.last_name, num)

        if event["type"] not in ["injury", "substitution", "red_card"]:

            if event["type"] == "own_goal":
                pitch = self.awayLineupPitch if home else self.homeLineupPitch
                ratings = self.matchFrame.matchInstance.awayRatings if home else self.matchFrame.matchInstance.homeRatings
                lineup = self.matchFrame.matchInstance.awayCurrentLineup if home else self.matchFrame.matchInstance.homeCurrentLineup
            else:
                pitch = self.homeLineupPitch if home else self.awayLineupPitch
                ratings = self.matchFrame.matchInstance.homeRatings if home else self.matchFrame.matchInstance.awayRatings
                lineup = self.matchFrame.matchInstance.homeCurrentLineup if home else self.matchFrame.matchInstance.awayCurrentLineup
                oppLineup = self.matchFrame.matchInstance.awayCurrentLineup if home else self.matchFrame.matchInstance.homeCurrentLineup
                oppRatings = self.matchFrame.matchInstance.awayRatings if home else self.matchFrame.matchInstance.homeRatings
                oppPitch = self.awayLineupPitch if home else self.homeLineupPitch

            self.updateRatingOval(pitch, event["player"], lineup, ratings)

            if event["type"] == "goal":
                self.updateRatingOval(pitch, event["assister"], lineup, ratings)

                for pos, playerID in oppLineup.items():
                    if pos in DEFENDER_POSITIONS + ["Goalkeeper"]:
                        self.updateRatingOval(oppPitch, playerID, oppLineup, oppRatings)

    def updateRatingOval(self, pitch, playerID, lineup, ratings):
        """
        Update the rating oval for a player on the pitch.
        
        Args:
            pitch (LineupPitch): The lineup pitch instance.
            playerID (str): The ID of the player.
            lineup (dict): The current lineup mapping positions to player IDs.
            ratings (dict): The ratings dictionary mapping player IDs to their ratings.
        """
        
        position = list(lineup.keys())[list(lineup.values()).index(playerID)]
        playerData = Players.get_player_by_id(playerID)
        pitch.updateRating(position, playerData.last_name, ratings[playerID])

    def countPlayerEvents(self, player_id, events, event_type):
        """
        Count the number of specific events for a player.
        
        Args:
            player_id (str): The ID of the player.
            events (dict): The events dictionary containing event data.
            event_type (str): The type of event to count.
        """
        
        group = EVENT_GROUPS.get(event_type, [event_type])

        if event_type == "assister":
            return sum(1 for e in events.values() if e.get("assister") == player_id)
        elif event_type == "penalty_miss":
            return sum(
                1
                for e in events.values()
                if e.get("type") == "penalty_miss"
                and (e.get("player") == player_id or e.get("keeper") == player_id)
            )
        else:
            return sum(
                1 for e in events.values()
                if e.get("player") == player_id and e.get("type") in group
            )

    def endSimulation(self):
        """
        Finalize the match simulation, process the results, and update the game state accordingly.
        """

        payload = {
                "team_updates": [],
                "manager_updates": [],
                "match_events": [],
                "player_bans": [],
                "yellow_card_checks": [],
                "score_updates": [],
                "fitness_updates": [],
                "sharpness_updates": [],
                "morale_updates": [],
                "lineup_updates": [],
                "stats_updates": [],
                "news_to_add": [],
            }
        
        payloads = []

        logger = logging.getLogger(__name__)

        logger.debug("Saving data for other matches in the league.")
        for frame in self.otherMatchesFrame.winfo_children():
            if frame.matchInstance:
                payloads.append(frame.matchInstance.saveData())

        logger.debug("Saving data for the managed match.")
        payloads.append(self.matchFrame.matchInstance.saveData(managing_team = "home" if self.home else "away"))

        logger.debug("Combining payloads.")
        for p in payloads:
            for k in payload.keys():
                val = p.get(k)
                if not val:
                    continue
                if isinstance(p[k], list):
                    payload[k].extend(p[k])
                else:
                    payload[k].append(p[k])

        logger.debug("Processing combined payload.")
        process_payload(payload)
        logger.debug("Payload processing complete.")

        ## Post match updates
        logger.debug("Updating team positions.")
        LeagueTeams.update_team_positions(self.league.id)
        currDate = Game.get_game_date(Managers.get_all_user_managers()[0].id)

        logger.debug("Checking if all matches are complete for the matchday.")
        if League.check_all_matches_complete(self.league.id, currDate):
            logger.debug("All matches complete, creating team of the week and team history.")
            _, email = League.team_of_the_week(self.league.id, self.matchFrame.matchInstance.matchday, team = self.homeTeam.id if self.home else self.awayTeam.id)
            logger.debug("Team of the week created.")
            for team in LeagueTeams.get_teams_by_league(self.league.id):
                matchday = League.get_current_matchday(self.league.id)
                TeamHistory.add_team(matchday, team.team_id, team.position, team.points)
            
            if email:
                Emails.add_email("team_of_the_week", self.matchFrame.matchInstance.matchday, None, None, self.league.id, (currDate + timedelta(days = 1)).replace(hour = 8, minute = 0, second = 0, microsecond = 0))

            League.update_current_matchday(self.league.id)

        logger.debug("Checking player game happiness.")
        check_player_games_happy(self.matchFrame.matchInstance.homeTeam.id, currDate)
        check_player_games_happy(self.matchFrame.matchInstance.awayTeam.id, currDate)
        for frame in self.otherMatchesFrame.winfo_children():
            if frame.matchInstance:
                check_player_games_happy(frame.matchInstance.homeTeam.id, currDate)
                check_player_games_happy(frame.matchInstance.awayTeam.id, currDate)

        ## Simulate other leagues' matches in the given interval
        logger.debug("Simulating matches for other leagues.")
        run_match_simulation([currDate, currDate + timedelta(hours = 2)], currDate, exclude_leagues = [self.league.id])
        logger.debug("Match simulation complete.")

        SavedLineups.delete_current_lineup()
        Players.reset_talked_to()

        self.pack_forget()
        self.update_idletasks()
        
        # Force a save of the game.
        try:
            db = DatabaseManager()
            db.commit_copy()
        except Exception as Ex:
            logger = logging.getLogger(__name__)
            logger.exception("Error occurred while saving game: %s", Ex)

        logger.debug("Incrementing game date.")
        Game.increment_game_date(Managers.get_all_user_managers()[0].id, timedelta(hours = 2))
        logger.debug("All done, resetting menu.")
        self.parent.resetMenu()
