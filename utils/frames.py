import customtkinter as ctk
import tkinter as tk
from settings import *
from data.database import *
from data.gamesDatabase import *
from PIL import Image, ImageDraw, ImageTk
import io, calendar
import tkinter.font as tkFont
from utils.teamLogo import TeamLogo
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from utils.playerProfileLink import PlayerProfileLink
from utils.match import Match
from utils.matchProfileLink import MatchProfileLink
from utils.util_functions import *
from utils.matchProfileLink import MatchProfileLink
from CTkMessagebox import CTkMessagebox

class MatchFrame(ctk.CTkFrame):
    def __init__(self, parent, manager_id, match, parentFrame, matchInfoFrame, parentTab):
        """
        Frame representing a single match, found in the schedule tab list form.
        
        Args:
            parent (ctk.CTkFrame): The parent frame.
            manager_id (str): The ID of the manager.
            match (Match): The match object.
            parentFrame (ctk.CTkFrame): The frame where this match frame will be placed.
            matchInfoFrame (ctk.CTkFrame): The frame to display match information.
            parentTab (ctk.CTkFrame): The parent tab containing this frame.
        """

        super().__init__(parentFrame, fg_color = TKINTER_BACKGROUND, width = 640, height = 50, corner_radius = 5)
        self.pack(expand = True, fill = "both", padx = 10, pady = (0, 10))

        self.bind("<Enter>", lambda event: self.onFrameHover())
        self.bind("<Leave>", lambda event: self.onFrameLeave())
        self.bind("<Button-1>", lambda event: self.displayMatchInfo())

        self.parent = parent
        self.parentFrame = parentFrame
        self.manager_id = manager_id
        self.match = match
        self.matchInfoFrame = matchInfoFrame
        self.parentTab = parentTab

        self.open = False
        self.played = False

        self.homeTeam = Teams.get_team_by_id(self.match.home_id)
        self.awayTeam = Teams.get_team_by_id(self.match.away_id) 

        if self.homeTeam.id == self.parent.team.id:
            self.home = True
            src = Image.open(io.BytesIO(self.awayTeam.logo))
        else:
            self.home = False
            src = Image.open(io.BytesIO(self.homeTeam.logo))

        src.thumbnail((35, 35))
        self.logo = TeamLogo(self, src, self.awayTeam if self.home else self.homeTeam, TKINTER_BACKGROUND, 0.05, 0.5, "center", self.parentTab)
        self.logo.getImageLabel().bind("<Enter>", lambda event: self.onFrameHover())

        self.oponent = ctk.CTkLabel(self, text = self.awayTeam.name if self.home else self.homeTeam.name, fg_color = TKINTER_BACKGROUND, font = (APP_FONT, 15), height = 0)
        self.oponent.place(relx = 0.1, rely = 0.35, anchor = "w")
        self.oponent.bind("<Enter>", lambda event: self.onFrameHover()) 
        self.oponent.bind("<Button-1>", lambda event: self.displayMatchInfo())

        _, dateText, time = format_datetime_split(self.match.date)
        self.date = ctk.CTkLabel(self, text = dateText, fg_color = TKINTER_BACKGROUND, font = (APP_FONT, 12), height = 0)
        self.date.place(relx = 0.1, rely = 0.65, anchor = "w")
        self.date.bind("<Enter>", lambda event: self.onFrameHover())
        self.date.bind("<Button-1>", lambda event: self.displayMatchInfo())

        self.leagueName = ctk.CTkLabel(self, text = self.parent.league.name, fg_color = TKINTER_BACKGROUND, font = (APP_FONT, 15))
        self.leagueName.place(relx = 0.45, rely = 0.5, anchor = "center")
        self.leagueName.bind("<Enter>", lambda event: self.onFrameHover())
        self.leagueName.bind("<Button-1>", lambda event: self.displayMatchInfo())

        self.time = ctk.CTkLabel(self, text = time, fg_color = TKINTER_BACKGROUND, font = (APP_FONT, 15))
        self.time.place(relx = 0.9, rely = 0.5, anchor = "e")
        self.time.bind("<Enter>", lambda event: self.onFrameHover())
        self.time.bind("<Button-1>", lambda event: self.displayMatchInfo())

        self.location = ctk.CTkLabel(self, text = "H" if self.home else "A", fg_color = TKINTER_BACKGROUND, font = (APP_FONT, 15))
        self.location.place(relx = 0.95, rely = 0.5, anchor = "e")
        self.location.bind("<Enter>", lambda event: self.onFrameHover())
        self.location.bind("<Button-1>", lambda event: self.displayMatchInfo())

        self.played = Matches.check_game_played(self.match, Game.get_game_date(Managers.get_all_user_managers()[0].id))
        if self.played:
            # If played, add the score and the result icon
            text = f"{self.match.score_home} - {self.match.score_away}" if self.home else f"{self.match.score_away} - {self.match.score_home}"
            self.score = ctk.CTkLabel(self, text = text, fg_color = TKINTER_BACKGROUND, font = (APP_FONT, 15))
            self.score.place(relx = 0.73, rely = 0.5, anchor = "center")
            self.score.bind("<Enter>", lambda event: self.onFrameHover())
            self.score.bind("<Button-1>", lambda event: self.displayMatchInfo())

            if self.home:
                self.result = "W" if self.match.score_home > self.match.score_away else "D" if self.match.score_home == self.match.score_away else "L"
            else:
                self.result = "W" if self.match.score_away > self.match.score_home else "D" if self.match.score_away == self.match.score_home else "L"

            if self.result == "W":
                src = Image.open("Images/game_win.png")
            elif self.result == "D":
                src = Image.open("Images/game_draw.png")
            else:
                src = Image.open("Images/game_lose.png")

            src.thumbnail((20, 20))
            ctk_image = ctk.CTkImage(src, None, (src.width, src.height))
            self.resultLabel = ctk.CTkLabel(self, image = ctk_image, text = "", fg_color = TKINTER_BACKGROUND)
            self.resultLabel.place(relx = 0.66, rely = 0.5, anchor = "center")
            self.resultLabel.bind("<Enter>", lambda event: self.onFrameHover())
            self.resultLabel.bind("<Button-1>", lambda event: self.displayMatchInfo())

    def onFrameHover(self):
        """
        Changes the frame and text color on hover.
        """
        
        self.configure(fg_color = DARK_GREY)
        self.logo.getImageLabel().configure(fg_color = DARK_GREY)
        self.oponent.configure(fg_color = DARK_GREY)
        self.leagueName.configure(fg_color = DARK_GREY)
        self.time.configure(fg_color = DARK_GREY)
        self.location.configure(fg_color = DARK_GREY)
        self.date.configure(fg_color = DARK_GREY)

        if self.played:
            self.score.configure(fg_color = DARK_GREY)
            self.resultLabel.configure(fg_color = DARK_GREY)

    def onFrameLeave(self):
        """
        Changes the frame and text color back to normal when not hovering.
        """

        self.configure(fg_color = TKINTER_BACKGROUND)
        self.logo.getImageLabel().configure(fg_color = TKINTER_BACKGROUND)
        self.oponent.configure(fg_color = TKINTER_BACKGROUND)
        self.leagueName.configure(fg_color = TKINTER_BACKGROUND)
        self.time.configure(fg_color = TKINTER_BACKGROUND)
        self.location.configure(fg_color = TKINTER_BACKGROUND)
        self.date.configure(fg_color = TKINTER_BACKGROUND)

        if self.played:
            self.score.configure(fg_color = TKINTER_BACKGROUND)
            self.resultLabel.configure(fg_color = TKINTER_BACKGROUND)

    def displayMatchInfo(self):
        """
        Displays detailed match information in the match info frame.
        """

        if self.open:
            return

        self.open = True

        if hasattr(self.parent, "frames"):
            # Checking if in list form or calendar form, as the calendar frame does not have frames attribute
            parentFrames = self.parent.frames
        else:
            parentFrames = self.parentTab.frames

        for otherMatchFrame in parentFrames:
            if otherMatchFrame != self:
                otherMatchFrame.open = False

        self.scoreFrame = ctk.CTkFrame(self.matchInfoFrame, fg_color = DARK_GREY, width = 260, height = 100, corner_radius = 10)
        self.scoreFrame.place(relx = 0.5, rely = 0.02, anchor = "n")

        srcHome = Image.open(io.BytesIO(self.homeTeam.logo))
        srcHome.thumbnail((50, 50))
        TeamLogo(self.scoreFrame, srcHome, self.homeTeam, DARK_GREY, 0.2, 0.5, "center", self.parentTab)

        srcAway = Image.open(io.BytesIO(self.awayTeam.logo))
        srcAway.thumbnail((50, 50))
        TeamLogo(self.scoreFrame, srcAway, self.awayTeam, DARK_GREY, 0.8, 0.5, "center", self.parentTab)

        if self.played:
            # Add the final score
            scoreLabel = MatchProfileLink(self.scoreFrame, self.match, f"{self.match.score_home} - {self.match.score_away}", "white", 0.5, 0.5, "center", DARK_GREY, self.parentTab, 30, APP_FONT_BOLD)
        else:
            # Otherwise, show the match time
            _, _, time = format_datetime_split(self.match.date)
            scoreLabel = ctk.CTkLabel(self.scoreFrame, text = time, fg_color = DARK_GREY, font = (APP_FONT, 30))
            scoreLabel.place(relx = 0.5, rely = 0.5, anchor = "center")
        
        self.matchdayEvents = MatchEvents.get_events_by_match(self.match.id)
        self.homeEvents = []
        self.awayEvents = []
        if self.played:
            for event in self.matchdayEvents:
                player = Players.get_player_by_id(event.player_id)
                if player.team_id == self.homeTeam.id:
                    if event.event_type == "own_goal":
                        self.awayEvents.append(event)
                    else:
                        self.homeEvents.append(event)
                elif player.team_id == self.awayTeam.id:
                    if event.event_type == "own_goal":
                        self.homeEvents.append(event)
                    else:
                        self.awayEvents.append(event)

            # remove all asissts and clean sheets
            self.homeEvents = [event for event in self.homeEvents if event.event_type != "assist" and event.event_type != "clean_sheet" and event.event_type != "penalty_saved" and event.event_type != "penalty_miss" and event.event_type != "sub_on" and event.event_type != "sub_off"]
            self.awayEvents = [event for event in self.awayEvents if event.event_type != "assist" and event.event_type != "clean_sheet" and event.event_type != "penalty_saved" and event.event_type != "penalty_miss" and event.event_type != "sub_on" and event.event_type != "sub_off"]

            self.homeLineup = TeamLineup.get_lineup_by_match_and_team(self.match.id, self.homeTeam.id)
            self.awayLineup = TeamLineup.get_lineup_by_match_and_team(self.match.id, self.awayTeam.id)

            if (max(len(self.homeLineup), len(self.awayLineup)) * 15) + (max(len(self.homeEvents), len(self.awayEvents)) * 30) > 410:
                # Create a scrollable frame if the content is too large
                self.eventsAndLineupsFrame = ctk.CTkScrollableFrame(self.matchInfoFrame, fg_color = DARK_GREY, width = 235, height = 420, corner_radius = 10)
                self.eventsAndLineupsFrame.place(relx = 0.5, rely = 0.203, anchor = "n")
            else:
                self.eventsAndLineupsFrame = ctk.CTkFrame(self.matchInfoFrame, fg_color = DARK_GREY, width = 260, height = 440, corner_radius = 10)
                self.eventsAndLineupsFrame.place(relx = 0.5, rely = 0.203, anchor = "n")
                self.eventsAndLineupsFrame.pack_propagate(False)
        else:
            self.eventsAndLineupsFrame = ctk.CTkFrame(self.matchInfoFrame, fg_color = DARK_GREY, width = 260, height = 440, corner_radius = 10)
            self.eventsAndLineupsFrame.place(relx = 0.5, rely = 0.203, anchor = "n")
            self.eventsAndLineupsFrame.pack_propagate(False)

        if self.played:
            self.matchEvents()
            self.lineups()

    def matchEvents(self):
        """
        Displays match events in the match info frame.
        """

        self.matchEventsFrame = ctk.CTkFrame(self.eventsAndLineupsFrame, fg_color = DARK_GREY, width = 235, height = max(len(self.homeEvents), len(self.awayEvents)) * 30)
        self.matchEventsFrame.pack(fill = "both", pady = 5)

        self.homeEventsFrame = ctk.CTkFrame(self.matchEventsFrame, fg_color = DARK_GREY, width = 120, height = len(self.homeEvents) * 30)
        self.homeEventsFrame.place(relx = 0, rely = 0, anchor = "nw")
        self.homeEventsFrame.pack_propagate(False)

        self.awayEventsFrame = ctk.CTkFrame(self.matchEventsFrame, fg_color = DARK_GREY, width = 120, height = len(self.awayEvents) * 30)
        self.awayEventsFrame.place(relx = 1, rely = 0, anchor = "ne")
        self.awayEventsFrame.pack_propagate(False)

        for event in self.homeEvents:
            self.addEvent(event, True, self.homeEventsFrame)

        for event in self.awayEvents:
            self.addEvent(event, False, self.awayEventsFrame)

    def addEvent(self, event, home, parent):
        """
        Adds a single event to the match events frame.
        """

        frame = ctk.CTkFrame(parent, fg_color = DARK_GREY, height = 30)
        frame.pack(fill = "x", expand = True)

        player = Players.get_player_by_id(event.player_id)

        if "+" in event.time:
            font = 9
            playerRelX = 0.35
        else:
            font = 10
            playerRelX = 0.25

        if home:
            ctk.CTkLabel(frame, text = event.time + "'", fg_color = DARK_GREY, font = (APP_FONT, font)).place(relx = 0.1, rely = 0.5, anchor = "w")
            ctk.CTkLabel(frame, text = player.last_name, fg_color = DARK_GREY, font = (APP_FONT, 10)).place(relx = playerRelX, rely = 0.5, anchor = "w")
        else:
            ctk.CTkLabel(frame, text = player.last_name, fg_color = DARK_GREY, font = (APP_FONT, 10)).place(relx = 1 - playerRelX, rely = 0.5, anchor = "e")
            ctk.CTkLabel(frame, text = event.time + "'", fg_color = DARK_GREY, font = (APP_FONT, font)).place(relx = 0.9, rely = 0.5, anchor = "e")

        if event.event_type == "goal":
            src = Image.open("Images/goal.png")
        elif event.event_type == "penalty_goal":
            src = Image.open("Images/penalty.png")
        elif event.event_type == "own_goal":
            src = Image.open("Images/ownGoal.png")
        elif event.event_type == "yellow_card":
            src = Image.open("Images/yellowCard.png")
        elif event.event_type == "red_card":
            src = Image.open("Images/redCard.png")
        elif event.event_type == "injury":
            src = Image.open("Images/injury.png")

        src.thumbnail((15, 15))
        ctk_image = ctk.CTkImage(src, None, (src.width, src.height))

        if home:
            ctk.CTkLabel(frame, image = ctk_image, text = "", fg_color = DARK_GREY).place(relx = 0.95, rely = 0.5, anchor = "e")
        else:
            ctk.CTkLabel(frame, image = ctk_image, text = "", fg_color = DARK_GREY).place(relx = 0.05, rely = 0.5, anchor = "w")

    def lineups(self):
        """
        Adds the lineups to the match info frame.
        """

        self.lineupFrame = ctk.CTkFrame(self.eventsAndLineupsFrame, fg_color = DARK_GREY, width = 235, height = max(len(self.homeLineup), len(self.awayLineup)) * 15)
        self.lineupFrame.grid_columnconfigure((1, 2), weight = 1)
        self.lineupFrame.grid_columnconfigure((0, 3), weight = 4)

        for i in range(max(len(self.homeLineup), len(self.awayLineup))):
            self.lineupFrame.grid_rowconfigure(i, weight = 1)

        self.lineupFrame.pack(fill = "both")
        self.lineupFrame.grid_propagate(False)

        for i, lineupEntry in enumerate(self.homeLineup):
            player = Players.get_player_by_id(lineupEntry.player_id)
            rating = lineupEntry.rating

            if "." not in str(rating):
                rating = f"{rating}.0"

            ctk.CTkLabel(self.lineupFrame, text = f"{player.first_name} {player.last_name}", fg_color = DARK_GREY, font = (APP_FONT, 10)).grid(row = i, column = 0, sticky = "e")
            ctk.CTkLabel(self.lineupFrame, text = rating, fg_color = DARK_GREY, font = (APP_FONT, 10)).grid(row = i, column = 1, sticky = "e", padx = (5, 10))

        for i, lineupEntry in enumerate(self.awayLineup):
            player = Players.get_player_by_id(lineupEntry.player_id)
            rating = lineupEntry.rating

            if "." not in str(rating):
                rating = f"{rating}.0"

            ctk.CTkLabel(self.lineupFrame, text = rating, fg_color = DARK_GREY, font = (APP_FONT, 10)).grid(row = i, column = 2, sticky = "w", padx = (10, 5))
            ctk.CTkLabel(self.lineupFrame, text = f"{player.first_name} {player.last_name}", fg_color = DARK_GREY, font = (APP_FONT, 10)).grid(row = i, column = 3, sticky = "w")

class CalendarFrame(ctk.CTkFrame):
    def __init__(self, parent, matches, parentFrame, parentTab, matchInfoFrame, teamID, managingTeam = False):
        """
        Calendar frame to display matches in a calendar format, found in the schedule tab calendar form.

        Args:
            parent (ctk.CTkFrame): The parent frame.
            matches (list): List of Match objects.
            parentFrame (ctk.CTkFrame): The frame where this calendar frame will be placed.
            parentTab (ctk.CTkFrame): The parent tab containing this frame.
            matchInfoFrame (ctk.CTkFrame): The frame to display match information.
            teamID (str): The ID of the team.
            managingTeam (bool): Whether the user is managing the team.
        """

        super().__init__(parentFrame, fg_color = TKINTER_BACKGROUND, width = 670, height = 590)

        self.matches = matches
        self.parentTab = parentTab
        self.parent = parent
        self.matchInfoFrame = matchInfoFrame
        self.teamID = teamID
        self.managingTeam = managingTeam

        self.months = ["August", "September", "October", "November", "December", "January", "February", "March", "April", "May", "June", "July"]
        self.calendarFrames = [None] * len(self.months)

        self.currDate = Game.get_game_date(Managers.get_all_user_managers()[0].id)
        self.startMonth = self.currDate.month
        self.choosingEvent = False
        self.activeMatch = None
        self.activeEventDate = None

        if self.startMonth >= 8:
            self.startYear = self.currDate.year
        else:
            self.startYear = self.currDate.year - 1
        self.currIndex = self.months.index(calendar.month_name[self.startMonth])

        self.switchFrameLeft = ctk.CTkButton(self, fg_color = GREY_BACKGROUND, width = 30, height = 30, text = "<", command = lambda: self.changeMonth(-1))
        self.switchFrameLeft.place(relx = 0.9, rely = 0.05, anchor = "e")

        self.switchFrameRight = ctk.CTkButton(self, fg_color = GREY_BACKGROUND, width = 30, height = 30, text = ">", command = lambda: self.changeMonth(1))
        self.switchFrameRight.place(relx = 0.98, rely = 0.05, anchor = "e")

        self.monthLabel = ctk.CTkLabel(self, text = "", fg_color = TKINTER_BACKGROUND, font = (APP_FONT_BOLD, 30), width = 0)
        self.monthLabel.place(relx = 0.02, rely = 0.05, anchor = "w")

        self.daysLabelFrame = ctk.CTkFrame(self, fg_color = TKINTER_BACKGROUND, width = 670, height = 30)
        self.daysLabelFrame.place(relx = 0, rely = 0.11, anchor = "w")
        self.daysLabelFrame.grid_propagate(False)

        self.daysLabelFrame.grid_columnconfigure((0, 1, 2, 3, 4, 5, 6), weight = 1)

        # Create day labels 
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for day in days:
            ctk.CTkLabel(self.daysLabelFrame, text = day, fg_color = TKINTER_BACKGROUND, font = (APP_FONT_BOLD, 12), width = 50).grid(row = 0, column = days.index(day), padx = 5, pady = 5)

        self.createCalendarMonth()

    def changeMonth(self, delta):
        """
        Changes the displayed month in the calendar.

        Args:
            delta (int): The change in month index (-1 for previous month, +1 for next month).
        """

        self.calendarFrames[self.currIndex].place_forget()
        self.currIndex = (self.currIndex + delta) % len(self.months)

        # If the frame for the new month does not exist, create it
        if not self.calendarFrames[self.currIndex]:
            self.createCalendarMonth()
        else:
            self.calendarFrames[self.currIndex].place(relx = 0, rely = 0.13, anchor = "nw")

            month = self.months[self.currIndex]
            year = self.startYear if self.currIndex <= 4 else self.startYear + 1
            self.monthLabel.configure(text = f"{month} {year}")   

    def createCalendarMonth(self):
        """
        Creates the calendar view for the current month.
        """
        
        frame = ctk.CTkFrame(self, fg_color = TKINTER_BACKGROUND, width = 670, height = 500, corner_radius = 0)

        month = self.months[self.currIndex]
        year = self.startYear if self.currIndex <= 4 else self.startYear + 1

        self.monthLabel.configure(text = f"{month} {year}")   

        frame.grid_propagate(False)
        frame.grid_columnconfigure((0, 1, 2, 3, 4, 5, 6), weight = 1)
        frame.grid_rowconfigure((0, 1, 2, 3, 4, 5), weight = 1)

        # Get month index
        month_index = list(calendar.month_name).index(month)
        start_weekday, num_days = calendar.monthrange(year, month_index)

        numRows = calendar.monthcalendar(year, month_index)

        day_num = 1
        for row in range(6):
            for col in range(7):
                if (row == 0 and col < start_weekday) or day_num > num_days:
                    continue

                date = datetime.datetime(year, month_index, day_num)
                today = self.currDate.date()

                if today == date.date():
                    border_color = APP_BLUE
                else:
                    border_color = "white"

                # Day cell
                matchObj = None
                for match in self.matches:
                    _, text, _ = format_datetime_split(match.date)

                    matchDay = text.split(" ")[0]
                    matchDay = int(re.sub(r'(st|nd|rd|th)', '', matchDay))
                    matchMonth = text.split(" ")[1]

                    if (matchDay == day_num and matchMonth == month):
                        matchObj = match
                        break
                
                if matchObj:
                    # If matchDay, create a match frame
                    CalendarMatchFrame(self, self.parentTab, frame, matchObj, day_num, self.teamID, 150, 150, TKINTER_BACKGROUND, 0, border_color, 1, row, col, 5, 5, "nsew", len(numRows), matchInfoFrame = self.matchInfoFrame)
                elif self.managingTeam:
                    # Otherwise, create a normal calendar event frame
                    CalendarEventFrame(self, frame, day_num, date, self.teamID, 150, 150, TKINTER_BACKGROUND, 0, border_color, 1, row, col, 5, 5, "nsew", matchInfoFrame = self.matchInfoFrame, today = today)
                else:
                    # Empty day cell for other teams
                    cell = ctk.CTkFrame(frame, fg_color = TKINTER_BACKGROUND, width = 150, height = 150, corner_radius = 0, border_width = 1, border_color = border_color)
                    cell.grid(row = row, column = col, padx = 5, pady = 5, sticky = "nsew")
                    ctk.CTkLabel(cell, text = str(day_num), font = (APP_FONT_BOLD, 12), height = 0).place(relx = 0.05, rely = 0.05, anchor = "nw")

                day_num += 1

        frame.place(relx = 0, rely = 0.13, anchor = "nw")
        self.calendarFrames[self.currIndex] = frame

