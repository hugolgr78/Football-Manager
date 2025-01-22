import customtkinter as ctk
from settings import *
from data.database import *
from data.gamesDatabase import *

class PlayerProfileLink(ctk.CTkLabel):
    def __init__(self, parent, session, player, text, textColor, relx, rely, anchor, fg_color, tab, fontSize = 20):
        super().__init__(parent, text = text, font = (APP_FONT, fontSize), fg_color = fg_color, text_color = textColor)
        self.place(relx = relx, rely = rely, anchor = anchor)

        self.session = session
        self.player = player
        self.textColor = textColor
        self.tab = tab

        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

        self.bind("<Button-1>", self.openPlayerProfile)

    def on_enter(self, event):
        self.configure(font = (APP_FONT, 20, "underline"), text_color = UNDERLINE_BLUE, cursor = "hand2")

    def on_leave(self, event):
        self.configure(font = (APP_FONT, 20), text_color = self.textColor, cursor = "")

    def openPlayerProfile(self, event):
        from tabs.playerProfile import PlayerProfile

        self.profile = PlayerProfile(self.tab, self.session, self.player, self.changeBack)
        self.profile.place(x = 0, y = 0, anchor = "nw")

        self.tab.parent.overlappingProfiles.append(self.profile)

    def changeBack(self):
        self.profile.place_forget()
