import customtkinter as ctk
from settings import *
from data.database import *
from data.gamesDatabase import *
from utils.teamProfileLink import *
from utils.leagueProfileLink import LeagueProfileLabel
from utils.playerProfileLink import *
from utils.teamLogo import TeamLogo
from PIL import Image
import io

class EmailFrame(ctk.CTkFrame):
    def __init__(self, parent, session, manager_id, email_type, matchday, player_id, emailFrame, parentTab):
        super().__init__(parent, fg_color = TKINTER_BACKGROUND, width = 260, height = 50)
        self.pack(fill = "both", padx = 10, pady = 5)

        self.parent = parent
        self.session = session
        self.manager_id = manager_id
        self.email_type = email_type
        self.matchday = matchday
        self.player_id = player_id
        self.emailFrame = emailFrame
        self.parentTab = parentTab

        self.emailOpen = False

        self.manager = Managers.get_manager_by_id(self.session, self.manager_id)
        self.team = Teams.get_teams_by_manager(self.session, self.manager_id)[0]
        self.leagueData = LeagueTeams.get_league_by_team(self.session, self.team.id)
        self.league = League.get_league_by_id(self.session, self.leagueData.league_id)
        self.player = Players.get_player_by_id(self.session, self.player_id) if self.player_id else None

        self.email = EMAIL_CLASSES[self.email_type](self, self.session)

        self.bind("<Enter>", lambda e: self.onFrameHover())
        self.bind("<Leave>", lambda e: self.onFrameLeave())
        self.bind("<Button-1>", lambda e: self.displayEmailInfo())

        self.addEmailSubject()

        self.canvas = ctk.CTkCanvas(self, width = 300, height = 5, bg = DARK_GREY, bd = 0, highlightthickness = 0)
        self.canvas.place(relx = 0.5, rely = 0.9, anchor = "center")
        self.canvas.bind("<Enter>", lambda e: self.onFrameHover())
        self.canvas.bind("<Button-1>", lambda e: self.displayEmailInfo())

    def onFrameHover(self):
        self.configure(fg_color = DARK_GREY)
        self.subjectLabel.configure(fg_color = DARK_GREY)
        self.senderLabel.configure(fg_color = DARK_GREY)
    
    def onFrameLeave(self):
        self.configure(fg_color = TKINTER_BACKGROUND)
        self.subjectLabel.configure(fg_color = TKINTER_BACKGROUND)
        self.senderLabel.configure(fg_color = TKINTER_BACKGROUND)

    def displayEmailInfo(self):

        if self.emailOpen:
            return

        self.canvas.place_forget()
        self.configure(border_color = APP_BLUE, border_width = 2)

        self.emailOpen = True

        for emailFrame in self.parent.winfo_children():
            if emailFrame != self:
                emailFrame.configure(border_color = TKINTER_BACKGROUND, border_width = 0)
                emailFrame.canvas.place(relx = 0.5, rely = 0.9, anchor = "center")
                emailFrame.emailOpen = False

        self.email.openEmail()
        
    def addEmailSubject(self):
        subject = self.email.subject
        sender = self.email.sender
        fontSize = self.email.subjectFontSize

        self.subjectLabel = ctk.CTkLabel(self, text = subject, font = (APP_FONT_BOLD, fontSize), fg_color = TKINTER_BACKGROUND)
        self.subjectLabel.place(relx = 0.05, rely = 0.3, anchor = "w")
        self.senderLabel = ctk.CTkLabel(self, text = sender, font = (APP_FONT, 10), height = 8, fg_color = TKINTER_BACKGROUND)
        self.senderLabel.place(relx = 0.05, rely = 0.7, anchor = "w")

        self.subjectLabel.bind("<Enter>", lambda event: self.onFrameHover())
        self.subjectLabel.bind("<Button-1>", lambda e: self.displayEmailInfo())
        self.senderLabel.bind("<Enter>", lambda event: self.onFrameHover())
        self.senderLabel.bind("<Button-1>", lambda e: self.displayEmailInfo())

    def getSuffix(self, number):
        if 10 <= number % 100 <= 20:
            return "th"
        else:
            return {1: "st", 2: "nd", 3: "rd"}.get(number % 10, "th")