class CalendarMatchFrame(ctk.CTkFrame):
    def __init__(self, parent, parentTab, parentFrame, match, day, teamID, width, heigth, fgColor, corner_radius, border_color, border_width, row, col, padx, pady, sticky, numRows, matchInfoFrame = None):
        """
        Match frame in the calendar view, found in the calendar tab (match days).

        Args:
            parent (ctk.CTkFrame): The parent frame.
            parentTab (ctk.CTkFrame): The parent tab containing this frame.
            parentFrame (ctk.CTkFrame): The frame where this match frame will be placed.
            match (Match): The match object.
            day (int): The day of the month.
            teamID (str): The ID of the team.
            width (int): The width of the frame.
            heigth (int): The height of the frame.
            fgColor (str): The foreground color of the frame.
            corner_radius (int): The corner radius of the frame.
            border_color (str): The border color of the frame.
            border_width (int): The border width of the frame.
            row (int): The row position in the grid.
            col (int): The column position in the grid.
            padx (int): The padding in x direction.
            pady (int): The padding in y direction.
            sticky (str): The sticky option for grid placement.
            numRows (int): The number of rows in the calendar month.
            matchInfoFrame (ctk.CTkFrame): The frame to display match information.
        """

        super().__init__(parentFrame, fg_color = fgColor, width = width, height = heigth, corner_radius = corner_radius, border_width = border_width, border_color = border_color)
        self.grid(row = row, column = col, padx = padx, pady = pady, sticky = sticky)
        
        self.pack_propagate(False)

        self.parent = parent
        self.parentTab = parentTab
        self.match = match
        self.day = day
        self.teamID = teamID
        self.fgColor = fgColor
        self.border_color = border_color
        self.border_width = border_width
        self.numRows = numRows
        self.matchInfoFrame = matchInfoFrame

        ctk.CTkLabel(self, text = str(day), font = (APP_FONT_BOLD, 12), height = 0).place(relx = 0.05, rely = 0.05, anchor = "nw")

        home = True if self.match.home_id == self.teamID else False
        oppNameY = 0.6 if numRows > 5 else 0.5

        src = Image.open(f"Images/{"stadium" if home else "plane"}.png")
        src.thumbnail((15, 15))
        ctk.CTkLabel(self, image = ctk.CTkImage(src, None, (src.width, src.height)), text = "", fg_color = TKINTER_BACKGROUND, height = 0).place(relx = 0.95, rely = 0.02, anchor = "ne")

        league = League.get_league_by_id(self.match.league_id)
        src = Image.open(io.BytesIO(league.logo))
        src.thumbnail((15, 15))
        ctk.CTkLabel(self, image = ctk.CTkImage(src, None, (src.width, src.height)), text = "", fg_color = TKINTER_BACKGROUND, height = 0).place(relx = 0.95, rely = 0.2 if oppNameY == 0.5 else 0.25, anchor = "ne")

        src = Image.open(io.BytesIO(Teams.get_team_by_id(self.match.away_id if home else self.match.home_id).logo))
        src.thumbnail((35, 35))
        ctk.CTkLabel(self, image = ctk.CTkImage(src, None, (src.width, src.height)), text = "", fg_color = TKINTER_BACKGROUND).place(relx = 0.5, rely = 0.1, anchor = "n")

        oppositionName = Teams.get_team_by_id(self.match.away_id if home else self.match.home_id).name
        ctk.CTkLabel(self, text = f"{oppositionName.split(" ")[0]}", font = (APP_FONT, 10), fg_color = TKINTER_BACKGROUND, height = 0).place(relx = 0.5, rely = oppNameY, anchor = "n")
        ctk.CTkLabel(self, text = f"{oppositionName.split(" ")[1]}", font = (APP_FONT_BOLD, 12), fg_color = TKINTER_BACKGROUND, height = 0).place(relx = 0.5, rely = oppNameY + 0.15, anchor = "n")

        if self.matchInfoFrame:
            for widget in self.winfo_children():
                widget.bind("<Button-1>", lambda event: self.displayMatchInfo())
                widget.bind("<Enter>", lambda event: self.onHoverCell())

            self.bind("<Button-1>", lambda event: self.displayMatchInfo())
            self.bind("<Enter>", lambda event: self.onHoverCell())
            self.bind("<Leave>", lambda event: self.onLeaveCell())

    def onHoverCell(self):
        """
        Changes the cell and text color on hover.
        """
        
        self.configure(cursor = "hand2")
        self.configure(fg_color = DARK_GREY)

        for child in self.winfo_children():
            child.configure(cursor = "hand2")

            if not isinstance(child, ctk.CTkFrame):
                child.configure(fg_color = DARK_GREY)

    def onLeaveCell(self):
        """
        Changes the cell and text color back to normal when not hovering.
        """
        
        self.configure(cursor = "")
        self.configure(fg_color = TKINTER_BACKGROUND)

        for child in self.winfo_children():
            child.configure(cursor = "")

            if not isinstance(child, ctk.CTkFrame):
                child.configure(fg_color = TKINTER_BACKGROUND)

    def displayMatchInfo(self):
        """
        Displays detailed match information in the match info frame.
        """

        if self.parent.choosingEvent or self.parent.activeMatch == self.match.id:
            return
            
        for widget in self.matchInfoFrame.winfo_children():
            widget.destroy()

        self.parent.activeMatch = self.match.id
        self.parent.activeEventDate = None
        self.homeTeam = Teams.get_team_by_id(self.match.home_id)
        self.awayTeam = Teams.get_team_by_id(self.match.away_id)

        self.played = Matches.check_game_played(self.match, Game.get_game_date(Managers.get_all_user_managers()[0].id))

        self.scoreFrame = ctk.CTkFrame(self.matchInfoFrame, fg_color = DARK_GREY, width = 260, height = 100, corner_radius = 10)
        self.scoreFrame.place(relx = 0.5, rely = 0.02, anchor = "n")

        srcHome = Image.open(io.BytesIO(self.homeTeam.logo))
        srcHome.thumbnail((50, 50))
        TeamLogo(self.scoreFrame, srcHome, self.homeTeam, DARK_GREY, 0.2, 0.5, "center", self.parentTab)

        srcAway = Image.open(io.BytesIO(self.awayTeam.logo))
        srcAway.thumbnail((50, 50))
        TeamLogo(self.scoreFrame, srcAway, self.awayTeam, DARK_GREY, 0.8, 0.5, "center", self.parentTab)

        if self.played:
            scoreLabel = MatchProfileLink(self.scoreFrame, self.match, f"{self.match.score_home} - {self.match.score_away}", "white", 0.5, 0.5, "center", DARK_GREY, self.parentTab, 30, APP_FONT_BOLD)
        else:
            _, _, time = format_datetime_split(self.match.date)
            scoreLabel = ctk.CTkLabel(self.scoreFrame, text = time, fg_color = DARK_GREY, font = (APP_FONT, 30))
            scoreLabel.place(relx = 0.5, rely = 0.5, anchor = "center")
        
        self.matchdayEvents = MatchEvents.get_events_by_match(self.match.id)
        self.homeEvents = []
        self.awayEvents = []
        if self.played:
            for event in self.matchdayEvents:
                player = Players.get_player_by_id(event.player_id)
                if player.team_id == self.homeTeam.id:
                    if event.event_type == "own_goal":
                        self.awayEvents.append(event)
                    else:
                        self.homeEvents.append(event)
                elif player.team_id == self.awayTeam.id:
                    if event.event_type == "own_goal":
                        self.homeEvents.append(event)
                    else:
                        self.awayEvents.append(event)

            # remove all asissts and clean sheets
            self.homeEvents = [event for event in self.homeEvents if event.event_type != "assist" and event.event_type != "clean_sheet" and event.event_type != "penalty_saved" and event.event_type != "penalty_miss" and event.event_type != "sub_on" and event.event_type != "sub_off"]
            self.awayEvents = [event for event in self.awayEvents if event.event_type != "assist" and event.event_type != "clean_sheet" and event.event_type != "penalty_saved" and event.event_type != "penalty_miss" and event.event_type != "sub_on" and event.event_type != "sub_off"]

            self.homeLineup = TeamLineup.get_lineup_by_match_and_team(self.match.id, self.homeTeam.id)
            self.awayLineup = TeamLineup.get_lineup_by_match_and_team(self.match.id, self.awayTeam.id)

            if (max(len(self.homeLineup), len(self.awayLineup)) * 15) + (max(len(self.homeEvents), len(self.awayEvents)) * 30) > 410:
                self.eventsAndLineupsFrame = ctk.CTkScrollableFrame(self.matchInfoFrame, fg_color = DARK_GREY, width = 235, height = 420, corner_radius = 10)
                self.eventsAndLineupsFrame.place(relx = 0.5, rely = 0.203, anchor = "n")
            else:
                self.eventsAndLineupsFrame = ctk.CTkFrame(self.matchInfoFrame, fg_color = DARK_GREY, width = 260, height = 440, corner_radius = 10)
                self.eventsAndLineupsFrame.place(relx = 0.5, rely = 0.203, anchor = "n")
                self.eventsAndLineupsFrame.pack_propagate(False)
        else:
            self.eventsAndLineupsFrame = ctk.CTkFrame(self.matchInfoFrame, fg_color = DARK_GREY, width = 260, height = 440, corner_radius = 10)
            self.eventsAndLineupsFrame.place(relx = 0.5, rely = 0.203, anchor = "n")
            self.eventsAndLineupsFrame.pack_propagate(False)

        if self.played:
            self.matchEvents()
            self.lineups()

    def matchEvents(self):
        """
        Displays match events in the match info frame.
        """

        self.matchEventsFrame = ctk.CTkFrame(self.eventsAndLineupsFrame, fg_color = DARK_GREY, width = 235, height = max(len(self.homeEvents), len(self.awayEvents)) * 30)
        self.matchEventsFrame.pack(fill = "both", pady = 5)

        self.homeEventsFrame = ctk.CTkFrame(self.matchEventsFrame, fg_color = DARK_GREY, width = 120, height = len(self.homeEvents) * 30)
        self.homeEventsFrame.place(relx = 0, rely = 0, anchor = "nw")
        self.homeEventsFrame.pack_propagate(False)

        self.awayEventsFrame = ctk.CTkFrame(self.matchEventsFrame, fg_color = DARK_GREY, width = 120, height = len(self.awayEvents) * 30)
        self.awayEventsFrame.place(relx = 1, rely = 0, anchor = "ne")
        self.awayEventsFrame.pack_propagate(False)

        for event in self.homeEvents:
            self.addEvent(event, True, self.homeEventsFrame)

        for event in self.awayEvents:
            self.addEvent(event, False, self.awayEventsFrame)

    def addEvent(self, event, home, parent):
        """
        Adds a single event to the match events frame.
        """
        
        frame = ctk.CTkFrame(parent, fg_color = DARK_GREY, height = 30)
        frame.pack(fill = "x", expand = True)

        player = Players.get_player_by_id(event.player_id)

        if "+" in event.time:
            font = 9
            playerRelX = 0.35
        else:
            font = 10
            playerRelX = 0.25

        if home:
            ctk.CTkLabel(frame, text = event.time + "'", fg_color = DARK_GREY, font = (APP_FONT, font)).place(relx = 0.1, rely = 0.5, anchor = "w")
            ctk.CTkLabel(frame, text = player.last_name, fg_color = DARK_GREY, font = (APP_FONT, 10)).place(relx = playerRelX, rely = 0.5, anchor = "w")
        else:
            ctk.CTkLabel(frame, text = player.last_name, fg_color = DARK_GREY, font = (APP_FONT, 10)).place(relx = 1 - playerRelX, rely = 0.5, anchor = "e")
            ctk.CTkLabel(frame, text = event.time + "'", fg_color = DARK_GREY, font = (APP_FONT, font)).place(relx = 0.9, rely = 0.5, anchor = "e")

        if event.event_type == "goal":
            src = Image.open("Images/goal.png")
        elif event.event_type == "penalty_goal":
            src = Image.open("Images/penalty.png")
        elif event.event_type == "own_goal":
            src = Image.open("Images/ownGoal.png")
        elif event.event_type == "yellow_card":
            src = Image.open("Images/yellowCard.png")
        elif event.event_type == "red_card":
            src = Image.open("Images/redCard.png")
        elif event.event_type == "injury":
            src = Image.open("Images/injury.png")

        src.thumbnail((15, 15))
        ctk_image = ctk.CTkImage(src, None, (src.width, src.height))

        if home:
            ctk.CTkLabel(frame, image = ctk_image, text = "", fg_color = DARK_GREY).place(relx = 0.95, rely = 0.5, anchor = "e")
        else:
            ctk.CTkLabel(frame, image = ctk_image, text = "", fg_color = DARK_GREY).place(relx = 0.05, rely = 0.5, anchor = "w")

    def lineups(self):
        """
        Adds the lineups to the match info frame.
        """
        
        self.lineupFrame = ctk.CTkFrame(self.eventsAndLineupsFrame, fg_color = DARK_GREY, width = 235, height = max(len(self.homeLineup), len(self.awayLineup)) * 15)
        self.lineupFrame.grid_columnconfigure((1, 2), weight = 1)
        self.lineupFrame.grid_columnconfigure((0, 3), weight = 4)

        for i in range(max(len(self.homeLineup), len(self.awayLineup))):
            self.lineupFrame.grid_rowconfigure(i, weight = 1)

        self.lineupFrame.pack(fill = "both")
        self.lineupFrame.grid_propagate(False)

        for i, lineupEntry in enumerate(self.homeLineup):
            player = Players.get_player_by_id(lineupEntry.player_id)
            rating = lineupEntry.rating

            if "." not in str(rating):
                rating = f"{rating}.0"

            ctk.CTkLabel(self.lineupFrame, text = f"{player.first_name} {player.last_name}", fg_color = DARK_GREY, font = (APP_FONT, 10)).grid(row = i, column = 0, sticky = "e")
            ctk.CTkLabel(self.lineupFrame, text = rating, fg_color = DARK_GREY, font = (APP_FONT, 10)).grid(row = i, column = 1, sticky = "e", padx = (5, 10))

        for i, lineupEntry in enumerate(self.awayLineup):
            player = Players.get_player_by_id(lineupEntry.player_id)
            rating = lineupEntry.rating

            if "." not in str(rating):
                rating = f"{rating}.0"

            ctk.CTkLabel(self.lineupFrame, text = rating, fg_color = DARK_GREY, font = (APP_FONT, 10)).grid(row = i, column = 2, sticky = "w", padx = (10, 5))
            ctk.CTkLabel(self.lineupFrame, text = f"{player.first_name} {player.last_name}", fg_color = DARK_GREY, font = (APP_FONT, 10)).grid(row = i, column = 3, sticky = "w")

class CalendarEventFrame(ctk.CTkFrame):
    def __init__(self, parent, parentFrame, day, date, teamID, width, height, fgColor, corner_radius, border_color, border_width, row, col, padx, pady, sticky, matchInfoFrame = None, today = None, interactive = True):
        """
        Event frame in the calendar view, found in the calendar view of the schedule tab (non-match days).
        
        Args:
            parent (ctk.CTkFrame): The parent frame.
            parentFrame (ctk.CTkFrame): The frame where this event frame will be placed.
            day (int): The day of the month.
            date (datetime): The date of the event.
            teamID (str): The ID of the team.
            width (int): The width of the frame.
            height (int): The height of the frame.
            fgColor (str): The foreground color of the frame.
            corner_radius (int): The corner radius of the frame.
            border_color (str): The border color of the frame.
            border_width (int): The border width of the frame.
            row (int): The row position in the grid.
            col (int): The column position in the grid.
            padx (int): The padding in x direction.
            pady (int): The padding in y direction.
            sticky (str): The sticky option for grid placement.
            matchInfoFrame (ctk.CTkFrame): The frame to display match information.
            today (date): The current date.
            interactive (bool): Whether the cell is interactive.
        """

        super().__init__(parentFrame, fg_color = fgColor, corner_radius = corner_radius, border_color = border_color, border_width = border_width, width = width, height = height)
        self.grid(row = row, column = col, padx = padx, pady = pady, sticky = sticky)
        
        self.parent = parent
        self.parentFrame = parentFrame
        self.day = day
        self.date = date
        self.teamID = teamID
        self.matchInfoFrame = matchInfoFrame

        self.eventsChooseFrame = ctk.CTkFrame(self.parent, fg_color = DARK_GREY, width = 400, height = 300, corner_radius = 10)

        self.chosenEvents = [None, None, None]
        self.gameTommorrow = Matches.check_if_game_date(self.teamID, self.date + timedelta(days = 1))
        self.gameYesterday = Matches.check_if_game_date(self.teamID, self.date - timedelta(days = 1))

        ctk.CTkLabel(self, text = str(day), font = (APP_FONT_BOLD, 12), height = 0).place(relx = 0.05, rely = 0.05, anchor = "nw")

        savedEvents = CalendarEvents.get_events_dates(self.teamID, self.date, self.date.replace(hour = 23), get_finished = True)

        # Check if the cell should be interactive
        add = (not today or today <= self.date.date() < today + timedelta(weeks = 2)) and interactive
        if add:
            bindings = [
                ("<Enter>", lambda e: self.onHoverCell()),
                ("<Leave>", lambda e: self.onLeaveCell()),
                ("<Button-1>", lambda e: self.setCalendarEvents())
            ]
            for seq, func in bindings:
                self.bind(seq, func)

            for widget in self.winfo_children():
                widget.bind("<Button-1>", lambda e: self.setCalendarEvents())
                widget.bind("<Enter>", lambda e: self.onHoverCell())

            for i, event in enumerate(savedEvents):
                self.addSmallEventFrame(event.event_type, i)
        else:
            for i, event in enumerate(savedEvents):
                self.addSmallEventFrame(event.event_type, i, bind = False)

    def onHoverCell(self):
        """
        Changes the cell and text color on hover.
        """
        
        self.configure(cursor = "hand2")
        self.configure(fg_color = DARK_GREY)

        for child in self.winfo_children():
            child.configure(cursor = "hand2")

            if not isinstance(child, ctk.CTkFrame):
                child.configure(fg_color = DARK_GREY)

    def onLeaveCell(self):
        """
        Changes the cell and text color back to normal when not hovering.
        """
        
        self.configure(cursor = "")
        self.configure(fg_color = TKINTER_BACKGROUND)

        for child in self.winfo_children():
            child.configure(cursor = "")

            if not isinstance(child, ctk.CTkFrame):
                child.configure(fg_color = TKINTER_BACKGROUND)

    def setCalendarEvents(self):
        """
        Displays the calendar events for the selected day.
        """

        if self.parent.choosingEvent or self.parent.activeEventDate == self.date:
            return
        
        self.parent.activeEventDate = self.date

        if self.matchInfoFrame:
            self.parent.activeMatch = None

            for widget in self.matchInfoFrame.winfo_children():
                widget.destroy()
        else:
            self.configure(border_color = APP_BLUE)

            self.parentFrame.place_forget()
            self.parentFrame.place(relx = 0.05, rely = 0.2, anchor = "nw")

            for cell in self.parentFrame.winfo_children():
                if isinstance(cell, CalendarEventFrame) and cell != self:
                    cell.configure(border_color = "white")

        # Differentiate between interaction in schedule or interaction from the email
        if self.matchInfoFrame:
            self.dayEventsFrame = ctk.CTkFrame(self.matchInfoFrame, fg_color = DARK_GREY, width = 260, height = 545, corner_radius = 10)
            self.dayEventsFrame.place(relx = 0.5, rely = 0.02, anchor = "n")

            morningFrameX = 0.5
            morningFrameY = 0.2
            afternoonFrameX = 0.5
            afternoonFrameY = 0.4
            eveningFrameX = 0.5
            eveningFrameY = 0.6
            okButtonX = 0.5
            okButtonY = 0.95

            buttonsWidth = 250
            okButtonWidth = 240
            okButtonHeight = 30

            self.buttonFont = (APP_FONT_BOLD, 20)
        else:
            self.dayEventsFrame = ctk.CTkFrame(self.parent, fg_color = GREY_BACKGROUND, width = 630, height = 110)
            self.dayEventsFrame.place(relx = 0.05, rely = 0.35, anchor = "nw")

            morningFrameX = 0.13
            morningFrameY = 0.05
            afternoonFrameX = 0.37
            afternoonFrameY = 0.05
            eveningFrameX = 0.61
            eveningFrameY = 0.05
            okButtonX = 0.87
            okButtonY = 0.72

            buttonsWidth = 150
            okButtonWidth = 100
            okButtonHeight = 50

            self.buttonFont = (APP_FONT_BOLD, 13)
        
        self.currEvents = CalendarEvents.get_events_week(self.date, self.teamID)

        day, text, _, = format_datetime_split(self.date)

        if self.matchInfoFrame:
            ctk.CTkLabel(self.matchInfoFrame, text = day, fg_color = DARK_GREY, bg_color = DARK_GREY, font = (APP_FONT_BOLD, 20), height = 0).place(relx = 0.5, rely = 0.09, anchor = "center")
            ctk.CTkLabel(self.matchInfoFrame, text = text, fg_color = DARK_GREY, bg_color = DARK_GREY, font = (APP_FONT, 15), height = 0).place(relx = 0.5, rely = 0.14, anchor = "center")

        morningFrame = ctk.CTkFrame(self.dayEventsFrame, fg_color = GREY_BACKGROUND, width = buttonsWidth, height = 100, corner_radius = 10)
        morningFrame.place(relx = morningFrameX, rely = morningFrameY, anchor = "n")
    
        ctk.CTkLabel(morningFrame, text = "Morning", fg_color = GREY_BACKGROUND, font = (APP_FONT, 15)).place(relx = 0.5, rely = 0.15, anchor = "center")

        self.morningButton = ctk.CTkButton(morningFrame, text = "+", command = lambda: self.addCalendarEvent(0), anchor = "center", border_color = "white", border_width = 2, height = 60, width = buttonsWidth - 10, fg_color = GREY_BACKGROUND, hover_color = DARK_GREY, font = (APP_FONT, 20))
        self.morningButton.place(relx = 0.5, rely = 0.6, anchor = "center")

        afternoonFrame = ctk.CTkFrame(self.dayEventsFrame, fg_color = GREY_BACKGROUND, width = buttonsWidth, height = 100, corner_radius = 10)
        afternoonFrame.place(relx = afternoonFrameX, rely = afternoonFrameY, anchor = "n")

        ctk.CTkLabel(afternoonFrame, text = "Afternoon", fg_color = GREY_BACKGROUND, font = (APP_FONT, 15)).place(relx = 0.5, rely = 0.15, anchor = "center")

        self.afternoonButton = ctk.CTkButton(afternoonFrame, text = "+", command = lambda: self.addCalendarEvent(1), anchor = "center", border_color = "white", border_width = 2, height = 60, width = buttonsWidth - 10, fg_color = GREY_BACKGROUND, hover_color = DARK_GREY, font = (APP_FONT, 20))
        self.afternoonButton.place(relx = 0.5, rely = 0.6, anchor = "center")

        eveningFrame = ctk.CTkFrame(self.dayEventsFrame, fg_color = GREY_BACKGROUND, width = buttonsWidth, height = 100, corner_radius = 10)
        eveningFrame.place(relx = eveningFrameX, rely = eveningFrameY, anchor = "n")

        ctk.CTkLabel(eveningFrame, text = "Evening", fg_color = GREY_BACKGROUND, font = (APP_FONT, 15)).place(relx = 0.5, rely = 0.15, anchor = "center")

        self.eveningButton = ctk.CTkButton(eveningFrame, text = "+", command = lambda: self.addCalendarEvent(2), anchor = "center", border_color = "white", border_width = 2, height = 60, width = buttonsWidth - 10, fg_color = GREY_BACKGROUND, hover_color = DARK_GREY, font = (APP_FONT, 20))
        self.eveningButton.place(relx = 0.5, rely = 0.6, anchor = "center")

        self.eventButtons = [self.morningButton, self.afternoonButton, self.eveningButton]

        okButton = ctk.CTkButton(self.dayEventsFrame, text = "OK", command = self.confirmEvents, anchor = "center", height = okButtonHeight, width = okButtonWidth, fg_color = APP_BLUE, hover_color = APP_BLUE, font = (APP_FONT, 15))
        okButton.place(relx = okButtonX, rely = okButtonY, anchor = "s")

        # Add the saved events to the buttons if they exist
        savedEvents = CalendarEvents.get_events_dates(self.teamID, self.date, self.date.replace(hour = 23), get_finished = True)
        times = [10, 14, 17]
        if len(savedEvents) > 0:
            for i, hour in enumerate(times):
                slot_time = self.date.replace(hour = hour)
                event = next((e for e in savedEvents if e.start_date <= slot_time <= e.end_date), None)

                if event:
                    self.chosenEvents[i] = event.event_type
                    eventText = event.event_type
                else:
                    eventText = "Rest"

                self.eventButtons[i].configure(text = eventText, fg_color = EVENT_COLOURS[eventText], hover_color = EVENT_COLOURS[eventText], border_width = 0, font = self.buttonFont)

    def addCalendarEvent(self, timeOfDay):
        """
        Opens the event selection frame for the specified time of day.
        """

        if self.parent.choosingEvent or self.chosenEvents[timeOfDay] == "Travel":
            return

        self.parent.choosingEvent = True
        self.eventsChooseFrame.place(relx = 0.5, rely = 0.5, anchor = "center")
        self.eventsChooseFrame.lift()

        for widget in self.eventsChooseFrame.winfo_children():
            widget.destroy()

        ctk.CTkLabel(self.eventsChooseFrame, text = "Event", fg_color = DARK_GREY, font = (APP_FONT, 20)).place(relx = 0.05, rely = 0.08, anchor = "w")
        ctk.CTkLabel(self.eventsChooseFrame, text = "Available", fg_color = DARK_GREY, font = (APP_FONT, 18)).place(relx = 0.8, rely = 0.08, anchor = "center")

        closeButton = ctk.CTkButton(self.eventsChooseFrame, text = "X", command = self.closeEventsChooseFrame, fg_color = DARK_GREY, hover_color = CLOSE_RED, font = (APP_FONT, 12), width = 25, height = 25, corner_radius = 5)
        closeButton.place(relx = 0.95, rely = 0.08, anchor = "center")

        gap = 0.12
        buttonHeight = 30
        for i, eventType in enumerate(MAX_EVENTS.keys()):
            button = ctk.CTkButton(self.eventsChooseFrame, fg_color = EVENT_COLOURS[eventType], hover_color = EVENT_COLOURS[eventType], width = 250, height = buttonHeight, corner_radius = 5, text = eventType, font = (APP_FONT, 15), anchor = "w", command = lambda e = eventType: self.closeEventsChooseFrame(e, timeOfDay))
            button.place(relx = 0.02, rely = 0.2 + (i * gap), anchor = "w")

            if eventType in self.currEvents.keys():
                # Calculate remaining available events
                text = MAX_EVENTS[eventType] - self.currEvents[eventType]

                if text == 0:
                    button.configure(state = "disabled")

            else:
                text = MAX_EVENTS[eventType]
            
            ctk.CTkLabel(self.eventsChooseFrame, text = text, fg_color = DARK_GREY, font = (APP_FONT, 12)).place(relx = 0.8, rely = 0.2 + (i * gap), anchor = "center")

        # Add Match Preparation/Review buttons if applicable
        if self.gameTommorrow or self.gameYesterday:
            if self.gameTommorrow:
                button = ctk.CTkButton(self.eventsChooseFrame, fg_color = EVENT_COLOURS["Match Preparation"], hover_color = EVENT_COLOURS["Match Preparation"], width = 250, height = buttonHeight, corner_radius = 5, text = "Match Preparation", font = (APP_FONT, 15), anchor = "w", command = lambda: self.closeEventsChooseFrame("Match Preparation", timeOfDay))
            
                if "Match Preparation" in self.chosenEvents:
                    button.configure(state = "disabled")   
                    text = "0"    
                else:
                    text = "1"

                ctk.CTkLabel(self.eventsChooseFrame, text = text, fg_color = DARK_GREY, font = (APP_FONT, 12)).place(relx = 0.8, rely = 0.2 + (len(MAX_EVENTS) * gap), anchor = "center")

            elif self.gameYesterday:
                button = ctk.CTkButton(self.eventsChooseFrame, fg_color = EVENT_COLOURS["Match Review"], hover_color = EVENT_COLOURS["Match Review"], width = 250, height = buttonHeight, corner_radius = 5, text = "Match Review", font = (APP_FONT, 15), anchor = "w", command = lambda: self.closeEventsChooseFrame("Match Review", timeOfDay))

                if "Match Review" in self.chosenEvents:
                    button.configure(state = "disabled")   
                    text = "0"
                else:
                    text = "1"

                ctk.CTkLabel(self.eventsChooseFrame, text = text, fg_color = DARK_GREY, font = (APP_FONT, 12)).place(relx = 0.8, rely = 0.2 + (len(MAX_EVENTS) * gap), anchor = "center")

            button.place(relx = 0.02, rely = 0.2 + (len(MAX_EVENTS) * gap), anchor = "w")

            self.addRestButton(len(MAX_EVENTS) + 1, gap, buttonHeight, timeOfDay)
        else:
            self.addRestButton(len(MAX_EVENTS), gap, buttonHeight, timeOfDay)

    def addRestButton(self, lenEvents, gap, buttonHeight, timeOfDay):
        """
        Adds the rest button to the event selection frame.
        """

        button = ctk.CTkButton(self.eventsChooseFrame, fg_color = EVENT_COLOURS["Rest"], hover_color = EVENT_COLOURS["Rest"], width = 250, height = buttonHeight, corner_radius = 5, text = "Rest", font = (APP_FONT, 15), anchor = "w", command = lambda: self.closeEventsChooseFrame("Rest", timeOfDay))
        button.place(relx = 0.02, rely = 0.2 + (lenEvents * gap), anchor = "w")

    def closeEventsChooseFrame(self, event = None, timeOfDay = None):
        """
        Closes the event selection frame and updates the chosen event.
        """
        
        self.eventsChooseFrame.place_forget()
        self.parent.choosingEvent = False

        if event:
            if event not in ["Rest", "Match Preparation", "Match Review"]:
                
                if event in self.currEvents.keys():
                    self.currEvents[event] += 1
                else:
                    self.currEvents[event] = 1

                if self.chosenEvents[timeOfDay] and self.chosenEvents[timeOfDay] not in ["Rest", "Match Preparation", "Match Review"]:
                    self.currEvents[self.chosenEvents[timeOfDay]] -= 1
            elif event == "Rest":
                if self.chosenEvents[timeOfDay] and self.chosenEvents[timeOfDay] not in ["Rest", "Match Preparation", "Match Review"]:
                    self.currEvents[self.chosenEvents[timeOfDay]] -= 1

            button = self.eventButtons[timeOfDay]
            self.chosenEvents[timeOfDay] = event if event != "Rest" else None

            button.configure(text = event, fg_color = EVENT_COLOURS[event], hover_color = EVENT_COLOURS[event], border_width = 0, font = self.buttonFont)

    def confirmEvents(self):
        """
        Confirms the chosen events and saves them to the database.
        """
        
        for widget in self.winfo_children():
            if isinstance(widget, ctk.CTkFrame):
                widget.destroy()

        count = 0
        for i, event in enumerate(self.chosenEvents):
            if event is None:
                button = self.eventButtons[i]
                button.configure(text = "Rest", fg_color = EVENT_COLOURS["Rest"], hover_color = EVENT_COLOURS["Rest"], border_width = 0, font = (APP_FONT, 20))
                
                startDate = self.date.replace(hour = EVENT_TIMES[i][0], minute = 0, second = 0, microsecond = 0)
                endDate = self.date.replace(hour = EVENT_TIMES[i][1], minute = 0, second = 0, microsecond = 0)
                event = CalendarEvents.get_event_by_time(self.teamID, startDate, endDate)

                if event:
                    CalendarEvents.remove_event(event.id)

                continue

            startHour, endHour = EVENT_TIMES[i]
            startDate = self.date.replace(hour = startHour, minute = 0, second = 0, microsecond = 0)
            endDate = self.date.replace(hour = endHour, minute = 0, second = 0, microsecond = 0)

            CalendarEvents.add_event(self.teamID, event, startDate, endDate)
            self.addSmallEventFrame(event, count)
            count += 1

    def addSmallEventFrame(self, event, count, bind = True):
        """
        Adds a small colored frame to the calendar cell.
        """
        
        frame = ctk.CTkFrame(self, fg_color = EVENT_COLOURS[event], width = 75, height = 15, corner_radius = 5)
        frame.place(relx = 0.5, rely = 0.3 + (count * 0.2), anchor = "n")

        if bind:
            frame.bind("<Enter>", lambda event: self.onHoverCell())
            frame.bind("<Button-1>", lambda event: self.setCalendarEvents())

