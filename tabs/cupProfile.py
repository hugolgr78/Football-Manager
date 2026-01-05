import customtkinter as ctk
from settings import *
from data.database import *
from data.gamesDatabase import *
from PIL import Image, ImageDraw
import io
from utils.frames import LeagueTable, MatchdayFrame, News
from utils.playerProfileLink import PlayerProfileLink
from utils.teamLogo import TeamLogo
from utils.util_functions import *

class CupProfile(ctk.CTkFrame):
    def __init__(self, parent, cup_id = None, changeBackFunction = None):
        """
        Class for the Cup Profile tab in the main menu.
        
        Args:
            parent (ctk.CTkFrame): The parent frame (main menu or other) where the Cup Profile tab will be placed.
            cup_id (str, optional): The ID of the cup to display the profile for. If None, displays the user's cup. Defaults to None.
            changeBackFunction (function, optional): Function to call when the back button is pressed. Defaults to None.
        """

        super().__init__(parent, fg_color = TKINTER_BACKGROUND, width = 1000, height = 700, corner_radius = 0)

        self.parent = parent
        self.changeBackFunction = changeBackFunction
        self.cup = Cup.get_cup_by_id(cup_id)

        ctk.CTkLabel(self, text = "Cup profile").place(relx = 0.5, rely = 0.5, anchor = "center")

        self.profile = Profile(self, self.cup)
        self.matchdays = None
        self.stages = None
        self.stats = None
        self.history = None
        self.news = None
        self.titles = ["Profile", "Matchdays", "Stages", "Stats", "News", "History"]
        self.tabs = [self.profile, self.matchdays, self.stages, self.stats, self.news, self.history]
        self.classNames = [Profile, Matchdays, Stages, Stats, News, History]

        self.activeButton = 0
        self.buttons = []

        self.tabsFrame = ctk.CTkFrame(self, fg_color = TKINTER_BACKGROUND, width = 1000, height = 50, corner_radius = 0)
        self.tabsFrame.pack(expand = True, fill = "both", padx = 10, pady = 10)

        self.createTabs()
        self.profile.pack(expand = True, fill = "both")

    def createTabs(self):
        """
        Creates the tab buttons for the League Profile tab.
        """

        self.buttonHeight = 40
        self.buttonWidth = 140
        self.button_background = TKINTER_BACKGROUND
        self.hover_background = GREY_BACKGROUND
        self.gap = 0.07

        gapCount = 0
        for i in range(len(self.tabs)):
            button = ctk.CTkButton(self.tabsFrame, text = self.titles[i], font = (APP_FONT, 18), fg_color = self.button_background, corner_radius = 0, height = self.buttonHeight, width = self.buttonWidth, hover_color = self.hover_background)
            button.place(relx = self.gap * gapCount, rely = 0, anchor = "nw")
            button.configure(command = lambda i = i: self.changeTab(i))
            
            gapCount += 2
            self.buttons.append(button)
            self.canvas(6, 55, self.gap * gapCount - 0.005)

        self.buttons[self.activeButton].configure(state = "disabled")

        ctk.CTkCanvas(self.tabsFrame, width = 1220, height = 5, bg = APP_BLUE, bd = 0, highlightthickness = 0).place(relx = 0, rely = 0.82, anchor = "w")

        if self.changeBackFunction:
            backButton = ctk.CTkButton(self.tabsFrame, text = "Back", font = (APP_FONT, 20), fg_color = TKINTER_BACKGROUND, corner_radius = 5, height = self.buttonHeight - 10, width = 80, hover_color = CLOSE_RED, command = lambda: self.changeBackFunction())
            backButton.place(relx = 0.94, rely = 0, anchor = "ne")

        # self.legendFrame = ctk.CTkFrame(self, fg_color = GREY_BACKGROUND, width = 225, height = 30, corner_radius = 0, background_corner_colors = [TKINTER_BACKGROUND, TKINTER_BACKGROUND, GREY_BACKGROUND, GREY_BACKGROUND])

        src = Image.open("Images/information.png")
        src.thumbnail((20, 20))
        img = ctk.CTkImage(src, None, (src.width, src.height))
        self.helpButton = ctk.CTkButton(self.tabsFrame, text = "", image = img, fg_color = TKINTER_BACKGROUND, hover_color = TKINTER_BACKGROUND, corner_radius = 5, height = 30, width = 30)
        self.helpButton.place(relx = 0.975, rely = 0, anchor = "ne")
        self.helpButton.bind("<Enter>", lambda e: self.showLegend(e))
        self.helpButton.bind("<Leave>", lambda e: self.legendFrame.place_forget())

        # self.legend()

    def showLegend(self, event):
        """
        Shows the legend frame when the help button is hovered over.
        
        Args:
            event: The event that triggered the function.
        """

        self.legendFrame.place(relx = 0.975, rely = 0.1, anchor = "ne")
        self.legendFrame.lift()

    def canvas(self, width, height, relx):
        """
        Creates a canvas for visual separation between tab buttons.
        
        Args:
            width (int): The width of the canvas.
            height (int): The height of the canvas.
            relx (float): The relative x position of the canvas.
        """
        
        canvas = ctk.CTkCanvas(self.tabsFrame, width = width, height = height, bg = GREY_BACKGROUND, bd = 0, highlightthickness = 0)
        canvas.place(relx = relx, rely = 0, anchor = "nw")

    def changeTab(self, index):
        """
        Changes the active tab to the specified index.
        
        Args:
            index (int): The index of the tab to switch to.
        """
        
        self.buttons[self.activeButton].configure(state = "normal")
        self.tabs[self.activeButton].pack_forget()
        
        self.activeButton = index
        self.buttons[self.activeButton].configure(state = "disabled")

        if self.tabs[self.activeButton] is None:
            if self.titles[self.activeButton] != "News":
                self.tabs[self.activeButton] = globals()[self.classNames[self.activeButton].__name__](self, self.cup)
            else:
                self.tabs[self.activeButton] = globals()[self.classNames[self.activeButton].__name__](self, comp_id = self.cup.id)

        self.tabs[self.activeButton].pack()

