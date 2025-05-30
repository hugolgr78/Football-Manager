import customtkinter as ctk
from settings import *
from data.database import *
from data.gamesDatabase import *
from PIL import Image
import io
from utils.teamLogo import TeamLogo
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from utils.playerProfileLink import PlayerProfileLink
from utils.match import Match
from utils.refereeProfileLink import RefereeProfileLabel

class MatchFrame(ctk.CTkFrame):
    def __init__(self, parent, manager_id, match, parentFrame, matchInfoFrame, parentTab):
        super().__init__(parentFrame, fg_color = TKINTER_BACKGROUND, width = 640, height = 50, corner_radius = 5)
        self.pack(expand = True, fill = "both", padx = 10, pady = (0, 10))

        self.bind("<Enter>", lambda event: self.onFrameHover())
        self.bind("<Leave>", lambda event: self.onFrameLeave())
        self.bind("<Button-1>", lambda event: self.displayMatchInfo())

        self.parent = parent
        self.parentFrame = parentFrame
        self.manager_id = manager_id
        self.match = match
        self.matchInfoFrame = matchInfoFrame
        self.parentTab = parentTab

        self.open = False
        
        self.played = False

        self.homeTeam = Teams.get_team_by_id(self.match.home_id)
        self.awayTeam = Teams.get_team_by_id(self.match.away_id) 

        if self.homeTeam.id == self.parent.team.id:
            self.home = True
            src = Image.open(io.BytesIO(self.awayTeam.logo))
        else:
            self.home = False
            src = Image.open(io.BytesIO(self.homeTeam.logo))

        src.thumbnail((35, 35))
        self.logo = TeamLogo(self, src, self.awayTeam if self.home else self.homeTeam, TKINTER_BACKGROUND, 0.05, 0.5, "center", self.parentTab)
        self.logo.getImageLabel().bind("<Enter>", lambda event: self.onFrameHover())

        self.oponent = ctk.CTkLabel(self, text = self.awayTeam.name if self.home else self.homeTeam.name, fg_color = TKINTER_BACKGROUND, font = (APP_FONT, 15))
        self.oponent.place(relx = 0.1, rely = 0.5, anchor = "w")
        self.oponent.bind("<Enter>", lambda event: self.onFrameHover()) 
        self.oponent.bind("<Button-1>", lambda event: self.displayMatchInfo())

        self.leagueName = ctk.CTkLabel(self, text = self.parent.league.name, fg_color = TKINTER_BACKGROUND, font = (APP_FONT, 15))
        self.leagueName.place(relx = 0.45, rely = 0.5, anchor = "center")
        self.leagueName.bind("<Enter>", lambda event: self.onFrameHover())
        self.leagueName.bind("<Button-1>", lambda event: self.displayMatchInfo())

        self.time = ctk.CTkLabel(self, text = self.match.time, fg_color = TKINTER_BACKGROUND, font = (APP_FONT, 15))
        self.time.place(relx = 0.9, rely = 0.5, anchor = "e")
        self.time.bind("<Enter>", lambda event: self.onFrameHover())
        self.time.bind("<Button-1>", lambda event: self.displayMatchInfo())

        self.location = ctk.CTkLabel(self, text = "H" if self.home else "A", fg_color = TKINTER_BACKGROUND, font = (APP_FONT, 15))
        self.location.place(relx = 0.95, rely = 0.5, anchor = "e")
        self.location.bind("<Enter>", lambda event: self.onFrameHover())
        self.location.bind("<Button-1>", lambda event: self.displayMatchInfo())

        if self.parent.league.current_matchday > self.match.matchday:
            self.played = True

            text = f"{self.match.score_home} - {self.match.score_away}" if self.home else f"{self.match.score_away} - {self.match.score_home}"
            self.score = ctk.CTkLabel(self, text = text, fg_color = TKINTER_BACKGROUND, font = (APP_FONT, 15))
            self.score.place(relx = 0.73, rely = 0.5, anchor = "center")
            self.score.bind("<Enter>", lambda event: self.onFrameHover())
            self.score.bind("<Button-1>", lambda event: self.displayMatchInfo())

            if self.home:
                self.result = "W" if self.match.score_home > self.match.score_away else "D" if self.match.score_home == self.match.score_away else "L"
            else:
                self.result = "W" if self.match.score_away > self.match.score_home else "D" if self.match.score_away == self.match.score_home else "L"

            if self.result == "W":
                src = Image.open("Images/game_win.png")
            elif self.result == "D":
                src = Image.open("Images/game_draw.png")
            else:
                src = Image.open("Images/game_lose.png")

            src.thumbnail((20, 20))
            ctk_image = ctk.CTkImage(src, None, (src.width, src.height))
            self.resultLabel = ctk.CTkLabel(self, image = ctk_image, text = "", fg_color = TKINTER_BACKGROUND)
            self.resultLabel.place(relx = 0.66, rely = 0.5, anchor = "center")
            self.resultLabel.bind("<Enter>", lambda event: self.onFrameHover())
            self.resultLabel.bind("<Button-1>", lambda event: self.displayMatchInfo())

    def onFrameHover(self):
        self.configure(fg_color = DARK_GREY)
        self.logo.getImageLabel().configure(fg_color = DARK_GREY)
        self.oponent.configure(fg_color = DARK_GREY)
        self.leagueName.configure(fg_color = DARK_GREY)
        self.time.configure(fg_color = DARK_GREY)
        self.location.configure(fg_color = DARK_GREY)

        if self.played:
            self.score.configure(fg_color = DARK_GREY)
            self.resultLabel.configure(fg_color = DARK_GREY)

    def onFrameLeave(self):
        self.configure(fg_color = TKINTER_BACKGROUND)
        self.logo.getImageLabel().configure(fg_color = TKINTER_BACKGROUND)
        self.oponent.configure(fg_color = TKINTER_BACKGROUND)
        self.leagueName.configure(fg_color = TKINTER_BACKGROUND)
        self.time.configure(fg_color = TKINTER_BACKGROUND)
        self.location.configure(fg_color = TKINTER_BACKGROUND)

        if self.played:
            self.score.configure(fg_color = TKINTER_BACKGROUND)
            self.resultLabel.configure(fg_color = TKINTER_BACKGROUND)

    def displayMatchInfo(self):

        if self.open:
            return

        self.open = True

        if hasattr(self.parent, "frames"):
            parentFrames = self.parent.frames
        else:
            parentFrames = self.parentTab.frames

        for otherMatchFrame in parentFrames:
            if otherMatchFrame != self:
                otherMatchFrame.open = False

        self.scoreFrame = ctk.CTkFrame(self.matchInfoFrame, fg_color = DARK_GREY, width = 260, height = 100, corner_radius = 10)
        self.scoreFrame.place(relx = 0.5, rely = 0.02, anchor = "n")

        srcHome = Image.open(io.BytesIO(self.homeTeam.logo))
        srcHome.thumbnail((50, 50))
        homeLogo = TeamLogo(self.scoreFrame, srcHome, self.homeTeam, DARK_GREY, 0.2, 0.5, "center", self.parentTab)

        srcAway = Image.open(io.BytesIO(self.awayTeam.logo))
        srcAway.thumbnail((50, 50))
        awayLogo = TeamLogo(self.scoreFrame, srcAway, self.awayTeam, DARK_GREY, 0.8, 0.5, "center", self.parentTab)

        if self.played:
            scoreLabel = ctk.CTkLabel(self.scoreFrame, text = f"{self.match.score_home} - {self.match.score_away}", fg_color = DARK_GREY, font = (APP_FONT_BOLD, 30))
        else:
            scoreLabel = ctk.CTkLabel(self.scoreFrame, text = self.match.time, fg_color = DARK_GREY, font = (APP_FONT, 30))
        
        scoreLabel.place(relx = 0.5, rely = 0.5, anchor = "center")

        self.matchdayEvents = MatchEvents.get_events_by_match(self.match.id)
        self.homeEvents = []
        self.awayEvents = []
        if self.played:
            for event in self.matchdayEvents:
                player = Players.get_player_by_id(event.player_id)
                if player.team_id == self.homeTeam.id:
                    if event.event_type == "own_goal":
                        self.awayEvents.append(event)
                    else:
                        self.homeEvents.append(event)
                elif player.team_id == self.awayTeam.id:
                    if event.event_type == "own_goal":
                        self.homeEvents.append(event)
                    else:
                        self.awayEvents.append(event)

            # remove all asissts and clean sheets
            self.homeEvents = [event for event in self.homeEvents if event.event_type != "assist" and event.event_type != "clean_sheet" and event.event_type != "penalty_saved" and event.event_type != "penalty_miss" and event.event_type != "sub_on" and event.event_type != "sub_off"]
            self.awayEvents = [event for event in self.awayEvents if event.event_type != "assist" and event.event_type != "clean_sheet" and event.event_type != "penalty_saved" and event.event_type != "penalty_miss" and event.event_type != "sub_on" and event.event_type != "sub_off"]

            self.homeLineup = TeamLineup.get_lineup_by_match_and_team(self.match.id, self.homeTeam.id)
            self.awayLineup = TeamLineup.get_lineup_by_match_and_team(self.match.id, self.awayTeam.id)

            if (max(len(self.homeLineup), len(self.awayLineup)) * 15) + (max(len(self.homeEvents), len(self.awayEvents)) * 30) > 320:
                self.eventsAndLineupsFrame = ctk.CTkScrollableFrame(self.matchInfoFrame, fg_color = DARK_GREY, width = 235, height = 330, corner_radius = 10)
                self.eventsAndLineupsFrame.place(relx = 0.5, rely = 0.203, anchor = "n")
            else:
                self.eventsAndLineupsFrame = ctk.CTkFrame(self.matchInfoFrame, fg_color = DARK_GREY, width = 260, height = 350, corner_radius = 10)
                self.eventsAndLineupsFrame.place(relx = 0.5, rely = 0.203, anchor = "n")
                self.eventsAndLineupsFrame.pack_propagate(False)
        else:
            self.eventsAndLineupsFrame = ctk.CTkFrame(self.matchInfoFrame, fg_color = DARK_GREY, width = 260, height = 350, corner_radius = 10)
            self.eventsAndLineupsFrame.place(relx = 0.5, rely = 0.203, anchor = "n")
            self.eventsAndLineupsFrame.pack_propagate(False)

        self.otherInfoFrame = ctk.CTkFrame(self.matchInfoFrame, fg_color = DARK_GREY, width = 260, height = 100, corner_radius = 10)
        self.otherInfoFrame.place(relx = 0.5, rely = 0.98, anchor = "s")

        if self.played:
            self.matchEvents()
            self.lineups()

        self.otherInfo()

    def matchEvents(self):

        self.matchEventsFrame = ctk.CTkFrame(self.eventsAndLineupsFrame, fg_color = DARK_GREY, width = 235, height = max(len(self.homeEvents), len(self.awayEvents)) * 30)

        self.matchEventsFrame.grid_columnconfigure((0, 2, 3, 5), weight = 1)
        self.matchEventsFrame.grid_columnconfigure((1, 4), weight = 2)
        
        for i in range(max(len(self.homeEvents), len(self.awayEvents))):
            self.matchEventsFrame.grid_rowconfigure(i, weight = 1)

        self.matchEventsFrame.pack(fill = "both", pady = 5)
        self.matchEventsFrame.grid_propagate(False)

        for i, event in enumerate(self.homeEvents):

            self.addEvent(event, True, i)

        for i, event in enumerate(self.awayEvents):

            self.addEvent(event, False, i)

        if len(self.awayEvents) == 0:
            ctk.CTkLabel(self.matchEventsFrame, text = "Hello There!", fg_color = DARK_GREY, font = (APP_FONT, 10), text_color = DARK_GREY).grid(row = 0, column = 4, sticky = "e")
        elif len(self.homeEvents) == 0:
            ctk.CTkLabel(self.matchEventsFrame, text = "General Kenobi!", fg_color = DARK_GREY, font = (APP_FONT, 10), text_color = DARK_GREY).grid(row = 0, column = 1, sticky = "w")

    def addEvent(self, event, home, i):
        player = Players.get_player_by_id(event.player_id)

        if "+" in event.time:
            font = 9
        else:
            font = 10

        if home:
            ctk.CTkLabel(self.matchEventsFrame, text = event.time + "'", fg_color = DARK_GREY, font = (APP_FONT, font)).grid(row = i, column = 0, sticky = "w", padx = 5)
            ctk.CTkLabel(self.matchEventsFrame, text = player.last_name, fg_color = DARK_GREY, font = (APP_FONT, 10)).grid(row = i, column = 1, sticky = "w")
        else:
            ctk.CTkLabel(self.matchEventsFrame, text = player.last_name, fg_color = DARK_GREY, font = (APP_FONT, 10)).grid(row = i, column = 4, sticky = "e")
            ctk.CTkLabel(self.matchEventsFrame, text = event.time + "'", fg_color = DARK_GREY, font = (APP_FONT, font)).grid(row = i, column = 5, sticky = "e", padx = 5)

        if event.event_type == "goal":
            src = Image.open("Images/goal.png")
        elif event.event_type == "penalty_goal":
            src = Image.open("Images/penalty.png")
        elif event.event_type == "own_goal":
            src = Image.open("Images/ownGoal.png")
        elif event.event_type == "yellow_card":
            src = Image.open("Images/yellowCard.png")
        elif event.event_type == "red_card":
            src = Image.open("Images/redCard.png")
        elif event.event_type == "injury":
            src = Image.open("Images/injury.png")

        src.thumbnail((15, 15))
        ctk_image = ctk.CTkImage(src, None, (src.width, src.height))

        if home:
            ctk.CTkLabel(self.matchEventsFrame, image = ctk_image, text = "", fg_color = DARK_GREY).grid(row = i, column = 2, sticky = "w")
        else:
            ctk.CTkLabel(self.matchEventsFrame, image = ctk_image, text = "", fg_color = DARK_GREY).grid(row = i, column = 3, sticky = "e")

    def lineups(self):
        self.lineupFrame = ctk.CTkFrame(self.eventsAndLineupsFrame, fg_color = DARK_GREY, width = 235, height = max(len(self.homeLineup), len(self.awayLineup)) * 15)
        self.lineupFrame.grid_columnconfigure((1, 2), weight = 1)
        self.lineupFrame.grid_columnconfigure((0, 3), weight = 4)

        for i in range(max(len(self.homeLineup), len(self.awayLineup))):
            self.lineupFrame.grid_rowconfigure(i, weight = 1)

        self.lineupFrame.pack(fill = "both")
        self.lineupFrame.grid_propagate(False)

        for i, lineupEntry in enumerate(self.homeLineup):
            player = Players.get_player_by_id(lineupEntry.player_id)
            rating = lineupEntry.rating

            ctk.CTkLabel(self.lineupFrame, text = f"{player.first_name} {player.last_name}", fg_color = DARK_GREY, font = (APP_FONT, 10)).grid(row = i, column = 0, sticky = "e")
            ctk.CTkLabel(self.lineupFrame, text = rating, fg_color = DARK_GREY, font = (APP_FONT, 10)).grid(row = i, column = 1, sticky = "e", padx = (5, 10))

        for i, lineupEntry in enumerate(self.awayLineup):
            player = Players.get_player_by_id(lineupEntry.player_id)
            rating = lineupEntry.rating

            ctk.CTkLabel(self.lineupFrame, text = rating, fg_color = DARK_GREY, font = (APP_FONT, 10)).grid(row = i, column = 2, sticky = "w", padx = (10, 5))
            ctk.CTkLabel(self.lineupFrame, text = f"{player.first_name} {player.last_name}", fg_color = DARK_GREY, font = (APP_FONT, 10)).grid(row = i, column = 3, sticky = "w")

    def otherInfo(self):
        self.matchReferee = Referees.get_referee_by_id(self.match.referee_id)

        RefereeProfileLabel(self.otherInfoFrame, self.matchReferee, f"{self.matchReferee.first_name} {self.matchReferee.last_name}", "Referee: ", "", 260, 30, self.parentTab, "white", DARK_GREY, 15).place(relx = 0.03, rely = 0.13, anchor = "w")
        
        ctk.CTkLabel(self.otherInfoFrame, text = f"Stadium: {self.homeTeam.stadium}", text_color = "white", fg_color = DARK_GREY, font = (APP_FONT, 15)).place(relx = 0.03, rely = 0.38, anchor = "w")
        ctk.CTkLabel(self.otherInfoFrame, text = f"Time: {self.match.time}", text_color = "white", fg_color = DARK_GREY, font = (APP_FONT, 15)).place(relx = 0.03, rely = 0.62, anchor = "w")
        
        if self.played:
            playerOTM = TeamLineup.get_player_OTM(self.match.id)
            player = Players.get_player_by_id(playerOTM.player_id)

            ctk.CTkLabel(self.otherInfoFrame, text = f"PoTM: {player.first_name} {player.last_name}", text_color = "white", fg_color = DARK_GREY, font = (APP_FONT, 15)).place(relx = 0.03, rely = 0.88, anchor = "w")
        else:
            ctk.CTkLabel(self.otherInfoFrame, text = "PoTM: N/A", fg_color = DARK_GREY, text_color = "white", font = (APP_FONT, 15)).place(relx = 0.03, rely = 0.88, anchor = "w")