class Welcome():
    def __init__(self, parent, session):

        self.parent = parent
        self.session = session
        self.frame = self.parent.emailFrame

        self.subject = f"Welcome to the {self.parent.team.name}!"
        self.sender = "Name, Chairman"
        self.subjectFontSize = 15

    def openEmail(self):
        for widget in self.frame.winfo_children():
            widget.place_forget()

        self.setUpEmail()

        self.emailTitle = ctk.CTkLabel(self.frame, text = self.subject, font = (APP_FONT_BOLD, 30))
        self.emailTitle.place(relx = 0.05, rely = 0.05, anchor = "w")

        ctk.CTkLabel(self.frame, text = self.emailText_1, font = (APP_FONT, 15), justify = "left", text_color = "white").place(relx = 0.05, rely = 0.13, anchor = "w")
        self.emailFrame_1.place(relx = 0.05, rely = 0.17, anchor = "w")
        ctk.CTkLabel(self.frame, text = self.emailText_1_1, font = (APP_FONT, 15), justify = "left", text_color = "white").place(relx = 0.05, rely = 0.21, anchor = "w")
        ctk.CTkLabel(self.frame, text = self.title_1, font = (APP_FONT_BOLD, 20), justify = "left", text_color = "white").place(relx = 0.05, rely = 0.28, anchor = "w")
        self.emailFrame_2.place(relx = 0.05, rely = 0.31, anchor = "w")
        ctk.CTkLabel(self.frame, text = self.emailTextBetFrame_1, font = (APP_FONT, 15), justify = "left", text_color = "white").place(relx = 0.05, rely = 0.35, anchor = "w")
        self.emailFrame_3.place(relx = 0.05, rely = 0.39, anchor = "w")
        ctk.CTkLabel(self.frame, text = self.title_2, font = (APP_FONT_BOLD, 20), justify = "left", text_color = "white").place(relx = 0.05, rely = 0.445, anchor = "w")
        ctk.CTkLabel(self.frame, text = self.emailText_3, font = (APP_FONT, 15), justify = "left", text_color = "white").place(relx = 0.05, rely = 0.48, anchor = "w")
        self.emailFrame_4.place(relx = 0.05, rely = 0.51, anchor = "w")
        ctk.CTkLabel(self.frame, text = self.emailText_3_1, font = (APP_FONT, 15), justify = "left", text_color = "white").place(relx = 0.05, rely = 0.54, anchor = "w")
        self.emailFrame_5.place(relx = 0.05, rely = 0.57, anchor = "w")
        ctk.CTkLabel(self.frame, text = self.emailText_3_2, font = (APP_FONT, 15), justify = "left", text_color = "white").place(relx = 0.05, rely = 0.601, anchor = "w")
        ctk.CTkLabel(self.frame, text = self.title_3, font = (APP_FONT_BOLD, 20), justify = "left", text_color = "white").place(relx = 0.05, rely = 0.645, anchor = "w")
        ctk.CTkLabel(self.frame, text = self.emailText_4, font = (APP_FONT, 15), justify = "left", text_color = "white").place(relx = 0.05, rely = 0.68, anchor = "w")
        self.emailFrame_6.place(relx = 0.05, rely = 0.71, anchor = "w")
        self.emailFrame_7.place(relx = 0.05, rely = 0.74, anchor = "w")
        self.emailFrame_8.place(relx = 0.05, rely = 0.771, anchor = "w")
        ctk.CTkLabel(self.frame, text = self.title_4, font = (APP_FONT_BOLD, 20), justify = "left", text_color = "white").place(relx = 0.05, rely = 0.83, anchor = "w")
        self.emailFrame_9.place(relx = 0.05, rely = 0.86, anchor = "w")
        ctk.CTkLabel(self.frame, text = self.emailText_5, font = (APP_FONT, 15), justify = "left", text_color = "white").place(relx = 0.05, rely = 0.891, anchor = "w")
        ctk.CTkLabel(self.frame, text = self.emailText_6, font = (APP_FONT, 15), justify = "left", text_color = "white").place(relx = 0.05, rely = 0.95, anchor = "w")

    def setUpEmail(self):
        self.emailText_1 = (
            f"Dear {self.parent.manager.first_name} {self.parent.manager.last_name},\n"
        )

        self.emailFrame_1 = TeamProfileLabel(
            self.frame,
            self.session,
            self.parent.manager.id,
            self.parent.team.name,
            f"Welcome to ",
            "! We’re thrilled to have you on board as the new manager of our",
            600,
            30,
            self.parent.parentTab,
            fontSize = 15
        )

        self.emailText_1_1 = (
            f"beloved team. As you take the reins, here’s an overview of what lies ahead for you and the squad\n"
            f"this season."
        )

        self.title_1 = "About the Club"
        self.emailFrame_2 = TeamProfileLabel(
            self.frame,
            self.session,
            self.parent.manager.id,
            self.parent.team.name,
            f"Founded in {self.parent.team.year_created}, ",
            f" is a club rich in history and tradition, with a loyal fan base that",
            600,
            30,
            self.parent.parentTab,
            fontSize = 15
        )

        self.emailTextBetFrame_1 = (
            f"proudly supports us every step of the way. We play our home matches at {self.parent.team.stadium}, a venue\n"
            f"known for its electric atmosphere and passionate crowd."
        )

        self.emailFrame_3 = LeagueProfileLabel(
            self.frame,
            self.session,
            self.parent.manager.id,
            self.parent.league.name,
            f"Our team competes in the ",
            f", and we’re striving to {get_objective_for_level(self.parent.team.level)} this season.",
            600,
            30,
            self.parent.parentTab,
            fontSize = 15
        )

        expected_finish = (200 - self.parent.team.level) // 2 + 1
        suffix = self.parent.getSuffix(expected_finish)
        self.firstMatch = Matches.get_team_first_match(self.session, self.parent.team.id)
        homeTeam = Teams.get_team_by_id(self.session, self.firstMatch.home_id)
        awayTeam = Teams.get_team_by_id(self.session, self.firstMatch.away_id)
        self.opponent = homeTeam if homeTeam.id != self.parent.team.id else awayTeam
        self.venue = "a home" if homeTeam.id == self.parent.team.id else "an away"

        self.title_2 = "Season Objectives"
        self.emailText_3 = (
            f"The board has set the following expectations for the season:"
        )

        self.emailFrame_4 = LeagueProfileLabel(
            self.frame,
            self.session,
            self.parent.manager.id,
            self.parent.league.name,
            f"- League Finish: {expected_finish}{suffix} place in the ",
            f".",
            600,
            30,
            self.parent.parentTab,
            fontSize = 15
        )

        self.emailText_3_1 = (
            f"- Cup Competitions:"
        )

        self.emailFrame_5 = TeamProfileLabel(
            self.frame,
            self.session,
            self.opponent.manager_id,
            self.opponent.name,
            f"Our journey starts with our first match against ",
            f". It’s {self.venue} game, and we’re",
            600,
            30,
            self.parent.parentTab,
            fontSize = 15
        )

        self.emailText_3_2 = (
           f"counting on you to set the tone for the season with a strong performance." 
        )

        self.stars = Players.get_all_star_players(self.session, self.parent.team.id)

        self.title_3 = "Key Players"
        self.emailText_4 = "Here are some of the standout players you’ll be working with:"

        player1 = self.stars[0]
        self.emailFrame_6 = PlayerProfileLabel(
            self.frame,
            self.session,
            player1,
            f"{player1.first_name} {player1.last_name}",
            "- ",
            f" ({player1.position}, star player)",
            600,
            30,
            self.parent.parentTab,
            fontSize = 15
        )

        player2 = self.stars[1]
        self.emailFrame_7 = PlayerProfileLabel(
            self.frame,
            self.session,
            player2,
            f"{player2.first_name} {player2.last_name}",
            "- ",
            f" ({player2.position}, star player)",
            600,
            30,
            self.parent.parentTab,
            fontSize = 15
        )

        player3 = self.stars[2]
        self.emailFrame_8 = PlayerProfileLabel(
            self.frame,
            self.session,
            player3,
            f"{player3.first_name} {player3.last_name}",
            "- ",
            f" ({player3.position}, star player)",
            600,
            30,
            self.parent.parentTab,
            fontSize = 15
        )

        self.title_4 = "Let's get to work!"

        self.emailFrame_9 = TeamProfileLabel(
            self.frame,
            self.session,
            self.parent.team.manager_id,
            self.parent.team.name,
            f"We’re confident in your abilities to lead ",
            f" to glory. The fans, the players, and the",
            600,
            30,
            self.parent.parentTab,
            fontSize = 15
        )
        
        self.emailText_5 = (
            f"board are all behind you. Let’s make this a season to remember!"
        )

        self.emailText_6 = (
            f"Best regards,\n"
            f"Name, Chairman"
        )
