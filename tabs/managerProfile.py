import customtkinter as ctk
from settings import *
from data.database import *
from data.gamesDatabase import *
from PIL import Image
import io
from utils.teamLogo import TeamLogo
from utils.frames import WinRatePieChart, TrophiesFrame
from utils.util_functions import *
from tabs.search import Search

class ManagerProfile(ctk.CTkFrame):
    def __init__(self, parent, manager_id = None, changeBackFunction = None):
        """
        A tab to display a manager's profile and history.
        
        Args:
            parent (ctk.CTkFrame): The parent frame (main menu or other).
            manager_id (str, optional): The ID of the manager to display. Defaults to None.
            changeBackFunction (function, optional): Function to call when the back button is pressed. Defaults to None.
        """

        super().__init__(parent, fg_color = TKINTER_BACKGROUND, width = 1000, height = 700, corner_radius = 0)

        self.parent = parent
        self.changeBackFunction = changeBackFunction
        
        if not manager_id:
            # If the manager_id is not provided, use the first user manager.
            self.manager_id = Managers.get_all_user_managers()[0].id
        else:
            self.manager_id = manager_id

        self.manager = Managers.get_manager_by_id(self.manager_id)
        team = Teams.get_teams_by_manager(self.manager_id)

        if team:
            self.team = team[0]
        else:
            self.team = None

        self.profile = Profile(self, self.manager_id)
        self.history = None
        self.titles = ["Profile", "History"]
        self.tabs = [self.profile, self.history]
        self.classNames = [Profile, History]

        self.activeButton = 0
        self.buttons = []

        self.tabsFrame = ctk.CTkFrame(self, fg_color = TKINTER_BACKGROUND, width = 1000, height = 50, corner_radius = 0)
        self.tabsFrame.pack(expand = True, fill = "both", padx = 10, pady = 10)

        self.createTabs()
        self.profile.pack(expand = True, fill = "both")

    def createTabs(self):
        """
        Create the tab buttons for navigating between different sections of the manager profile.
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

        if self.manager.user == 0:
            backButton = ctk.CTkButton(self.tabsFrame, text = "Back", font = (APP_FONT, 20), fg_color = TKINTER_BACKGROUND, corner_radius = 5, height = self.buttonHeight - 10, width = 100, hover_color = CLOSE_RED, command = lambda: self.changeBackFunction())
            backButton.place(relx = 0.975, rely = 0, anchor = "ne")

    def canvas(self, width, height, relx):
        """
        Create a canvas for visual separation between tab buttons.
        
        Args:
            width (int): The width of the canvas.
            height (int): The height of the canvas.
            relx (float): The relative x position to place the canvas.
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
            self.tabs[self.activeButton] = globals()[self.classNames[self.activeButton].__name__](self, self.manager_id)

        self.tabs[self.activeButton].pack()

class Profile(ctk.CTkFrame):
    def __init__(self, parent, manager_id):
        """
        A frame to display the profile information of a manager.
        
        Args:
            parent (ctk.CTkFrame): The parent frame (ManagerProfile).
            manager_id (str): The ID of the manager to display.
        """
        
        super().__init__(parent, fg_color = TKINTER_BACKGROUND, width = 1000, height = 630, corner_radius = 0) 

        self.parent = parent
        self.manager_id = manager_id

        user = Managers.get_all_user_managers()[0]
        if user.id == self.manager_id:
            self.parentTab = self.parent
        elif isinstance(self.parent.parent, Search):
            self.parentTab = self.parent.parent
        else:
            self.parentTab = self.parent.parent.parent

        src = Image.open("Images/default_user.png")
        src.thumbnail((200, 200))
        self.photo = ctk.CTkImage(src, None, (src.width, src.height))
        ctk.CTkLabel(self, image = self.photo, text = "").place(relx = 0.05, rely = 0.05, anchor = "nw")

        ctk.CTkLabel(self, text = f"{self.parent.manager.first_name} {self.parent.manager.last_name}", font = (APP_FONT_BOLD, 40), fg_color = TKINTER_BACKGROUND).place(relx = 0.3, rely = 0.15, anchor = "w")

        flag = Image.open(io.BytesIO(self.parent.manager.flag))
        flag.thumbnail((50, 50))
        self.flag = ctk.CTkImage(flag, None, (flag.width, flag.height))
        ctk.CTkLabel(self, image = self.flag, text = "").place(relx = 0.3, rely = 0.23, anchor = "w")
        ctk.CTkLabel(self, text = self.parent.manager.nationality.capitalize(), font = (APP_FONT, 20), fg_color = TKINTER_BACKGROUND).place(relx = 0.36, rely = 0.23, anchor = "w")

        ctk.CTkLabel(self, text = f"{self.parent.manager.age} years old / {self.parent.manager.date_of_birth}", font = (APP_FONT, 20), fg_color = TKINTER_BACKGROUND).place(relx = 0.3, rely = 0.3, anchor = "w")

        if self.parent.team:
            teamLogo = Image.open(io.BytesIO(self.parent.team.logo))
            teamLogo.thumbnail((200, 200))
            self.teamLogo = TeamLogo(self, teamLogo, self.parent.team, TKINTER_BACKGROUND, 0.83, 0.22, "center", self.parentTab)

        canvas = ctk.CTkCanvas(self, width = 1000, height = 5, bg = GREY_BACKGROUND, bd = 0, highlightthickness = 0)
        canvas.place(relx = 0.5, rely = 0.4, anchor = "center")

        self.pieChart = WinRatePieChart(self, self.parent.manager.games_played, self.parent.manager.games_won, self.parent.manager.games_lost, (3, 3), TKINTER_BACKGROUND, 0.2, 0.65, "center")

        ctk.CTkLabel(self, text = f"Games Played: {self.parent.manager.games_played}", font = (APP_FONT, 20), fg_color = TKINTER_BACKGROUND).place(relx = 0.2, rely = 0.82, anchor = "center")
        ctk.CTkLabel(self, 
                    text = 
                    f"Won: {self.parent.manager.games_won}, "
                    f"Lost: {self.parent.manager.games_lost}, "
                    f"Drawn: {self.parent.manager.games_played - self.parent.manager.games_won - self.parent.manager.games_lost}", 
                    font = (APP_FONT, 20), fg_color = TKINTER_BACKGROUND).place(relx = 0.2, rely = 0.87, anchor = "center")
        
        self.trophiesFrame = TrophiesFrame(self, self.manager_id, GREY_BACKGROUND, 550, 300, 15, 0.67, 0.7, "center", team = False)

class History(ctk.CTkScrollableFrame):
    def __init__(self, parent, manager_id):
        """
        A frame to display the history of a manager.

        Args:
            parent (ctk.CTkFrame): The parent frame (ManagerProfile).
            manager_id (str): The ID of the manager to display. 
        """
        
        super().__init__(parent, fg_color = TKINTER_BACKGROUND, width = 965, height = 630, corner_radius = 0) 

        self.parent = parent
        self.manager_id = manager_id