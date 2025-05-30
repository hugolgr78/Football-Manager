import customtkinter as ctk
from settings import *
from data.database import *
from data.gamesDatabase import *
from utils.frames import MatchDayMatchFrame, FootballPitchMatchDay, FootballPitchLineup, LineupPlayerFrame
from utils.shouts import ShoutFrame
import threading, time
import concurrent.futures
from PIL import Image
class MatchDay(ctk.CTkFrame):
    def __init__(self, parent, teamLineup, teamSubstitutes, team, players):
        super().__init__(parent, width = APP_SIZE[0], height = APP_SIZE[1], fg_color = TKINTER_BACKGROUND)
        self.pack(fill = "both", expand = True)

        self.parent = parent
        self.teamLineup = teamLineup
        self.teamSubstitutes = teamSubstitutes
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

        self.lastShout = 0

        self.leagueTeams = LeagueTeams.get_league_by_team(self.team.id)
        self.league = League.get_league_by_id(self.leagueTeams.league_id)
        self.currentMatchDay = self.league.current_matchday
        self.matchDay = Matches.get_matchday_for_league(self.league.id, self.currentMatchDay)

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

        self.homeLineupPitch = FootballPitchMatchDay(self.teamMatchFrame, 270, 600, 0.02, 0.02, "nw", TKINTER_BACKGROUND, GREY_BACKGROUND)
        self.awayLineupPitch = FootballPitchMatchDay(self.teamMatchFrame, 270, 600, 0.98, 0.02, "ne", TKINTER_BACKGROUND, GREY_BACKGROUND)

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
        
    def addSpeedButtons(self):
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
        self.timerThread_running = False
        self.speed = speed
        self.timerThread_running = True

    def addMatches(self):
        for match in self.matchDay:
            if match.home_id == self.team.id or match.away_id == self.team.id:
                self.teamMatch = match
                self.matchFrame = MatchDayMatchFrame(self.teamMatchFrame, match, TKINTER_BACKGROUND, 150, 400, imageSize = 70, relx =  0.5, rely =  0.03, anchor = "n", border_width = 3, border_color = GREY_BACKGROUND, pack = False)
                
                self.matchDataFrame = ctk.CTkScrollableFrame(self.teamMatchFrame, width = 370, height = 300, fg_color = TKINTER_BACKGROUND, border_width = 3, border_color = GREY_BACKGROUND)
                self.matchDataFrame.place(relx = 0.5, rely = 0.27, anchor = "n")
                self.matchDataFrame._scrollbar.grid_configure(padx = 5)

                self.opposition = Teams.get_team_by_id(match.away_id if match.home_id == self.team.id else match.home_id)

                if match.home_id != self.team.id:
                    self.home = False
                    self.matchFrame.matchInstance.awayCurrentLineup = self.teamLineup
                    self.matchFrame.matchInstance.awayCurrentSubs = self.teamSubstitutes
                else:
                    self.matchFrame.matchInstance.homeCurrentLineup = self.teamLineup
                    self.matchFrame.matchInstance.homeCurrentSubs = self.teamSubstitutes

            else:
                frame = MatchDayMatchFrame(self.otherMatchesFrame, match, TKINTER_BACKGROUND, 60, 300)
                frame.matchInstance.createTeamLineup(match.home_id, True)
                frame.matchInstance.createTeamLineup(match.away_id, False)
                frame.matchInstance.generateScore()

    def addTime(self):
        self.timeLabel = ctk.CTkLabel(self.timeFrame, text = "00:00", font = (APP_FONT_BOLD, 50), fg_color = TKINTER_BACKGROUND)
        self.timeLabel.place(relx = 0.5, rely = 0.4, anchor = "center")

        self.extraTimeLabel = ctk.CTkLabel(self.timeFrame, text = "ET", font = (APP_FONT, 18), fg_color = TKINTER_BACKGROUND)

        self.pauseButton = ctk.CTkButton(self.timeFrame, text = "Simulate", font = (APP_FONT, 20), fg_color = APP_BLUE, bg_color = TKINTER_BACKGROUND, command = self.simulateMatch)
        self.pauseButton.place(relx = 0.5, rely = 0.8, anchor = "center")

    def addLineups(self):
        
        teamPitch = self.homeLineupPitch if self.home else self.awayLineupPitch
        teamSubFrame = self.homeSubstituteFrame if self.home else self.awaySubstituteFrame
        oppPitch = self.awayLineupPitch if self.home else self.homeLineupPitch
        oppSubFrame = self.awaySubstituteFrame if self.home else self.homeSubstituteFrame
        oppTeamID = self.opposition.id

        self.matchFrame.matchInstance.createTeamLineup(oppTeamID, not self.home)
        self.oppositionLineup = self.matchFrame.matchInstance.awayCurrentLineup if self.home else self.matchFrame.matchInstance.homeCurrentLineup
        oppositionSubstitutes = self.matchFrame.matchInstance.awayCurrentSubs if self.home else self.matchFrame.matchInstance.homeCurrentSubs

        for position, playerID, in self.teamLineup.items():
            player = Players.get_player_by_id(playerID)
            teamPitch.addPlayer(position, player.last_name)

        for i, playerID in enumerate(self.teamSubstitutes):
            player = Players.get_player_by_id(playerID)
            ctk.CTkLabel(teamSubFrame, text = player.first_name + " " + player.last_name, font = (APP_FONT, 10), fg_color = GREY_BACKGROUND).place(relx = 0.1, rely = 0.25 + 0.11 * i, anchor = "w")
            ctk.CTkLabel(teamSubFrame, text = player.specific_positions, font = (APP_FONT, 10), fg_color = GREY_BACKGROUND).place(relx = 0.9, rely = 0.25 + 0.11 * i, anchor = "e")

        for position, playerID in self.oppositionLineup.items():
            player = Players.get_player_by_id(playerID)
            oppPitch.addPlayer(position, player.last_name)

        for i, playerID in enumerate(oppositionSubstitutes):
            player = Players.get_player_by_id(playerID)
            ctk.CTkLabel(oppSubFrame, text = player.first_name + " " + player.last_name, font = (APP_FONT, 10), fg_color = GREY_BACKGROUND).place(relx = 0.1, rely = 0.25 + 0.11 * i, anchor = "w")
            ctk.CTkLabel(oppSubFrame, text = player.specific_positions, font = (APP_FONT, 10), fg_color = GREY_BACKGROUND).place(relx = 0.9, rely = 0.25 + 0.11 * i, anchor = "e")

        self.matchFrame.matchInstance.generateScore(teamMatch = True, home = self.home)

    def updateSubFrame(self, home, playerOnID, playerOffID):
        playerOn = Players.get_player_by_id(playerOnID)
        playerOff = Players.get_player_by_id(playerOffID)

        subFrame = self.homeSubstituteFrame if home else self.awaySubstituteFrame

        for i, widget in enumerate(subFrame.winfo_children()):
            if widget.cget("text") == playerOn.first_name + " " + playerOn.last_name:
                widget.configure(text = playerOff.first_name + " " + playerOff.last_name, text_color = "grey")

                subFrame.winfo_children()[i + 1].place_forget()

    def simulateMatch(self):
        self.pauseButton.configure(text = "Pause", command = self.pauseMatch)
        self.substitutionButton.configure(state = "normal") 
        self.shoutsButton.configure(state = "normal")

        self.timerThread_running = True
        self.timerThread = threading.Thread(target = self.gameLoop)
        self.timerThread.daemon = True
        self.timerThread.start()

    def pauseMatch(self):
        self.pauseButton.configure(text = "Resume", command = self.resumeMatch)
        self.timerThread_running = False

    def resumeMatch(self, halfTime = False):

        if halfTime:
            self.halfTimeFrame.pack_forget()   

        self.pauseButton.configure(text = "Pause", command = self.pauseMatch)
        self.timerThread_running = True
        self.timerThread = threading.Thread(target = self.gameLoop)
        self.timerThread.daemon = True
        self.timerThread.start()

    def gameLoop(self):
        while self.timerThread_running:
            
            currTime = self.timeLabel.cget("text")

            # After HT, once the player hits Resume
            if currTime == "HT":
                minutes = 45
                seconds = 0

                # reset all the score labels as they were before HT
                for frame in self.otherMatchesFrame.winfo_children():
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

            if seconds == 59:
                minutes += 1
                seconds = 0
            else:
                seconds += 1

            if minutes == self.lastShout + 10 and seconds == 0:
                self.shoutsButton.configure(state = "normal")

            ## ----------- half time ------------
            if minutes == 45 and seconds == 0:

                ## extra time
                self.halfTime = True
                self.matchFrame.matchInstance.halfTime = True
                self.maxExtraTimeHalf = 0
                for frame in self.otherMatchesFrame.winfo_children():
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

                        elif minute < 45 and event_details["type"] != "susbtitution":
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

            ## Half time for every time now
            if self.halfTime:
                self.extraTimeLabel.place(relx = 0.76, rely = 0.48, anchor = "center")
                if minutes == 45 + self.maxExtraTimeHalf and seconds == 0:
                    self.timerThread_running = False
                    self.halfTimeTalks()
                    # self.pauseButton.configure(text = "Resume", command = self.resumeMatch)

                    ## Add HT labels if they are not already there
                    for frame in self.otherMatchesFrame.winfo_children():
                        if not frame.halfTimeLabel.winfo_ismapped():
                            frame.HTLabel()

                    if not self.matchFrame.halfTimeLabel.winfo_ismapped():
                        self.matchFrame.HTLabel() 

                    self.extraTimeLabel.place_forget()

                    self.halfTime = False
                    self.halfTimeEnded = True

            ## ----------- full time ------------
            if minutes == 90 and seconds == 0:
               
                self.fullTime = True
                self.matchFrame.matchInstance.fullTime = True
                self.maxExtraTimeFull = 0

                for frame in self.otherMatchesFrame.winfo_children():
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

            if self.fullTime:
                self.extraTimeLabel.place(relx = 0.76, rely = 0.48, anchor = "center")
                if minutes == 90 + self.maxExtraTimeFull and seconds == 0:
                    self.timerThread_running = False
                    self.pauseButton.configure(text = "Save", command = self.endSimulation)
                    self.fullTime = False
                    self.fullTimeEnded = True

                    for frame in self.otherMatchesFrame.winfo_children():
                        if not frame.fullTimeLabel.winfo_ismapped():
                            frame.FTLabel()

                    if not self.matchFrame.fullTimeLabel.winfo_ismapped():
                        self.matchFrame.FTLabel()
                    
                    self.extraTimeLabel.place_forget()

            ## ----------- substitution end ------------
            if minutes == 89 + self.maxExtraTimeFull and seconds == 0:
                self.substitutionButton.configure(state = "disabled")

            ## ----------- other matches ------------ 
            for frame in self.otherMatchesFrame.winfo_children():

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

            if minutes == 45 + self.matchFrame.matchInstance.extraTimeHalf and self.halfTime and seconds == 0:
                self.shoutsButton.configure(state = "disabled")
                self.substitutionButton.configure(state = "disabled")
                self.matchFrame.HTLabel()
            
            if minutes == 90 + self.matchFrame.matchInstance.extraTimeFull and self.fullTime and seconds == 0:
                self.shoutsButton.configure(state = "disabled")
                self.substitutionButton.configure(state = "disabled")
                self.matchFrame.FTLabel()

            ## ----------- managing team match ------------
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
                                self.substitution(redCardPlayer = newEvent["player"])

                            self.after(0, self.updateMatchDataFrame, newEvent, event_time, True)
                    else:
                        if not (self.halfTime or self.fullTime):
                            if event_details["type"] in ["own_goal", "goal", "penalty_goal"]:
                                self.matchFrame.updateScoreLabel()
                            newEvent = self.matchFrame.matchInstance.getEventPlayer(event_details, True, event_time, teamMatch = self, managing_team = True if self.home else False)
                            self.matchFrame.matchInstance.homeProcessedEvents[event_time] = event_details

                            if self.home and event_details["type"] == "injury":
                                self.substitution(forceSub = True, injuredPlayer=newEvent["player"])
                            if self.home and event_details["type"] == "red_card":
                                self.substitution(redCardPlayer = newEvent["player"])

                            self.after(0, self.updateMatchDataFrame, newEvent, event_time, True)

            for event_time, event_details in list(self.matchFrame.matchInstance.awayEvents.items()):
                if event_time == str(minutes) + ":" + str(seconds) and event_time not in self.matchFrame.matchInstance.awayProcessedEvents:
                    if event_details["extra"]:
                        if self.halfTime or self.fullTime:
                            if event_details["type"] in ["own_goal", "goal", "penalty_goal"]:
                                self.matchFrame.updateScoreLabel(home = False)
                            newEvent = self.matchFrame.matchInstance.getEventPlayer(event_details, False, event_time, teamMatch = self, managing_team = True if not self.home else False)
                            self.matchFrame.matchInstance.awayProcessedEvents[event_time] = event_details

                            if not self.home and event_details["type"] == "injury":
                                self.substitution(forceSub = True, injuredPlayer = newEvent["player"])
                            if not self.home and event_details["type"] == "red_card":
                                self.substitution(redCardPlayer = newEvent["player"])

                            self.after(0, self.updateMatchDataFrame, newEvent, event_time, False)
                    else:
                        if not (self.halfTime or self.fullTime):
                            if event_details["type"] in ["own_goal", "goal", "penalty_goal"]:
                                self.matchFrame.updateScoreLabel(home = False)
                            newEvent = self.matchFrame.matchInstance.getEventPlayer(event_details, False, event_time, teamMatch = self, managing_team = True if not self.home else False)
                            self.matchFrame.matchInstance.awayProcessedEvents[event_time] = event_details

                            if not self.home and event_details["type"] == "injury":
                                self.substitution(forceSub = True, injuredPlayer = newEvent["player"])
                            if not self.home and event_details["type"] == "red_card":
                                self.substitution(redCardPlayer = newEvent["player"])

                            self.after(0, self.updateMatchDataFrame, newEvent, event_time, False)

            if self.halfTimeEnded:
                self.timeLabel.configure(text = "HT")
                self.halfTimeEnded = False
            elif self.fullTimeEnded:
                self.timeLabel.configure(text = "FT")
            else:
                self.after(0, self.updateTimeLabel, minutes, seconds)

            time.sleep(self.speed)

    def shouts(self):

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
        self.shoutMade = True
        self.shoutsButton.configure(state = "disabled")

    def closeShouts(self):

        if self.shoutMade:
            self.lastShout = self.currMin + 1 if self.currMin == 0 else self.currMin
        else:
            self.shoutsButton.configure(state = "normal")

        self.shoutsFrame.place_forget()
        self.pauseButton.configure(state = "normal")
        self.substitutionButton.configure(state = "normal")
        self.resumeMatch()

    def substitution(self, forceSub = False, injuredPlayer = None, redCardPlayer = None):
        
        self.startTeamLineup = self.matchFrame.matchInstance.homeCurrentLineup.copy() if self.home else self.matchFrame.matchInstance.awayCurrentLineup.copy()
        self.startTeamSubstitutes = self.matchFrame.matchInstance.homeCurrentSubs.copy() if self.home else self.matchFrame.matchInstance.awayCurrentSubs.copy()
        self.teamLineup = self.startTeamLineup.copy()
        self.teamSubstitutes = self.startTeamSubstitutes.copy()

        self.playersOn = {}
        self.playersOff = {}

        self.forceSub = forceSub
        self.injuredPlayer = Players.get_player_by_id(injuredPlayer) if injuredPlayer else None

        self.currentSubs = 0

        self.values = list(POSITION_CODES.keys())

        self.pauseMatch()

        self.substitutionFrame = ctk.CTkFrame(self, width = APP_SIZE[0], height = APP_SIZE[1], fg_color = TKINTER_BACKGROUND)
        self.substitutionFrame.place(relx = 0, rely = 0, anchor = "nw")

        self.lineupPitch = FootballPitchLineup(self.substitutionFrame, 450, 750, 0, 0, "nw", TKINTER_BACKGROUND, "green")

        self.addFrame = ctk.CTkFrame(self.substitutionFrame, fg_color = GREY_BACKGROUND, width = 370, height = 50, corner_radius = 10)
        self.addFrame.place(relx = 0.01, rely = 0.98, anchor = "sw")

        ctk.CTkLabel(self.addFrame, text = "Add Substitute:", font = (APP_FONT, 18), text_color = "white", fg_color = GREY_BACKGROUND).place(relx = 0.05, rely = 0.5, anchor = "w")

        self.dropDown = ctk.CTkComboBox(self.addFrame, font = (APP_FONT, 15), fg_color = GREY_BACKGROUND, corner_radius = 10, dropdown_fg_color = GREY_BACKGROUND, dropdown_hover_color = DARK_GREY, width = 210, height = 30, state = "disabled", command = self.choosePlayer)
        self.dropDown.place(relx = 0.4, rely = 0.5, anchor = "w")
        self.dropDown.set("Choose Position")

        self.substitutesFrame = ctk.CTkFrame(self.substitutionFrame, width = 520, height = 615, fg_color = GREY_BACKGROUND, corner_radius = 10)
        self.substitutesFrame.place(relx = 0.33, rely = 0.02, anchor = "nw")
        self.substitutesFrame.pack_propagate(False)

        self.confirmButton = ctk.CTkButton(self.substitutionFrame, text = "Confirm", width = 520, height = 50, font = (APP_FONT, 20), fg_color = APP_BLUE, bg_color = TKINTER_BACKGROUND, corner_radius = 10, command = self.finishSubstitution)
        self.confirmButton.place(relx = 0.33, rely = 0.98, anchor = "sw")

        ctk.CTkLabel(self.substitutesFrame, text = "Substitutes", font = (APP_FONT, 30), fg_color = GREY_BACKGROUND).pack(pady = 10)

        for position, playerID in self.startTeamLineup.items():
            player = Players.get_player_by_id(playerID)
            positionCode = POSITION_CODES[position]
            name = player.first_name + " " + player.last_name

            if self.injuredPlayer and self.injuredPlayer.first_name + " " + self.injuredPlayer.last_name == name:
                self.injuredPosition = position
                if self.completedSubs != MAX_SUBS:
                    LineupPlayerFrame(self.lineupPitch,
                                    POSITIONS_PITCH_POSITIONS[position][0],
                                    POSITIONS_PITCH_POSITIONS[position][1],
                                    "center",
                                    INJURY_RED,
                                    65,
                                    65,
                                    name,
                                    positionCode,
                                    position,
                                    self.removePlayer)
            else:
                LineupPlayerFrame(self.lineupPitch,
                                POSITIONS_PITCH_POSITIONS[position][0],
                                POSITIONS_PITCH_POSITIONS[position][1],
                                "center",
                                GREY_BACKGROUND,
                                65,
                                65,
                                name,
                                positionCode,
                                position,
                                self.removePlayer)
            
            if position in self.values:
                self.values.remove(position)

        for playerID in self.startTeamSubstitutes:
            player = Players.get_player_by_id(playerID)
            self.addSubstitute(player.first_name + " " + player.last_name, player.specific_positions)

        self.choosePlayerFrame = ctk.CTkFrame(self, fg_color = GREY_BACKGROUND, width = 400, height = 50, corner_radius = 0, border_color = APP_BLUE, border_width = 2)

        self.backButton = ctk.CTkButton(self.choosePlayerFrame, text = "Back", font = (APP_FONT, 15), fg_color = DARK_GREY, corner_radius = 10, height = 30, width = 100, hover_color = CLOSE_RED, command = self.stop_choosePlayer)
        self.backButton.place(relx = 0.95, rely = 0.5, anchor = "e")

        self.playerDropDown = ctk.CTkComboBox(self.choosePlayerFrame, font = (APP_FONT, 15), fg_color = GREY_BACKGROUND, corner_radius = 10, dropdown_fg_color = GREY_BACKGROUND, dropdown_hover_color = DARK_GREY, width = 220, height = 30, state = "readonly", command = self.choosePosition)
        self.playerDropDown.place(relx = 0.05, rely = 0.5, anchor = "w")
        self.playerDropDown.set("Choose Player")

        if self.forceSub: 
            if self.completedSubs == MAX_SUBS: # if injury occurs after making all 5 substitutions
                self.confirmButton.configure(state = "normal")
                self.dropDown.configure(state = "disabled")

                for frame in self.lineupPitch.winfo_children():
                    if isinstance(frame, LineupPlayerFrame):
                        frame.removeButton.configure(state = "disabled")

                self.addSubstitute(self.injuredPlayer.first_name + " " + self.injuredPlayer.last_name, self.injuredPlayer.specific_positions, unavailablePlayer = True)

                lineup = self.matchFrame.matchInstance.homeCurrentLineup if self.home else self.matchFrame.matchInstance.awayCurrentLineup
                finalLineup = self.matchFrame.matchInstance.homeFinalLineup if self.home else self.matchFrame.matchInstance.awayFinalLineup
                pitch = self.homeLineupPitch if self.home else self.awayLineupPitch

                pitch.removePlayer(self.injuredPosition)
                lineup.pop(self.injuredPosition)
                finalLineup[self.injuredPosition] = self.injuredPlayer
            else:
                self.confirmButton.configure(state = "disabled")

        if redCardPlayer:
            player = Players.get_player_by_id(redCardPlayer)
            self.addSubstitute(player.first_name + " " + player.last_name, player.specific_positions, unavailablePlayer = True)

    def addSubstitute(self, playerName, positions, unavailablePlayer = False):
        frame = ctk.CTkFrame(self.substitutesFrame, width = 520, height = 30, fg_color = GREY_BACKGROUND)
        frame.pack()
        
        frame.unavailable = unavailablePlayer
        ctk.CTkLabel(frame, text = positions, font = (APP_FONT, 15), fg_color = GREY_BACKGROUND).place(relx = 0.95, rely = 0.5, anchor = "e")
        
        if not unavailablePlayer:
            ctk.CTkLabel(frame, text = playerName, font = (APP_FONT, 15), fg_color = GREY_BACKGROUND).place(relx = 0.05, rely = 0.5, anchor = "w")
        else:
            ctk.CTkLabel(frame, text = playerName, font = (APP_FONT, 15), fg_color = GREY_BACKGROUND, text_color = INJURY_RED).place(relx = 0.05, rely = 0.5, anchor = "w")

    def removePlayer(self, frame, playerName, playerPosition): 
        
        for position in POSITION_CODES.keys():
            if position == playerPosition:
                self.values.append(position)

                if position in RELATED_POSITIONS:
                    for related_position in RELATED_POSITIONS[position]:
                        self.values.append(related_position)
                break

        frame.place_forget()

        self.dropDown.configure(state = "readonly")
        self.dropDown.configure(values = self.values)

        playerData = Players.get_player_by_name(playerName.split(" ")[0], playerName.split(" ")[1], self.team.id)
        if playerData.id in self.startTeamLineup.values():
            self.playersOff[playerPosition] = playerData.id
            self.currentSubs += 1
        else:
            del self.playersOn[playerPosition]

        self.addSubstitute(playerName, playerData.specific_positions)
        
        self.teamSubstitutes.append(playerData.id)
        self.teamLineup.pop(playerPosition)

        for frame in self.lineupPitch.winfo_children():
            if isinstance(frame, LineupPlayerFrame):
                frame.removeButton.configure(state = "disabled")

    def choosePlayer(self, selected_position):
        self.selected_position = selected_position
        self.dropDown.configure(state = "disabled")
        self.confirmButton.configure(state = "disabled")

        self.choosePlayerFrame.place(relx = 0.225, rely = 0.5, anchor = "center")

        values = []
        for frame in self.substitutesFrame.winfo_children():
            if isinstance(frame, ctk.CTkFrame):
                labels = frame.winfo_children()
                if len(labels) >= 2:
                    playerName = labels[1].cget("text")
                    positions = labels[0].cget("text")
                    unavailable = frame.unavailable

                    player = Players.get_player_by_name(playerName.split(" ")[0], playerName.split(" ")[1], self.team.id)
                    if self.currentSubs > MAX_SUBS - self.completedSubs:
                        if POSITION_CODES[selected_position] in positions.split(",") and player.id in self.startTeamLineup.values() and player.id not in self.teamLineup.values() and not unavailable:
                            values.append(playerName)
                    else:
                        if POSITION_CODES[selected_position] in positions.split(",") and player.id not in self.teamLineup.values() and not unavailable:
                            values.append(playerName)
        
        if len(values) == 0:
            self.playerDropDown.set("No available players")
            self.playerDropDown.configure(state = "disabled")
        else:
            self.playerDropDown.set("Choose Player")
            self.playerDropDown.configure(values = values)
            self.playerDropDown.configure(state = "normal")

    def stop_choosePlayer(self):
        self.choosePlayerFrame.place_forget()
        self.dropDown.configure(state = "normal")
        self.playerDropDown.set("Choose Player")
        self.confirmButton.configure(state = "normal")

    def choosePosition(self, selected_player):
        self.stop_choosePlayer()
        self.dropDown.configure(state = "disabled")

        if self.selected_position in self.values:
            self.values.remove(self.selected_position)

            if self.selected_position in RELATED_POSITIONS:
                for related_position in RELATED_POSITIONS[self.selected_position]:
                    if related_position in self.values:
                        self.values.remove(related_position)

        self.dropDown.configure(values = self.values)

        playerData = Players.get_player_by_name(selected_player.split(" ")[0], selected_player.split(" ")[1], self.team.id)
        if playerData.id in self.startTeamLineup.values():
            for position, playerID in list(self.playersOff.items()):
                if playerID == playerData.id:
                    del self.playersOff[position]
                    break

            self.currentSubs -= 1
        else:
            self.playersOn[self.selected_position] = playerData.id

        self.teamLineup[self.selected_position] = playerData.id

        for playerID in self.teamSubstitutes:
            if playerID == playerData.id:
                self.teamSubstitutes.remove(playerID)

        color = GREY_BACKGROUND
        if self.injuredPlayer:
            injured_player_name = self.injuredPlayer.first_name + " " + self.injuredPlayer.last_name
            if selected_player == injured_player_name:
                color = INJURY_RED

        LineupPlayerFrame(self.lineupPitch, 
                            POSITIONS_PITCH_POSITIONS[self.selected_position][0], 
                            POSITIONS_PITCH_POSITIONS[self.selected_position][1], 
                            "center", 
                            color,
                            65, 
                            65, 
                            selected_player,
                            POSITION_CODES[self.selected_position],
                            self.selected_position,
                            self.removePlayer
                        )
        
        for frame in self.substitutesFrame.winfo_children():
            if frame.winfo_children()[1].cget("text") == selected_player:
                frame.destroy()

        for frame in self.lineupPitch.winfo_children():
            if isinstance(frame, LineupPlayerFrame):
                frame.removeButton.configure(state = "normal")

        if self.forceSub:
            if self.injuredPlayer in self.playersOff.values():
                self.confirmButton.configure(state = "normal")
            elif self.injuredPlayer not in self.playersOn.values():
                self.confirmButton.configure(state = "disabled")

    def finishSubstitution(self):
        if self.currentSubs != 0:
            lineup = self.matchFrame.matchInstance.homeCurrentLineup if self.home else self.matchFrame.matchInstance.awayCurrentLineup
            finalLineup = self.matchFrame.matchInstance.homeFinalLineup if self.home else self.matchFrame.matchInstance.awayFinalLineup
            subs = self.matchFrame.matchInstance.homeCurrentSubs if self.home else self.matchFrame.matchInstance.awayCurrentSubs
            events = self.matchFrame.matchInstance.homeEvents if self.home else self.matchFrame.matchInstance.awayEvents

            times = []
            for i in range(1, self.currentSubs + 1):
                currMinute = int(self.timeLabel.cget("text").split(":")[0])
                currSeconds = int(self.timeLabel.cget("text").split(":")[1])
                
                if currSeconds + (i * 10) > 60:
                    eventSeconds = (currSeconds + (i * 10)) - 60
                    eventMinute = currMinute + 1
                else:
                    eventSeconds = currSeconds + (i * 10)
                    eventMinute = currMinute

                eventTime = str(eventMinute) + ":" + str(eventSeconds)
                times.append(eventTime)

                events[eventTime] = {
                    "type": "substitution",
                    "player": None,
                    "player_off": None,
                    "player_on": None,
                    "injury": False,
                    "extra": True if self.halfTime else False
                }

            ## Adding / removing players from the lineup and lineup pitch (checking differences between startTeamLineup and teamLineup)
            pitch = self.homeLineupPitch if self.home else self.awayLineupPitch
            for position, playerID in self.startTeamLineup.items(): # changing a player's position 
                if position in self.teamLineup and playerID != self.teamLineup[position]:
                    lineupPlayer = Players.get_player_by_id(self.teamLineup[position])
                    pitch.removePlayer(position)
                    pitch.addPlayer(position, lineupPlayer.last_name)

                    lineup[position] = self.teamLineup[position]
                elif position not in self.teamLineup: # removing a player from the lineup
                    pitch.removePlayer(position)
                    lineup.pop(position)

            for position, playerID in list(self.teamLineup.items()):
                if position not in self.startTeamLineup: # adding a player to the lineup
                    player = Players.get_player_by_id(playerID)
                    pitch.addPlayer(position, player.last_name)
                    lineup[position] = playerID

            ## Substitution events
            for i, (positionOff, playerOffID) in enumerate(list(self.playersOff.items()), 1):
                event = events[times[i - 1]]
                finalLineup[positionOff] = playerOffID
                
                # Find the player in playersOn that suits the position of playerOff the most
                for positionOn, playerOnID in list(self.playersOn.items()):
                    if positionOn == positionOff:
                        self.matchFrame.matchInstance.addPlayerToLineup(event, playerOnID, playerOffID, positionOn, subs, lineup, self, self.home, managing_team = True)
                        del self.playersOn[positionOn]
                        break
                else:
                    # Find the player in playersOn that has the same overall position as playerOff
                    for positionOn, playerOnID in list(self.playersOn.items()):
                        playerOn = Players.get_player_by_id(playerOnID)
                        playerOff = Players.get_player_by_id(playerOffID)
                        if playerOn.position == playerOff.position:
                            self.matchFrame.matchInstance.addPlayerToLineup(event, playerOnID, playerOffID, positionOn, subs, lineup, self, self.home, managing_team = True)
                            del self.playersOn[positionOn]
                            break
                    else:
                        # Use a random player from the playersOn
                        positionOn, playerOnID = random.choice(list(self.playersOn.items()))
                        self.matchFrame.matchInstance.addPlayerToLineup(event, playerOnID, playerOffID, positionOn, subs, lineup, self, self.home, managing_team = True)
                        del self.playersOn[positionOn]

        self.substitutionFrame.place_forget()
        self.resumeMatch()
        self.completedSubs += self.currentSubs
        self.currentSubs = 0

        if self.completedSubs == MAX_SUBS:
            self.substitutionButton.configure(state = "disabled")

    def halfTimeTalks(self):

        ## Create frames
        self.halfTimeFrame = ctk.CTkFrame(self, width = APP_SIZE[0], height = APP_SIZE[1], fg_color = TKINTER_BACKGROUND)
        self.halfTimeFrame.pack(fill = "both", expand = True)

        self.HTbuttonsFrame = ctk.CTkFrame(self.halfTimeFrame, width = APP_SIZE[0] - 20, height = 120, fg_color = TKINTER_BACKGROUND, corner_radius = 10)
        self.HTbuttonsFrame.place(relx = 0.99, rely = 0.99, anchor = "se")

        self.HTresumeButton = ctk.CTkButton(self.HTbuttonsFrame, text = "Resume Game >>", width = 400, height = 55, font = (APP_FONT, 15), fg_color = APP_BLUE, corner_radius = 10, bg_color = TKINTER_BACKGROUND, command = lambda: self.resumeMatch(halfTime = True))
        self.HTresumeButton.place(relx = 1, rely = 1, anchor = "se")

        self.HTsubsButton = ctk.CTkButton(self.HTbuttonsFrame, text = "Substitutions", width = 400, height = 55, font = (APP_FONT, 15), fg_color = APP_BLUE, corner_radius = 10, bg_color = TKINTER_BACKGROUND)
        self.HTsubsButton.place(relx = 1, rely = 0, anchor = "ne")

        self.HTscoreDataFrame = ctk.CTkFrame(self.HTbuttonsFrame, width = 765, height = 120, fg_color = GREY_BACKGROUND, corner_radius = 10)
        self.HTscoreDataFrame.place(relx = 0, rely = 0, anchor = "nw")

        self.HTpromptsFrame = ctk.CTkFrame(self.halfTimeFrame, width = 670, height = 550, fg_color = GREY_BACKGROUND, corner_radius = 10)

        self.HTplayersFrame = ctk.CTkFrame(self.halfTimeFrame, width = 520, height = 550, fg_color = GREY_BACKGROUND, corner_radius = 10)

        ## Half time score data frame
        src = Image.open(f"Images/Teams/{self.team.name}.png")
        src.thumbnail((75, 75))
        teamImage = ctk.CTkImage(src, None, (src.width, src.height))

        src = Image.open(f"Images/Teams/{self.opposition.name}.png")
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

        def addGoal(home):
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
        self.timeLabel.configure(text = f"{str(minutes).zfill(2)}:{str(seconds).zfill(2)}")

    def updateMatchDataFrame(self, event, time, home = True):

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
            subText = Players.get_player_by_id(event["assister"]).last_name if "assister" in event else "Penalty"
        elif event["type"] == "own_goal":
            src = Image.open("Images/ownGoal.png")
            subText = "Own Goal"
        elif event["type"] == "yellow_card":
            src = Image.open("Images/yellowCard.png")
            subText = "Yellow Card"
        elif event["type"] == "red_card":
            src = Image.open("Images/redCard.png")
            subText = "Red Card"
        elif event["type"] == "penalty_miss":
            src = Image.open("Images/missed_penalty.png")
            subText = "Missed Penalty"
        elif event["type"] == "injury":
            src = Image.open("Images/injury.png")
            subText = "Injury"
        elif event["type"] == "substitution":
            if home:
                src = Image.open("Images/substitution_home.png")
            else:
                src = Image.open("Images/substitution_away.png")

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

    def endSimulation(self):

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(frame.matchInstance.saveData) for frame in self.otherMatchesFrame.winfo_children()]
            concurrent.futures.wait(futures)

        self.matchFrame.matchInstance.saveData(managing_team = "home" if self.home else "away")

        LeagueTeams.update_team_positions(self.league.id)

        for team in LeagueTeams.get_teams_by_league(self.league.id):
            TeamHistory.add_team(self.currentMatchDay, team.team_id, team.position, team.points)

        League.update_current_matchday(self.league.id)

        self.pack_forget()
        self.parent.resetMenu()
