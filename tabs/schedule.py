import customtkinter as ctk
from settings import *
from data.database import *
from data.gamesDatabase import *
from utils.frames import MatchFrame

class Schedule(ctk.CTkFrame):
    def __init__(self, parent, session, manager_id):
        super().__init__(parent, fg_color = TKINTER_BACKGROUND, width = 1000, height = 700, corner_radius = 0)

        self.session = session
        self.manager_id = manager_id
        self.parent = parent

        self.frames = []

        self.team = Teams.get_teams_by_manager(session, manager_id)[0]
        self.matches = Matches.get_all_matches_by_team(session, self.team.id)
        self.league = League.get_league_by_id(session, self.matches[0].league_id)

        self.titleFrame = ctk.CTkFrame(self, fg_color = TKINTER_BACKGROUND, width = 1000, height = 60, corner_radius = 0)
        self.titleFrame.place(relx = 0.5, rely = 0.05, anchor = "center")

        ctk.CTkLabel(self.titleFrame, text = f"{self.team.name} Schedule", font = (APP_FONT_BOLD, 35), fg_color = TKINTER_BACKGROUND).place(relx = 0.03, rely = 0.35, anchor = "w")
        
        canvas = ctk.CTkCanvas(self.titleFrame, width = 900, height = 5, bg = GREY_BACKGROUND, bd = 0, highlightthickness = 0)
        canvas.place(relx = 0.5, rely = 0.9, anchor = "center")

        self.scheduleFrame = ctk.CTkScrollableFrame(self, fg_color = TKINTER_BACKGROUND, width = 650, height = 590, corner_radius = 0)
        self.scheduleFrame.place(relx = 0.02, rely = 0.15, anchor = "nw")

        self.matchInfoFrame = ctk.CTkFrame(self, fg_color = GREY_BACKGROUND, width = 280, height = 590, corner_radius = 15)
        self.matchInfoFrame.place(relx = 0.98, rely = 0.15, anchor = "ne")

        self.addMatches()

    def addMatches(self, replace = False):

        if replace:
            for widget in self.winfo_children():
                widget.destroy()

        for match in self.matches:
            frame = MatchFrame(self, self.session, self.manager_id, match, self.scheduleFrame, self.matchInfoFrame, self)
            self.frames.append(frame)
