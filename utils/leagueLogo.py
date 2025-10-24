import customtkinter as ctk
from settings import *
from data.database import *
from data.gamesDatabase import *
from utils.util_functions import append_overlapping_profile

class LeagueLogo(ctk.CTkImage):
    def __init__(self, parent, image, league, fg_color, relx, rely, anchor, tab):
        """
        A clickable league logo that opens the league profile when clicked.

        Args:
            parent (ctk.CTkFrame): The parent frame where the logo will be placed.
            image (PIL.Image): The image to be used as the league logo.
            league (League): The league object associated with this logo.
            fg_color (str): The foreground color for the logo background.
            relx (float): The relative x position in the parent frame.
            rely (float): The relative y position in the parent frame.
            anchor (str): The anchor position for placing the logo.
            tab (ctk.CTkFrame): The tab frame where the league profile will be displayed.
        """

        super().__init__(image, None, (image.width, image.height))
        
        self.parent = parent
        self.fg_color = fg_color
        self.league = league
        self.tab = tab
        
        self.imageLabel = ctk.CTkLabel(self.parent, image = self, text = "", fg_color = self.fg_color)
        self.imageLabel.place(relx = relx, rely = rely, anchor = anchor)

        self.imageLabel.bind("<Enter><Button-1>", lambda event: self.openLeagueProfile())

    def openLeagueProfile(self):
        """
        Opens the league profile tab for the associated league.
        """

        from tabs.leagueProfile import LeagueProfile

        self.profile = LeagueProfile(self.tab, league_id = self.league.id, changeBackFunction = self.changeBack)
        self.profile.place(x = 0, y = 0, anchor = "nw")
        append_overlapping_profile(self.tab, self.profile)

    def changeBack(self):
        """
        Closes the league profile tab.
        """

        self.profile.place_forget()

    def getImageLabel(self):
        """
        Returns the image label widget.
        """
        
        return self.imageLabel