class MatchdayFrame(ctk.CTkFrame):
    def __init__(self, parent, matchday, matchdayNum, currentMatchday, parentFrame, parentTab, width, heigth, fgColor, relx, rely, anchor):
        super().__init__(parent, fg_color = fgColor, width = width, height = heigth, corner_radius = 15)
        self.place(relx = relx, rely = rely, anchor = anchor)

        self.parent = parent
        self.parentFrame = parentFrame
        self.matchday = matchday
        self.matchdayNum = matchdayNum
        self.currentMatchday = currentMatchday
        self.parentTab = parentTab

        self.relx = relx
        self.rely = rely
        self.anchor = anchor
        
        ctk.CTkLabel(self, text = f"Matchday {self.matchdayNum}", fg_color = fgColor, font = (APP_FONT_BOLD, 30)).place(relx = 0.5, rely = 0.1, anchor = "center")

        startY = 0.2
        gap = 0.08

        for i, match in enumerate(self.matchday):

            homeTeam = Teams.get_team_by_id(match.home_id)
            awayTeam = Teams.get_team_by_id(match.away_id) 

            homeSrc = Image.open(io.BytesIO(homeTeam.logo))
            homeSrc.thumbnail((35, 35))
            homeLogo = TeamLogo(self, homeSrc, homeTeam, fgColor, 0.4, startY + gap * i, "center", self.parentTab)
            ctk.CTkLabel(self, text = homeTeam.name, fg_color = fgColor, font = (APP_FONT, 20)).place(relx = 0.35, rely = startY + gap * i, anchor = "e")

            awaySrc = Image.open(io.BytesIO(awayTeam.logo))
            awaySrc.thumbnail((35, 35))
            awayLogo = TeamLogo(self, awaySrc, awayTeam, fgColor, 0.6, startY + gap * i, "center", self.parentTab)
            ctk.CTkLabel(self, text = awayTeam.name, fg_color = fgColor, font = (APP_FONT, 20)).place(relx = 0.65, rely = startY + gap * i, anchor = "w")

            if self.currentMatchday > self.matchdayNum:
                text = f"{match.score_home} - {match.score_away}"
                ctk.CTkLabel(self, text = text, fg_color = fgColor, font = (APP_FONT, 20)).place(relx = 0.5, rely = startY + gap * i, anchor = "center")
            else:
                ctk.CTkLabel(self, text = match.time, fg_color = fgColor, font = (APP_FONT, 20)).place(relx = 0.5, rely = startY + gap * i, anchor = "center")

    def placeFrame(self):
        self.place(relx = self.relx, rely = self.rely, anchor = self.anchor)

