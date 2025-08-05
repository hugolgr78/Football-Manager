import customtkinter as ctk
from settings import *
from data.database import *
from data.gamesDatabase import *
from PIL import Image
from utils.util_functions import *
from utils.frames import FootballPitchMatchDay, TeamLogo
from data.database import Teams, MatchEvents
import io
import itertools

class MatchProfile(ctk.CTkFrame):
    def __init__(self, parent, match, parentTab, changeBackFunction = None):
        super().__init__(parent, fg_color = TKINTER_BACKGROUND, width = 1000, height = 700, corner_radius = 0)

        self.match = match
        self.parentTab = parentTab
        self.changeBackFunction = changeBackFunction

        self.homeTeam = Teams.get_team_by_id(match.home_id)
        self.awayTeam = Teams.get_team_by_id(match.away_id)

        ctk.CTkLabel(self, text = f"{self.homeTeam.name} vs {self.awayTeam.name}", font = (APP_FONT_BOLD, 30), fg_color = TKINTER_BACKGROUND, text_color = "white").place(relx = 0.01, rely = 0.05, anchor = "w")

        self.matchResultsFrame = ctk.CTkFrame(self, fg_color = GREY_BACKGROUND, width = 400, height = 625, corner_radius = 10)
        self.matchResultsFrame.place(relx = 0.005, rely = 0.1, anchor = "nw")

        self.matchAddiInfoFrame = ctk.CTkFrame(self, fg_color = GREY_BACKGROUND, width = 580, height = 150, corner_radius = 10)
        self.matchAddiInfoFrame.place(relx = 0.995, rely = 0.99, anchor = "se")

        self.homeLineupPitch = FootballPitchMatchDay(self, 340, 520, 0.553, 0.16, "n", TKINTER_BACKGROUND, GREY_BACKGROUND)
        self.awayLineupPitch = FootballPitchMatchDay(self, 340, 520, 0.855, 0.16, "n", TKINTER_BACKGROUND, GREY_BACKGROUND)

        ctk.CTkLabel(self, text = self.homeTeam.name, font = (APP_FONT_BOLD, 20), fg_color = TKINTER_BACKGROUND, text_color = "white").place(relx = 0.553, rely = 0.11, anchor = "n")
        ctk.CTkLabel(self, text = self.awayTeam.name, font = (APP_FONT_BOLD, 20), fg_color = TKINTER_BACKGROUND, text_color = "white").place(relx = 0.855, rely = 0.11, anchor = "n")

        backButton = ctk.CTkButton(self, text = "Back", font = (APP_FONT, 20), fg_color = TKINTER_BACKGROUND, corner_radius = 5, height = 30, width = 100, hover_color = CLOSE_RED, command = lambda: self.changeBackFunction())
        backButton.place(relx = 0.995, rely = 0.05, anchor = "e")

        self.matchResults()
        self.lineups()
        self.additionalInfo()

    def matchResults(self):
        ctk.CTkCanvas(self.matchResultsFrame, width = 350, height = 5, bg = APP_BLUE, bd = 0, highlightthickness = 0).place(relx = 0.5, rely = 0.38, anchor = "center")

        logosFrame = ctk.CTkFrame(self.matchResultsFrame, fg_color = GREY_BACKGROUND, width = 390, height = 70)
        logosFrame.place(relx = 0.5, rely = 0.02, anchor = "n")

        srcHome = Image.open(io.BytesIO(self.homeTeam.logo))
        srcHome.thumbnail((70, 70))
        homeLogo = TeamLogo(logosFrame, srcHome, self.homeTeam, GREY_BACKGROUND, 0.2, 0.5, "center", self.parentTab)

        srcAway = Image.open(io.BytesIO(self.awayTeam.logo))
        srcAway.thumbnail((70, 70))
        awayLogo = TeamLogo(logosFrame, srcAway, self.awayTeam, GREY_BACKGROUND, 0.8, 0.5, "center", self.parentTab)

        scoreLabel = ctk.CTkLabel(logosFrame, text = f"{self.match.score_home} - {self.match.score_away}", fg_color = GREY_BACKGROUND, font = (APP_FONT_BOLD, 40))
        scoreLabel.place(relx = 0.5, rely = 0.5, anchor = "center")

        self.matchEvents = MatchEvents.get_events_by_match(self.match.id)

        homeGoals = {}
        awayGoals = {}
        homeOwnGoals = {}
        awayOwnGoals = {}
        homeRedCards = {}
        awayRedCards = {}

        maxTimesFirstLine = 3
        maxTimesSubsequentLines = 5

        # Populate the dicts
        for event in self.matchEvents:
            player = Players.get_player_by_id(event.player_id)
            if (event.event_type == "goal" or event.event_type == "penalty_goal") and player.team_id == self.homeTeam.id:
                if player.id not in homeGoals:
                    homeGoals[player.id] = []

                homeGoals[player.id].append(event.time)
            elif (event.event_type == "goal" or event.event_type == "penalty_goal") and player.team_id == self.awayTeam.id:
                if player.id not in awayGoals:
                    awayGoals[player.id] = []

                awayGoals[player.id].append(event.time)
            elif event.event_type == "own_goal" and player.team_id == self.homeTeam.id:
                # Home player scored own goal, so it goes to away team's score
                if player.id not in awayOwnGoals:
                    awayOwnGoals[player.id] = []

                awayOwnGoals[player.id].append(event.time)
            elif event.event_type == "own_goal" and player.team_id == self.awayTeam.id:
                # Away player scored own goal, so it goes to home team's score
                if player.id not in homeOwnGoals:
                    homeOwnGoals[player.id] = []

                homeOwnGoals[player.id].append(event.time)
            elif event.event_type == "red_card" and player.team_id == self.homeTeam.id:
                if player.id not in homeRedCards:
                    homeRedCards[player.id] = []

                homeRedCards[player.id].append(event.time)
            elif event.event_type == "red_card" and player.team_id == self.awayTeam.id:
                if player.id not in awayRedCards:
                    awayRedCards[player.id] = []

                awayRedCards[player.id].append(event.time)

        # Sort the dicts based on time
        homeGoals = {k: v for k, v in sorted(homeGoals.items(), key = lambda item: item[1])}
        awayGoals = {k: v for k, v in sorted(awayGoals.items(), key = lambda item: item[1])}
        homeOwnGoals = {k: v for k, v in sorted(homeOwnGoals.items(), key = lambda item: item[1])}
        awayOwnGoals = {k: v for k, v in sorted(awayOwnGoals.items(), key = lambda item: item[1])}
        homeRedCards = {k: v for k, v in sorted(homeRedCards.items(), key = lambda item: item[1])}
        awayRedCards = {k: v for k, v in sorted(awayRedCards.items(), key = lambda item: item[1])}

        # Combine regular goals and own goals for display
        allHomeGoalPlayers = list(homeGoals.keys()) + list(homeOwnGoals.keys())
        allAwayGoalPlayers = list(awayGoals.keys()) + list(awayOwnGoals.keys())

        # Return if there were no goals or red cards
        if not allHomeGoalPlayers and not allAwayGoalPlayers and not homeRedCards and not awayRedCards:
            return
    
        # Calculate events considering multi-line players count as multiple events
        homeEventCount = 0
        for player in allHomeGoalPlayers:
            if player in homeGoals:
                goalCount = len(homeGoals[player])
                # Regular goals - use normal limits
                maxFirstLine = maxTimesFirstLine
                maxSubsequentLines = maxTimesSubsequentLines
            else:
                # Own goals have times + separate (OG) line
                goalCount = len(homeOwnGoals[player]) + 1  # +1 for the (OG) line
                # Own goals with separate (OG) line - use normal limits
                maxFirstLine = maxTimesFirstLine
                maxSubsequentLines = maxTimesSubsequentLines
            
            # Calculate how many lines this player needs
            if goalCount <= maxFirstLine:
                linesNeeded = 1
            else:
                remainingGoals = goalCount - maxFirstLine
                additionalLines = (remainingGoals + maxSubsequentLines - 1) // maxSubsequentLines
                linesNeeded = 1 + additionalLines
            homeEventCount += linesNeeded
        
        awayEventCount = 0
        for player in allAwayGoalPlayers:
            if player in awayGoals:
                goalCount = len(awayGoals[player])
                # Regular goals - use normal limits
                maxFirstLine = maxTimesFirstLine
                maxSubsequentLines = maxTimesSubsequentLines
            else:
                # Own goals have times + separate (OG) line
                goalCount = len(awayOwnGoals[player]) + 1  # +1 for the (OG) line
                # Own goals with separate (OG) line - use normal limits
                maxFirstLine = maxTimesFirstLine
                maxSubsequentLines = maxTimesSubsequentLines
            
            # Calculate how many lines this player needs
            if goalCount <= maxFirstLine:
                linesNeeded = 1
            else:
                remainingGoals = goalCount - maxFirstLine
                additionalLines = (remainingGoals + maxSubsequentLines - 1) // maxSubsequentLines
                linesNeeded = 1 + additionalLines
            awayEventCount += linesNeeded
        
        maxEvents = max(homeEventCount, awayEventCount, len(homeRedCards) + len(awayRedCards))

        # Use a scrollable frame if there are many events
        if maxEvents > 6:
            scrollableFrame = True
            # Create a container frame to control the exact height
            containerFrame = ctk.CTkFrame(self.matchResultsFrame, fg_color = GREY_BACKGROUND, width = 390, height = 145)
            containerFrame.place(relx = 0.52, rely = 0.26, anchor = "center")
            containerFrame.pack_propagate(False)
            
            # Put the scrollable frame inside the container
            goalsFrame = ctk.CTkScrollableFrame(containerFrame, fg_color = GREY_BACKGROUND, width = 340, height = 100)
            goalsFrame.pack(fill = "both", expand = True, padx = 5, pady = 5)
        else:
            scrollableFrame = False
            goalsFrame = ctk.CTkFrame(self.matchResultsFrame, fg_color = GREY_BACKGROUND, width = 390, height = 145)
            goalsFrame.place(relx = 0.5, rely = 0.26, anchor = "center")
            goalsFrame.pack_propagate(False)

        firstFrameCreated = False
        
        for i, (homePlayer, awayPlayer) in enumerate(itertools.zip_longest(allHomeGoalPlayers, allAwayGoalPlayers)):

            # Determine frame height based on number of goals for both players
            maxLinesNeeded = 1
            homeTimeStrings = []
            awayTimeStrings = []

            # Populate the time strings for each player and get the number of lines needed for the frame
            if homePlayer is not None:
                if homePlayer in homeGoals:
                    homeTimeStrings = [str(time) + "'" for time in homeGoals[homePlayer]]
                else:
                    # Own goals - just add times with apostrophes, (OG) will be on a separate line
                    homeTimeStrings = [str(time) + "'" for time in homeOwnGoals[homePlayer]]
                    # Add (OG) as a separate "time" entry for display
                    homeTimeStrings.append("(OG)")
                
                # Calculate lines needed
                if len(homeTimeStrings) <= maxTimesFirstLine:
                    homeLinesNeeded = 1
                else:
                    remainingGoals = len(homeTimeStrings) - maxTimesFirstLine
                    additionalLines = (remainingGoals + maxTimesSubsequentLines - 1) // maxTimesSubsequentLines
                    homeLinesNeeded = 1 + additionalLines
                maxLinesNeeded = max(maxLinesNeeded, homeLinesNeeded)
            
            if awayPlayer is not None:
                if awayPlayer in awayGoals:
                    awayTimeStrings = [str(time) + "'" for time in awayGoals[awayPlayer]]
                else:
                    # Own goals - just add times with apostrophes, (OG) will be on a separate line
                    awayTimeStrings = [str(time) + "'" for time in awayOwnGoals[awayPlayer]]
                    # Add (OG) as a separate "time" entry for display
                    awayTimeStrings.append("(OG)")
                
                # Calculate lines needed
                if len(awayTimeStrings) <= maxTimesFirstLine:
                    awayLinesNeeded = 1
                else:
                    remainingGoals = len(awayTimeStrings) - maxTimesFirstLine
                    additionalLines = (remainingGoals + maxTimesSubsequentLines - 1) // maxTimesSubsequentLines
                    awayLinesNeeded = 1 + additionalLines
                maxLinesNeeded = max(maxLinesNeeded, awayLinesNeeded)
            
            frameHeight = maxLinesNeeded * 20
            frame = ctk.CTkFrame(goalsFrame, fg_color = GREY_BACKGROUND, width = 350, height = frameHeight)
            frame.pack(fill = "x", padx = 5, pady = (0, 2))

            # Add the strings to the frame
            if homePlayer is not None:
                homePlayerObj = Players.get_player_by_id(homePlayer)
                
                # Split goals using the normal limits
                goalChunks = []
                if len(homeTimeStrings) <= maxTimesFirstLine:
                    goalChunks = [homeTimeStrings]
                else:
                    # First chunk: use maxTimesFirstLine
                    goalChunks.append(homeTimeStrings[:maxTimesFirstLine])
                    # Remaining chunks: use maxTimesSubsequentLines each
                    remaining = homeTimeStrings[maxTimesFirstLine:]
                    for i in range(0, len(remaining), maxTimesSubsequentLines):
                        goalChunks.append(remaining[i:i + maxTimesSubsequentLines])
                
                for lineIndex, chunk in enumerate(goalChunks):
                    if lineIndex == 0:
                        # First line includes player name - handle (OG) separately to avoid comma
                        if "(OG)" in chunk:
                            # Remove (OG) from chunk, join the rest with commas, then add (OG) without comma
                            times = [item for item in chunk if item != "(OG)"]
                            if times:
                                lineText = f"{homePlayerObj.last_name} {', '.join(times)} (OG)"
                            else:
                                lineText = f"{homePlayerObj.last_name} (OG)"
                        else:
                            lineText = f"{homePlayerObj.last_name} {', '.join(chunk)}"
                    else:
                        # Subsequent lines - handle (OG) separately to avoid comma
                        if "(OG)" in chunk:
                            # Remove (OG) from chunk, join the rest with commas, then add (OG) without comma
                            times = [item for item in chunk if item != "(OG)"]
                            if times:
                                lineText = f"{', '.join(times)} (OG)"
                            else:
                                lineText = "(OG)"
                        else:
                            lineText = ', '.join(chunk)
                    
                    # Calculate vertical position for this line
                    relY = (lineIndex + 0.5) / maxLinesNeeded
                    ctk.CTkLabel(frame, text = lineText, fg_color = GREY_BACKGROUND, font = (APP_FONT, 15)).place(relx = 0.45, rely = relY, anchor = "e")

            if awayPlayer is not None:
                awayPlayerObj = Players.get_player_by_id(awayPlayer)
                
                # Split goals using the normal limits
                goalChunks = []
                if len(awayTimeStrings) <= maxTimesFirstLine:
                    goalChunks = [awayTimeStrings]
                else:
                    # First chunk: use maxTimesFirstLine
                    goalChunks.append(awayTimeStrings[:maxTimesFirstLine])
                    # Remaining chunks: use maxTimesSubsequentLines each
                    remaining = awayTimeStrings[maxTimesFirstLine:]
                    for i in range(0, len(remaining), maxTimesSubsequentLines):
                        goalChunks.append(remaining[i:i + maxTimesSubsequentLines])

                for lineIndex, chunk in enumerate(goalChunks):
                    if lineIndex == 0:
                        # First line includes player name - handle (OG) separately to avoid comma
                        if "(OG)" in chunk:
                            # Remove (OG) from chunk, join the rest with commas, then add (OG) without comma
                            times = [item for item in chunk if item != "(OG)"]
                            if times:
                                lineText = f"{awayPlayerObj.last_name} {', '.join(times)} (OG)"
                            else:
                                lineText = f"{awayPlayerObj.last_name} (OG)"
                        else:
                            lineText = f"{awayPlayerObj.last_name} {', '.join(chunk)}"
                    else:
                        # Subsequent lines - handle (OG) separately to avoid comma
                        if "(OG)" in chunk:
                            # Remove (OG) from chunk, join the rest with commas, then add (OG) without comma
                            times = [item for item in chunk if item != "(OG)"]
                            if times:
                                lineText = f"{', '.join(times)} (OG)"
                            else:
                                lineText = "(OG)"
                        else:
                            lineText = ', '.join(chunk)
                    
                    # Calculate vertical position for this line
                    relY = (lineIndex + 0.5) / maxLinesNeeded
                    ctk.CTkLabel(frame, text = lineText, fg_color = GREY_BACKGROUND, font = (APP_FONT, 15)).place(relx = 0.55, rely = relY, anchor = "w")

            # Add goal icon to the first frame only
            if not firstFrameCreated:
                firstFrameCreated = True
                
                src = Image.open("Images/goal.png")
                src.thumbnail((15, 15))
                goalIcon = ctk.CTkImage(src, None, (src.width, src.height))
                ctk.CTkLabel(frame, text = "", image = goalIcon, fg_color = GREY_BACKGROUND).place(x = 190 if not scrollableFrame else 175, y = 10, anchor = "center")

    def lineups(self):
        pass

    def additionalInfo(self):
        pass