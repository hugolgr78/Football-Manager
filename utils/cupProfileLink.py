import customtkinter as ctk
from settings import *
from data.database import *
from data.gamesDatabase import *
from utils.util_functions import append_overlapping_profile

class CupProfileLabel(ctk.CTkFrame):
    def __init__(self, parent, cup_name, prefix_text, suffix_text, width, height, tab, textColor = "white", fg_color = TKINTER_BACKGROUND, fontSize = 20):
        """
        A label that displays a cup profile link with prefix and suffix text.

        Args:
            parent (ctk.CTkFrame): The parent frame where the label will be placed.
            cup_name (str): The name of the cup to be displayed as a link.
            prefix_text (str): The text to display before the cup link.
            suffix_text (str): The text to display after the cup link.
            width (int): The width of the label frame.
            height (int): The height of the label frame.
            tab (ctk.CTkFrame): The tab frame where the cup profile will be displayed.
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
        self.link = CupProfileLink(
            self, 
            text = cup_name, 
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

class CupProfileLink(ctk.CTkLabel):
    def __init__(self, parent, text, textColor, relx, rely, anchor, fg_color, tab, fontSize = 20):
        """
        A clickable label that opens the cup profile when clicked.
        
        Args:
            parent (ctk.CTkFrame): The parent frame where the label will be placed.
            text (str): The text to be displayed as the cup link.
            textColor (str): The color of the text.
            relx (float): The relative x position in the parent frame.
            rely (float): The relative y position in the parent frame.
            anchor (str): The anchor position for placing the label.
            fg_color (str): The background color of the label.
            tab (ctk.CTkFrame): The tab frame where the cup profile will be displayed.
            fontSize (int): The font size of the text. Default is 20.
        """
        super().__init__(parent, text = text, font = (APP_FONT, fontSize), fg_color = fg_color, text_color = textColor)
        self.place(relx = relx, rely = rely, anchor = anchor)

        self.cup_name = text
        self.cup = Cup.get_cup_by_name(text)
        self.textColor = textColor
        self.tab = tab
        self.fontSize = fontSize

        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

        self.bind("<Button-1>", self.opencupProfile)

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

    def openCupProfile(self, event):
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
