import customtkinter as ctk
from settings import *
from CTkMessagebox import CTkMessagebox
from data.database import DatabaseManager

class SettingsTab(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color = TKINTER_BACKGROUND, width = 1000, height = 700, corner_radius = 0)

        self.parent = parent

        ctk.CTkLabel(self, text = "Settings", font = (APP_FONT_BOLD, 30), fg_color = TKINTER_BACKGROUND).place(relx = 0.02, rely = 0.04, anchor = "w")

        ctk.CTkLabel(self, text = "Save", font = (APP_FONT, 25), fg_color = TKINTER_BACKGROUND).place(relx = 0.02, rely = 0.85, anchor = "w")
        ctk.CTkLabel(self, text = "Quit Game", font = (APP_FONT, 25), fg_color = TKINTER_BACKGROUND).place(relx = 0.02, rely = 0.945, anchor = "w")

        self.saveButton = ctk.CTkButton(self, text = "Save", font = (APP_FONT, 20), height = 40, width = 150, fg_color = APP_BLUE, command = lambda: self.save(exit_ = False))
        self.saveButton.place(relx = 0.18, rely = 0.85, anchor = "w")

        self.saveAndExitButton = ctk.CTkButton(self, text = "Save and Exit", font = (APP_FONT, 20), height = 40, width = 150, fg_color = APP_BLUE, command = lambda: self.save(exit_ = True))
        self.saveAndExitButton.place(relx = 0.35, rely = 0.85, anchor = "w")

        self.mainMenuButton = ctk.CTkButton(self, text = "To Main menu", font = (APP_FONT, 20), height = 40, width = 150, fg_color = APP_BLUE, command = lambda: self.quit_game(menu = True))
        self.mainMenuButton.place(relx = 0.18, rely = 0.95, anchor = "w")

        self.quitButton = ctk.CTkButton(self, text = "To Desktop", font = (APP_FONT, 20), height = 40, width = 150, fg_color = APP_BLUE, command = lambda: self.quit_game(menu = False))
        self.quitButton.place(relx = 0.35, rely = 0.95, anchor = "w")

    def checkSave(self):
        db = DatabaseManager()
        canSave = db.has_unsaved_changes()

        if not canSave:
            self.saveButton.configure(state = "disabled")
            self.saveAndExitButton.configure(state = "disabled")
        else:
            self.saveButton.configure(state = "normal")
            self.saveAndExitButton.configure(state = "normal")

    def quitGame(self, menu):
        response = CTkMessagebox(title = "Exit", message = "Are you sure you want to exit?", icon = "question", option_1 = "Yes", option_2 = "No")

        if response.get() == "Yes":
            if menu:
                from startMenu import StartMenu

                self.loginMenu = StartMenu(self.parent.parent)
                self.parent.destroy()
            else:
                self.parent.quit()

    def save(self, exit_):
        db = DatabaseManager()
        db.commit_copy()

        if exit_:
            self.parent.quit()
        else:
            self.saveButton.configure(state = "disabled")
            self.saveAndExitButton.configure(state = "disabled")