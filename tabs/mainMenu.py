import threading
import logging, time
import customtkinter as ctk
from settings import *
from data.database import *
from data.gamesDatabase import *
from PIL import Image
from utils.util_functions import *
from concurrent.futures import as_completed, ThreadPoolExecutor

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

class MainMenu(ctk.CTkFrame):
    def __init__(self, parent, manager_id, created):
        """
        Main menu frame containing all tabs and navigation.

        Args:
            parent (ctk.CTk): The parent tkinter frame.
            manager_id (str): The ID of the user manager.
            created (bool): Flag indicating if a new game was created.
        """

        super().__init__(parent, fg_color = TKINTER_BACKGROUND)
        self.pack(fill = "both", expand = True)

        self.parent = parent
        self.manager_id = manager_id
        self.movingDate = False

        if created:
            # If the game was just created, commit the copy to the main database
            db = DatabaseManager()
            db.commit_copy()

        self.team = Teams.get_teams_by_manager(self.manager_id)[0]

        self.initUI()

    def initUI(self):
        """
        Initializes the main menu UI components.
        """

        self.overlappingProfiles = []
        self.emailsAdded = False

        # Initialize the Hub tab
        self.hub = Hub(self)
        self.hub.place(x = 200, y = 0, anchor = "nw")

        # Initialize all other tab objects as None        
        self.inbox = None
        self.squad = None
        self.schedule = None
        self.tactics = None
        self.teamProfile = None
        self.leagueProfile = None
        self.managerProfile = None
        self.search = None
        self.settings = None

        # Set up for the tab system
        self.activeButton = 0
        self.buttons = []
        self.titles = ["  Main Hub", "  Inbox", "  Squad", "  Schedule", "  Tactics", "  Club", "  League", "  Profile", "  Search"]
        self.tabs = [self.hub, self.inbox, self.squad, self.schedule, self.tactics, self.teamProfile, self.leagueProfile, self.managerProfile, self.search, self.settings]
        self.classNames = [Hub, Inbox, Squad, Schedule, Tactics, TeamProfile, LeagueProfile, ManagerProfile, Search, SettingsTab]

        self.tabsFrame = ctk.CTkFrame(self, fg_color = TKINTER_BACKGROUND, width = 200, height = 700)
        self.tabsFrame.place(x = 0, y = 0, anchor = "nw")

        self.movingFrame = ctk.CTkFrame(self, fg_color = TKINTER_BACKGROUND, width = 1000, height = 200)
        self.movingFrame.place(relx = 0, rely = -1.0, anchor = "nw")

        self.bottom_border = ctk.CTkFrame(self.movingFrame, height = 2, width = 1000, fg_color = APP_BLUE)
        self.bottom_border.place(relx = 0, rely = 1, anchor = "sw")  

        # Set up for the progress bar when moving date
        self.progressBar = ctk.CTkProgressBar(
            self.movingFrame,
            width = 900,
            height = 40,
            fg_color = GREY_BACKGROUND,     
            progress_color = APP_BLUE,     
            corner_radius = 0               
        )   
        self.progressBar.place(relx = 0.02, rely = 0.55, anchor = "w")
        self.progressBar.set(0)
        self.completedSteps = 0

        self.progressLabel = ctk.CTkLabel(self.movingFrame, text = "0%", font = (APP_FONT_BOLD, 15), text_color = "white", fg_color = TKINTER_BACKGROUND)
        self.progressLabel.place(relx = 0.97, rely = 0.55, anchor = "e")

        self.dateLabel = ctk.CTkLabel(self.movingFrame, text = f"", font = (APP_FONT_BOLD, 25), text_color = "white", fg_color = TKINTER_BACKGROUND)
        self.dateLabel.place(relx = 0.02, rely = 0.12, anchor = "w")
        self.textTimeLabel = ctk.CTkLabel(self.movingFrame, text = f"", font = (APP_FONT, 20), text_color = "white", fg_color = TKINTER_BACKGROUND)
        self.textTimeLabel.place(relx = 0.02, rely = 0.27, anchor = "w")

        self.tip = random.choice(TIPS)
        self.tipLabel = ctk.CTkLabel(self.movingFrame, text = f"Tip: {self.tip}", font = (APP_FONT, 15), text_color = "white", fg_color = TKINTER_BACKGROUND)
        self.tipLabel.place(relx = 0.02, rely = 0.82, anchor = "w")

        src = Image.open("Images/Loading/1.png")
        src.thumbnail((50, 50))
        img = ctk.CTkImage(src, None, (src.width, src.height))
        self.loadingImage = ctk.CTkLabel(self.movingFrame, image = img, text = "", fg_color = TKINTER_BACKGROUND)
        self.loadingImage.place(relx = 0.96, rely = 0.22, anchor = "e")

        self.loadingImages = [Image.open(f"Images/Loading/{i}.png") for i in range(1, 31)]
        self.loadingObjects = []
        for image in self.loadingImages:
            image.thumbnail((50, 50))
            ctkImage = ctk.CTkImage(image, None, (image.width, image.height))
            self.loadingObjects.append(ctkImage)

        self.loadingIndex = 0

        canvas = ctk.CTkCanvas(self, width = 5, height = 1000, bg = APP_BLUE, bd = 0, highlightthickness = 0)
        canvas.place(x = 245, y = 0, anchor = "nw")

        self.dayLabel = None
        self.timeLabel = None
        self.continueButton = None

        self.createTabs()
        self.addDate()
        self.addInboxNotification()

        # instance logger
        self._logger = logging.getLogger(__name__)

    def createTabs(self):
        """
        Creates the tabs on the side menu.
        """

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

        # Add all the tab buttons on the side menu
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

        inboxButton = self.buttons[1]
        inboxButton.bind("<Enter>", lambda e: self.onHoverInbox())
        inboxButton.bind("<Leave>", lambda e: self.onLeaveInbox())

        src = Image.open("Images/player_bad.png")
        src.thumbnail((10, 10))
        img = ctk.CTkImage(src, None, (src.width, src.height))
        self.inboxNotification = ctk.CTkLabel(inboxButton, image = img, text = "", fg_color = TKINTER_BACKGROUND)
        self.inboxNotification.bind("<Button-1>", lambda e: self.changeTab(1))
        self.inboxNotification.bind("<Enter>", lambda e: self.onHoverInbox())

    def onHoverInbox(self):
        """
        Event handler for when the mouse hovers over the Inbox button.
        """

        self.buttons[1].configure(fg_color = GREY_BACKGROUND)

        if self.inboxNotification.winfo_ismapped():
            self.inboxNotification.configure(fg_color = GREY_BACKGROUND)

    def onLeaveInbox(self):
        """
        Event handler for when the mouse leaves the Inbox button.
        """

        self.buttons[1].configure(fg_color = TKINTER_BACKGROUND)

        if self.inboxNotification.winfo_ismapped():
            self.inboxNotification.configure(fg_color = TKINTER_BACKGROUND)

    def canvas(self, width, height, rely):
        """
        Helper function to create a canvas separator.
        """

        canvas = ctk.CTkCanvas(self.tabsFrame, width = width, height = height, bg = GREY_BACKGROUND, bd = 0, highlightthickness = 0)
        canvas.place(relx = 0.5, rely = rely, anchor = "center")

    def changeTab(self, index):
        """
        Changes the active tab to the specified index.

        Args:
            index (int): The index of the tab to switch to.
        """

        # Reset the old tab as normal and hide it
        self.buttons[self.activeButton].configure(state = "normal")
        self.tabs[self.activeButton].place_forget()

        # Reset the overlapping profile frames
        for frame in self.overlappingProfiles:
            frame.place_forget()

        # Set the new tab as active and show it
        self.activeButton = index
        self.buttons[self.activeButton].configure(state = "disabled")

        # Create the tab if it doesn't exist, then show it
        if not self.tabs[self.activeButton]:
            self.tabs[self.activeButton] = globals()[self.classNames[self.activeButton].__name__](self)
        self.tabs[self.activeButton].place(x = 200, y = 0, anchor = "nw")

        # Update specific tabs if needed
        if self.activeButton == 9:
            self.tabs[self.activeButton].updateSettings()
        elif self.activeButton == 3:
            self.tabs[self.activeButton].updateCalendar()
        elif self.activeButton == 1:
            self.tabs[self.activeButton].resetOpenEmail()

    def addInboxNotification(self):
        """
        Adds a small red dot next to the Inbox tab title to indicate new messages.
        """

        if self.inboxNotification.winfo_ismapped():
            return
        
        emails = Emails.get_all_emails(Game.get_game_date(self.manager_id))
        hasUnread = any(not email.read for email in emails)

        if not hasUnread:
            return
            
        self.inboxNotification.place(relx = 0.94, rely = 0, anchor = "ne")

    def removeInboxNotification(self):
        """
        Removes the red dot notification from the Inbox tab title.
        """

        if not self.inboxNotification.winfo_ismapped():
            return
        
        self.inboxNotification.place_forget()

    def addDate(self):
        """
        Adds the current game date display and continue/matchday button.
        """

        if self.dayLabel:
            self.dayLabel.destroy()
            self.timeLabel.destroy()
            self.continueButton.destroy()

        self.currDate = Game.get_game_date(self.manager_id)
        day, text, time = format_datetime_split(self.currDate)

        self.dayLabel = ctk.CTkLabel(self.tabsFrame, text = day, font = (APP_FONT_BOLD, 13), text_color = "white", fg_color = TKINTER_BACKGROUND)
        self.dayLabel.place(relx = 0.03, rely = 0.86, anchor = "w")
        self.timeLabel = ctk.CTkLabel(self.tabsFrame, text = f"{text} {time}", font = (APP_FONT_BOLD, 13), text_color = "white", fg_color = TKINTER_BACKGROUND)
        self.timeLabel.place(relx = 0.03, rely = 0.89, anchor = "w")

        gameTime = Matches.check_if_game_time(self.team.id, self.currDate)

        # Set the continue or matchday button based on whether it's game time
        if not gameTime:
            self.continueButton = ctk.CTkButton(self.tabsFrame, text = "Continue >>", font = (APP_FONT_BOLD, 15), text_color = "white", fg_color = APP_BLUE, corner_radius = 10, height = 50, width = 127, hover_color = APP_BLUE, command = self.showProgressBar)
            self.continueButton.place(relx = 0.32, rely = 0.99, anchor = "sw")
        else:
            self.continueButton = ctk.CTkButton(self.tabsFrame, text = "Matchday >>", font = (APP_FONT_BOLD, 15), text_color = "white", fg_color = PIE_RED, corner_radius = 10, height = 50, width = 127, hover_color = PIE_RED, command = lambda: self.changeTab(4))
            self.continueButton.place(relx = 0.32, rely = 0.99, anchor = "sw")

            if self.tabs[4]:
                self.tabs[4].turnSubsOn()

    def showProgressBar(self):
        """
        Displays the progress bar and starts moving the date forward.
        """

        day, text, _ = format_datetime_split(self.currDate)
        self.configureMovingFrame(day, text)
        self.addMovingFrame()

    def moveDate(self):
        """
        Moves the game date forward. Will create calendar events, update player attributes, and simulate matches as needed.
        """

        self.movingDate = True
    
        db = DatabaseManager()
        db.start_copy()

        self.currDate = Game.get_game_date(self.manager_id)
        self._logger.debug("moveDate start - manager_id=%s currDate=%s", self.manager_id, self.currDate)

        # Filter teams to only those in loaded leagues
        leagues = League.get_all_leagues()
        loaded_leagues = [league.id for league in leagues if league.loaded]
        teamIDs = [t.id for t in Teams.get_all_teams() if LeagueTeams.get_league_by_team(t.id).league_id in loaded_leagues]
        self._logger.debug("Filtered teamIDs to %d teams in loaded leagues", len(teamIDs))

        # Stop date is the earliest of next match or next email
        gameDate = Matches.get_team_next_match(self.team.id, self.currDate).date
        emailDate = Emails.get_next_email(self.currDate).date
        stopDate = min(gameDate, emailDate)
        overallTimeInBetween = stopDate - self.currDate
        self._logger.debug("Computed stopDate=%s overallTimeInBetween=%s", stopDate, overallTimeInBetween)

        # ------------------- Checking if we need to create events -------------------
        self._logger.info("Starting calendar events generation from %s to %s", self.currDate, stopDate)
        
        # Checking if we are going past a monday at 8.59am
        current_day = self.currDate
        createEvents = False
        while current_day.date() <= stopDate.date():
            if current_day.weekday() == 0:
                monday_moment = datetime.datetime(current_day.year, current_day.month, current_day.day, 8, 59)
                if monday_moment > current_day and monday_moment <= stopDate:
                    createEvents = True
                    break
            current_day += timedelta(days = 1)

        # ------------------- Counting total steps for progress bar -------------------
        self.totalSteps = 0

        if createEvents:
            self.totalSteps += len(teamIDs) # for calendar event creations
        
        self.totalSteps += len(teamIDs)  # for player attribute updates
        matchesToSim = Matches.get_matches_time_frame(self.currDate, stopDate)

        if matchesToSim:
            self.totalSteps += len(matchesToSim)  # for match simulations

        # ------------------- Creating calendar events for other teams -------------------

        if createEvents:
            team_list = teamIDs.copy()
            self._logger.info("Creating calendar events for %d teams", len(team_list))
            if not Settings.get_setting("events_delegated") and self.team.id in team_list:
                team_list.remove(self.team.id)

            max_workers = len(team_list)
            all_events_to_add = []
            with ThreadPoolExecutor(max_workers = max_workers) as ex:
                self._logger.info("Preparing futures for creating calendar events (count=%d)", len(team_list))
                futures = [ex.submit(create_events_for_other_teams, team_id, current_day, managing_team = team_id == self.team.id) for team_id in team_list]
                self._logger.info("Prepared futures for creating calendar events")

                for fut in as_completed(futures):
                    try:
                        events = fut.result()
                        if events:
                            all_events_to_add.extend(events)
                        self._logger.info("Finished creating events for a team (returned %d events)", len(events) if events else 0)
                        self.updateProgressBar()
                    except Exception:
                        self._logger.exception("Calendar events worker raised an exception")
            try:
                if all_events_to_add:
                    CalendarEvents.batch_add_events(all_events_to_add)
                    self._logger.info("Batch-added %d calendar events", len(all_events_to_add))
            except Exception:
                self._logger.exception("Failed to batch-add calendar events")

        self._logger.debug("Created/checked calendar events between %s and %s for %d teams", self.currDate, stopDate, len(teamIDs))

        # -------------------Figuring out intervals -------------------

        self._logger.debug("Computing intervals between %s and %s for %d teams", self.currDate, stopDate, len(teamIDs))
        intervals = self.getIntervals(self.currDate, stopDate, teamIDs)
        self._logger.debug("Computed intervals count=%d", len(intervals))

        # ------------------- Update player attributes and carry out events ------------

        self._logger.info("Starting player attribute updates and event processing across %d intervals", len(intervals))

        def _process_team(teamID):
            start_time = time.perf_counter()
            try:
                # Set up the player attribute dictionaries
                injuredPlayers = PlayerBans.get_team_injured_player_ids(teamID)
                players = Players.get_all_players_by_team(teamID, youths = False)

                playerFitnesses = {player.id: [player.fitness, True if player.id in injuredPlayers else False] for player in players}
                playerSharpnesses = {player.id: player.sharpness for player in players}
                playerMorales = {player.id: player.morale for player in players}

                events_to_update = []
                reduce_intervals = []

                for start, end in intervals:
                    timeInBetween = end - start

                    events = CalendarEvents.get_events_dates(teamID, start, end)

                    if len(events) == 0:
                        # No events: update sharpness/fitness for the interval
                        apply_attribute_changes(playerFitnesses, playerSharpnesses, timeInBetween)
                        continue

                    for event in events:
                        # Update the player attributes based on the event type
                        events_to_update.append(event.id)
                        if event.event_type == "Team Building":
                            update_dict_values(playerMorales, 10, 0, 100)
                        elif event.event_type in EVENT_CHANGES.keys():
                            fitness, sharpness = EVENT_CHANGES[event.event_type]
                            update_fitness_dict_values(playerFitnesses, fitness, 0, 100)
                            update_dict_values(playerSharpnesses, sharpness, 10, 100)

                    # Record interval to later reduce injuries for this team
                    reduce_intervals.append(timeInBetween)

                elapsed = time.perf_counter() - start_time
                self._logger.info("Finished preparing team %s in %.3f seconds", teamID, elapsed)

                return {
                    'team_id': teamID,
                    'events': events_to_update,
                    'fitness': playerFitnesses,
                    'sharpness': playerSharpnesses,
                    'morale': playerMorales,
                    'reduce_intervals': reduce_intervals,
                }
            except Exception:
                self._logger.exception("Error while processing team %s", teamID)
                return {
                    'team_id': teamID,
                    'events': [],
                    'fitness': {},
                    'sharpness': {},
                    'morale': {},
                    'reduce_intervals': [],
                }

        # Run workers in a ThreadPoolExecutor (reads and in-memory computations)
        combined_events = []
        combined_fitness = {}
        combined_sharpness = {}
        combined_morale = {}
        reduce_tasks = []

        with ThreadPoolExecutor(max_workers = len(teamIDs)) as ex:
            futures = {ex.submit(_process_team, tid): tid for tid in teamIDs}

            for fut in as_completed(futures):
                res = fut.result()

                # Aggregate events
                combined_events.extend(res.get('events', []))
                combined_fitness.update(res.get('fitness', {}))
                combined_sharpness.update(res.get('sharpness', {}))
                combined_morale.update(res.get('morale', {}))

                # collect reduce intervals to call PlayerBans.reduce_injuries_for_team in main thread
                if res.get('reduce_intervals'):
                    reduce_tasks.append((res['team_id'], res['reduce_intervals']))

                self.updateProgressBar()

        # After all workers finished, perform DB writes in main thread (timed)
        try:
            if combined_events:
                unique_events = list(set(combined_events))
                CalendarEvents.batch_update_events(unique_events)
            self._logger.info("Applied batch calendar event updates via CalendarEvents.batch_update_events")

            if combined_fitness or combined_sharpness or combined_morale:
                Players.batch_update_player_stats(combined_fitness, combined_sharpness, combined_morale)
                self._logger.info("Applied batch player stats updates via Players.batch_update_player_stats")
                
            try:
                PlayerBans.batch_reduce_injuries(overallTimeInBetween, stopDate)
                self._logger.info("Applied batch injury reductions via PlayerBans.batch_reduce_injuries")
            except Exception:
                self._logger.exception("Failed to apply batch injury reductions")
        except Exception:
            self._logger.exception("Error applying batch DB updates for teams")

        # Update player ages
        update_ages(self.currDate, stopDate)
        self._logger.debug("Updated player ages between %s and %s", self.currDate, stopDate)

        # ------------------- Matches simulation -------------------

        if self.tabs[4]:
            SavedLineups.delete_current_lineup()
            self.tabs[4].saveLineup()
    
        run_match_simulation([self.currDate, stopDate], self.currDate, progress_callback = self.updateProgressBar)

        self.currDate += overallTimeInBetween
        Game.increment_game_date(self.manager_id, overallTimeInBetween)
        self._logger.debug("Updated game date to %s with %s difference", self.currDate, overallTimeInBetween)

        # ------------------- Reset/End -------------------

        self.addInboxNotification()
        self.progressBar.set(1.0)
        self.progressLabel.configure(text = "100%")
        self.dateLabel.configure(text = f"Date: {self.currDate}")
        self.removeMovingFrame()
        
    def getIntervals(self, start_date, end_date, teamIDs):
        """
        Get the intervals of events for the specified teams within the given date range.
        """

        intervals = set()

        # Aggregate all event intervals for the teams
        for team_id in teamIDs:
            teamEvents = CalendarEvents.get_events_dates(team_id, start_date, end_date)
            for event in teamEvents:
                intervals.add((event.start_date, event.end_date))

        # Fill in gaps between intervals (time in between events)
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

        # Insert injury intervals (any injuries that happen in between intervals will split the interval in two)
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
        """
        Reset the menu to its initial state by destroying all tabs and re-initializing the UI.
        """
    
        for tab in self.tabs:
            if tab:
                tab.destroy()

        self.tabsFrame.destroy()
        self.initUI()

    def resetTabs(self, *tab_indices):
        """
        Resets the specified tabs by destroying them and recreating the active tab if needed.
        """

        for i in tab_indices:
            if self.tabs[i]:
                self.tabs[i].destroy()
                self.tabs[i] = None

        # If resetting the active tab, recreate it
        if self.activeButton in tab_indices:
            self.tabs[self.activeButton] = globals()[self.classNames[self.activeButton].__name__](self)
            self.tabs[self.activeButton].place(x = 200, y = 0, anchor = "nw")

        # Reset overlapping profile frames
        for frame in self.overlappingProfiles:
            if frame.winfo_exists():
                frame.place_forget()

        self.overlappingProfiles = []

    def configureMovingFrame(self, day = None, text = None, tip = None):
        """
        Configures the moving frame with the specified date and time text.
        """

        if day:
            self.dateLabel.configure(text = f"{day}")
            self.textTimeLabel.configure(text = f"{text}")

        if tip:
            self.tipLabel.configure(text = f"Tip: {tip}")

        self.movingFrame.update_idletasks()

    def updateProgressBar(self):
        """
        Updates the progress bar during the date moving process.
        """

        self.completedSteps += 1
        progress = self.completedSteps / self.totalSteps
        self.progressBar.set(progress)
        self.progressLabel.configure(text = f"{int(progress * 100)}%")

        self.movingFrame.update_idletasks()

    def addMovingFrame(self):
        """
        Animates the moving frame into view and starts the date moving process.
        """

        self.movingFrame.lift()
        current_rely = float(self.movingFrame.place_info().get("rely"))
        target_rely = 0.0

        if current_rely < target_rely:
            new_rely = current_rely + 0.02
            self.movingFrame.place(x = 200, rely = new_rely, anchor = "nw")
            self.after(10, self.addMovingFrame)
        else:
            self.movingFrame.place(x = 200, rely = target_rely, anchor = "nw")
            self.animateID = self.after(0, self.animateLoadingImage)
            self.tipID = self.after(10000, self.changeTip)
            threading.Thread(target = self.moveDate, daemon = True).start()

    def removeMovingFrame(self):
        """
        Resets the moving frame to its initial state and resets tabs.
        """

        current_rely = float(self.movingFrame.place_info().get("rely"))
        target_rely = -1.0

        if current_rely > target_rely:
            new_rely = current_rely - 0.02
            self.movingFrame.place(x = 200, rely = new_rely, anchor = "nw")
            self.after(10, self.removeMovingFrame)
        else:
            self.movingFrame.place(x = 200, rely = target_rely, anchor = "nw")
            self.progressBar.set(0)
            self.completedSteps = 0
            self.progressLabel.configure(text = "0%")
            self.after_cancel(self.animateID)
            self.after_cancel(self.tipID)
            self.resetTabs(0, 1, 2, 3, 4, 5, 6)
            self.addDate()
            self.movingDate = False

    def animateLoadingImage(self):
        """
        Animates the loading image in the moving frame.
        """

        img = self.loadingObjects[self.loadingIndex]
        self.loadingImage.configure(image = img)

        self.loadingIndex = (self.loadingIndex + 1) % len(self.loadingObjects)
        self.movingFrame.update_idletasks()
        self.animateID = self.after(20, self.animateLoadingImage)
    
    def changeTip(self):

        tip = random.choice(TIPS)
        while self.tip == tip:
            tip = random.choice(TIPS)
        
        self.tip = tip
        self.configureMovingFrame(tip = self.tip)
        self.tipID = self.after(10000, self.changeTip)