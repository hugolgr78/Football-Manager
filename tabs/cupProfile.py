import customtkinter as ctk
from settings import *
from data.database import *
from data.gamesDatabase import *
from PIL import Image, ImageDraw
import io
from utils.frames import CupRoundFrame, News, StatsFrame, CupGroupFrame, CompStats
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
        self.rounds = None
        self.knockout = None
        self.stats = None
        self.history = None
        self.news = None
        self.titles = ["Profile", "Rounds", "Knockout", "Stats", "News", "History"]
        self.tabs = [self.profile, self.rounds, self.knockout, self.stats, self.news, self.history]
        self.classNames = [Profile, Rounds, Knockout, CompStats, News, History]

        self.activeButton = 0
        self.buttons = []

        self.tabsFrame = ctk.CTkFrame(self, fg_color = TKINTER_BACKGROUND, width = 1000, height = 50, corner_radius = 0)
        self.tabsFrame.pack(expand = True, fill = "both", padx = 10, pady = 10)

        self.createTabs()
        self.profile.pack(expand = True, fill = "both")

    def createTabs(self):
        """
        Creates the tab buttons for the cup Profile tab.
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

        self.legendFrame = ctk.CTkFrame(self, fg_color = GREY_BACKGROUND, width = 225, height = 90, corner_radius = 0, background_corner_colors = [TKINTER_BACKGROUND, TKINTER_BACKGROUND, GREY_BACKGROUND, GREY_BACKGROUND])

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

    def legend(self):
        """
        Creates the legend frame for the cup profile tab.
        """

        self.legendFrame.grid_rowconfigure((0, 1, 2), weight = 0)
        self.legendFrame.grid_columnconfigure((0), weight = 0)
        self.legendFrame.grid_columnconfigure((1), weight = 1)
        self.legendFrame.grid_propagate(False)

        ctk.CTkLabel(self.legendFrame, text = "Legend", font = (APP_FONT_BOLD, 18), fg_color = GREY_BACKGROUND).grid(row = 0, column = 0, columnspan = 2, pady = (5, 0))

        canvas = ctk.CTkCanvas(self.legendFrame, width = 5, height = 200 / 14.74, bg = PIE_GREEN, bd = 0, highlightthickness = 0)
        canvas.grid(row = 1, column = 0, sticky = "w", padx = (8, 0), pady = (0, 2))
        ctk.CTkLabel(self.legendFrame, text = "Next Stage", font = (APP_FONT, 12), fg_color = GREY_BACKGROUND).grid(row = 1, column = 1, sticky = "w", padx = (8, 0), pady = (0, 2))

        canvas = ctk.CTkCanvas(self.legendFrame, width = 5, height = 200 / 14.74, bg = FRUSTRATED_COLOR, bd = 0, highlightthickness = 0)
        canvas.grid(row = 2, column = 0, sticky = "w", padx = (8, 0), pady = (0, 5))
        ctk.CTkLabel(self.legendFrame, text = "Potential Qualification", font = (APP_FONT, 12), fg_color = GREY_BACKGROUND).grid(row = 2, column = 1, sticky = "w", padx = (8, 0), pady = (0, 5))

class Profile(ctk.CTkFrame):
    def __init__(self, parent, cup):
        """
        Class for displaying the cup profile information.

        Args:
            parent (ctk.CTk): The parent widget (cupProfile).
            cup (Cup): The cup object.
        """
        
        super().__init__(parent, fg_color = TKINTER_BACKGROUND, width = 1000, height = 630, corner_radius = 0) 

        self.parent = parent
        self.cup = cup

        src = Image.open(io.BytesIO(self.cup.logo))
        src.thumbnail((100, 100))
        self.logo = ctk.CTkImage(src, None, (src.width, src.height))
        ctk.CTkLabel(self, image = self.logo, text = "", fg_color = TKINTER_BACKGROUND).place(relx = 0.08, rely = 0.1, anchor = "center")

        ctk.CTkLabel(self, text = f"{self.cup.name} - {self.cup.year}", font = (APP_FONT_BOLD, 30), fg_color = TKINTER_BACKGROUND).place(relx = 0.15, rely = 0.1, anchor = "w")

        self.statsFrame = StatsFrame(self, self.cup.id, 310, 480, GREY_BACKGROUND, 0.64, 0.2, "nw")

        self.groupsFrame = ctk.CTkScrollableFrame(self, fg_color = GREY_BACKGROUND, width = 560, height = 450, corner_radius = 15)
        self.groupsFrame.place(relx = 0.03, rely = 0.2, anchor = "nw")
        self.groupData = CupTeams.get_group_data_cup(self.cup.id, next_best = True if self.cup.next_best_playoff > 0 else False)

        for group_key, group_teams in self.groupData.items():

            if group_key == "next_best":
                ctk.CTkLabel(self.groupsFrame, text = f"Best {self.cup.promoted_per_group + 1}{getSuffix(self.cup.promoted_per_group + 1)} place teams", font = (APP_FONT_BOLD, 20), fg_color = GREY_BACKGROUND).pack(pady = 5)
                groupFrame = CupGroupFrame(self.groupsFrame, self.cup, group_teams, GREY_BACKGROUND, 550, 264, Managers.get_all_user_managers()[0].id, promoted = self.cup.next_best_playoff)
            else:
                ctk.CTkLabel(self.groupsFrame, text = f"Group {group_key}", font = (APP_FONT_BOLD, 20), fg_color = GREY_BACKGROUND).pack(pady = 5)
                groupFrame = CupGroupFrame(self.groupsFrame, self.cup, group_teams, GREY_BACKGROUND, 550, 120, Managers.get_all_user_managers()[0].id)
    
            groupFrame.pack(pady = 10, padx = 10)

class Rounds(ctk.CTkFrame):
    def __init__(self, parent, cup):
        """
        Class for displaying rounds in the cup profile.

        Args:
            parent (ctk.CTk): The parent widget (CupProfile).
            cup (Cup): The cup object.
        """
        
        super().__init__(parent, fg_color = TKINTER_BACKGROUND, width = 1000, height = 630, corner_radius = 0) 

        self.parent = parent
        self.cup = cup
        self.currentRound = self.cup.current_round
        self.parentTab = self.parent.parent

        self.roundNames = Matches.get_all_cup_rounds(self.cup.id)
        self.countFrames()    

        self.buttonsFrame = ctk.CTkFrame(self, fg_color = TKINTER_BACKGROUND, width = 980, height = 60, corner_radius = 15)
        self.buttonsFrame.place(relx = 0, rely = 0.98, anchor = "sw")

        self.createFrames()
        self.addButtons()

    def countFrames(self):
        """
        Counts the number of frames needed for the rounds.
        """
        
        self.frames = []

        totalFrames = 0
        previousMax = -1
        self.roundStrToFrameRange = {}
        for round_ in self.roundNames:
            totalFrames += self.framesPerRoundForRound(round_)
            self.roundStrToFrameRange[round_] = (previousMax + 1, totalFrames - 1)
            previousMax = totalFrames - 1

        for _ in range(totalFrames):
            self.frames.append(None)

    def framesPerRoundForRound(self, roundName):
        """
        Returns the number of frames needed for a specific round.

        Args:
            roundName (str): The name of the round.
        """

        matches = Matches.get_cup_matches_by_round(self.cup.id, str(roundName))
        totalRows = 2 + len(matches)
        return (totalRows // 12) + (1 if totalRows % 12 != 0 else 0)

    def createFrames(self):
        """
        Creates frames for each round in the cup.
        """
        
        frameIndex = 0
        for round_ in self.roundNames:
            if round_ == self.currentRound:
                matches = Matches.get_cup_matches_by_round(self.cup.id, round_)
                roundFrames = CupRoundFrame(self, matches, self.currentRound, self.parentTab, frameIndex, 980, 550, GREY_BACKGROUND, 0, 0, "nw")
                self.activeFrame = frameIndex
                self.currentRoundFrame = frameIndex

                frames = roundFrames.getFrames()
                frames[0].place(relx = 0, rely = 0, anchor = "nw")
            
            for frame in frames:
                self.frames[frame.index] = frame
                frameIndex += 1

            else:
                frameIndex += self.framesPerRoundForRound(round_)
            
    def addButtons(self):
        """
        Adds navigation buttons for rounds.
        """
        
        self.back5Button = ctk.CTkButton(self.buttonsFrame, text = "<<", font = (APP_FONT, 20), fg_color = GREY_BACKGROUND, corner_radius = 10, height = 55, width = 90, hover_color = GREY_BACKGROUND, command = lambda: self.changeFrame(-5))
        self.back5Button.place(relx = 0.05, rely = 0.5, anchor = "center")

        self.back1Button = ctk.CTkButton(self.buttonsFrame, text = "<", font = (APP_FONT, 20), fg_color = GREY_BACKGROUND, corner_radius = 10, height = 55, width = 90, hover_color = GREY_BACKGROUND, command = lambda: self.changeFrame(-1))
        self.back1Button.place(relx = 0.15, rely = 0.5, anchor = "center")

        self.currentRoundButton = ctk.CTkButton(self.buttonsFrame, text = "Current Round", font = (APP_FONT, 20), fg_color = GREY_BACKGROUND, corner_radius = 10, height = 55, width = 580, hover_color = GREY_BACKGROUND, state = "disabled", command = self.goCurrentRound)
        self.currentRoundButton.place(relx = 0.5, rely = 0.5, anchor = "center")

        self.forward1Button = ctk.CTkButton(self.buttonsFrame, text = ">", font = (APP_FONT, 20), fg_color = GREY_BACKGROUND, corner_radius = 10, height = 55, width = 90, hover_color = GREY_BACKGROUND, command = lambda: self.changeFrame(1))
        self.forward1Button.place(relx = 0.85, rely = 0.5, anchor = "center")

        self.forward5Button = ctk.CTkButton(self.buttonsFrame, text = ">>", font = (APP_FONT, 20), fg_color = GREY_BACKGROUND, corner_radius = 10, height = 55, width = 90, hover_color = GREY_BACKGROUND, command = lambda: self.changeFrame(5))
        self.forward5Button.place(relx = 0.95, rely = 0.5, anchor = "center")

    def frameIndexToRound(self, frameIndex):
        """
        Converts a frame index to its corresponding round string.

        Args:
            frameIndex (int): The index of the frame.
        """
        
        for roundStr, (minIndex, maxIndex) in self.roundStrToFrameRange.items():
            if frameIndex <= maxIndex and frameIndex >= minIndex:
                return roundStr

    def changeFrame(self, direction):
        """
        Changes the active rounds frame based on the direction.
        
        Args:
            direction (int): The direction to change the frame. Positive values move forward, negative values move backward.
        """
        
        self.frames[self.activeFrame].place_forget()
        self.activeFrame = (self.activeFrame + direction) % len(self.frames)

        if self.activeFrame == self.currentRoundFrame:
            self.currentRoundButton.configure(state = "disabled")
        else:
            self.currentRoundButton.configure(state = "normal")

        if self.frames[self.activeFrame] is None:
            round_str = self.frameIndexToRound(self.activeFrame)

            matches = Matches.get_cup_matches_by_round(self.cup.id, round_str)
            roundFrames = CupRoundFrame(self, matches, round_str, self.parentTab, self.roundStrToFrameRange[round_str][0], 980, 550, GREY_BACKGROUND, 0, 0, "nw")

            frames = roundFrames.getFrames()

            for frame in frames:
                self.frames[frame.index] = frame

        self.frames[self.activeFrame].place(relx = 0, rely = 0, anchor = "nw")

    def goCurrentRound(self):
        """
        Navigates to the current round frame.
        """
        
        if self.frames[self.activeFrame] is not None:
            self.frames[self.activeFrame].place_forget()

        self.activeFrame = self.currentRoundFrame
        self.currentRoundButton.configure(state = "disabled")
        self.frames[self.activeFrame].place(relx = 0, rely = 0, anchor = "nw")

class Knockout(ctk.CTkScrollableFrame):
    def __init__(self, parent, cup):
        super().__init__(parent, fg_color = TKINTER_BACKGROUND, width = 965, height = 630, corner_radius = 0)

        self.parent = parent
        self.cup = cup

        self.parent = parent
        self.cup = cup

        knockoutRounds = Matches.get_cup_knockout_rounds(self.cup.id)

        # Main horizontal container
        container = ctk.CTkFrame(self, fg_color = TKINTER_BACKGROUND)
        container.pack(fill = "both", expand = True)

        # Layout constants
        MATCH_HEIGHT = 70
        HALF_HEIGHT = MATCH_HEIGHT // 2
        PADY = 10
        UNIT_HEIGHT = MATCH_HEIGHT + PADY

        for round_index, knockoutRound in enumerate(knockoutRounds):
            frame_width = 965 // len(knockoutRounds)
            round_frame = ctk.CTkFrame(container, fg_color = TKINTER_BACKGROUND, width = frame_width)
            round_frame.pack(side = "left", padx = 5, anchor = "n")

            title = ctk.CTkLabel(round_frame, text = knockoutRound,font = ("Arial", 12, "bold"))
            title.pack(anchor = "n", pady = (0, 10))

            matches = Matches.get_cup_matches_by_round(self.cup.id, knockoutRound)

            # Spacer sizes grow each round
            if round_index == 0:
                space_before = 0
                space_between = 0
            else:
                unit_height = MATCH_HEIGHT + PADY + 1 if round_index == 1 else MATCH_HEIGHT + PADY + 0.5
                space_before = HALF_HEIGHT + ((2 ** (round_index - 1) - 1) * unit_height)
                space_between = (2 ** round_index - 1) * unit_height

            # Top spacer for rounds after first
            if space_before > 0:
                ctk.CTkFrame(round_frame, fg_color = TKINTER_BACKGROUND, height = space_before, width = frame_width - 10).pack()

            # ----- MATCHES -----
            for i, match in enumerate(matches):
                match_frame = self._create_match_frame(round_frame, match, frame_width - 10, height = MATCH_HEIGHT if round_index == 0 else UNIT_HEIGHT)
                match_frame.pack(pady = (0, 10) if round_index == 0 else 0)

                if i < len(matches) - 1 and space_between > 0:
                    ctk.CTkFrame(round_frame, fg_color = TKINTER_BACKGROUND, height = space_between, width = frame_width - 10).pack()

    def _create_match_frame(self, parent, match, width, height):
        matchFrame = ctk.CTkFrame(
            parent,
            fg_color = GREY_BACKGROUND,
            height = height,
            width = width,
            corner_radius = 10
        )
        matchFrame.pack_propagate(False)

        return matchFrame
    
class History(ctk.CTkScrollableFrame):
    def __init__(self, parent, cup):
        """
        Class for displaying cup history in the cup profile.

        Args:
            parent (ctk.CTk): The parent widget (CupProfile).
            cup (Cup): The cup object.
        """
        
        super().__init__(parent, fg_color = TKINTER_BACKGROUND, width = 965, height = 630, corner_radius = 0) 

        self.parent = parent
        self.cup = cup