import customtkinter as ctk
import tkinter.font as tkFont
from settings import *
from data.database import Matches, Teams, LeagueTeams, PlayerBans, TeamLineup, MatchEvents
from data.gamesDatabase import *
from PIL import Image
import io
from utils.teamLogo import TeamLogo
from utils.frames import FootballPitchPlayerPos, FormGraph, PlayerMatchFrame
from utils.util_functions import *

class PlayerProfile(ctk.CTkFrame):
    def __init__(self, parent, player, changeBackFunction = None):
        super().__init__(parent, fg_color = TKINTER_BACKGROUND, width = 1000, height = 700, corner_radius = 0)

        self.parent = parent
        self.player = player
        self.changeBackFunction = changeBackFunction

        self.team = Teams.get_team_by_id(self.player.team_id)
        self.league = LeagueTeams.get_league_by_team(self.team.id)

        self.profile = Profile(self, self.player)
        self.matches = None
        self.attributes = None
        self.history = None
        self.titles = ["Profile", "Matches", "Attributes", "History"]
        self.tabs = [self.profile, self.matches, self.attributes, self.history]
        self.classNames = [Profile, MatchesTab, Attributes, History]

        self.activeButton = 0
        self.buttons = []

        self.tabsFrame = ctk.CTkFrame(self, fg_color = TKINTER_BACKGROUND, width = 1000, height = 50, corner_radius = 0)
        self.tabsFrame.pack(expand = True, fill = "both", padx = 10, pady = 10)

        self.createTabs()
        self.profile.pack(expand = True, fill = "both")

    def createTabs(self):

        self.buttonHeight = 40
        self.buttonWidth = 200
        self.button_background = TKINTER_BACKGROUND
        self.hover_background = GREY_BACKGROUND
        self.gap = 0.102

        gapCount = 0
        for i in range(len(self.tabs)):
            button = ctk.CTkButton(self.tabsFrame, text = self.titles[i], font = (APP_FONT, 20), fg_color = self.button_background, corner_radius = 0, height = self.buttonHeight, width = self.buttonWidth, hover_color = self.hover_background)
            button.place(relx = self.gap * gapCount, rely = 0, anchor = "nw")
            button.configure(command = lambda i = i: self.changeTab(i))
            
            gapCount += 2
            self.buttons.append(button)
            self.canvas(6, 55, self.gap * gapCount - 0.005)

        self.buttons[self.activeButton].configure(state = "disabled")

        ctk.CTkCanvas(self.tabsFrame, width = 1220, height = 5, bg = APP_BLUE, bd = 0, highlightthickness = 0).place(relx = 0, rely = 0.82, anchor = "w")

        backButton = ctk.CTkButton(self.tabsFrame, text = "Back", font = (APP_FONT, 20), fg_color = TKINTER_BACKGROUND, corner_radius = 5, height = self.buttonHeight - 10, width = 100, hover_color = CLOSE_RED, command = lambda: self.changeBackFunction())
        backButton.place(relx = 0.94, rely = 0, anchor = "ne")

        self.legendFrame = ctk.CTkFrame(self, fg_color = GREY_BACKGROUND, width = 225, height = 150, corner_radius = 0, background_corner_colors = [TKINTER_BACKGROUND, TKINTER_BACKGROUND, GREY_BACKGROUND, GREY_BACKGROUND])

        src = Image.open("Images/information.png")
        src.thumbnail((20, 20))
        img = ctk.CTkImage(src, None, (src.width, src.height))
        self.helpButton = ctk.CTkButton(self.tabsFrame, text = "", image = img, fg_color = TKINTER_BACKGROUND, hover_color = TKINTER_BACKGROUND, corner_radius = 5, height = 30, width = 30)
        self.helpButton.place(relx = 0.975, rely = 0, anchor = "ne")
        self.helpButton.bind("<Enter>", lambda e: self.legendFrame.place(relx = 0.96, rely = 0.05, anchor = "ne"))
        self.helpButton.bind("<Leave>", lambda e: self.legendFrame.place_forget())

        self.legend()

    def canvas(self, width, height, relx):
        canvas = ctk.CTkCanvas(self.tabsFrame, width = width, height = height, bg = GREY_BACKGROUND, bd = 0, highlightthickness = 0)
        canvas.place(relx = relx, rely = 0, anchor = "nw")

    def changeTab(self, index):
        self.buttons[self.activeButton].configure(state = "normal")
        self.tabs[self.activeButton].pack_forget()
        
        self.activeButton = index
        self.buttons[self.activeButton].configure(state = "disabled")

        if not self.tabs[self.activeButton]:
            self.tabs[self.activeButton] = globals()[self.classNames[self.activeButton].__name__](self, self.player)

        self.tabs[self.activeButton].pack()

    def legend(self):
        self.legendFrame.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight = 0)
        self.legendFrame.grid_rowconfigure((0, 2), weight = 0)
        self.legendFrame.grid_rowconfigure((1, 3), weight = 1)
        self.legendFrame.grid_propagate(False)

        ctk.CTkLabel(self.legendFrame, text = "Legend", font = (APP_FONT_BOLD, 18), fg_color = GREY_BACKGROUND).grid(row = 0, column = 0, columnspan = 6, pady = (5, 0))

        imageNames = ["played", "redCard", "yellowCard", "averageRating"]
        iconNames = ["Played", "Red Cards", "Yellow Cards", "Average Rating"]

        if self.player.position == "goalkeeper":
            imageNames.append("cleanSheet")
            iconNames.append("Clean Sheets")
            imageNames.append("saved_penalty")
            iconNames.append("Saved Penalties")
        else:
            imageNames.append("goal")
            iconNames.append("Goals")
            imageNames.append("assist")
            iconNames.append("Assists")

        # Image in columns 0 and 2, text in columns 1 and 3
        for i, (imageName, iconName) in enumerate(zip(imageNames, iconNames)):
            src = Image.open(f"Images/{imageName}.png")
            src.thumbnail((15, 15))
            icon = ctk.CTkImage(src, None, (src.width, src.height))

            ctk.CTkLabel(self.legendFrame, text = "", image = icon, fg_color = GREY_BACKGROUND).grid(row = i // 2 + 1, column = i % 2 * 2, sticky = "w", padx = (8, 0), pady = (0, 2))
            ctk.CTkLabel(self.legendFrame, text = iconName, font = (APP_FONT, 12), fg_color = GREY_BACKGROUND).grid(row = i // 2 + 1, column = i % 2 * 2 + 1, sticky = "w", padx = (8, 0), pady = (0, 2))

class Profile(ctk.CTkFrame):
    def __init__(self, parent, player):
        super().__init__(parent, fg_color = TKINTER_BACKGROUND, width = 1000, height = 630, corner_radius = 0) 

        self.parent = parent
        self.player = player

        self.suspended = False
        self.susBan = None
        self.injured = False

        src = Image.open("Images/default_user.png")
        src.thumbnail((200, 200))
        self.photo = ctk.CTkImage(src, None, (src.width, src.height))
        ctk.CTkLabel(self, image = self.photo, text = "").place(relx = 0.05, rely = 0.05, anchor = "nw")

        flag = Image.open(io.BytesIO(self.player.flag))
        flag.thumbnail((50, 50))
        self.flag = ctk.CTkImage(flag, None, (flag.width, flag.height))
        ctk.CTkLabel(self, image = self.flag, text = "").place(relx = 0.3, rely = 0.2, anchor = "w")
        ctk.CTkLabel(self, text = self.player.nationality.capitalize(), font = (APP_FONT, 20), fg_color = TKINTER_BACKGROUND).place(relx = 0.36, rely = 0.2, anchor = "w")

        ctk.CTkLabel(self, text = f"{self.player.age} years old / {self.player.date_of_birth}", font = (APP_FONT, 20), fg_color = TKINTER_BACKGROUND).place(relx = 0.3, rely = 0.27, anchor = "w")
        ctk.CTkLabel(self, text = self.player.player_role, font = (APP_FONT, 20), fg_color = TKINTER_BACKGROUND).place(relx = 0.3, rely = 0.33, anchor = "w")

        playerBans = PlayerBans.get_bans_for_player(self.player.id)

        if not playerBans:
            ctk.CTkLabel(self, text = f"{self.player.first_name} {self.player.last_name}", font = (APP_FONT_BOLD, 40), fg_color = TKINTER_BACKGROUND).place(relx = 0.3, rely = 0.12, anchor = "w")

        for ban in playerBans:
            if ban.ban_type == "injury":
                injuryLabel = ctk.CTkLabel(self, text = f"Expected return in {ban.ban_length} matchday(s)", font = (APP_FONT, 15), fg_color = TKINTER_BACKGROUND)

                src = Image.open("Images/injury.png")
                src.thumbnail((35, 35))
                img = ctk.CTkImage(src, None, (src.width, src.height))
                injuryImage = ctk.CTkLabel(self, image = img, text = "")
                injuryImage.place(relx = 0.3, rely = 0.12, anchor = "w")

                injuryImage.bind("<Enter>", lambda e: injuryLabel.place(relx = 0.32, rely = 0.07, anchor = "center"))
                injuryImage.bind("<Leave>", lambda e: injuryLabel.place_forget())

                ctk.CTkLabel(self, text = f"{self.player.first_name} {self.player.last_name}", font = (APP_FONT_BOLD, 40), fg_color = TKINTER_BACKGROUND).place(relx = 0.35, rely = 0.12, anchor = "w")
            else:
                self.suspended = True
                self.susBan = ban

        teamLogo = Image.open(io.BytesIO(self.parent.team.logo))
        teamLogo.thumbnail((200, 200))
        self.teamLogo = TeamLogo(self, teamLogo, self.parent.team, TKINTER_BACKGROUND, 0.83, 0.22, "center", self.parent.parent)

        canvas = ctk.CTkCanvas(self, width = 1000, height = 5, bg = GREY_BACKGROUND, bd = 0, highlightthickness = 0)
        canvas.place(relx = 0.5, rely = 0.4, anchor = "center")

        self.footballPitch = FootballPitchPlayerPos(self, 400, 250, 0.2, 0.65, "center", TKINTER_BACKGROUND)
        positions = self.player.specific_positions.split(",")
        self.footballPitch.add_player_positions(positions)

        ctk.CTkLabel(self, text = self.player.position.capitalize(), font = (APP_FONT_BOLD, 20), fg_color = TKINTER_BACKGROUND).place(relx = 0.2, rely = 0.45, anchor = "center")

        self.formFrame = ctk.CTkFrame(self, fg_color = GREY_BACKGROUND, width = 520, height = 250, corner_radius = 15)
        self.formFrame.place(relx = 0.67, rely = 0.63, anchor = "center")
        ctk.CTkLabel(self.formFrame, text = "Form", font = (APP_FONT_BOLD, 30), fg_color = GREY_BACKGROUND).place(relx = 0.5, rely = 0.1, anchor = "center")

        FormGraph(self.formFrame, self.player, 520, 250, 0.5, 0.6, "center", GREY_BACKGROUND)

        self.statsFrame = ctk.CTkFrame(self, fg_color = GREY_BACKGROUND, width = 907, height = 75, corner_radius = 15)
        self.statsFrame.place(relx = 0.04, rely = 0.85, anchor = "nw")

        self.addStats()

    def addStats(self):

        ctk.CTkLabel(self.statsFrame, text = "Eclipse League stats: ", font = (APP_FONT, 20), fg_color = GREY_BACKGROUND).place(relx = 0.03, rely = 0.5, anchor = "w")
        
        if self.suspended:
            src = Image.open(f"Images/redCard_{self.susBan.ban_length}.png")
            src.thumbnail((35, 35))
            img = ctk.CTkImage(src, None, (src.width, src.height))
            ctk.CTkLabel(self.statsFrame, image = img, text = "").place(relx = 0.98, rely = 0.5, anchor = "e")

        played = TeamLineup.get_number_matches_by_player(self.player.id, self.parent.league.league_id)
        yellowCards = MatchEvents.get_yellow_cards_by_player(self.player.id)
        redCards = MatchEvents.get_red_cards_by_player(self.player.id)
        averageRating = TeamLineup.get_player_average_rating(self.player.id, self.parent.league.league_id)

        if self.player.position != "goalkeeper":
            goals = MatchEvents.get_goals_and_pens_by_player(self.player.id)
            assists = MatchEvents.get_assists_by_player(self.player.id)
            stats = [averageRating, redCards, yellowCards, assists, goals, played]
            statsNames = ["averageRating", "redCard", "yellowCard", "assist", "goal", "played"]
        else:
            cleanSheets = MatchEvents.get_clean_sheets_by_player(self.player.id)
            savedPens = MatchEvents.get_penalty_saves_by_player(self.player.id)
            stats = [averageRating, cleanSheets, savedPens, redCards, yellowCards, played]
            statsNames = ["averageRating", "cleanSheet", "savedPen", "redCard", "yellowCard", "played"]

        gap = 0.08  # Define the gap between images
        initial_relx = 0.9  # Starting position from the right

        for i, (stat, statPath) in enumerate(zip(stats, statsNames)):
            src = Image.open(f"Images/{statPath}.png")
            src.thumbnail((25, 25))
            self.photo = ctk.CTkImage(src, None, (src.width, src.height))
            relx_position = initial_relx - i * gap
            ctk.CTkLabel(self.statsFrame, image = self.photo, text = "").place(relx = relx_position, rely = 0.25, anchor = "center")

            if stat != "N/A":
                stat = str(round(stat, 2))

            ctk.CTkLabel(self.statsFrame, text = stat, font = (APP_FONT, 20), fg_color = GREY_BACKGROUND).place(relx = relx_position, rely = 0.7, anchor = "center")

class MatchesTab(ctk.CTkFrame):
    def __init__(self, parent, player):
        super().__init__(parent, fg_color = TKINTER_BACKGROUND, width = 1000, height = 630, corner_radius = 0) 

        self.parent = parent
        self.player = player

        self.matchesFrame = ctk.CTkScrollableFrame(self, fg_color = TKINTER_BACKGROUND, width = 950, height = 630, corner_radius = 0)
        self.matchesFrame.pack(fill = "both", expand = True, pady = (0, 10))

        self.games = Matches.get_all_player_matches(self.player.id)

        for game in reversed(self.games):
            PlayerMatchFrame(self.matchesFrame, game, self.player, 940, 80, TKINTER_BACKGROUND, self.parent.parent)

            canvas = ctk.CTkCanvas(self.matchesFrame, width = 940, height = 5, bg = GREY_BACKGROUND, highlightthickness = 0)
            canvas.pack(fill = "x")

class Attributes(ctk.CTkFrame):
    def __init__(self, parent, player):
        super().__init__(parent, fg_color = TKINTER_BACKGROUND, width = 1000, height = 630, corner_radius = 0) 

        self.parent = parent
        self.player = player

class History(ctk.CTkScrollableFrame):
    def __init__(self, parent, player):
        super().__init__(parent, fg_color = TKINTER_BACKGROUND, width = 965, height = 630, corner_radius = 0) 

        self.parent = parent
        self.player = player