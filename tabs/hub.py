import customtkinter as ctk
import tkinter.font as tkFont
from settings import *
from data.database import *
from data.gamesDatabase import Game
from PIL import Image
import io
from utils.frames import LeagueTableScrollable, next5Matches
from utils.teamLogo import TeamLogo
from utils.util_functions import *

class Hub(ctk.CTkFrame):
    def __init__(self, parent):
        """
        Class for the Hub tab in the main menu.

        Args:
            parent (ctk.CTkFrame): The parent frame (main menu) where the Hub tab will be placed.
        """

        super().__init__(parent, fg_color = TKINTER_BACKGROUND, width = 1000, height = 700, corner_radius = 0)

        self.parent = parent
        self.manager_id = Managers.get_all_user_managers()[0].id

        self.team = Teams.get_teams_by_manager(self.manager_id)[0]
        self.league = LeagueTeams.get_league_by_team(self.team.id)

        # Add the next match and the morale sections
        self.nextMatch = nextMatch(self, self.manager_id)
        self.playerMorale = PlayerMorale(self)

        # Add the league table
        self.leagueTable = LeagueTableScrollable(self, 490, 312, 0, 0.3, TKINTER_BACKGROUND, DARK_GREY, GREY_BACKGROUND, "nw", small = True)
        self.leagueTable.defineManager(self.manager_id)
        self.leagueTable.addLeagueTable()

        # Add the next 5 matches
        self.next5Matches = next5Matches(self, self.manager_id, TKINTER_BACKGROUND, 333, 600, 90, 0.67, 0.3, "nw", 0.4, self)
        self.next5Matches.showNext5Matches()

        self.addCanvas()

    def addCanvas(self):
        """
        Adds canvas lines to separate different sections in the Hub tab.
        """

        canvas = ctk.CTkCanvas(self, width = 1500, height = 5, bg = GREY_BACKGROUND, bd = 0, highlightthickness = 0)
        canvas.place(x = 0, y = 250, anchor = "nw")

        canvas = ctk.CTkCanvas(self, width = 5, height = 800, bg = GREY_BACKGROUND, bd = 0, highlightthickness = 0)
        canvas.place(x = 410, y = 250, anchor = "nw")

        canvas = ctk.CTkCanvas(self, width = 5, height = 800, bg = GREY_BACKGROUND, bd = 0, highlightthickness = 0)
        canvas.place(x = 830, y = 250, anchor = "nw")

    def changeBack(self):
        """
        Changes the background of the Hub tab and repositions the elements.
        """

        self.profile.place_forget()
         
        self.nextMatch.place(x = 0, y = 0, anchor = "nw")
        self.leagueTable.place(x = 0, y = 205, anchor = "nw")
        self.playerMorale.place(x = 333, y = 205, anchor = "nw")
        self.next5Matches.place(x = 666, y = 200, anchor = "nw")

        self.addCanvas()

    def resetMorale(self):
        """
        Resets the player morale section by re-adding the player morale information.
        """
        
        self.playerMorale.addPlayerMorale(replace = True)