class PlayerFrame(ctk.CTkFrame):
    def __init__(self, parent, manager_id, player, parentFrame, teamSquad = True, talkFunction = None):
        super().__init__(parentFrame, fg_color = TKINTER_BACKGROUND, width = 982, height = 50, corner_radius = 5)
        self.pack(expand = True, fill = "both", padx = 10, pady = (0, 10))

        self.bind("<Enter>", lambda event: self.onFrameHover())
        self.bind("<Leave>", lambda event: self.onFrameLeave())

        self.parent = parent
        self.parentFrame = parentFrame
        self.manager_id = manager_id
        self.player = player
        self.parentTab = self.parent

        self.teamSquad = teamSquad

        if not self.teamSquad:
            self.parentTab = self.parent.parent

        self.playerNumber = ctk.CTkLabel(self, text = self.player.number, font = (APP_FONT, 20), fg_color = TKINTER_BACKGROUND)
        self.playerNumber.place(relx = 0.05, rely = 0.5, anchor = "center")
        self.playerNumber.bind("<Enter>", lambda event: self.onFrameHover())

        self.playerName = PlayerProfileLink(self, self.player, self.player.first_name + " " + self.player.last_name, "white", 0.155, 0.5, "w", TKINTER_BACKGROUND, self.parentTab)
        self.playerName.bind("<Enter>", lambda event: self.onFrameHover())

        self.playerAge = ctk.CTkLabel(self, text = self.player.age, font = (APP_FONT, 20), fg_color = TKINTER_BACKGROUND)
        self.playerAge.place(relx = 0.4655, rely = 0.5, anchor = "center")
        self.playerAge.bind("<Enter>", lambda event: self.onFrameHover())

        self.positions = self.player.specific_positions.replace(",", ", ")
        self.playerPosition = ctk.CTkLabel(self, text = self.positions, font = (APP_FONT, 15), fg_color = TKINTER_BACKGROUND)
        self.playerPosition.place(relx = 0.6, rely = 0.5, anchor = "center")
        self.playerPosition.bind("<Enter>", lambda event: self.onFrameHover())

        flag = Image.open(io.BytesIO(self.player.flag))
        flag.thumbnail((30, 30))
        flagImage = ctk.CTkImage(flag, None, (flag.width, flag.height))
        self.flagLabel = ctk.CTkLabel(self, text = "", image = flagImage, fg_color = TKINTER_BACKGROUND)
        self.flagLabel.place(relx = 0.705, rely = 0.5, anchor = "center")
        self.flagLabel.bind("<Enter>", lambda event: self.onFrameHover())

        PROGRESS_COLOR = MORALE_GREEN

        if self.player.morale <= 25:
            PROGRESS_COLOR = MORALE_RED
        elif self.player.morale <= 75:
            PROGRESS_COLOR = MORALE_YELLOW

        self.moraleSlider = ctk.CTkSlider(self, 
            fg_color = TKINTER_BACKGROUND, 
            width = 100, 
            height = 20, 
            corner_radius = 0, 
            from_ = 0, 
            to = 100,
            button_length = 0,
            button_color = PROGRESS_COLOR,
            progress_color = PROGRESS_COLOR,
            border_width = 0,
            border_color = GREY_BACKGROUND,
        )

        self.moraleSlider.set(self.player.morale)
        self.moraleSlider.configure(state = "disabled")
        self.moraleSlider.place(relx = 0.825, rely = 0.5, anchor = "center")
        self.moraleSlider.bind("<Enter>", lambda event: self.onSliderHover())
        self.moraleSlider.bind("<Leave>", lambda event: self.onSliderLeave())

        if self.teamSquad:
            src = Image.open("Images/conversation.png")
            src.thumbnail((30, 30))
            talkImage = ctk.CTkImage(src, None, (src.width, src.height))
            self.talkButton = ctk.CTkButton(self, text = "", image = talkImage, width = 20, fg_color = TKINTER_BACKGROUND, hover_color = TKINTER_BACKGROUND, command = lambda: talkFunction(player))
            self.talkButton.place(relx = 0.93, rely = 0.5, anchor = "center")
            self.talkButton.bind("<Enter>", lambda event: self.onFrameHover())

    def onFrameHover(self):
        self.configure(fg_color = DARK_GREY)
        self.playerNumber.configure(fg_color = DARK_GREY)
        self.playerName.configure(fg_color = DARK_GREY)
        self.playerAge.configure(fg_color = DARK_GREY)
        self.playerPosition.configure(fg_color = DARK_GREY)
        self.flagLabel.configure(fg_color = DARK_GREY)

        if self.teamSquad:
            self.talkButton.configure(fg_color = DARK_GREY)

    def onSliderHover(self):
        self.onFrameHover()

        self.moraleLabel = ctk.CTkLabel(self, text = f"{self.moraleSlider.get()}%", fg_color = DARK_GREY, width = 5, height = 5)
        self.moraleLabel.place(relx = 0.75, rely = 0.5, anchor = "center")

    def onSliderLeave(self):
        self.onFrameHover()
        self.moraleLabel.place_forget()

    def onFrameLeave(self):
        self.configure(fg_color = TKINTER_BACKGROUND)
        self.playerNumber.configure(fg_color = TKINTER_BACKGROUND)
        self.playerName.configure(fg_color = TKINTER_BACKGROUND)
        self.playerAge.configure(fg_color = TKINTER_BACKGROUND)
        self.playerPosition.configure(fg_color = TKINTER_BACKGROUND)
        self.flagLabel.configure(fg_color = TKINTER_BACKGROUND)

        if self.teamSquad:
            self.talkButton.configure(fg_color = TKINTER_BACKGROUND)

    def disableTalkButton(self):
        self.talkButton.configure(state = "disabled")

    def enableTalkButton(self):
        self.talkButton.configure(state = "normal")

    def updateMorale(self, moraleChange):
        currMorale = self.moraleSlider.get()
        newMorale = currMorale + moraleChange

        PROGRESS_COLOR = MORALE_GREEN

        if newMorale <= 25:
            PROGRESS_COLOR = MORALE_RED
        elif newMorale <= 75:
            PROGRESS_COLOR = MORALE_YELLOW

        self.moraleSlider.set(newMorale)
        self.moraleSlider.configure(progress_color = PROGRESS_COLOR, button_color = PROGRESS_COLOR)

