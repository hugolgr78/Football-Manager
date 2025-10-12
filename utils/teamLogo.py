import customtkinter as ctk
from settings import *
from data.database import *
from data.gamesDatabase import *
from utils.util_functions import append_overlapping_profile

class TeamLogo(ctk.CTkImage):
    def __init__(self, parent, image, team, fg_color, relx, rely, anchor, tab):
        super().__init__(image, None, (image.width, image.height))
        
        self.parent = parent
        self.fg_color = fg_color
        self.team = team
        self.tab = tab
        
        self.imageLabel = ctk.CTkLabel(self.parent, image = self, text = "", fg_color = self.fg_color)
        self.imageLabel.place(relx = relx, rely = rely, anchor = anchor)

        self.imageLabel.bind("<Enter><Button-1>", lambda event: self.openClubProfile())

    def openClubProfile(self):
        from tabs.teamProfile import TeamProfile

        manager = Managers.get_manager_by_id(self.team.manager_id)

        if manager.user != 1:
            self.profile = TeamProfile(self.tab, manager_id = self.team.manager_id, parentTab = self.tab, changeBackFunction = self.changeBack)
            self.profile.place(x = 0, y = 0, anchor = "nw")
            append_overlapping_profile(self.tab, self.profile)
        else:
            self.tab.parent.changeTab(5)

    def changeBack(self):
        self.profile.place_forget()

    def getImageLabel(self):
        return self.imageLabel