import customtkinter as ctk
from settings import *
from CTkMessagebox import CTkMessagebox
from data.database import DatabaseManager, SavedLineups, Settings, Emails, League
from data.gamesDatabase import Game
from utils.frames import ChoosingLeagueFrame

class SettingsTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color = TKINTER_BACKGROUND, width = 1000, height = 700, corner_radius = 0)

        self.parent = parent

        ctk.CTkLabel(self, text = "Settings", font = (APP_FONT_BOLD, 30), fg_color = TKINTER_BACKGROUND).place(relx = 0.02, rely = 0.04, anchor = "w")
        ctk.CTkLabel(self, text = "Delegate events", font = (APP_FONT, 20), fg_color = TKINTER_BACKGROUND).place(relx = 0.02, rely = 0.15, anchor = "w")

        delegated = Settings.get_setting("events_delegated")
        self.delegateVar = ctk.BooleanVar(value=delegated)

        self.delegateOn = ctk.CTkSwitch(
            self,
            text="",
            font=(APP_FONT, 15),
            fg_color=TKINTER_BACKGROUND,
            variable=self.delegateVar,
            command=self.toggleDelegate,
            onvalue=True,
            offvalue=False
        )
        self.delegateOn.place(relx = 0.18, rely = 0.15, anchor = "w")

        ctk.CTkLabel(self, text = "Loaded leagues", font = (APP_FONT, 20), fg_color = TKINTER_BACKGROUND).place(relx = 0.02, rely = 0.22, anchor = "w")
        self.leaguesButton = ctk.CTkButton(self, text = "Change", font = (APP_FONT, 15), height = 40, width = 200, fg_color = APP_BLUE, command = lambda: self.chooseLeagues())
        self.leaguesButton.place(relx = 0.18, rely = 0.22, anchor = "w")

        ctk.CTkLabel(self, text = "Save", font = (APP_FONT, 25), fg_color = TKINTER_BACKGROUND).place(relx = 0.02, rely = 0.85, anchor = "w")
        ctk.CTkLabel(self, text = "Quit Game", font = (APP_FONT, 25), fg_color = TKINTER_BACKGROUND).place(relx = 0.02, rely = 0.945, anchor = "w")

        self.saveButton = ctk.CTkButton(self, text = "Save", font = (APP_FONT, 20), height = 40, width = 150, fg_color = APP_BLUE, command = lambda: self.save(exit_ = False))
        self.saveButton.place(relx = 0.18, rely = 0.85, anchor = "w")

        self.saveAndExitButton = ctk.CTkButton(self, text = "Save and Exit", font = (APP_FONT, 20), height = 40, width = 150, fg_color = APP_BLUE, command = lambda: self.save(exit_ = True))
        self.saveAndExitButton.place(relx = 0.35, rely = 0.85, anchor = "w")

        self.mainMenuButton = ctk.CTkButton(self, text = "To Main menu", font = (APP_FONT, 20), height = 40, width = 150, fg_color = APP_BLUE, command = lambda: self.quitGame(menu = True))
        self.mainMenuButton.place(relx = 0.18, rely = 0.95, anchor = "w")

        self.quitButton = ctk.CTkButton(self, text = "To Desktop", font = (APP_FONT, 20), height = 40, width = 150, fg_color = APP_BLUE, command = lambda: self.quitGame(menu = False))
        self.quitButton.place(relx = 0.35, rely = 0.95, anchor = "w")

    def updateSettings(self):
        delegated = Settings.get_setting("events_delegated")
        self.delegateVar.set(delegated)

        if not delegated:
            self.delegateOn.configure(text="Off")
        else:
            self.delegateOn.configure(text="On")

        self.checkSave()

    def toggleDelegate(self):
        Settings.set_setting("events_delegated", self.delegateVar.get())
        Emails.toggle_send_calendar_emails(Game.get_game_date(self.parent.manager_id))

        if self.delegateVar.get():
            self.delegateOn.configure(text="On")
        else:
            self.delegateOn.configure(text="Off")

        self.checkSave()

    def chooseLeagues(self):
        self.chooseLeaguesFrame = ChoosingLeagueFrame(self.parent, fgColor = TKINTER_BACKGROUND, width = 1200, height = 700, corner_radius = 0, border_width = 0, border_color = APP_BLUE, endFunction = self.finishLeagues, settings = True)
        self.chooseLeaguesFrame.place(relx = 0.5, rely = 0.5, anchor = "center")

    def finishLeagues(self):
        self.chooseLeaguesFrame.place_forget()
        leagues = League.get_all_leagues()

        loadedLeagues = {}
        for league in leagues:
            loadedLeagues[league.name] = 1 if league.to_be_loaded else 0

        if loadedLeagues != self.chooseLeaguesFrame.loadedLeagues:
            League.update_loaded_leagues(self.chooseLeaguesFrame.loadedLeagues)
            self.checkSave()

    def checkSave(self):
        db = DatabaseManager()
        self.canSave = db.has_unsaved_changes()

        if not self.canSave:
            self.saveButton.configure(state = "disabled")
            self.saveAndExitButton.configure(state = "disabled")
        else:
            self.saveButton.configure(state = "normal")
            self.saveAndExitButton.configure(state = "normal")

    def quitGame(self, menu):
        if self.canSave:
            response = CTkMessagebox(
                title="Exit",
                message="Would you like to save before quitting?",
                icon="question",
                option_1="Save and Exit",
                option_2="Exit without Saving",
                option_3="Cancel",
                button_color=(CLOSE_RED, APP_BLUE, APP_BLUE),
                button_hover_color=(CLOSE_RED, APP_BLUE, APP_BLUE)
            )

            try:
                if hasattr(response, "button_1"):
                    response.button_1.configure(hover_color=CLOSE_RED)
                if hasattr(response, "button_2"):
                    response.button_2.configure(hover_color=APP_BLUE)
                if hasattr(response, "button_3"):
                    response.button_3.configure(hover_color=APP_BLUE)
            except Exception:
                pass

            choice = response.get()

            if choice == "Save and Exit":
                self.save(exit_=False)
                self.exit_(menu)

            elif choice == "Exit without Saving":
                self.rollBack()
                self.exit_(menu)

        else:
            response = CTkMessagebox(
                title="Exit",
                message="Are you sure you want to exit?",
                icon="question",
                option_1="Yes",
                option_2="No",
                button_color=(CLOSE_RED, APP_BLUE),
                button_hover_color=(CLOSE_RED, APP_BLUE)
            )

            try:
                if hasattr(response, "button_1"):
                    response.button_1.configure(hover_color=CLOSE_RED)
                if hasattr(response, "button_2"):
                    response.button_2.configure(hover_color=APP_BLUE)
            except Exception:
                pass

            if response.get() == "Yes":
                self.exit_(menu)

    def exit_(self, menu):
        if menu:
            from startMenu import StartMenu

            self.loginMenu = StartMenu(self.parent.parent)
            self.parent.destroy()
        else:
            self.parent.quit()

    def save(self, exit_):
        if self.parent.tabs[4]:
            SavedLineups.delete_current_lineup()
            self.parent.tabs[4].saveLineup()

        db = DatabaseManager()
        db.commit_copy()

        if exit_:

            response = CTkMessagebox(
                title="Exit",
                message="Are you sure you want to exit?",
                icon="question",
                option_1="Yes",
                option_2="No",
                button_color=(CLOSE_RED, APP_BLUE),
                button_hover_color=(CLOSE_RED, APP_BLUE)
            )
            try:
                if hasattr(response, "button_1"):
                    response.button_1.configure(hover_color=CLOSE_RED)
                if hasattr(response, "button_2"):
                    response.button_2.configure(hover_color=APP_BLUE)
            except Exception:
                pass

            if response.get() == "Yes":
                self.parent.quit()
            else:
                self.saveButton.configure(state = "disabled")
                self.saveAndExitButton.configure(state = "disabled")
                self.canSave = False
        else:
            self.saveButton.configure(state = "disabled")
            self.saveAndExitButton.configure(state = "disabled")
            self.canSave = False

    def rollBack(self):
        db = DatabaseManager()
        db.discard_copy()