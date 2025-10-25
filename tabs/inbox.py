import customtkinter as ctk
from settings import *
from data.database import *
from data.gamesDatabase import *
from utils.email import *
from utils.util_functions import *

class Inbox(ctk.CTkFrame):
    def __init__(self, parent):
        """
        Inbox tab where the user can see all their emails.
        
        Args:
            parent (ctk.CTkFrame): The parent frame (main menu) where the Inbox tab will be placed.
        """

        super().__init__(parent, fg_color = TKINTER_BACKGROUND, width = 1000, height = 700, corner_radius = 0)

        self.parent = parent
        self.manager_id = Managers.get_all_user_managers()[0].id

        self.emailsToAdd = {}
        self.currentEmail = None
        self.frames = []

        self.team = Teams.get_teams_by_manager(self.manager_id)[0]
        self.leagueTeams = LeagueTeams.get_league_by_team(self.team.id)
        self.league = League.get_league_by_id(self.leagueTeams.league_id)

        self.emailsFrame = ctk.CTkScrollableFrame(self, width = 280, height = 645, fg_color = TKINTER_BACKGROUND, corner_radius = 0)
        self.emailsFrame.place(x = 0, y = 55, anchor = "nw")

        self.titleFrame = ctk.CTkFrame(self, width = 300, height = 50, fg_color = TKINTER_BACKGROUND, corner_radius = 0)
        self.titleFrame.place(x = 0, y = 0, anchor = "nw")

        ctk.CTkLabel(self.titleFrame, text = "Emails", font = (APP_FONT_BOLD, 30), fg_color = TKINTER_BACKGROUND).place(relx = 0.5, rely = 0.5, anchor = "center")

        src = Image.open("Images/read.png")
        src.thumbnail((20, 20))
        img = ctk.CTkImage(src, None, (src.width, src.height))
        self.readAllButton = ctk.CTkButton(self.titleFrame, text = "", image = img, fg_color = TKINTER_BACKGROUND, hover_color = TKINTER_BACKGROUND, command = self.markAllAsRead, state = "disabled", height = 0, width = 0)
        self.readAllButton.place(relx = 0.98, rely = 0.95, anchor = "se")

        self.emailDataFrame = ctk.CTkFrame(self, width = 700, height = 700, fg_color = TKINTER_BACKGROUND, corner_radius = 0)
        self.emailDataFrame.place(x = 300, y = 0, anchor = "nw")
        
        canvas = ctk.CTkCanvas(self, width = 5, height = 1000, bg = GREY_BACKGROUND, bd = 0, highlightthickness = 0)
        canvas.place(x = 370, rely = 0.5, anchor = "w")

        canvas = ctk.CTkCanvas(self, width = 370, height = 5, bg = GREY_BACKGROUND, bd = 0, highlightthickness = 0)
        canvas.place(x = 0, y = 65, anchor = "w")

        self.addEmails()

    def resetOpenEmail(self):
        """
        Reopens a currently opened calendar events email, if any (to update the content).
        """
        
        if self.currentEmail and self.currentEmail.email_type == "calendar_events":

            for widget in self.emailDataFrame.winfo_children():
                widget.destroy()

            self.currentEmail.email.openEmail()

    def addEmails(self):
        """
        Adds all emails to the emails frame, grouped by date.
        """
        
        self.emails = Emails.get_all_emails(Game.get_game_date(self.manager_id))
        unread = False

        currentDate = ""
        for email in self.emails:

            if not email.read:
                unread = True

            _, date, _ = format_datetime_split(email.date)
            if date != currentDate:
                currentDate = date

                frame = ctk.CTkFrame(self.emailsFrame, fg_color = TKINTER_BACKGROUND, width = 260, height = 50)
                frame.pack(fill = "both", padx = 10, pady = 5)

                ctk.CTkLabel(frame, text = date, font = (APP_FONT_BOLD, 20), fg_color = TKINTER_BACKGROUND).place(relx = 0, rely = 0.5, anchor = "w")

            self.addEmail(email)

        if unread:
            self.parent.addInboxNotification()
            self.readAllButton.configure(state = "normal")

    def addEmail(self, email):
        """
        Adds a single email to the emails frame.
        """
        
        frame = EmailFrame(self.emailsFrame, self.manager_id, email, self.emailDataFrame, self)
        self.frames.append(frame)

    def removeNotificationDot(self):
        """
        Removes the notification dot from the Inbox tab in the main menu.
        """

        emails = Emails.get_all_emails(Game.get_game_date(self.manager_id))
        for email in emails:
            if not email.read:
                return
            
        self.readAllButton.configure(state = "disabled")
        self.parent.removeInboxNotification()   

    def markAllAsRead(self):


        Emails.batch_mark_all_as_read(Game.get_game_date(self.manager_id))

        for frame in self.frames:
            frame.updateReadStatus()

        self.readAllButton.configure(state = "disabled")
        self.parent.removeInboxNotification()