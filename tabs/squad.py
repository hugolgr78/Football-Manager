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
                PlayerFrame(self, self.manager_id, player, self.playersFrame, talkFunction = self.talkToPlayer)

    def talkToPlayer(self, player):

        self.talkFrame = ctk.CTkFrame(self, fg_color = TKINTER_BACKGROUND, width = 650, height = 500, corner_radius = 15, border_width = 3, border_color = GREY_BACKGROUND)
        self.talkFrame.place(relx = 0.5, rely = 0.5, anchor = "center")

        for frame in self.playersFrame.winfo_children():
            frame.disableTalkButton()

        managerFrame = ctk.CTkFrame(self.talkFrame, fg_color = TKINTER_BACKGROUND, width = 145, height = 490, corner_radius = 0)
        managerFrame.place(x = 150, y = 5, anchor = "ne")

        src = Image.open("Images/default_user.png")
        src.thumbnail((75, 75))
        managerImage = ctk.CTkImage(src, None, (src.width, src.height))
        ctk.CTkLabel(managerFrame, image = managerImage, text = "").place(relx = 0.5, rely = 0.1, anchor = "n")

        manager = Managers.get_manager_by_id(self.manager_id)
        ctk.CTkLabel(managerFrame, text = f"{manager.first_name} {manager.last_name}", font = (APP_FONT_BOLD, 15), fg_color = TKINTER_BACKGROUND).place(relx = 0.5, rely = 0.27, anchor = "n")


        playerFrame = ctk.CTkFrame(self.talkFrame, fg_color = TKINTER_BACKGROUND, width = 145, height = 490, corner_radius = 0)
        playerFrame.place(x = 500, y = 5, anchor = "nw")

        src = Image.open("Images/default_user.png")
        src.thumbnail((75, 75))
        playerImage = ctk.CTkImage(src, None, (src.width, src.height))
        ctk.CTkLabel(playerFrame, image = playerImage, text = "").place(relx = 0.5, rely = 0.1, anchor = "n")
        ctk.CTkLabel(playerFrame, text = f"{player.first_name} {player.last_name}", font = (APP_FONT_BOLD, 15), fg_color = TKINTER_BACKGROUND).place(relx = 0.5, rely = 0.27, anchor = "n")

        talkingFrame = ctk.CTkFrame(self.talkFrame, fg_color = TKINTER_BACKGROUND, width = 350, height = 390, corner_radius = 0)
        talkingFrame.place(x = 150, y = 5, anchor = "nw")

        promptsFrame = ctk.CTkFrame(self.talkFrame, fg_color = TKINTER_BACKGROUND, width = 350, height = 95, corner_radius = 0)
        promptsFrame.place(x = 150, y = 400, anchor = "nw")

        canvas = ctk.CTkCanvas(self.talkFrame, width = 5, height = 700, bg = GREY_BACKGROUND, bd = 0, highlightthickness = 0)
        canvas.place(x = 185, rely = 0.5, anchor = "center")

        canvas = ctk.CTkCanvas(self.talkFrame, width = 5, height = 700, bg = GREY_BACKGROUND, bd = 0, highlightthickness = 0)
        canvas.place(x = 625, rely = 0.5, anchor = "center")

        canvas = ctk.CTkCanvas(self.talkFrame, width = 440, height = 5, bg = GREY_BACKGROUND, bd = 0, highlightthickness = 0)
        canvas.place(relx = 0.5, rely = 0.8, anchor = "center")