class Profile(ctk.CTkFrame):
    def __init__(self, parent, cup):
        """
        Class for displaying league history in the league profile.

        Args:
            parent (ctk.CTk): The parent widget (leagueProfile).
            league (League): The league object containing history information.
        """
        
        super().__init__(parent, fg_color = TKINTER_BACKGROUND, width = 1000, height = 630, corner_radius = 0) 

        self.parent = parent
        self.cup = cup

class Matchdays(ctk.CTkFrame):
    def __init__(self, parent, cup):
        """
        Class for displaying league history in the league profile.

        Args:
            parent (ctk.CTk): The parent widget (leagueProfile).
            league (League): The league object containing history information.
        """
        
        super().__init__(parent, fg_color = TKINTER_BACKGROUND, width = 1000, height = 630, corner_radius = 0) 

        self.parent = parent
        self.cup = cup

class Stages(ctk.CTkFrame):
    def __init__(self, parent, cup):
        """
        Class for displaying league history in the league profile.

        Args:
            parent (ctk.CTk): The parent widget (leagueProfile).
            league (League): The league object containing history information.
        """
        
        super().__init__(parent, fg_color = TKINTER_BACKGROUND, width = 1000, height = 630, corner_radius = 0) 

        self.parent = parent
        self.cup = cup

class Stats(ctk.CTkFrame):
    def __init__(self, parent, cup):
        """
        Class for displaying league history in the league profile.

        Args:
            parent (ctk.CTk): The parent widget (leagueProfile).
            league (League): The league object containing history information.
        """
        
        super().__init__(parent, fg_color = TKINTER_BACKGROUND, width = 1000, height = 630, corner_radius = 0) 

        self.parent = parent
        self.cup = cup

class History(ctk.CTkScrollableFrame):
    def __init__(self, parent, cup):
        """
        Class for displaying league history in the league profile.

        Args:
            parent (ctk.CTk): The parent widget (leagueProfile).
            league (League): The league object containing history information.
        """
        
        super().__init__(parent, fg_color = TKINTER_BACKGROUND, width = 965, height = 630, corner_radius = 0) 

        self.parent = parent
        self.cup = cup