class MatchdayFrame(ctk.CTkFrame):
    def __init__(self, parent, matchday, matchdayNum, currentMatchday, parentFrame, parentTab, width, heigth, fgColor, relx, rely, anchor):
        """
        Matchday frame displaying all matches for a specific matchday for a league, found in league profiles

        Args:
            parent (ctk.CTkFrame): The parent frame.
            matchday (list): List of Match objects for the matchday.
            matchdayNum (int): The matchday number.
            currentMatchday (int): The current matchday number.
            parentFrame (ctk.CTkFrame): The frame where this matchday frame will be placed.
            parentTab (ctk.CTkFrame): The tab where this matchday frame is located.
            width (int): The width of the frame.
            heigth (int): The height of the frame.
            fgColor (str): The foreground color of the frame.
            relx (float): The relative x position for placing the frame.
            rely (float): The relative y position for placing the frame.
            anchor (str): The anchor position for placing the frame.
        """

        super().__init__(parent, fg_color = fgColor, width = width, height = heigth, corner_radius = 15)
        self.place(relx = relx, rely = rely, anchor = anchor)

        self.parent = parent
        self.parentFrame = parentFrame
        self.matchday = matchday
        self.matchdayNum = matchdayNum
        self.currentMatchday = currentMatchday
        self.parentTab = parentTab

        self.relx = relx
        self.rely = rely
        self.anchor = anchor
        
        # Display matchday information (playoffs if matchdayNum is 39)
        if self.matchdayNum != 39:
            ctk.CTkLabel(self, text = f"Matchday {self.matchdayNum}", fg_color = fgColor, font = (APP_FONT_BOLD, 30)).place(relx = 0.5, rely = 0.05, anchor = "center")
        else:
            ctk.CTkLabel(self, text = f"Playoffs", fg_color = fgColor, font = (APP_FONT_BOLD, 30)).place(relx = 0.5, rely = 0.05, anchor = "center")

        startY = 0.17
        gap = 0.075

        day, text, _ = format_datetime_split(self.matchday[0].date)
        currDay = day
        ctk.CTkLabel(self, text = f"{day} {text}", fg_color = fgColor, font = (APP_FONT_BOLD, 20)).place(relx = 0.02, rely = 0.1, anchor = "w")

        newDay = False
        for i, match in enumerate(self.matchday):

            day, text, _ = format_datetime_split(match.date)

            if day != currDay:
                ctk.CTkLabel(self, text = f"{day} {text}", fg_color = fgColor, font = (APP_FONT_BOLD, 20)).place(relx = 0.02, rely = startY + gap * i, anchor = "w")
                currDay = day
                newDay = True
            
            if newDay:
                index = i + 1
            else:
                index = i

            homeTeam = Teams.get_team_by_id(match.home_id)
            awayTeam = Teams.get_team_by_id(match.away_id) 

            if homeTeam:
                homeSrc = Image.open(io.BytesIO(homeTeam.logo))
                homeSrc.thumbnail((35, 35))
                TeamLogo(self, homeSrc, homeTeam, fgColor, 0.4, startY + gap * index, "center", self.parentTab)
                ctk.CTkLabel(self, text = homeTeam.name, fg_color = fgColor, font = (APP_FONT, 20)).place(relx = 0.35, rely = startY + gap * index, anchor = "e")
            else:
                # PlayOffs
                if i == 0:
                    ctk.CTkLabel(self, text = "4th Place", fg_color = fgColor, font = (APP_FONT, 20)).place(relx = 0.35, rely = startY + gap * index, anchor = "e")
                elif i == 1:
                    ctk.CTkLabel(self, text = "5th Place", fg_color = fgColor, font = (APP_FONT, 20)).place(relx = 0.35, rely = startY + gap * index, anchor = "e")
                else:
                    ctk.CTkLabel(self, text = "4th / 5th place", fg_color = fgColor, font = (APP_FONT, 20)).place(relx = 0.35, rely = startY + gap * index, anchor = "e")

            if awayTeam:
                awaySrc = Image.open(io.BytesIO(awayTeam.logo))
                awaySrc.thumbnail((35, 35))
                TeamLogo(self, awaySrc, awayTeam, fgColor, 0.6, startY + gap * index, "center", self.parentTab)
                ctk.CTkLabel(self, text = awayTeam.name, fg_color = fgColor, font = (APP_FONT, 20)).place(relx = 0.65, rely = startY + gap * index, anchor = "w")
            else:
                # PlayOffs
                if i == 0:
                    ctk.CTkLabel(self, text = "6th Place", fg_color = fgColor, font = (APP_FONT, 20)).place(relx = 0.65, rely = startY + gap * index, anchor = "w")
                elif i == 1:
                    ctk.CTkLabel(self, text = "7th Place", fg_color = fgColor, font = (APP_FONT, 20)).place(relx = 0.65, rely = startY + gap * index, anchor = "w")
                else:
                    ctk.CTkLabel(self, text = "6th / 7th place", fg_color = fgColor, font = (APP_FONT, 20)).place(relx = 0.65, rely = startY + gap * index, anchor = "w")

            if Matches.check_game_played(match, Game.get_game_date(Managers.get_all_user_managers()[0].id)):
                MatchProfileLink(self, match, f"{match.score_home} - {match.score_away}", "white", 0.5, startY + gap * index, "center", fgColor, self.parentTab, 20, APP_FONT_BOLD)
            else:
                _, _, time = format_datetime_split(match.date)
                ctk.CTkLabel(self, text = time, fg_color = fgColor, font = (APP_FONT, 20)).place(relx = 0.5, rely = startY + gap * index, anchor = "center")

    def placeFrame(self):
        """
        Places the matchday frame at its specified position.
        """
        
        self.place(relx = self.relx, rely = self.rely, anchor = self.anchor)

class PlayerFrame(ctk.CTkFrame):
    def __init__(self, parent, manager_id, player, parentFrame, caStars, paStars, teamSquad = True, talkFunction = None):
        """
        Frame representing a player with their details, found in the squad.
        
        Args:
            parent (ctk.CTkFrame): The parent frame.
            manager_id (str): The ID of the manager.
            player (Player): The player object.
            parentFrame (ctk.CTkFrame): The frame where this player frame will be placed.
            caStars (int): Current ability stars.
            paStars (int): Potential ability stars.
            teamSquad (bool): Whether the player is in the team squad.
            talkFunction (function): Function to call when the talk button is pressed.
        """

        super().__init__(parentFrame, fg_color = TKINTER_BACKGROUND, width = 982, height = 50, corner_radius = 5)
        self.pack(expand = True, fill = "both", padx = 10, pady = (0, 10))

        self.bind("<Enter>", lambda event: self.onFrameHover())
        self.bind("<Leave>", lambda event: self.onFrameLeave())

        self.parent = parent
        self.parentFrame = parentFrame
        self.manager_id = manager_id
        self.player = player
        self.parentTab = self.parent
        self.stat = "Current ability"
        self.league = LeagueTeams.get_league_by_team(self.player.team_id)
        self.caStars = caStars
        self.paStars = paStars

        self.teamSquad = teamSquad

        if not self.teamSquad:
            self.parentTab = self.parent.parent

        self.playerNumber = ctk.CTkLabel(self, text = self.player.number, font = (APP_FONT, 20), fg_color = TKINTER_BACKGROUND)
        self.playerNumber.place(relx = 0.05, rely = 0.5, anchor = "center")
        self.playerNumber.bind("<Enter>", lambda event: self.onFrameHover())

        self.playerName = PlayerProfileLink(self, self.player, self.player.first_name + " " + self.player.last_name, "white", 0.12, 0.5, "w", TKINTER_BACKGROUND, self.parentTab, caStars = caStars)
        self.playerName.bind("<Enter>", lambda event: self.onFrameHover())

        self.statFrame = ctk.CTkFrame(self, fg_color = TKINTER_BACKGROUND, width = 105, height = 30, corner_radius = 15)
        self.statFrame.place(relx = 0.3995, rely = 0.5, anchor = "center")
        self.statFrame.bind("<Enter>", lambda event: self.onFrameHover())

        self.addStat()

        self.playerAge = ctk.CTkLabel(self, text = self.player.age, font = (APP_FONT, 15), fg_color = TKINTER_BACKGROUND)
        self.playerAge.place(relx = 0.5155, rely = 0.5, anchor = "center")
        self.playerAge.bind("<Enter>", lambda event: self.onFrameHover())

        self.positions = self.player.specific_positions.replace(",", ", ")
        self.playerPosition = ctk.CTkLabel(self, text = self.positions, font = (APP_FONT, 13), fg_color = TKINTER_BACKGROUND)
        self.playerPosition.place(relx = 0.6, rely = 0.5, anchor = "center")
        self.playerPosition.bind("<Enter>", lambda event: self.onFrameHover())

        flag = Image.open(io.BytesIO(self.player.flag))
        flag.thumbnail((30, 30))
        flagImage = ctk.CTkImage(flag, None, (flag.width, flag.height))
        self.flagLabel = ctk.CTkLabel(self, text = "", image = flagImage, fg_color = TKINTER_BACKGROUND)
        self.flagLabel.place(relx = 0.705, rely = 0.5, anchor = "center")
        self.flagLabel.bind("<Enter>", lambda event: self.onFrameHover())

        PROGRESS_COLOR = MORALE_GREEN

        if self.player.morale <= 25:
            PROGRESS_COLOR = MORALE_RED
        elif self.player.morale <= 75:
            PROGRESS_COLOR = MORALE_YELLOW

        self.moraleSlider = ctk.CTkSlider(self, 
            fg_color = TKINTER_BACKGROUND, 
            width = 100, 
            height = 20, 
            corner_radius = 0, 
            from_ = 0, 
            to = 100,
            button_length = 0,
            button_color = PROGRESS_COLOR,
            progress_color = PROGRESS_COLOR,
            border_width = 0,
            border_color = GREY_BACKGROUND,
        )

        self.moraleSlider.set(self.player.morale)
        self.moraleSlider.configure(state = "disabled")
        self.moraleSlider.place(relx = 0.825, rely = 0.5, anchor = "center")
        self.moraleSlider.bind("<Enter>", lambda event: self.onSliderHover())
        self.moraleSlider.bind("<Leave>", lambda event: self.onSliderLeave())

        self.talkButton = None
        if self.teamSquad and talkFunction:
            src = Image.open("Images/conversation.png")
            src.thumbnail((30, 30))
            talkImage = ctk.CTkImage(src, None, (src.width, src.height))
            self.talkButton = ctk.CTkButton(self, text = "", image = talkImage, width = 20, fg_color = TKINTER_BACKGROUND, hover_color = TKINTER_BACKGROUND, command = lambda: talkFunction(player))
            self.talkButton.place(relx = 0.93, rely = 0.5, anchor = "center")
            self.talkButton.bind("<Enter>", lambda event: self.onFrameHover())

            if self.player.talked_to:
                self.talkButton.configure(state = "disabled")

    def onFrameHover(self):
        """
        Changes the frame color on hover.
        """
        
        self.configure(fg_color = DARK_GREY)
        self.playerNumber.configure(fg_color = DARK_GREY)
        self.playerName.configure(fg_color = DARK_GREY)
        self.playerAge.configure(fg_color = DARK_GREY)
        self.playerPosition.configure(fg_color = DARK_GREY)
        self.flagLabel.configure(fg_color = DARK_GREY)
        self.statFrame.configure(fg_color = DARK_GREY)

        for widget in self.statFrame.winfo_children():
            widget.configure(fg_color = DARK_GREY)

        if self.teamSquad and self.talkButton:
            self.talkButton.configure(fg_color = DARK_GREY)

    def onSliderHover(self):
        """
        Adds a label showing the morale percentage when hovering over the slider.
        """

        self.onFrameHover()

        self.moraleLabel = ctk.CTkLabel(self, text = f"{self.moraleSlider.get()}%", fg_color = DARK_GREY, width = 5, height = 5)
        self.moraleLabel.place(relx = 0.75, rely = 0.5, anchor = "center")

    def onSliderLeave(self):
        """
        Removes the morale percentage label when not hovering over the slider.
        """
        
        self.onFrameHover()
        self.moraleLabel.place_forget()

    def onFrameLeave(self):
        """
        Resets the frame color when not hovering.
        """
        
        self.configure(fg_color = TKINTER_BACKGROUND)
        self.playerNumber.configure(fg_color = TKINTER_BACKGROUND)
        self.playerName.configure(fg_color = TKINTER_BACKGROUND)
        self.playerAge.configure(fg_color = TKINTER_BACKGROUND)
        self.playerPosition.configure(fg_color = TKINTER_BACKGROUND)
        self.flagLabel.configure(fg_color = TKINTER_BACKGROUND)
        self.statFrame.configure(fg_color = TKINTER_BACKGROUND)

        for widget in self.statFrame.winfo_children():
            widget.configure(fg_color = TKINTER_BACKGROUND)

        if self.teamSquad and self.talkButton:
            self.talkButton.configure(fg_color = TKINTER_BACKGROUND)

    def disableTalkButton(self):
        """
        Disables the talk button.
        """
        
        self.talkButton.configure(state = "disabled")

    def enableTalkButton(self):
        """
        Enables the talk button.
        """
        
        self.talkButton.configure(state = "normal")

    def updateMorale(self, moraleChange):
        """
        Updates the player's morale slider by the specified change amount.

        Args:
            moraleChange (int): The amount to change the morale by.
        """
        
        currMorale = self.moraleSlider.get()
        newMorale = currMorale + moraleChange

        PROGRESS_COLOR = MORALE_GREEN

        if newMorale <= 25:
            PROGRESS_COLOR = MORALE_RED
        elif newMorale <= 75:
            PROGRESS_COLOR = MORALE_YELLOW

        self.moraleSlider.set(newMorale)
        self.moraleSlider.configure(progress_color = PROGRESS_COLOR, button_color = PROGRESS_COLOR)

    def addStat(self):
        """
        Adds the selected statistic to the stat frame.
        """

        for widget in self.statFrame.winfo_children():
            widget.destroy()

        match self.stat:
            case "Current ability":
                imageNames = star_images(self.caStars)

                for i, imageName in enumerate(imageNames):
                    src = Image.open(f"Images/{imageName}.png")
                    src.thumbnail((20, 20))
                    img = ctk.CTkImage(src, None, (src.width, src.height))
                    ctk.CTkLabel(self.statFrame, image = img, text = "").place(relx = 0.1 + i * 0.2, rely = 0.5, anchor = "center")
            case "Potential ability":
                imageNames = star_images(self.paStars)

                for i, imageName in enumerate(imageNames):
                    src = Image.open(f"Images/{imageName}.png")
                    src.thumbnail((20, 20))
                    img = ctk.CTkImage(src, None, (src.width, src.height))
                    ctk.CTkLabel(self.statFrame, image = img, text = "").place(relx = 0.1 + i * 0.2, rely = 0.5, anchor = "center")
            case "Goals / Assists":
                playerGoals = MatchEvents.get_goals_and_pens_by_player(self.player.id)
                playerAssists = MatchEvents.get_assists_by_player(self.player.id)

                ctk.CTkLabel(self.statFrame, text = f"{playerGoals} / {playerAssists}", fg_color = TKINTER_BACKGROUND, font = (APP_FONT, 15)).place(relx = 0.5, rely = 0.5, anchor = "center")
            case "Yellows / Reds":
                yellowCards = MatchEvents.get_yellow_cards_by_player(self.player.id)
                redCards = MatchEvents.get_red_cards_by_player(self.player.id)

                ctk.CTkLabel(self.statFrame, text = f"{yellowCards} / {redCards}", fg_color = TKINTER_BACKGROUND, font = (APP_FONT, 15)).place(relx = 0.5, rely = 0.5, anchor = "center")
            case "POTM Awards":
                potmAwards = TeamLineup.get_player_potm_awards(self.player.id)

                ctk.CTkLabel(self.statFrame, text = f"{potmAwards}", fg_color = TKINTER_BACKGROUND, font = (APP_FONT, 15)).place(relx = 0.5, rely = 0.5, anchor = "center")
            case "Form":
                last5 = Matches.get_team_last_5_matches(self.player.team_id, Game.get_game_date(Managers.get_all_user_managers()[0].id))

                imageNames = []
                for match in last5:
                    lineup = TeamLineup.get_lineup_by_match(match.id)
                    playerIDs = [player.player_id for player in lineup]

                    if self.player.id not in playerIDs:
                        imageNames.append("player_none")
                    else:
                        playerLineupData = [player for player in lineup if player.player_id == self.player.id][0]
                        potm = TeamLineup.get_player_OTM(match.id)
                        if potm.player_id == self.player.id:
                            imageNames.append("player_potm")
                        else:
                            if playerLineupData.rating >= 7:
                                imageNames.append("player_good")
                            elif playerLineupData.rating >= 5:
                                imageNames.append("player_mid")
                            else:
                                imageNames.append("player_bad")

                for i, imageName in enumerate(imageNames):
                    src = Image.open(f"Images/{imageName}.png")
                    src.thumbnail((18, 18))
                    img = ctk.CTkImage(src, None, (src.width, src.height))
                    ctk.CTkLabel(self.statFrame, image = img, text = "").place(relx = 0.9 - i * 0.18, rely = 0.5, anchor = "center")
            case "Fitness":
                player = Players.get_player_by_id(self.player.id)
                fitness = player.fitness if player else 0
                ctk.CTkLabel(self.statFrame, text = f"{fitness}%", fg_color = TKINTER_BACKGROUND, font = (APP_FONT, 15)).place(relx = 0.7, rely = 0.5, anchor = "e")

                if fitness > 75:
                    src = "Images/fitness_good.png"
                elif fitness > 25:
                    src = "Images/fitness_ok.png"
                else:
                    src = "Images/fitness_bad.png"

                image = Image.open(src)
                image.thumbnail((20, 20))
                ctk_image = ctk.CTkImage(image, None, (image.width, image.height))
                ctk.CTkLabel(self.statFrame, image = ctk_image, text = "", fg_color = TKINTER_BACKGROUND).place(relx = 0.95, rely = 0.5, anchor = "e")
            case "Match sharpness":
                player = Players.get_player_by_id(self.player.id)
                match_sharpness = player.sharpness if player else 0

                ctk.CTkLabel(self.statFrame, text = f"{match_sharpness}%", fg_color = TKINTER_BACKGROUND, font = (APP_FONT, 15)).place(relx = 0.5, rely = 0.5, anchor = "center")

                if match_sharpness > 75:
                    src = "Images/sharpness_good.png"
                elif match_sharpness > 25:
                    src = "Images/sharpness_ok.png"
                else:
                    src = "Images/sharpness_bad.png"

                image = Image.open(src)
                image.thumbnail((20, 20))
                ctk_image = ctk.CTkImage(image, None, (image.width, image.height))
                ctk.CTkLabel(self.statFrame, image = ctk_image, text = "", fg_color = TKINTER_BACKGROUND).place(relx = 0.95, rely = 0.5, anchor = "e")

        for widget in self.statFrame.winfo_children():
            widget.bind("<Enter>", lambda event: self.onFrameHover())

