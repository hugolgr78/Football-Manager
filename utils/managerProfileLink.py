import customtkinter as ctk
from settings import *
from data.database import *
from data.gamesDatabase import *
from utils.util_functions import append_overlapping_profile

class ManagerProfileLink(ctk.CTkLabel):
    def __init__(self, parent, manager_id, text, textColor, relx, rely, anchor, fg_color, tab, fontSize = 20):
        super().__init__(parent, text = text, font = (APP_FONT, fontSize), fg_color = fg_color, text_color = textColor)
        self.place(relx = relx, rely = rely, anchor = anchor)

        self.manager_id = manager_id
        self.textColor = textColor
        self.tab = tab

        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

        self.bind("<Button-1>", self.openManagerProfile)

    def on_enter(self, event):
        self.configure(font = (APP_FONT, 20, "underline"), text_color = UNDERLINE_BLUE, cursor = "hand2")

    def on_leave(self, event):
        self.configure(font = (APP_FONT, 20), text_color = self.textColor, cursor = "")

    def openManagerProfile(self, event):
        from tabs.managerProfile import ManagerProfile

        manager = Managers.get_manager_by_id(self.manager_id)

        if manager.user != 1:
            self.profile = ManagerProfile(self.tab, manager_id = self.manager_id, changeBackFunction = self.changeBack)
            self.profile.place(x = 0, y = 0, anchor = "nw")
            append_overlapping_profile(self.tab, self.profile)
        else:
            self.tab.parent.changeTab(7)

    def changeBack(self):
        self.profile.place_forget()
