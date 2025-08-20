import customtkinter as ctk
from settings import *

class SettingsTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color = TKINTER_BACKGROUND, width = 1000, height = 700, corner_radius = 0)

        self.parent = parent
