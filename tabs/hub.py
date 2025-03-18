import customtkinter as ctk
from settings import *
from data.database import *
from PIL import Image
import io
from tabs.teamProfile import TeamProfile
from utils.frames import LeagueTableScrollable, next5Matches
from utils.teamLogo import TeamLogo

class Hub(ctk.CTkFrame):
    def __init__(self, parent, manager_id):
        super().__init__(parent, fg_color = TKINTER_BACKGROUND, width = 1000, height = 700, corner_radius = 0)

        self.parent = parent
        self.manager_id = manager_id

        self.team = Teams.get_teams_by_manager(self.manager_id)[0]
        self.league = LeagueTeams.get_league_by_team(self.team.id)

        self.nextMatch = nextMatch(self, self.manager_id)
        self.playerMorale = PlayerMorale(self, self.manager_id)

        self.leagueTable = LeagueTableScrollable(self, 490, 312, 0, 0.3, TKINTER_BACKGROUND, DARK_GREY, GREY_BACKGROUND, "nw", small = True)
        self.leagueTable.defineManager(self.manager_id)
        self.leagueTable.addLeagueTable()

        self.next5Matches = next5Matches(self, self.manager_id, TKINTER_BACKGROUND, 333, 600, 90, 0.67, 0.3, "nw", 0.4, self)
        self.next5Matches.showNext5Matches()

        self.addCanvas()

    def addCanvas(self):

        canvas = ctk.CTkCanvas(self, width = 1500, height = 5, bg = GREY_BACKGROUND, bd = 0, highlightthickness = 0)
        canvas.place(x = 0, y = 250, anchor = "nw")

        canvas = ctk.CTkCanvas(self, width = 5, height = 800, bg = GREY_BACKGROUND, bd = 0, highlightthickness = 0)
        canvas.place(x = 410, y = 250, anchor = "nw")

        canvas = ctk.CTkCanvas(self, width = 5, height = 800, bg = GREY_BACKGROUND, bd = 0, highlightthickness = 0)
        canvas.place(x = 830, y = 250, anchor = "nw")

    def openClubProfile(self, team):
    
        for widget in self.winfo_children():
            widget.place_forget()
        
        self.profile = TeamProfile(self.parent, team.manager_id, self.changeBack)
        self.profile.place(x = 200, y = 0, anchor = "nw")

    def changeBack(self):

        self.profile.place_forget()
         
        self.nextMatch.place(x = 0, y = 0, anchor = "nw")
        self.leagueTable.place(x = 0, y = 205, anchor = "nw")
        self.playerMorale.place(x = 333, y = 205, anchor = "nw")
        self.next5Matches.place(x = 666, y = 200, anchor = "nw")

        self.addCanvas()

    def resetMorale(self):
        self.playerMorale.addPlayerMorale(replace = True)

class nextMatch(ctk.CTkFrame):
    def __init__(self, parent, manager_id):
        super().__init__(parent, fg_color = TKINTER_BACKGROUND, width = 1000, height = 200, corner_radius = 0)
        self.place(x = 0, y = 0, anchor = "nw")
        
        self.parent = parent
        self.manager_id = manager_id

        self.showNextMatch()

    def showNextMatch(self, replace = False):

        if replace:
            for widget in self.winfo_children():
                widget.destroy()

        ctk.CTkLabel(self, text = "VS", font = (APP_FONT_BOLD, 40), text_color = "white", fg_color = TKINTER_BACKGROUND).place(relx = 0.5, rely = 0.5, anchor = "center")

        nextMatch = Matches.get_team_next_match(self.parent.team.id, self.parent.league.league_id)

        homeTeam = Teams.get_team_by_id(nextMatch.home_id)
        awayTeam = Teams.get_team_by_id(nextMatch.away_id) 

        homeImage = Image.open(io.BytesIO(homeTeam.logo))
        homeImage.thumbnail((150, 150))
        homeLogo = TeamLogo(self, homeImage, homeTeam, TKINTER_BACKGROUND, 0.35, 0.5, "center", self.parent)

        awayImage = Image.open(io.BytesIO(awayTeam.logo))
        awayImage.thumbnail((150, 150))
        awayLogo = TeamLogo(self, awayImage, awayTeam, TKINTER_BACKGROUND, 0.65, 0.5, "center", self.parent)

        ctk.CTkLabel(self, text = homeTeam.name.split()[0], font = (APP_FONT, 33), text_color = "white", fg_color = TKINTER_BACKGROUND).place(relx = 0.15, rely = 0.4, anchor = "center")
        ctk.CTkLabel(self, text = homeTeam.name.split()[1], font = (APP_FONT_BOLD, 38), text_color = "white", fg_color = TKINTER_BACKGROUND).place(relx = 0.15, rely = 0.6, anchor = "center")
        ctk.CTkLabel(self, text = awayTeam.name.split()[0], font = (APP_FONT, 33), text_color = "white", fg_color = TKINTER_BACKGROUND).place(relx = 0.85, rely = 0.4, anchor = "center")
        ctk.CTkLabel(self, text = awayTeam.name.split()[1], font = (APP_FONT_BOLD, 38), text_color = "white", fg_color = TKINTER_BACKGROUND).place(relx = 0.85, rely = 0.6, anchor = "center")

class PlayerMorale(ctk.CTkScrollableFrame):
    def __init__(self, parent, manager_id):
        super().__init__(parent, fg_color = TKINTER_BACKGROUND, width = 315, height = 495, corner_radius = 0, scrollbar_button_color = DARK_GREY, scrollbar_button_hover_color = GREY_BACKGROUND)
        self.place(x = 333, y = 205, anchor = "nw")

        self.parent = parent
        self.manager_id = manager_id

        self.addPlayerMorale()

    def addPlayerMorale(self, replace = False):

        if replace:
            for widget in self.winfo_children():
                widget.destroy()

        players = Players.get_all_players_by_team(self.parent.team.id)

        for player in players:
            morale = player.morale

            if player.player_role == "Youth Team":
                continue

            if morale > 75:
                src = "Images/morale_happy.png"
            elif morale > 25:
                src = "Images/morale_neutral.png"
            else:
                src = "Images/morale_angry.png"

            image = Image.open(src)
            image.thumbnail((25, 25))
            ctk_image = ctk.CTkImage(image, None, (image.width, image.height))

            playerFrame = ctk.CTkFrame(self, fg_color = TKINTER_BACKGROUND, width = 315, height = 35, corner_radius = 0)
            playerFrame.pack()

            ctk.CTkLabel(playerFrame, text = player.first_name + " " + player.last_name, font = (APP_FONT_BOLD, 15), text_color = "white", fg_color = TKINTER_BACKGROUND).place(relx = 0.05, rely = 0.15, anchor = "nw")
            ctk.CTkLabel(playerFrame, text = str(morale) + "%", font = (APP_FONT_BOLD, 13), text_color = "white", fg_color = TKINTER_BACKGROUND).place(relx = 0.7, rely = 0.5, anchor = "center")
            ctk.CTkLabel(playerFrame, image = ctk_image, text = "").place(relx = 0.9, rely = 0.5, anchor = "center")