class LeagueTableScrollable(ctk.CTkScrollableFrame):
    def __init__(self, parent, height, width, x, y, fg_color, scrollbar_button_color, scrollbar_button_hover_color, anchor, textColor = "white", small = False, highlightManaged = False):
        """
        Scrollable frame representing a league table with team statistics, found in the hub.
        
        Args:
            parent (ctk.CTkFrame): The parent frame.
            height (int): The height of the frame.
            width (int): The width of the frame.
            x (float): The relative x position for placing the frame.
            y (float): The relative y position for placing the frame.
            fg_color (str): The foreground color of the frame.
            scrollbar_button_color (str): The color of the scrollbar button.
            scrollbar_button_hover_color (str): The hover color of the scrollbar button.
            anchor (str): The anchor position for placing the frame.
            textColor (str): The text color for labels.
            small (bool): Whether to use a compact layout.
            highlightManaged (bool): Whether to highlight the managed team.
        """

        super().__init__(parent, fg_color = fg_color, width = width, height = height, corner_radius = 0, scrollbar_button_color = scrollbar_button_color, scrollbar_button_hover_color = scrollbar_button_hover_color)
        self.place(relx = x, rely = y, anchor = anchor)

        self.parent = parent
        self.fgColor = fg_color
        self.textColor = textColor
        self.small = small
        self.highlightManaged = highlightManaged

        self.grid_columnconfigure(0, weight = 3)
        self.grid_columnconfigure(1, weight = 4)
        self.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23), weight = 1)
        if self.small:
            # Small only has goal difference and points as extra data
            self.grid_columnconfigure(2, weight = 10)
            self.grid_columnconfigure((3, 4, 5), weight = 1)

            ctk.CTkLabel(self, text = "GD", fg_color = self.fgColor, text_color = self.textColor, font = (APP_FONT_BOLD, 12), height = 5).grid(row = 0, column = 4, pady = (5, 0))
            ctk.CTkLabel(self, text = "P", fg_color = self.fgColor, text_color = self.textColor, font = (APP_FONT_BOLD, 12), height = 5, width = 5).grid(row = 0, column = 5, pady = (5, 0))
        else:
            # Otherwise all extra data
            self.grid_columnconfigure((2, 3, 4, 5, 6, 7, 8, 9, 10), weight = 1)
            self.grid_propagate(False)

            ctk.CTkLabel(self, text = "W", fg_color = self.fgColor, text_color = self.textColor, font = (APP_FONT_BOLD, 12), height = 5).grid(row = 0, column = 4, pady = (5, 0))
            ctk.CTkLabel(self, text = "D", fg_color = self.fgColor, text_color = self.textColor, font = (APP_FONT_BOLD, 12), height = 5).grid(row = 0, column = 5, pady = (5, 0))
            ctk.CTkLabel(self, text = "L", fg_color = self.fgColor, text_color = self.textColor, font = (APP_FONT_BOLD, 12), height = 5).grid(row = 0, column = 6, pady = (5, 0))
            ctk.CTkLabel(self, text = "GF", fg_color = self.fgColor, text_color = self.textColor, font = (APP_FONT_BOLD, 12), height = 5).grid(row = 0, column = 7, pady = (5, 0))
            ctk.CTkLabel(self, text = "GA", fg_color = self.fgColor, text_color = self.textColor, font = (APP_FONT_BOLD, 12), height = 5).grid(row = 0, column = 8, pady = (5, 0))
            ctk.CTkLabel(self, text = "GD", fg_color = self.fgColor, text_color = self.textColor, font = (APP_FONT_BOLD, 12), height = 5).grid(row = 0, column = 9, pady = (5, 0))
            ctk.CTkLabel(self, text = "P", fg_color = self.fgColor, text_color = self.textColor, font = (APP_FONT_BOLD, 12), height = 5, width = 5).grid(row = 0, column = 10, pady = (5, 0))

        ctk.CTkLabel(self, text = "#", fg_color = self.fgColor, text_color = self.textColor, height = 5).grid(row = 0, column = 0, sticky = "e", pady = (10, 5))
        ctk.CTkLabel(self, text = "Team", fg_color = self.fgColor, text_color = self.textColor, font = (APP_FONT_BOLD, 12), height = 5).grid(row = 0, column = 2, sticky = "w", pady = (5, 0))
        ctk.CTkLabel(self, text = "GP", fg_color = self.fgColor, text_color = self.textColor, font = (APP_FONT_BOLD, 12), height = 5).grid(row = 0, column = 3, pady = (5, 0))

    def defineManager(self, manager_id):
        """
        Defines the manager for whom the league table is being displayed.

        Args:
            manager_id (str): The ID of the manager.
        """
        
        self.manager_id = manager_id
        self.team = Teams.get_teams_by_manager(self.manager_id)[0]
        self.league = LeagueTeams.get_league_by_team(self.team.id)

    def addLeagueTable(self):
        """
        Populates the league table with team statistics.
        """

        teamsData = LeagueTeams.get_teams_by_position(self.league.league_id)

        for i, team in enumerate(teamsData):
            teamName = Teams.get_team_by_id(team.team_id)
            team_logo_blob = teamName.logo
            team_image = Image.open(io.BytesIO(team_logo_blob))
            team_image.thumbnail((20, 20))
            ctk_team_image = ctk.CTkImage(team_image, None, (team_image.width, team_image.height))

            if self.highlightManaged and self.team.name == teamName.name:    
                font = (APP_FONT_BOLD, 12)
            else:
                font = (APP_FONT, 12)

            ctk.CTkLabel(self, text = i + 1, fg_color = self.fgColor, text_color = self.textColor, font = font).grid(row = i + 1, column = 0, sticky = "e")
            ctk.CTkLabel(self, image = ctk_team_image, text = "", fg_color = self.fgColor).grid(row = i + 1, column = 1)
            ctk.CTkLabel(self, text = teamName.name, fg_color = self.fgColor, text_color = self.textColor, font = font).grid(row = i + 1, column = 2, sticky = "w")
            ctk.CTkLabel(self, text = team.games_won + team.games_lost + team.games_drawn, fg_color = self.fgColor, text_color = self.textColor, font = font).grid(row = i + 1, column = 3)
            if self.small:
                ctk.CTkLabel(self, text = team.goals_scored - team.goals_conceded, fg_color = self.fgColor, text_color = self.textColor, font = font).grid(row = i + 1, column = 4)
                ctk.CTkLabel(self, text = team.points, fg_color = self.fgColor, text_color = self.textColor, font = font).grid(row = i + 1, column = 5)
            else:
                ctk.CTkLabel(self, text = team.games_won, fg_color = self.fgColor, text_color = self.textColor, height = 5, font = font).grid(row = i + 1, column = 4)
                ctk.CTkLabel(self, text = team.games_drawn, fg_color = self.fgColor, text_color = self.textColor, height = 5, font = font).grid(row = i + 1, column = 5)
                ctk.CTkLabel(self, text = team.games_lost, fg_color = self.fgColor, text_color = self.textColor, height = 5, font = font).grid(row = i + 1, column = 6)
                ctk.CTkLabel(self, text = team.goals_scored, fg_color = self.fgColor, text_color = self.textColor, height = 5, font = font).grid(row = i + 1, column = 7)
                ctk.CTkLabel(self, text = team.goals_conceded, fg_color = self.fgColor, text_color = self.textColor, height = 5, font = font).grid(row = i + 1, column = 8)
                ctk.CTkLabel(self, text = team.goals_scored - team.goals_conceded, fg_color = self.fgColor, text_color = self.textColor, height = 5, font = font).grid(row = i + 1, column = 9)
                ctk.CTkLabel(self, text = team.points, fg_color = self.fgColor, text_color = self.textColor, height = 5, font = font).grid(row = i + 1, column = 10)

class LeagueTable(ctk.CTkFrame):
    def __init__(self, parent, height, width, relx, rely, fg_color, anchor, textColor = "white", small = False, highlightManaged = False, corner_radius = 0):
        """
        Frame representing a league table with team statistics, found in the league tab and start menu.
        
        Args:
            parent (ctk.CTkFrame): The parent frame.
            height (int): The height of the frame.
            width (int): The width of the frame.
            x (float): The relative x position for placing the frame.
            y (float): The relative y position for placing the frame.
            fg_color (str): The foreground color of the frame.
            anchor (str): The anchor position for placing the frame.
            textColor (str): The text color for labels.
            small (bool): Whether to use a compact layout.
            highlightManaged (bool): Whether to highlight the managed team.
            corner_radius (int): The corner radius of the frame.
        """

        super().__init__(parent, fg_color = fg_color, width = width, height = height, corner_radius = corner_radius)
        self.place(relx = relx, rely = rely, anchor = anchor)

        self.height = height
        self.parent = parent
        self.fgColor = fg_color
        self.small = small
        self.highlightManaged = highlightManaged    
        self.textColor = textColor

        self.grid_columnconfigure(0, weight = 1)
        self.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23), weight = 1)
        if self.small:
            self.grid_columnconfigure(1, weight = 3)
            self.grid_columnconfigure(2, weight = 10)
            self.grid_columnconfigure((3, 4, 5), weight = 1)

            ctk.CTkLabel(self, text = "GD", fg_color = self.fgColor, text_color = self.textColor, font = (APP_FONT_BOLD, 12), height = 5).grid(row = 0, column = 4, pady = (5, 0))
            ctk.CTkLabel(self, text = "P", fg_color = self.fgColor, text_color = self.textColor, font = (APP_FONT_BOLD, 12), height = 5, width = 5).grid(row = 0, column = 5, pady = (5, 0))

            ctk.CTkLabel(self, text = "#", fg_color = self.fgColor, text_color = self.textColor, height = 5).grid(row = 0, column = 0, sticky = "e", pady = (10, 5))
            ctk.CTkLabel(self, text = "Team", fg_color = self.fgColor, text_color = self.textColor, font = (APP_FONT_BOLD, 12), height = 5).grid(row = 0, column = 2, sticky = "w", pady = (5, 0))
            ctk.CTkLabel(self, text = "GP", fg_color = self.fgColor, text_color = self.textColor, font = (APP_FONT_BOLD, 12), height = 5).grid(row = 0, column = 3, pady = (5, 0))
        else:
            self.grid_columnconfigure(1, weight = 1)
            self.grid_columnconfigure(2, weight = 1)
            self.grid_columnconfigure(3, weight = 3)
            self.grid_columnconfigure((4, 5, 6, 7, 8, 9, 10, 11), weight = 1)
            self.grid_propagate(False)

            ctk.CTkLabel(self, text = "W", fg_color = self.fgColor, text_color = self.textColor, font = (APP_FONT_BOLD, 12), height = 5).grid(row = 0, column = 5, pady = (5, 0))
            ctk.CTkLabel(self, text = "D", fg_color = self.fgColor, text_color = self.textColor, font = (APP_FONT_BOLD, 12), height = 5).grid(row = 0, column = 6, pady = (5, 0))
            ctk.CTkLabel(self, text = "L", fg_color = self.fgColor, text_color = self.textColor, font = (APP_FONT_BOLD, 12), height = 5).grid(row = 0, column = 7, pady = (5, 0))
            ctk.CTkLabel(self, text = "GF", fg_color = self.fgColor, text_color = self.textColor, font = (APP_FONT_BOLD, 12), height = 5).grid(row = 0, column = 8, pady = (5, 0))
            ctk.CTkLabel(self, text = "GA", fg_color = self.fgColor, text_color = self.textColor, font = (APP_FONT_BOLD, 12), height = 5).grid(row = 0, column = 9, pady = (5, 0))
            ctk.CTkLabel(self, text = "GD", fg_color = self.fgColor, text_color = self.textColor, font = (APP_FONT_BOLD, 12), height = 5).grid(row = 0, column = 10, pady = (5, 0))
            ctk.CTkLabel(self, text = "P", fg_color = self.fgColor, text_color = self.textColor, font = (APP_FONT_BOLD, 12), height = 5, width = 5).grid(row = 0, column = 11, pady = (5, 0))

            ctk.CTkLabel(self, text = "#", fg_color = self.fgColor, text_color = self.textColor, height = 5).grid(row = 0, column = 1, sticky = "w", pady = (10, 5))
            ctk.CTkLabel(self, text = "Team", fg_color = self.fgColor, text_color = self.textColor, font = (APP_FONT_BOLD, 12), height = 5).grid(row = 0, column = 3, sticky = "w", pady = (5, 0))
            ctk.CTkLabel(self, text = "GP", fg_color = self.fgColor, text_color = self.textColor, font = (APP_FONT_BOLD, 12), height = 5).grid(row = 0, column = 4, pady = (5, 0))

        self.grid_propagate(False)

    def defineManager(self, manager_id, managingLeague = True):
        """
        Defines the manager for whom the league table is being displayed.

        Args:
            manager_id (str): The ID of the manager.    
            managingLeague (bool): Whether the manager is managing the league being displayed.
        """
        
        self.manager_id = manager_id
        self.team = Teams.get_teams_by_manager(self.manager_id)[0]
        self.league = LeagueTeams.get_league_by_team(self.team.id)
        self.leagueData = League.get_league_by_id(self.league.league_id)

        self.highlightManaged = managingLeague
        self.div1 = self.leagueData.league_above is None

    def addLeagueTable(self):
        """
        Populates the league table with team statistics.
        """

        teamsData = LeagueTeams.get_teams_by_position(self.league.league_id)

        for i, team in enumerate(teamsData):
            teamData = Teams.get_team_by_id(team.team_id)
            team_image = Image.open(io.BytesIO(teamData.logo))
            team_image.thumbnail((20, 20))
            ctk_team_image = ctk.CTkImage(team_image, None, (team_image.width, team_image.height))

            if self.highlightManaged and self.team.name == teamData.name:    
                font = (APP_FONT_BOLD, 12)
            else:
                font = (APP_FONT, 12)
            
            if self.small:
                ctk.CTkLabel(self, text = team.goals_scored - team.goals_conceded, fg_color = self.fgColor, text_color = self.textColor, font = font).grid(row = i + 1, column = 4)
                ctk.CTkLabel(self, text = team.points, fg_color = self.fgColor, text_color = self.textColor, font = font).grid(row = i + 1, column = 5)

                ctk.CTkLabel(self, text = i + 1, fg_color = self.fgColor, text_color = self.textColor, font = font).grid(row = i + 1, column = 0, sticky = "e")
                ctk.CTkLabel(self, image = ctk_team_image, text = "", fg_color = self.fgColor).grid(row = i + 1, column = 1)
                ctk.CTkLabel(self, text = teamData.name, fg_color = self.fgColor, text_color = self.textColor, font = font).grid(row = i + 1, column = 2, sticky = "w")
                ctk.CTkLabel(self, text = team.games_won + team.games_lost + team.games_drawn, fg_color = self.fgColor, text_color = self.textColor, font = font).grid(row = i + 1, column = 3)
            else:
                if i < self.leagueData.promotion:
                    canvas = ctk.CTkCanvas(self, width = 5, height = self.height / 14.74, bg = PIE_GREEN, bd = 0, highlightthickness = 0)
                    canvas.grid(row = i + 1, column = 0)
                elif i + 1 > 20 - self.leagueData.relegation:
                    canvas = ctk.CTkCanvas(self, width = 5, height = self.height / 14.74, bg = PIE_RED, bd = 0, highlightthickness = 0)
                    canvas.grid(row = i + 1, column = 0)
                elif not self.div1 and i in [3, 4, 5, 6]:
                    canvas = ctk.CTkCanvas(self, width = 5, height = self.height / 14.74, bg = FRUSTRATED_COLOR, bd = 0, highlightthickness = 0)
                    canvas.grid(row = i + 1, column = 0)

                ctk.CTkLabel(self, text = i + 1, fg_color = self.fgColor, text_color = self.textColor, font = font).grid(row = i + 1, column = 1, sticky = "w")
                ctk.CTkLabel(self, image = ctk_team_image, text = "", fg_color = self.fgColor).grid(row = i + 1, column = 2, sticky = "w")
                ctk.CTkLabel(self, text = teamData.name, fg_color = self.fgColor, text_color = self.textColor, font = font).grid(row = i + 1, column = 3, sticky = "w")
                
                ctk.CTkLabel(self, text = team.games_won + team.games_lost + team.games_drawn, fg_color = self.fgColor, text_color = self.textColor, font = font).grid(row = i + 1, column = 4)
                ctk.CTkLabel(self, text = team.games_won, fg_color = self.fgColor, text_color = self.textColor, height = 5, font = font).grid(row = i + 1, column = 5)
                ctk.CTkLabel(self, text = team.games_drawn, fg_color = self.fgColor, text_color = self.textColor, height = 5, font = font).grid(row = i + 1, column = 6)
                ctk.CTkLabel(self, text = team.games_lost, fg_color = self.fgColor, text_color = self.textColor, height = 5, font = font).grid(row = i + 1, column = 7)
                ctk.CTkLabel(self, text = team.goals_scored, fg_color = self.fgColor, text_color = self.textColor, height = 5, font = font).grid(row = i + 1, column = 8)
                ctk.CTkLabel(self, text = team.goals_conceded, fg_color = self.fgColor, text_color = self.textColor, height = 5, font = font).grid(row = i + 1, column = 9)
                ctk.CTkLabel(self, text = team.goals_scored - team.goals_conceded, fg_color = self.fgColor, text_color = self.textColor, height = 5, font = font).grid(row = i + 1, column = 10)
                ctk.CTkLabel(self, text = team.points, fg_color = self.fgColor, text_color = self.textColor, height = 5, font = font).grid(row = i + 1, column = 11)

    def clearTable(self):
        """
        Clears the league table of all team statistics.
        """
        
        for widget in self.winfo_children():
            if widget.grid_info()["row"] > 0:
                widget.destroy()

class next5Matches(ctk.CTkFrame):
    def __init__(self, parent, manager_id, fg_color, width, height, frameHeight, relx, rely, anchor, textY, parentTab, corner_radius = 0):
        """
        Frame displaying the next 5 matches for a team managed by the specified manager, found in the hub and team profiles.
        
        Args:
            parent (ctk.CTkFrame): The parent frame.
            manager_id (str): The ID of the manager.
            fg_color (str): The foreground color of the frame.
            width (int): The width of the frame.
            height (int): The height of the frame.
            frameHeight (int): The height of each match frame.
            relx (float): The relative x position for placing the frame.
            rely (float): The relative y position for placing the frame.
            anchor (str): The anchor position for placing the frame.
            textY (float): The relative y position for team name labels within match frames.
            parentTab (ctk.CTkFrame): The parent tab frame for team logos.
            corner_radius (int): The corner radius of the frame.
        """
        
        super().__init__(parent, fg_color = fg_color, width = width, height = height, corner_radius = corner_radius)
        self.place(relx = relx, rely = rely, anchor = anchor)

        self.parent = parent
        self.manager_id = manager_id
        self.fgColor = fg_color
        self.width = width
        self.frameHeight = frameHeight
        self.textY = textY
        self.parentTab = parentTab
        self.corner_radius = corner_radius

        self.pack_propagate(False)

        self.team = Teams.get_teams_by_manager(self.manager_id)[0]
        self.league = LeagueTeams.get_league_by_team(self.team.id)

    def showNext5Matches(self):
        """
        Displays the next 5 matches for the team.
        """

        next5 = Matches.get_team_next_5_matches(self.team.id, Game.get_game_date(Managers.get_all_user_managers()[0].id))

        ctk.CTkLabel(self, text = "Next 5 Matches", font = (APP_FONT_BOLD, 30), text_color = "white", fg_color = self.fgColor).pack(fill = "both", pady = (10, 0))

        for match in next5:
            matchFrame = ctk.CTkFrame(self, fg_color = self.fgColor, width = self.width, height = self.frameHeight, corner_radius = self.corner_radius)
            matchFrame.pack(fill = "both")

            ctk.CTkLabel(matchFrame, text = "VS", font = (APP_FONT_BOLD, 20), text_color = "white", fg_color = self.fgColor).place(relx = 0.5, rely = 0.5, anchor = "center")

            homeTeam = Teams.get_team_by_id(match.home_id)
            awayTeam = Teams.get_team_by_id(match.away_id) 

            homeImage = Image.open(io.BytesIO(homeTeam.logo))
            homeImage.thumbnail((50, 50))
            homeLogo = TeamLogo(matchFrame, homeImage, homeTeam, self.fgColor, 0.35, 0.5, "center", self.parentTab, clickable = match.home_id != self.team.id)

            awayImage = Image.open(io.BytesIO(awayTeam.logo))
            awayImage.thumbnail((50, 50))
            awayLogo = TeamLogo(matchFrame, awayImage, awayTeam, self.fgColor, 0.65, 0.5, "center", self.parentTab, clickable = match.away_id != self.team.id)

            ctk.CTkLabel(matchFrame, text = homeTeam.name.split()[0], font = (APP_FONT, 13), text_color = "white", fg_color = self.fgColor).place(relx = 0.15, rely = self.textY, anchor = "center")
            ctk.CTkLabel(matchFrame, text = homeTeam.name.split()[1], font = (APP_FONT_BOLD, 18), text_color = "white", fg_color = self.fgColor).place(relx = 0.15, rely = 0.63, anchor = "center")
            ctk.CTkLabel(matchFrame, text = awayTeam.name.split()[0], font = (APP_FONT, 13), text_color = "white", fg_color = self.fgColor).place(relx = 0.85, rely = self.textY, anchor = "center")
            ctk.CTkLabel(matchFrame, text = awayTeam.name.split()[1], font = (APP_FONT_BOLD, 18), text_color = "white", fg_color = self.fgColor).place(relx = 0.85, rely = 0.63, anchor = "center")

