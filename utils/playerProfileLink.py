import customtkinter as ctk
from settings import *
from data.database import *
from data.gamesDatabase import *

class PlayerProfileLabel(ctk.CTkFrame):
    def __init__(self, parent, player, player_name, prefix_text, suffix_text, width, height, tab, textColor = "white", fg_color = TKINTER_BACKGROUND, fontSize = 20):
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
        self.configure(font = (self.font, self.fontSize, "underline"), text_color = UNDERLINE_BLUE, cursor = "hand2")

    def on_leave(self, event):
        self.configure(font = (self.font, self.fontSize), text_color = self.textColor, cursor = "")

    def openPlayerProfile(self, event):

        if self.ingame:
            self.ingameFunction(self.player)
        else:
            from tabs.playerProfile import PlayerProfile

            self.profile = PlayerProfile(self.tab, self.player, changeBackFunction = self.changeBack, caStars = self.caStars)
            self.profile.place(x = 0, y = 0, anchor = "nw")

            self.tab.parent.overlappingProfiles.append(self.profile)

    def changeBack(self):
        self.profile.place_forget()
