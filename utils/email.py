import customtkinter as ctk
import tkinter.font as tkFont
from settings import *
from data.database import *
from data.gamesDatabase import *
from utils.teamProfileLink import *
from utils.leagueProfileLink import LeagueProfileLabel
from utils.playerProfileLink import *
from utils.teamLogo import TeamLogo
from utils.util_functions import *
from utils.matchProfileLink import MatchProfileLink
from PIL import Image
import io

class EmailFrame(ctk.CTkFrame):
    def __init__(self, parent, manager_id, email, emailFrame, parentTab):
        super().__init__(parent, fg_color = TKINTER_BACKGROUND, width = 260, height = 50)
        self.pack(fill = "both", padx = 10, pady = 5)

        self.parent = parent
        self.manager_id = manager_id
        self.email_id = email.id
        self.email_type = email.email_type
        self.matchday = email.matchday if hasattr(email, 'matchday') else None
        self.player_id = email.player_id if hasattr(email, 'player_id') else None
        self.suspension = email.suspension if hasattr(email, 'suspension') else None
        self.injury = email.injury if hasattr(email, 'injury') else None
        self.comp_id = email.comp_id if hasattr(email, 'comp_id') else None
        self.actioned = email.action_complete
        self.fullDate = email.date
        self.day, self.date, self.time = format_datetime_split(self.fullDate)
        self.emailFrame = emailFrame
        self.parentTab = parentTab
        self.mainMenu = self.parentTab.parent

        self.emailOpen = False

        self.manager = Managers.get_manager_by_id(self.manager_id)
        self.team = Teams.get_teams_by_manager(self.manager_id)[0]
        self.leagueData = LeagueTeams.get_league_by_team(self.team.id)
        self.league = League.get_league_by_id(self.leagueData.league_id)
        self.player = Players.get_player_by_id(self.player_id) if self.player_id else None

        self.email = EMAIL_CLASSES[self.email_type](self)

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
        self.timeLabel.configure(fg_color = DARK_GREY)

    def onFrameLeave(self):
        self.configure(fg_color = TKINTER_BACKGROUND)
        self.subjectLabel.configure(fg_color = TKINTER_BACKGROUND)
        self.senderLabel.configure(fg_color = TKINTER_BACKGROUND)
        self.timeLabel.configure(fg_color = TKINTER_BACKGROUND)

    def displayEmailInfo(self):

        if self.emailOpen:
            return

        self.canvas.place_forget()
        self.configure(border_color = APP_BLUE, border_width = 2)

        self.emailOpen = True

        for emailFrame in self.parent.winfo_children():
            if emailFrame != self and isinstance(emailFrame, EmailFrame):
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

        self.timeLabel = ctk.CTkLabel(self, text = self.time, font = (APP_FONT, 10), height = 8, fg_color = TKINTER_BACKGROUND)
        self.timeLabel.place(relx = 0.95, rely = 0.7, anchor = "e")

        self.subjectLabel.bind("<Enter>", lambda event: self.onFrameHover())
        self.subjectLabel.bind("<Button-1>", lambda e: self.displayEmailInfo())
        self.senderLabel.bind("<Enter>", lambda event: self.onFrameHover())
        self.senderLabel.bind("<Button-1>", lambda e: self.displayEmailInfo())
        self.timeLabel.bind("<Enter>", lambda event: self.onFrameHover())
        self.timeLabel.bind("<Button-1>", lambda e: self.displayEmailInfo())