class LeagueTableScrollable(ctk.CTkScrollableFrame):
    def __init__(self, parent, height, width, x, y, fg_color, scrollbar_button_color, scrollbar_button_hover_color, anchor, textColor = "white", small = False, highlightManaged = False):
        super().__init__(parent, fg_color = fg_color, width = width, height = height, corner_radius = 0, scrollbar_button_color = scrollbar_button_color, scrollbar_button_hover_color = scrollbar_button_hover_color)
        self.place(relx = x, rely = y, anchor = anchor)

        self.parent = parent
        self.fgColor = fg_color
        self.textColor = textColor
        self.small = small
        self.highlightManaged = highlightManaged

        self.grid_columnconfigure(0, weight = 3)
        self.grid_columnconfigure(1, weight = 4)
        self.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23), weight = 1)
        if self.small:
            self.grid_columnconfigure(2, weight = 10)
            self.grid_columnconfigure((3, 4, 5), weight = 1)

            ctk.CTkLabel(self, text = "GD", fg_color = self.fgColor, text_color = self.textColor, font = (APP_FONT_BOLD, 12), height = 5).grid(row = 0, column = 4, pady = (5, 0))
            ctk.CTkLabel(self, text = "P", fg_color = self.fgColor, text_color = self.textColor, font = (APP_FONT_BOLD, 12), height = 5, width = 5).grid(row = 0, column = 5, pady = (5, 0))
        else:
            self.grid_columnconfigure((2, 3, 4, 5, 6, 7, 8, 9, 10), weight = 1)
            self.grid_propagate(False)

            ctk.CTkLabel(self, text = "W", fg_color = self.fgColor, text_color = self.textColor, font = (APP_FONT_BOLD, 12), height = 5).grid(row = 0, column = 4, pady = (5, 0))
            ctk.CTkLabel(self, text = "D", fg_color = self.fgColor, text_color = self.textColor, font = (APP_FONT_BOLD, 12), height = 5).grid(row = 0, column = 5, pady = (5, 0))
            ctk.CTkLabel(self, text = "L", fg_color = self.fgColor, text_color = self.textColor, font = (APP_FONT_BOLD, 12), height = 5).grid(row = 0, column = 6, pady = (5, 0))
            ctk.CTkLabel(self, text = "GF", fg_color = self.fgColor, text_color = self.textColor, font = (APP_FONT_BOLD, 12), height = 5).grid(row = 0, column = 7, pady = (5, 0))
            ctk.CTkLabel(self, text = "GA", fg_color = self.fgColor, text_color = self.textColor, font = (APP_FONT_BOLD, 12), height = 5).grid(row = 0, column = 8, pady = (5, 0))
            ctk.CTkLabel(self, text = "GD", fg_color = self.fgColor, text_color = self.textColor, font = (APP_FONT_BOLD, 12), height = 5).grid(row = 0, column = 9, pady = (5, 0))
            ctk.CTkLabel(self, text = "P", fg_color = self.fgColor, text_color = self.textColor, font = (APP_FONT_BOLD, 12), height = 5, width = 5).grid(row = 0, column = 10, pady = (5, 0))

        ctk.CTkLabel(self, text = "#", fg_color = self.fgColor, text_color = self.textColor, height = 5).grid(row = 0, column = 0, sticky = "e", pady = (10, 5))
        ctk.CTkLabel(self, text = "Team", fg_color = self.fgColor, text_color = self.textColor, font = (APP_FONT_BOLD, 12), height = 5).grid(row = 0, column = 2, sticky = "w", pady = (5, 0))
        ctk.CTkLabel(self, text = "GP", fg_color = self.fgColor, text_color = self.textColor, font = (APP_FONT_BOLD, 12), height = 5).grid(row = 0, column = 3, pady = (5, 0))

    def defineManager(self, manager_id):
        self.manager_id = manager_id
        self.team = Teams.get_teams_by_manager(self.manager_id)[0]
        self.league = LeagueTeams.get_league_by_team(self.team.id)

    def addLeagueTable(self):

        teamsData = LeagueTeams.get_teams_by_position(self.league.league_id)

        for i, team in enumerate(teamsData):
            teamName = Teams.get_team_by_id(team.team_id)
            team_logo_blob = teamName.logo
            team_image = Image.open(io.BytesIO(team_logo_blob))
            team_image.thumbnail((20, 20))
            ctk_team_image = ctk.CTkImage(team_image, None, (team_image.width, team_image.height))

            if self.highlightManaged and self.team.name == teamName.name:    
                font = (APP_FONT_BOLD, 12)
            else:
                font = (APP_FONT, 12)

            ctk.CTkLabel(self, text = i + 1, fg_color = self.fgColor, text_color = self.textColor, font = font).grid(row = i + 1, column = 0, sticky = "e")
            ctk.CTkLabel(self, image = ctk_team_image, text = "", fg_color = self.fgColor).grid(row = i + 1, column = 1)
            ctk.CTkLabel(self, text = teamName.name, fg_color = self.fgColor, text_color = self.textColor, font = font).grid(row = i + 1, column = 2, sticky = "w")
            ctk.CTkLabel(self, text = team.games_won + team.games_lost + team.games_drawn, fg_color = self.fgColor, text_color = self.textColor, font = font).grid(row = i + 1, column = 3)
            if self.small:
                ctk.CTkLabel(self, text = team.goals_scored - team.goals_conceded, fg_color = self.fgColor, text_color = self.textColor, font = font).grid(row = i + 1, column = 4)
                ctk.CTkLabel(self, text = team.points, fg_color = self.fgColor, text_color = self.textColor, font = font).grid(row = i + 1, column = 5)
            else:
                ctk.CTkLabel(self, text = team.games_won, fg_color = self.fgColor, text_color = self.textColor, height = 5, font = font).grid(row = i + 1, column = 4)
                ctk.CTkLabel(self, text = team.games_drawn, fg_color = self.fgColor, text_color = self.textColor, height = 5, font = font).grid(row = i + 1, column = 5)
                ctk.CTkLabel(self, text = team.games_lost, fg_color = self.fgColor, text_color = self.textColor, height = 5, font = font).grid(row = i + 1, column = 6)
                ctk.CTkLabel(self, text = team.goals_scored, fg_color = self.fgColor, text_color = self.textColor, height = 5, font = font).grid(row = i + 1, column = 7)
                ctk.CTkLabel(self, text = team.goals_conceded, fg_color = self.fgColor, text_color = self.textColor, height = 5, font = font).grid(row = i + 1, column = 8)
                ctk.CTkLabel(self, text = team.goals_scored - team.goals_conceded, fg_color = self.fgColor, text_color = self.textColor, height = 5, font = font).grid(row = i + 1, column = 9)
                ctk.CTkLabel(self, text = team.points, fg_color = self.fgColor, text_color = self.textColor, height = 5, font = font).grid(row = i + 1, column = 10)