class MatchdayReview():
    def __init__(self, parent, session):

        self.parent = parent
        self.session = session
        self.matchday = self.parent.matchday
        self.frame = self.parent.emailFrame

        self.subject = f"Matchday {self.parent.matchday} review"
        self.sender = "Name, Assistant Manager"
        self.subjectFontSize = 20

    def openEmail(self):
        for widget in self.frame.winfo_children():
            widget.place_forget()

        self.setUpEmail()

        self.emailTitle = ctk.CTkLabel(self.frame, text = self.subject, font = (APP_FONT_BOLD, 30))
        self.emailTitle.place(relx = 0.05, rely = 0.05, anchor = "w")

        ctk.CTkLabel(self.frame, text = self.emailText_1, font = (APP_FONT, 15), justify = "left", text_color = "white").place(relx = 0.05, rely = 0.1, anchor = "w")
        self.statsFrame.place(relx = 0.98, rely = 0.12, anchor = "ne")
        ctk.CTkLabel(self.frame, text = self.emailText_2, font = (APP_FONT, 15), justify = "left", text_color = "white").place(relx = 0.05, rely = 0.15, anchor = "w")
        self.emailFrame_1.place(relx = 0.05, rely = 0.179, anchor = "w")
        ctk.CTkLabel(self.frame, text = self.emailText_3, font = (APP_FONT, 15), justify = "left", text_color = "white").place(relx = 0.05, rely = 0.22, anchor = "w")

    def setUpEmail(self):
        self.emailText_1 = "Here is everything you need to know about the matchday that just passed:"

        self.statsFrame = ctk.CTkFrame(self.frame, fg_color = TKINTER_BACKGROUND, border_color = GREY_BACKGROUND, border_width = 4, width = 250, height = 600)
        self.statsFrame.pack_propagate(0)

        self.matchFrame()

        match_ = Matches.get_team_matchday_match(self.session, self.parent.team.id, self.parent.league.id, self.matchday)
        homeTeam = Teams.get_team_by_id(self.session, match_.home_id)
        awayTeam = Teams.get_team_by_id(self.session, match_.away_id)

        opponentTeam = homeTeam if homeTeam.id != self.parent.team.id else awayTeam
        expectation = get_expectation(self.parent.team.level, opponentTeam.level)
        home = True if homeTeam.id == self.parent.team.id else False

        goalDifference = match_.score_home - match_.score_away if home else match_.score_away - match_.score_home
        if goalDifference > 0:
            result = "win"
        elif goalDifference < 0:
            result = "loss"
        else:
            result = "draw"
        result_category = get_result_category(result, goalDifference)

        fan_reaction = get_fan_reaction(result_category, expectation)
        fan_message = get_fan_message(fan_reaction)

        self.emailText_2 = (
            f"The game ended in a {result} for us against"
        )
        
        self.emailFrame_1 = TeamProfileLabel(
            self.frame,
            self.session,
            opponentTeam.manager_id,
            opponentTeam.name,
            f"",
            f", with a goal difference of {goalDifference}.",
            240,
            30,
            self.parent.parentTab,
            fontSize = 15
        )

        self.emailText_3 = (
            f"{fan_message}"
        )

    def matchFrame(self):
        matches = Matches.get_matchday_for_league(self.session, self.parent.league.id, self.matchday)
        bestMatch = self.findBestMatch(matches)
        bestPlayer, events, rating = self.findBestPlayer(matches)

        matchFrame = ctk.CTkFrame(self.statsFrame, fg_color = TKINTER_BACKGROUND, width = 240, height = 250)
        matchFrame.pack(fill = "both", padx = 5, pady = 5)

        ctk.CTkLabel(matchFrame, text = "Best showing:", font = (APP_FONT_BOLD, 25), fg_color = TKINTER_BACKGROUND).place(relx = 0.5, rely = 0.15, anchor = "center")

        homeTeam = Teams.get_team_by_id(self.session, bestMatch.home_id)
        homeImage = Image.open(io.BytesIO(homeTeam.logo))
        homeImage.thumbnail((75,  75))
        TeamLogo(matchFrame, self.session, homeImage, homeTeam, TKINTER_BACKGROUND, 0.2, 0.45, "center", self.parent.parentTab)

        ctk.CTkLabel(matchFrame, text = homeTeam.name.split()[0], font = (APP_FONT, 13), fg_color = TKINTER_BACKGROUND).place(relx = 0.2, rely = 0.65, anchor = "center")
        ctk.CTkLabel(matchFrame, text = homeTeam.name.split()[1], font = (APP_FONT_BOLD, 18), fg_color = TKINTER_BACKGROUND).place(relx = 0.2, rely = 0.75, anchor = "center")

        awayTeam = Teams.get_team_by_id(self.session, bestMatch.away_id)
        awayImage = Image.open(io.BytesIO(awayTeam.logo))
        awayImage.thumbnail((75,  75))
        TeamLogo(matchFrame, self.session, awayImage, awayTeam, TKINTER_BACKGROUND, 0.8, 0.45, "center", self.parent.parentTab)

        ctk.CTkLabel(matchFrame, text = awayTeam.name.split()[0], font = (APP_FONT, 13), fg_color = TKINTER_BACKGROUND).place(relx = 0.8, rely = 0.65, anchor = "center")
        ctk.CTkLabel(matchFrame, text = awayTeam.name.split()[1], font = (APP_FONT_BOLD, 18), fg_color = TKINTER_BACKGROUND).place(relx = 0.8, rely = 0.75, anchor = "center")

        ctk.CTkLabel(matchFrame, text = f"{bestMatch.score_home} - {bestMatch.score_away}", font = (APP_FONT_BOLD, 25), fg_color = TKINTER_BACKGROUND).place(relx = 0.5, rely = 0.5, anchor = "center")

        playerOTM = self.getPlayerOfTheMatch(bestMatch)

        ctk.CTkLabel(matchFrame, text = f"POTM: ", font = (APP_FONT, 18), fg_color = TKINTER_BACKGROUND).place(relx = 0.05, rely = 0.92, anchor = "w")
        PlayerProfileLink(matchFrame, self.session, playerOTM, f"{playerOTM.first_name} {playerOTM.last_name}", "white", 0.31, 0.92, "w", TKINTER_BACKGROUND, self.parent.parentTab, fontSize = 18)

        canvas = ctk.CTkCanvas(self.statsFrame, width = 10, height = 5, bg = GREY_BACKGROUND, bd = 0, highlightthickness = 0)
        canvas.pack(fill = "both", padx = 5, pady = 5)  

        playerFrame = ctk.CTkFrame(self.statsFrame, fg_color = TKINTER_BACKGROUND, width = 240, height = 250)
        playerFrame.pack(fill = "both", padx = 5, pady = 5)

        ctk.CTkLabel(playerFrame, text = "Best player:", font = (APP_FONT_BOLD, 25), fg_color = TKINTER_BACKGROUND).place(relx = 0.5, rely = 0.1, anchor = "center")

        src = Image.open("Images/default_user.png")
        src.thumbnail((75,  75))
        playerImage = ctk.CTkImage(src, None, (src.width, src.height))
        ctk.CTkLabel(playerFrame, image = playerImage, text = "", fg_color = TKINTER_BACKGROUND).place(relx = 0.2, rely = 0.4, anchor = "center")

        PlayerProfileLink(playerFrame, self.session, bestPlayer, f"{bestPlayer.first_name} {bestPlayer.last_name}", "white", 0.45, 0.35, "w", TKINTER_BACKGROUND, self.parent.parentTab, fontSize = 15)
        playerTeam = Teams.get_team_by_id(self.session, bestPlayer.team_id)
        TeamProfileLink(playerFrame, self.session, playerTeam.manager_id, playerTeam.name, "white", 0.45, 0.45, "w", TKINTER_BACKGROUND, self.parent.parentTab, fontSize = 12)

        src = Image.open("Images/averageRating.png")
        src.thumbnail((25,  25))
        ratingImage = ctk.CTkImage(src, None, (src.width, src.height))
        ctk.CTkLabel(playerFrame, image = ratingImage, text = f"", fg_color = TKINTER_BACKGROUND).place(relx = 0.05, rely = 0.7, anchor = "w")
        ctk.CTkLabel(playerFrame, text = f"Rating: {rating:.2f}", font = (APP_FONT, 20), fg_color = TKINTER_BACKGROUND).place(relx = 0.2, rely = 0.7, anchor = "w")

        events_data = {}
        for event in events:
            if event.event_type == "goal" or event.event_type == "penalty_goal":
                if "goal" not in events_data:
                    events_data["goal"] = 1
                else:
                    events_data["goal"] += 1
            elif event.event_type == "assist":
                if "assist" not in events_data:
                    events_data["assist"] = 1
                else:
                    events_data["assist"] += 1

        for i, (data, num) in enumerate(events_data.items()):
            if data == "goal":
                src = Image.open("Images/goal.png")
                text = "Goals: " + str(num)
            elif data == "assist":
                src = Image.open("Images/assist.png")
                text = "Assists: " + str(num)
        
            src.thumbnail((25,  25))
            eventImage = ctk.CTkImage(src, None, (src.width, src.height))
            ctk.CTkLabel(playerFrame, image = eventImage, text = "", fg_color = TKINTER_BACKGROUND).place(relx = 0.05, rely = 0.812 + i * 0.12, anchor = "w")
            ctk.CTkLabel(playerFrame, text = text, font = (APP_FONT, 20), fg_color = TKINTER_BACKGROUND).place(relx = 0.2, rely = 0.812 + i * 0.12, anchor = "w")

    def findBestMatch(self, matches):
        highestScore = 0
        currMatch = None

        for match in matches:
            if match.score_home + match.score_away > highestScore:
                highestScore = match.score_home + match.score_away
                currMatch = match

        return currMatch
    
    def findBestPlayer(self, matches):
        highestRating = 0
        currPlayer = None
        playerEvents = []

        for match in matches:
            lineupHome = TeamLineup.get_lineup_by_match_and_team(self.session, match.id, match.home_id)
            lineupAway = TeamLineup.get_lineup_by_match_and_team(self.session, match.id, match.away_id)

            for player in lineupHome:
                if player.rating > highestRating:
                    highestRating = player.rating
                    playerData = Players.get_player_by_id(self.session, player.player_id)
                    currPlayer = playerData
                    playerEvents = MatchEvents.get_events_by_match_and_player(self.session, match.id, player.player_id)

            for player in lineupAway:
                if player.rating > highestRating:
                    highestRating = player.rating
                    playerData = Players.get_player_by_id(self.session, player.player_id)
                    currPlayer = playerData
                    playerEvents = MatchEvents.get_events_by_match_and_player(self.session, match.id, player.player_id)
        
        return currPlayer, playerEvents, highestRating
    
    def getPlayerOfTheMatch(self, match):
        highestRating = 0
        currPlayer = None

        lineupHome = TeamLineup.get_lineup_by_match_and_team(self.session, match.id, match.home_id)
        lineupAway = TeamLineup.get_lineup_by_match_and_team(self.session, match.id, match.away_id)

        for player in lineupHome:
            if player.rating > highestRating:
                highestRating = player.rating
                playerData = Players.get_player_by_id(self.session, player.player_id)
                currPlayer = playerData

        for player in lineupAway:
            if player.rating > highestRating:
                highestRating = player.rating
                playerData = Players.get_player_by_id(self.session, player.player_id)
                currPlayer = playerData

        return currPlayer