class Welcome():
    def __init__(self, parent):

        self.parent = parent
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
            f"proudly supports us every step of the way. We play our home matches at {self.parent.team.stadium},\n"
            f"a venue known for its electric atmosphere and passionate crowd."
        )

        teamAverages = Teams.get_average_current_ability_per_team(self.parent.league.id)
        self.emailFrame_3 = LeagueProfileLabel(
            self.frame,
            self.parent.manager.id,
            self.parent.league.name,
            f"Our team competes in the ",
            f", and we’re striving to {get_objective_for_level(teamAverages, self.parent.team.id)} this season.",
            600,
            30,
            self.parent.parentTab,
            fontSize = 15
        )

        teamStrengths = Teams.get_team_strengths(self.parent.league.id)
        expectedFinish = expected_finish(self.parent.team.name, teamStrengths)
        suffix = getSuffix(expectedFinish)
        self.firstMatch = Matches.get_team_first_match(self.parent.team.id)
        homeTeam = Teams.get_team_by_id(self.firstMatch.home_id)
        awayTeam = Teams.get_team_by_id(self.firstMatch.away_id)
        self.opponent = homeTeam if homeTeam.id != self.parent.team.id else awayTeam
        self.venue = "a home" if homeTeam.id == self.parent.team.id else "an away"

        self.title_2 = "Season Objectives"
        self.emailText_3 = (
            f"The board has set the following expectations for the season:"
        )

        self.emailFrame_4 = LeagueProfileLabel(
            self.frame,
            self.parent.manager.id,
            self.parent.league.name,
            f"- League Finish: {expectedFinish}{suffix} place in the ",
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

        self.stars = Players.get_all_star_players(self.parent.team.id)

        self.title_3 = "Key Players"
        self.emailText_4 = "Here are some of the standout players you’ll be working with:"

        player1 = self.stars[0]
        self.emailFrame_6 = PlayerProfileLabel(
            self.frame,
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
    def __init__(self, parent):

        self.parent = parent
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
        ctk.CTkLabel(self.frame, text = self.emailText_3, font = (APP_FONT, 15), justify = "left", text_color = "white").place(relx = 0.05, rely = 0.23, anchor = "w")
        ctk.CTkLabel(self.frame, text = self.emailTitle_1, font = (APP_FONT_BOLD, 20), justify = "left", text_color = "white").place(relx = 0.05, rely = 0.29, anchor = "w")
        self.emailFrame_2.place(relx = 0.05, rely = 0.33, anchor = "w")
        ctk.CTkLabel(self.frame, text = self.emailText_4, font = (APP_FONT, 15), justify = "left", text_color = "white").place(relx = 0.05, rely = 0.36, anchor = "w")
        ctk.CTkLabel(self.frame, text = self.emailText_5, font = (APP_FONT, 15), justify = "left", text_color = "white").place(relx = 0.05, rely = 0.41, anchor = "w")

        for i, frame in enumerate(self.emailFrames_3):
            frame.place(relx = 0.05, rely = 0.44 + i * 0.031, anchor = "w")

        ctk.CTkLabel(self.frame, text = self.emailTitle_2, font = (APP_FONT_BOLD, 20), justify = "left", text_color = "white").place(relx = 0.05, rely = 0.56, anchor = "w")
        ctk.CTkLabel(self.frame, text = self.emailText_6, font = (APP_FONT, 15), justify = "left", text_color = "white").place(relx = 0.05, rely = 0.625, anchor = "w")

    def setUpEmail(self):
        self.emailText_1 = "Here is everything you need to know about the matchday that just passed:"

        self.statsFrame = ctk.CTkFrame(self.frame, fg_color = TKINTER_BACKGROUND, border_color = GREY_BACKGROUND, border_width = 4, width = 250, height = 600)
        self.statsFrame.pack_propagate(0)

        self.matchFrame()

        match_ = Matches.get_team_matchday_match(self.parent.team.id, self.parent.league.id, self.matchday)
        homeTeam = Teams.get_team_by_id(match_.home_id)
        awayTeam = Teams.get_team_by_id(match_.away_id)

        opponentTeam = homeTeam if homeTeam.id != self.parent.team.id else awayTeam
        expectation = get_expectation(Teams.get_team_average_current_ability(self.parent.team.id), Teams.get_team_average_current_ability(opponentTeam.id))
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
            f"The game result was a {result} for our team against"
        )
        
        self.emailFrame_1 = TeamProfileLabel(
            self.frame,
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

        lineups = TeamLineup.get_lineup_by_match(match_.id)
        playerOTM, rating = self.getPlayerOfTheMatch(match_)
        teamBest3 = self.getBest3Players(lineups)

        self.emailTitle_1 = "Player performances"

        self.emailFrame_2 = PlayerProfileLabel(
            self.frame,
            playerOTM,
            f"{playerOTM.first_name} {playerOTM.last_name}",
            "The player of the match was ",
            f" with a",
            240,
            30,
            self.parent.parentTab,
            fontSize = 15
        )

        self.emailText_4 = (
            f"rating of {rating}."
        )

        self.emailText_5 = (
            f"Here are the top 3 players from our team:"
        )

        self.emailFrames_3 = []
        for player in teamBest3:
            playerData = Players.get_player_by_id(player.player_id)

            frame = PlayerProfileLabel(
                self.frame,
                playerData,
                f"{playerData.first_name} {playerData.last_name}",
                f"- ",
                f" with a rating of {player.rating}",
                240,
                30,
                self.parent.parentTab,
                fontSize = 15
            )

            self.emailFrames_3.append(frame)

        self.emailTitle_2 = "League Table"

        teamAverages = Teams.get_average_current_ability_per_team(self.parent.league.id)
        lastMatchdayTable = TeamHistory.get_team_data_matchday(self.parent.team.id, self.matchday - 1)
        matchdayTable = TeamHistory.get_team_data_matchday(self.parent.team.id, self.matchday)
        league = self.parent.league

        currPosition = matchdayTable.position

        suffix = getSuffix(currPosition)
        if not lastMatchdayTable:
            text = f"As a result of this matchday, we are now in {currPosition}{suffix}\nposition."
        else:
            lastPosition = lastMatchdayTable.position
            if currPosition == 1 and lastPosition != 1:
                text = "As a result of this matchday, we have now taken the lead\nof the league!"

            # Promotion zone changes
            elif league.promotion != 0:
                if currPosition <= league.promotion and lastPosition > league.promotion:
                    text = "As a result of this matchday, we have moved up into the\npromotion spots."
                elif currPosition > league.promotion and lastPosition <= league.promotion:
                    text = "As a result of this matchday, we have moved down from the\npromotion spots."

            # Relegation zone changes
            elif currPosition > 20 - league.relegation and lastPosition <= 20 - league.relegation:
                text = "As a result of this matchday, we have moved down into the\nrelegation zone."
            elif currPosition <= 20 - league.relegation and lastPosition > 20 - league.relegation:
                text = "As a result of this matchday, we have climbed out of the\nrelegation zone."

            # Position changes
            elif currPosition < lastPosition:
                text = f"As a result of this matchday, we have moved up into\n{currPosition}{suffix} position."
            elif currPosition > lastPosition:
                text = f"As a result of this matchday, we have moved down into\n{currPosition}{suffix} position."

            # No change
            else:
                text = f"As a result of this matchday, we have stayed in\n{currPosition}{suffix} position."

        self.emailText_6 = (text)

        if currPosition == 1:
            secondPlace = TeamHistory.get_team_data_position(2, self.matchday)
            pointsDiff = matchdayTable.points - secondPlace.points
            text = f"We are currently leading second place by\n{pointsDiff} points, good work!"
        elif currPosition > 17:
            aboveRel = TeamHistory.get_team_data_position(20 - league.relegation, self.matchday)
            pointsDiff = aboveRel.points - matchdayTable.points
            text = f"We currently need {pointsDiff} points to get out of the\nrelegation zone."
        elif currPosition <= 10 and currPosition > 5:
            text = f"We have settled nicely within the top ten of\nthe league, "

            teamObjective = get_objective_for_level(teamAverages, self.parent.team.id)

            if teamObjective == "fight for the title":
                text += "let's keep pushing."
            elif teamObjective == "finish in the top half":
                text += "great work!"
            else:
                text += "fantastic work, the fans are delighted!"
        elif currPosition <= 5:
            firstPlace = TeamHistory.get_team_data_position(1, self.matchday)
            pointsDiff = firstPlace.points - matchdayTable.points
            text = f"We are currently {pointsDiff} points behind the\nleader."
        elif currPosition >= 11 and currPosition < 18 - league.relegation:
            text = f"We are well above relegation,"

            teamObjective = get_objective_for_level(teamAverages, self.parent.team.id)

            if teamObjective == "fight for the title":
                text += " but the\nfans are dissapointed."
            elif teamObjective == "finish in the top half":
                text += " let's keep\npushing."
            else:
                text += " great work!"
        else:
            firstRelegated = TeamHistory.get_team_data_position(21 - league.relegation, self.matchday)
            pointsDiff = matchdayTable.points - firstRelegated.points
            text = f"We are currently {pointsDiff} points ahead of the\nrelegation spots."

        self.emailText_6 += " " + text

    def getBest3Players(self, lineups):
        bestPlayers = []
        for lineup in lineups:
            player = Players.get_player_by_id(lineup.player_id)
            
            if player.team_id != self.parent.team.id:
                continue

            bestPlayers.append(lineup)

        bestPlayers.sort(key = lambda x: x.rating, reverse = True)
        
        return bestPlayers[:3]

    def matchFrame(self):
        matches = Matches.get_matchday_for_league(self.parent.league.id, self.matchday)
        bestMatch = self.findBestMatch(matches)
        bestPlayer, events, rating = self.findBestPlayer(matches)

        matchFrame = ctk.CTkFrame(self.statsFrame, fg_color = TKINTER_BACKGROUND, width = 240, height = 250)
        matchFrame.pack(fill = "both", padx = 5, pady = 5)

        ctk.CTkLabel(matchFrame, text = "Best showing:", font = (APP_FONT_BOLD, 25), fg_color = TKINTER_BACKGROUND).place(relx = 0.5, rely = 0.15, anchor = "center")

        homeTeam = Teams.get_team_by_id(bestMatch.home_id)
        homeImage = Image.open(io.BytesIO(homeTeam.logo))
        homeImage.thumbnail((75,  75))
        TeamLogo(matchFrame, homeImage, homeTeam, TKINTER_BACKGROUND, 0.2, 0.45, "center", self.parent.parentTab)

        ctk.CTkLabel(matchFrame, text = homeTeam.name.split()[0], font = (APP_FONT, 13), fg_color = TKINTER_BACKGROUND).place(relx = 0.2, rely = 0.65, anchor = "center")
        ctk.CTkLabel(matchFrame, text = homeTeam.name.split()[1], font = (APP_FONT_BOLD, 18), fg_color = TKINTER_BACKGROUND).place(relx = 0.2, rely = 0.75, anchor = "center")

        awayTeam = Teams.get_team_by_id(bestMatch.away_id)
        awayImage = Image.open(io.BytesIO(awayTeam.logo))
        awayImage.thumbnail((75,  75))
        TeamLogo(matchFrame, awayImage, awayTeam, TKINTER_BACKGROUND, 0.8, 0.45, "center", self.parent.parentTab)

        ctk.CTkLabel(matchFrame, text = awayTeam.name.split()[0], font = (APP_FONT, 13), fg_color = TKINTER_BACKGROUND).place(relx = 0.8, rely = 0.65, anchor = "center")
        ctk.CTkLabel(matchFrame, text = awayTeam.name.split()[1], font = (APP_FONT_BOLD, 18), fg_color = TKINTER_BACKGROUND).place(relx = 0.8, rely = 0.75, anchor = "center")

        MatchProfileLink(matchFrame, bestMatch, f"{bestMatch.score_home} - {bestMatch.score_away}", "white", 0.5, 0.5, "center", TKINTER_BACKGROUND, self.parent.parentTab, 25, APP_FONT_BOLD)

        playerOTM, _ = self.getPlayerOfTheMatch(bestMatch)

        ctk.CTkLabel(matchFrame, text = f"POTM: ", font = (APP_FONT, 18), fg_color = TKINTER_BACKGROUND).place(relx = 0.05, rely = 0.92, anchor = "w")
        PlayerProfileLink(matchFrame, playerOTM, f"{playerOTM.first_name} {playerOTM.last_name}", "white", 0.31, 0.92, "w", TKINTER_BACKGROUND, self.parent.parentTab, fontSize = 18)

        canvas = ctk.CTkCanvas(self.statsFrame, width = 10, height = 5, bg = GREY_BACKGROUND, bd = 0, highlightthickness = 0)
        canvas.pack(fill = "both", padx = 5, pady = 5)  

        playerFrame = ctk.CTkFrame(self.statsFrame, fg_color = TKINTER_BACKGROUND, width = 240, height = 250)
        playerFrame.pack(fill = "both", padx = 5, pady = 5)

        ctk.CTkLabel(playerFrame, text = "Best player:", font = (APP_FONT_BOLD, 25), fg_color = TKINTER_BACKGROUND).place(relx = 0.5, rely = 0.1, anchor = "center")

        src = Image.open("Images/default_user.png")
        src.thumbnail((75,  75))
        playerImage = ctk.CTkImage(src, None, (src.width, src.height))
        ctk.CTkLabel(playerFrame, image = playerImage, text = "", fg_color = TKINTER_BACKGROUND).place(relx = 0.2, rely = 0.4, anchor = "center")

        PlayerProfileLink(playerFrame, bestPlayer, f"{bestPlayer.first_name} {bestPlayer.last_name}", "white", 0.45, 0.35, "w", TKINTER_BACKGROUND, self.parent.parentTab, fontSize = 15)
        playerTeam = Teams.get_team_by_id(bestPlayer.team_id)
        TeamProfileLink(playerFrame, playerTeam.manager_id, playerTeam.name, "white", 0.45, 0.45, "w", TKINTER_BACKGROUND, self.parent.parentTab, fontSize = 12)

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
            lineupHome = TeamLineup.get_lineup_by_match_and_team(match.id, match.home_id)
            lineupAway = TeamLineup.get_lineup_by_match_and_team(match.id, match.away_id)

            for player in lineupHome:
                if player.rating > highestRating:
                    highestRating = player.rating
                    playerData = Players.get_player_by_id(player.player_id)
                    currPlayer = playerData
                    playerEvents = MatchEvents.get_events_by_match_and_player(match.id, player.player_id)

            for player in lineupAway:
                if player.rating > highestRating:
                    highestRating = player.rating
                    playerData = Players.get_player_by_id(player.player_id)
                    currPlayer = playerData
                    playerEvents = MatchEvents.get_events_by_match_and_player(match.id, player.player_id)
        
        return currPlayer, playerEvents, highestRating
    
    def getPlayerOfTheMatch(self, match):
        highestRating = 0
        currPlayer = None

        lineupHome = TeamLineup.get_lineup_by_match_and_team(match.id, match.home_id)
        lineupAway = TeamLineup.get_lineup_by_match_and_team(match.id, match.away_id)

        for player in lineupHome:
            if player.rating > highestRating:
                highestRating = player.rating
                playerData = Players.get_player_by_id(player.player_id)
                currPlayer = playerData

        for player in lineupAway:
            if player.rating > highestRating:
                highestRating = player.rating
                playerData = Players.get_player_by_id(player.player_id)
                currPlayer = playerData

        return currPlayer, highestRating

class MatchdayPreview():
    def __init__(self, parent):

        self.parent = parent
        self.frame = self.parent.emailFrame
        self.matchday = self.parent.matchday

        self.nextMatch = Matches.get_team_matchday_match(self.parent.team.id, self.parent.league.id, self.matchday)
        self.homeTeam = Teams.get_team_by_id(self.nextMatch.home_id)
        self.awayTeam = Teams.get_team_by_id(self.nextMatch.away_id)
        self.opponent = self.homeTeam if self.homeTeam.id != self.parent.team.id else self.awayTeam
        self.opponentData = TeamHistory.get_team_data_matchday(self.opponent.id, self.matchday - 1)

        self.subject = f"{self.opponent.name} preview"
        self.sender = "Name, Assistant Manager"
        self.subjectFontSize = 20 if len(self.subject) < 20 else 15

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
        ctk.CTkLabel(self.frame, text = self.emailText_3, font = (APP_FONT, 15), justify = "left", text_color = "white").place(relx = 0.05, rely = 0.405, anchor = "nw")

        if self.matchday != 1:
            self.emailText_5 = ctk.CTkLabel(self.frame, text = "For more information, you can open your analysis tab by going to Tactics -> Analysis", font = (APP_FONT, 15), justify = "left", text_color = "white")
            self.emailText_5.place(relx = 0.05, rely = 0.428, anchor = "nw")
            
            self.analysisButton = ctk.CTkButton(self.frame, text = "Go to Analysis", font = (APP_FONT_BOLD, 15), command = lambda: self.goToAnalysis(), width = 200, height = 40, corner_radius = 8, fg_color = DARK_GREY, hover_color = GREY_BACKGROUND)
            self.analysisButton.place(relx = 0.95, rely = 0.88, anchor = "se")
        
        ctk.CTkLabel(self.frame, text = self.title_3, font = (APP_FONT_BOLD, 20), justify = "left", text_color = "white").place(relx = 0.05, rely = 0.5, anchor = "nw")
        ctk.CTkLabel(self.frame, text = self.emailText_4, font = (APP_FONT, 15), justify = "left", text_color = "white").place(relx = 0.05, rely = 0.95, anchor = "nw")

        self.tacticsButton = ctk.CTkButton(self.frame, text = "Select Lineup", font = (APP_FONT_BOLD, 15), command = lambda: self.gotToTactics(), width = 200, height = 40, corner_radius = 8, fg_color = DARK_GREY, hover_color = GREY_BACKGROUND)
        self.tacticsButton.place(relx = 0.95, rely = 0.95, anchor = "se")


    def setUpEmail(self):

        font = tkFont.Font(family = APP_FONT, size = 15)
        text_width_px = font.measure(self.homeTeam.name)

        # Measure parent frame width (fallback to fixed value if needed)
        frame_width_px = self.frame.winfo_width() or 800

        # Convert to relx
        rel_offset = 0.165 + (text_width_px / frame_width_px) 

        self.emailFrame_3_x = rel_offset

        self.emailFrame_1 = TeamProfileLabel(
            self.frame,
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

        self.emailFrame_2 = TeamProfileLabel(
            self.frame,
            self.homeTeam.manager_id,
            self.homeTeam.name,
            f"- Fixture: ",
            f" vs ",
            600,
            30,
            self.parent.parentTab,
            fontSize = 15
        )

        self.emailFrame_3 = TeamProfileLabel(
            self.frame,
            self.awayTeam.manager_id,
            self.awayTeam.name,
            f"",
            f"",
            600,
            30,
            self.parent.parentTab,
            fontSize = 15
        )

        day, text, time = format_datetime_split(self.nextMatch.date)

        self.emailText_2 = (
            f"- Date: {day} {text}\n"
            f"- Kick-off: {time}\n"
            f"- Venue: {self.homeTeam.stadium}\n"
            f"- Weather Forecast: \n"
        )

        if self.matchday == 1:

            self.emailFrame_4 = TeamProfileLabel(
                self.frame,
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

        else:
            last5 = Matches.get_team_last_5_matches(self.opponent.id, Game.get_game_date(Managers.get_all_user_managers()[0].id))
            opponentPosition = self.opponentData.position
            suffix = getSuffix(opponentPosition)

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
                results.append(f"drawn {draws}")
            if losses > 0:
                results.append(f"lost {losses}")

            # Join the results with commas
            results_text = ", ".join(results)
            games_played = self.matchday - 1

            self.emailFrame_4 = LeagueProfileLabel(
                self.frame,
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
            )

        self.title_3 = "Proposed Lineup"

        self.proposedLineup = getProposedLineup(self.parent.team.id, self.opponent.id, self.parent.league.id, Game.get_game_date(self.parent.manager.id))

        self.playersFrame = ctk.CTkFrame(self.frame, fg_color = TKINTER_BACKGROUND, width = 400, height = 250)
        self.playersFrame.place(relx = 0.035, rely = 0.55, anchor = "nw")
        self.playersFrame.pack_propagate(False)

        for position, playerID in self.proposedLineup.items():
            player = Players.get_player_by_id(playerID)

            frame = ctk.CTkFrame(self.playersFrame, fg_color = TKINTER_BACKGROUND, width = 150, height = 20)
            frame.pack(expand = True, fill = "x", padx = 2, pady = (0, 3))
            ctk.CTkLabel(frame, text = f"{POSITION_CODES[position]}", font = (APP_FONT, 15), text_color = "white", fg_color = TKINTER_BACKGROUND).place(relx = 0.02, rely = 0.5, anchor = "w")
            ctk.CTkLabel(frame, text = "-", font = (APP_FONT, 15), text_color = "white", fg_color = TKINTER_BACKGROUND).place(relx = 0.1, rely = 0.5, anchor = "w")
            PlayerProfileLink(frame, player, f"{player.first_name} {player.last_name}", "white", 0.13, 0.5, "w", TKINTER_BACKGROUND, self.parent.parentTab, 15)

        self.emailText_4 = (
            "Name, Assistant Manager"
        )

    def gotToTactics(self):
        self.parent.mainMenu.changeTab(4)
        self.parent.mainMenu.update_idletasks()
        self.parent.mainMenu.tabs[4].changeTab(0)
        self.parent.mainMenu.tabs[4].activateProposed(self.proposedLineup)

    def goToAnalysis(self):
        self.parent.mainMenu.changeTab(4)
        self.parent.mainMenu.tabs[4].changeTab(1)

class PlayerGamesIssue():
    def __init__(self, parent):

        self.parent = parent
        self.frame = self.parent.emailFrame

        self.subject = f"{self.parent.player.last_name} issue"
        self.sender = "Name, Assistant Manager"
        self.subjectFontSize = 20

    def openEmail(self):
        for widget in self.frame.winfo_children():
            widget.place_forget()

class SeasonReview():
    def __init__(self, parent):

        self.parent = parent
        self.frame = self.parent.emailFrame

        self.subject = f"{self.parent.league.year} season review"
        self.sender = "Name, League Journalist"
        self.subjectFontSize = 20

    def openEmail(self):
        for widget in self.frame.winfo_children():
            widget.place_forget()

class SeasonPreview():
    def __init__(self, parent):

        self.parent = parent
        self.frame = self.parent.emailFrame

        self.subject = f"{self.parent.league.year} season preview"
        self.sender = "Name, League Journalist"
        self.subjectFontSize = 20

    def openEmail(self):
        for widget in self.frame.winfo_children():
            widget.place_forget()

class PlayerInjury():
    def __init__(self, parent):

        self.parent = parent
        self.frame = self.parent.emailFrame

        self.subject = f"{self.parent.player.last_name} injury"
        self.sender = "Name, Assistant Manager"
        self.subjectFontSize = 20

    def openEmail(self):
        for widget in self.frame.winfo_children():
            widget.place_forget()

        self.setUpEmail()

        self.emailTitle = ctk.CTkLabel(self.frame, text = self.subject, font = (APP_FONT_BOLD, 30))
        self.emailTitle.place(relx = 0.05, rely = 0.05, anchor = "w")

        self.emailFrame_1.place(relx = 0.05, rely = 0.1, anchor = "w")
        ctk.CTkLabel(self.frame, text = self.emailText_1, font = (APP_FONT, 15), justify = "left", text_color = "white").place(relx = 0.05, rely = 0.131, anchor = "w")

        ctk.CTkLabel(self.frame, text = self.emailText_2, font = (APP_FONT, 15), justify = "left", text_color = "white").place(relx = 0.05, rely = 0.18, anchor = "w")

    def setUpEmail(self):

        self.emailFrame_1 = PlayerProfileLabel(
            self.frame,
            self.parent.player,
            f"{self.parent.player.first_name} {self.parent.player.last_name}",
            "I regret to inform you that ",
            " has suffered an injury.",
            240,
            30,
            self.parent.parentTab,
            fontSize = 15
        )

        injuryTime = self.parent.injury - self.parent.fullDate
        months = injuryTime.days // 30
        remainingDays = injuryTime.days % 30
        self.emailText_1 = f"We expect him to be out for at least {months} M and {remainingDays} D."

        self.emailText_2 = "Name, Assistant Manager"

class PlayerBan():
    def __init__(self, parent):

        self.parent = parent
        self.frame = self.parent.emailFrame

        self.subject = f"{self.parent.player.last_name} suspension"
        self.sender = "Name, Assistant Manager"
        self.subjectFontSize = 20

    def openEmail(self):
        for widget in self.frame.winfo_children():
            widget.place_forget()

        self.setUpEmail()

        self.emailTitle = ctk.CTkLabel(self.frame, text = self.subject, font = (APP_FONT_BOLD, 30))
        self.emailTitle.place(relx = 0.05, rely = 0.05, anchor = "w")

        self.emailFrame_1.place(relx = 0.05, rely = 0.12, anchor = "w")
        self.emailFrame_2.place(relx = 0.05, rely = 0.151, anchor = "w")

        ctk.CTkLabel(self.frame, text = self.emailText_1, font = (APP_FONT, 15), justify = "left", text_color = "white").place(relx = 0.05, rely = 0.2, anchor = "w")

    def setUpEmail(self):

        competition = League.get_league_by_id(self.parent.comp_id)

        self.emailFrame_1 = PlayerProfileLabel(
            self.frame,
            self.parent.player,
            f"{self.parent.player.first_name} {self.parent.player.last_name}",
            "I regret to inform you that ",
            " has picked up a suspension.",
            240,
            30,
            self.parent.parentTab,
            fontSize = 15
        )

        self.emailFrame_2 = LeagueProfileLabel(
            self.frame,
            self.parent.manager_id,
            f"{competition.name}",
            f"He will miss {self.parent.suspension} match(es) in the ",
            ".",
            240,
            30,
            self.parent.parentTab,
            fontSize = 15
        )

        self.emailText_1 = "Name, Assistant Manager"

class PlayerBirthday():
    def __init__(self, parent):

        self.parent = parent
        self.frame = self.parent.emailFrame

        self.subject = f"{self.parent.player.last_name} birthday"
        self.sender = "Name, Assistant Manager"
        self.subjectFontSize = 20

    def openEmail(self):
        for widget in self.frame.winfo_children():
            widget.place_forget()

        self.setUpEmail()

        self.emailTitle = ctk.CTkLabel(self.frame, text = self.subject, font = (APP_FONT_BOLD, 30))
        self.emailTitle.place(relx = 0.05, rely = 0.05, anchor = "w")

        self.emailFrame_1.place(relx = 0.05, rely = 0.1, anchor = "w")
        ctk.CTkLabel(self.frame, text = self.emailText_1, font = (APP_FONT, 15), justify = "left", text_color = "white").place(relx = 0.05, rely = 0.131, anchor = "w")

        ctk.CTkLabel(self.frame, text = self.emailText_2, font = (APP_FONT, 15), justify = "left", text_color = "white").place(relx = 0.05, rely = 0.18, anchor = "w")

        self.button = ctk.CTkButton(self.frame, text = "Send Birthday Wishes", font = (APP_FONT_BOLD, 15), command = lambda: self.sendBirthdayWish(), width = 200, height = 40, corner_radius = 8, fg_color = DARK_GREY, hover_color = GREY_BACKGROUND)
        self.button.place(relx = 0.95, rely = 0.95, anchor = "se")

        if self.parent.actioned:
            self.button.configure(state = "disabled")

    def setUpEmail(self):

        self.emailFrame_1 = PlayerProfileLabel(
            self.frame,
            self.parent.player,
            f"{self.parent.player.first_name} {self.parent.player.last_name}",
            "I am pleased to inform you that today is ",
            "'s birthday.",
            240,
            30,
            self.parent.parentTab,
            fontSize = 15
        )

        self.emailText_1 = f"Feel free to wish him a happy birthday!"
        self.emailText_2 = "Name, Assistant Manager"

    def sendBirthdayWish(self):
        Players.update_morale(self.parent.player.id, 10)
        self.button.configure(state = "disabled")

        Emails.update_action(self.parent.email_id)

EMAIL_CLASSES = {
    "welcome": Welcome,
    "matchday_review": MatchdayReview,
    "matchday_preview": MatchdayPreview,
    "player_games_issue": PlayerGamesIssue,
    "season_review": SeasonReview,
    "season_preview": SeasonPreview,
    "player_injury": PlayerInjury,
    "player_ban": PlayerBan,
    "player_birthday": PlayerBirthday
}