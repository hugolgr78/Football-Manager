import customtkinter as ctk
from settings import *
from data.database import *
from data.gamesDatabase import *
from utils.email import *

class Inbox(ctk.CTkFrame):
    def __init__(self, parent, manager_id):
        super().__init__(parent, fg_color = TKINTER_BACKGROUND, width = 1000, height = 700, corner_radius = 0)

        self.parent = parent
        self.manager_id = manager_id

        self.team = Teams.get_teams_by_manager(self.manager_id)[0]
        self.leagueTeams = LeagueTeams.get_league_by_team(self.team.id)
        self.league = League.get_league_by_id(self.leagueTeams.league_id)

        self.emailsFrame = ctk.CTkScrollableFrame(self, width = 280, height = 645, fg_color = TKINTER_BACKGROUND, corner_radius = 0)
        self.emailsFrame.place(x = 0, y = 55, anchor = "nw")

        self.titleFrame = ctk.CTkFrame(self, width = 300, height = 50, fg_color = TKINTER_BACKGROUND, corner_radius = 0)
        self.titleFrame.place(x = 0, y = 0, anchor = "nw")

        ctk.CTkLabel(self.titleFrame, text = "Emails", font = (APP_FONT_BOLD, 30), fg_color = TKINTER_BACKGROUND).place(relx = 0.5, rely = 0.5, anchor = "center")

        self.emailDataFrame = ctk.CTkFrame(self, width = 700, height = 700, fg_color = TKINTER_BACKGROUND, corner_radius = 0)
        self.emailDataFrame.place(x = 300, y = 0, anchor = "nw")
        
        canvas = ctk.CTkCanvas(self, width = 5, height = 1000, bg = GREY_BACKGROUND, bd = 0, highlightthickness = 0)
        canvas.place(x = 370, rely = 0.5, anchor = "w")

        canvas = ctk.CTkCanvas(self, width = 370, height = 5, bg = GREY_BACKGROUND, bd = 0, highlightthickness = 0)
        canvas.place(x = 0, y = 65, anchor = "w")

        self.importEmails()

    def importEmails(self):
        emails = Emails.get_all_emails()

        if not emails:
            self.addEmail("matchday_preview", matchday = 1)
            self.addEmail("welcome")
            self.saveEmail("welcome")
            self.saveEmail("matchday_preview", matchday = 1)

            return

        current_matchday = self.league.current_matchday
        addedEmails = []

        # Add emails
        for matchday in range(current_matchday, 0, -1):
            if matchday <= 38:
                if not Emails.get_email_by_matchday_and_type(matchday, "matchday_preview"):
                    self.addEmail("matchday_preview", matchday = matchday)
                    addedEmails.append(["matchday_preview", matchday])
            if matchday > 1:
                if not Emails.get_email_by_matchday_and_type(matchday - 1, "matchday_review"):
                    self.addEmail("matchday_review", matchday = matchday - 1)
                    addedEmails.append(["matchday_review", matchday - 1])

        for email in reversed(addedEmails):
            self.saveEmail(email[0], matchday = email[1])

        for email in reversed(emails):
            self.addEmail(email.email_type, email.matchday, email.player_id, email.ban_length, email.comp_id)

    def addEmail(self, email_type, matchday = None, player_id = None, ban_length = None, comp_id = None):
        EmailFrame(self.emailsFrame, self.manager_id, email_type, matchday, player_id, ban_length, comp_id, self.emailDataFrame, self)

    def saveEmail(self, email_type, matchday = None, player_id = None, ban_length = None, comp_id = None):
        Emails.add_email(email_type, matchday, player_id, ban_length, comp_id)
