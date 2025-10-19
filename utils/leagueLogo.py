import customtkinter as ctk
from settings import *
from data.database import *
from data.gamesDatabase import *
from utils.util_functions import append_overlapping_profile

class LeagueLogo(ctk.CTkImage):
    def __init__(self, parent, image, league, fg_color, relx, rely, anchor, tab):
        super().__init__(image, None, (image.width, image.height))
        
        self.parent = parent
        self.fg_color = fg_color
        self.league = league
        self.tab = tab
        
        self.imageLabel = ctk.CTkLabel(self.parent, image = self, text = "", fg_color = self.fg_color)
        self.imageLabel.place(relx = relx, rely = rely, anchor = anchor)

        self.imageLabel.bind("<Enter><Button-1>", lambda event: self.openLeagueProfile())

    def openLeagueProfile(self):
        from tabs.leagueProfile import LeagueProfile

        self.profile = LeagueProfile(self.tab, league_id = self.league.id, changeBackFunction = self.changeBack)
        self.profile.place(x = 0, y = 0, anchor = "nw")
        append_overlapping_profile(self.tab, self.profile)

    def changeBack(self):
        self.profile.place_forget()

    def getImageLabel(self):
        return self.imageLabel