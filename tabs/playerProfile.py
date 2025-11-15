import customtkinter as ctk
from settings import *
from data.database import Matches, PlayerAttributes, Teams, LeagueTeams, PlayerBans, TeamLineup, MatchEvents, Players, Managers, League
from data.gamesDatabase import *
from PIL import Image
import io
from utils.teamLogo import TeamLogo
from utils.frames import FootballPitchPlayerPos, FormGraph, PlayerMatchFrame, AttributesPolygon
from utils.util_functions import *

class PlayerProfile(ctk.CTkFrame):
    def __init__(self, parent, player, changeBackFunction = None, caStars = None):
        """
        Initialize the PlayerProfile tab with multiple sub-tabs for player information.
        
        Args:
            parent (ctk.CTkFrame): The parent frame (main menu or other).
            player (Player): The player object whose profile is to be displayed.
            changeBackFunction (function, optional): Function to call when the back button is pressed. Defaults to None.
            caStars (int, optional): Current Ability star rating of the player. Defaults to None.
        """

        super().__init__(parent, fg_color = TKINTER_BACKGROUND, width = 1000, height = 700, corner_radius = 0)

        self.parent = parent
        self.player = player
        self.changeBackFunction = changeBackFunction
        self.caStars = caStars

        self.team = Teams.get_team_by_id(self.player.team_id)
        self.leagueTeams = LeagueTeams.get_league_by_team(self.team.id)
        self.league = League.get_league_by_id(self.leagueTeams.league_id)

        self.profile = Profile(self, self.player)
        self.matches = None
        self.attributes = None
        self.history = None
        self.titles = ["Profile", "Attributes", "Matches",  "History"]
        self.tabs = [self.profile, self.attributes, self.matches, self.history]
        self.classNames = [Profile, Attributes, MatchesTab, History]

        self.activeButton = 0
        self.buttons = []

        self.tabsFrame = ctk.CTkFrame(self, fg_color = TKINTER_BACKGROUND, width = 1000, height = 50, corner_radius = 0)
        self.tabsFrame.pack(expand = True, fill = "both", padx = 10, pady = 10)

        self.createTabs()
        self.profile.pack(expand = True, fill = "both")

    def createTabs(self):
        """
        Create the tab buttons for navigating between different player profile sections.
        """

        self.button_background = TKINTER_BACKGROUND
        self.hover_background = GREY_BACKGROUND
        self.buttonHeight = 40
        self.buttonWidth = 140
        self.gap = 0.07

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

        self.legendFrame = ctk.CTkFrame(self, fg_color = GREY_BACKGROUND, width = 225, height = 180, corner_radius = 0, background_corner_colors = [TKINTER_BACKGROUND, TKINTER_BACKGROUND, GREY_BACKGROUND, GREY_BACKGROUND])

        src = Image.open("Images/information.png")
        src.thumbnail((20, 20))
        img = ctk.CTkImage(src, None, (src.width, src.height))
        self.helpButton = ctk.CTkButton(self.tabsFrame, text = "", image = img, fg_color = TKINTER_BACKGROUND, hover_color = TKINTER_BACKGROUND, corner_radius = 5, height = 30, width = 30)
        self.helpButton.place(relx = 0.975, rely = 0, anchor = "ne")
        self.helpButton.bind("<Enter>", lambda e: self.showLegend(e))
        self.helpButton.bind("<Leave>", lambda e: self.legendFrame.place_forget())

        self.legend()

    def showLegend(self, event):
        """
        Show the legend frame when the help button is hovered over.
        
        Args:
            event: The event object from the hover action.
        """
        
        self.legendFrame.place(relx = 0.975, rely = 0.1, anchor = "ne")
        self.legendFrame.lift()

    def canvas(self, width, height, relx):
        """
        Create a canvas separator between tab buttons.
        
        Args:
            width (int): Width of the canvas.
            height (int): Height of the canvas.
            relx (float): Relative x position for placing the canvas.
        """
        
        canvas = ctk.CTkCanvas(self.tabsFrame, width = width, height = height, bg = GREY_BACKGROUND, bd = 0, highlightthickness = 0)
        canvas.place(relx = relx, rely = 0, anchor = "nw")

    def changeTab(self, index):
        """
        Change the active tab to the specified index.
        
        Args:
            index (int): The index of the tab to switch to.
        """
        
        self.buttons[self.activeButton].configure(state = "normal")
        self.tabs[self.activeButton].pack_forget()
        
        self.activeButton = index
        self.buttons[self.activeButton].configure(state = "disabled")

        if self.tabs[self.activeButton] is None:
            self.tabs[self.activeButton] = globals()[self.classNames[self.activeButton].__name__](self, self.player)

        self.tabs[self.activeButton].pack()

    def legend(self):
        """
        Create a legend frame that explains the icons used in the player profile.
        """
        
        self.legendFrame.grid_rowconfigure((0, 1, 2, 3, 4, 5), weight = 0)
        self.legendFrame.grid_columnconfigure((0, 2), weight = 0)
        self.legendFrame.grid_columnconfigure((1, 3), weight = 1)
        self.legendFrame.grid_propagate(False)

        ctk.CTkLabel(self.legendFrame, text = "Legend", font = (APP_FONT_BOLD, 18), fg_color = GREY_BACKGROUND).grid(row = 0, column = 0, columnspan = 4, pady = (5, 0))

        imageNames = ["played", "redCard", "yellowCard", "averageRating"]
        iconNames = ["Played", "Red Cards", "Yellow Cards", "Avg. Rating"]

        if self.player.position == "goalkeeper":
            imageNames.append("cleanSheet")
            iconNames.append("Clean Sheets")
            imageNames.append("saved_penalty")
            iconNames.append("Saved Pens")
        else:
            imageNames.append("goal")
            iconNames.append("Goals")
            imageNames.append("assist")
            iconNames.append("Assists")

        imageNames += ["morale_happy", "fitness_good", "sharpness_good"]
        iconNames += ["Morale", "Fitness", "Sharpness"]

        # Image in columns 0 and 2, text in columns 1 and 3
        for i, (imageName, iconName) in enumerate(zip(imageNames, iconNames)):
            src = Image.open(f"Images/{imageName}.png")
            src.thumbnail((15, 15))
            icon = ctk.CTkImage(src, None, (src.width, src.height))

            ctk.CTkLabel(self.legendFrame, text = "", image = icon, fg_color = GREY_BACKGROUND).grid(row = i // 2 + 1, column = i % 2 * 2, sticky = "w", padx = (8, 0), pady = (0, 2))
            ctk.CTkLabel(self.legendFrame, text = iconName, font = (APP_FONT, 12), fg_color = GREY_BACKGROUND).grid(row = i // 2 + 1, column = i % 2 * 2 + 1, sticky = "w", padx = (8, 0), pady = (0, 2))

class Profile(ctk.CTkFrame):
    def __init__(self, parent, player):
        """
        Initialize the Profile tab for displaying player information.
        
        Args:
            parent (ctk.CTkFrame): The parent frame (playerProfile).
            player (Player): The player object whose profile is to be displayed.
        """
        
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

        for ban in playerBans:
            if ban.ban_type == "injury":
                self.injured = True

                currDate = Game.get_game_date(Managers.get_all_user_managers()[0].id)
                injuryTime = ban.injury - currDate
                months = injuryTime.days // 30
                remainingDays = injuryTime.days % 30
                injuryLabel = ctk.CTkLabel(self, text = f"Expected return: {months} M, {remainingDays} D", font = (APP_FONT, 15), fg_color = TKINTER_BACKGROUND)

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

        if not self.injured:
            ctk.CTkLabel(self, text = f"{self.player.first_name} {self.player.last_name}", font = (APP_FONT_BOLD, 40), fg_color = TKINTER_BACKGROUND).place(relx = 0.3, rely = 0.12, anchor = "w")

        teamLogo = Image.open(io.BytesIO(self.parent.team.logo))
        teamLogo.thumbnail((150, 150))
        self.teamLogo = TeamLogo(self, teamLogo, self.parent.team, TKINTER_BACKGROUND, 0.83, 0.15, "center", self.parent.parent)

        if not self.parent.caStars:
            self.parent.caStars, = Players.get_players_star_ratings([self.player], self.parent.league.id).values()

        paStars, = Players.get_players_star_ratings([self.player], self.parent.league.id, CA = False).values()

        caFrame = ctk.CTkFrame(self, fg_color = TKINTER_BACKGROUND, width = 200, height = 30, corner_radius = 15)
        caFrame.place(relx = 0.83, rely = 0.3, anchor = "center")
        ctk.CTkLabel(caFrame, text = "CA", font = (APP_FONT, 15), fg_color = TKINTER_BACKGROUND).place(relx = 0.1, rely = 0.6, anchor = "center")

        ctk.CTkLabel(self, text = f"{self.player.current_ability}", font = (APP_FONT, 15), fg_color = TKINTER_BACKGROUND).place(relx = 0.95, rely = 0.3, anchor = "e")

        imageNames = star_images(self.parent.caStars)

        for i, imageName in enumerate(imageNames):
            src = Image.open(f"Images/{imageName}.png")
            src.thumbnail((25, 25))
            img = ctk.CTkImage(src, None, (src.width, src.height))
            ctk.CTkLabel(caFrame, image = img, text = "").place(relx = 0.25 + i * 0.15, rely = 0.5, anchor = "center")

        paFrame = ctk.CTkFrame(self, fg_color = TKINTER_BACKGROUND, width = 200, height = 30, corner_radius = 15)
        paFrame.place(relx = 0.83, rely = 0.36, anchor = "center")
        ctk.CTkLabel(paFrame, text = "PA", font = (APP_FONT, 15), fg_color = TKINTER_BACKGROUND).place(relx = 0.1, rely = 0.6, anchor = "center")

        ctk.CTkLabel(self, text = f"{self.player.potential_ability}", font = (APP_FONT, 15), fg_color = TKINTER_BACKGROUND).place(relx = 0.95, rely = 0.36, anchor = "e")

        imageNames = star_images(paStars)

        for i, imageName in enumerate(imageNames):
            src = Image.open(f"Images/{imageName}.png")
            src.thumbnail((25, 25))
            img = ctk.CTkImage(src, None, (src.width, src.height))
            ctk.CTkLabel(paFrame, image = img, text = "").place(relx = 0.25 + i * 0.15, rely = 0.5, anchor = "center")

        canvas = ctk.CTkCanvas(self, width = 1000, height = 5, bg = GREY_BACKGROUND, bd = 0, highlightthickness = 0)
        canvas.place(relx = 0.5, rely = 0.4, anchor = "center")

        self.footballPitch = FootballPitchPlayerPos(self, 435, 250, 0.04, 0.43, "nw", TKINTER_BACKGROUND)
        positions = self.player.specific_positions.split(",")
        self.footballPitch.add_player_positions(positions)

        self.attributesFrame = ctk.CTkFrame(self, fg_color = TKINTER_BACKGROUND, width = 350, height = 50, corner_radius = 15)
        self.attributesFrame.place(relx = 0.04, rely = 0.84, anchor = "sw")

        self.formFrame = ctk.CTkFrame(self, fg_color = GREY_BACKGROUND, width = 520, height = 250, corner_radius = 15)
        self.formFrame.place(relx = 0.67, rely = 0.43, anchor = "n")
        ctk.CTkLabel(self.formFrame, text = "Form", font = (APP_FONT_BOLD, 30), fg_color = GREY_BACKGROUND).place(relx = 0.5, rely = 0.1, anchor = "center")

        FormGraph(self.formFrame, self.player, 520, 250, 0.5, 0.6, "center", GREY_BACKGROUND)

        self.statsFrame = ctk.CTkFrame(self, fg_color = GREY_BACKGROUND, width = 907, height = 75, corner_radius = 15)
        self.statsFrame.place(relx = 0.04, rely = 0.85, anchor = "nw")

        self.addStats()
        self.addAttr()

    def addStats(self):
        """
        Add player statistics to the stats frame.
        """

        ctk.CTkLabel(self.statsFrame, text = f"{self.parent.league.name} stats: ", font = (APP_FONT, 20), fg_color = GREY_BACKGROUND).place(relx = 0.03, rely = 0.5, anchor = "w")
        
        if self.suspended:
            src = Image.open(f"Images/redCard_{self.susBan.suspension}.png")
            src.thumbnail((35, 35))
            img = ctk.CTkImage(src, None, (src.width, src.height))
            ctk.CTkLabel(self.statsFrame, image = img, text = "").place(relx = 0.98, rely = 0.5, anchor = "e")

        played = TeamLineup.get_number_matches_by_player(self.player.id, self.parent.league.id)
        yellowCards = MatchEvents.get_yellow_cards_by_player(self.player.id, comp = self.parent.league.id)
        redCards = MatchEvents.get_red_cards_by_player(self.player.id, comp = self.parent.league.id)
        averageRating = TeamLineup.get_player_average_rating(self.player.id, self.parent.league.id)

        if self.player.position != "goalkeeper":
            goals = MatchEvents.get_goals_and_pens_by_player(self.player.id, comp = self.parent.league.id)
            assists = MatchEvents.get_assists_by_player(self.player.id, comp = self.parent.league.id)
            stats = [averageRating, redCards, yellowCards, assists, goals, played]
            statsNames = ["averageRating", "redCard", "yellowCard", "assist", "goal", "played"]
        else:
            cleanSheets = MatchEvents.get_clean_sheets_by_player(self.player.id, comp = self.parent.league.id)
            savedPens = MatchEvents.get_penalty_saves_by_player(self.player.id, comp = self.parent.league.id)
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

    def addAttr(self):
        """
        Add player attributes (morale, fitness, sharpness, position) to the attributes frame.
        """
        
        morale = self.player.morale

        if morale > 75:
            src = "Images/morale_happy.png"
        elif morale > 25:
            src = "Images/morale_neutral.png"
        else:
            src = "Images/morale_angry.png"

        image = Image.open(src)
        image.thumbnail((25, 25))
        ctk_image = ctk.CTkImage(image, None, (image.width, image.height))
        ctk.CTkLabel(self.attributesFrame, image = ctk_image, text = "", fg_color = TKINTER_BACKGROUND).place(relx = 0, rely = 0.5, anchor = "w")
        ctk.CTkLabel(self.attributesFrame, text = f"{morale}%", font = (APP_FONT, 15), fg_color = TKINTER_BACKGROUND).place(relx = 0.1, rely = 0.5, anchor = "w")

        fitness = self.player.fitness

        if fitness > 75:
            src = "Images/fitness_good.png"
        elif fitness > 25:
            src = "Images/fitness_ok.png"
        else:
            src = "Images/fitness_bad.png"

        image = Image.open(src)
        image.thumbnail((25, 25))
        ctk_image = ctk.CTkImage(image, None, (image.width, image.height))
        ctk.CTkLabel(self.attributesFrame, image = ctk_image, text = "", fg_color = TKINTER_BACKGROUND).place(relx = 0.3, rely = 0.5, anchor = "w")
        ctk.CTkLabel(self.attributesFrame, text = f"{fitness}%", font = (APP_FONT, 15), fg_color = TKINTER_BACKGROUND).place(relx = 0.4, rely = 0.5, anchor = "w")

        sharpness = self.player.sharpness

        if sharpness > 75:
            src = "Images/sharpness_good.png"
        elif sharpness > 25:
            src = "Images/sharpness_ok.png"
        else:
            src = "Images/sharpness_bad.png"

        image = Image.open(src)
        image.thumbnail((25, 25))
        ctk_image = ctk.CTkImage(image, None, (image.width, image.height))
        ctk.CTkLabel(self.attributesFrame, image = ctk_image, text = "", fg_color = TKINTER_BACKGROUND).place(relx = 0.6, rely = 0.5, anchor = "w")
        ctk.CTkLabel(self.attributesFrame, text = f"{sharpness}%", font = (APP_FONT, 15), fg_color = TKINTER_BACKGROUND).place(relx = 0.7, rely = 0.5, anchor = "w")

        canvas = ctk.CTkCanvas(self.attributesFrame, width = 5, height = 40, bg = GREY_BACKGROUND, highlightthickness = 0, bd = 0)

        canvasX = 0.85 if self.player.position == "goalkeeper" else 0.84
        canvas.place(relx = canvasX, rely = 0.5, anchor = "center")

        positionCodes = {
            "goalkeeper": "GK",
            "defender": "DEF",
            "midfielder": "MID",
            "forward": "FWD"
        }

        ctk.CTkLabel(self.attributesFrame, text = positionCodes[self.player.position], font = (APP_FONT_BOLD, 18), fg_color = TKINTER_BACKGROUND).place(relx = 0.94, rely = 0.5, anchor = "center")

class Attributes(ctk.CTkFrame):
    def __init__(self, parent, player):
        """
        Initialize the Attributes tab for displaying player's attributes.
        
        Args:
            parent (ctk.CTkFrame): The parent frame (playerProfile).
            player (Player): The player object whose attributes are to be displayed.
        """
        
        super().__init__(parent, fg_color = TKINTER_BACKGROUND, width = 1000, height = 630, corner_radius = 0) 

        self.parent = parent
        self.player = player

        self.attributesFrame = ctk.CTkFrame(self, fg_color = TKINTER_BACKGROUND, width = 710, height = 300, corner_radius = 15)
        self.attributesFrame.place(relx = 0.13, rely = 0.02, anchor = "nw")

        self.technicalFrame = ctk.CTkFrame(self.attributesFrame, fg_color = TKINTER_BACKGROUND, width = 340, height = 290)
        self.technicalFrame.place(x = 5, y = 5, anchor = "nw")

        self.otherFrame = ctk.CTkFrame(self.attributesFrame, fg_color = TKINTER_BACKGROUND, width = 340, height = 290)
        self.otherFrame.place(x = 355, y = 5, anchor = "nw")

        ctk.CTkFrame(self, width = 7, height = 280, fg_color = GREY_BACKGROUND, corner_radius = 0).place(relx = 0.118, rely = 0.02, anchor = "nw")
        ctk.CTkFrame(self, width = 7, height = 280, fg_color = GREY_BACKGROUND, corner_radius = 0).place(relx = 0.85, rely = 0.02, anchor = "nw")

        if player.position != "goalkeeper":
            technical = PlayerAttributes.get_player_attributes(player.id)  
        else:
            technical = PlayerAttributes.get_keeper_attributes(player.id)
        
        mental_physical = PlayerAttributes.get_mental_attributes(player.id)

        self.addAttributes(technical, self.technicalFrame)
        self.addAttributes(mental_physical, self.otherFrame, type_ = "Mental & Physical")
        self.addPolygons(technical, mental_physical)

    def addAttributes(self, data, frame, type_ = "Technical"):
        """
        Add player attributes to the specified frame.
        
        Args:
            data (dict): Dictionary of attributes to display.
            frame (ctk.CTkFrame): The frame to add the attributes to.
            type_ (str, optional): Type of attributes (e.g., "Technical", "Mental & Physical"). Defaults to "Technical".
        """

        frame.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6, 7), weight = 0)
        frame.grid_columnconfigure((0, 1), weight = 0)

        ctk.CTkLabel(frame, text = f"{type_} Attributes", font = (APP_FONT_BOLD, 25), fg_color = TKINTER_BACKGROUND).grid(row = 0, column = 0, columnspan = 2, pady = 10)

        row = 1
        column = 0
        for i, (attr, value) in enumerate(data.items()):

            if i % 2 != 0:
                backgroundColor = GREY_BACKGROUND
            else:
                backgroundColor = TKINTER_BACKGROUND
                
            frame2 = ctk.CTkFrame(frame, fg_color = backgroundColor, width = 160, height = 30, corner_radius = 0)

            ctk.CTkLabel(frame2, text = attr.capitalize().replace('_', ' '), font = (APP_FONT, 15), fg_color = backgroundColor, height = 0).place(relx = 0.1, rely = 0.5, anchor = "w")

            if value < 5:
                textColor = "grey"
            elif value < 10:
                textColor = "white"
            elif value < 15:
                textColor = PIE_GREEN
            else:
                textColor = APP_BLUE

            ctk.CTkLabel(frame2, text = value, font = (APP_FONT, 15), fg_color = backgroundColor, text_color = textColor, height = 0).place(relx = 0.85, rely = 0.5, anchor = "e")

            if attr in CORE_ATTRIBUTES[self.player.position]:
                src = Image.open("Images/averageRating.png")
                src.thumbnail((12, 12))
                icon = ctk.CTkImage(src, None, (src.width, src.height))
                ctk.CTkLabel(frame2, image = icon, text = "", fg_color = backgroundColor, height = 0).place(relx = 0.97, rely = 0.5, anchor = "e")
            elif attr in SECONDARY_ATTRIBUTES[self.player.position]:
                src = Image.open("Images/diamond.png")
                src.thumbnail((12, 12))
                icon = ctk.CTkImage(src, None, (src.width, src.height))
                ctk.CTkLabel(frame2, image = icon, text = "", fg_color = backgroundColor, height = 0).place(relx = 0.97, rely = 0.5, anchor = "e")

            frame2.grid(row = row, column = column, padx = 10)

            if i == 6:
                row = 1
                column = 1
            else:
                row += 1    

    def addPolygons(self, technical, mental_physical):
        """
        Add attribute polygons to visualize player's strengths.
        
        Args:
            technical (dict): Technical attributes of the player.
            mental_physical (dict): Mental and physical attributes of the player.
        """

        core = {k: v for k, v in technical.items() if k in CORE_ATTRIBUTES[self.player.position]}
        sec = {k: v for k, v in technical.items() if k in SECONDARY_ATTRIBUTES[self.player.position]}

        core.update({k: v for k, v in mental_physical.items() if k in CORE_ATTRIBUTES[self.player.position]})
        sec.update({k: v for k, v in mental_physical.items() if k in SECONDARY_ATTRIBUTES[self.player.position]})


        self.corePoly = AttributesPolygon(self, core, 350, 400, TKINTER_BACKGROUND, "white")
        self.corePoly.place(relx = 0.335, rely = 0.95, anchor = "s")

        self.secPoly = AttributesPolygon(self, sec, 350, 400, TKINTER_BACKGROUND, "white")
        self.secPoly.place(relx = 0.69, rely = 0.95, anchor = "s")

class MatchesTab(ctk.CTkFrame):
    def __init__(self, parent, player):
        """
        Initialize the Matches tab for displaying player's match history.
        
        Args:
            parent (ctk.CTkFrame): The parent frame (playerProfile).
            player (Player): The player object whose match history is to be displayed.
        """
        
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

class History(ctk.CTkScrollableFrame):
    def __init__(self, parent, player):
        """
        Initialize the History tab for displaying player's history.
        
        Args:
            parent (ctk.CTkFrame): The parent frame (playerProfile).
            player (Player): The player object whose history is to be displayed.
        """
        
        super().__init__(parent, fg_color = TKINTER_BACKGROUND, width = 965, height = 630, corner_radius = 0) 

        self.parent = parent
        self.player = player