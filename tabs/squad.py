import customtkinter as ctk
from settings import *
from data.database import *
from data.gamesDatabase import *
from PIL import Image
from utils.frames import PlayerFrame
from utils.util_functions import *

class Squad(ctk.CTkFrame):
    def __init__(self, parent, manager_id):
        super().__init__(parent, fg_color = TKINTER_BACKGROUND, width = 1000, height = 700, corner_radius = 0)

        self.parent = parent
        self.manager_id = manager_id

        self.talkedTo = []
        self.playerInjured = False

        self.team = Teams.get_teams_by_manager(manager_id)[0]
        self.players = Players.get_all_players_by_team(self.team.id)

        self.titleFrame = ctk.CTkFrame(self, fg_color = TKINTER_BACKGROUND, width = 1000, height = 100, corner_radius = 0)
        self.titleFrame.pack(expand = True, fill = "both", padx = 10, pady = 10)

        ctk.CTkLabel(self.titleFrame, text = f"{self.team.name} Squad", font = (APP_FONT_BOLD, 35), fg_color = TKINTER_BACKGROUND).place(relx = 0.03, rely = 0.2, anchor = "w")
        
        canvas = ctk.CTkCanvas(self.titleFrame, width = 900, height = 5, bg = GREY_BACKGROUND, bd = 0, highlightthickness = 0)
        canvas.place(relx = 0.5, rely = 0.5, anchor = "center")

        self.infoFrame = ctk.CTkFrame(self.titleFrame, fg_color = TKINTER_BACKGROUND, width = 1000, height = 40, corner_radius = 0)
        self.infoFrame.place(relx = 0.5, rely = 0.75, anchor = "center")

        ctk.CTkLabel(self.infoFrame, text = "Number", font = (APP_FONT_BOLD, 20), fg_color = TKINTER_BACKGROUND).place(relx = 0.05, rely = 0.5, anchor = "center")
        ctk.CTkLabel(self.infoFrame, text = "Name", font = (APP_FONT_BOLD, 20), fg_color = TKINTER_BACKGROUND).place(relx = 0.15, rely = 0.5, anchor = "w")
        ctk.CTkLabel(self.infoFrame, text = "Age", font = (APP_FONT_BOLD, 20), fg_color = TKINTER_BACKGROUND).place(relx = 0.45, rely = 0.5, anchor = "center")
        ctk.CTkLabel(self.infoFrame, text = "Positions", font = (APP_FONT_BOLD, 20), fg_color = TKINTER_BACKGROUND).place(relx = 0.58, rely = 0.5, anchor = "center")
        ctk.CTkLabel(self.infoFrame, text = "Nat", font = (APP_FONT_BOLD, 20), fg_color = TKINTER_BACKGROUND).place(relx = 0.68, rely = 0.5, anchor = "center")
        ctk.CTkLabel(self.infoFrame, text = "Morale", font = (APP_FONT_BOLD, 20), fg_color = TKINTER_BACKGROUND).place(relx = 0.79, rely = 0.5, anchor = "center")
        ctk.CTkLabel(self.infoFrame, text = "Talk", font = (APP_FONT_BOLD, 20), fg_color = TKINTER_BACKGROUND).place(relx = 0.9, rely = 0.5, anchor = "center")

        self.playersFrame = ctk.CTkScrollableFrame(self, fg_color = TKINTER_BACKGROUND, width = 982, height = 580, corner_radius = 0)
        self.playersFrame.pack(expand = True, fill = "both", padx = (0, 20))

        self.addPlayers()

    def addPlayers(self, replace = False):

        if replace:
            for widget in self.winfo_children():
                widget.destroy()

        for player in self.players:
            if player.player_role != "Youth Team":
                PlayerFrame(self, self.manager_id, player, self.playersFrame, talkFunction = self.talkToPlayer)

    def talkToPlayer(self, player):

        self.talkFrame = ctk.CTkFrame(self, fg_color = TKINTER_BACKGROUND, width = 650, height = 500, corner_radius = 15, border_width = 3, border_color = GREY_BACKGROUND)
        self.talkFrame.place(relx = 0.5, rely = 0.5, anchor = "center")

        for frame in self.playersFrame.winfo_children():
            frame.disableTalkButton()

        self.addTalkingFrames(player)

    def addTalkingFrames(self, player):
        managerFrame = ctk.CTkFrame(self.talkFrame, fg_color = TKINTER_BACKGROUND, width = 145, height = 490, corner_radius = 0)
        managerFrame.place(x = 150, y = 5, anchor = "ne")

        src = Image.open("Images/default_user.png")
        src.thumbnail((75, 75))
        managerImage = ctk.CTkImage(src, None, (src.width, src.height))
        ctk.CTkLabel(managerFrame, image = managerImage, text = "").place(relx = 0.5, rely = 0.1, anchor = "n")

        manager = Managers.get_manager_by_id(self.manager_id)
        ctk.CTkLabel(managerFrame, text = f"{manager.first_name} {manager.last_name}", font = (APP_FONT_BOLD, 15), fg_color = TKINTER_BACKGROUND).place(relx = 0.5, rely = 0.27, anchor = "n")

        playerFrame = ctk.CTkFrame(self.talkFrame, fg_color = TKINTER_BACKGROUND, width = 145, height = 490, corner_radius = 0)
        playerFrame.place(x = 500, y = 5, anchor = "nw")

        self.backButton = ctk.CTkButton(playerFrame, text = "X", font = (APP_FONT, 15), fg_color = TKINTER_BACKGROUND, hover_color = CLOSE_RED, corner_radius = 10, width = 20, height = 20, command = lambda: self.backToSquad())
        self.backButton.place(relx = 0.96, rely = 0.01, anchor = "ne")

        src = Image.open("Images/default_user.png")
        src.thumbnail((75, 75))
        playerImage = ctk.CTkImage(src, None, (src.width, src.height))
        ctk.CTkLabel(playerFrame, image = playerImage, text = "").place(relx = 0.5, rely = 0.1, anchor = "n")
        ctk.CTkLabel(playerFrame, text = f"{player.first_name} {player.last_name}", font = (APP_FONT_BOLD, 15), fg_color = TKINTER_BACKGROUND).place(relx = 0.5, rely = 0.27, anchor = "n")

        canvas = ctk.CTkCanvas(playerFrame, width = 320, height = 5, bg = GREY_BACKGROUND, bd = 0, highlightthickness = 0)
        canvas.place(relx = 0.5, rely = 0.34, anchor = "center")

        self.talkingFrame = ctk.CTkFrame(self.talkFrame, fg_color = TKINTER_BACKGROUND, width = 350, height = 390, corner_radius = 0)
        self.talkingFrame.place(x = 150, y = 5, anchor = "nw")

        canvas = ctk.CTkCanvas(self.talkFrame, width = 5, height = 700, bg = GREY_BACKGROUND, bd = 0, highlightthickness = 0)
        canvas.place(x = 185, rely = 0.5, anchor = "center")

        canvas = ctk.CTkCanvas(self.talkFrame, width = 5, height = 700, bg = GREY_BACKGROUND, bd = 0, highlightthickness = 0)
        canvas.place(x = 625, rely = 0.5, anchor = "center")

        canvas = ctk.CTkCanvas(self.talkFrame, width = 440, height = 5, bg = GREY_BACKGROUND, bd = 0, highlightthickness = 0)
        canvas.place(relx = 0.5, rely = 0.8, anchor = "center")

        introductoryText = random.choice(INTRODUCTORY_TEXTS)
        introduction = ctk.CTkLabel(self.talkingFrame, text = introductoryText, fg_color = GREY_BACKGROUND, width = 100, height = 50, corner_radius = 10, anchor = "e")
        introduction.place(relx = 0.95, rely = 0.2, anchor = "e")

        lastMatchData = ctk.CTkFrame(playerFrame, fg_color = TKINTER_BACKGROUND, width = 130, height = 300, corner_radius = 0)
        lastMatchData.place(relx = 0.5, rely = 0.36, anchor = "n")

        team = Teams.get_team_by_id(player.team_id)
        league = LeagueTeams.get_league_by_team(team.id)

        lastMatch = Matches.get_team_last_match(team.id, league.league_id)

        if not lastMatch:
            ctk.CTkLabel(lastMatchData, text = "Did not play", font = (APP_FONT, 13), fg_color = TKINTER_BACKGROUND).place(relx = 0.1, rely = 0.15, anchor = "w")   
            return

        lastMatchEvents = MatchEvents.get_events_by_match_and_player(lastMatch.id, player.id)
        lineup = TeamLineup.get_lineup_by_match_and_team(lastMatch.id, team.id)
        lastMatchRating = [playerLineup.rating for playerLineup in lineup if playerLineup.player_id == player.id]

        ctk.CTkLabel(lastMatchData, text = "Last match stats:", font = (APP_FONT_BOLD, 15), fg_color = TKINTER_BACKGROUND).place(relx = 0.5, rely = 0.01, anchor = "n")
        
        if lastMatchRating == []:
            ctk.CTkLabel(lastMatchData, text = "Did not play", font = (APP_FONT, 13), fg_color = TKINTER_BACKGROUND).place(relx = 0.1, rely = 0.15, anchor = "w")
        else:
            self.addPrompts(player)
            events = {}
            for event in lastMatchEvents:

                if event.event_type == "sub_on" or event.event_type == "sub_off" or event.event_type == "penalty_miss":
                    continue
                elif event.event_type == "injury":
                    self.playerInjured = True
                elif event.event_type == "penalty_goal" or event.event_type == "goal":
                    eventType = "Goal(s)"
                elif event.event_type == "assist":
                    eventType = "Assist(s)"
                elif event.event_type == "penalty_saved":
                    eventType = "Penalty(ies) saved"
                elif event.event_type == "yellow_card":
                    eventType = "Yellow card(s)"
                elif event.event_type == "red_card":
                    eventType = "Red card(s)"
                elif event.event_type == "own_goal":
                    eventType = "Own goal(s)"
                elif event.event_type == "clean_sheet":
                    eventType = "Clean sheet(s)"

                if eventType in events:
                    events[eventType] += 1
                else:
                    events[eventType] = 1
                    
            self.rating = lastMatchRating[0]

            PROGRESS_COLOR = MORALE_GREEN

            if self.rating < 5.5:
                PROGRESS_COLOR = MORALE_RED
            elif self.rating < 7.5:
                PROGRESS_COLOR = MORALE_YELLOW

            ratingSlider = ctk.CTkSlider(lastMatchData, 
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

            ratingSlider.set(self.rating * 10)
            ratingSlider.configure(state = "disabled")
            ratingSlider.place(relx = 0.5, rely = 0.18, anchor = "center")
            ctk.CTkLabel(lastMatchData, text = f"Rating: {self.rating}", font = (APP_FONT, 13), fg_color = TKINTER_BACKGROUND).place(relx = 0.5, rely = 0.28, anchor = "center")

            for event in events:
                ctk.CTkLabel(lastMatchData, text = f"{event}: {events[event]}", font = (APP_FONT, 13), fg_color = TKINTER_BACKGROUND).place(relx = 0.1, rely = 0.3 + (list(events.keys()).index(event) + 1) * 0.1, anchor = "w")

    def addPrompts(self, player):
        
        self.promptsFrame = ctk.CTkFrame(self.talkFrame, fg_color = TKINTER_BACKGROUND, width = 350, height = 95, corner_radius = 0)
        self.promptsFrame.place(x = 150, y = 400, anchor = "nw")

        prompts = [
            "Congratulate", # Congratulate player on a good performance
            "Injury", # Encourage player when they get injured
            "Criticize", # Criticize player on a bad performance
            "Motivate" # Motivate player to perform better
        ]

        i = 0
        y = 0.05
        for prompt in prompts:
            ctk.CTkButton(self.promptsFrame, text = prompt, font = (APP_FONT, 15), fg_color = GREY_BACKGROUND, hover_color = GREY_BACKGROUND, corner_radius = 5, width = 100, height = 30, command = lambda prompt = prompt: self.carryOutPrompt(player, prompt)).place(relx = 0.01 + i * 0.3, rely = y, anchor = "nw")
            i += 1

            if i % 3 == 0:
                i = 0
                y = y + 0.35

    def carryOutPrompt(self, player, prompt):
        self.talkedTo.append(player.id)
        
        for button in self.promptsFrame.winfo_children():
            button.configure(state = "disabled")

        text = PROMPT_TO_TEXT[prompt]
        reply = ctk.CTkLabel(self.talkingFrame, text = text, fg_color = GREY_BACKGROUND, width = 100, height = 100, corner_radius = 10, anchor = "w")
        reply.place(relx = 0.05, rely = 0.45, anchor = "w")

        playerReply, accepted = get_player_response(prompt, self.rating, self.playerInjured)
        reply = ctk.CTkLabel(self.talkingFrame, text = playerReply, fg_color = GREY_BACKGROUND, width = 100, height = 50, corner_radius = 10, anchor = "e")
        reply.place(relx = 0.95, rely = 0.7, anchor = "e")

        if not accepted:
            moraleChange = get_morale_decrease_role(player)
        else:
            moraleChange = random.randint(3, 8)

        Players.update_morale(player.id, moraleChange)
        
        for frame in self.playersFrame.winfo_children():
            if frame.player.id == player.id:
                frame.updateMorale(moraleChange)

        self.parent.hub.resetMorale()

    def backToSquad(self):
        self.talkFrame.destroy()

        for frame in self.playersFrame.winfo_children():
            if frame.player.id not in self.talkedTo:
                frame.enableTalkButton()