class LeagueTable(ctk.CTkFrame):
    def __init__(self, parent, height, width, x, y, fg_color, anchor, textColor = "white", small = False, highlightManaged = False, corner_radius = 0):
        super().__init__(parent, fg_color = fg_color, width = width, height = height, corner_radius = corner_radius)
        self.place(relx = x, rely = y, anchor = anchor)

        self.height = height
        self.parent = parent
        self.fgColor = fg_color
        self.small = small
        self.highlightManaged = highlightManaged    
        self.textColor = textColor

        self.grid_columnconfigure(0, weight = 1)
        self.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23), weight = 1)
        if self.small:
            self.grid_columnconfigure(1, weight = 3)
            self.grid_columnconfigure(2, weight = 10)
            self.grid_columnconfigure((3, 4, 5), weight = 1)

            ctk.CTkLabel(self, text = "GD", fg_color = self.fgColor, text_color = self.textColor, font = (APP_FONT_BOLD, 12), height = 5).grid(row = 0, column = 4, pady = (5, 0))
            ctk.CTkLabel(self, text = "P", fg_color = self.fgColor, text_color = self.textColor, font = (APP_FONT_BOLD, 12), height = 5, width = 5).grid(row = 0, column = 5, pady = (5, 0))

            ctk.CTkLabel(self, text = "#", fg_color = self.fgColor, text_color = self.textColor, height = 5).grid(row = 0, column = 0, sticky = "e", pady = (10, 5))
            ctk.CTkLabel(self, text = "Team", fg_color = self.fgColor, text_color = self.textColor, font = (APP_FONT_BOLD, 12), height = 5).grid(row = 0, column = 2, sticky = "w", pady = (5, 0))
            ctk.CTkLabel(self, text = "GP", fg_color = self.fgColor, text_color = self.textColor, font = (APP_FONT_BOLD, 12), height = 5).grid(row = 0, column = 3, pady = (5, 0))
        else:
            self.grid_columnconfigure(1, weight = 1)
            self.grid_columnconfigure(2, weight = 1)
            self.grid_columnconfigure(3, weight = 3)
            self.grid_columnconfigure((4, 5, 6, 7, 8, 9, 10, 11), weight = 1)
            self.grid_propagate(False)

            ctk.CTkLabel(self, text = "W", fg_color = self.fgColor, text_color = self.textColor, font = (APP_FONT_BOLD, 12), height = 5).grid(row = 0, column = 5, pady = (5, 0))
            ctk.CTkLabel(self, text = "D", fg_color = self.fgColor, text_color = self.textColor, font = (APP_FONT_BOLD, 12), height = 5).grid(row = 0, column = 6, pady = (5, 0))
            ctk.CTkLabel(self, text = "L", fg_color = self.fgColor, text_color = self.textColor, font = (APP_FONT_BOLD, 12), height = 5).grid(row = 0, column = 7, pady = (5, 0))
            ctk.CTkLabel(self, text = "GF", fg_color = self.fgColor, text_color = self.textColor, font = (APP_FONT_BOLD, 12), height = 5).grid(row = 0, column = 8, pady = (5, 0))
            ctk.CTkLabel(self, text = "GA", fg_color = self.fgColor, text_color = self.textColor, font = (APP_FONT_BOLD, 12), height = 5).grid(row = 0, column = 9, pady = (5, 0))
            ctk.CTkLabel(self, text = "GD", fg_color = self.fgColor, text_color = self.textColor, font = (APP_FONT_BOLD, 12), height = 5).grid(row = 0, column = 10, pady = (5, 0))
            ctk.CTkLabel(self, text = "P", fg_color = self.fgColor, text_color = self.textColor, font = (APP_FONT_BOLD, 12), height = 5, width = 5).grid(row = 0, column = 11, pady = (5, 0))

            ctk.CTkLabel(self, text = "#", fg_color = self.fgColor, text_color = self.textColor, height = 5).grid(row = 0, column = 1, sticky = "w", pady = (10, 5))
            ctk.CTkLabel(self, text = "Team", fg_color = self.fgColor, text_color = self.textColor, font = (APP_FONT_BOLD, 12), height = 5).grid(row = 0, column = 3, sticky = "w", pady = (5, 0))
            ctk.CTkLabel(self, text = "GP", fg_color = self.fgColor, text_color = self.textColor, font = (APP_FONT_BOLD, 12), height = 5).grid(row = 0, column = 4, pady = (5, 0))

        self.grid_propagate(False)

    def defineManager(self, manager_id):
        self.manager_id = manager_id
        self.team = Teams.get_teams_by_manager(self.manager_id)[0]
        self.league = LeagueTeams.get_league_by_team(self.team.id)
        self.leagueData = League.get_league_by_id(self.league.league_id)

    def addLeagueTable(self):

        teamsData = LeagueTeams.get_teams_by_position(self.league.league_id)

        for i, team in enumerate(teamsData):
            teamName = Teams.get_team_by_id(team.team_id)
            team_logo_blob = teamName.logo
            team_image = Image.open(io.BytesIO(team_logo_blob))
            team_image.thumbnail((20, 20))
            ctk_team_image = ctk.CTkImage(team_image, None, (team_image.width, team_image.height))

            if self.highlightManaged and self.team.name == teamName.name:    
                font = (APP_FONT_BOLD, 12)
            else:
                font = (APP_FONT, 12)

            
            if self.small:
                ctk.CTkLabel(self, text = team.goals_scored - team.goals_conceded, fg_color = self.fgColor, text_color = self.textColor, font = font).grid(row = i + 1, column = 4)
                ctk.CTkLabel(self, text = team.points, fg_color = self.fgColor, text_color = self.textColor, font = font).grid(row = i + 1, column = 5)

                ctk.CTkLabel(self, text = i + 1, fg_color = self.fgColor, text_color = self.textColor, font = font).grid(row = i + 1, column = 0, sticky = "e")
                ctk.CTkLabel(self, image = ctk_team_image, text = "", fg_color = self.fgColor).grid(row = i + 1, column = 1)
                ctk.CTkLabel(self, text = teamName.name, fg_color = self.fgColor, text_color = self.textColor, font = font).grid(row = i + 1, column = 2, sticky = "w")
                ctk.CTkLabel(self, text = team.games_won + team.games_lost + team.games_drawn, fg_color = self.fgColor, text_color = self.textColor, font = font).grid(row = i + 1, column = 3)
            else:

                if i < self.leagueData.promotion:
                    canvas = ctk.CTkCanvas(self, width = 5, height = self.height / 14.74, bg = PIE_GREEN, bd = 0, highlightthickness = 0)
                    canvas.grid(row = i + 1, column = 0)
                elif i + 1 > 20 - self.leagueData.relegation:
                    canvas = ctk.CTkCanvas(self, width = 5, height = self.height / 14.74, bg = PIE_RED, bd = 0, highlightthickness = 0)
                    canvas.grid(row = i + 1, column = 0)

                ctk.CTkLabel(self, text = i + 1, fg_color = self.fgColor, text_color = self.textColor, font = font).grid(row = i + 1, column = 1, sticky = "w")
                ctk.CTkLabel(self, image = ctk_team_image, text = "", fg_color = self.fgColor).grid(row = i + 1, column = 2, sticky = "w")
                ctk.CTkLabel(self, text = teamName.name, fg_color = self.fgColor, text_color = self.textColor, font = font).grid(row = i + 1, column = 3, sticky = "w")
                
                ctk.CTkLabel(self, text = team.games_won + team.games_lost + team.games_drawn, fg_color = self.fgColor, text_color = self.textColor, font = font).grid(row = i + 1, column = 4)
                ctk.CTkLabel(self, text = team.games_won, fg_color = self.fgColor, text_color = self.textColor, height = 5, font = font).grid(row = i + 1, column = 5)
                ctk.CTkLabel(self, text = team.games_drawn, fg_color = self.fgColor, text_color = self.textColor, height = 5, font = font).grid(row = i + 1, column = 6)
                ctk.CTkLabel(self, text = team.games_lost, fg_color = self.fgColor, text_color = self.textColor, height = 5, font = font).grid(row = i + 1, column = 7)
                ctk.CTkLabel(self, text = team.goals_scored, fg_color = self.fgColor, text_color = self.textColor, height = 5, font = font).grid(row = i + 1, column = 8)
                ctk.CTkLabel(self, text = team.goals_conceded, fg_color = self.fgColor, text_color = self.textColor, height = 5, font = font).grid(row = i + 1, column = 9)
                ctk.CTkLabel(self, text = team.goals_scored - team.goals_conceded, fg_color = self.fgColor, text_color = self.textColor, height = 5, font = font).grid(row = i + 1, column = 10)
                ctk.CTkLabel(self, text = team.points, fg_color = self.fgColor, text_color = self.textColor, height = 5, font = font).grid(row = i + 1, column = 11)

    def clearTable(self):
        for widget in self.winfo_children():
            if widget.grid_info()["row"] > 0:
                widget.destroy()

