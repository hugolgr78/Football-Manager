import customtkinter as ctk
from settings import *
from data.database import *
from data.gamesDatabase import *
from PIL import Image, ImageTk
from utils.util_functions import *
from utils.frames import FootballPitchMatchDay, TeamLogo
from data.database import Teams, MatchEvents, TeamLineup
from utils.refereeProfileLink import RefereeProfileLink
import io

class MatchProfile(ctk.CTkFrame):
    def __init__(self, parent, match, parentTab, changeBackFunction = None):
        """
        Frame showing detailed information about a match, including lineups, events, and statistics.

        Args:
            parent (ctk.CTkFrame): The parent frame.
            match (Match): The match object containing match details.
            parentTab (ctk.CTkFrame): The parent tab frame.
            changeBackFunction (function, optional): Function to call when the back button is pressed. Defaults to None.
        """

        super().__init__(parent, fg_color = TKINTER_BACKGROUND, width = 1000, height = 700, corner_radius = 0)

        self.match = match
        self.parentTab = parentTab
        self.changeBackFunction = changeBackFunction

        self.homeTeam = Teams.get_team_by_id(match.home_id)
        self.awayTeam = Teams.get_team_by_id(match.away_id)
        self.league = League.get_league_by_id(self.match.league_id)

        ctk.CTkLabel(self, text = f"{self.homeTeam.name} vs {self.awayTeam.name}", font = (APP_FONT_BOLD, 30), fg_color = TKINTER_BACKGROUND, text_color = "white").place(relx = 0.01, rely = 0.05, anchor = "w")

        self.matchResultsFrame = ctk.CTkFrame(self, fg_color = GREY_BACKGROUND, width = 400, height = 625, corner_radius = 10)
        self.matchResultsFrame.place(relx = 0.005, rely = 0.1, anchor = "nw")

        self.matchAddiInfoFrame = ctk.CTkFrame(self, fg_color = GREY_BACKGROUND, width = 580, height = 150, corner_radius = 10)
        self.matchAddiInfoFrame.place(relx = 0.995, rely = 0.99, anchor = "se")
        self.matchAddiInfoFrame.pack_propagate(False)

        self.infoFrame = ctk.CTkFrame(self.matchAddiInfoFrame, fg_color = GREY_BACKGROUND, width = 580, height = 150, corner_radius = 10)
        self.infoFrame.place(relx = 0, rely = 0, anchor = "nw")
        self.infoFrame.pack_propagate(False)

        self.statsFrame = ctk.CTkFrame(self.matchAddiInfoFrame, fg_color = GREY_BACKGROUND, width = 580, height = 150, corner_radius = 10)
        self.statsAdded = False

        self.swapDataButton = ctk.CTkButton(self.matchAddiInfoFrame, text = "Stats", font = (APP_FONT, 15), fg_color = DARK_GREY, command = self.swapData, width = 40, height = 10)
        self.swapDataButton.place(relx = 0.99, rely = 0.05, anchor = "ne")

        self.legendFrame = ctk.CTkFrame(self, fg_color = GREY_BACKGROUND, width = 225, height = 150, corner_radius = 0, background_corner_colors = [TKINTER_BACKGROUND, TKINTER_BACKGROUND, GREY_BACKGROUND, GREY_BACKGROUND])

        src = Image.open("Images/information.png")
        src.thumbnail((20, 20))
        img = ctk.CTkImage(src, None, (src.width, src.height))
        self.helpButton = ctk.CTkButton(self, text = "", image = img, fg_color = TKINTER_BACKGROUND, hover_color = TKINTER_BACKGROUND, corner_radius = 5, height = 30, width = 30)
        self.helpButton.place(relx = 0.995, rely = 0.05, anchor = "e")
        self.helpButton.bind("<Enter>", lambda e: self.legendFrame.place(relx = 0.98, rely = 0.05, anchor = "ne"))
        self.helpButton.bind("<Leave>", lambda e: self.legendFrame.place_forget())

        self.homeStartLineupPitch = FootballPitchMatchDay(self, 340, 520, 0.553, 0.16, "n", TKINTER_BACKGROUND, GREY_BACKGROUND)
        self.homeEndLineupPitch = FootballPitchMatchDay(self, 340, 520, 0.553, 0.16, "n", TKINTER_BACKGROUND, GREY_BACKGROUND)
        self.homeEndLineupPitch.removePitch()

        self.changeHomeLineupButton = ctk.CTkButton(self, text = "Start", font = (APP_FONT, 15), text_color = "white", fg_color = DARK_GREY, bg_color = GREY_BACKGROUND, width = 20, hover_color = DARK_GREY, command = lambda: self.changePitch(True))
        self.changeHomeLineupButton.place(relx = 0.686, rely = 0.17, anchor = "ne")

        self.awayStartLineupPitch = FootballPitchMatchDay(self, 340, 520, 0.855, 0.16, "n", TKINTER_BACKGROUND, GREY_BACKGROUND)
        self.awayEndLineupPitch = FootballPitchMatchDay(self, 340, 520, 0.855, 0.16, "n", TKINTER_BACKGROUND, GREY_BACKGROUND)
        self.awayEndLineupPitch.removePitch()

        self.changeAwayLineupButton = ctk.CTkButton(self, text = "Start", font = (APP_FONT, 15), text_color = "white", fg_color = DARK_GREY, bg_color = GREY_BACKGROUND, width = 20, hover_color = DARK_GREY, command = lambda: self.changePitch(False))
        self.changeAwayLineupButton.place(relx = 0.989, rely = 0.17, anchor = "ne")

        ctk.CTkLabel(self, text = self.homeTeam.name, font = (APP_FONT_BOLD, 20), fg_color = TKINTER_BACKGROUND, text_color = "white").place(relx = 0.553, rely = 0.11, anchor = "n")
        ctk.CTkLabel(self, text = self.awayTeam.name, font = (APP_FONT_BOLD, 20), fg_color = TKINTER_BACKGROUND, text_color = "white").place(relx = 0.855, rely = 0.11, anchor = "n")

        backButton = ctk.CTkButton(self, text = "Back", font = (APP_FONT, 20), fg_color = TKINTER_BACKGROUND, corner_radius = 5, height = 30, width = 100, hover_color = CLOSE_RED, command = lambda: self.changeBackFunction())
        backButton.place(relx = 0.96, rely = 0.05, anchor = "e")

        self.matchResults()
        self.lineups()
        self.legend()
        self.additionalInfo()
        self.legendFrame.lift()

    def changePitch(self, home):
        """
        Change the lineup pitch between starting and ending lineups for home or away team.

        Args:
            home (bool): True if changing home team lineup, False if changing away team lineup.
        """

        if home:
            if self.changeHomeLineupButton.cget("text") == "Start":
                self.homeStartLineupPitch.removePitch()
                self.homeEndLineupPitch.placePitch()
                self.changeHomeLineupButton.configure(text = "End")
            else:
                self.homeEndLineupPitch.removePitch()
                self.homeStartLineupPitch.placePitch()
                self.changeHomeLineupButton.configure(text = "Start")
        else:
            if self.changeAwayLineupButton.cget("text") == "Start":
                self.awayStartLineupPitch.removePitch()
                self.awayEndLineupPitch.placePitch()
                self.changeAwayLineupButton.configure(text = "End")
            else:
                self.awayEndLineupPitch.removePitch()
                self.awayStartLineupPitch.placePitch()
                self.changeAwayLineupButton.configure(text = "Start")

    def matchResults(self):
        """
        Display the match results including team logos, score, and match events.
        """

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

        homeGoals = {k: sorted(v, key = sort_time) for k, v in sorted(homeGoals.items(), key = lambda item: sort_time(item[1][0]))}
        awayGoals = {k: sorted(v, key = sort_time) for k, v in sorted(awayGoals.items(), key = lambda item: sort_time(item[1][0]))}
        homeOwnGoals = {k: sorted(v, key = sort_time) for k, v in sorted(homeOwnGoals.items(), key = lambda item: sort_time(item[1][0]))}
        awayOwnGoals = {k: sorted(v, key = sort_time) for k, v in sorted(awayOwnGoals.items(), key = lambda item: sort_time(item[1][0]))}
        homeRedCards = {k: sorted(v, key = sort_time) for k, v in sorted(homeRedCards.items(), key = lambda item: sort_time(item[1][0]))}
        awayRedCards = {k: sorted(v, key = sort_time) for k, v in sorted(awayRedCards.items(), key = lambda item: sort_time(item[1][0]))}

        # Combine all goal players, including own goals and sort
        allHomeGoalPlayers = {}
        for player_id in set(list(homeGoals.keys()) + list(homeOwnGoals.keys())):
            regular_goals = homeGoals.get(player_id, [])
            own_goals = homeOwnGoals.get(player_id, [])
            all_times = regular_goals + own_goals
            if all_times:
                earliest_time = min(all_times, key = sort_time)
                allHomeGoalPlayers[player_id] = earliest_time
        
        allAwayGoalPlayers = {}
        for player_id in set(list(awayGoals.keys()) + list(awayOwnGoals.keys())):
            regular_goals = awayGoals.get(player_id, [])
            own_goals = awayOwnGoals.get(player_id, [])
            all_times = regular_goals + own_goals
            if all_times:
                earliest_time = min(all_times, key = sort_time)
                allAwayGoalPlayers[player_id] = earliest_time
        
        # Sort players by their earliest goal time
        allAwayGoalPlayers = dict(sorted(allAwayGoalPlayers.items(), key = lambda item: sort_time(item[1])))
        allHomeGoalPlayers = dict(sorted(allHomeGoalPlayers.items(), key = lambda item: sort_time(item[1])))
        
        # Convert back to lists for compatibility with existing code
        allHomeGoalPlayers = list(allHomeGoalPlayers.keys())
        allAwayGoalPlayers = list(allAwayGoalPlayers.keys())
    
        # Helper: weight an entry (extra-time entries count as 2, regular as 1, (OG) as 1)
        def entry_weight(entry):
            try:
                if entry == "(OG)":
                    return 1
                if "+" in str(entry):
                    return 2
            except Exception:
                pass
            return 1

        # Pack a list of time entries into chunks using capacities (first line and subsequent lines)
        def pack_weighted(entries, first_cap, subsequent_cap):
            chunks = []
            cap = first_cap
            current = []
            remaining = cap
            for item in entries:
                w = entry_weight(item)
                # If this single item is heavier than the cap, force it into its own line
                if w > cap and not current:
                    chunks.append([item])
                    # after first line, switch to subsequent cap
                    cap = subsequent_cap
                    remaining = cap
                    current = []
                    continue

                if w <= remaining:
                    current.append(item)
                    remaining -= w
                else:
                    # start new chunk
                    chunks.append(current)
                    current = [item]
                    cap = subsequent_cap
                    remaining = cap - w

            if current:
                chunks.append(current)

            return chunks

        # Calculate events considering multi-line players count as multiple events
        homeEventCount = 0
        for player in allHomeGoalPlayers:
            # Build the display entries as they will be shown (times with apostrophes, and (OG) where applicable)
            if player in homeGoals:
                entries = [str(t) + "'" for t in homeGoals[player]]
            else:
                entries = [str(t) + "'" for t in homeOwnGoals[player]]
                entries.append("(OG)")

            # Count weighted entries (each extra-time entry counts as 2)
            goalCount = sum(entry_weight(e) for e in entries)

            # Calculate how many lines this player needs
            if goalCount <= maxTimesFirstLine:
                linesNeeded = 1
            else:
                remainingGoals = goalCount - maxTimesFirstLine
                additionalLines = (remainingGoals + maxTimesSubsequentLines - 1) // maxTimesSubsequentLines
                linesNeeded = 1 + additionalLines

            homeEventCount += linesNeeded

        awayEventCount = 0
        for player in allAwayGoalPlayers:
            if player in awayGoals:
                entries = [str(t) + "'" for t in awayGoals[player]]
            else:
                entries = [str(t) + "'" for t in awayOwnGoals[player]]
                entries.append("(OG)")

            goalCount = sum(entry_weight(e) for e in entries)

            if goalCount <= maxTimesFirstLine:
                linesNeeded = 1
            else:
                remainingGoals = goalCount - maxTimesFirstLine
                additionalLines = (remainingGoals + maxTimesSubsequentLines - 1) // maxTimesSubsequentLines
                linesNeeded = 1 + additionalLines
            awayEventCount += linesNeeded
        
        maxGoalEvents = max(homeEventCount, awayEventCount)
        maxRedCards = max(len(homeRedCards), len(awayRedCards))
        maxEvents = maxGoalEvents + maxRedCards

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

            # Fixed position for scrollable frame
            self.goalsFrameEnd = 0.38
        elif maxEvents > 0:
            scrollableFrame = False
            goalsFrame = ctk.CTkFrame(self.matchResultsFrame, fg_color = GREY_BACKGROUND, width = 390, height = 24.2 * maxEvents)
            goalsFrame.place(relx = 0.5, rely = 0.15, anchor = "n")
            goalsFrame.pack_propagate(False)

            # Calculate position right after the goals frame ends
            self.goalsFrameEnd = 0.15 + (20 * maxEvents) / 625 + 0.02  # start position + frame height + small gap
        else: 
            self.goalsFrameEnd = 0.15 

        # Create main goals frame (packed)
        if allHomeGoalPlayers or allAwayGoalPlayers:
            goalsMainFrame = ctk.CTkFrame(goalsFrame, fg_color = GREY_BACKGROUND, width = 350, height = 20 * max(homeEventCount, awayEventCount))
            goalsMainFrame.pack(fill = "x", padx = 5, pady = (5, 0))
            goalsMainFrame.pack_propagate(False)

            # Create home and away frames within goals frame (placed)
            homeGoalsFrame = ctk.CTkFrame(goalsMainFrame, fg_color = GREY_BACKGROUND, width = 175 if not scrollableFrame else 160, height = 20 * homeEventCount)
            homeGoalsFrame.place(relx = 0, rely = 0, anchor = "nw")
            homeGoalsFrame.pack_propagate(False)

            awayGoalsFrame = ctk.CTkFrame(goalsMainFrame, fg_color = GREY_BACKGROUND, width = 175 if not scrollableFrame else 160, height = 20 * awayEventCount)
            awayGoalsFrame.place(relx = 1, rely = 0, anchor = "ne")
            awayGoalsFrame.pack_propagate(False)

            # Add goal icon (placed)
            src = Image.open("Images/goal.png")
            src.thumbnail((15, 15))
            goalIcon = ctk.CTkImage(src, None, (src.width, src.height))
            ctk.CTkLabel(goalsMainFrame, text = "", image = goalIcon, fg_color = GREY_BACKGROUND).place(relx = 0.5, y = 7, anchor = "center")

            currentHomeY = 7
            currentAwayY = 7

            # Add home team goals
            for player in allHomeGoalPlayers:
                homePlayerObj = Players.get_player_by_id(player)
                
                if player in homeGoals:
                    homeTimeStrings = [str(time) + "'" for time in homeGoals[player]]
                else:
                    # Own goals - just add times with apostrophes, (OG) will be on a separate line
                    homeTimeStrings = [str(time) + "'" for time in homeOwnGoals[player]]
                    # Add (OG) as a separate "time" entry for display
                    homeTimeStrings.append("(OG)")
                
                # Split goals using weighted packing so extra-time entries take 2 slots
                goalChunks = pack_weighted(homeTimeStrings, maxTimesFirstLine, maxTimesSubsequentLines)
                
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
                    
                    ctk.CTkLabel(homeGoalsFrame, text = lineText, fg_color = GREY_BACKGROUND, font = (APP_FONT, 15), height = 20).place(x = 170 if not scrollableFrame else 155, y = currentHomeY, anchor = "e")
                    currentHomeY += 20

            # Add away team goals
            for player in allAwayGoalPlayers:
                awayPlayerObj = Players.get_player_by_id(player)
                
                if player in awayGoals:
                    awayTimeStrings = [str(time) + "'" for time in awayGoals[player]]
                else:
                    # Own goals - just add times with apostrophes, (OG) will be on a separate line
                    awayTimeStrings = [str(time) + "'" for time in awayOwnGoals[player]]
                    # Add (OG) as a separate "time" entry for display
                    awayTimeStrings.append("(OG)")
                
                # Split goals using weighted packing so extra-time entries take 2 slots
                goalChunks = pack_weighted(awayTimeStrings, maxTimesFirstLine, maxTimesSubsequentLines)

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
                    
                    ctk.CTkLabel(awayGoalsFrame, text = lineText, fg_color = GREY_BACKGROUND, font = (APP_FONT, 15), height = 20).place(x = 5, y = currentAwayY, anchor = "w")
                    currentAwayY += 20

        # Create main red cards frame (packed)
        if homeRedCards or awayRedCards:
            redCardsMainFrame = ctk.CTkFrame(goalsFrame, fg_color = GREY_BACKGROUND, width = 350, height = 20 * max(len(homeRedCards), len(awayRedCards)))
            redCardsMainFrame.pack(fill = "x", padx = 5, pady = 0)
            redCardsMainFrame.pack_propagate(False)

            # Create home and away frames within red cards frame (placed)
            homeRedCardsFrame = ctk.CTkFrame(redCardsMainFrame, fg_color = GREY_BACKGROUND, width = 175 if not scrollableFrame else 160, height = 20 * len(homeRedCards))
            homeRedCardsFrame.place(relx = 0, rely = 0, anchor = "nw")
            homeRedCardsFrame.pack_propagate(False)

            awayRedCardsFrame = ctk.CTkFrame(redCardsMainFrame, fg_color = GREY_BACKGROUND, width = 175 if not scrollableFrame else 160, height = 20 * len(awayRedCards))
            awayRedCardsFrame.place(relx = 1, rely = 0, anchor = "ne")
            awayRedCardsFrame.pack_propagate(False)

            # Add red card icon (placed)
            src = Image.open("Images/redCard.png")
            src.thumbnail((15, 15))
            redCardIcon = ctk.CTkImage(src, None, (src.width, src.height))
            ctk.CTkLabel(redCardsMainFrame, text = "", image = redCardIcon, fg_color = GREY_BACKGROUND).place(relx = 0.5, y = 7, anchor = "center")

            currentHomeY = 7
            currentAwayY = 7

            for player in homeRedCards:
                homePlayerObj = Players.get_player_by_id(player)
                redCardTimes = [str(time) + "'" for time in homeRedCards[player]]
                lineText = f"{homePlayerObj.last_name} {', '.join(redCardTimes)}"
                ctk.CTkLabel(homeRedCardsFrame, text = lineText, fg_color = GREY_BACKGROUND, font = (APP_FONT, 15), height = 20).place(x = 170 if not scrollableFrame else 155, y = currentHomeY, anchor = "e")
                currentHomeY += 20

            for player in awayRedCards:
                awayPlayerObj = Players.get_player_by_id(player)
                redCardTimes = [str(time) + "'" for time in awayRedCards[player]]
                lineText = f"{awayPlayerObj.last_name} {', '.join(redCardTimes)}"
                ctk.CTkLabel(awayRedCardsFrame, text = lineText, fg_color = GREY_BACKGROUND, font = (APP_FONT, 15), height = 20).place(x = 5, y = currentAwayY, anchor = "w")
                currentAwayY += 20

        ctk.CTkCanvas(self.matchResultsFrame, width = 350, height = 5, bg = APP_BLUE, bd = 0, highlightthickness = 0).place(relx = 0.5, rely = self.goalsFrameEnd, anchor = "center")

        height = 350 + (24.2 * (6 - min(6, maxEvents)))

        self.addMatchEvents(height)

    def addMatchEvents(self, height):
        """
        Add detailed match events to the match results frame.
        
        Args:
            height (int): The height of the match events frame.
        """

        maxFrames = height // 50
        eventsCount = 2 # Start at 2 to account for the half time and full time frames

        for event in self.matchEvents:
            if event.event_type == "sub_on" or event.event_type == "assist" or event.event_type == "clean_sheet":
                continue
            eventsCount += 1

        if eventsCount > maxFrames:
            self.matchEventsFrame = ctk.CTkScrollableFrame(self.matchResultsFrame, fg_color = GREY_BACKGROUND, width = 374, height = height)
            self.matchEventsFrame.place(relx = 0.5, rely = self.goalsFrameEnd + 0.01, anchor = "n")
            frameWidth = 374
        else:
            self.matchEventsFrame = ctk.CTkFrame(self.matchResultsFrame, fg_color = GREY_BACKGROUND, width = 374, height = height)
            self.matchEventsFrame.place(relx = 0.5, rely = self.goalsFrameEnd + 0.02, anchor = "n")
            frameWidth = 400
        
        self.matchEvents.sort(key = lambda x: sort_time(x.time))

        halfTimeAdded = False
        for event in self.matchEvents:
            
            if event.event_type == "sub_on" or event.event_type == "assist" or event.event_type == "clean_sheet" or event.event_type == "penalty_saved":
                continue

            frame = ctk.CTkFrame(self.matchEventsFrame, fg_color = GREY_BACKGROUND, width = frameWidth, height = 50)
            frame.pack(expand = True)

            player = Players.get_player_by_id(event.player_id)

            time = event.time

            if "+" not in time and int(time) > 45 and not halfTimeAdded:
                ctk.CTkLabel(frame, text = "------------------ Half Time ------------------", font = (APP_FONT, 15), fg_color = GREY_BACKGROUND).place(relx = 0.5, rely = 0.5, anchor = "center")
                halfTimeAdded = True

                frame = ctk.CTkFrame(self.matchEventsFrame, fg_color = GREY_BACKGROUND, width = frameWidth, height = 50)
                frame.pack(expand = True)

            if "+" in time:
                minuteFont = 13
            else:
                minuteFont = 15

            if player.team_id == self.homeTeam.id:
                homePlayer = True
            else:
                homePlayer = False

            if event.event_type != "sub_off":

                text = player.last_name

                if event.event_type == "goal" or event.event_type == "penalty_goal":
                    src = Image.open("Images/goal.png")

                    assist_event = None
                    for event2 in self.matchEvents:
                        if event2.event_type == "assist" and event2.time == time and event2.player_id != player.id:
                            assist_event = event2
                            break   
                        
                    subText = Players.get_player_by_id(assist_event.player_id).last_name if assist_event else "Penalty"
                elif event.event_type == "own_goal":
                    src = Image.open("Images/ownGoal.png")
                    subText = "Own Goal"
                    homePlayer = not homePlayer  # Own goal is credited to the opposing team
                elif event.event_type == "yellow_card":
                    src = Image.open("Images/yellowCard.png")
                    subText = "Yellow Card"
                elif event.event_type == "red_card":
                    src = Image.open("Images/redCard.png")
                    subText = "Red Card"
                elif event.event_type == "penalty_miss":
                    src = Image.open("Images/missed_penalty.png")
                    subText = "Missed Penalty"
                elif event.event_type == "injury":
                    src = Image.open("Images/injury.png")
                    subText = "Injury"
            else:
                # Sub on event is the next event in the list
                sub_on_event = self.matchEvents[self.matchEvents.index(event) + 1] if self.matchEvents.index(event) + 1 < len(self.matchEvents) else None
                player_on = Players.get_player_by_id(sub_on_event.player_id) if sub_on_event else None

                text = player_on.last_name if player_on else "Unknown"
                subText = player.last_name

                if homePlayer:
                    src = Image.open("Images/substitution_home.png")
                else:
                    src = Image.open("Images/substitution_away.png")

            src.thumbnail((40, 40))
            image = ctk.CTkImage(src, None, (src.width, src.height))
            
            if homePlayer:
                ctk.CTkLabel(frame, text = f"{event.time}'", font = (APP_FONT, minuteFont), fg_color = GREY_BACKGROUND).place(relx = 0.07, rely = 0.5, anchor = "center")
                ctk.CTkLabel(frame, text = "", image = image, fg_color = GREY_BACKGROUND).place(relx = 0.15, rely = 0.5, anchor = "w")
                ctk.CTkLabel(frame, text = text, font = (APP_FONT_BOLD, 18), fg_color = GREY_BACKGROUND).place(relx = 0.3, rely = 0.3, anchor = "w")
                ctk.CTkLabel(frame, text = subText, font = (APP_FONT, 12), fg_color = GREY_BACKGROUND, height = 10).place(relx = 0.3, rely = 0.7, anchor = "w")
            else:
                ctk.CTkLabel(frame, text = f"{event.time}'", font = (APP_FONT, minuteFont), fg_color = GREY_BACKGROUND).place(relx = 0.93, rely = 0.5, anchor = "center")
                ctk.CTkLabel(frame, text = "", image = image, fg_color = GREY_BACKGROUND).place(relx = 0.85, rely = 0.5, anchor = "e")
                ctk.CTkLabel(frame, text = text, font = (APP_FONT_BOLD, 18), fg_color = GREY_BACKGROUND).place(relx = 0.7, rely = 0.3, anchor = "e")
                ctk.CTkLabel(frame, text = subText, font = (APP_FONT, 12), fg_color = GREY_BACKGROUND, height = 10).place(relx = 0.7, rely = 0.7, anchor = "e")

        frame = ctk.CTkFrame(self.matchEventsFrame, fg_color = GREY_BACKGROUND, width = frameWidth, height = 50)
        frame.pack(expand = True, fill = "both")

        ctk.CTkLabel(frame, text = "------------------ Full Time ------------------", font = (APP_FONT, 15), fg_color = GREY_BACKGROUND).place(relx = 0.5, rely = 0.5, anchor = "center")

    def lineups(self):
        """
        Display the lineups for both teams, including player positions and events.
        """
        
        self.homeLineup = TeamLineup.get_lineup_by_match_and_team(self.match.id, self.homeTeam.id)
        self.awayLineup = TeamLineup.get_lineup_by_match_and_team(self.match.id, self.awayTeam.id)

        self.homeEvents = [event for event in self.matchEvents if Players.get_player_by_id(event.player_id).team_id == self.homeTeam.id]
        self.awayEvents = [event for event in self.matchEvents if Players.get_player_by_id(event.player_id).team_id == self.awayTeam.id]

        self.imageSize = (12, 12)

        self.potm = TeamLineup.get_player_OTM(self.match.id)

        def has_event(player_id, event_type, events_list):
            return any(event.player_id == player_id and event.event_type == event_type for event in events_list)

        for player in self.homeLineup:
            playerData = Players.get_player_by_id(player.player_id)

            pitch = "Start"

            subbed_on = has_event(player.player_id, "sub_on", self.homeEvents)
            subbed_off = has_event(player.player_id, "sub_off", self.homeEvents)
            red_carded = has_event(player.player_id, "red_card", self.homeEvents)
            yellow_carded = has_event(player.player_id, "yellow_card", self.homeEvents)
            injured = has_event(player.player_id, "injury", self.homeEvents)

            numGoals = len([event for event in self.homeEvents if event.player_id == player.player_id and (event.event_type == "goal" or event.event_type == "penalty_goal")])
            numOwnGoals = len([event for event in self.homeEvents if event.player_id == player.player_id and event.event_type == "own_goal"])
            numPenaltiesMissed = len([event for event in self.homeEvents if event.player_id == player.player_id and event.event_type == "penalty_miss"])
            numAssists = len([event for event in self.homeEvents if event.player_id == player.player_id and event.event_type == "assist"])
            numPenaltiesSaved = len([event for event in self.homeEvents if event.player_id == player.player_id and event.event_type == "penalty_saved"])

            if (subbed_on and subbed_off) or (not player.start_position and not player.end_position):
                continue 
            
            if not subbed_on:
                # Starting player → always show in start lineup
                self.homeStartLineupPitch.addPlayer(player.start_position, playerData.last_name)
                
                # Also show in end lineup if they finished the match (not subbed off and not red carded)
                if not subbed_off and not red_carded and not injured:
                    self.homeEndLineupPitch.addPlayer(player.end_position, playerData.last_name)
                    pitch = "Both"
            else:
                # Substitute player → only show in end lineup if they weren't red carded
                if not red_carded:
                    self.homeEndLineupPitch.addPlayer(player.end_position, playerData.last_name)
                    pitch = "End"

            # Add events icons and ratings
            if subbed_off:
                src = Image.open("Images/subbed_off_wb.png")
                src.thumbnail(self.imageSize)
                img = ImageTk.PhotoImage(src)
                self.homeStartLineupPitch.addIcon("Sub", img, player.start_position, playerData.last_name, 1)
            elif subbed_on:
                src = Image.open("Images/subbed_on_wb.png")
                src.thumbnail(self.imageSize)
                img = ImageTk.PhotoImage(src)

                # Check the player finished the game
                if player.end_position:
                    self.homeEndLineupPitch.addIcon("Sub", img, player.end_position, playerData.last_name, 1)
            
            if yellow_carded and red_carded:
                src = Image.open("Images/yellowCard_wb.png")
                src.thumbnail(self.imageSize)
                img = ImageTk.PhotoImage(src)

                src = Image.open("Images/redCard_wb.png")
                src.thumbnail(self.imageSize)
                img2 = ImageTk.PhotoImage(src)

                if pitch == "Start":
                    self.homeStartLineupPitch.addIcon("Cards", img, player.start_position, playerData.last_name, 1)
                    self.homeStartLineupPitch.addIcon("Cards", img2, player.start_position, playerData.last_name, 2)
                elif pitch == "End":
                    self.homeEndLineupPitch.addIcon("Cards", img, player.end_position, playerData.last_name, 1)
                    self.homeEndLineupPitch.addIcon("Cards", img2, player.end_position, playerData.last_name, 2)
            elif yellow_carded:
                src = Image.open("Images/yellowCard_wb.png")
                src.thumbnail(self.imageSize)
                img = ImageTk.PhotoImage(src)

                if pitch == "Start":
                    self.homeStartLineupPitch.addIcon("Cards", img, player.start_position, playerData.last_name, 1)
                elif pitch == "End":
                    self.homeEndLineupPitch.addIcon("Cards", img, player.end_position, playerData.last_name, 1)
                else:
                    self.homeStartLineupPitch.addIcon("Cards", img, player.start_position, playerData.last_name, 1)
                    self.homeEndLineupPitch.addIcon("Cards", img, player.end_position, playerData.last_name, 1)
            elif red_carded:
                src = Image.open("Images/redCard_wb.png")
                src.thumbnail(self.imageSize)
                img = ImageTk.PhotoImage(src)

                if pitch == "Start":
                    self.homeStartLineupPitch.addIcon("Cards", img, player.start_position, playerData.last_name, 1)
                elif pitch == "End":
                    self.homeEndLineupPitch.addIcon("Cards", img, player.end_position, playerData.last_name, 1)

            for i in range(numGoals):
                src = Image.open("Images/goal_wb.png")
                src.thumbnail(self.imageSize)
                img = ImageTk.PhotoImage(src)

                if pitch == "Start":
                    self.homeStartLineupPitch.addIcon("Goals", img, player.start_position, playerData.last_name, i + 1)
                elif pitch == "End":
                    self.homeEndLineupPitch.addIcon("Goals", img, player.end_position, playerData.last_name, i + 1)
                else:
                    self.homeStartLineupPitch.addIcon("Goals", img, player.start_position, playerData.last_name, i + 1)
                    self.homeEndLineupPitch.addIcon("Goals", img, player.end_position, playerData.last_name, i + 1)

            count = numGoals
            for i in range(count, numOwnGoals + count):
                src = Image.open("Images/ownGoal_wb.png")
                src.thumbnail(self.imageSize)
                img = ImageTk.PhotoImage(src)

                if pitch == "Start":
                    self.homeStartLineupPitch.addIcon("Goals", img, player.start_position, playerData.last_name, i + 1)
                elif pitch == "End":
                    self.homeEndLineupPitch.addIcon("Goals", img, player.end_position, playerData.last_name, i + 1)
                else:
                    self.homeStartLineupPitch.addIcon("Goals", img, player.start_position, playerData.last_name, i + 1)
                    self.homeEndLineupPitch.addIcon("Goals", img, player.end_position, playerData.last_name, i + 1)

            count = numGoals + numOwnGoals
            for i in range(count, count + numPenaltiesSaved):
                src = Image.open("Images/saved_penalty_wb.png")
                src.thumbnail(self.imageSize)
                img = ImageTk.PhotoImage(src)

                if pitch == "Start":
                    self.homeStartLineupPitch.addIcon("Goals", img, player.start_position, playerData.last_name, i + 1)
                elif pitch == "End":
                    self.homeEndLineupPitch.addIcon("Goals", img, player.end_position, playerData.last_name, i + 1)
                else:
                    self.homeStartLineupPitch.addIcon("Goals", img, player.start_position, playerData.last_name, i + 1)
                    self.homeEndLineupPitch.addIcon("Goals", img, player.end_position, playerData.last_name, i + 1)

            for i in range(numPenaltiesMissed):
                src = Image.open("Images/missed_penalty_wb.png")
                src.thumbnail(self.imageSize)
                img = ImageTk.PhotoImage(src)

                if pitch == "Start":
                    self.homeStartLineupPitch.addIcon("Missed Pens", img, player.start_position, playerData.last_name, i + 1)
                elif pitch == "End":
                    self.homeEndLineupPitch.addIcon("Missed Pens", img, player.end_position, playerData.last_name, i + 1)
                else:
                    self.homeStartLineupPitch.addIcon("Missed Pens", img, player.start_position, playerData.last_name, i + 1)
                    self.homeEndLineupPitch.addIcon("Missed Pens", img, player.end_position, playerData.last_name, i + 1)

            for i in range(numAssists):
                src = Image.open("Images/assist_wb.png")
                src.thumbnail(self.imageSize)
                img = ImageTk.PhotoImage(src)

                if pitch == "Start":
                    self.homeStartLineupPitch.addIcon("Assists", img, player.start_position, playerData.last_name, i + 1)
                elif pitch == "End":
                    self.homeEndLineupPitch.addIcon("Assists", img, player.end_position, playerData.last_name, i + 1)
                else:
                    self.homeStartLineupPitch.addIcon("Assists", img, player.start_position, playerData.last_name, i + 1)
                    self.homeEndLineupPitch.addIcon("Assists", img, player.end_position, playerData.last_name, i + 1)

            playerRating = player.rating
            if pitch == "Start":
                self.homeStartLineupPitch.addRating(player.start_position, playerData.last_name, playerRating, True if player.id == self.potm.id else False)
            elif pitch == "End":
                self.homeEndLineupPitch.addRating(player.end_position, playerData.last_name, playerRating, True if player.id == self.potm.id else False)
            else:
                self.homeStartLineupPitch.addRating(player.start_position, playerData.last_name, playerRating, True if player.id == self.potm.id else False)
                self.homeEndLineupPitch.addRating(player.end_position, playerData.last_name, playerRating, True if player.id == self.potm.id else False)

            if injured:
                src = Image.open("Images/injury.png")
                src.thumbnail((10, 10))
                img = ImageTk.PhotoImage(src)

                if pitch == "Start":
                    self.homeStartLineupPitch.addInjuryIcon(player.start_position, playerData.last_name, img)
                elif pitch == "End":
                    self.homeEndLineupPitch.addInjuryIcon(player.end_position, playerData.last_name, img)
                else:
                    self.homeStartLineupPitch.addInjuryIcon(player.start_position, playerData.last_name, img)
                    self.homeEndLineupPitch.addInjuryIcon(player.end_position, playerData.last_name, img)

        for player in self.awayLineup:
            playerData = Players.get_player_by_id(player.player_id)

            pitch = "Start"

            subbed_on = has_event(player.player_id, "sub_on", self.awayEvents)
            subbed_off = has_event(player.player_id, "sub_off", self.awayEvents)
            red_carded = has_event(player.player_id, "red_card", self.awayEvents)
            yellow_carded = has_event(player.player_id, "yellow_card", self.awayEvents)
            injured = has_event(player.player_id, "injury", self.awayEvents)

            numGoals = len([event for event in self.awayEvents if event.player_id == player.player_id and (event.event_type == "goal" or event.event_type == "penalty_goal")])
            numOwnGoals = len([event for event in self.awayEvents if event.player_id == player.player_id and event.event_type == "own_goal"])
            numPenaltiesMissed = len([event for event in self.awayEvents if event.player_id == player.player_id and event.event_type == "penalty_miss"])
            numAssists = len([event for event in self.awayEvents if event.player_id == player.player_id and event.event_type == "assist"])
            numPenaltiesSaved = len([event for event in self.awayEvents if event.player_id == player.player_id and event.event_type == "penalty_saved"])

            if (subbed_on and subbed_off) or (not player.start_position and not player.end_position):
                continue
        
            if not subbed_on:
                # Starting player → always show in start lineup
                self.awayStartLineupPitch.addPlayer(player.start_position, playerData.last_name)

                # Also show in end lineup if they finished the match (not subbed off and not red carded)
                if not subbed_off and not red_carded and not injured:
                    self.awayEndLineupPitch.addPlayer(player.end_position, playerData.last_name)
                    pitch = "Both"
            else:
                # Substitute player → only show in end lineup if they weren't red carded
                if not red_carded:
                    self.awayEndLineupPitch.addPlayer(player.end_position, playerData.last_name)
                    pitch = "End"

            # Add events icons and ratings
            if subbed_off:
                src = Image.open("Images/subbed_off_wb.png")
                src.thumbnail(self.imageSize)
                img = ImageTk.PhotoImage(src)
                self.awayStartLineupPitch.addIcon("Sub", img, player.start_position, playerData.last_name, 1)
            elif subbed_on:
                src = Image.open("Images/subbed_on_wb.png")
                src.thumbnail(self.imageSize)
                img = ImageTk.PhotoImage(src)
                self.awayEndLineupPitch.addIcon("Sub", img, player.end_position, playerData.last_name, 1)
            
            if yellow_carded and red_carded:
                src = Image.open("Images/yellowCard_wb.png")
                src.thumbnail(self.imageSize)
                img = ImageTk.PhotoImage(src)

                src = Image.open("Images/redCard_wb.png")
                src.thumbnail(self.imageSize)
                img2 = ImageTk.PhotoImage(src)

                if pitch == "Start":
                    self.awayStartLineupPitch.addIcon("Cards", img, player.start_position, playerData.last_name, 1)
                    self.awayStartLineupPitch.addIcon("Cards", img2, player.start_position, playerData.last_name, 2)
                elif pitch == "End":
                    self.awayEndLineupPitch.addIcon("Cards", img, player.end_position, playerData.last_name, 1)
                    self.awayEndLineupPitch.addIcon("Cards", img2, player.end_position, playerData.last_name, 2)
            elif yellow_carded:
                src = Image.open("Images/yellowCard_wb.png")
                src.thumbnail(self.imageSize)
                img = ImageTk.PhotoImage(src)

                if pitch == "Start":
                    self.awayStartLineupPitch.addIcon("Cards", img, player.start_position, playerData.last_name, 1)
                elif pitch == "End":
                    self.awayEndLineupPitch.addIcon("Cards", img, player.end_position, playerData.last_name, 1)
                else:
                    self.awayStartLineupPitch.addIcon("Cards", img, player.start_position, playerData.last_name, 1)
                    self.awayEndLineupPitch.addIcon("Cards", img, player.end_position, playerData.last_name, 1)
            elif red_carded:
                src = Image.open("Images/redCard_wb.png")
                src.thumbnail(self.imageSize)
                img = ImageTk.PhotoImage(src)

                if pitch == "Start":
                    self.awayStartLineupPitch.addIcon("Cards", img, player.start_position, playerData.last_name, 1)
                elif pitch == "End":
                    self.awayEndLineupPitch.addIcon("Cards", img, player.end_position, playerData.last_name, 1)

            for i in range(numGoals):
                src = Image.open("Images/goal_wb.png")
                src.thumbnail(self.imageSize)
                img = ImageTk.PhotoImage(src)

                if pitch == "Start":
                    self.awayStartLineupPitch.addIcon("Goals", img, player.start_position, playerData.last_name, i + 1)
                elif pitch == "End":
                    self.awayEndLineupPitch.addIcon("Goals", img, player.end_position, playerData.last_name, i + 1)
                else:
                    self.awayStartLineupPitch.addIcon("Goals", img, player.start_position, playerData.last_name, i + 1)
                    self.awayEndLineupPitch.addIcon("Goals", img, player.end_position, playerData.last_name, i + 1)

            count = numGoals
            for i in range(count, numOwnGoals + count):
                src = Image.open("Images/ownGoal_wb.png")
                src.thumbnail(self.imageSize)
                img = ImageTk.PhotoImage(src)

                if pitch == "Start":
                    self.awayStartLineupPitch.addIcon("Goals", img, player.start_position, playerData.last_name, i + 1)
                elif pitch == "End":
                    self.awayEndLineupPitch.addIcon("Goals", img, player.end_position, playerData.last_name, i + 1)
                else:
                    self.awayStartLineupPitch.addIcon("Goals", img, player.start_position, playerData.last_name, i + 1)
                    self.awayEndLineupPitch.addIcon("Goals", img, player.end_position, playerData.last_name, i + 1)

            count = numGoals + numOwnGoals
            for i in range(count, count + numPenaltiesSaved):
                src = Image.open("Images/saved_penalty_wb.png")
                src.thumbnail(self.imageSize)
                img = ImageTk.PhotoImage(src)

                if pitch == "Start":
                    self.awayStartLineupPitch.addIcon("Goals", img, player.start_position, playerData.last_name, i + 1)
                elif pitch == "End":
                    self.awayEndLineupPitch.addIcon("Goals", img, player.end_position, playerData.last_name, i + 1)
                else:
                    self.awayStartLineupPitch.addIcon("Goals", img, player.start_position, playerData.last_name, i + 1)
                    self.awayEndLineupPitch.addIcon("Goals", img, player.end_position, playerData.last_name, i + 1)

            for i in range(numPenaltiesMissed):
                src = Image.open("Images/missed_penalty_wb.png")
                src.thumbnail(self.imageSize)
                img = ImageTk.PhotoImage(src)

                if pitch == "Start":
                    self.awayStartLineupPitch.addIcon("Missed Pens", img, player.start_position, playerData.last_name, i + 1)
                elif pitch == "End":
                    self.awayEndLineupPitch.addIcon("Missed Pens", img, player.end_position, playerData.last_name, i + 1)
                else:
                    self.awayStartLineupPitch.addIcon("Missed Pens", img, player.start_position, playerData.last_name, i + 1)
                    self.awayEndLineupPitch.addIcon("Missed Pens", img, player.end_position, playerData.last_name, i + 1)

            for i in range(numAssists):
                src = Image.open("Images/assist_wb.png")
                src.thumbnail(self.imageSize)
                img = ImageTk.PhotoImage(src)

                if pitch == "Start":
                    self.awayStartLineupPitch.addIcon("Assists", img, player.start_position, playerData.last_name, i + 1)
                elif pitch == "End":
                    self.awayEndLineupPitch.addIcon("Assists", img, player.end_position, playerData.last_name, i + 1)
                else:
                    self.awayStartLineupPitch.addIcon("Assists", img, player.start_position, playerData.last_name, i + 1)
                    self.awayEndLineupPitch.addIcon("Assists", img, player.end_position, playerData.last_name, i + 1)

            playerRating = player.rating
            if pitch == "Start":
                self.awayStartLineupPitch.addRating(player.start_position, playerData.last_name, playerRating, True if player.id == self.potm.id else False)
            elif pitch == "End":
                self.awayEndLineupPitch.addRating(player.end_position, playerData.last_name, playerRating, True if player.id == self.potm.id else False)
            else:
                self.awayStartLineupPitch.addRating(player.start_position, playerData.last_name, playerRating, True if player.id == self.potm.id else False)
                self.awayEndLineupPitch.addRating(player.end_position, playerData.last_name, playerRating, True if player.id == self.potm.id else False)

            if injured:
                src = Image.open("Images/injury.png")
                src.thumbnail((10, 10))
                img = ImageTk.PhotoImage(src)

                if pitch == "Start":
                    self.awayStartLineupPitch.addInjuryIcon(player.start_position, playerData.last_name, img)
                elif pitch == "End":
                    self.awayEndLineupPitch.addInjuryIcon(player.end_position, playerData.last_name, img)
                else:
                    self.awayStartLineupPitch.addInjuryIcon(player.start_position, playerData.last_name, img)
                    self.awayEndLineupPitch.addInjuryIcon(player.end_position, playerData.last_name, img)

    def legend(self):
        """
        Create a legend frame that explains the icons used in the lineup pitches.
        """
        
        self.legendFrame.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight = 0)
        self.legendFrame.grid_rowconfigure((0, 2), weight = 0)
        self.legendFrame.grid_rowconfigure((1, 3), weight = 1)
        self.legendFrame.grid_propagate(False)

        ctk.CTkLabel(self.legendFrame, text = "Legend", font = (APP_FONT_BOLD, 18), fg_color = GREY_BACKGROUND).grid(row = 0, column = 0, columnspan = 6, pady = (5, 0))

        imageNames = ["goal_wb", "assist_wb", "redCard_wb", "yellowCard_wb", "ownGoal_wb", "missed_penalty_wb", "saved_penalty_wb", "injury"]
        iconNames = ["Goal", "Assist", "Red Card", "Yellow Card", "Own Goal", "Missed Penalty", "Saved Penalty", "Injury"]

        # Image in columns 0 and 2, text in columns 1 and 3
        for i, (imageName, iconName) in enumerate(zip(imageNames, iconNames)):
            src = Image.open(f"Images/{imageName}.png")
            src.thumbnail((15, 15))
            icon = ctk.CTkImage(src, None, (src.width, src.height))

            ctk.CTkLabel(self.legendFrame, text = "", image = icon, fg_color = GREY_BACKGROUND).grid(row = i // 2 + 1, column = i % 2 * 2, sticky = "w", padx = (8, 0), pady = (0, 2))
            ctk.CTkLabel(self.legendFrame, text = iconName, font = (APP_FONT, 12), fg_color = GREY_BACKGROUND).grid(row = i // 2 + 1, column = i % 2 * 2 + 1, sticky = "w", padx = (8, 0), pady = (0, 2))

    def swapData(self):
        """
        Swap between displaying match info and match stats.
        """
        
        if self.swapDataButton.cget("text") == "Stats":
            self.swapDataButton.configure(text = "Info")
            self.infoFrame.place_forget()
            self.statsFrame.place(relx = 0, rely = 0, anchor = "nw")

            if not self.statsAdded:
                self.statsAdded = True
                self.stats()
        else:
            self.swapDataButton.configure(text = "Stats")
            self.statsFrame.place_forget()
            self.infoFrame.place(relx = 0, rely = 0, anchor = "nw")

    def additionalInfo(self):
        """
        Display additional match information such as date, league, stadium, attendance, and referee.
        """
        
        frame = ctk.CTkFrame(self.infoFrame, fg_color = GREY_BACKGROUND, width = 100, height = 25)
        frame.pack(fill = "x", expand = True, padx = (5, 0), pady = (5, 0))

        src = Image.open("Images/calendar.png")
        src.thumbnail((20, 20))
        img = ctk.CTkImage(src, None, (src.width, src.height))
        ctk.CTkLabel(frame, text = "", image = img, fg_color = GREY_BACKGROUND).place(relx = 0.02, rely = 0.5, anchor = "w")

        day, dateText, time = format_datetime_split(self.match.date)
        ctk.CTkLabel(frame, text = f"{day} {dateText}, {time}", font = (APP_FONT, 12), fg_color = GREY_BACKGROUND).place(relx = 0.08, rely = 0.5, anchor = "w")

        frame = ctk.CTkFrame(self.infoFrame, fg_color = GREY_BACKGROUND, width = 100, height = 25)
        frame.pack(fill = "x", expand = True, padx = (5, 0), pady = (5, 0))

        src = Image.open(io.BytesIO(self.league.logo))
        src.thumbnail((20, 20))
        img = ctk.CTkImage(src, None, (src.width, src.height))
        ctk.CTkLabel(frame, text = "", image = img, fg_color = GREY_BACKGROUND).place(relx = 0.02, rely = 0.5, anchor = "w")
        ctk.CTkLabel(frame, text = f"{self.league.name} Matchday {self.match.matchday}", font = (APP_FONT, 12), fg_color = GREY_BACKGROUND).place(relx = 0.08, rely = 0.5, anchor = "w")

        frame = ctk.CTkFrame(self.infoFrame, fg_color = GREY_BACKGROUND, width = 100, height = 25)
        frame.pack(fill = "x", expand = True, padx = (5, 0), pady = (5, 0))

        src = Image.open("Images/stadium.png")
        src.thumbnail((20, 20))
        img = ctk.CTkImage(src, None, (src.width, src.height))
        ctk.CTkLabel(frame, text = "", image = img, fg_color = GREY_BACKGROUND).place(relx = 0.02, rely = 0.5, anchor = "w")
        ctk.CTkLabel(frame, text = f"{self.homeTeam.stadium}", font = (APP_FONT, 12), fg_color = GREY_BACKGROUND).place(relx = 0.08, rely = 0.5, anchor = "w")

        frame = ctk.CTkFrame(self.infoFrame, fg_color = GREY_BACKGROUND, width = 100, height = 25)
        frame.pack(fill = "x", expand = True, padx = (5, 0), pady = (5, 0))

        src = Image.open("Images/user.png")
        src.thumbnail((20, 20))
        img = ctk.CTkImage(src, None, (src.width, src.height))
        ctk.CTkLabel(frame, text = "", image = img, fg_color = GREY_BACKGROUND).place(relx = 0.02, rely = 0.5, anchor = "w")
        ctk.CTkLabel(frame, text = f"Attendance", font = (APP_FONT, 12), fg_color = GREY_BACKGROUND).place(relx = 0.08, rely = 0.5, anchor = "w")

        frame = ctk.CTkFrame(self.infoFrame, fg_color = GREY_BACKGROUND, width = 100, height = 25)
        frame.pack(fill = "x", expand = True, padx = (5, 0), pady = 5)

        referee = Referees.get_referee_by_id(self.match.referee_id)

        src = Image.open("Images/whistle.png")
        src.thumbnail((20, 20))
        img = ctk.CTkImage(src, None, (src.width, src.height))
        ctk.CTkLabel(frame, text = "", image = img, fg_color = GREY_BACKGROUND).place(relx = 0.02, rely = 0.5, anchor = "w")
        RefereeProfileLink(frame, referee, f"{referee.first_name} {referee.last_name}", "white", 0.08, 0.5, "w", GREY_BACKGROUND, self.parentTab, 12)

    def stats(self):
        """
        Display match statistics for both teams.
        """
        
        self.statsFrame.grid_columnconfigure((0, 2, 4), weight = 2)
        self.statsFrame.grid_columnconfigure((1, 3, 5), weight = 1)
        self.statsFrame.grid_rowconfigure((0, 1, 2, 3, 4), weight = 1)

        homeStats = MatchStats.get_team_stats_in_match(self.match.id, self.homeTeam.id)
        awayStats = MatchStats.get_team_stats_in_match(self.match.id, self.awayTeam.id)

        currCol = 0
        # Use canonical SAVED_STATS ordering to ensure home/away stats align reliably
        stat_names = list(SAVED_STATS)
        for i, statName in enumerate(stat_names):
            currRow = i % 5

            if i % 5 == 0 and i != 0:
                currCol += 2

            homeValue = homeStats.get(statName, 0)
            awayValue = awayStats.get(statName, 0)

            text = f"{homeValue} / {awayValue}"

            ctk.CTkLabel(self.statsFrame, text = statName, font = (APP_FONT, 12), fg_color = GREY_BACKGROUND).grid(row = currRow, column = currCol, sticky = "w", padx = 8)
            ctk.CTkLabel(self.statsFrame, text = text, font = (APP_FONT_BOLD, 14), fg_color = GREY_BACKGROUND).grid(row = currRow, column = currCol + 1, sticky = "nsew", padx = 5)
