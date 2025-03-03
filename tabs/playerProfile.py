import customtkinter as ctk
from settings import *
from data.database import *
from data.gamesDatabase import *
from PIL import Image
import io
from utils.teamLogo import TeamLogo
from utils.frames import FootballPitchPlayerPos

class PlayerProfile(ctk.CTkFrame):
    def __init__(self, parent, session, player, changeBackFunction = None):
        super().__init__(parent, fg_color = TKINTER_BACKGROUND, width = 1000, height = 700, corner_radius = 0)

        self.parent = parent
        self.session = session
        self.player = player
        self.changeBackFunction = changeBackFunction

        self.team = Teams.get_team_by_id(self.session, self.player.team_id)
        self.league = LeagueTeams.get_league_by_team(self.session, self.team.id)

        self.profile = Profile(self, self.session, self.player)
        self.attributes = None
        self.contract = None
        self.history = None
        self.titles = ["Profile", "Attributes", "Contract", "History"]
        self.tabs = [self.profile, self.attributes, self.contract, self.history]
        self.classNames = [Profile, Attributes, Contract, History]

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
        backButton.place(relx = 0.975, rely = 0, anchor = "ne")

    def canvas(self, width, height, relx):
        canvas = ctk.CTkCanvas(self.tabsFrame, width = width, height = height, bg = GREY_BACKGROUND, bd = 0, highlightthickness = 0)
        canvas.place(relx = relx, rely = 0, anchor = "nw")

    def changeTab(self, index):
        self.buttons[self.activeButton].configure(state = "normal")
        self.tabs[self.activeButton].pack_forget()
        
        self.activeButton = index
        self.buttons[self.activeButton].configure(state = "disabled")

        if not self.tabs[self.activeButton]:
            self.tabs[self.activeButton] = globals()[self.classNames[self.activeButton].__name__](self, self.session, self.player)

        self.tabs[self.activeButton].pack()

