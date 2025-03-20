import customtkinter as ctk
from settings import *
from data.database import *
from data.gamesDatabase import *

class RefereeProfileLabel(ctk.CTkFrame):
    def __init__(self, parent, referee, referee_name, prefix_text, suffix_text, width, height, tab, textColor = "white", fg_color = TKINTER_BACKGROUND, fontSize = 20):
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
        self.link = RefereeProfileLink(
            self, referee, 
            text = referee_name, 
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

class RefereeProfileLink(ctk.CTkLabel):
    def __init__(self, parent, referee, text, textColor, relx, rely, anchor, fg_color, tab, fontSize = 20):
        super().__init__(parent, text = text, font = (APP_FONT, fontSize), fg_color = fg_color, text_color = textColor)
        self.place(relx = relx, rely = rely, anchor = anchor)

        self.referee = referee
        self.textColor = textColor
        self.tab = tab
        self.fontSize = fontSize

        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

        self.bind("<Button-1>", self.openPlayerProfile)

    def on_enter(self, event):
        self.configure(font = (APP_FONT, self.fontSize, "underline"), text_color = UNDERLINE_BLUE, cursor = "hand2")

    def on_leave(self, event):
        self.configure(font = (APP_FONT, self.fontSize), text_color = self.textColor, cursor = "")

    def openPlayerProfile(self, event):
        from tabs.refereeProfile import RefereeProfile

        self.profile = RefereeProfile(self.tab, self.referee, self.changeBack)
        self.profile.place(x = 0, y = 0, anchor = "nw")

        self.tab.parent.overlappingProfiles.append(self.profile)

    def changeBack(self):
        self.profile.place_forget()
