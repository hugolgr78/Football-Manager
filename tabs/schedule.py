import customtkinter as ctk
from settings import *
import calendar
from data.database import *
from data.gamesDatabase import *
from utils.frames import MatchFrame, CalendarFrame
from utils.util_functions import *

class Schedule(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color = TKINTER_BACKGROUND, width = 1000, height = 700, corner_radius = 0)

        self.manager_id = Managers.get_all_user_managers()[0].id
        self.parent = parent

        self.frames = []

        self.team = Teams.get_teams_by_manager(self.manager_id)[0]
        self.leagueData = LeagueTeams.get_league_by_team(self.team.id)
        self.league = League.get_league_by_id(self.leagueData.league_id)
        self.matches = Matches.get_all_matches_by_team(self.team.id)

        self.titleFrame = ctk.CTkFrame(self, fg_color = TKINTER_BACKGROUND, width = 1000, height = 60, corner_radius = 0)
        self.titleFrame.place(relx = 0.5, rely = 0.05, anchor = "center")

        ctk.CTkLabel(self.titleFrame, text = f"{self.team.name} Schedule", font = (APP_FONT_BOLD, 35), fg_color = TKINTER_BACKGROUND).place(relx = 0.03, rely = 0.35, anchor = "w")
        
        canvas = ctk.CTkCanvas(self.titleFrame, width = 900, height = 5, bg = GREY_BACKGROUND, bd = 0, highlightthickness = 0)
        canvas.place(relx = 0.5, rely = 0.9, anchor = "center")

        self.scheduleFrame = ctk.CTkScrollableFrame(self, fg_color = TKINTER_BACKGROUND, width = 650, height = 590, corner_radius = 0)
        self.scheduleFrame.place(relx = 0.02, rely = 0.15, anchor = "nw")

        self.matchInfoFrame = ctk.CTkFrame(self, fg_color = GREY_BACKGROUND, width = 280, height = 560, corner_radius = 15)
        self.matchInfoFrame.place(relx = 0.98, rely = 0.15, anchor = "ne")

        self.calendarFrame = CalendarFrame(self, self.matches, self, self, self.matchInfoFrame, self.team.id, managingTeam = True)

        self.switchButton = ctk.CTkButton(self, text = "Calendar", fg_color = GREY_BACKGROUND, command = self.switchFrames, width = 280, height = 15)
        self.switchButton.place(relx = 0.98, rely = 0.99, anchor = "se")

        self.addMatches()

    def addMatches(self, replace = False):

        if replace:
            for widget in self.winfo_children():
                widget.destroy()

        currentMonth = ""
        for match in self.matches:

            _, text, _ = format_datetime_split(match.date)
            month = text.split(" ")[1]

            if month != currentMonth:
                currentMonth = month
                frame = ctk.CTkFrame(self.scheduleFrame, fg_color = TKINTER_BACKGROUND, width = 640, height = 50, corner_radius = 0)
                frame.pack(expand = True, fill = "both", padx = 10, pady = (0, 10))

                ctk.CTkLabel(frame, text = month, font = (APP_FONT_BOLD, 25), fg_color = TKINTER_BACKGROUND).place(relx = 0, rely = 0.5, anchor = "w")

            frame = MatchFrame(self, self.manager_id, match, self.scheduleFrame, self.matchInfoFrame, self)
            self.frames.append(frame)

    def switchFrames(self):
        if self.scheduleFrame.winfo_ismapped():
            self.scheduleFrame.place_forget()
            self.calendarFrame.place(relx = 0.02, rely = 0.15, anchor = "nw")
            self.switchButton.configure(text = "List")
        else:
            self.calendarFrame.place_forget()
            self.scheduleFrame.place(relx = 0.02, rely = 0.15, anchor = "nw")
            self.switchButton.configure(text = "Calendar")