class next5Matches(ctk.CTkFrame):
    def __init__(self, parent, manager_id, fg_color, width, height, frameHeight, relx, rely, anchor, textY, parentTab, corner_radius = 0):
        super().__init__(parent, fg_color = fg_color, width = width, height = height, corner_radius = corner_radius)
        self.place(relx = relx, rely = rely, anchor = anchor)

        self.parent = parent
        self.manager_id = manager_id
        self.fgColor = fg_color
        self.width = width
        self.frameHeight = frameHeight
        self.textY = textY
        self.parentTab = parentTab
        self.corner_radius = corner_radius

        self.pack_propagate(False)

        self.team = Teams.get_teams_by_manager(self.manager_id)[0]
        self.league = LeagueTeams.get_league_by_team(self.team.id)

    def showNext5Matches(self):

        next5 = Matches.get_team_next_5_matches(self.team.id, self.league.league_id)

        ctk.CTkLabel(self, text = "Next 5 Matches", font = (APP_FONT_BOLD, 30), text_color = "white", fg_color = self.fgColor).pack(fill = "both", pady = (10, 0))

        for match in next5:
            matchFrame = ctk.CTkFrame(self, fg_color = self.fgColor, width = self.width, height = self.frameHeight, corner_radius = self.corner_radius)
            matchFrame.pack(fill = "both")

            ctk.CTkLabel(matchFrame, text = "VS", font = (APP_FONT_BOLD, 20), text_color = "white", fg_color = self.fgColor).place(relx = 0.5, rely = 0.5, anchor = "center")

            homeTeam = Teams.get_team_by_id(match.home_id)
            awayTeam = Teams.get_team_by_id(match.away_id) 

            homeImage = Image.open(io.BytesIO(homeTeam.logo))
            homeImage.thumbnail((50, 50))
            homeLogo = TeamLogo(matchFrame, homeImage, homeTeam, self.fgColor, 0.35, 0.5, "center", self.parentTab)

            awayImage = Image.open(io.BytesIO(awayTeam.logo))
            awayImage.thumbnail((50, 50))
            awayLogo = TeamLogo(matchFrame, awayImage, awayTeam, self.fgColor, 0.65, 0.5, "center", self.parentTab)

            ctk.CTkLabel(matchFrame, text = homeTeam.name.split()[0], font = (APP_FONT, 13), text_color = "white", fg_color = self.fgColor).place(relx = 0.15, rely = self.textY, anchor = "center")
            ctk.CTkLabel(matchFrame, text = homeTeam.name.split()[1], font = (APP_FONT_BOLD, 18), text_color = "white", fg_color = self.fgColor).place(relx = 0.15, rely = 0.63, anchor = "center")
            ctk.CTkLabel(matchFrame, text = awayTeam.name.split()[0], font = (APP_FONT, 13), text_color = "white", fg_color = self.fgColor).place(relx = 0.85, rely = self.textY, anchor = "center")
            ctk.CTkLabel(matchFrame, text = awayTeam.name.split()[1], font = (APP_FONT_BOLD, 18), text_color = "white", fg_color = self.fgColor).place(relx = 0.85, rely = 0.63, anchor = "center")

class WinRatePieChart(ctk.CTkCanvas):
    def __init__(self, parent, gamesPlayed, gamesWon, gamesLost, figSize, fgColor, relx, rely, anchor):
        super().__init__(parent) 

        if gamesPlayed == 0:
            colours = [PIE_GREY]
            sizes = [100]
        else:
            winRate = (gamesWon / gamesPlayed) * 100
            lossRate = (gamesLost / gamesPlayed) * 100
            drawRate = 100 - winRate - lossRate
            
            sizes = []
            colours = []

            if winRate > 0:
                sizes.append(winRate)
                colours.append(PIE_GREEN)

            if lossRate > 0:
                sizes.append(lossRate)
                colours.append(PIE_RED)

            if drawRate > 0:
                sizes.append(drawRate)
                colours.append(PIE_GREY)

        piechart = Figure(figsize = figSize, dpi = 100, facecolor = fgColor)
        ax = piechart.add_subplot(111)

        ax.pie(sizes, colors = colours, autopct = '%d%%')
        ax.axis('equal')

        canvas = FigureCanvasTkAgg(piechart, master = parent)
        canvas.draw()
        canvas.get_tk_widget().place(relx = relx, rely = rely, anchor = anchor)

class TrophiesFrame(ctk.CTkFrame):
    def __init__(self, parent, id_, fg_color, width, height, corner_radius, relx, rely, anchor, team = True):
        super().__init__(parent, fg_color = fg_color, width = width, height = height, corner_radius = corner_radius)
        self.place(relx = relx, rely = rely, anchor = anchor)

        self.id = id_

        ctk.CTkLabel(self, text = "Trophies", font = (APP_FONT_BOLD, 30), fg_color = GREY_BACKGROUND).place(relx = 0.5, rely = 0.1, anchor = "center")

        if team:
            self.trophies = Trophies.get_all_trophies_by_team(self.id)
        else:
            self.trophies = Trophies.get_all_trophies_by_manager(self.id)

        self.comps = {}

        if self.trophies:
            for trophy in self.trophies:
                if trophy.competition_id not in self.comps:
                    self.comps[trophy.competition_id] = {}
                    self.comps[trophy.competition_id]["years"] = f"{trophy.year}, "
                else:
                    self.comps[trophy.competition_id]["years"] += f"{trophy.year}, "

            for competition in self.comps:
                self.league = League.get_league_by_id(competition)

                src = Image.open(io.BytesIO(self.league.logo))
                src.thumbnail((100, 100))
                logo = ctk.CTkImage(src, None, (src.width, src.height))
                ctk.CTkLabel(self, image = logo, text = "", fg_color = GREY_BACKGROUND).place(relx = 0.2, rely = 0.3, anchor = "center")
                ctk.CTkLabel(self, text = f"{self.league.name}", font = (APP_FONT, 25), fg_color = GREY_BACKGROUND).place(relx = 0.5, rely = 0.3, anchor = "center")
                ctk.CTkLabel(self, text = f"{self.formatYears(self.comps[competition]['years'])}", font = (APP_FONT, 15), fg_color = GREY_BACKGROUND).place(relx = 0.1, rely = 0.45, anchor = "w")

    def formatYears(self, years):
        years = years.split(",")
        return " - ".join(years) 
    
class FootballPitchVertical(ctk.CTkFrame):
    def __init__(self, parent, width, heigth, relx, rely, anchor, fgColor):
        super().__init__(parent, width = width, height = heigth, fg_color = fgColor)
        self.place(relx = relx, rely = rely, anchor = anchor)

        # Adjustable pitch dimensions (Horizontal)
        self.pitch_width = width  # Width of the pitch in pixels (horizontal)
        self.pitch_height = heigth  # Height of the pitch in pixels (vertical)

        # Canvas to draw the pitch
        self.canvas = ctk.CTkCanvas(self, width = self.pitch_width, height = self.pitch_height, bg = fgColor)
        self.canvas.pack()

    def draw_pitch(self):
        # Draw center circle
        center_x = self.pitch_width / 2
        center_y = self.pitch_height / 2
        self.canvas.create_oval(center_x - 50, center_y - 50, center_x + 50, center_y + 50, outline = "white", width = 2)
        self.canvas.create_line(center_x, 0, center_x, self.pitch_height + 5, fill = "white", width = 2)

        # Draw penalty areas
        self.canvas.create_rectangle(0, 25, 75, 225, outline = "white", width = 2)
        self.canvas.create_rectangle(self.pitch_width - 71, 25, self.pitch_width + 5, 225, outline = "white", width = 2)

        # Draw goal areas
        self.canvas.create_rectangle(0, self.pitch_height / 3, 25, self.pitch_height * 2 / 3, outline = "white", width = 2)
        self.canvas.create_rectangle(self.pitch_width - 21, self.pitch_height / 3, self.pitch_width + 5, self.pitch_height * 2 / 3, outline = "white", width = 2)