class Profile(ctk.CTkFrame):
    def __init__(self, parent, session, player):
        super().__init__(parent, fg_color = TKINTER_BACKGROUND, width = 1000, height = 630, corner_radius = 0) 

        self.parent = parent
        self.session = session
        self.player = player

        self.suspended = False
        self.susBan = None
        self.injured = False

        src = Image.open("Images/default_user.png")
        src.thumbnail((200, 200))
        self.photo = ctk.CTkImage(src, None, (src.width, src.height))
        ctk.CTkLabel(self, image = self.photo, text = "").place(relx = 0.05, rely = 0.05, anchor = "nw")

        ctk.CTkLabel(self, text = f"{self.player.first_name} {self.player.last_name}", font = (APP_FONT_BOLD, 40), fg_color = TKINTER_BACKGROUND).place(relx = 0.3, rely = 0.12, anchor = "w")

        flag = Image.open(io.BytesIO(self.player.flag))
        flag.thumbnail((50, 50))
        self.flag = ctk.CTkImage(flag, None, (flag.width, flag.height))
        ctk.CTkLabel(self, image = self.flag, text = "").place(relx = 0.3, rely = 0.2, anchor = "w")
        ctk.CTkLabel(self, text = self.player.nationality.capitalize(), font = (APP_FONT, 20), fg_color = TKINTER_BACKGROUND).place(relx = 0.36, rely = 0.2, anchor = "w")

        ctk.CTkLabel(self, text = f"{self.player.age} years old / {self.player.date_of_birth}", font = (APP_FONT, 20), fg_color = TKINTER_BACKGROUND).place(relx = 0.3, rely = 0.27, anchor = "w")

        playerBans = PlayerBans.get_bans_for_player(self.session, self.player.id)

        for ban in playerBans:
            if ban.ban_type == "injury":
                ctk.CTkLabel(self, text = f"Injured. Expected return in {ban.ban_length} matchday(s)", font = (APP_FONT, 20), fg_color = TKINTER_BACKGROUND).place(relx = 0.3, rely = 0.33, anchor = "w")
                self.injured = True
            else:
                self.suspended = True
                self.susBan = ban

        if not self.injured:
            ctk.CTkLabel(self, text = self.player.player_role, font = (APP_FONT, 20), fg_color = TKINTER_BACKGROUND).place(relx = 0.3, rely = 0.33, anchor = "w")

        teamLogo = Image.open(io.BytesIO(self.parent.team.logo))
        teamLogo.thumbnail((200, 200))
        self.teamLogo = TeamLogo(self, self.session, teamLogo, self.parent.team, TKINTER_BACKGROUND, 0.83, 0.22, "center", self.parent.parent)

        canvas = ctk.CTkCanvas(self, width = 1000, height = 5, bg = GREY_BACKGROUND, bd = 0, highlightthickness = 0)
        canvas.place(relx = 0.5, rely = 0.4, anchor = "center")

        self.footballPitch = FootballPitchPlayerPos(self, 400, 250, 0.2, 0.65, "center", TKINTER_BACKGROUND)
        positions = self.player.specific_positions.split(",")
        self.footballPitch.add_player_positions(positions)

        ctk.CTkLabel(self, text = self.player.position.capitalize(), font = (APP_FONT_BOLD, 20), fg_color = TKINTER_BACKGROUND).place(relx = 0.2, rely = 0.45, anchor = "center")

        self.formFrame = ctk.CTkFrame(self, fg_color = GREY_BACKGROUND, width = 520, height = 250, corner_radius = 15)
        self.formFrame.place(relx = 0.67, rely = 0.63, anchor = "center")
        ctk.CTkLabel(self.formFrame, text = "Form", font = (APP_FONT_BOLD, 30), fg_color = GREY_BACKGROUND).place(relx = 0.5, rely = 0.1, anchor = "center")

        self.statsFrame = ctk.CTkFrame(self, fg_color = GREY_BACKGROUND, width = 907, height = 75, corner_radius = 15)
        self.statsFrame.place(relx = 0.04, rely = 0.85, anchor = "nw")

        self.addStats()

    def addStats(self):

        if not self.suspended:
            ctk.CTkLabel(self.statsFrame, text = "Eclipse League stats: ", font = (APP_FONT, 20), fg_color = GREY_BACKGROUND).place(relx = 0.03, rely = 0.5, anchor = "w")
        else:
            ctk.CTkLabel(self.statsFrame, text = f"Eclipse League stats: (# for {self.susBan.ban_length} match(es))", font = (APP_FONT, 20), fg_color = GREY_BACKGROUND).place(relx = 0.03, rely = 0.5, anchor = "w")

        played = TeamLineup.get_number_matches_by_player(self.session, self.player.id, self.parent.league.league_id)
        yellowCards = MatchEvents.get_yellow_cards_by_player(self.session, self.player.id)
        redCards = MatchEvents.get_red_cards_by_player(self.session, self.player.id)
        averageRating = TeamLineup.get_player_average_rating(self.session, self.player.id, self.parent.league.league_id)

        if self.player.position != "goalkeeper":
            goals = MatchEvents.get_goals_and_pens_by_player(self.session, self.player.id)
            assists = MatchEvents.get_assists_by_player(self.session, self.player.id)
            stats = [averageRating, redCards, yellowCards, assists, goals, played]
            statsNames = ["averageRating", "redCard", "yellowCard", "assist", "goal", "played"]
        else:
            cleanSheets = MatchEvents.get_clean_sheets_by_player(self.session, self.player.id)
            savedPens = MatchEvents.get_penalty_saves_by_player(self.session, self.player.id)
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

class Attributes(ctk.CTkFrame):
    def __init__(self, parent, session, player):
        super().__init__(parent, fg_color = TKINTER_BACKGROUND, width = 1000, height = 630, corner_radius = 0) 

        self.parent = parent
        self.session = session
        self.player = player

class Contract(ctk.CTkFrame):
    def __init__(self, parent, session, player):
        super().__init__(parent, fg_color = TKINTER_BACKGROUND, width = 1000, height = 630, corner_radius = 0) 

        self.parent = parent
        self.session = session
        self.player = player

class History(ctk.CTkScrollableFrame):
    def __init__(self, parent, session, player):
        super().__init__(parent, fg_color = TKINTER_BACKGROUND, width = 965, height = 630, corner_radius = 0) 

        self.parent = parent
        self.session = session
        self.player = player