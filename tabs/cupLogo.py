import customtkinter as ctk
from settings import *
from data.database import *
from data.gamesDatabase import *
from utils.util_functions import append_overlapping_profile

class CupLogo(ctk.CTkImage):
    def __init__(self, parent, image, cup, fg_color, relx, rely, anchor, tab):
        """
        A clickable cup logo that opens the cup profile when clicked.

        Args:
            parent (ctk.CTkFrame): The parent frame where the logo will be placed.
            image (PIL.Image): The image to be used as the cup logo.
            cup (Cup): The cup object associated with this logo.
            fg_color (str): The foreground color for the logo background.
            relx (float): The relative x position in the parent frame.
            rely (float): The relative y position in the parent frame.
            anchor (str): The anchor position for placing the logo.
            tab (ctk.CTkFrame): The tab frame where the cup profile will be displayed.
        """

        super().__init__(image, None, (image.width, image.height))
        
        self.parent = parent
        self.fg_color = fg_color
        self.cup = cup
        self.tab = tab
        
        self.imageLabel = ctk.CTkLabel(self.parent, image = self, text = "", fg_color = self.fg_color)
        self.imageLabel.place(relx = relx, rely = rely, anchor = anchor)

        self.imageLabel.bind("<Enter><Button-1>", lambda event: self.openCupProfile())

    def openCupProfile(self):
        """
        Opens the cup profile tab for the associated cup.
        """

        from tabs.cupProfile import CupProfile

        self.profile = CupProfile(self.tab, cup_id = self.cup.id, changeBackFunction = self.changeBack)
        self.profile.place(x = 0, y = 0, anchor = "nw")
        append_overlapping_profile(self.tab, self.profile)

    def changeBack(self):
        """
        Closes the cup profile tab.
        """

        self.profile.place_forget()

    def getImageLabel(self):
        """
        Returns the image label widget.
        """
        
        return self.imageLabel