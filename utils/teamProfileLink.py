import customtkinter as ctk
from settings import *
from data.database import *
from data.gamesDatabase import *
from utils.util_functions import append_overlapping_profile

class TeamProfileLabel(ctk.CTkFrame):
    def __init__(self, parent, manager_id, team_name, prefix_text, suffix_text, width, height, tab, textColor = "white", fg_color = TKINTER_BACKGROUND, fontSize = 20):
        """
        A label that displays a team name as a clickable link to the team's profile,
        
        Args:
            parent (ctk.CTkFrame): The parent frame where the label will be placed.
            manager_id (int): The ID of the team's manager.
            team_name (str): The name of the team to be displayed as a link.
            prefix_text (str): The text to display before the team link.
            suffix_text (str): The text to display after the team link.
            width (int): The width of the label frame.
            height (int): The height of the label frame.
            tab (ctk.CTkFrame): The tab frame where the team profile will be displayed.
            textColor (str): The color of the text. Default is "white".
            fg_color (str): The background color of the label frame. Default is TKINTER_BACKGROUND.
            fontSize (int): The font size of the text. Default is 20.
        """

        super().__init__(parent, fg_color = fg_color, width = width, height = height, corner_radius = 0)
        
        # Static part of the text
        self.prefix_label = ctk.CTkLabel(
            self, text = prefix_text, 
            font = (APP_FONT, fontSize), 
            text_color = textColor, 
            fg_color = fg_color
        )
        self.prefix_label.pack(side = "left")
        
        # Clickable link part
        self.link = TeamProfileLink(
            self, manager_id, 
            text = team_name, 
            textColor = textColor, 
            relx = 0, rely = 0, anchor = "w", 
            fg_color = fg_color, 
            tab = tab, 
            fontSize = fontSize
        )
        self.link.pack(side = "left")

        # Static suffix text
        self.suffix_label = ctk.CTkLabel(
            self, text = suffix_text,
            font = (APP_FONT, fontSize), 
            text_color = textColor, 
            fg_color = fg_color
        )
        self.suffix_label.pack(side = "left")

class TeamProfileLink(ctk.CTkLabel):
    def __init__(self, parent, manager_id, text, textColor, relx, rely, anchor, fg_color, tab, fontSize = 20):
        """
        A clickable label that opens the team profile when clicked.
        
        Args:
            parent (ctk.CTkFrame): The parent frame where the label will be placed.
            manager_id (int): The ID of the team's manager.
            text (str): The text to display as the team link.
            textColor (str): The color of the text.
            relx (float): The relative x position for placing the label.
            rely (float): The relative y position for placing the label.
            anchor (str): The anchor position for placing the label.
            fg_color (str): The background color of the label.
            tab (ctk.CTkFrame): The tab frame where the team profile will be displayed.
            fontSize (int): The font size of the text. Default is 20.
        """

        super().__init__(parent, text = text, font = (APP_FONT, fontSize), fg_color = fg_color, text_color = textColor)
        self.place(relx = relx, rely = rely, anchor = anchor)

        self.manager_id = manager_id
        self.textColor = textColor
        self.tab = tab
        self.fontSize = fontSize

        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

        self.bind("<Button-1>", self.openClubProfile)

    def on_enter(self, event):
        """
        Handles mouse enter event to underline the text and change color.
        """
        
        self.configure(font = (APP_FONT, self.fontSize, "underline"), text_color = UNDERLINE_BLUE, cursor = "hand2")

    def on_leave(self, event):
        """
        Handles mouse leave event to revert text appearance.
        """
        
        self.configure(font = (APP_FONT, self.fontSize), text_color = self.textColor, cursor = "")

    def openClubProfile(self, event):
        """
        Opens the team profile tab for the associated team.
        """
        
        from tabs.teamProfile import TeamProfile

        manager = Managers.get_manager_by_id(self.manager_id)

        if manager.user != 1:
            self.profile = TeamProfile(self.tab, manager_id = self.manager_id, parentTab = self.tab, changeBackFunction = self.changeBack)
            self.profile.place(x = 0, y = 0, anchor = "nw")
            append_overlapping_profile(self.tab, self.profile)
        else:
            self.tab.parent.changeTab(5)

    def changeBack(self):
        """
        Closes the team profile tab.
        """
        
        self.profile.place_forget()