class WinRatePieChart(ctk.CTkCanvas):
    def __init__(self, parent, gamesPlayed, gamesWon, gamesLost, figSize, fgColor, relx, rely, anchor):
        """
        Frame displaying a pie chart representing win, loss, and draw rates, found in the start menu and manager profile.
        
        Args:
            parent (ctk.CTkFrame): The parent frame.
            gamesPlayed (int): The total number of games played.
            gamesWon (int): The number of games won.
            gamesLost (int): The number of games lost.
            figSize (tuple): The size of the figure.
            fgColor (str): The foreground color of the frame.
            relx (float): The relative x position for placing the frame.
            rely (float): The relative y position for placing the frame.
            anchor (str): The anchor position for placing the frame.
        """

        super().__init__(parent) 

        if gamesPlayed == 0:
            colours = [PIE_GREY]
            sizes = [100]
        else:
            winRate = (gamesWon / gamesPlayed) * 100
            lossRate = (gamesLost / gamesPlayed) * 100
            drawRate = 100 - winRate - lossRate
            
            sizes = []
            colours = []

            if winRate > 0:
                sizes.append(winRate)
                colours.append(PIE_GREEN)

            if lossRate > 0:
                sizes.append(lossRate)
                colours.append(PIE_RED)

            if drawRate > 0:
                sizes.append(drawRate)
                colours.append(PIE_GREY)

        piechart = Figure(figsize = figSize, dpi = 100, facecolor = fgColor)
        ax = piechart.add_subplot(111)

        ax.pie(sizes, colors = colours, autopct = '%d%%')
        ax.axis('equal')

        canvas = FigureCanvasTkAgg(piechart, master = parent)
        canvas.draw()
        canvas.get_tk_widget().place(relx = relx, rely = rely, anchor = anchor)

class TrophiesFrame(ctk.CTkFrame):
    def __init__(self, parent, id_, fg_color, width, height, corner_radius, relx, rely, anchor, team = True):
        """
        Frame displaying the trophies won by a team, found in team profiles.

        Args:
            parent (ctk.CTkFrame): The parent frame.
            id_ (str): The ID of the team.
            fg_color (str): The foreground color of the frame.
            width (int): The width of the frame.
            height (int): The height of the frame.
            corner_radius (int): The corner radius of the frame.
            relx (float): The relative x position for placing the frame.
            rely (float): The relative y position for placing the frame.
            anchor (str): The anchor position for placing the frame.
            team (bool): Whether the ID is for a team (True) or a manager (False).
        """

        super().__init__(parent, fg_color = fg_color, width = width, height = height, corner_radius = corner_radius)
        self.place(relx = relx, rely = rely, anchor = anchor)

        self.id = id_

        ctk.CTkLabel(self, text = "Trophies", font = (APP_FONT_BOLD, 30), fg_color = GREY_BACKGROUND).place(relx = 0.5, rely = 0.1, anchor = "center")

        if team:
            self.trophies = Trophies.get_all_trophies_by_team(self.id)
        else:
            self.trophies = Trophies.get_all_trophies_by_manager(self.id)

        self.comps = {}

        if self.trophies:
            for trophy in self.trophies:
                if trophy.competition_id not in self.comps:
                    self.comps[trophy.competition_id] = {}
                    self.comps[trophy.competition_id]["years"] = f"{trophy.year}, "
                else:
                    self.comps[trophy.competition_id]["years"] += f"{trophy.year}, "

            for competition in self.comps:
                self.league = League.get_league_by_id(competition)

                src = Image.open(io.BytesIO(self.league.logo))
                src.thumbnail((100, 100))
                logo = ctk.CTkImage(src, None, (src.width, src.height))
                ctk.CTkLabel(self, image = logo, text = "", fg_color = GREY_BACKGROUND).place(relx = 0.2, rely = 0.3, anchor = "center")
                ctk.CTkLabel(self, text = f"{self.league.name}", font = (APP_FONT, 25), fg_color = GREY_BACKGROUND).place(relx = 0.5, rely = 0.3, anchor = "center")
                ctk.CTkLabel(self, text = f"{self.formatYears(self.comps[competition]['years'])}", font = (APP_FONT, 15), fg_color = GREY_BACKGROUND).place(relx = 0.1, rely = 0.45, anchor = "w")

    def formatYears(self, years):
        """
        Formats a string of years into a more readable format.
        """
        
        years = years.split(",")
        return " - ".join(years) 
    
class FootballPitchHorizontal(ctk.CTkFrame):
    def __init__(self, parent, width, height, relx, rely, anchor, fgColor):
        """
        Frame representing a horizontal football pitch, found in player profiles

        Args:
            parent (ctk.CTkFrame): The parent frame.
            width (int): The width of the frame.
            height (int): The height of the frame.
            relx (float): The relative x position for placing the frame.
            rely (float): The relative y position for placing the frame.
            anchor (str): The anchor position for placing the frame.
            fgColor (str): The foreground color of the frame.
        """

        super().__init__(parent, width = width, height = height, fg_color = fgColor)
        self.place(relx = relx, rely = rely, anchor = anchor)

        # Adjustable pitch dimensions (Horizontal)
        self.pitch_width = width  # Width of the pitch in pixels (horizontal)
        self.pitch_height = height  # Height of the pitch in pixels (vertical)

        # Canvas to draw the pitch
        self.canvas = ctk.CTkCanvas(self, width = self.pitch_width, height = self.pitch_height, bg = fgColor)
        self.canvas.pack()

    def draw_pitch(self):
        """
        Draws the football pitch on the canvas.
        """
        
        # Draw center circle
        center_x = self.pitch_width / 2
        center_y = self.pitch_height / 2
        self.canvas.create_oval(center_x - 50, center_y - 50, center_x + 50, center_y + 50, outline = "white", width = 2)
        self.canvas.create_line(center_x, 0, center_x, self.pitch_height + 5, fill = "white", width = 2)

        # Draw penalty areas
        self.canvas.create_rectangle(0, 25, 75, 225, outline = "white", width = 2)
        self.canvas.create_rectangle(self.pitch_width - 71, 25, self.pitch_width + 5, 225, outline = "white", width = 2)

        # Draw goal areas
        self.canvas.create_rectangle(0, self.pitch_height / 3, 25, self.pitch_height * 2 / 3, outline = "white", width = 2)
        self.canvas.create_rectangle(self.pitch_width - 21, self.pitch_height / 3, self.pitch_width + 5, self.pitch_height * 2 / 3, outline = "white", width = 2)

class FootballPitchVertical(ctk.CTkFrame):
    def __init__(self, parent, width, height, relx, rely, anchor, fgColor, pitchColor):
        """
        Frame representing a vertical football pitch, found in the tactics tab, emails, match profiles and in-game.

        Args:
            parent (ctk.CTkFrame): The parent frame.
            width (int): The width of the frame.
            height (int): The height of the frame.
            relx (float): The relative x position for placing the frame.
            rely (float): The relative y position for placing the frame.
            anchor (str): The anchor position for placing the frame.
            fgColor (str): The foreground color of the frame.
            pitchColor (str): The color of the pitch.
        """

        super().__init__(parent, width = width - 50, height = height - 100, fg_color = fgColor)
        self.place(relx = relx, rely = rely, anchor = anchor)

        # Adjustable pitch dimensions (Horizontal)
        self.pitch_width = width  # Width of the pitch in pixels (horizontal)
        self.pitch_height = height  # Height of the pitch in pixels (vertical)

        self.canvas = ctk.CTkCanvas(self, width = self.pitch_width, height = self.pitch_height, bg = pitchColor)
        self.canvas.place(relx = 0.5, rely = 0.5, anchor = "center")

        self.draw_pitch()

    def draw_pitch(self):
        """
        Draws the football pitch on the canvas.
        """

        # Draw center circle
        center_x = self.pitch_width / 2
        center_y = self.pitch_height / 2
        self.canvas.create_oval(center_x - 50, center_y - 50, center_x + 50, center_y + 50, outline = "white", width = 2)
        self.canvas.create_line(0, center_y, self.pitch_width + 5, center_y, fill = "white", width = 2)

        # Draw penalty areas
        self.canvas.create_rectangle(self.pitch_width * (5/18), 0, self.pitch_width * (13/18), self.pitch_height * (4/27), outline = "white", width = 2)
        self.canvas.create_rectangle(self.pitch_width * (5/18), self.pitch_height - self.pitch_height * (19/135), self.pitch_width * (13/18), self.pitch_height + 5, outline = "white", width = 2)

        # Draw goal areas
        self.canvas.create_rectangle(self.pitch_width * (7/18), 0, self.pitch_width * (11/18), self.pitch_height * (8/135), outline = "white", width = 2)
        self.canvas.create_rectangle(self.pitch_width * (7/18), self.pitch_height - self.pitch_height * (7/135), self.pitch_width * (11/18), self.pitch_height + 5, outline = "white", width = 2)

class FootballPitchPlayerPos(FootballPitchHorizontal):
    def __init__(self, parent, width, height, relx, rely, anchor, fgColor):
        """
        Frame representing a horizontal football pitch with player positions, found in player profiles.

        Args:
            parent (ctk.CTkFrame): The parent frame.
            width (int): The width of the frame.
            height (int): The height of the frame.
            relx (float): The relative x position for placing the frame.
            rely (float): The relative y position for placing the frame.
            anchor (str): The anchor position for placing the frame.
            fgColor (str): The foreground color of the frame.
        """
        
        super().__init__(parent, width, height, relx, rely, anchor, fgColor)
        super().draw_pitch()

    def add_player_positions(self, highlighted_positions):
        """
        Adds player position circles to the pitch, highlighting specified positions.
        """
        
        # Define player positions in the form (x, y) with labels for each position
        player_positions = {
            "GK": (25, self.pitch_height / 2),  # Goalkeeper at the far left
            "LB": (90, self.pitch_height / 4),  # Left Back
            "RB": (90, self.pitch_height * 3 / 4),  # Right Back
            "CB": (90, self.pitch_height / 2),  # Center Back
            "DM": (155, self.pitch_height / 2),  # Defensive Midfielder
            "LM": (220, self.pitch_height / 4),  # Left Midfielder
            "CM": (220, self.pitch_height / 2),  # Central Midfielder
            "RM": (220, self.pitch_height * 3 / 4),  # Right Midfielder
            "LW": (285, self.pitch_height / 4),  # Left Winger
            "RW": (285, self.pitch_height * 3 / 4),  # Right Winger
            "AM": (285, self.pitch_height / 2),  # Attacking Midfielder
            "CF": (350, self.pitch_height / 2),  # Center Forward
        }

        # Size of the player circles
        player_radius = 12

        # Draw circles for each player position and label them
        for position, (x, y) in player_positions.items():

            if position in highlighted_positions:
                fill_color = APP_BLUE
                outline_color = APP_BLUE
            else:
                fill_color = TKINTER_BACKGROUND
                outline_color = GREY
            self.canvas.create_oval(x - player_radius, y - player_radius, x + player_radius, y + player_radius, fill = fill_color, outline = outline_color) 

class FootballPitchLineup(FootballPitchVertical):
    def __init__(self, parent, width, height, relx, rely, anchor, fgColor, pitchColor):
        """
        Football pitch frame for displaying player lineups with drop zones, found in the tactics tab and in-game for substitutions

        Args:
            parent (ctk.CTkFrame): The parent frame.
            width (int): The width of the frame.
            height (int): The height of the frame.
            relx (float): The relative x position for placing the frame.
            rely (float): The relative y position for placing the frame.
            anchor (str): The anchor position for placing the frame.
            fgColor (str): The foreground color of the frame.
            pitchColor (str): The color of the pitch.
        """
       
        super().__init__(parent, width, height, relx, rely, anchor, fgColor, pitchColor)
        super().draw_pitch()

        self.pitchColor = pitchColor

        self.counter = 0
        self.drop_zones = []
        self.zone_occupancies = {}

        self.create_drop_zones()

    def create_drop_zones(self):
        """
        Creates drop zones on the pitch for player positions.
        """
        
        for pos, pitch_pos in POSITIONS_PITCH_POSITIONS.items():
            zone = ctk.CTkFrame(self, width = 65, height = 65, fg_color = self.pitchColor, bg_color = self.pitchColor, border_color = "red", border_width = 2, background_corner_colors = [self.pitchColor, self.pitchColor, self.pitchColor, self.pitchColor], corner_radius = 10)
            zone.pos = pos
            zone.pitch_pos = pitch_pos

            self.drop_zones.append(zone)
            self.zone_occupancies[pos] = 0  # Initialize occupancy status

    def increment_counter(self):
        """
        Increments the internal counter by 1.
        """

        self.counter += 1
    
    def decrement_counter(self):
        """
        Decrements the internal counter by 1.
        """
        
        self.counter -= 1

    def get_counter(self):
        """
        Returns the current value of the internal counter.
        """
        
        return self.counter

    def reset_counter(self):
        """
        Resets the internal counter to 0.
        """
        
        self.counter = 0

    def set_counter(self, num):
        """
        Sets the internal counter to a specific value.

        Args:
            num (int): The value to set the counter to.
        """
        
        self.counter = num
        
