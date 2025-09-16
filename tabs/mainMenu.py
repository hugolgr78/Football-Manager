import customtkinter as ctk
from settings import *
from data.database import *
from data.gamesDatabase import *
from PIL import Image
from utils.util_functions import *
from concurrent.futures import ThreadPoolExecutor, as_completed
import traceback

from tabs.hub import Hub
from tabs.inbox import Inbox
from tabs.squad import Squad
from tabs.schedule import Schedule
from tabs.tactics import Tactics
from tabs.teamProfile import TeamProfile
from tabs.leagueProfile import LeagueProfile
from tabs.managerProfile import ManagerProfile
from tabs.search import Search
from tabs.settingsTab import SettingsTab
from utils.match import Match

class MainMenu(ctk.CTkFrame):
    def __init__(self, parent, manager_id, created):
        super().__init__(parent, fg_color = TKINTER_BACKGROUND)
        self.pack(fill = "both", expand = True)

        self.parent = parent
        self.manager_id = manager_id

        if created:
            db = DatabaseManager()
            db.commit_copy()

        self.team = Teams.get_teams_by_manager(self.manager_id)[0]

        self.initUI()

    def initUI(self):

        self.overlappingProfiles = []
        self.emailsAdded = False

        self.hub = Hub(self)
        self.hub.place(x = 200, y = 0, anchor = "nw")
        
        self.inbox = None
        self.squad = None
        self.schedule = None
        self.tactics = None
        self.teamProfile = None
        self.leagueProfile = None
        self.managerProfile = None
        self.search = None
        self.settings = None

        self.activeButton = 0
        self.buttons = []
        self.titles = ["  Main Hub", "  Inbox", "  Squad", "  Schedule", "  Tactics", "  Club", "  League", "  Profile", "  Search"]
        self.tabs = [self.hub, self.inbox, self.squad, self.schedule, self.tactics, self.teamProfile, self.leagueProfile, self.managerProfile, self.search, self.settings]
        self.classNames = [Hub, Inbox, Squad, Schedule, Tactics, TeamProfile, LeagueProfile, ManagerProfile, Search, SettingsTab]

        self.tabsFrame = ctk.CTkFrame(self, fg_color = TKINTER_BACKGROUND, width = 200, height = 700)
        self.tabsFrame.place(x = 0, y = 0, anchor = "nw")

        canvas = ctk.CTkCanvas(self, width = 5, height = 1000, bg = APP_BLUE, bd = 0, highlightthickness = 0)
        canvas.place(x = 245, y = 0, anchor = "nw")

        self.dayLabel = None
        self.timeLabel = None
        self.continueButton = None

        self.createTabs()
        self.addDate()

    def createTabs(self):

        ctk.CTkLabel(self.tabsFrame, text = "Football", font = (APP_FONT_BOLD, 28), text_color = "white", fg_color = TKINTER_BACKGROUND).place(relx = 0.5, rely = 0.04, anchor = "center")
        ctk.CTkLabel(self.tabsFrame, text = "Manager", font = (APP_FONT_BOLD, 35), text_color = "white", fg_color = TKINTER_BACKGROUND).place(relx = 0.5, rely = 0.09, anchor = "center")

        canvas = ctk.CTkCanvas(self.tabsFrame, width = 250, height = 5, bg = APP_BLUE, bd = 0, highlightthickness = 0)
        canvas.place(relx = 0.5, rely = 0.14, anchor = "center")

        self.buttonHeight = 40
        self.buttonWidth = 200
        self.startHeight = 0.17
        self.button_background = TKINTER_BACKGROUND
        self.hover_background = GREY_BACKGROUND
        self.gap = 0.03

        gapCount = 0
        for i in range(len(self.titles)):
            button = ctk.CTkButton(self.tabsFrame, text = self.titles[i], font = (APP_FONT, 20), fg_color = self.button_background, corner_radius = 0, height = self.buttonHeight, width = self.buttonWidth, hover_color = self.hover_background, anchor = "w")
            button.place(relx = 0.5, rely = self.startHeight + self.gap * gapCount, anchor = "center")
            button.configure(command = lambda i = i: self.changeTab(i))
            
            self.buttons.append(button)
            self.canvas(250, 5, self.startHeight + self.gap * (gapCount + 1))

            gapCount += 2

        self.buttons[self.activeButton].configure(state = "disabled")

        src = Image.open("Images/settings.png")
        src.thumbnail((30, 30))
        img = ctk.CTkImage(src, None, (src.width, src.height))

        settingsButton = ctk.CTkButton(self.tabsFrame, text = "", image = img, fg_color = APP_BLUE, corner_radius = 10, height = 50, width = 50, hover_color = APP_BLUE)
        settingsButton.place(relx = 0.03, rely = 0.99, anchor = "sw")
        settingsButton.configure(command = lambda: self.changeTab(len(self.tabs) - 1))
        self.buttons.append(settingsButton)

    def canvas(self, width, height, rely):
        canvas = ctk.CTkCanvas(self.tabsFrame, width = width, height = height, bg = GREY_BACKGROUND, bd = 0, highlightthickness = 0)
        canvas.place(relx = 0.5, rely = rely, anchor = "center")

    def changeTab(self, index):
        self.buttons[self.activeButton].configure(state = "normal")
        self.tabs[self.activeButton].place_forget()

        for frame in self.overlappingProfiles:
            frame.place_forget()

        self.activeButton = index
        self.buttons[self.activeButton].configure(state = "disabled")

        if not self.tabs[self.activeButton]:
            self.tabs[self.activeButton] = globals()[self.classNames[self.activeButton].__name__](self)

        self.tabs[self.activeButton].place(x = 200, y = 0, anchor = "nw")

        if self.activeButton == 9:
            self.tabs[self.activeButton].updateSettings()
        elif self.activeButton == 3:
            self.tabs[self.activeButton].updateCalendar()
        elif self.activeButton == 1:
            self.tabs[self.activeButton].resetOpenEmail()

    def addDate(self):

        if self.dayLabel:
            self.dayLabel.destroy()
            self.timeLabel.destroy()
            self.continueButton.destroy()

        currDate = Game.get_game_date(self.manager_id)
        day, text, time = format_datetime_split(currDate)

        self.dayLabel = ctk.CTkLabel(self.tabsFrame, text = day, font = (APP_FONT, 13), text_color = "white", fg_color = TKINTER_BACKGROUND)
        self.dayLabel.place(relx = 0.03, rely = 0.86, anchor = "w")
        self.timeLabel = ctk.CTkLabel(self.tabsFrame, text = f"{text} {time}", font = (APP_FONT_BOLD, 13), text_color = "white", fg_color = TKINTER_BACKGROUND)
        self.timeLabel.place(relx = 0.03, rely = 0.89, anchor = "w")

        gameTime = Matches.check_if_game_time(self.team.id, currDate)

        if not gameTime:
            self.continueButton = ctk.CTkButton(self.tabsFrame, text = "Continue >>", font = (APP_FONT_BOLD, 15), text_color = "white", fg_color = APP_BLUE, corner_radius = 10, height = 50, width = 127, hover_color = APP_BLUE, command = self.moveDate)
            self.continueButton.place(relx = 0.32, rely = 0.99, anchor = "sw")
        else:
            self.continueButton = ctk.CTkButton(self.tabsFrame, text = "Matchday >>", font = (APP_FONT_BOLD, 15), text_color = "white", fg_color = PIE_RED, corner_radius = 10, height = 50, width = 127, hover_color = PIE_RED, command = lambda: self.changeTab(4))
            self.continueButton.place(relx = 0.32, rely = 0.99, anchor = "sw")

            if self.tabs[4]:
                self.tabs[4].turnSubsOn()

    def moveDate(self):
        self.currDate = Game.get_game_date(self.manager_id)
        teamIDs = Teams.get_all_teams()

        dates = []
        dates.append(Matches.get_team_next_match(self.team.id, self.currDate).date)
        dates.append(Emails.get_next_email(self.currDate).date)
        stopDate = min(dates)
        overallTimeInBetween = stopDate - self.currDate

        # ------------------- Creating calendar events for other teams -------------------
        current_day = self.currDate # + timedelta(days = 1)
        while current_day.date() <= stopDate.date():
            if current_day.weekday() == 0:
                monday_moment = datetime.datetime(current_day.year, current_day.month, current_day.day, 8, 59)
                if monday_moment > self.currDate and monday_moment <= stopDate:
                    for team_id in teamIDs:
                        if team_id != self.team.id or Settings.get_setting("events_delegated"):
                            create_events_for_other_teams(team_id, current_day, managing_team = team_id == self.team.id)
            current_day += timedelta(days = 1)

        # -------------------Figuring out intervals -------------------

        intervals = self.getIntervals(self.currDate, stopDate, teamIDs)

        # ------------------- Update player attributes and carry out events -------------------

        for start, end in intervals:
            timeInBetween = end - start

            for teamID in teamIDs:
                events = CalendarEvents.get_events_dates(teamID, start, end)

                if len(events) == 0:
                    Players.update_sharpness_and_fitness(timeInBetween, teamID)
                    continue

                for event in events:
                    self.carryOutEvent(event)
                    CalendarEvents.update_event(event.id)

            PlayerBans.reduce_injuries(timeInBetween, stopDate)

        update_ages(self.currDate, stopDate)

        # ------------------- Matches simulation -------------------

        if self.tabs[4]:
            SavedLineups.delete_current_lineup()
            self.tabs[4].saveLineup()

        matches = []
        matchesToSim = Matches.get_matches_time_frame(self.currDate, stopDate)
        if matchesToSim:
            # Phase 1: create all Match objects
            for game in matchesToSim:
                try:
                    match = Match(game, auto = True)  # init only
                    matches.append(match)
                except Exception as e:
                    traceback.print_exc()
                    print(e)

            # Phase 2: run startGame in parallel with ThreadPoolExecutor
            with ThreadPoolExecutor(max_workers = len(matches)) as ex:
                # submit a wrapper that starts the match thread and then joins it
                def _run_and_join(m):
                    m.startGame()
                    m.join()
                
                futures = [ex.submit(_run_and_join, match) for match in matches]

                # Phase 3: wait for all to finish
                for fut in as_completed(futures):
                    try:
                        fut.result()
                    except Exception as e:
                        traceback.print_exc()
                        print(e)

        self.currDate += overallTimeInBetween
        Game.increment_game_date(self.manager_id, overallTimeInBetween)

        # ------------------- Post-match updates -------------------

        leagueIDs = list({match.league.league_id for match in matches})
        for id_ in leagueIDs:
            LeagueTeams.update_team_positions(id_)
            if League.check_all_matches_complete(id_, self.currDate):
                for team in LeagueTeams.get_teams_by_league(id_):
                    matchday = League.get_current_matchday(id_)
                    TeamHistory.add_team(matchday, team.team_id, team.position, team.points)

                League.update_current_matchday(id_)   

        teams = []
        for match in matches:
            teams.append(match.homeTeam)
            teams.append(match.awayTeam)

        check_player_games_happy(teams, self.currDate)

        # ------------------- Reset/End -------------------

        self.resetTabs(0, 1, 2, 3, 4, 5, 6)
        self.addDate()

    def getIntervals(self, start_date, end_date, teamIDs):
        intervals = set()

        for team_id in teamIDs:
            teamEvents = CalendarEvents.get_events_dates(team_id, start_date, end_date)
            for event in teamEvents:
                intervals.add((event.start_date, event.end_date))

        # Fill in gaps between intervals
        intervals = sorted(intervals)
        numIntervals = len(intervals)
        for i in range(numIntervals):
            _, currIntervalEnd = intervals[i]

            if i + 1 >= numIntervals:
                break

            nextIntervalStart, _ = intervals[i + 1]
            if currIntervalEnd != nextIntervalStart:
                intervals.insert(i + 1, (currIntervalEnd, nextIntervalStart))
                numIntervals += 1

        # Add the start and end dates
        if len(intervals) != 0:
            intervals.insert(0, (start_date, intervals[0][0]))
            intervals.append((intervals[-1][1], end_date))
        else:
            intervals.append((start_date, end_date))

        # Insert injury intervals
        injuries = PlayerBans.get_injuries_dates(start_date, end_date)
        for inj in injuries:
            for i in range(len(intervals)):
                start, end = list(intervals)[i]
                injuryDate = inj.injury
                if start <= injuryDate <= end:
                    intervals.remove((start, end))
                    intervals.append((start, injuryDate))
                    intervals.append((injuryDate, end))
                    break

        return sorted(intervals)

    def carryOutEvent(self, event):
        team = Teams.get_team_by_id(event.team_id)
        updateStats = True
        match event.event_type:
            case "Light Training":
                Players.update_sharpness_and_fitness_with_values(team.id, -5, 5)
                updateStats = False
            case "Medium Training":
                Players.update_sharpness_and_fitness_with_values(team.id, -12, 10)
                updateStats = False
            case "Intense Training":
                Players.update_sharpness_and_fitness_with_values(team.id, -20, 15)
                updateStats = False
            case "Team Building":
                Players.update_morale_with_values(team.id, random.randint(5, 10))
            case "Recovery":
                Players.update_sharpness_and_fitness_with_values(team.id, 20, 0)
                updateStats = False

        if updateStats:
            Players.update_sharpness_and_fitness(event.end_date - event.start_date, team.id)

    def resetMenu(self):
        
        for tab in self.tabs:
            if tab:
                tab.destroy()

        self.tabsFrame.destroy()
        self.initUI()

    def resetTabs(self, *tab_indices):
        for i in tab_indices:
            if self.tabs[i]:
                self.tabs[i].destroy()
                self.tabs[i] = None

        if self.activeButton in tab_indices:
            self.tabs[self.activeButton] = globals()[self.classNames[self.activeButton].__name__](self)
            self.tabs[self.activeButton].place(x = 200, y = 0, anchor = "nw")

        for frame in self.overlappingProfiles:
            if frame.winfo_exists():
                frame.place_forget()

        self.overlappingProfiles = []