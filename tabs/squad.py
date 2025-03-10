import customtkinter as ctk
from settings import *
from data.database import *
from data.gamesDatabase import *
from PIL import Image
import io
from utils.frames import PlayerFrame

class Squad(ctk.CTkFrame):
    def __init__(self, parent, manager_id):
        super().__init__(parent, fg_color = TKINTER_BACKGROUND, width = 1000, height = 700, corner_radius = 0)

        self.parent = parent
        self.manager_id = manager_id

        self.team = Teams.get_teams_by_manager(manager_id)[0]
        self.players = Players.get_all_players_by_team(self.team.id)

        self.titleFrame = ctk.CTkFrame(self, fg_color = TKINTER_BACKGROUND, width = 1000, height = 100, corner_radius = 0)
        self.titleFrame.pack(expand = True, fill = "both", padx = 10, pady = 10)

        ctk.CTkLabel(self.titleFrame, text = f"{self.team.name} Squad", font = (APP_FONT_BOLD, 35), fg_color = TKINTER_BACKGROUND).place(relx = 0.03, rely = 0.2, anchor = "w")
        
        canvas = ctk.CTkCanvas(self.titleFrame, width = 900, height = 5, bg = GREY_BACKGROUND, bd = 0, highlightthickness = 0)
        canvas.place(relx = 0.5, rely = 0.5, anchor = "center")

        self.infoFrame = ctk.CTkFrame(self.titleFrame, fg_color = TKINTER_BACKGROUND, width = 1000, height = 40, corner_radius = 0)
        self.infoFrame.place(relx = 0.5, rely = 0.75, anchor = "center")

        ctk.CTkLabel(self.infoFrame, text = "Number", font = (APP_FONT_BOLD, 20), fg_color = TKINTER_BACKGROUND).place(relx = 0.05, rely = 0.5, anchor = "center")
        ctk.CTkLabel(self.infoFrame, text = "Name", font = (APP_FONT_BOLD, 20), fg_color = TKINTER_BACKGROUND).place(relx = 0.15, rely = 0.5, anchor = "w")
        ctk.CTkLabel(self.infoFrame, text = "Age", font = (APP_FONT_BOLD, 20), fg_color = TKINTER_BACKGROUND).place(relx = 0.45, rely = 0.5, anchor = "center")
        ctk.CTkLabel(self.infoFrame, text = "Positions", font = (APP_FONT_BOLD, 20), fg_color = TKINTER_BACKGROUND).place(relx = 0.58, rely = 0.5, anchor = "center")
        ctk.CTkLabel(self.infoFrame, text = "Nat", font = (APP_FONT_BOLD, 20), fg_color = TKINTER_BACKGROUND).place(relx = 0.68, rely = 0.5, anchor = "center")
        ctk.CTkLabel(self.infoFrame, text = "Morale", font = (APP_FONT_BOLD, 20), fg_color = TKINTER_BACKGROUND).place(relx = 0.79, rely = 0.5, anchor = "center")
        ctk.CTkLabel(self.infoFrame, text = "Talk", font = (APP_FONT_BOLD, 20), fg_color = TKINTER_BACKGROUND).place(relx = 0.9, rely = 0.5, anchor = "center")

        self.playersFrame = ctk.CTkScrollableFrame(self, fg_color = TKINTER_BACKGROUND, width = 982, height = 580, corner_radius = 0)
        self.playersFrame.pack(expand = True, fill = "both", padx = (0, 20))

        self.addPlayers()

    def addPlayers(self, replace = False):

        if replace:
            for widget in self.winfo_children():
                widget.destroy()

        for player in self.players:
            if player.player_role != "Youth Team":
                PlayerFrame(self, self.manager_id, player, self.playersFrame)
