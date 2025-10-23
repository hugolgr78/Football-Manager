import customtkinter as ctk
from settings import *
from data.database import *
from data.gamesDatabase import *
from utils.util_functions import append_overlapping_profile

class LeagueProfileLabel(ctk.CTkFrame):
    def __init__(self, parent, manager_id, league_name, prefix_text, suffix_text, width, height, tab, textColor = "white", fg_color = TKINTER_BACKGROUND, fontSize = 20):
        """
        A label that displays a league profile link with prefix and suffix text.

        Args:
            parent (ctk.CTkFrame): The parent frame where the label will be placed.
            manager_id (int): The ID of the manager associated with the league.
            league_name (str): The name of the league to be displayed as a link.
            prefix_text (str): The text to display before the league link.
            suffix_text (str): The text to display after the league link.
            width (int): The width of the label frame.
            height (int): The height of the label frame.
            tab (ctk.CTkFrame): The tab frame where the league profile will be displayed.
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
        self.link = LeagueProfileLink(
            self, manager_id, 
            text = league_name, 
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

class LeagueProfileLink(ctk.CTkLabel):
    def __init__(self, parent, manager_id, text, textColor, relx, rely, anchor, fg_color, tab, fontSize = 20):
        """
        A clickable label that opens the league profile when clicked.
        
        Args:
            parent (ctk.CTkFrame): The parent frame where the label will be placed.
            manager_id (int): The ID of the manager associated with the league.
            text (str): The text to be displayed as the league link.
            textColor (str): The color of the text.
            relx (float): The relative x position in the parent frame.
            rely (float): The relative y position in the parent frame.
            anchor (str): The anchor position for placing the label.
            fg_color (str): The background color of the label.
            tab (ctk.CTkFrame): The tab frame where the league profile will be displayed.
            fontSize (int): The font size of the text. Default is 20.
        """
        super().__init__(parent, text = text, font = (APP_FONT, fontSize), fg_color = fg_color, text_color = textColor)
        self.place(relx = relx, rely = rely, anchor = anchor)

        self.league_name = text
        self.manager_id = manager_id
        self.league = League.get_league_by_name(text)
        self.textColor = textColor
        self.tab = tab
        self.fontSize = fontSize

        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

        self.bind("<Button-1>", self.openLeagueProfile)

    def on_enter(self, event):
        """
        Changes the label appearance on mouse hover.
        """

        self.configure(font = (APP_FONT, self.fontSize, "underline"), text_color = UNDERLINE_BLUE, cursor = "hand2")

    def on_leave(self, event):
        """
        Reverts the label appearance when mouse leaves.
        """

        self.configure(font = (APP_FONT, self.fontSize), text_color = self.textColor, cursor = "")

    def openLeagueProfile(self, event):
        """
        Opens the league profile tab for the associated league.
        """

        from tabs.leagueProfile import LeagueProfile
        
        managerTeam = Teams.get_teams_by_manager(Managers.get_all_user_managers()[0].id)[0]
        leagueTeams = LeagueTeams.get_league_by_team(managerTeam.id)
        managerLeagueID = League.get_league_by_id(leagueTeams.league_id).id

        if self.league.id != managerLeagueID:
            self.profile = LeagueProfile(self.tab, league_id = self.league.id, changeBackFunction = self.changeBack)
            self.profile.place(x = 0, y = 0, anchor = "nw")
            append_overlapping_profile(self.tab, self.profile)
        else:
            self.tab.parent.changeTab(6)

    def changeBack(self):
        """
        Closes the league profile tab.
        """
        
        self.profile.place_forget()