class FootballPitchMatchDay(FootballPitchVertical):
    def __init__(self, parent, width, height, relx, rely, anchor, fgColor, pitchColor):
        """
        Football pitch frame for displaying player positions during match day, found in match profiles, emails, and in-game for lineups.

        Args:
            parent (ctk.CTkFrame): The parent frame.
            width (int): The width of the frame.
            height (int): The height of the frame.
            relx (float): The relative x position for placing the frame.
            rely (float): The relative y position for placing the frame.
            anchor (str): The anchor position for placing the frame.
            fgColor (str): The foreground color of the frame.
            pitchColor (str): The color of the pitch.
        """

        super().__init__(parent, width, height, relx, rely, anchor, fgColor, pitchColor)
        super().draw_pitch()
        
        self.player_radius = 15
        self.relx = relx
        self.rely = rely
        self.anchor = anchor
        self.icon_images = {}

        self.positions = {
            "Goalkeeper": (0.5, 0.94),      
            "Left Back": (0.12, 0.75),      
            "Right Back": (0.88, 0.75),     
            "Center Back Right": (0.675, 0.75),  
            "Center Back": (0.5, 0.75),  
            "Center Back Left": (0.325, 0.75),  
            "Defensive Midfielder": (0.5, 0.6),     
            "Defensive Midfielder Right": (0.65, 0.6),      
            "Defensive Midfielder Left": (0.35, 0.6),   
            "Left Midfielder": (0.12, 0.4),     
            "Central Midfielder Right": (0.65, 0.4),    
            "Central Midfielder": (0.5, 0.4),     
            "Central Midfielder Left": (0.35, 0.4),     
            "Right Midfielder": (0.88, 0.4),    
            "Left Winger": (0.12, 0.25),    
            "Right Winger": (0.88, 0.25),   
            "Attacking Midfielder": (0.5, 0.25),    
            "Striker Left": (0.3, 0.15),    
            "Striker Right": (0.7, 0.15),   
            "Center Forward": (0.5, 0.05),  
        }

        self.iconPositions = {
            "Sub": [(0.1, 0.1), None],
            "Goals": [(0.9, 0.9), True],
            "Cards": [(0, 0.5), False],
            "Assists": [(0.1, 0.9), False],
            "Missed Pens": [(1, 0.6), True],
        }

    def addIcon(self, icon_type, image, position, playerName, num):
        """
        Adds an icon to the player's oval on the pitch.

        Args:
            icon_type (str): The type of icon (e.g., "Sub", "Goals", "Cards", etc.).
            image (tk.PhotoImage): The image to use for the icon.
            position (str): The position of the player.
            playerName (str): The name of the player.
            num (int): The number of icons to display (for offsetting).
        """
        
        # Add the icon relative the the position oval (so 0.1, 0.1 is the top left of the oval)
        positions, offsetDirection = self.iconPositions[icon_type]
        key = f"{icon_type}_{position}_{num}"
        self.icon_images[key] = image  # Store the image in the dictionary
        
        # Apply offset if num > 1
        if num > 1:
            if offsetDirection is not None:  # Only apply offset if direction is specified
                offset = 0.25 * (num - 1)  # Calculate offset based on num
                if offsetDirection:  # True means positive offset
                    positions = positions[0] + offset, positions[1]
                else:  # False means negative offset
                    positions = positions[0] - offset, positions[1]
            else:
                positions = positions[0], positions[1]
        else:
            positions = positions[0], positions[1]

        # Use positions from self.positions dictionary (these are relative coordinates)
        player_relx, player_rely = self.positions[position]
        
        # Calculate the center position of the oval
        oval_center_x = player_relx * self.pitch_width
        oval_center_y = player_rely * self.pitch_height
        
        # Calculate the icon position relative to the oval center
        # positions[0] and positions[1] are relative offsets from the icon positions
        icon_x = oval_center_x + (positions[0] - 0.5) * (2 * self.player_radius)
        icon_y = oval_center_y + (positions[1] - 0.5) * (2 * self.player_radius)

        position_tag = f"{position.replace(' ', '_')}+{playerName.replace(' ', '_')}"
        self.canvas.create_image(icon_x, icon_y, image = image, tags = (position_tag, "icon"))

    def addRating(self, position, playerName, text, potm):
        """
        Adds a rating oval with text to the player's oval on the pitch.

        Args:
            position (str): The position of the player.
            playerName (str): The name of the player.
            text (float): The rating text to display.
            potm (bool): Whether the rating is for Player of the Month.
        """
        
        # Use positions from self.positions dictionary (these are relative coordinates)

        player_relx, player_rely = self.positions[position]
        
        # Calculate the center position of the oval
        oval_center_x = player_relx * self.pitch_width
        oval_center_y = player_rely * self.pitch_height
        
        # Calculate the icon position relative to the oval center
        # positions[0] and positions[1] are relative offsets from the icon positions
        icon_x = oval_center_x + (0.9 - 0.5) * (2 * self.player_radius)
        icon_y = oval_center_y + (0.1 - 0.5) * (2 * self.player_radius)

        if text >= 7:
            oval_color = PIE_GREEN
        elif text >= 5:
            oval_color = NEUTRAL_COLOR
        else:
            oval_color = PIE_RED

        if potm:
            oval_color = POTM_BLUE

        # Text has at least 1 dp and max 2 dps
        formatted_text = text
        if "." not in str(text):
            formatted_text = f"{text}.0"
        elif len(str(text).split(".")[1]) == 1:
            formatted_text = f"{text}0"

        position_tag = f"{position.replace(' ', '_')}+{playerName.replace(' ', '_')}"

        # === Font settings ===
        font_name = APP_FONT_BOLD
        font_size = 9
        font = tkFont.Font(family = font_name, size = font_size)

        # === Measure text width ===
        text_width = font.measure(formatted_text)
        padding_x = 6  # left/right padding
        padding_y = 2  # top/bottom padding

        rect_width = text_width + 2 * padding_x
        rect_height = font.metrics("linespace") + 3 * padding_y
        radius = rect_height // 2 + 10

        x0 = icon_x - 5
        y0 = (icon_y - rect_height // 2) - 3
        x1 = x0 + rect_width
        y1 = y0 + rect_height

        # === Draw pill ===
        create_rounded_rectangle(
            self.canvas,
            x0, y0, x1, y1,
            radius = radius,
            fill = oval_color,
            outline = oval_color,
            tags = (position_tag, "rating_oval")
        )

        # === Draw left-aligned text ===
        self.canvas.create_text(
            x0 + padding_x,
            icon_y - 3,
            text = formatted_text,
            fill = "white",
            font = (font_name, font_size),
            anchor = "w",  # west (left-aligned)
            tags = (position_tag, "rating_text")
        )

    def updateRating(self, position, playerName, newRating):
        """
        Updates the rating oval and text for a player on the pitch.
        """
        
        position_tag = f"{position.replace(' ', '_')}+{playerName.replace(' ', '_')}"
        self.canvas.delete(f"{position_tag}_rating_oval")
        self.canvas.delete(f"{position_tag}_rating_text")
        self.addRating(position, playerName, newRating, False)

    def addInjuryIcon(self, position, playerName, image):
        """
        Adds an injury icon to the player's oval on the pitch.

        Args:
            position (str): The position of the player.
            playerName (str): The name of the player.
            image (ctk.CTkImage): The injury icon image.
        """

        # Store the image to prevent garbage collection
        key = f"injury_{position}"
        self.icon_images[key] = image
        position_tag = f"{position.replace(' ', '_')}+{playerName.replace(' ', '_')}"

        text_tag = f"player_{position_tag}_text"
        playerName = self.canvas.itemcget(text_tag, "text")
        self.canvas.delete(text_tag) 

        # Add the text back offset to the right and add the image to the left of the text
        relx, rely = self.positions[position]
        text_x = relx * self.pitch_width + 15
        text_y = rely * self.pitch_height + 25

        self.canvas.create_text(
            text_x,
            text_y,
            text = playerName,
            fill = "white",
            font = (APP_FONT, 10),
            tags = text_tag
        )

        self.canvas.create_image(text_x - 30, text_y, image = image, tags = (position_tag, "injury_icon"))

    def addPlayer(self, position, playerName, matchday = False):
        """
        Adds a player oval and name to the pitch at the specified position.

        Args:
            position (str): The position of the player.
            playerName (str): The name of the player.
            matchday (bool): Whether to add a default rating for matchday display.
        """

        relx, rely = self.positions[position]
        position_tag = f"{position.replace(' ', '_')}+{playerName.replace(' ', '_')}"

        oval_tag = f"player_{position_tag}_oval"
        text_tag = f"player_{position_tag}_text"

        self.canvas.create_oval(
            relx * self.pitch_width - self.player_radius,
            rely * self.pitch_height - self.player_radius,
            relx * self.pitch_width + self.player_radius,
            rely * self.pitch_height + self.player_radius,
            fill = APP_BLUE,
            outline = APP_BLUE,
            tags = oval_tag
        )

        self.canvas.create_text(
            relx * self.pitch_width,
            rely * self.pitch_height + 25,
            text = playerName,
            fill = "white",
            font = (APP_FONT, 10),
            tags = text_tag
        )

        if matchday:
            self.addRating(position, playerName, 6.0, False)

    def removePlayer(self, position, playerName):
        """
        Removes a player oval, name, and any associated icons from the pitch.

        Args:
            position (str): The position of the player to remove.
            playerName (str): The name of the player to remove.
        """
        
        position_tag = f"{position.replace(' ', '_')}+{playerName.replace(' ', '_')}"
        oval_tag = f"player_{position_tag}_oval"
        text_tag = f"player_{position_tag}_text"

        # Delete the player oval and text
        self.canvas.delete(oval_tag)
        self.canvas.delete(text_tag)
        
        # Delete any icons associated with this position
        self.canvas.delete(position_tag)  # This will delete all items with this tag including icons

        # Clear any stored images for this position
        for key in list(self.icon_images.keys()):
            if position_tag in key:
                del self.icon_images[key]

    def movePlayer(self, oldPosition, newPosition, playerName):

        if oldPosition not in self.positions or newPosition not in self.positions:
            return

        old_pos_tag = f"{oldPosition.replace(' ', '_')}+{playerName.replace(' ', '_')}"
        new_pos_tag = f"{newPosition.replace(' ', '_')}+{playerName.replace(' ', '_')}"

        oval_tag_old = f"player_{old_pos_tag}_oval"
        text_tag_old = f"player_{old_pos_tag}_text"
        oval_tag_new = f"player_{new_pos_tag}_oval"
        text_tag_new = f"player_{new_pos_tag}_text"

        # Find the oval item for the old position (used to compute old centre)
        oval_items = self.canvas.find_withtag(oval_tag_old)
        if not oval_items:
            return
        oval_item = oval_items[0]

        # Old centre: prefer coords() result if it gives 4 values, otherwise use bbox()
        oval_coords = self.canvas.coords(oval_item)
        if not oval_coords or len(oval_coords) != 4:
            bbox = self.canvas.bbox(oval_item)
            if not bbox:
                return
            ox0, oy0, ox1, oy1 = bbox
        else:
            ox0, oy0, ox1, oy1 = oval_coords

        old_cx = (ox0 + ox1) / 2
        old_cy = (oy0 + oy1) / 2

        # New centre (based on relative position)
        relx, rely = self.positions[newPosition]
        new_cx = relx * self.pitch_width
        new_cy = rely * self.pitch_height

        # Collect all items that include the old position tag OR the old player tags
        items_set = set()
        items_set.update(self.canvas.find_withtag(old_pos_tag))
        items_set.update(self.canvas.find_withtag(oval_tag_old))
        items_set.update(self.canvas.find_withtag(text_tag_old))

        for item in items_set:
            # canvas.coords(item) may return None for some item types; normalize to a list
            coords = self.canvas.coords(item)
            if not coords:
                coords = []

            # Compute current item centre
            item_cx = None
            item_cy = None

            if len(coords) == 4:
                x0, y0, x1, y1 = coords
                item_cx = (x0 + x1) / 2
                item_cy = (y0 + y1) / 2
                w = x1 - x0
                h = y1 - y0
            elif len(coords) == 2:
                item_cx, item_cy = coords
                w = None
                h = None
            else:
                # Fallback: place at new centre
                item_cx, item_cy = old_cx, old_cy

            dx = item_cx - old_cx
            dy = item_cy - old_cy

            new_item_cx = new_cx + dx
            new_item_cy = new_cy + dy

            # Move item by delta to preserve item type semantics (works for images, ovals, text, polygons)
            dx_move = new_item_cx - item_cx
            dy_move = new_item_cy - item_cy
            try:
                # move works across item types and avoids coordinate arity errors
                self.canvas.move(item, dx_move, dy_move)
            except Exception:
                # Fallback: if move fails and we have a bounding box, set coords explicitly
                if len(coords) == 4 and w is not None and h is not None:
                    nx0 = new_item_cx - w / 2
                    ny0 = new_item_cy - h / 2
                    nx1 = new_item_cx + w / 2
                    ny1 = new_item_cy + h / 2
                    try:
                        self.canvas.coords(item, nx0, ny0, nx1, ny1)
                    except Exception:
                        # Last resort: ignore this item if we can't position it
                        pass

            # Update tags for the item: replace occurrences of old_pos_tag with new_pos_tag
            tags = list(self.canvas.gettags(item))
            if tags:
                new_tags = []
                for t in tags:
                    if old_pos_tag in t:
                        new_tags.append(t.replace(old_pos_tag, new_pos_tag))
                    else:
                        new_tags.append(t)
                # Ensure player-specific text/oval tags get renamed fully
                renamed_tags = []
                for t in new_tags:
                    if f"player_{old_pos_tag}_oval" in t:
                        renamed_tags.append(t.replace(f"player_{old_pos_tag}_oval", oval_tag_new))
                    elif f"player_{old_pos_tag}_text" in t:
                        renamed_tags.append(t.replace(f"player_{old_pos_tag}_text", text_tag_new))
                    else:
                        renamed_tags.append(t)
                # Apply new tags
                try:
                    self.canvas.itemconfig(item, tags=tuple(renamed_tags))
                except Exception:
                    # if itemconfig fails for some reason, ignore tag update for that item
                    pass

        # Update the explicit player text item to show the provided playerName
        text_items = self.canvas.find_withtag(text_tag_old)
        for t in text_items:
            try:
                self.canvas.itemconfig(t, text=playerName)
            except Exception:
                pass

        # Update stored icon images keys to point to the new position
        new_icon_images = {}
        for key, img in list(self.icon_images.items()):
            if (f"_{oldPosition}_" in key) or key.startswith(f"injury_{oldPosition}") or key.endswith(f"_{oldPosition}"):
                new_key = key.replace(oldPosition, newPosition)
                new_icon_images[new_key] = img
            else:
                new_icon_images[key] = img

        self.icon_images = new_icon_images

    def placePitch(self):
        """
        Places the pitch frame at its designated relative position.
        """
        
        super().place(relx = self.relx, rely = self.rely, anchor = self.anchor)

    def removePitch(self):
        """
        Removes the pitch frame from view.
        """
        
        super().place_forget()

class LineupPlayerFrame(ctk.CTkFrame):
    def __init__(self, parent, relx, rely, anchor, fgColor, height, width, playerID, positionCode, position, removePlayer, updateLineup, substitutesFrame, swapLineupPositions, caStars, xDisabled = False):
        """
        Frame representing a player in the lineup on the football pitch, with drag-and-drop functionality, found in FootballPitchLineup.

        Args:
            parent (ctk.CTkFrame): The parent frame.
            relx (float): The relative x position for placing the frame.
            rely (float): The relative y position for placing the frame.
            anchor (str): The anchor position for placing the frame.
            fgColor (str): The foreground color of the frame.
            height (int): The height of the frame.
            width (int): The width of the frame.
            playerID (str): The ID of the player.
            positionCode (str): The code representing the player's position.
            position (str): The name of the player's position.
            removePlayer (function): Function to remove the player from the lineup.
            updateLineup (function): Function to update the lineup after changes.
            substitutesFrame (ctk.CTkFrame): Frame containing substitute players.
            swapLineupPositions (function): Function to swap player positions in the lineup.
            caStars (float): Current ability stars of the player.
            xDisabled (bool): Whether the remove button is disabled.
        """

        super().__init__(parent, fg_color = fgColor, width = width, height = height, corner_radius = 0)
        self.place(relx = relx, rely = rely, anchor = anchor)

        self.position = position
        self.parent = parent
        self.player = Players.get_player_by_id(playerID)
        self.removePlayer = removePlayer
        self.updateLineup = updateLineup
        self.substitutesFrame = substitutesFrame
        self.swapLineupPositions = swapLineupPositions
        self.caStars = caStars
        self.additionalPositions = []

        self.parent.zone_occupancies[self.position] = 1  # Set the initial occupancy status
        self.current_zone = self.position

        self.origin = [relx, rely]
        self.drag_start_x = 0
        self.drag_start_y = 0

        playerPositions = self.player.specific_positions.split(",")
        self.positionsTitles = []
        for pos in playerPositions:
            matching_titles = [position for position, code in POSITION_CODES.items() if code == pos]
            self.positionsTitles.extend(matching_titles)

        self.positionLabel = ctk.CTkLabel(self, text = positionCode, font = (APP_FONT, 10), height = 0, fg_color = fgColor)
        self.positionLabel.place(relx = 0.05, rely = 0.03, anchor = "nw")

        self.firstName = ctk.CTkLabel(self, text = self.player.first_name, font = (APP_FONT, 10), height = 0, width = 0, fg_color = fgColor)
        self.firstName.place(relx = 0.5, rely = 0.35, anchor = "center")
        self.lastName = ctk.CTkLabel(self, text = self.player.last_name, font = (APP_FONT_BOLD, 12), fg_color = fgColor, height = 0, width = 0)
        self.lastName.place(relx = 0.5, rely = 0.6, anchor = "center")

        self.removeButton = ctk.CTkButton(self, text = "X", font = (APP_FONT, 10), width = 0, height = 0, fg_color = fgColor, hover_color = CLOSE_RED, corner_radius = 0, command = self.remove)
        self.removeButton.place(relx = 0.95, rely = 0.03, anchor = "ne")

        if xDisabled:
            self.removeButton.configure(state = "disabled")

        self.attsFrame = ctk.CTkFrame(self, fg_color = fgColor, width = 55, height = 13, corner_radius = 0)
        self.attsFrame.place(relx = 0.5, rely = 0.95, anchor = "s")

        src = Image.open(f"Images/star_full.png")
        src.thumbnail((10, 10))
        img = ctk.CTkImage(src, None, (src.width, src.height))
        ctk.CTkLabel(self.attsFrame, image = img, text = "").place(relx = 0, rely = 0.3, anchor = "w")
        ctk.CTkLabel(self.attsFrame, text = round(self.caStars, 1), font = (APP_FONT, 12), fg_color = fgColor, height = 0, width = 0).place(relx = 0.22, rely = 0.3, anchor = "w")

        fitness = self.player.fitness
        if fitness > 75:
            src = "Images/fitness_good.png"
        elif fitness > 25:
            src = "Images/fitness_ok.png"
        else:
            src = "Images/fitness_bad.png"

        image = Image.open(src)
        image.thumbnail((10, 10))
        ctk_image = ctk.CTkImage(image, None, (image.width, image.height))
        ctk.CTkLabel(self.attsFrame, image = ctk_image, text = "", fg_color = fgColor, height = 0, width = 0).place(relx = 0.58, rely = 0.4, anchor = "w")

        sharpness = self.player.sharpness
        if sharpness > 75:
            src = "Images/sharpness_good.png"
        elif sharpness > 25:
            src = "Images/sharpness_ok.png"
        else:
            src = "Images/sharpness_bad.png"

        image = Image.open(src)
        image.thumbnail((10, 10))
        ctk_image = ctk.CTkImage(image, None, (image.width, image.height))
        ctk.CTkLabel(self.attsFrame, image = ctk_image, text = "", fg_color = fgColor, height = 0, width = 0).place(relx = 0.82, rely = 0.4, anchor = "w")

        self.bind("<Button-1>", self.start_drag)
        self.bind("<B1-Motion>", self.do_drag)
        self.bind("<ButtonRelease-1>", self.stop_drag)

        for child in self.winfo_children():
            if not isinstance(child, ctk.CTkButton) :
                child.bind("<Button-1>", self.start_drag)
                child.bind("<B1-Motion>", self.do_drag)
                child.bind("<ButtonRelease-1>", self.stop_drag)

        for child in self.attsFrame.winfo_children():
            child.bind("<Button-1>", self.start_drag)
            child.bind("<B1-Motion>", self.do_drag)
            child.bind("<ButtonRelease-1>", self.stop_drag)

    def showBorder(self):
        """
        Shows a green border around the player frame.
        """
        
        self.configure(border_color = PIE_GREEN, border_width = 2)

    def updateFrame(self):
        """
        Updates the player frame with the latest player information.
        """
        
        self.firstName.configure(text = self.player.first_name)
        self.lastName.configure(text = self.player.last_name)
        self.positionLabel.configure(text = POSITION_CODES[self.position])

        playerPositions = self.player.specific_positions.split(",")
        self.positionsTitles = []
        for pos in playerPositions:
            matching_titles = [position for position, code in POSITION_CODES.items() if code == pos]
            self.positionsTitles.extend(matching_titles)

    def start_drag(self, event):
        """
        Initiates the drag operation for the player frame.

        Args:
            event (tk.Event): The mouse button press event.
        """
        
        self.drag_start_x = event.x_root - self.winfo_rootx()
        self.drag_start_y = event.y_root - self.winfo_rooty()
        self.lift()

        for drop_zone in self.parent.drop_zones:
            pos = drop_zone.pos

            if pos not in self.positionsTitles and pos not in self.additionalPositions:
                continue

            # Check related positions: allow if all are empty or occupied by self
            related_positions = RELATED_POSITIONS.get(pos, [])
            if any(
                self.parent.zone_occupancies.get(rel_pos) == 1 and rel_pos != self.position
                for rel_pos in related_positions
            ):
                continue

            # If all checks pass, show the drop zone
            drop_zone.place(relx = drop_zone.pitch_pos[0], rely = drop_zone.pitch_pos[1], anchor = "center")

        self.parent.update_idletasks()

    def do_drag(self, event):
        """
        Handles the dragging motion of the player frame.
        
        Args:
            event (tk.Event): The mouse motion event.
        """

        # Calculate new position relative to the parent
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_w = self.parent.winfo_width()
        parent_h = self.parent.winfo_height()

        # Substitutes frame position
        subs_x = self.substitutesFrame.winfo_rootx() - parent_x
        subs_w = self.substitutesFrame.winfo_width()
        subs_right = subs_x + subs_w

        # Mouse position relative to parent
        rel_mouse_x = event.x_root - parent_x - self.drag_start_x + self.winfo_width() // 2
        rel_mouse_y = event.y_root - parent_y - self.drag_start_y + self.winfo_height() // 2

        # Clamping bounds
        min_x = self.winfo_width() // 2  # left bound = left of main frame
        max_x = subs_right - self.winfo_width() // 2  # right bound = right of subs frame

        min_y = self.winfo_height() // 2
        max_y = parent_h - self.winfo_height() // 2

        # Clamp values
        clamped_x = max(min_x, min(rel_mouse_x, max_x))
        clamped_y = max(min_y, min(rel_mouse_y, max_y))

        # Apply new position
        relx = clamped_x / parent_w
        rely = clamped_y / parent_h

        self.place(relx = relx, rely = rely, anchor = "center")

    def check_overlap(self, target_widget):
        """
        Checks if the dragged frame overlaps with the target widget's drop zone.

        Args:
            target_widget (ctk.CTkFrame): The target drop zone widget.
        """

        # Get absolute positions of the dragged frame
        drag_x = self.winfo_rootx()
        drag_y = self.winfo_rooty()
        drag_w = self.winfo_width()
        drag_h = self.winfo_height()

        # Get center of the target widget
        target_x = target_widget.winfo_rootx()
        target_y = target_widget.winfo_rooty()
        target_w = target_widget.winfo_width()
        target_h = target_widget.winfo_height()
        center_x = target_x + target_w // 2
        center_y = target_y + target_h // 2

        # Define the square region centered at the target's center
        half = 20 // 2
        square_left = center_x - half
        square_top = center_y - half
        square_right = center_x + half
        square_bottom = center_y + half

        # Check for rectangle overlap with the square region
        overlap_x = (drag_x < square_right) and (drag_x + drag_w > square_left)
        overlap_y = (drag_y < square_bottom) and (drag_y + drag_h > square_top)
        return overlap_x and overlap_y

    def stop_drag(self, event):
        """
        Stores the final position of the player frame after dragging.

        Args:
            event (tk.Event): The mouse button release event.
        """

        # Get absolute mouse position
        mouse_x = event.x_root
        mouse_y = event.y_root

        # Get substitutes frame absolute position and size
        subs_abs_x = self.substitutesFrame.winfo_rootx()
        subs_abs_y = self.substitutesFrame.winfo_rooty()
        subs_w = self.substitutesFrame.winfo_width()
        subs_h = self.substitutesFrame.winfo_height()

        # If mouse is inside the substitutes frame, remove the player
        if (subs_abs_x <= mouse_x <= subs_abs_x + subs_w) and (subs_abs_y <= mouse_y <= subs_abs_y + subs_h):
            self.remove()
            return
        
        dropped = False

        # Check for overlap with drop zones
        for drop_zone in self.parent.drop_zones:
            if drop_zone.winfo_manager() == "place":
                if self.parent.zone_occupancies[drop_zone.pos] == 0:
                    if self.check_overlap(drop_zone):
                        # Place the frame at the drop zone position
                        self.place(relx = drop_zone.pitch_pos[0], rely = drop_zone.pitch_pos[1], anchor = "center")
                        self.origin = [drop_zone.pitch_pos[0], drop_zone.pitch_pos[1]]

                        if self.current_zone:
                            self.parent.zone_occupancies[self.current_zone] = 0

                        self.parent.zone_occupancies[drop_zone.pos] = 1  # Update occupancy status
                        self.updateLineup(self.player, self.position, drop_zone.pos)
                        self.position = drop_zone.pos
                        self.positionLabel.configure(text = POSITION_CODES[self.position])
                        self.current_zone = drop_zone.pos

                        dropped = True
                        break

                else:
                    if self.check_overlap(drop_zone) and drop_zone.pos != self.position:
                        # We already know that the draged frame can be placed in the new positin. Only remains to check that the one being replaced can be placed in the dragged position.
                        for frame in self.parent.winfo_children():
                            # Find the frame that we are dropping onto
                            if isinstance(frame, LineupPlayerFrame) and frame.origin == list(drop_zone.pitch_pos) and POSITION_CODES[self.position] in frame.player.specific_positions:
                                self.place(relx = self.origin[0], rely = self.origin[1], anchor = "center")

                                temp = frame.player
                                frame.player = self.player
                                self.player = temp

                                self.updateFrame()
                                frame.updateFrame()

                                self.swapLineupPositions(self.position, drop_zone.pos)

                                dropped = True
                                break
                        
                        if dropped:
                            break

        # Hide all drop zones
        for drop_zone in self.parent.drop_zones:
            if drop_zone.winfo_manager() == "place":
                drop_zone.place_forget()

        if not dropped:
            self.place(relx = self.origin[0], rely = self.origin[1], anchor = "center")

    def remove(self):
        """
        Removes the player from the lineup and updates the parent frame.
        """

        player_name = f"{self.player.first_name} {self.player.last_name}"
        self.parent.zone_occupancies[self.current_zone] = 0  # Clear the occupancy status for the current zone

        for drop_zone in self.parent.drop_zones:
            if drop_zone.winfo_manager() == "place":
                drop_zone.place_forget()

        self.removePlayer(self, player_name, self.position)

class SubstitutePlayer(ctk.CTkFrame):
    def __init__(self, parent, fgColor, height, width, player, parentTab, comp_id, row, column, caStars, checkBoxFunction = None, unavailable = False, ingame = False, ingameFunction = None):
        """
        Frame representing a substitute player with various attributes and functionalities, found in the tactics tab and for in-game substitutions.
        
        Args:
            parent (ctk.CTkFrame): The parent frame.
            fgColor (str): The foreground color of the frame.
            height (int): The height of the frame.
            width (int): The width of the frame.
            player (Player): The player object.
            parentTab (ctk.CTkFrame): The parent tab frame.
            comp_id (str): The competition ID.
            row (int): The grid row position.
            column (int): The grid column position.
            caStars (float): Current ability stars of the player.
            checkBoxFunction (function, optional): Function to call when checkbox is toggled. Defaults to None.
            unavailable (bool, optional): Whether the player is unavailable. Defaults to False.
            ingame (bool, optional): Whether the player is being used for in-game substitutions. Defaults to False.
            ingameFunction (function, optional): Function to call for in-game substitutions. Defaults to None.
        """

        super().__init__(parent, fg_color = fgColor, width = width, height = height, corner_radius = 0)
        self.grid(row = row, column = column, padx = 5, pady = 5)
        self.fgColor = fgColor

        self.player = player
        self.playerBanned = PlayerBans.check_bans_for_player(self.player.id, comp_id) # For greying out a name when choosing a lineup
        self.unavailable = unavailable # For greying out a name when making in-game substitutions (injury/red card)

        textColor = "white"
        if self.playerBanned:
            textColor = GREY
        if self.unavailable:
            textColor = PIE_RED

        positions = self.player.specific_positions.replace(",", " ")
        self.positionLabel = ctk.CTkLabel(self, text = positions, font = (APP_FONT, 10), height = 10, fg_color = fgColor)
        self.positionLabel.place(relx = 0.05, rely = 0.2, anchor = "nw")

        self.caFrame = ctk.CTkFrame(self, fg_color = fgColor, width = 65, height = 15, corner_radius = 15)
        self.caFrame.place(relx = 0.03, rely = 0.05, anchor = "nw")

        imageNames = star_images(caStars)

        for i, imageName in enumerate(imageNames):
            src = Image.open(f"Images/{imageName}.png")
            src.thumbnail((12, 12))
            img = ctk.CTkImage(src, None, (src.width, src.height))
            ctk.CTkLabel(self.caFrame, image = img, text = "").place(relx = 0.1 + i * 0.2, rely = 0.3, anchor = "center")

        self.firstName = ctk.CTkLabel(self, text = self.player.first_name, font = (APP_FONT, 13), height = 10, fg_color = fgColor)
        self.firstName.place(relx = 0.5, rely = 0.46, anchor = "center")

        PlayerProfileLink(self, player, self.player.last_name, textColor, 0.5, 0.65, "center", fgColor, parentTab, 15, APP_FONT_BOLD, ingame = ingame, ingameFunction = ingameFunction)

        fitness = self.player.fitness
        if fitness > 75:
            src = "Images/fitness_good.png"
        elif fitness > 25:
            src = "Images/fitness_ok.png"
        else:
            src = "Images/fitness_bad.png"

        image = Image.open(src)
        image.thumbnail((15, 15))
        ctk_image = ctk.CTkImage(image, None, (image.width, image.height))
        ctk.CTkLabel(self, image = ctk_image, text = "", fg_color = fgColor, height = 0, width = 0).place(relx = 0.95, rely = 0.05, anchor = "ne")

        sharpness = self.player.sharpness
        if sharpness > 75:
            src = "Images/sharpness_good.png"
        elif sharpness > 25:
            src = "Images/sharpness_ok.png"
        else:
            src = "Images/sharpness_bad.png"

        image = Image.open(src)
        image.thumbnail((15, 15))
        ctk_image = ctk.CTkImage(image, None, (image.width, image.height))
        ctk.CTkLabel(self, image = ctk_image, text = "", fg_color = fgColor, height = 0, width = 0).place(relx = 0.95, rely = 0.23, anchor = "ne")

        if checkBoxFunction is not None:
            self.checkBox = ctk.CTkCheckBox(self, text = "", fg_color = GREY, checkbox_height = 10, checkbox_width = 80, border_width = 1, border_color = GREY)
            self.checkBox.configure(command = lambda: checkBoxFunction(self.checkBox, player))

    def showCheckBox(self):
        """
        Shows the checkbox for selecting the player, unless the player is banned.
        """

        if self.playerBanned:
            return

        self.checkBox.place(relx = 0.6, rely = 1, anchor = "s")
        self.checkBox.configure(state = "normal")

    def hideCheckBox(self):
        """
        Hides the checkbox for selecting the player.
        """
        
        self.checkBox.place_forget()
    
    def disableCheckBox(self):
        """
        Disables the checkbox for selecting the player.
        """
        
        self.checkBox.configure(state = "disabled")

    def enableCheckBox(self):
        """
        Enables the checkbox for selecting the player.
        """
        
        self.checkBox.configure(state = "normal")

    def uncheckCheckBox(self):
        """
        Unchecks the checkbox for selecting the player.
        """
        
        self.checkBox.deselect()

    def showBorder(self):
        """
        Shows a red border around the player frame.
        """
        
        self.configure(border_color = PIE_RED, border_width = 2)

class MatchDayMatchFrame(ctk.CTkFrame):
    def __init__(self, parent, match, fgColor, height, width, imageSize = 40, relx = 0, rely = 0, anchor = "nw", border_width = None, border_color = None, pack = True):
        """
        Frame representing a match in-game (frames on the right when playing a game), found in-game.

        Args:
            parent (ctk.CTkFrame): The parent frame.
            match (Match): The match object.
            fgColor (str): The foreground color of the frame.
            height (int): The height of the frame.
            width (int): The width of the frame.
            imageSize (int, optional): The size of the team logos. Defaults to 40.
            relx (float, optional): The relative x position for placing the frame. Defaults to 0.
            rely (float, optional): The relative y position for placing the frame. Defaults to 0.
            anchor (str, optional): The anchor position for placing the frame. Defaults to "nw".
            border_width (int, optional): The border width of the frame. Defaults to None.
            border_color (str, optional): The border color of the frame. Defaults to None.
            pack (bool, optional): Whether to pack the frame or place it. Defaults to True.
        """

        super().__init__(parent, fg_color = fgColor, width = width, height = height, border_width = border_width, border_color = border_color)
        
        self.match = match
        self.fgColor = fgColor
        self.imageSize = imageSize
        self.relx = relx
        self.rely = rely
        self.anchor = anchor
        self.packFrame = pack

        self.score = "0 - 0"

        currDate = Game.get_game_date(Managers.get_all_user_managers()[0].id)
        self.played = Matches.check_game_played(match, currDate)

        if currDate + timedelta(hours = 2) < match.date:
            self.laterGame = True
        else:
            self.laterGame = False

        # Create match instance only if the match is not played and not a later game
        if not self.played and not self.laterGame:
            self.matchInstance = Match(self.match, teamMatch = not self.packFrame)
        else:
            self.matchInstance = None

        self.addFrame()

    def addFrame(self):
        """
        Adds the match frame with team logos, names, and score or time.
        """
        
        if self.packFrame: 
            # smaller frames on the side
            self.pack(expand = True, fill = "both", pady = (0, 3))
            scoreSize = 23
            teamNameSize1 = 10
            teamNameSize2 = 13
            teamNamePlaceY1 = 0.3
            teamNamePlaceY2 = 0.7
        else:
            # large frame for team match
            self.place(relx = self.relx, rely = self.rely, anchor = self.anchor)
            scoreSize = 30
            teamNameSize1 = 15
            teamNameSize2 = 18
            teamNamePlaceY1 = 0.4
            teamNamePlaceY2 = 0.6

        self.homeTeam = Teams.get_team_by_id(self.match.home_id)
        ctk.CTkLabel(self, text = self.homeTeam.name.split(" ")[0], font = (APP_FONT, teamNameSize1), fg_color = self.fgColor).place(relx = 0.12, rely = teamNamePlaceY1, anchor = "center")
        ctk.CTkLabel(self, text = self.homeTeam.name.split(" ")[1], font = (APP_FONT_BOLD, teamNameSize2), fg_color = self.fgColor).place(relx = 0.12, rely = teamNamePlaceY2, anchor = "center")

        srcHome = Image.open(io.BytesIO(self.homeTeam.logo))
        srcHome.thumbnail((self.imageSize, self.imageSize))
        homeLogo = ctk.CTkImage(srcHome, None, (srcHome.width, srcHome.height))
        ctk.CTkLabel(self, image = homeLogo, text = "", fg_color = self.fgColor).place(relx = 0.3, rely = 0.5, anchor = "center")

        self.awayTeam = Teams.get_team_by_id(self.match.away_id)
        ctk.CTkLabel(self, text = self.awayTeam.name.split(" ")[0], font = (APP_FONT, teamNameSize1), fg_color = self.fgColor).place(relx = 0.88, rely = teamNamePlaceY1, anchor = "center")
        ctk.CTkLabel(self, text = self.awayTeam.name.split(" ")[1], font = (APP_FONT_BOLD, teamNameSize2), fg_color = self.fgColor).place(relx = 0.88, rely = teamNamePlaceY2, anchor = "center")

        srcAway = Image.open(io.BytesIO(self.awayTeam.logo))
        srcAway.thumbnail((self.imageSize, self.imageSize))
        awayLogo = ctk.CTkImage(srcAway, None, (srcAway.width, srcAway.height))
        ctk.CTkLabel(self, image = awayLogo, text = "", fg_color = self.fgColor).place(relx = 0.7, rely = 0.5, anchor = "center")

        if not self.played and not self.laterGame:
            self.scoreLabel = ctk.CTkLabel(self, text = f"0 - 0", font = (APP_FONT_BOLD, scoreSize), fg_color = self.fgColor)
        elif self.played:
            self.scoreLabel = ctk.CTkLabel(self, text = f"{self.match.score_home} - {self.match.score_away}", font = (APP_FONT_BOLD, scoreSize), fg_color = self.fgColor)
        else:
            day, text, time = format_datetime_split(self.match.date)
            self.scoreLabel = ctk.CTkLabel(self, text = time, font = (APP_FONT_BOLD, scoreSize), fg_color = self.fgColor)
            dateLabel = ctk.CTkLabel(self, text = f"{day[:3]} {text.split(" ")[0]}", font = (APP_FONT, 10), fg_color = self.fgColor, height = 0)
            dateLabel.place(relx = 0.5, rely = 0.8, anchor = "center")

        self.scoreLabel.place(relx = 0.5, rely = 0.5, anchor = "center")

        if self.packFrame:
            self.halfTimeLabel = ctk.CTkLabel(self, text = "HT", font = (APP_FONT, 10), fg_color = self.fgColor)
            self.fullTimeLabel = ctk.CTkLabel(self, text = "FT", font = (APP_FONT, 10), fg_color = self.fgColor)

            if not self.played and not self.laterGame:
                self.liveLabel = ctk.CTkLabel(self, text = "LIVE", font = (APP_FONT, 10), fg_color = self.fgColor)
                self.liveLabel.place(relx = 0.5, rely = 0.8, anchor = "center")

            self.labelY = 0.8
        else:
            self.halfTimeLabel = ctk.CTkLabel(self, text = "HT", font = (APP_FONT, 20), fg_color = self.fgColor)
            self.fullTimeLabel = ctk.CTkLabel(self, text = "FT", font = (APP_FONT, 20), fg_color = self.fgColor)
            self.labelY = 0.7

        if self.played:
            self.FTLabel(place = True)

    def HTLabel(self, place = True):
        """
        Places or removes the half-time label on the match frame.

        Args:
            place (bool): Whether to place or remove the label.
        """
        
        if place:
            self.halfTimeLabel.place(relx = 0.5, rely = self.labelY, anchor = "center")

            if hasattr(self, "liveLabel"):
                self.liveLabel.place_forget()
        else:
            self.halfTimeLabel.place_forget()

            if hasattr(self, "liveLabel"):
                self.liveLabel.place(relx = 0.5, rely = self.labelY, anchor = "center")
    
    def FTLabel(self, place = True):
        """
        Places or removes the full-time label on the match frame.

        Args:
            place (bool): Whether to place or remove the label.
        """
        
        if place:
            self.fullTimeLabel.place(relx = 0.5, rely = self.labelY, anchor = "center")

            if hasattr(self, "liveLabel"):
                self.liveLabel.place_forget()
        else:
            self.fullTimeLabel.place_forget()

            if hasattr(self, "liveLabel"):
                self.liveLabel.place(relx = 0.5, rely = self.labelY, anchor = "center")

    def updateScoreLabel(self, home = True, textAdd = None):
        """
        Updates the score label on the match frame.

        Args:
            home (bool): Whether to update the home team's score. Defaults to True.
            textAdd (str, optional): Custom score text to set. Defaults to None.
        """
        
        if home:
            if textAdd:
                text = textAdd
            else:
                homeGoals = int(self.scoreLabel.cget("text").split(" - ")[0]) + 1
                awayGoals = int(self.scoreLabel.cget("text").split(" - ")[1])

                text = f"{homeGoals} - {awayGoals}"
                self.score = text
        else:
            if textAdd:
                text = textAdd
            else:
                awayGoals = int(self.scoreLabel.cget("text").split(" - ")[1]) + 1
                homeGoals = int(self.scoreLabel.cget("text").split(" - ")[0])

                text = f"{homeGoals} - {awayGoals}"
                self.score = text

        self.scoreLabel.configure(text = text)

    def getCurrentScore(self):
        """
        Returns the current score as a list of [homeGoals, awayGoals].
        """
        
        return self.scoreLabel.cget("text").split(" - ")

class FormGraph(ctk.CTkCanvas):
    def __init__(self, frame, player, width, height, relx, rely, anchor, fgColor):
        """
        Form graph canvas showing the last 5 match ratings of a player, found in player profiles and in-game substitute data

        Args:
            frame (ctk.CTkFrame): The parent frame.
            player (Player): The player object.
            width (int): The width of the canvas.
            height (int): The height of the canvas.
            relx (float): The relative x position for placing the canvas.
            rely (float): The relative y position for placing the canvas.
            anchor (str): The anchor position for placing the canvas.
            fgColor (str): The foreground color of the canvas.
        """

        super().__init__(frame, width = width, height = height, bg = fgColor, bd = 0, highlightthickness = 0)
        self.place(relx = relx, rely = rely, anchor = anchor)

        self.player = player
        self.fgColor = fgColor
        self.width = width
        self.height = height

        self.last5Events = []

        self.leagueTeams = LeagueTeams.get_league_by_team(self.player.team_id)
        self.last5 = Matches.get_team_last_5_matches(self.player.team_id, Game.get_game_date(Managers.get_all_user_managers()[0].id))

        self.draw_axes()

        self.last5Events = []
        
        self.draw_bars()

    def draw_axes(self):
        """
        Draws the axes for the form graph.
        """
        
        # Vertical axis line (left border of canvas)
        self.create_line(0, 0, 0, self.height - 30, fill = "black", width = 8)
        
        # Horizontal axis line (moved up to leave space for text below)
        self.create_line(0, self.height - 30, self.width, self.height - 30, fill = "black", width = 4)

    def draw_bars(self):
        """
        Draws the bars representing the player's ratings in the last 5 matches.
        """
        
        bar_width = self.width / 5  # Canvas width divided by 5 bars
        max_bar_height = self.height - 50  # Leave space for axes and text
        
        # Check if player played in any of the 5 matches and collect ratings
        played_any = False
        self.ratings = []
        for match in reversed(self.last5):
            lineup = TeamLineup.get_lineup_by_match(match.id)
            playerIDs = [player.player_id for player in lineup]
            if self.player.id in playerIDs:
                played_any = True
                playerLineupData = [player for player in lineup if player.player_id == self.player.id][0]
                self.ratings.append(playerLineupData.rating)
        
        # If player didn't play in any match, show "No data" message
        if not played_any:
            self.create_text(self.width / 2, self.height / 2 - 20, text = "No data", fill = "white", font = ("Arial Bold", 25))
            return
        
        # Find maximum rating to scale the chart
        max_rating = max(self.ratings)
        # Ensure minimum scale of 5 for better visibility
        scale_max = max(max_rating + 1, 5)

        for i, match in enumerate(reversed(self.last5)):
            lineup = TeamLineup.get_lineup_by_match(match.id)
            playerIDs = [player.player_id for player in lineup]
            self.last5Events.append(MatchEvents.get_events_by_match_and_player(match.id, self.player.id))
            
            # Calculate bar position
            bar_x = i * bar_width + bar_width / 2
            
            if self.player.id not in playerIDs:
                self.create_text(bar_x, self.height - 15, text = f"0'", fill = "white", font = ("Arial", 10))
                continue

            # Get player data
            playerLineupData = [player for player in lineup if player.player_id == self.player.id][0]
            rating = playerLineupData.rating

            timePlayed = MatchEvents.get_player_game_time(self.player.id, match.id)

            # Determine bar color based on rating
            if rating >= 7:
                bar_color = PIE_GREEN
            elif rating >= 5:
                bar_color = NEUTRAL_COLOR
            else:
                bar_color = PIE_RED

            # Calculate bar height using dynamic scale
            bar_height = (rating / scale_max) * max_bar_height
            
            # Draw the bar without outline
            bar_left = bar_x - bar_width / 4  # Make bars a bit thinner than full width
            bar_right = bar_x + bar_width / 4
            bar_top = self.height - 32 - bar_height
            bar_bottom = self.height - 32
            
            bar_rect = self.create_rectangle(bar_left, bar_top, bar_right, bar_bottom, fill = bar_color, outline = "")
            
            # Create rating text but don't show it initially
            rating_text = self.create_text(bar_x, bar_top - 10, text = f"{rating:.2f}", fill = "white", font = ("Arial", 10), state = "hidden")
            
            # Bind mouse events to show/hide rating on hover
            self.tag_bind(bar_rect, "<Enter>", lambda event, text_id = rating_text: self.itemconfig(text_id, state = "normal"))
            self.tag_bind(bar_rect, "<Leave>", lambda event, text_id = rating_text: self.itemconfig(text_id, state = "hidden"))
            
            # Add minutes played text below the axis
            self.create_text(bar_x, self.height - 15, text = f"{timePlayed}'", fill = "white", font = ("Arial", 10))

class PlayerMatchFrame(ctk.CTkFrame):
    def __init__(self, parent, game, player, width, height, fgColor, parentTab):
        """
        Frame representing a match played, found in player profiles.
        
        Args:
            parent (ctk.CTkFrame): The parent frame.
            game (Match): The match object.
            player (Player): The player object.
            width (int): The width of the frame.
            height (int): The height of the frame.
            fgColor (str): The foreground color of the frame.
            parentTab (ctk.CTkFrame): The parent tab frame.
        """

        super().__init__(parent, fg_color = fgColor, width = width, height = height, corner_radius = 10)
        self.pack(expand = True, fill = "both", pady = 10)

        self.game = game
        self.player = player
        self.fgColor = fgColor
        self.parentTab = parentTab

        oppositionID = self.game.home_id if self.player.team_id != self.game.home_id else self.game.away_id
        home = "(H)" if self.player.team_id == self.game.home_id else "(A)"
        opposition = Teams.get_team_by_id(oppositionID)
        self.rating = TeamLineup.get_player_rating(self.player.id, self.game.id)
        potm = TeamLineup.get_player_OTM(self.game.id)
        events = MatchEvents.get_events_by_match_and_player(self.game.id, self.player.id)

        src = Image.open(io.BytesIO(opposition.logo))
        src.thumbnail((65, 65))
        self.logo = TeamLogo(self, src, opposition, self.fgColor, 0.05, 0.5, "center", self.parentTab)

        self.oppName = ctk.CTkLabel(self, text = f"{opposition.name} {home}", font = (APP_FONT_BOLD, 18), fg_color = self.fgColor).place(relx = 0.1, rely = 0.35, anchor = "w")
        self.score = ctk.CTkLabel(self, text = f"{self.game.score_home} - {self.game.score_away}", font = (APP_FONT, 15), fg_color = self.fgColor, height = 10).place(relx = 0.1, rely = 0.65, anchor = "w")

        self.league = League.get_league_by_id(self.game.league_id)
        self.compName = ctk.CTkLabel(self, text = f"{self.league.name} - Matchday {self.game.matchday}", font = (APP_FONT, 15), fg_color = DARK_GREY, corner_radius = 10).place(relx = 0.97, rely = 0.25, anchor = "e")

        ratingBG = PIE_RED
        if self.rating >= 7:
            ratingBG = PIE_GREEN
        elif self.rating >= 5:
            ratingBG = NEUTRAL_COLOR

        if self.player.id == potm.player_id:
            ratingBG = POTM_BLUE

        if "." not in str(self.rating):
            self.rating = f"{self.rating}.0"

        self.ratingLabel = ctk.CTkLabel(self, text = self.rating, font = (APP_FONT_BOLD, 15), fg_color = ratingBG, height = 30, width = 50, corner_radius = 10).place(relx = 0.97, rely = 0.7, anchor = "e")

        eventsToShow = {}

        for event in events:
            if event.event_type == "goal" or event.event_type == "penalty_goal":
                if "goal" not in eventsToShow:
                    eventsToShow["goal"] = 0
                eventsToShow["goal"] += 1
            elif event.event_type == "yellow_card":
                if "yellow_card" not in eventsToShow:
                    eventsToShow["yellow_card"] = 0
                eventsToShow["yellow_card"] += 1
            elif event.event_type == "red_card":
                if "red_card" not in eventsToShow:
                    eventsToShow["red_card"] = 0
                eventsToShow["red_card"] += 1
            elif event.event_type == "assist":
                if "assist" not in eventsToShow:
                    eventsToShow["assist"] = 0
                eventsToShow["assist"] += 1
            elif event.event_type == "own_goal":
                if "own_goal" not in eventsToShow:
                    eventsToShow["own_goal"] = 0
                eventsToShow["own_goal"] += 1
            elif event.event_type == "penalty_saved":
                if "penalty_saved" not in eventsToShow:
                    eventsToShow["penalty_saved"] = 0
                eventsToShow["penalty_saved"] += 1
            elif event.event_type == "penalty_miss":
                if "penalty_miss" not in eventsToShow:
                    eventsToShow["penalty_miss"] = 0
                eventsToShow["penalty_miss"] += 1

        self.gameTime = MatchEvents.get_player_game_time(self.player.id, self.game.id)
        self.gameTimeLabel = ctk.CTkLabel(self, text = f"{self.gameTime}'", font = (APP_FONT_BOLD, 15), fg_color = DARK_GREY, height = 32, width = 50, corner_radius = 10).place(relx = 0.91, rely = 0.7, anchor = "e")

        startRelx = 0.83  # Starting position moved more to the right
        overlay = 0.03  # Amount of overlap between icons
        overallCount = 0
        for eventType, count in eventsToShow.items():
            match eventType:
                case "goal":
                    src = Image.open("Images/goal.png")
                case "yellow_card":
                    src = Image.open("Images/yellowCard.png")
                case "red_card":
                    src = Image.open("Images/redCard.png")
                case "assist":
                    src = Image.open("Images/assist.png")
                case "own_goal":
                    src = Image.open("Images/ownGoal.png")
                case "penalty_saved":
                    src = Image.open("Images/saved_penalty.png")
                case "penalty_miss":
                    src = Image.open("Images/missed_penalty.png")

            for _ in range(count):
                src.thumbnail((25, 25))
                image = ctk.CTkImage(src, None, (src.width, src.height))
                ctk.CTkLabel(self, image = image, text = "", fg_color = self.fgColor).place(relx = startRelx - (overallCount * overlay), rely = 0.7, anchor = "e")

                overallCount += 1

        self.bind("<Enter>", lambda e: self.onHover())
        self.bind("<Leave>", lambda e: self.onLeave())

        self.bind("<Button-1>", lambda e: self.onClick())

        for widget in self.winfo_children():
            widget.bind("<Enter>", lambda e: self.onHover())
            if isinstance(widget, ctk.CTkLabel) and hasattr(widget, '_image') and isinstance(widget._image, TeamLogo):
                continue
            widget.bind("<Button-1>", lambda e: self.onClick())

    def onHover(self):
        """
        Changes the frame and its child widgets' colors on hover.
        """
        
        self.configure(fg_color = GREY_BACKGROUND)

        for widget in self.winfo_children():
            if isinstance(widget, ctk.CTkLabel) and widget.cget("text") != self.rating and widget.cget("text") != f"{self.gameTime}'" and widget.cget("text") != f"{self.league.name} - Matchday {self.game.matchday}":
                widget.configure(fg_color = GREY_BACKGROUND)

    def onLeave(self):
        """
        Resets the frame and its child widgets' colors when not hovered.
        """
        
        self.configure(fg_color = self.fgColor)

        for widget in self.winfo_children():
            if isinstance(widget, ctk.CTkLabel) and widget.cget("text") != self.rating and widget.cget("text") != f"{self.gameTime}'" and widget.cget("text") != f"{self.league.name} - Matchday {self.game.matchday}":
                widget.configure(fg_color = self.fgColor)

    def onClick(self):
        """
        Opens the player's profile when the frame is clicked.
        """
        
        from tabs.matchProfile import MatchProfile

        self.profile = MatchProfile(self.parentTab, self.game, self.parentTab, changeBackFunction = self.changeBack)
        self.profile.place(x = 0, y = 0, anchor = "nw")
        from utils.util_functions import append_overlapping_profile
        append_overlapping_profile(self.parentTab, self.profile)

    def changeBack(self):
        """
        Closes the player's profile.
        """
        
        self.profile.place_forget()

class InGamePlayerFrame(ctk.CTkFrame):
    def __init__(self, parent, playerID, width, height, fgColor):
        """
        Frame representing a player in-game with their fitness, found in-game, with the players data option.
        
        Args:
            parent (ctk.CTkFrame): The parent frame.
            playerID (str): The ID of the player.
            width (int): The width of the frame.
            height (int): The height of the frame.
            fgColor (str): The foreground color of the frame.
        """

        super().__init__(parent, fg_color = fgColor, width = width, height = height)
        self.pack(pady = 5, padx = 2)

        self.playerID = playerID

        self.player = Players.get_player_by_id(self.playerID)

        fitness = self.player.fitness

        if fitness > 75:
            src = "Images/fitness_good.png"
        elif fitness > 25:
            src = "Images/fitness_ok.png"
        else:
            src = "Images/fitness_bad.png"

        image = Image.open(src)
        image.thumbnail((20, 20))
        ctk_image = ctk.CTkImage(image, None, (image.width, image.height))

        self.nameLabel = ctk.CTkLabel(self, text = f"{self.player.first_name} {self.player.last_name}", font = (APP_FONT, 12), fg_color = fgColor, height = 0, text_color = "white")
        self.nameLabel.place(relx = 0.05, rely = 0.5, anchor = "w")

        self.fitnessImage = ctk.CTkLabel(self, text = "", image = ctk_image)
        self.fitnessImage.place(relx = 0.95, rely = 0.5, anchor = "e")
        self.fitnessLabel = ctk.CTkLabel(self, text = f"{fitness}%", font = (APP_FONT, 12), fg_color = fgColor, height = 0)
        self.fitnessLabel.place(relx = 0.8, rely = 0.5, anchor = "e")

    def updateFitness(self, fitness):
        """
        Updates the player's fitness display.

        Args:
            fitness (int): The new fitness value.     
        """

        self.fitnessLabel.configure(text = f"{round(fitness)}%")

        if fitness > 75:
            src = "Images/fitness_good.png"
        elif fitness > 25:
            src = "Images/fitness_ok.png"
        else:
            src = "Images/fitness_bad.png"

        image = Image.open(src)
        image.thumbnail((20, 20))
        ctk_image = ctk.CTkImage(image, None, (image.width, image.height))
        self.fitnessImage.configure(image = ctk_image)

    def removeFitness(self):
        """
        Removes the fitness display, used when the player is injured or suspended.
        """
        
        try:
            self.fitnessImage.destroy()
            self.fitnessLabel.destroy()
        except:
            # Silence any exceptions (Tkinter sometimes will throw errors when removing the images)
            pass

        self.nameLabel.configure(text_color = GREY)

class InGameStatFrame(ctk.CTkFrame):
    def __init__(self, parent, statName, width, height, fgColor):
        """
        Frame representing a statistic in-game, found in-game, with the stats data option.

        Args:
            parent (ctk.CTkFrame): The parent frame.
            statName (str): The name of the statistic.
            width (int): The width of the frame.
            height (int): The height of the frame.
            fgColor (str): The foreground color of the frame.
        """
        
        super().__init__(parent, fg_color = fgColor, width = width, height = height)
        self.pack(pady = 5, padx = 2)

        self.statName = statName
        self.statValue = 0
        self.fgColor = fgColor

        ctk.CTkLabel(self, text = self.statName, font = (APP_FONT, 12), fg_color = fgColor, height = height, text_color = "white", width = 0).place(relx = 0.05, rely = 0.5, anchor = "w")

        pill_height = 24
        self.valueLabel = ctk.CTkLabel(
            self,
            text = f"{self.statValue}",
            font = (APP_FONT, 12),
            fg_color = self.fgColor,
            text_color = "white",
            height = pill_height,
            corner_radius = pill_height // 2,
            padx = 8
        )
        self.valueLabel.place(relx = 0.8, rely = 0.5, anchor = "center")

    def updateValue(self, value, color):
        """
        Updates the statistic value display.
        
        Args:
            value (int): The new statistic value.
            color (bool): Whether to change the color of the value display.
        """
        
        self.statValue = value
        self.valueLabel.configure(text = f"{self.statValue}")

        if color:
            self.valueLabel.configure(fg_color = "white", text_color = "black")
        else:
            self.valueLabel.configure(fg_color = self.fgColor, text_color = "white")
class ChoosingLeagueFrame(ctk.CTkFrame):
    def __init__(self, parent, fgColor, width, height, corner_radius, border_width, border_color, endFunction, settings = False):
        """
        Frame for choosing leagues to load, found in new game setup and the settings tab.
        
        Args:
            parent (ctk.CTkFrame): The parent frame.
            fgColor (str): The foreground color of the frame.
            width (int): The width of the frame.
            height (int): The height of the frame.
            corner_radius (int): The corner radius of the frame.
            border_width (int): The border width of the frame.
            border_color (str): The border color of the frame.
            endFunction (function): The function to call when finishing league selection.
            settings (bool, optional): Whether this is in settings mode. Defaults to False.
        """

        super().__init__(parent, fg_color = fgColor, width = width, height = height, corner_radius = corner_radius, border_width = border_width, border_color = border_color)

        self.parent = parent
        self.endFunction = endFunction
        self.settings = settings
        self.loadedLeagues = {}
        self.unCheckable = []

        if self.settings:
            mng = Managers.get_all_user_managers()[0]
            team = Teams.get_teams_by_manager(mng.id)[0]
            league = LeagueTeams.get_league_by_team(team.id)
            leagueObj = League.get_league_by_id(league.league_id)

            self.unCheckable = [leagueObj.name]

            while leagueObj.league_above:
                leagueObj = League.get_league_by_id(leagueObj.league_above)
                self.unCheckable.append(leagueObj.name)

        self.selectLeagues()

    def selectLeagues(self):
        """
        Sets up the league selection interface with checkboxes for each league.
        """

        if not self.settings:
            try:
                with open("data/leagues.json", "r") as file:
                    self.leaguesJson = json.load(file)
            except FileNotFoundError:
                self.leaguesJson = {}

            if len(self.loadedLeagues) == 0:
                for league in self.leaguesJson:
                    if not league["league_above"]:
                        self.loadedLeagues[league["name"]] = 1
                    else:
                        self.loadedLeagues[league["name"]] = 0
        else:
            leagues = League.get_all_leagues()
            self.leaguesJson = []
            for league in leagues:
                self.loadedLeagues[league.name] = 1 if league.to_be_loaded else 0
                self.leaguesJson.append({
                    "name": league.name,
                })

        ctk.CTkLabel(self, text = "Choose leagues", font = (APP_FONT_BOLD, 35), bg_color = TKINTER_BACKGROUND).place(relx = 0.03, rely = 0.1, anchor = "w")
        ctk.CTkLabel(self, text = "Any league you do not choose will be unplayable and unsimulated. You can only change the loaded leagues at every new season. Load less leagues for better game performance.", font = (APP_FONT, 13.5), bg_color = TKINTER_BACKGROUND).place(relx = 0.012, rely = 0.93, anchor = "w")

        if not self.settings:
            okText = "Teams >"
            backText = "< Manager"
        else:
            okText = "OK"
            backText = "< Settings"

        self.doneLeaguesbutton = ctk.CTkButton(self, text = okText, font = (APP_FONT, 15), fg_color = GREY_BACKGROUND, corner_radius = 10, width = 150, height = 45, command = lambda: self.finishLeagues())
        self.doneLeaguesbutton.place(relx = 0.97, rely = 0.05, anchor = "ne")

        backButton = ctk.CTkButton(self, text = backText, font = (APP_FONT, 15), fg_color = GREY_BACKGROUND, corner_radius = 10, width = 150, height = 45, hover_color = CLOSE_RED, command = lambda: self.place_forget())
        backButton.place(relx = 0.82, rely = 0.05, anchor = "ne")

        leagueFrameWidth = 135
        leagueFrameHeight = 400
        gap = leagueFrameWidth / 1150 + 0.005

        # Create the league selection frame for each planet
        for i, planetName in enumerate(PLANETS):
            frame = ctk.CTkFrame(self, fg_color = GREY_BACKGROUND, height = leagueFrameHeight, width = leagueFrameWidth, corner_radius = 10)
            frame.place(relx = 0.012 + gap * i, rely = 0.2, anchor = "nw")
            frame.checkBoxes = {}

            ctk.CTkLabel(frame, text = planetName, font = (APP_FONT_BOLD, 15), bg_color = GREY_BACKGROUND).place(relx = 0.5, rely = 0.02, anchor = "n")

            leagues = self.leaguesJson[(i * 4):(i * 4) + 4]
            gap2 = 0.08
            for j, league in enumerate(leagues):
                leagueCheck = ctk.CTkCheckBox(frame, text = "", fg_color = GREY_BACKGROUND, checkbox_height = 20, checkbox_width = 20, border_width = 1, border_color = "white", corner_radius = 0)
                leagueCheck.place(relx = 0.05, rely = 0.15 + gap2 * j, anchor = "w")
                frame.checkBoxes[league["name"]] = leagueCheck

                leagueCheck.configure(command = lambda f = frame, c = leagueCheck, n = league["name"]: self.checkLeague(f, c, n))

                if self.loadedLeagues[league["name"]] == 1:
                    leagueCheck.select()
                
                if league["name"] in self.unCheckable:
                    leagueCheck.configure(state = "disabled")

                ctk.CTkLabel(frame, text = league["name"], font = (APP_FONT, 11), bg_color = GREY_BACKGROUND).place(relx = 0.25, rely = 0.15 + gap2 * j, anchor = "w")

            ctk.CTkLabel(frame, text = PLANET_DESCRIPTIONS[planetName], font = (APP_FONT, 12), bg_color = GREY_BACKGROUND).place(relx = 0.5, rely = 0.45, anchor = "n")


    def checkLeague(self, frame, checkbox, leagueName):
        """
        Handles the logic for checking and unchecking leagues, ensuring hierarchical selection.

        Args:
            frame (ctk.CTkFrame): The frame containing the league checkboxes.
            checkbox (ctk.CTkCheckBox): The checkbox that was checked or unchecked.
            leagueName (str): The name of the league associated with the checkbox.
        """

        if checkbox.get() == 0:
            # unchecking
            self.loadedLeagues[leagueName] = 0

            below = False
            for name, cb in frame.checkBoxes.items():
                
                if below:
                    cb.deselect()
                    self.loadedLeagues[name] = 0
                
                if name == leagueName:
                    below = True

        else:
            # checking 
            self.loadedLeagues[leagueName] = 1

            above = True
            for name, cb in frame.checkBoxes.items():
                
                if above:
                    cb.select()
                    self.loadedLeagues[name] = 1
                
                if name == leagueName:
                    above = False

    def finishLeagues(self):
        """
        Finalizes the league selection and calls the end function.
        """
    
        if 1 not in self.loadedLeagues.values():
            CTkMessagebox(title = "Error", message = "Please select at least one league to load", icon = "cancel")
            return
        else:
            self.endFunction()

class News(ctk.CTkFrame):
    def __init__(self, parent, league_id = None, team_id = None):
        """
        Class for displaying news in the league profile or the teams profile.

        Args:
            parent (ctk.CTkFrame): The parent frame.
            league_id (str, optional): The ID of the league. Defaults to None.
            team_id (str, optional): The ID of the team. Defaults to None.
        """
        
        super().__init__(parent, fg_color = TKINTER_BACKGROUND, width = 1000, height = 630, corner_radius = 0)  

        self.parent = parent
        self.league_id = league_id
        self.team_id = team_id
        self.hovering = False

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
        Populates the main news frame with league news using a Canvas.
        """

        canvasSize = 770
        src = Image.open("Images/news_backdrop.png")
        src = src.resize((canvasSize, canvasSize))

        if src.mode != "RGBA":
            src = src.convert("RGBA")

        rounded = Image.new("RGBA", src.size, TKINTER_BACKGROUND)  # fill the new image with background color
        mask = Image.new("L", src.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle((0, 0, src.width, src.height), 25, fill = 255)

        # Paste transparent src where the mask allows it
        rounded.paste(src, (0, 0), mask)

        # Create a canvas inside mainNewsFrame
        self.canvas = tk.Canvas(self.mainNewsFrame, width = canvasSize, height = canvasSize, highlightthickness = 0, bg = TKINTER_BACKGROUND)
        self.canvas.place(relx = 0.5, rely = 0.5, anchor = "center")

        # Draw the background image
        photo = ImageTk.PhotoImage(rounded)
        self.image = self.canvas.create_image(0, 0, anchor = "nw", image = photo)
        self.canvas.image = photo  # keep a reference

        # Get news
        if self.league_id:
            self.news = LeagueNews.get_news_for_league(self.league_id)
        else:
            self.news = LeagueNews.get_news_for_team(self.team_id)

        if not self.news:
            self.canvas.create_text(20, 730, anchor = "w", text = "No news available.", fill = "white", font = (APP_FONT_BOLD, 35))  
            return

        self.leftArrowButton = self.canvas.create_text(20, 740, anchor = "w", text = "<", fill = "white", font = (APP_FONT_BOLD, 25))
        self.rightArrowButton = self.canvas.create_text(750, 740, anchor = "e", text = ">", fill = "white", font = (APP_FONT_BOLD, 25))

        self.canvas.tag_bind(self.leftArrowButton, "<Button-1>", lambda e: self.moveTitle(-1))
        self.canvas.tag_bind(self.rightArrowButton, "<Button-1>", lambda e: self.moveTitle(1))

        self.canvas.bind("<Motion>", self.checkHover)
        self.canvas.bind("<Enter>", self.showNewsDetails)
        self.canvas.bind("<Leave>", self.removeNewsDetails)

        self.generateTitles()
        if len(self.newsTitles) == 0:
            self.canvas.create_text(20, 730, anchor = "w", text = "No news available.", fill = "white", font = (APP_FONT_BOLD, 35))  
            return

        fontSize = 30
        if len(self.newsTitles[0]) > 40:
            fontSize = 20
        elif len(self.newsTitles[0]) > 35:
            fontSize = 25 
        
        self.currentNews = 0
        self.titleText = self.canvas.create_text(20, 680, anchor = "w", text = self.newsTitles[0], fill = "white", font = (APP_FONT_BOLD, fontSize))
        self.title_coords = [20, 680]  # Track current coordinates of the title

        self.newsText = self.canvas.create_text(20, 800, anchor = "nw", text = self.newsDetails[0], fill = "white", font = (APP_FONT, 15))
        self.newsText_coords = [20, 800]  # Track current coordinates of the news text

        self.afterID = self.after(5000, lambda: self.moveTitle(1))

    def generateTitles(self):
        """
        Generates the news titles for each news item.
        """
        
        self.newsTitles = []
        self.newsDetails = []
        self.currentNewsInds = []

        numNews = len(self.news)

        # --- Layout constants ---
        canvas_width = 770
        y_pos = 740  # vertical position (same as before)
        indicator_radius = 6
        spacing = 30  # fixed horizontal distance between indicators

        total_width = (numNews - 1) * spacing
        start_x = (canvas_width - total_width) / 2

        for i, newsObj in enumerate(self.news):

            x_center = start_x + i * spacing
            oval = self.canvas.create_oval(
                x_center - indicator_radius, y_pos - indicator_radius,
                x_center + indicator_radius, y_pos + indicator_radius,
                fill="white" if i == 0 else "gray",
                outline=""
            )
            self.currentNewsInds.append(oval)

            match newsObj.news_type:
                case "milestone":
                    player = Players.get_player_by_id(newsObj.player_id)
                    last_name = player.last_name
                    position = player.position
                    team = Teams.get_team_by_id(player.team_id).name
                    competition = League.get_league_by_id(newsObj.league_id).name

                    match = Matches.get_match_by_id(newsObj.match_id)
                    if match.home_id == player.team_id:
                        opponentTeam = Teams.get_team_by_id(match.away_id).name
                    else:
                        opponentTeam = Teams.get_team_by_id(match.home_id).name

                    title = generate_news_title("milestone", player = last_name, value = newsObj.news_number, milestone_type = newsObj.milestone_type)
                    self.newsTitles.append(title)

                    detail = generate_news_detail("milestone", player = last_name, value = newsObj.news_number, milestone_type = newsObj.milestone_type, position = position, team = team, comp = competition, opponent = opponentTeam)
                    self.newsDetails.append(detail)
                case "big_score":
                    matchObj = Matches.get_match_by_id(newsObj.match_id)
                    homeTeam = Teams.get_team_by_id(matchObj.home_id)
                    awayTeam = Teams.get_team_by_id(matchObj.away_id)
                    events = MatchEvents.get_events_by_match(matchObj.id)

                    for event in events:
                        if event.event_type == "goal" or event.event_type == "penalty_goal":
                            player1 = Players.get_player_by_id(event.player_id).last_name

                    firstTeam = homeTeam.name
                    secondTeam = awayTeam.name

                    title = generate_news_title("big_score", team1 = firstTeam, team2 = secondTeam)
                    self.newsTitles.append(title)

                    detail = generate_news_detail("big_score", team1 = firstTeam, team2 = secondTeam, score = f"{matchObj.score_home}-{matchObj.score_away}", player1 = player1)
                    self.newsDetails.append(detail)
                case "big_win":
                    matchObj = Matches.get_match_by_id(newsObj.match_id)
                    homeTeam = Teams.get_team_by_id(matchObj.home_id)
                    awayTeam = Teams.get_team_by_id(matchObj.away_id)

                    if matchObj.score_home > matchObj.score_away:
                        winner = "home"
                        firstTeam = homeTeam
                        secondTeam = awayTeam
                    else:
                        winner = "away"
                        firstTeam = awayTeam
                        secondTeam = homeTeam

                    manager = Managers.get_manager_by_id(firstTeam.manager_id) if winner == "home" else Managers.get_manager_by_id(secondTeam.manager_id)
                    stadium = homeTeam.stadium if winner == "home" else awayTeam.stadium
                    potm = TeamLineup.get_player_OTM(matchObj.id)

                    title = generate_news_title("big_win", team1 = firstTeam.name, team2 = secondTeam.name, score = f"{matchObj.score_home}-{matchObj.score_away}")
                    self.newsTitles.append(title)

                    detail = generate_news_detail("big_win", team1 = firstTeam.name, team2 = secondTeam.name, score = f"{matchObj.score_home}-{matchObj.score_away}", manager = manager.last_name, stadium = stadium, potm = Players.get_player_by_id(potm.player_id).last_name)
                    self.newsDetails.append(detail)
                case "injury":
                    player = Players.get_player_by_id(newsObj.player_id)
                    injured = PlayerBans.get_player_injured(newsObj.player_id)

                    if not injured:
                        continue

                    bans = PlayerBans.get_bans_for_player(newsObj.player_id)
                    for ban in bans:
                        if ban.injury:
                            injuryLength = ban.injury - newsObj.date 

                    # turn injury length into months (round up)
                    injuryMonths = -(-injuryLength.days // 30)  # Ceiling division

                    title = generate_news_title(newsObj.news_type, player = player.last_name, months = injuryMonths)
                    self.newsTitles.append(title)

                    match = Matches.get_team_last_match(player.team_id, newsObj.date)
                    playerTeam = Teams.get_team_by_id(player.team_id)
                    teamName = playerTeam.name
                    manager = Managers.get_manager_by_id(playerTeam.manager_id)
                    opponentTeam = Teams.get_team_by_id(match.away_id if match.home_id == player.team_id else match.home_id).name
                    score = f"{match.score_home}-{match.score_away}"
                    competition = League.get_league_by_id(match.league_id).name

                    detail = generate_news_detail("injury", player = player.last_name, team = teamName, opponent = opponentTeam, score = score, competition = competition, months = injuryMonths, position = player.position, injury_type = "N/A", manager = manager.last_name)
                    self.newsDetails.append(detail)

                case "disciplinary":
                    matchObj = Matches.get_match_by_id(newsObj.match_id)
                    homeTeam = Teams.get_team_by_id(matchObj.home_id)
                    homeName = homeTeam.name
                    awayTeam = Teams.get_team_by_id(matchObj.away_id)
                    awayName = awayTeam.name
                    stadium = homeTeam.stadium
                    number = newsObj.news_number

                    events = MatchEvents.get_events_by_match(matchObj.id)
                    homeCount = 0
                    awayCount = 0
                    detailPlayer = None
                    for event in events:
                        if event.event_type == "yellow_card" or event.event_type == "red_card":
                            player = Players.get_player_by_id(event.player_id)

                            if not detailPlayer:
                                detailPlayer = player.last_name
                            
                            if player.team_id == homeTeam.id:
                                homeCount += 1
                            else:
                                awayCount += 1
                    
                    if homeCount > awayCount:
                        manager = Managers.get_manager_by_id(homeTeam.manager_id).last_name
                    else:
                        manager = Managers.get_manager_by_id(awayTeam.manager_id).last_name

                    title = generate_news_title(newsObj.news_type, number = newsObj.news_number, team = homeName)
                    self.newsTitles.append(title)   

                    detail = generate_news_detail("disciplinary", player = detailPlayer, team = homeName, opponent = awayName, score = f"{matchObj.score_home}-{matchObj.score_away}", stadium = stadium, number = number, manager = manager)
                    self.newsDetails.append(detail)
                case "lead_change":
                    team = Teams.get_team_by_id(newsObj.team_id)
                    match = Matches.get_match_by_id(newsObj.match_id)
                    opponentTeam = Teams.get_team_by_id(match.away_id if match.home_id == team.id else match.home_id).name

                    manager = Managers.get_manager_by_id(team.manager_id).last_name

                    title = generate_news_title("lead_change", team = team.name)
                    self.newsTitles.append(title)

                    detail = generate_news_detail("lead_change", team = team.name, opponent = opponentTeam, manager = manager)
                    self.newsDetails.append(detail)
                case "relegation_change":
                    team = Teams.get_team_by_id(newsObj.team_id)
                    match = Matches.get_match_by_id(newsObj.match_id)
                    opponentTeam = Teams.get_team_by_id(match.away_id if match.home_id == team.id else match.home_id).name

                    manager = Managers.get_manager_by_id(team.manager_id).last_name

                    title = generate_news_title("relegation_change", team = team.name)
                    self.newsTitles.append(title)

                    detail = generate_news_detail("relegation_change", team = team.name, opponent = opponentTeam, manager = manager)
                    self.newsDetails.append(detail)
                case "overthrow":
                    team = Teams.get_team_by_id(newsObj.team_id)
                    match = Matches.get_match_by_id(newsObj.match_id)
                    team2 = Teams.get_team_by_id(match.away_id if match.home_id == team.id else match.home_id).name
                    score = f"{match.score_home}-{match.score_away}"
                    manager = Managers.get_manager_by_id(team.manager_id).last_name

                    title = generate_news_title("overthrow", team1 = team.name, team2 = team2)
                    self.newsTitles.append(title)

                    detail = generate_news_detail("overthrow", team1 = team.name, team2 = team2, score = score, manager = manager)
                    self.newsDetails.append(detail)
                case "player_goals":
                    player = Players.get_player_by_id(newsObj.player_id)
                    team = Teams.get_team_by_id(player.team_id)
                    match = Matches.get_match_by_id(newsObj.match_id)
                    opponentTeam = Teams.get_team_by_id(match.away_id if match.home_id == player.team_id else match.home_id).name
                    manager = Managers.get_manager_by_id(team.manager_id).last_name
                    value = newsObj.news_number
                    competition = League.get_league_by_id(match.league_id).name
                    position = player.position

                    title = generate_news_title("player_goals", player = player.last_name, value = value, opponent = opponentTeam)
                    self.newsTitles.append(title)

                    detail = generate_news_detail("player_goals", player = player.last_name, team = team.name, opponent = opponentTeam, value = value, competition = competition, position = position, manager = manager)
                    self.newsDetails.append(detail)
                case "winless_form":
                    team = Teams.get_team_by_id(newsObj.team_id)
                    value = newsObj.news_number
                    match = Matches.get_match_by_id(newsObj.match_id)
                    manager = Managers.get_manager_by_id(team.manager_id).last_name
                    competition = League.get_league_by_id(match.league_id).name

                    title = generate_news_title("winless_form", team = team.name, value = value)
                    self.newsTitles.append(title)

                    detail = generate_news_detail("winless_form", team = team.name, value = value, competition = competition, manager = manager)
                    self.newsDetails.append(detail)
                case "unbeaten_form":
                    team = Teams.get_team_by_id(newsObj.team_id)
                    value = newsObj.news_number
                    match = Matches.get_match_by_id(newsObj.match_id)
                    manager = Managers.get_manager_by_id(team.manager_id).last_name
                    competition = League.get_league_by_id(match.league_id).name

                    title = generate_news_title("unbeaten_form", team = team.name, value = value)
                    self.newsTitles.append(title)

                    detail = generate_news_detail("unbeaten_form", team = team.name, value = value, competition = competition, manager = manager)
                    self.newsDetails.append(detail)

    def checkHover(self, event):
        """
        Check if the mouse is hovering over the news area.

        Args:
            event (Event): The event object.
        """

        if 0 <= event.x <= 770 and 0 <= event.y <= 700:
            if not self.hovering:
                self.hovering = True
                self.showNewsDetails(event)
        else:
            if self.hovering:
                self.hovering = False
                self.removeNewsDetails(event)

    def showNewsDetails(self, event):
        """
        Animate title up when hovering.

        Args:
            event (Event): The event object.
        """

        if event.y > 700:
            return
        self.animate_title((self.title_coords[0], 50))

    def removeNewsDetails(self, event):
        """
        Animate title down when leaving.

        Args:
            event (Event): The event object.
        """

        self.animate_title((self.title_coords[0], 680))

    def animate_title(self, target):
        """
        Smoothly animate the title (and news details) to the target position with safe cancellation.
        The news details follows the title: always 20 px below when moving up, snap to 800 when fully down.

        Args:
            target (tuple): The target (x, y) position for the title.
        """

        target_x, target_y = target

        # Cancel previous animation safely
        if hasattr(self, "anim_id") and self.anim_id is not None:
            try:
                self.canvas.after_cancel(self.anim_id)
            except ValueError:
                pass
            self.anim_id = None

        # Track coordinates manually
        if not hasattr(self, "title_coords"):
            self.title_coords = [20, 680]
        if not hasattr(self, "newsText_coords"):
            self.newsText_coords = [20, 800]

        steps = 70
        delay = 15

        x0, y0 = self.title_coords

        def ease(t):
            return t * t * (3 - 2 * t)

        def animate(step=0):
            t = ease(step / steps)
            new_x = x0 + (target_x - x0) * t
            new_y = y0 + (target_y - y0) * t

            dx = new_x - self.title_coords[0]
            dy = new_y - self.title_coords[1]

            # Move title
            self.canvas.move(self.titleText, dx, dy)
            self.title_coords = [new_x, new_y]

            # Move news text: 20 px below if moving up, follow title
            if target_y < 680:  # title moving up
                new_news_y = new_y + 40
            else:  # moving down
                new_news_y = self.newsText_coords[1] + dy
                if new_y == 680:  # fully down
                    new_news_y = 800

            dy_news = new_news_y - self.newsText_coords[1]
            self.canvas.move(self.newsText, 0, dy_news)
            self.newsText_coords[1] = new_news_y

            if step < steps:
                self.anim_id = self.canvas.after(delay, animate, step + 1)
            else:
                # Snap final positions
                try:
                    self.canvas.coords(self.titleText, target_x, target_y)
                    final_news_y = target_y + 40 if target_y < 680 else 800
                    self.canvas.coords(self.newsText, target_x, final_news_y)
                    self.newsText_coords[1] = final_news_y
                except Exception:
                    pass
                self.title_coords = [target_x, target_y]
                self.anim_id = None

        animate()

    def moveTitle(self, direction):
        """
        Animate the current news title sliding left/right only if fully down.
        If the title is moving up/down, just replace the text without horizontal slide.
        Updates both title and details text.

        Args:
            direction (int): 1 for right, -1 for left.
        """

        if hasattr(self, "afterID") and self.afterID is not None:
            try:
                self.after_cancel(self.afterID)
            except Exception:
                pass
            self.afterID = None

        # Determine next index
        if direction == 1:
            nextNews = (self.currentNews + 1) % len(self.newsTitles)
        else:
            nextNews = (self.currentNews - 1) % len(self.newsTitles)

        # Update the indicator dots
        for i, oval in enumerate(self.currentNewsInds):
            color = "white" if i == nextNews else "gray"
            self.canvas.itemconfigure(oval, fill = color)

        fontSize = 30
        if len(self.newsTitles[nextNews]) > 40:
            fontSize = 20
        elif len(self.newsTitles[nextNews]) > 35:
            fontSize = 25 

        # If the title is not fully down, just replace the text
        if self.title_coords[1] != 680:
            self.canvas.itemconfigure(self.titleText, text = self.newsTitles[nextNews], font = (APP_FONT_BOLD, fontSize))
            self.canvas.itemconfigure(self.newsText, text = self.newsDetails[nextNews])
            self.currentNews = nextNews
            self.afterID = self.after(5000, lambda: self.moveTitle(1))
            return

        # --- Full horizontal slide ---
        self.canvas.update_idletasks()
        canvas_width = self.canvas.winfo_width()
        end_x = 20
        current_y = 680  # fully down
        start_x = canvas_width + 400 if direction == 1 else -800
        old_target_x = -800 if direction == 1 else canvas_width + 400

        newText = self.canvas.create_text(
            start_x, current_y,
            text=self.newsTitles[nextNews],
            fill="white",
            font=(APP_FONT_BOLD, fontSize),
            anchor="w"
        )

        # Update details immediately
        self.canvas.itemconfigure(self.newsText, text=self.newsDetails[nextNews])


        steps = 30
        delay = 15

        def ease(t):
            return t * t * (3 - 2 * t)

        old_start_x = self.title_coords[0]

        def animate(step=0):
            if step <= steps:
                t = ease(step / steps)

                # Horizontal positions
                old_x = old_start_x + (old_target_x - old_start_x) * t
                new_x = start_x + (end_x - start_x) * t
                dx_old = old_x - self.title_coords[0]
                dx_new = new_x - self.canvas.coords(newText)[0]

                self.canvas.move(self.titleText, dx_old, 0)
                self.canvas.move(newText, dx_new, 0)
                self.title_coords[0] = old_x

                # News text only moves vertically if needed (here fully down, so no horizontal)
                self.canvas.move(self.newsText, 0, 0)

                self.canvas.after(delay, animate, step + 1)
            else:
                self.canvas.coords(newText, end_x, current_y)
                self.title_coords = [end_x, current_y]
                self.canvas.delete(self.titleText)
                self.titleText = newText
                self.currentNews = nextNews

        animate()
        self.afterID = self.after(5000, lambda: self.moveTitle(1))

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