class MatchdayPreview():
    def __init__(self, parent, session):

        self.parent = parent
        self.session = session
        self.frame = self.parent.emailFrame
        self.matchday = self.parent.matchday

        self.subject = f"Matchday {self.parent.matchday} preview"
        self.sender = "Name, Assistant Manager"
        self.subjectFontSize = 20

    def openEmail(self):
        for widget in self.frame.winfo_children():
            widget.place_forget()

        self.setUpEmail()

        self.emailTitle = ctk.CTkLabel(self.frame, text = self.subject, font = (APP_FONT_BOLD, 30))
        self.emailTitle.place(relx = 0.05, rely = 0.05, anchor = "w")

        self.emailFrame_1.place(relx = 0.05, rely = 0.12, anchor = "w")
        ctk.CTkLabel(self.frame, text = self.title_1, font = (APP_FONT_BOLD, 20), justify = "left", text_color = "white").place(relx = 0.05, rely = 0.17, anchor = "w")
        self.emailFrame_2.place(relx = 0.05, rely = 0.2, anchor = "w")
        self.emailFrame_3.place(relx = self.emailFrame_3_x, rely = 0.2, anchor = "w")
        ctk.CTkLabel(self.frame, text = self.emailText_2, font = (APP_FONT, 15), justify = "left", text_color = "white").place(relx = 0.05, rely = 0.275, anchor = "w")
        ctk.CTkLabel(self.frame, text = self.title_2, font = (APP_FONT_BOLD, 20), justify = "left", text_color = "white").place(relx = 0.05, rely = 0.355, anchor = "w")
        self.emailFrame_4.place(relx = 0.05, rely = 0.39, anchor = "w")
        ctk.CTkLabel(self.frame, text = self.emailText_3, font = (APP_FONT, 15), justify = "left", text_color = "white").place(relx = 0.05, rely = 0.44, anchor = "w")
        ctk.CTkLabel(self.frame, text = self.title_3, font = (APP_FONT_BOLD, 20), justify = "left", text_color = "white").place(relx = 0.05, rely = 0.53, anchor = "w")
        ctk.CTkLabel(self.frame, text = self.emailText_4, font = (APP_FONT, 15), justify = "left", text_color = "white").place(relx = 0.05, rely = 0.55, anchor = "nw")

        for i in range(len(self.emailFrames_5)):
            self.emailFrames_5[i].place(relx = 0.05, rely = 0.6 + 0.031 * i, anchor = "w")

        ctk.CTkLabel(self.frame, text = self.title_4, font = (APP_FONT_BOLD, 20), justify = "left", text_color = "white").place(relx = 0.05, rely = 0.72, anchor = "w")
        self.emailFrame_6.place(relx = 0.05, rely = 0.76, anchor = "w")
        ctk.CTkLabel(self.frame, text = self.title_5, font = (APP_FONT_BOLD, 20), justify = "left", text_color = "white").place(relx = 0.05, rely = 0.82, anchor = "w")
        ctk.CTkLabel(self.frame, text = self.emailText_6, font = (APP_FONT, 15), justify = "left", text_color = "white").place(relx = 0.05, rely = 0.85, anchor = "nw")

    def setUpEmail(self):

        self.nextMatch = Matches.get_team_matchday_match(self.session, self.parent.team.id, self.parent.league.id, self.matchday)
        homeTeam = Teams.get_team_by_id(self.session, self.nextMatch.home_id)
        awayTeam = Teams.get_team_by_id(self.session, self.nextMatch.away_id)
        self.opponent = homeTeam if homeTeam.id != self.parent.team.id else awayTeam
        self.opponentData = TeamHistory.get_team_data_matchday(self.session, self.opponent.id, self.matchday - 1)

        self.emailFrame_1 = TeamProfileLabel(
            self.frame,
            self.session,
            self.opponent.manager_id,
            self.opponent.name,
            f"Here is everything you need to know about our upcoming match against ",
            ":",
            600,
            30,
            self.parent.parentTab,
            fontSize = 15
        )

        self.title_1 = "Match Details"
        self.title_2 = "Opposition Analysis"
        self.title_3 = "Key players to watch"
        self.title_4 = "Last Encounter"
        self.title_5 = "Last lineup"

        self.emailFrame_2 = TeamProfileLabel(
            self.frame,
            self.session,
            homeTeam.manager_id,
            homeTeam.name,
            f"- Fixture: ",
            f" vs ",
            600,
            30,
            self.parent.parentTab,
            fontSize = 15
        )

        self.emailFrame_3 = TeamProfileLabel(
            self.frame,
            self.session,
            awayTeam.manager_id,
            awayTeam.name,
            f"",
            f"",
            600,
            30,
            self.parent.parentTab,
            fontSize = 15
        )

        if len(homeTeam.name) >= 16:
            self.emailFrame_3_x = 0.34
        else:
            self.emailFrame_3_x = 0.32

        self.emailText_2 = (
            f"- Date: \n"
            f"- Kick-off: {self.nextMatch.time}\n"
            f"- Venue: {homeTeam.stadium}\n"
            f"- Weather Forecast: \n"
        )

        if self.matchday == 1:

            self.emailFrame_4 = TeamProfileLabel(
                self.frame,
                self.session,
                self.opponent.manager_id,
                self.opponent.name,
                f"As it is the start of the season, we currently do not have data available on ",
                f".",
                600,
                30,
                self.parent.parentTab,
                fontSize = 15
            )

            self.emailText_3 = (
                f"However, we expect them to be a strong contender based on their performance last season.\n"
                f"Keep an eye on their key players who have shown great potential in the past.\n"
                f"Stay prepared and let's aim for a strong start to the season!"
            )
            
            self.stars = Players.get_all_star_players(self.session, self.opponent.id)
            top_players = min(3, len(self.stars))
            self.emailText_4 = "Here are the top players to watch out for in the upcoming match:\n"

            self.emailFrames_5 = []

            for i in range(top_players):
                player = self.stars[i]
                frame = PlayerProfileLabel(
                    self.frame,
                    self.session,
                    player,
                    f"{player.first_name} {player.last_name}",
                    f"- ",
                    f" ({player.position}, star player)",
                    600,
                    30,
                    self.parent.parentTab,
                    fontSize = 15
                )
                self.emailFrames_5.append(frame)

            self.emailText_4 = self.emailText_4.strip()  # Remove the trailing newline

            self.emailText_6 = (
                f"No games have been played yet this season so we do not have data on {self.opponent.name}'s\n"
                f"last lineup. We expect them to field a strong team and we need to be prepared for any\n"
                f"formation they might use."
            )

        else:
            last5 = Matches.get_team_last_5_matches_from_matchday(self.session, self.opponent.id, self.matchday)
            opponentPosition = self.opponentData.position
            suffix = self.parent.getSuffix(opponentPosition)

            wins = len([match for match in last5 if match.home_id == self.opponent.id and match.score_home > match.score_away or match.away_id == self.opponent.id and match.score_away > match.score_home])
            draws = len([match for match in last5 if match.score_home == match.score_away])
            losses = len(last5) - wins - draws
            goals_scored = sum([match.score_home if match.home_id == self.opponent.id else match.score_away for match in last5])
            goals_conceded = sum([match.score_away if match.home_id == self.opponent.id else match.score_home for match in last5])

            if len(last5) == 1:
                text = "game"
            else:
                text = f"{len(last5)} games"

            results = []
            if wins > 0:
                results.append(f"won {wins}")
            if draws > 0:
                results.append(f"drew {draws}")
            if losses > 0:
                results.append(f"lost {losses}")

            # Join the results with commas
            results_text = ", ".join(results)
            games_played = self.matchday - 1

            self.emailFrame_4 = LeagueProfileLabel(
                self.frame,
                self.session,
                self.parent.manager.id,
                self.parent.league.name,
                f"They are currently {opponentPosition}{suffix} in the ",
                f", with {self.opponentData.points} points from {games_played} match(es) played.",
                600,
                30,
                self.parent.parentTab,
                fontSize = 15
            )

            self.emailText_3 = (
                f"In their last {text}, they have {results_text}. They scored {goals_scored} goals and conceded {goals_conceded}.\n"
                f"Their current top scorer is Name with N goals and their top assist provider is Name with N assists.\n"
                f"Throughout the season, they have kept N clean sheets and have failed to score in N matches."
            )
        
            last5lineups = [TeamLineup.get_lineup_by_match_and_team(self.session, match.id, self.opponent.id) for match in last5]
            best3Players = self.getBest3Players(last5lineups)
            self.emailText_4 = (
                f"Here are the top 3 players to watch out for in the upcoming match:"
            )

            self.emailFrames_5 = []

            for i in range(3):
                player = best3Players[i]['player']
                frame = PlayerProfileLabel(
                    self.frame,
                    self.session,
                    player,
                    f"{player.first_name} {player.last_name}",
                    f"- ",
                    f" ({player.position}, had an average rating of {best3Players[i]['average_rating']} in the last 5 matches)",
                    600,
                    30,
                    self.parent.parentTab,
                    fontSize = 15
                )
                self.emailFrames_5.append(frame)

            lastMatch = Matches.get_team_last_match_from_matchday(self.session, self.opponent.id, self.matchday)

            lastLineup = TeamLineup.get_lineup_by_match_and_team(self.session, lastMatch.id, self.opponent.id)
            defs, mids, fwds = self.countFormation(lastLineup, lastMatch)
            goalkeeper = Players.get_player_by_id(self.session, lastLineup[0].player_id)

            self.emailText_6 = (
                f"In their last match, {self.opponent.name} lined up in a {defs}-{mids}-{fwds} formation. Here is their starting XI:\n"
                f"- Goalkeeper: {goalkeeper.first_name} {goalkeeper.last_name}\n"
            )

            text1 = "- Defenders: "
            for i in range(1, defs + 1):
                player = Players.get_player_by_id(self.session, lastLineup[i].player_id)
                if i != defs:
                    text1 += f"{player.first_name} {player.last_name}, "
                else:
                    text1 += f"{player.first_name} {player.last_name}"

            self.emailText_6 += text1 + "\n"

            # Midfielders
            text2 = "- Midfielders: "
            for i in range(defs + 1, defs + mids + 1):
                player = Players.get_player_by_id(self.session, lastLineup[i].player_id)
                if i != defs + mids:
                    text2 += f"{player.first_name} {player.last_name}, "
                else:
                    text2 += f"{player.first_name} {player.last_name}"

            self.emailText_6 += text2 + "\n"

            # Forwards
            text3 = "- Forwards: "
            for i in range(defs + mids + 1, defs + mids + fwds + 1):
                player = Players.get_player_by_id(self.session, lastLineup[i].player_id)
                if i != defs + mids + fwds:
                    text3 += f"{player.first_name} {player.last_name}, "
                else:
                    text3 += f"{player.first_name} {player.last_name}"

            self.emailText_6 += text3

        lastEncounter = Matches.get_last_encounter_from_matchday(self.session, self.parent.team.id, self.opponent.id, self.matchday)

        if lastEncounter:

            self.emailFrame_6 = TeamProfileLabel(
                self.frame,
                self.session,
                self.opponent.manager_id,
                self.opponent.name,
                f"Our last encounter against ",
                f" ended in {lastEncounter.score_home}-{lastEncounter.score_away}.",
                600,
                30,
                self.parent.parentTab,
                fontSize = 15
            )
        else:

            self.emailFrame_6 = TeamProfileLabel(
                self.frame,
                self.session,
                self.opponent.manager_id,
                self.opponent.name,
                f"We have never faced ",
                f" before.",
                600,
                30,
                self.parent.parentTab,
                fontSize = 15
            )

        self.emailText_7 = (
            "Name, Assistant Manager"
        )

    def getBest3Players(self, lineups):
        players = {}
        for lineup in lineups:
            for player in lineup:
                playerData = Players.get_player_by_id(self.session, player.player_id)
                key = f"{playerData.first_name} {playerData.last_name}"
                if key in players:
                    players[key]['total_rating'] += player.rating
                    players[key]['matches'] += 1
                else:
                    players[key] = {'player': playerData, 'total_rating': player.rating, 'matches': 1}

        # Calculate average rating and sort players by it
        for key in players:
            players[key]['average_rating'] = round(players[key]['total_rating'] / players[key]['matches'], 2)

        sorted_players = sorted(players.values(), key = lambda x: x['average_rating'], reverse = True)
        return sorted_players[:3]

    def countFormation(self, lineup, match):
        position_counts = {"defenders": 0, "midfielders": 0, "attackers": 0}
        events = MatchEvents.get_events_by_match(self.session, match.id)

        for player in lineup:
            
            subbed_on = False
            for event in events:
                if event.event_type == "sub_on" and event.player_id == player.player_id:
                    subbed_on = True

            if not subbed_on:
                if player.position in DEFENSIVE_POSITIONS:
                    position_counts["defenders"] += 1
                elif player.position in MIDFIELD_POSITIONS:
                    position_counts["midfielders"] += 1
                elif player.position in ATTACKING_POSITIONS:
                    position_counts["attackers"] += 1

        return position_counts['defenders'], position_counts['midfielders'], position_counts['attackers']