class nextMatch(ctk.CTkFrame):
    def __init__(self, parent, manager_id):
        """
        Class for displaying the next match information in the Hub tab.

        Args:
            parent (ctk.CTkFrame): The parent frame (Hub tab) where the next match information will be placed.
            manager_id (str): The ID of the manager to retrieve team and match information.
        """
        
        super().__init__(parent, fg_color = TKINTER_BACKGROUND, width = 1000, height = 200, corner_radius = 0)
        self.place(x = 0, y = 0, anchor = "nw")
        
        self.parent = parent
        self.manager_id = manager_id

        self.showNextMatch()

    def showNextMatch(self, replace = False):
        """
        Displays the next match information including team logos and names.
        
        Args:
            replace (bool): If True, replaces the existing content. Defaults to False.
        """

        if replace:
            for widget in self.winfo_children():
                widget.destroy()

        ctk.CTkLabel(self, text = "VS", font = (APP_FONT_BOLD, 40), text_color = "white", fg_color = TKINTER_BACKGROUND).place(relx = 0.5, rely = 0.5, anchor = "center")

        currDate = Game.get_game_date(self.manager_id)
        gameTime = Matches.check_if_game_time(self.parent.team.id, currDate)

        if gameTime:
            nextMatch = Matches.get_match_by_team_and_date(self.parent.team.id, currDate)
        else:
            nextMatch = Matches.get_team_next_match(self.parent.team.id, currDate)

        if not nextMatch:
            ctk.CTkLabel(self, text = "No upcoming matches", font = (APP_FONT_BOLD, 20), text_color = "white", fg_color = TKINTER_BACKGROUND).place(relx = 0.5, rely = 0.5, anchor = "center")
            return

        homeTeam = Teams.get_team_by_id(nextMatch.home_id)
        awayTeam = Teams.get_team_by_id(nextMatch.away_id) 

        homeImage = Image.open(io.BytesIO(homeTeam.logo))
        homeImage.thumbnail((150, 150))
        TeamLogo(self, homeImage, homeTeam, TKINTER_BACKGROUND, 0.35, 0.5, "center", self.parent)

        awayImage = Image.open(io.BytesIO(awayTeam.logo))
        awayImage.thumbnail((150, 150))
        TeamLogo(self, awayImage, awayTeam, TKINTER_BACKGROUND, 0.65, 0.5, "center", self.parent)

        ctk.CTkLabel(self, text = homeTeam.name.split()[0], font = (APP_FONT, 33), text_color = "white", fg_color = TKINTER_BACKGROUND).place(relx = 0.15, rely = 0.4, anchor = "center")
        ctk.CTkLabel(self, text = homeTeam.name.split()[1], font = (APP_FONT_BOLD, 38), text_color = "white", fg_color = TKINTER_BACKGROUND).place(relx = 0.15, rely = 0.6, anchor = "center")
        ctk.CTkLabel(self, text = awayTeam.name.split()[0], font = (APP_FONT, 33), text_color = "white", fg_color = TKINTER_BACKGROUND).place(relx = 0.85, rely = 0.4, anchor = "center")
        ctk.CTkLabel(self, text = awayTeam.name.split()[1], font = (APP_FONT_BOLD, 38), text_color = "white", fg_color = TKINTER_BACKGROUND).place(relx = 0.85, rely = 0.6, anchor = "center")

class PlayerMorale(ctk.CTkScrollableFrame):
    def __init__(self, parent):
        """
        Class for displaying player morale information in the Hub tab.
        
        Args:
            parent (ctk.CTkFrame): The parent frame (Hub tab) where the player morale information will be placed.
        """
        
        super().__init__(parent, fg_color = TKINTER_BACKGROUND, width = 315, height = 495, corner_radius = 0, scrollbar_button_color = DARK_GREY, scrollbar_button_hover_color = GREY_BACKGROUND)
        self.place(x = 333, y = 205, anchor = "nw")

        self.parent = parent

        self.addPlayerMorale()

    def addPlayerMorale(self, replace = False):
        """
        Adds player morale information to the frame.
        
        Args:
            replace (bool): If True, replaces the existing content. Defaults to False.
        """

        if replace:
            for widget in self.winfo_children():
                widget.destroy()

        players = Players.get_all_players_by_team(self.parent.team.id, youths = False)

        for player in players:
            morale = player.morale

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

            font_first = tkFont.Font(family = APP_FONT, size = 15)
            first_name_width_px = font_first.measure(player.first_name)

            # Convert pixels to relative frame width (assuming playerFrame has fixed width)
            frame_width_px = playerFrame.winfo_reqwidth()  # or use actual width if set
            rel_offset = first_name_width_px / frame_width_px

            ctk.CTkLabel(
                playerFrame,
                text = player.first_name,
                font = (APP_FONT, 15),
                text_color = "white",
                fg_color = TKINTER_BACKGROUND
            ).place(relx = 0.05, rely = 0.15, anchor = "nw")

            ctk.CTkLabel(
                playerFrame,
                text = " " + player.last_name,
                font = (APP_FONT_BOLD, 18),
                text_color = "white",
                fg_color = TKINTER_BACKGROUND
            ).place(relx = 0.05 + rel_offset, rely = 0.15, anchor = "nw")

            ctk.CTkLabel(playerFrame, text = str(morale) + "%", font = (APP_FONT_BOLD, 13), text_color = "white", fg_color = TKINTER_BACKGROUND).place(relx = 0.7, rely = 0.5, anchor = "center")
            ctk.CTkLabel(playerFrame, image = ctk_image, text = "").place(relx = 0.9, rely = 0.5, anchor = "center")