class FootballPitchHorizontal(ctk.CTkFrame):
    def __init__(self, parent, width, height, relx, rely, anchor, fgColor, pitchColor):
        super().__init__(parent, width = width - 50, height = height - 100, fg_color = fgColor)
        self.place(relx = relx, rely = rely, anchor = anchor)

        # Adjustable pitch dimensions (Horizontal)
        self.pitch_width = width  # Width of the pitch in pixels (horizontal)
        self.pitch_height = height  # Height of the pitch in pixels (vertical)

        self.canvas = ctk.CTkCanvas(self, width = self.pitch_width, height = self.pitch_height, bg = pitchColor)
        self.canvas.place(relx = 0.5, rely = 0.5, anchor = "center")

        self.draw_pitch()

    def draw_pitch(self):

         # Draw center circle
        center_x = self.pitch_width / 2
        center_y = self.pitch_height / 2
        self.canvas.create_oval(center_x - 50, center_y - 50, center_x + 50, center_y + 50, outline = "white", width = 2)
        self.canvas.create_line(0, center_y, self.pitch_width + 5, center_y, fill = "white", width = 2)

        # Draw penalty areas
        self.canvas.create_rectangle(self.pitch_width * (5/18), 0, self.pitch_width * (13/18), self.pitch_height * (4/27), outline = "white", width = 2)
        self.canvas.create_rectangle(self.pitch_width * (5/18), self.pitch_height - self.pitch_height * (19/135), self.pitch_width * (13/18), self.pitch_height + 5, outline = "white", width = 2)

        # Draw goal areas
        self.canvas.create_rectangle(self.pitch_width * (7/18), 0, self.pitch_width * (11/18), self.pitch_height * (8/135), outline = "white", width = 2)
        self.canvas.create_rectangle(self.pitch_width * (7/18), self.pitch_height - self.pitch_height * (7/135), self.pitch_width * (11/18), self.pitch_height + 5, outline = "white", width = 2)

class FootballPitchPlayerPos(FootballPitchVertical):
    def __init__(self, parent, width, heigth, relx, rely, anchor, fgColor):
        super().__init__(parent, width, heigth, relx, rely, anchor, fgColor)
        super().draw_pitch()

    def add_player_positions(self, highlighted_positions):
        # Define player positions in the form (x, y) with labels for each position
        player_positions = {
            "GK": (25, self.pitch_height / 2),  # Goalkeeper at the far left
            "LB": (90, self.pitch_height / 4),  # Left Back
            "RB": (90, self.pitch_height * 3 / 4),  # Right Back
            "CB": (90, self.pitch_height / 2),  # Center Back
            "DM": (155, self.pitch_height / 2),  # Defensive Midfielder
            "LM": (220, self.pitch_height / 4),  # Left Midfielder
            "CM": (220, self.pitch_height / 2),  # Central Midfielder
            "RM": (220, self.pitch_height * 3 / 4),  # Right Midfielder
            "LW": (285, self.pitch_height / 4),  # Left Winger
            "RW": (285, self.pitch_height * 3 / 4),  # Right Winger
            "AM": (285, self.pitch_height / 2),  # Attacking Midfielder
            "CF": (350, self.pitch_height / 2),  # Center Forward
        }

        # Size of the player circles
        player_radius = 12

        # Draw circles for each player position and label them
        for position, (x, y) in player_positions.items():

            if position in highlighted_positions:
                fill_color = APP_BLUE
                outline_color = APP_BLUE
            else:
                fill_color = TKINTER_BACKGROUND
                outline_color = GREY_BACKGROUND
            self.canvas.create_oval(x - player_radius, y - player_radius, x + player_radius, y + player_radius, fill = fill_color, outline = outline_color) 

class FootballPitchLineup(FootballPitchHorizontal):
    def __init__(self, parent, width, height, relx, rely, anchor, fgColor, pitchColor):
        super().__init__(parent, width, height, relx, rely, anchor, fgColor, pitchColor)
        super().draw_pitch()

        self.counter = 0

    def increment_counter(self):
        self.counter += 1
    
    def decrement_counter(self):
        self.counter -= 1

    def get_counter(self):
        return self.counter

    def reset_counter(self):
        self.counter = 0

    def set_counter(self, num):
        self.counter = num
        
class FootballPitchMatchDay(FootballPitchHorizontal):
    def __init__(self, parent, width, height, relx, rely, anchor, fgColor, pitchColor):
        super().__init__(parent, width, height, relx, rely, anchor, fgColor, pitchColor)
        super().draw_pitch()
        
        self.player_radius = 12

        self.positions = {
            "Goalkeeper": (0.5, 0.9),  # Goalkeeper
            "Left Back": (0.15, 0.75),  # Left Back
            "Right Back": (0.85, 0.75),  # Right Back
            "Center Back Right": (0.675, 0.75),  # Center Back Right
            "Center Back": (0.5, 0.75),  # Center Back
            "Center Back Left": (0.325, 0.75),  # Center Back Left
            "Defensive Midfielder": (0.5, 0.6),  # Defensive Midfielder
            "Defensive Midfielder Right": (0.65, 0.6),  # Defensive Midfielder Right
            "Defensive Midfielder Left": (0.35, 0.6),  # Defensive Midfielder Left
            "Left Midfielder": (0.15, 0.45),  # Left Midfielder
            "Central Midfielder Right": (0.65, 0.45),  # Center Midfielder Right
            "Central Midfielder": (0.5, 0.45),  # Center Midfielder
            "Central Midfielder Left": (0.35, 0.45),  # Center Midfielder Left
            "Right Midfielder": (0.85, 0.45),  # Right Midfielder
            "Left Winger": (0.15, 0.3),  # Left Winger
            "Right Winger": (0.85, 0.3),  # Right Winger
            "Attacking Midfielder": (0.5, 0.3),  # Attacking Midfielder
            "Striker Left": (0.3, 0.15),  # Striker Left
            "Striker Right": (0.7, 0.15),  # Striker Right
            "Center Forward": (0.5, 0.1),  # Center Forward
        }

    def addPlayer(self, position, playerName):
        relx, rely = self.positions[position]
        position_tag = position.replace(" ", "_")

        oval_tag = f"player_{position_tag}_oval"
        text_tag = f"player_{position_tag}_text"

        self.canvas.create_oval(
            relx * self.pitch_width - self.player_radius,
            rely * self.pitch_height - self.player_radius,
            relx * self.pitch_width + self.player_radius,
            rely * self.pitch_height + self.player_radius,
            fill = APP_BLUE,
            outline = APP_BLUE,
            tags = oval_tag
        )

        self.canvas.create_text(
            relx * self.pitch_width,
            rely * self.pitch_height + 20,
            text = playerName,
            fill = "white",
            font = (APP_FONT, 10),
            tags = text_tag
        )

    def removePlayer(self, position):
        position_tag = position.replace(" ", "_")
        oval_tag = f"player_{position_tag}_oval"
        text_tag = f"player_{position_tag}_text"

        self.canvas.delete(oval_tag)
        self.canvas.delete(text_tag)

