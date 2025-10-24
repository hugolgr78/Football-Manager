import customtkinter as ctk
from settings import *
from data.database import *
from data.gamesDatabase import *
from utils.util_functions import append_overlapping_profile

class MatchProfileLabel(ctk.CTkFrame):
    def __init__(self, parent, match, match_score, prefix_text, suffix_text, width, height, tab, textColor = "white", fg_color = TKINTER_BACKGROUND, fontSize = 20):
        """
        A label that displays a match profile link with prefix and suffix text.
        
        Args:
            parent (ctk.CTkFrame): The parent frame where the label will be placed.
            match (Match): The match object associated with this link.
            match_score (str): The text to be displayed as the match score link.
            prefix_text (str): The text to display before the match link.
            suffix_text (str): The text to display after the match link.
            width (int): The width of the label frame.
            height (int): The height of the label frame.
            tab (ctk.CTkFrame): The tab frame where the match profile will be displayed.
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
        self.link = MatchProfileLink(
            self, match, 
            text = match_score, 
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

class MatchProfileLink(ctk.CTkLabel):
    def __init__(self, parent, match, text, textColor, relx, rely, anchor, fg_color, tab, fontSize = 20, font = APP_FONT):
        """
        A clickable label that opens the match profile when clicked.
        
        Args:
            parent (ctk.CTkFrame): The parent frame where the label will be placed.
            match (Match): The match object associated with this link.
            text (str): The text to be displayed on the label.
            textColor (str): The color of the text.
            relx (float): The relative x position in the parent frame.
            rely (float): The relative y position in the parent frame.
            anchor (str): The anchor position for placing the label.
            fg_color (str): The background color of the label.
            tab (ctk.CTkFrame): The tab frame where the match profile will be displayed.
            fontSize (int): The font size of the text. Default is 20.
            font (str): The font family of the text. Default is APP_FONT.
        """
        
        super().__init__(parent, text = text, font = (font, fontSize), fg_color = fg_color, text_color = textColor, height = 0)
        self.place(relx = relx, rely = rely, anchor = anchor)

        self.match = match
        self.textColor = textColor
        self.tab = tab
        self.fontSize = fontSize
        self.font = font

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
        Opens the match profile tab for the associated match.
        """
        
        from tabs.matchProfile import MatchProfile

        self.profile = MatchProfile(self.tab, self.match, self.tab, self.changeBack)
        self.profile.place(x = 0, y = 0, anchor = "nw")
        append_overlapping_profile(self.tab, self.profile)

    def changeBack(self):
        """
        Closes the match profile tab.
        """
        
        self.profile.place_forget()