class PlayerGamesIssue():
    def __init__(self, parent, session):

        self.parent = parent
        self.session = session
        self.frame = self.parent.emailFrame

        self.subject = f"{self.parent.player.last_name} issue"
        self.sender = "Name, Assistant Manager"
        self.subjectFontSize = 20

    def openEmail(self):
        for widget in self.frame.winfo_children():
            widget.place_forget()

class SeasonReview():
    def __init__(self, parent, session):

        self.parent = parent
        self.session = session
        self.frame = self.parent.emailFrame

        self.subject = f"{self.parent.league.year} season review"
        self.sender = "Name, League Journalist"
        self.subjectFontSize = 20

    def openEmail(self):
        for widget in self.frame.winfo_children():
            widget.place_forget()

class SeasonPreview():
    def __init__(self, parent, session):

        self.parent = parent
        self.session = session
        self.frame = self.parent.emailFrame

        self.subject = f"{self.parent.league.year} season preview"
        self.sender = "Name, League Journalist"
        self.subjectFontSize = 20

    def openEmail(self):
        for widget in self.frame.winfo_children():
            widget.place_forget()

class PlayerInjury():
    def __init__(self, parent, session):

        self.parent = parent
        self.session = session
        self.frame = self.parent.emailFrame

        self.subject = f"{self.parent.player.last_name} injury"
        self.sender = "Name, Assistant Manager"
        self.subjectFontSize = 20

    def openEmail(self):
        for widget in self.frame.winfo_children():
            widget.place_forget()

class PlayerBan():
    def __init__(self, parent, session):

        self.parent = parent
        self.session = session
        self.frame = self.parent.emailFrame

        self.subject = f"{self.parent.player.last_name} suspension"
        self.sender = "Name, Assistant Manager"
        self.subjectFontSize = 20

    def openEmail(self):
        for widget in self.frame.winfo_children():
            widget.place_forget()

EMAIL_CLASSES = {
    "welcome": Welcome,
    "matchday_review": MatchdayReview,
    "matchday_preview": MatchdayPreview,
    "player_games_issue": PlayerGamesIssue,
    "season_review": SeasonReview,
    "season_preview": SeasonPreview,
    "player_injury": PlayerInjury,
    "player_ban": PlayerBan
}