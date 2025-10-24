import customtkinter as ctk
from settings import *
from data.database import *
from data.gamesDatabase import *
from utils.util_functions import append_overlapping_profile

class TeamLogo(ctk.CTkImage):
    def __init__(self, parent, image, team, fg_color, relx, rely, anchor, tab, clickable = True):
        """
        A clickable team logo that opens the team's profile when clicked.
        
        Args:
            parent: The parent tkinter widget.
            image: The image to display as the team logo.
            team: The team object associated with the logo.
            fg_color: The foreground color for the label background.
            relx: The relative x position for placing the label.
            rely: The relative y position for placing the label.
            anchor: The anchor position for placing the label.
            tab: The tab in which this logo is displayed.
            clickable: Whether the logo is clickable to open the team profile.
        """

        super().__init__(image, None, (image.width, image.height))
        
        self.parent = parent
        self.fg_color = fg_color
        self.team = team
        self.tab = tab
        
        self.imageLabel = ctk.CTkLabel(self.parent, image = self, text = "", fg_color = self.fg_color)
        self.imageLabel.place(relx = relx, rely = rely, anchor = anchor)

        if clickable:
            self.imageLabel.bind("<Enter><Button-1>", lambda event: self.openClubProfile())

    def openClubProfile(self):
        """
        Opens the team profile tab for the associated team.
        """
        
        from tabs.teamProfile import TeamProfile

        manager = Managers.get_manager_by_id(self.team.manager_id)

        if manager.user != 1:
            self.profile = TeamProfile(self.tab, manager_id = self.team.manager_id, parentTab = self.tab, changeBackFunction = self.changeBack)
            self.profile.place(x = 0, y = 0, anchor = "nw")
            append_overlapping_profile(self.tab, self.profile)
        else:
            self.tab.parent.changeTab(5)

    def changeBack(self):
        """
        Closes the team profile tab.
        """
        
        self.profile.place_forget()

    def getImageLabel(self):
        """
        Returns the image label widget.
        """
        
        return self.imageLabel