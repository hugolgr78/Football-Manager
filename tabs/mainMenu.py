import gc, traceback, logging, time, os
import customtkinter as ctk
from settings import *
from data.database import *
from data.gamesDatabase import *
from PIL import Image
from utils.util_functions import *
from concurrent.futures import ProcessPoolExecutor, as_completed, ThreadPoolExecutor

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

def _simulate_match(game, manager_base_name):

    base_name = manager_base_name
    dbm = DatabaseManager()
    dbm.set_database(base_name)
    try:
        per_process_copy = f"data/{base_name}_copy_{os.getpid()}.db"
        dbm.copy_path = per_process_copy
        dbm.start_copy()
    except Exception:
        logging.getLogger(__name__).exception("Failed to start DB copy for manager %s", base_name)

    match = Match(game, auto=True)
    match.startGame()
    match.join()

    try:
        if dbm.scoped_session:
            dbm.scoped_session.remove()
    except Exception:
        pass
    try:
        if dbm.engine:
            dbm.engine.dispose()
    except Exception:
        pass
    gc.collect()

    if 'per_process_copy' in locals() and per_process_copy and os.path.exists(per_process_copy):
        try:
            os.remove(per_process_copy)
            logging.getLogger(__name__).debug("Removed per-process DB copy %s", per_process_copy)
        except Exception:
            logging.getLogger(__name__).exception("Failed to remove per-process DB copy %s", per_process_copy)

    result = {
        "id": getattr(game, "id", None),
        "score": match.score,
    }

    return result
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

        # instance logger
        self._logger = logging.getLogger(__name__)

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
    
        def run_match_simulation(self, stopDate):
            matches = []
            matchesToSim = Matches.get_matches_time_frame(self.currDate, stopDate)
            if matchesToSim:
                self._logger.info("Preparing to simulate %d matches", len(matchesToSim))
                self._logger.info("Starting match initialization")

                self._logger.info("Starting parallel match simulation with %d workers", max(1, len(matchesToSim)))

                sim_start = time.perf_counter()

                # Run in ProcessPoolExecutor
                matches = []
                with ProcessPoolExecutor(max_workers=len(matchesToSim)) as ex:
                    # compute base name once (we're on the main process and DB is already set)
                    mgr = Managers.get_manager_by_id(self.manager_id)
                    base_name = f"{mgr.first_name}{mgr.last_name}"
                    futures = [ex.submit(_simulate_match, g, base_name) for g in matchesToSim]

                    for fut in as_completed(futures):
                        try:
                            result = fut.result()
                            matches.append(Matches.get_match_by_id(result["id"]))
                            self._logger.info("Finished match %s with score %s", result["id"], result["score"])
                        except Exception:
                            self._logger.exception("Match worker raised an exception")
                            traceback.print_exc()

                sim_end = time.perf_counter()

                elapsed = sim_end - sim_start
                self._logger.info("Match smulation completed in %.3f seconds for %d matches", elapsed, len(matchesToSim))

            return matches

        db = DatabaseManager()
        db.start_copy()

        self.currDate = Game.get_game_date(self.manager_id)
        self._logger.debug("moveDate start - manager_id=%s currDate=%s", self.manager_id, self.currDate)
        teamIDs = Teams.get_all_teams()

        dates = []
        dates.append(Matches.get_team_next_match(self.team.id, self.currDate).date)
        dates.append(Emails.get_next_email(self.currDate).date)
        stopDate = min(dates)
        overallTimeInBetween = stopDate - self.currDate
        self._logger.debug("Computed stopDate=%s overallTimeInBetween=%s", stopDate, overallTimeInBetween)

        # ------------------- Creating calendar events for other teams -------------------
        self._logger.info("Starting calendar events generation from %s to %s", self.currDate, stopDate)
        
        current_day = self.currDate
        createEvents = False
        while current_day.date() <= stopDate.date():
            if current_day.weekday() == 0:
                monday_moment = datetime.datetime(current_day.year, current_day.month, current_day.day, 8, 59)
                if monday_moment > current_day and monday_moment <= stopDate:
                    createEvents = True
                    break
            current_day += timedelta(days = 1)

        if createEvents:
            team_list = list(teamIDs)
            if not Settings.get_setting("events_delegated") and self.team.id in team_list:
                team_list.remove(self.team.id)

            max_workers = len(team_list)
            with ThreadPoolExecutor(max_workers = max_workers) as ex:
                self._logger.info("Preparing futures for creating calendar events (count=%d)", len(team_list))
                futures = [ex.submit(create_events_for_other_teams, team_id, current_day, managing_team = team_id == self.team.id) for team_id in team_list]
                self._logger.info("Prepared futures for creating calendar events")

                for fut in as_completed(futures):
                    try:
                        fut.result()
                        self._logger.info("Finished creating events for a team")
                    except Exception:
                        self._logger.exception("Calendar events worker raised an exception")

        self._logger.debug("Created/checked calendar events between %s and %s for %d teams", self.currDate, stopDate, len(teamIDs))

        # -------------------Figuring out intervals -------------------

        self._logger.debug("Computing intervals between %s and %s for %d teams", self.currDate, stopDate, len(teamIDs))
        intervals = self.getIntervals(self.currDate, stopDate, teamIDs)
        self._logger.debug("Computed intervals count=%d", len(intervals))

        # ------------------- Update player attributes and carry out events -------------------

        self._logger.info("Starting player attribute updates and event processing across %d intervals", len(intervals))

        for teamID in teamIDs:
            team_start = time.perf_counter()
            injuredPlayers = PlayerBans.get_team_injured_player_ids(teamID)
            playerFitnesses = {player.id: [player.fitness, True if player.id in injuredPlayers else False] for player in Players.get_all_players_by_team(teamID, youths = False)}
            playerSharpnesses = {player.id: player.sharpness for player in Players.get_all_players_by_team(teamID, youths = False)}
            playerMorales = {player.id: player.morale for player in Players.get_all_players_by_team(teamID, youths = False)}

            for start, end in intervals:
                timeInBetween = end - start

                eventsToUpdate = []
                events = CalendarEvents.get_events_dates(teamID, start, end)

                if len(events) == 0:
                    self._logger.debug("No calendar events for team %s in interval %s - %s: updating sharpness/fitness", teamID, start, end)
                    apply_attribute_changes(playerFitnesses, playerSharpnesses, timeInBetween)
                    continue

                for event in events:
                    eventsToUpdate.append(event.id)
                    self._logger.debug("Carrying out event %s for team %s", event.event_type, teamID)
                    if event.event_type == "Team Building":
                        update_dict_values(playerMorales, 20, 0, 100)
                    elif event.event_type in EVENT_CHANGES.keys():
                        fitness, sharpness = EVENT_CHANGES[event.event_type]
                        update_fitness_dict_values(playerFitnesses, fitness, 0, 100)
                        update_dict_values(playerSharpnesses, sharpness, 10, 100)
        
            CalendarEvents.batch_update_events(eventsToUpdate)
            PlayerBans.reduce_injuries_for_team(timeInBetween, stopDate, teamID)
            Players.batch_update_player_stats(playerFitnesses, playerSharpnesses, playerMorales)

            team_elapsed = time.perf_counter() - team_start
            self._logger.info("Finished processing team %s in %.3f seconds", teamID, team_elapsed)

        update_ages(self.currDate, stopDate)
        self._logger.debug("Updated player ages between %s and %s", self.currDate, stopDate)

        # ------------------- Matches simulation -------------------

        if self.tabs[4]:
            SavedLineups.delete_current_lineup()
            self.tabs[4].saveLineup()
    
        matches = run_match_simulation(self, stopDate)

        self.currDate += overallTimeInBetween
        Game.increment_game_date(self.manager_id, overallTimeInBetween)
        self._logger.debug("Updated game date to %s with %s difference", self.currDate, overallTimeInBetween)

        # ------------------- Post-match updates -------------------

        leagueIDs = list({match.league_id for match in matches})
        for id_ in leagueIDs:
            LeagueTeams.update_team_positions(id_)
            if League.check_all_matches_complete(id_, self.currDate):
                for team in LeagueTeams.get_teams_by_league(id_):
                    matchday = League.get_current_matchday(id_)
                    TeamHistory.add_team(matchday, team.team_id, team.position, team.points)

                League.update_current_matchday(id_)   

        teams = []
        for match in matches:
            teams.append(Teams.get_team_by_id(match.home_id))
            teams.append(Teams.get_team_by_id(match.away_id))

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