import customtkinter as ctk
from settings import *
from data.database import *
from data.gamesDatabase import *
from PIL import Image
import io
from utils.teamLogo import TeamLogo

class RefereeProfile(ctk.CTkFrame):
    def __init__(self, parent, referee, changeBackFunction = None):
        super().__init__(parent, fg_color = TKINTER_BACKGROUND, width = 1000, height = 700, corner_radius = 0)

        self.parent = parent
        self.referee = referee
        self.changeBackFunction = changeBackFunction

        self.profile = Profile(self, self.referee)
        self.titles = ["Profile"]
        self.tabs = [self.profile]
        self.classNames = [Profile]

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
            self.tabs[self.activeButton] = globals()[self.classNames[self.activeButton].__name__](self, self.referee)

        self.tabs[self.activeButton].pack()

class Profile(ctk.CTkFrame):
    def __init__(self, parent, referee):
        super().__init__(parent, fg_color = TKINTER_BACKGROUND, width = 1000, height = 630, corner_radius = 0) 

        self.parent = parent
        self.referee = referee
        self.parentTab = self.parent.parent

        src = Image.open("Images/default_user.png")
        src.thumbnail((200, 200))
        self.photo = ctk.CTkImage(src, None, (src.width, src.height))
        ctk.CTkLabel(self, image = self.photo, text = "").place(relx = 0.05, rely = 0.05, anchor = "nw")

        ctk.CTkLabel(self, text = f"{self.referee.first_name} {self.referee.last_name}", font = (APP_FONT_BOLD, 40), fg_color = TKINTER_BACKGROUND).place(relx = 0.3, rely = 0.12, anchor = "w")

        flag = Image.open(io.BytesIO(self.referee.flag))
        flag.thumbnail((50, 50))
        self.flag = ctk.CTkImage(flag, None, (flag.width, flag.height))
        ctk.CTkLabel(self, image = self.flag, text = "").place(relx = 0.3, rely = 0.2, anchor = "w")
        ctk.CTkLabel(self, text = self.referee.nationality.capitalize(), font = (APP_FONT, 20), fg_color = TKINTER_BACKGROUND).place(relx = 0.36, rely = 0.2, anchor = "w")

        ctk.CTkLabel(self, text = f"{self.referee.age} years old / {self.referee.date_of_birth}", font = (APP_FONT, 20), fg_color = TKINTER_BACKGROUND).place(relx = 0.3, rely = 0.27, anchor = "w")
        ctk.CTkLabel(self, text = "Referee", font = (APP_FONT, 20), fg_color = TKINTER_BACKGROUND).place(relx = 0.3, rely = 0.33, anchor = "w")

        canvas = ctk.CTkCanvas(self, width = 1000, height = 5, bg = GREY_BACKGROUND, bd = 0, highlightthickness = 0)
        canvas.place(relx = 0.5, rely = 0.4, anchor = "center")

        statsFrame = ctk.CTkFrame(self, fg_color = GREY_BACKGROUND, width = 750, height = 300, corner_radius = 15)
        statsFrame.place(relx = 0.5, rely = 0.7, anchor = "center")

        gamesRefereed = Matches.get_all_played_referee_matches(self.referee.id)

        if gamesRefereed:
            headerFrame = ctk.CTkFrame(statsFrame, fg_color = GREY_BACKGROUND, width = 740, height = 50, corner_radius = 15)
            headerFrame.pack(expand = True, fill = "both", pady = 5, padx = 5)

            headerFrame.grid_columnconfigure(0, weight = 5)
            headerFrame.grid_columnconfigure((1, 2), weight = 1)
            headerFrame.grid_propagate(False)

            ctk.CTkLabel(headerFrame, text = "Game", font = (APP_FONT_BOLD, 20), fg_color = GREY_BACKGROUND).grid(row = 0, column = 0, sticky = "w", padx = 10, pady = 5)

            src = Image.open("Images/yellowCard.png")
            src.thumbnail((35, 35))
            img = ctk.CTkImage(src, None, (src.width, src.height))
            ctk.CTkLabel(headerFrame, text = "", image = img, width = 20, fg_color = GREY_BACKGROUND).grid(row = 0, column = 1, pady = 5)

            src = Image.open("Images/redCard.png")
            src.thumbnail((35, 35))
            img = ctk.CTkImage(src, None, (src.width, src.height))
            ctk.CTkLabel(headerFrame, text = "", image = img, width = 20, fg_color = GREY_BACKGROUND).grid(row = 0, column = 2, pady = 5)

            if len(gamesRefereed) > 4:
                dataFrame = ctk.CTkScrollableFrame(statsFrame, fg_color = GREY_BACKGROUND, width = 720, height = 210, corner_radius = 15)
            else:
                dataFrame = ctk.CTkFrame(statsFrame, fg_color = GREY_BACKGROUND, width = 740, height = 240, corner_radius = 15)

            dataFrame.pack(expand = True, fill = "both", pady = 5, padx = 5)

            dataFrame.grid_columnconfigure(0, weight = 5)
            dataFrame.grid_columnconfigure((1, 2), weight = 1)
            
            if len(gamesRefereed) <= 4:
                dataFrame.grid_propagate(False)

            for match in gamesRefereed:
                matchFrame = ctk.CTkFrame(dataFrame, fg_color = GREY_BACKGROUND, width = 10, height = 50, corner_radius = 0)
                matchFrame.grid(row = gamesRefereed.index(match), column = 0, pady = 5, padx = 10, sticky = "ew")

                homeTeam = Teams.get_team_by_id(match.home_id)
                awayTeam = Teams.get_team_by_id(match.away_id) 

                homeSrc = Image.open(io.BytesIO(homeTeam.logo))
                homeSrc.thumbnail((35, 35))
                homeLogo = TeamLogo(matchFrame, homeSrc, homeTeam, GREY_BACKGROUND, 0.4, 0.5, "center", self.parentTab)
                ctk.CTkLabel(matchFrame, text = homeTeam.name, fg_color = GREY_BACKGROUND, font = (APP_FONT, 15)).place(relx = 0.35, rely = 0.5, anchor = "e")

                awaySrc = Image.open(io.BytesIO(awayTeam.logo))
                awaySrc.thumbnail((35, 35))
                awayLogo = TeamLogo(matchFrame, awaySrc, awayTeam, GREY_BACKGROUND, 0.6, 0.5, "center", self.parentTab)
                ctk.CTkLabel(matchFrame, text = awayTeam.name, fg_color = GREY_BACKGROUND, font = (APP_FONT, 15)).place(relx = 0.65, rely = 0.5, anchor = "w")

                text = f"{match.score_home} - {match.score_away}"
                ctk.CTkLabel(matchFrame, text = text, fg_color = GREY_BACKGROUND, font = (APP_FONT, 15)).place(relx = 0.5, rely = 0.5, anchor = "center")

                yellowCards = MatchEvents.get_event_by_type_and_match("yellow_card", match.id)
                redCards = MatchEvents.get_event_by_type_and_match("red_card", match.id)

                ctk.CTkLabel(dataFrame, text = len(yellowCards), fg_color = GREY_BACKGROUND, width = 20, font = (APP_FONT, 15)).grid(row = gamesRefereed.index(match), column = 1, pady = 5, padx = 5)
                ctk.CTkLabel(dataFrame, text = len(redCards), fg_color = GREY_BACKGROUND, width = 20, font = (APP_FONT, 15)).grid(row = gamesRefereed.index(match), column = 2, pady = 5, padx = 5)

        else:
            ctk.CTkLabel(statsFrame, text = "No games refereed yet", font = (APP_FONT, 20), fg_color = GREY_BACKGROUND).place(relx = 0.5, rely = 0.5, anchor = "center")