class LineupPlayerFrame(ctk.CTkFrame):
    def __init__(self, parent, relx, rely, anchor, fgColor, height, width, playerName, positionCode, position, removePlayer):
        super().__init__(parent, fg_color = fgColor, width = width, height = height, background_corner_colors = [fgColor, fgColor, fgColor, fgColor])
        self.place(relx = relx, rely = rely, anchor = anchor)

        self.position = position

        ctk.CTkLabel(self, text = positionCode, font = (APP_FONT, 15), height = 10, fg_color = fgColor).place(relx = 0.05, rely = 0.05, anchor = "nw")

        self.firstName = ctk.CTkLabel(self, text = playerName.split(" ")[0], font = (APP_FONT, 10), height = 10, fg_color = fgColor)
        self.firstName.place(relx = 0.5, rely = 0.45, anchor = "center")
        self.lastName = ctk.CTkLabel(self, text = playerName.split(" ")[1], font = (APP_FONT_BOLD, 13), fg_color = fgColor)
        self.lastName.place(relx = 0.5, rely = 0.75, anchor = "center")

        self.removeButton = ctk.CTkButton(self, text = "X", width = 10, height = 10, fg_color = fgColor, hover_color = CLOSE_RED, corner_radius = 0, command = lambda f = self, p = playerName: removePlayer(f, p, self.position))
        self.removeButton.place(relx = 0.95, rely = 0.05, anchor = "ne")

class SubstitutePlayer(ctk.CTkFrame):
    def __init__(self, parent, fgColor, height, width, player, checkBoxFunction, parentTab, comp_id):
        super().__init__(parent, fg_color = fgColor, width = width, height = height)
        self.pack(pady = 5)

        self.player = player
        self.playerBanned = PlayerBans.check_bans_for_player(self.player.id, comp_id)

        if not self.playerBanned:
            textColor = "white"
        else:
            textColor = GREY

        ctk.CTkLabel(self, text = "SUB", font = (APP_FONT, 15), fg_color = GREY_BACKGROUND).place(relx = 0.02, rely = 0.5, anchor = "w")
        
        self.playerName = PlayerProfileLink(self, player, player.first_name + " " + player.last_name, textColor, 0.15, 0.5, "w", GREY_BACKGROUND, parentTab, 15)

        ctk.CTkLabel(self, text = player.specific_positions.split(","), font = (APP_FONT, 15), fg_color = GREY_BACKGROUND).place(relx = 0.85, rely = 0.5, anchor = "e")

        self.checkBox = ctk.CTkCheckBox(self, text = "", fg_color = DARK_GREY, checkbox_height = 20, width = 20)
        self.checkBox.configure(command = lambda: checkBoxFunction(self.checkBox, player))

    def showCheckBox(self):

        if self.playerBanned:
            return

        self.checkBox.place(relx = 0.95, rely = 0.5, anchor = "e")
        self.checkBox.configure(state = "normal")

    def hideCheckBox(self):
        self.checkBox.place_forget()
    
    def disableCheckBox(self):
        self.checkBox.configure(state = "disabled")

    def enableCheckBox(self):
        self.checkBox.configure(state = "normal")

    def uncheckCheckBox(self):
        self.checkBox.deselect()

class MatchDayMatchFrame(ctk.CTkFrame):
    def __init__(self, parent, match, fgColor, height, width, imageSize = 40, relx = 0, rely = 0, anchor = "nw", border_width = None, border_color = None, pack = True):
        super().__init__(parent, fg_color = fgColor, width = width, height = height, border_width = border_width, border_color = border_color)
        
        self.match = match
        self.fgColor = fgColor
        self.imageSize = imageSize
        self.relx = relx
        self.rely = rely
        self.anchor = anchor
        self.packFrame = pack

        self.score = "0 - 0"

        self.matchInstance = Match(self.match)

        self.addFrame()

    def addFrame(self):
        
        if self.packFrame: 
            # smaller frames on the side
            self.pack(expand = True, fill = "both", pady = (0, 3))
            scoreSize = 23
            teamNameSize1 = 10
            teamNameSize2 = 13
            teamNamePlaceY1 = 0.3
            teamNamePlaceY2 = 0.7
        else:
            # large frame for team match
            self.place(relx = self.relx, rely = self.rely, anchor = self.anchor)
            scoreSize = 30
            teamNameSize1 = 15
            teamNameSize2 = 18
            teamNamePlaceY1 = 0.4
            teamNamePlaceY2 = 0.6

        self.homeTeam = Teams.get_team_by_id(self.match.home_id)
        ctk.CTkLabel(self, text = self.homeTeam.name.split(" ")[0], font = (APP_FONT, teamNameSize1), fg_color = self.fgColor).place(relx = 0.12, rely = teamNamePlaceY1, anchor = "center")
        ctk.CTkLabel(self, text = self.homeTeam.name.split(" ")[1], font = (APP_FONT_BOLD, teamNameSize2), fg_color = self.fgColor).place(relx = 0.12, rely = teamNamePlaceY2, anchor = "center")

        srcHome = Image.open(io.BytesIO(self.homeTeam.logo))
        srcHome.thumbnail((self.imageSize, self.imageSize))
        homeLogo = ctk.CTkImage(srcHome, None, (srcHome.width, srcHome.height))
        ctk.CTkLabel(self, image = homeLogo, text = "", fg_color = self.fgColor).place(relx = 0.3, rely = 0.5, anchor = "center")

        self.awayTeam = Teams.get_team_by_id(self.match.away_id)
        ctk.CTkLabel(self, text = self.awayTeam.name.split(" ")[0], font = (APP_FONT, teamNameSize1), fg_color = self.fgColor).place(relx = 0.88, rely = teamNamePlaceY1, anchor = "center")
        ctk.CTkLabel(self, text = self.awayTeam.name.split(" ")[1], font = (APP_FONT_BOLD, teamNameSize2), fg_color = self.fgColor).place(relx = 0.88, rely = teamNamePlaceY2, anchor = "center")

        srcAway = Image.open(io.BytesIO(self.awayTeam.logo))
        srcAway.thumbnail((self.imageSize, self.imageSize))
        awayLogo = ctk.CTkImage(srcAway, None, (srcAway.width, srcAway.height))
        ctk.CTkLabel(self, image = awayLogo, text = "", fg_color = self.fgColor).place(relx = 0.7, rely = 0.5, anchor = "center")

        self.scoreLabel = ctk.CTkLabel(self, text = f"0 - 0", font = (APP_FONT_BOLD, scoreSize), fg_color = self.fgColor)
        self.scoreLabel.place(relx = 0.5, rely = 0.5, anchor = "center")

        if self.packFrame:
            self.halfTimeLabel = ctk.CTkLabel(self, text = "HT", font = (APP_FONT, 10), fg_color = self.fgColor)
            self.fullTimeLabel = ctk.CTkLabel(self, text = "FT", font = (APP_FONT, 10), fg_color = self.fgColor)
            self.labelY = 0.8
        else:
            self.halfTimeLabel = ctk.CTkLabel(self, text = "HT", font = (APP_FONT, 20), fg_color = self.fgColor)
            self.fullTimeLabel = ctk.CTkLabel(self, text = "FT", font = (APP_FONT, 20), fg_color = self.fgColor)
            self.labelY = 0.7

    def HTLabel(self, place = True):
        if place:
            self.halfTimeLabel.place(relx = 0.5, rely = self.labelY, anchor = "center")
        else:
            self.halfTimeLabel.place_forget()
    
    def FTLabel(self, place = True):
        if place:
            self.fullTimeLabel.place(relx = 0.5, rely = self.labelY, anchor = "center")
        else:
            self.fullTimeLabel.place_forget()

    def updateScoreLabel(self, home = True, textAdd = None):
        if home:
            if textAdd:
                text = textAdd
            else:
                homeGoals = int(self.scoreLabel.cget("text").split(" - ")[0]) + 1
                awayGoals = int(self.scoreLabel.cget("text").split(" - ")[1])

                text = f"{homeGoals} - {awayGoals}"
                self.score = text
        else:
            if textAdd:
                text = textAdd
            else:
                awayGoals = int(self.scoreLabel.cget("text").split(" - ")[1]) + 1
                homeGoals = int(self.scoreLabel.cget("text").split(" - ")[0])

                text = f"{homeGoals} - {awayGoals}"
                self.score = text

        self.scoreLabel.configure(text = text)

    def getScoreLabel(self):
        return self.scoreLabel.cget("text")

    def getCurrentScore(self):
        return self.scoreLabel.cget("text").split(" - ")

class MatchEventFrame(ctk.CTkFrame):
    def __init__(self, parent, width, height, corner_radius, fgColor, event, time):
        super().__init__(parent, fg_color = fgColor, width = width, height = height, corner_radius = corner_radius)
        self.pack(expand = True, fill = "both", padx = 10, pady = (0, 10))