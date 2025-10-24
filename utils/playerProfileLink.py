import customtkinter as ctk
from settings import *
from data.database import *
from data.gamesDatabase import *
from utils.util_functions import append_overlapping_profile

class PlayerProfileLabel(ctk.CTkFrame):
    def __init__(self, parent, player, player_name, prefix_text, suffix_text, width, height, tab, textColor = "white", fg_color = TKINTER_BACKGROUND, fontSize = 20):
        """
        A label that displays a player profile link with prefix and suffix text.
        
        Args:
            parent (ctk.CTkFrame): The parent frame where the label will be placed.
            player (Player): The player object associated with this link.
            player_name (str): The name of the player to be displayed as a link.
            prefix_text (str): The text to display before the player link.
            suffix_text (str): The text to display after the player link.
            width (int): The width of the label frame.
            height (int): The height of the label frame.
            tab (ctk.CTkFrame): The tab frame where the player profile will be displayed.
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
        self.link = PlayerProfileLink(
            self, player, 
            text = player_name, 
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

class PlayerProfileLink(ctk.CTkLabel):
    def __init__(self, parent, player, text, textColor, relx, rely, anchor, fg_color, tab, fontSize = 20, font = APP_FONT, ingame = False, ingameFunction = None, caStars = None):
        """
        A clickable label that opens the player profile when clicked.

        Args:
            parent (ctk.CTkFrame): The parent frame where the label will be placed.
            player (Player): The player object whose profile will be opened.
            text (str): The text to be displayed on the label.
            textColor (str): The color of the text.
            relx (float): The relative x position in the parent frame.
            rely (float): The relative y position in the parent frame.
            anchor (str): The anchor position for placing the label.
            fg_color (str): The background color of the label.
            tab (ctk.CTkFrame): The tab frame where the player profile will be displayed.
            fontSize (int): The font size of the text. Default is 20.
            font (str): The font type of the text. Default is APP_FONT.
            ingame (bool): Whether to use ingame function or not. Default is False.
            ingameFunction (function): The function to call if ingame is True. Default is None.
            caStars (int): The CA stars to display on the profile. Default is None.
        """

        super().__init__(parent, text = text, font = (font, fontSize), fg_color = fg_color, text_color = textColor, height = 0)
        self.place(relx = relx, rely = rely, anchor = anchor)

        self.player = player
        self.textColor = textColor
        self.tab = tab
        self.fontSize = fontSize
        self.font = font
        self.ingame = ingame
        self.ingameFunction = ingameFunction
        self.caStars = caStars

        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

        self.bind("<Button-1>", self.openPlayerProfile)

    def on_enter(self, event):
        """
        Handles mouse enter event to underline the text and change color.
        """

        self.configure(font = (self.font, self.fontSize, "underline"), text_color = UNDERLINE_BLUE, cursor = "hand2")

    def on_leave(self, event):
        """
        Handles mouse leave event to revert text appearance.
        """
        
        self.configure(font = (self.font, self.fontSize), text_color = self.textColor, cursor = "")

    def openPlayerProfile(self, event):
        """
        Opens the player profile tab for the associated player.
        """

        if self.ingame:
            self.ingameFunction(self.player)
        else:
            from tabs.playerProfile import PlayerProfile

            self.profile = PlayerProfile(self.tab, self.player, changeBackFunction = self.changeBack, caStars = self.caStars)
            self.profile.place(x = 0, y = 0, anchor = "nw")
            append_overlapping_profile(self.tab, self.profile)

    def changeBack(self):
        """
        Closes the player profile tab.
        """
        
        self.profile.place_forget()
