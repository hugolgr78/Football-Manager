import customtkinter as ctk
import math
from settings import *
from data.database import *
from CTkMessagebox import CTkMessagebox
from data.gamesDatabase import *
from utils.frames import FootballPitchLineup, SubstitutePlayer, LineupPlayerFrame, TeamLogo
from utils.playerProfileLink import PlayerProfileLink
from utils.matchProfileLink import MatchProfileLink
from utils.util_functions import *
from tabs.matchday import MatchDay
from PIL import Image
from collections import defaultdict
import io

class Tactics(ctk.CTkFrame):
    def __init__(self, parent, manager_id):
        super().__init__(parent, fg_color = TKINTER_BACKGROUND, width = 1000, height = 700, corner_radius = 0)

        self.manager_id = manager_id
        self.parent = parent
        self.selected_position = None

        self.team = Teams.get_teams_by_manager(self.manager_id)[0]

        self.lineupTab = Lineup(self, self.manager_id)
        self.analysis = None

        self.titles = ["Lineup", "Analysis"]
        self.tabs = [self.lineupTab, self.analysis]
        self.classNames = [Lineup, Analysis]

        self.activeButton = 0
        self.buttons = []

        self.tabsFrame = ctk.CTkFrame(self, fg_color = TKINTER_BACKGROUND, width = 1000, height = 50, corner_radius = 0)
        self.tabsFrame.pack(expand = True, fill = "both", padx = 10, pady = 10)

        self.createTabs()
        self.lineupTab.pack(expand = True, fill = "both")

    def createTabs(self):

        self.buttonHeight = 40
        self.buttonWidth = 200
        self.button_background = TKINTER_BACKGROUND
        self.hover_background = GREY_BACKGROUND
        self.gap = 0.102

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

    def canvas(self, width, height, relx):
        canvas = ctk.CTkCanvas(self.tabsFrame, width = width, height = height, bg = GREY_BACKGROUND, bd = 0, highlightthickness = 0)
        canvas.place(relx = relx, rely = 0, anchor = "nw")

    def changeTab(self, index):
        self.buttons[self.activeButton].configure(state = "normal")
        self.tabs[self.activeButton].pack_forget()
        
        self.activeButton = index
        self.buttons[self.activeButton].configure(state = "disabled")

        if not self.tabs[self.activeButton]:
            self.tabs[self.activeButton] = globals()[self.classNames[self.activeButton].__name__](self, self.manager_id)

        self.tabs[self.activeButton].pack(expand = True, fill = "both")

class Lineup(ctk.CTkFrame):
    def __init__(self, parent, manager_id):
        super().__init__(parent, fg_color = TKINTER_BACKGROUND, width = 1000, height = 630, corner_radius = 0) 

        self.manager_id = manager_id
        self.parent = parent
        self.mainMenu = self.parent.parent
        self.team = self.parent.team

        self.players = Players.get_all_players_by_team(self.team.id)

        self.selectedLineup = {}
        self.substitutePlayers = []
        self.subCounter = 0

        self.positionsCopy = POSITION_CODES.copy()

        self.addFrame = ctk.CTkFrame(self, fg_color = GREY_BACKGROUND, width = 340, height = 50, corner_radius = 10)
        self.addFrame.place(relx = 0.086, rely = 0.98, anchor = "sw")

        src = Image.open("Images/settings.png")
        src.thumbnail((30, 30))
        img = ctk.CTkImage(src, None, (src.width, src.height))
        self.settingsButton = ctk.CTkButton(self, text = "", image = img, width = 50, height = 50, fg_color = GREY_BACKGROUND, hover_color = DARK_GREY, corner_radius = 10, command = self.lineupSettings)
        self.settingsButton.place(relx = 0.023, rely = 0.98, anchor = "sw")

        self.settingsFrame = ctk.CTkFrame(self, fg_color = GREY_BACKGROUND, width = 400, height = 250, corner_radius = 10, border_color = APP_BLUE, border_width = 2, background_corner_colors = ["green", DARK_GREY, DARK_GREY, "green"])
        self.createSettingsFrame()

        ctk.CTkLabel(self.addFrame, text = "Add Position:", font = (APP_FONT, 18), text_color = "white", fg_color = GREY_BACKGROUND).place(relx = 0.04, rely = 0.5, anchor = "w")

        self.dropDown = ctk.CTkComboBox(self.addFrame, font = (APP_FONT, 15), fg_color = GREY_BACKGROUND, corner_radius = 10, dropdown_fg_color = GREY_BACKGROUND, dropdown_hover_color = DARK_GREY, width = 190, height = 30, state = "readonly", command = self.choosePlayer)
        self.dropDown.place(relx = 0.4, rely = 0.5, anchor = "w")
        self.dropDown.set("Choose Position")
        self.dropDown.configure(values = list(POSITION_CODES.keys()))

        self.resetButton = ctk.CTkButton(self, text = "Reset", font = (APP_FONT, 15), fg_color = GREY_BACKGROUND, corner_radius = 10, height = 50, width = 240, command = self.reset)
        self.resetButton.place(relx = 0.43, rely = 0.98, anchor = "sw")

        self.finishButton = ctk.CTkButton(self, text = "Matchday >>", font = (APP_FONT, 15), fg_color = APP_BLUE, corner_radius = 10, height = 50, width = 300, state = "disabled", command = self.finishLineup)
        self.finishButton.place(relx = 0.965, rely = 0.98, anchor = "se")

        self.substituteFrame = ctk.CTkScrollableFrame(self, fg_color = DARK_GREY, width = 520, height = 523, corner_radius = 10)
        self.substituteFrame.place(relx = 0.965, rely = 0.005, anchor = "ne")

        self.lineupPitch = FootballPitchLineup(self, 500, 675, 0, -0.02, "nw", TKINTER_BACKGROUND, "green")
        self.substituteFrame.lift()

        self.createChoosePlayerFrame()
        self.importLineup()

    def createChoosePlayerFrame(self):
        self.choosePlayerFrame = ctk.CTkFrame(self, fg_color = GREY_BACKGROUND, width = 400, height = 50, corner_radius = 0, border_color = APP_BLUE, border_width = 2)

        self.backButton = ctk.CTkButton(self.choosePlayerFrame, text = "Back", font = (APP_FONT, 15), fg_color = DARK_GREY, corner_radius = 10, height = 30, width = 100, hover_color = CLOSE_RED, command = self.stop_choosePlayer)
        self.backButton.place(relx = 0.95, rely = 0.5, anchor = "e")

        self.playerDropDown = ctk.CTkComboBox(self.choosePlayerFrame, font = (APP_FONT, 15), fg_color = GREY_BACKGROUND, corner_radius = 10, dropdown_fg_color = GREY_BACKGROUND, dropdown_hover_color = DARK_GREY, width = 220, height = 30, state = "readonly", command = self.choosePosition)
        self.playerDropDown.place(relx = 0.05, rely = 0.5, anchor = "w")
        self.playerDropDown.set("Choose Player")

    def createSettingsFrame(self):
        ctk.CTkButton(self.settingsFrame, text = "Back", font = (APP_FONT, 15), fg_color = DARK_GREY, corner_radius = 10, height = 30, width = 100, hover_color = CLOSE_RED, command = self.settingsFrame.place_forget).place(relx = 0.95, rely = 0.05, anchor = "ne")

        ctk.CTkLabel(self.settingsFrame, text = "Save lineup", font = (APP_FONT, 15), text_color = "white", fg_color = GREY_BACKGROUND).place(relx = 0.05, rely = 0.15, anchor = "w")
        self.saveBox = ctk.CTkEntry(self.settingsFrame, width = 250, height = 30, font = (APP_FONT, 10), fg_color = GREY_BACKGROUND, corner_radius = 10, border_color = GREY, border_width = 2)
        self.saveBox.place(relx = 0.05, rely = 0.28, anchor = "w")
        ctk.CTkButton(self.settingsFrame, text = "OK", fg_color = DARK_GREY, corner_radius = 10, height = 30, width = 30, command = self.saveLineup).place(relx = 0.95, rely = 0.28, anchor = "e")

        ctk.CTkLabel(self.settingsFrame, text = "Load lineup", font = (APP_FONT, 15), text_color = "white", fg_color = GREY_BACKGROUND).place(relx = 0.05, rely = 0.45, anchor = "w")
        self.loadBox = ctk.CTkComboBox(self.settingsFrame, width = 250, height = 30, font = (APP_FONT, 15), fg_color = GREY_BACKGROUND, corner_radius = 10, dropdown_fg_color = GREY_BACKGROUND, dropdown_hover_color = DARK_GREY)
        self.loadBox.place(relx = 0.05, rely = 0.58, anchor = "w")
        ctk.CTkButton(self.settingsFrame, text = "OK", fg_color = DARK_GREY, corner_radius = 10, height = 30, width = 30, command = self.loadLineup).place(relx = 0.95, rely = 0.58, anchor = "e")

        ctk.CTkLabel(self.settingsFrame, text = "Automatic lineup", font = (APP_FONT, 15), text_color = "white", fg_color = GREY_BACKGROUND).place(relx = 0.05, rely = 0.75, anchor = "w")
        self.autoBox = ctk.CTkComboBox(self.settingsFrame, width = 250, height = 30, font = (APP_FONT, 15), fg_color = GREY_BACKGROUND, corner_radius = 10, dropdown_fg_color = GREY_BACKGROUND, dropdown_hover_color = DARK_GREY)
        self.autoBox.place(relx = 0.05, rely = 0.88, anchor = "w")
        ctk.CTkButton(self.settingsFrame, text = "OK", fg_color = DARK_GREY, corner_radius = 10, height = 30, width = 30, command = self.autoLineup).place(relx = 0.95, rely = 0.88, anchor = "e")

        self.autoBox.configure(values = FORMATIONS_POSITIONS.keys())

    def importLineup(self, loaded = None, auto = None):
        self.leagueTeams = LeagueTeams.get_league_by_team(self.team.id)
        self.league = League.get_league_by_id(self.leagueTeams.league_id)
        self.players = [player.id for player in Players.get_all_players_by_team(self.team.id, youths = False)]
        self.checkPositionsForYouth()

        if not loaded and not auto:

            lastMatchday = self.league.current_matchday - 1

            if lastMatchday == 0:
                self.addSubstitutePlayers()
                return
            
            self.matchdayMatches = Matches.get_matchday_for_league(self.league.id, lastMatchday)

            for match in self.matchdayMatches:
                if match.home_id == self.team.id or match.away_id == self.team.id:
                    self.lastTeamMatch = match
                    self.lineup = TeamLineup.get_lineup_by_match_and_team(match.id, self.team.id)
        else:
            self.lineup = loaded if loaded else auto

        playersCount = 0
        for playerData in self.lineup.values() if auto else self.lineup:
            if not loaded and not auto:
                position = playerData.start_position
                player = Players.get_player_by_id(playerData.player_id)
            elif loaded:
                position = playerData.position
                player = Players.get_player_by_id(playerData.player_id)
            else:
                position = [pos for pos, pid in self.lineup.items() if pid == playerData][0]
                player = Players.get_player_by_id(playerData.id)

            if not position:
                continue

            positionCode = POSITION_CODES[position]

            # Remove any youths that arent in the players list as the position is now free
            if player.player_role == "Youth Team" and player.id not in self.players:
                continue

            # If the player finished the match out of position, skip them
            if positionCode not in player.specific_positions.split(","):
                continue
        
            # Remove any players that are banned
            if PlayerBans.check_bans_for_player(player.id, self.league.id):
                continue

            playersCount += 1

            self.selectedLineup[position] = player.id
            LineupPlayerFrame(self.lineupPitch, 
                            POSITIONS_PITCH_POSITIONS[position][0], 
                            POSITIONS_PITCH_POSITIONS[position][1], 
                            "center", 
                            GREY_BACKGROUND,
                            65, 
                            65, 
                            player.id,
                            positionCode,
                            position,
                            self.removePlayer,
                            self.updateLineup,
                            self.substituteFrame,
                            self.swapLineupPositions
                        )
            
        self.lineupPitch.set_counter(playersCount)

        if playersCount == 11:
            self.dropDown.configure(state = "disabled")

        self.addSubstitutePlayers(importing = True, playersCount = playersCount)

        for position in POSITION_CODES.keys():
            if position in self.selectedLineup:
                del self.positionsCopy[position]
            
        self.dropDown.configure(values = self.positionsCopy)

    def checkPositionsForYouth(self):

        for position in POSITION_CODES.keys():
            playersForPosition = []
            for playerID in self.players:
                player = Players.get_player_by_id(playerID)
                if POSITION_CODES[position] not in player.specific_positions.split(","):
                    continue

                if not PlayerBans.check_bans_for_player(player.id, self.league.id):
                    playersForPosition.append(playerID)

            if position in DEFENSIVE_POSITIONS:
                overallPosition = "defender"
            elif position in MIDFIELD_POSITIONS:
                overallPosition = "midfielder"
            elif position in ATTACKING_POSITIONS:
                overallPosition = "forward"
            else:
                overallPosition = "goalkeeper"

            if POSITION_CODES[position] in POSITIONS_MAX.keys():
                maxPlayers = POSITIONS_MAX[POSITION_CODES[position]]
            else:
                maxPlayers = 1

            if len(playersForPosition) < maxPlayers:
                youths = PlayerBans.get_all_non_banned_youth_players_for_comp(self.team.id, self.league.id)
                youthForPosition = [youth for youth in youths if POSITION_CODES[position] in youth.specific_positions.split(",") and youth.id not in self.players]

                if len(youthForPosition) > 0:
                    self.players.append(youthForPosition[0].id)
                else:
                    newYouth = Players.add_player(self.team.id, overallPosition, position, "Youth Team")
                    self.players.append(newYouth.id)

                if position == "Goalkeeper":
                    newYouth = Players.add_player(self.team.id, overallPosition, position, "Youth Team")
                    self.players.append(newYouth.id)

            elif position == "Goalkeeper" and len(playersForPosition) == 1:
                youths = PlayerBans.get_all_non_banned_youth_players_for_comp(self.team.id, self.league.id)
                youthForPosition = [youth for youth in youths if POSITION_CODES[position] in youth.specific_positions.split(",") and youth.id not in self.players]

                if len(youthForPosition) > 0:
                    self.players.append(youthForPosition[0].id)
                else:
                    newYouth = Players.add_player(self.team.id, overallPosition, position, "Youth Team")
                    self.players.append(newYouth.id)

    def addSubstitutePlayers(self, importing = False, playersCount = None):
        ctk.CTkLabel(self.substituteFrame, text = "Substitutes", font = (APP_FONT_BOLD, 20), fg_color = DARK_GREY).pack(pady = 5)
        
        players_per_row = 5

        # Define position groups and their display names
        position_groups = [
            ("goalkeeper", "Goalkeepers"),
            ("defender", "Defenders"),
            ("midfielder", "Midfielders"),
            ("forward", "Forwards"),
        ]

        playersIDs = self.players.copy()
        playersList = [Players.get_player_by_id(player) for player in playersIDs]
        playersList.sort(key = lambda x: (POSITION_ORDER.get(x.position, 99), x.last_name))

        for pos_key, heading in position_groups:
            group_players = [p for p in playersList if p.position == pos_key and p.id not in self.selectedLineup.values()]
            num_players = len(group_players)

            if num_players == 0:
                continue

            frame = ctk.CTkFrame(self.substituteFrame, fg_color = DARK_GREY, width = 500, height = 100 * max(1, math.ceil(num_players / players_per_row)))
            frame.grid_columnconfigure(players_per_row, weight = 1)
            frame.grid_rowconfigure(1 + math.ceil(num_players / 4), weight = 1)
            ctk.CTkLabel(frame, text = heading, font = (APP_FONT_BOLD, 20), fg_color = DARK_GREY).grid(row = 0, column = 0, padx = 5, pady = 5, sticky = "w", columnspan = 4)

            count = 0
            for player in group_players:

                if importing and player.id in self.selectedLineup.values():
                    count -= 1
                    continue

                row = 1 + count // players_per_row
                col = count % players_per_row
                sub_frame = SubstitutePlayer(frame, GREY_BACKGROUND, 85, 85, player, self.parent, self.league.id, row, col, self.checkSubstitute)

                if importing and playersCount == 11:
                    sub_frame.showCheckBox()

                count += 1

            frame.pack(fill = "x", padx = 10, pady = 5)

        if playersCount == 11:
            self.dropDown.configure(state = "disabled")
        else:
            self.dropDown.configure(state = "readonly")
            self.finishButton.configure(state = "disabled")

            for frame in self.substituteFrame.winfo_children():
                for child in frame.winfo_children():
                    if isinstance(child, SubstitutePlayer):
                        child.hideCheckBox()
                        child.uncheckCheckBox()

    def choosePlayer(self, selected_position):
        self.selected_position = selected_position
        self.dropDown.configure(state = "disabled")
        self.resetButton.configure(state = "disabled")

        self.choosePlayerFrame.place(relx = 0.221, rely = 0.435, anchor = "center")

        values = []
        for playerID in self.players:
            player = Players.get_player_by_id(playerID)
            playerName = player.first_name + " " + player.last_name
            if POSITION_CODES[selected_position] in player.specific_positions.split(",") and player.id not in self.selectedLineup.values() and not PlayerBans.check_bans_for_player(player.id, self.league.id):
                values.append(playerName)
        
        if len(values) == 0:
            self.playerDropDown.set("No available players")
            self.playerDropDown.configure(state = "disabled")
        else:
            self.playerDropDown.set("Choose Player")
            self.playerDropDown.configure(values = values)
            self.playerDropDown.configure(state = "normal")

    def stop_choosePlayer(self):
        self.choosePlayerFrame.place_forget()
        self.dropDown.configure(state = "normal")
        self.resetButton.configure(state = "normal")
        self.playerDropDown.set("Choose Player")

    def choosePosition(self, selected_player):

        self.stop_choosePlayer()

        if self.selected_position in self.positionsCopy:
            del self.positionsCopy[self.selected_position]

            if self.selected_position in RELATED_POSITIONS:
                for related_position in RELATED_POSITIONS[self.selected_position]:
                    if related_position in self.positionsCopy:
                        del self.positionsCopy[related_position]

        self.dropDown.configure(values = list(self.positionsCopy.keys()))

        self.lineupPitch.increment_counter()

        player = Players.get_player_by_name(selected_player.split(" ")[0], selected_player.split(" ")[1], self.team.id)
        self.selectedLineup[self.selected_position] = player.id

        LineupPlayerFrame(self.lineupPitch, 
                            POSITIONS_PITCH_POSITIONS[self.selected_position][0], 
                            POSITIONS_PITCH_POSITIONS[self.selected_position][1], 
                            "center", 
                            GREY_BACKGROUND,
                            65, 
                            65, 
                            player.id,
                            POSITION_CODES[self.selected_position],
                            self.selected_position,
                            self.removePlayer,
                            self.updateLineup,
                            self.substituteFrame,
                            self.swapLineupPositions
                        )

        for widget in self.substituteFrame.winfo_children():
            widget.destroy()

        self.addSubstitutePlayers(importing = True, playersCount = self.lineupPitch.get_counter())

    def removePlayer(self, frame, playerName, playerPosition):
        playerData = Players.get_player_by_name(playerName.split(" ")[0], playerName.split(" ")[1], self.team.id)
        for position, playerID in self.selectedLineup.items():
            if playerID == playerData.id:
                del self.selectedLineup[position]
                break

        self.lineupPitch.decrement_counter()
        frame.place_forget()

        for position, position_code in POSITION_CODES.items():
            if position == playerPosition:
                self.positionsCopy[position] = position_code

                if position in RELATED_POSITIONS:
                    for related_position in RELATED_POSITIONS[position]:
                        self.positionsCopy[related_position] = position_code

                break

        for widget in self.substituteFrame.winfo_children():
            widget.destroy()

        self.addSubstitutePlayers(importing = True, playersCount = self.lineupPitch.get_counter())

        # Reset the substitutes chosen
        self.dropDown.configure(values = list(self.positionsCopy.keys()))
        self.substitutePlayers = []
        self.subCounter = 0

    def updateLineup(self, player, old_position, new_position):
        if old_position in self.selectedLineup:
            del self.selectedLineup[old_position]

        self.selectedLineup[new_position] = player.id

        ## Add the old position back into to dropdown, accouting for related positions and remove the new position
        if old_position not in self.positionsCopy:
            # Don't add old_position if new_position is a related position of old_position, or vice versa
            related_to_old = RELATED_POSITIONS.get(old_position, [])
            related_to_new = RELATED_POSITIONS.get(new_position, [])
            if new_position not in related_to_old and old_position not in related_to_new:
                self.positionsCopy[old_position] = POSITION_CODES[old_position]

        if old_position in RELATED_POSITIONS:
            for related_position in RELATED_POSITIONS[old_position]:
                # Only add the related position if none of its other related positions are in the lineup
                other_related = [r for r in RELATED_POSITIONS.get(related_position, []) if r != old_position]
                if all(r not in self.selectedLineup for r in other_related):
                    if related_position not in self.selectedLineup:
                        self.positionsCopy[related_position] = POSITION_CODES[old_position]

        if new_position in self.positionsCopy:
            del self.positionsCopy[new_position]

        if new_position in RELATED_POSITIONS:
            for related_position in RELATED_POSITIONS[new_position]:
                if related_position in self.positionsCopy:
                    del self.positionsCopy[related_position]

        self.dropDown.configure(values = list(self.positionsCopy.keys()))

    def swapLineupPositions(self, position_1, position_2):
        temp = self.selectedLineup[position_1]
        self.selectedLineup[position_1] = self.selectedLineup[position_2]
        self.selectedLineup[position_2] = temp

    def reset(self, addSubs = True):
        self.lineupPitch.destroy()
        self.lineupPitch = FootballPitchLineup(self, 500, 675, 0, -0.02, "nw", TKINTER_BACKGROUND, "green")

        self.lineupPitch.reset_counter()
        self.dropDown.configure(state = "normal")
        self.dropDown.set("Choose Position")
        self.positionsCopy = POSITION_CODES.copy()
        self.dropDown.configure(values = list(self.positionsCopy.keys()))
        self.selectedLineup = {}
        self.finishButton.configure(state = "disabled")

        for frame in self.substituteFrame.winfo_children():
            frame.destroy()
        
        if addSubs:
            self.addSubstitutePlayers()

        self.choosePlayerFrame.destroy()
        self.createChoosePlayerFrame()

    def checkSubstitute(self, checkBox, player):
        if checkBox.get() == 0:
            del self.substitutePlayers[self.substitutePlayers.index(player.id)]
            self.subCounter -= 1

            if self.subCounter < MATCHDAY_SUBS:
                self.finishButton.configure(state = "disabled")

                for frame in self.substituteFrame.winfo_children():
                    for widget in frame.winfo_children():
                        if isinstance(widget, SubstitutePlayer):
                            widget.enableCheckBox()
        else:
            self.substitutePlayers.append(player.id)
            self.subCounter += 1

            if self.subCounter == MATCHDAY_SUBS:
                self.finishButton.configure(state = "normal")

                for frame in self.substituteFrame.winfo_children():
                    for widget in frame.winfo_children():
                        if isinstance(widget, SubstitutePlayer):
                            if widget.checkBox.get() == 0:
                                widget.disableCheckBox()

    def finishLineup(self):
        players = [Players.get_player_by_id(playerID) for playerID in self.players]
        MatchDay(self.mainMenu, self.selectedLineup, self.substitutePlayers, self.team, players)

    def lineupSettings(self):
        self.settingsFrame.place(relx = 0.5, rely = 0.4, anchor = "center")
        self.settingsFrame.lift()

        lineupNames = SavedLineups.get_all_lineup_names()
        self.loadBox.set("Choose Lineup")
        self.loadBox.configure(values = lineupNames)

        self.autoBox.set("Choose Lineup")

    def saveLineup(self):
        lineupName = self.saveBox.get()
        if lineupName:

            if self.lineupPitch.get_counter() != 11:
                CTkMessagebox(title = "Error", message = "You need 11 players in your lineup to save it.", icon = "cancel")
                return
            
            lineupNames = SavedLineups.get_all_lineup_names()
            if lineupName in lineupNames:
                CTkMessagebox(title = "Error", message = "This lineup name already exists.", icon = "cancel")
                return
            
            SavedLineups.add_lineup(lineupName, self.selectedLineup)

            self.settingsFrame.place_forget()
            pass

    def loadLineup(self):
        lineupName = self.loadBox.get()
        if lineupName and lineupName != "Choose Lineup":
            self.settingsFrame.place_forget()
            self.reset(addSubs = False)

            chosenLineup = SavedLineups.get_lineup_by_name(lineupName)
            self.importLineup(loaded = chosenLineup)

    def autoLineup(self):
        lineupName = self.autoBox.get()
        if lineupName and lineupName != "Choose Lineup":
            self.settingsFrame.place_forget()
            self.reset(addSubs = False)

            lineup = {}
            defNums, midNums, _ = map(int, lineupName.split("-"))

            goalkeepers = [Players.get_player_by_id(playerID) for playerID in self.players if Players.get_player_by_id(playerID).position == "goalkeeper"]
            defenders = [Players.get_player_by_id(playerID) for playerID in self.players if Players.get_player_by_id(playerID).position == "defender"]
            midfielders = [Players.get_player_by_id(playerID) for playerID in self.players if Players.get_player_by_id(playerID).position == "midfielder"]
            attackers = [Players.get_player_by_id(playerID) for playerID in self.players if Players.get_player_by_id(playerID).position == "forward"]

            lineup["Goalkeeper"] = goalkeepers[0]

            # defenders
            self.choosePlayers(FORMATIONS_POSITIONS[lineupName][1:defNums + 1], defenders, lineup)

            # midfielders
            self.choosePlayers(FORMATIONS_POSITIONS[lineupName][defNums + 1:defNums + midNums + 1], midfielders, lineup)

            # attackers
            self.choosePlayers(FORMATIONS_POSITIONS[lineupName][defNums + midNums + 1:], attackers, lineup)

            self.importLineup(auto = lineup)

    def choosePlayers(self, position_names, players, lineup):

        position_options = defaultdict(list)

        for position in position_names:
            position_options[position] = []
            for player in players:
                if POSITION_CODES[position] in player.specific_positions:
                    position_options[position].append(player)

        assigned_players = set()

        while position_options != {}:
            sorted_positions = sorted(position_options.keys(), key = lambda pos: len(position_options[pos]))

            position = sorted_positions[0]
            available_players = [p for p in position_options[position] if p not in assigned_players]
            
            # Step 3: Prioritize by role (star > first_team > rotation)
            best_fit = next((p for p in available_players if p.player_role == "Star player"), None) or \
                    next((p for p in available_players if p.player_role == "First Team"), None) or \
                    next((p for p in available_players if p.player_role == "Rotation"), None)

            if not best_fit:
                best_fit = available_players[0]

            lineup[position] = best_fit
            assigned_players.add(best_fit)

            # Remove empty position entries
            del position_options[position]

class Analysis(ctk.CTkFrame):
    def __init__(self, parent, manager_id):
        super().__init__(parent, fg_color = TKINTER_BACKGROUND, width = 1000, height = 630, corner_radius = 0) 

        self.parent = parent
        self.manager_id = manager_id
        self.team = self.parent.team

        league = LeagueTeams.get_league_by_team(self.team.id)
        self.nextmatch = Matches.get_team_next_match(self.team.id, league.league_id)
        self.opponent = Teams.get_team_by_id(self.nextmatch.away_id if self.nextmatch.home_id == self.team.id else self.nextmatch.home_id)

        self.oppLastMatch = Matches.get_team_last_match(self.opponent.id, league.league_id)
        self.oppLast5Matches = Matches.get_team_last_5_matches(self.opponent.id, league.league_id)

        if not self.oppLastMatch:
            ctk.CTkLabel(self, text = "No analysis available for this team.", font = (APP_FONT, 20), fg_color = TKINTER_BACKGROUND).place(relx = 0.5, rely = 0.5, anchor = "center")
            return

        canvas = ctk.CTkCanvas(self, width = 5, height = 770, bg = GREY_BACKGROUND, bd = 0, highlightthickness = 0)
        canvas.place(relx = 0.5, rely = 0, anchor = "n")

        ctk.CTkLabel(self, text = f"{self.opponent.name} Analysis", font = (APP_FONT_BOLD, 30), fg_color = TKINTER_BACKGROUND).place(relx = 0.25, rely = 0.03, anchor = "center")

        self.best5PlayersFrame = ctk.CTkFrame(self, fg_color = GREY_BACKGROUND, width = 480, height = 150, corner_radius = 10)
        self.best5PlayersFrame.place(relx = 0.25, rely = 0.1, anchor = "n")
        self.best5PlayersFrame.pack_propagate(False)

        self.last5FormFrame = ctk.CTkFrame(self, fg_color = GREY_BACKGROUND, width = 480, height = 150, corner_radius = 10)
        self.last5FormFrame.place(relx = 0.25, rely = 0.4, anchor = "n")
        self.last5FormFrame.pack_propagate(False)

        self.topStatPlayersFrame = ctk.CTkFrame(self, fg_color = GREY_BACKGROUND, width = 480, height = 150, corner_radius = 10)
        self.topStatPlayersFrame.place(relx = 0.25, rely = 0.7, anchor = "n")
        self.topStatPlayersFrame.pack_propagate(False)

        self.predictedLineupFrame = ctk.CTkFrame(self, fg_color = GREY_BACKGROUND, width = 460, height = 390, corner_radius = 10)
        self.predictedLineupFrame.place(relx = 0.74, rely = 0.02, anchor = "n")

        self.lastMeetingsFrame = ctk.CTkFrame(self, fg_color = GREY_BACKGROUND, width = 460, height = 150, corner_radius = 10)
        self.lastMeetingsFrame.place(relx = 0.74, rely = 0.7, anchor = "n")

        self.best5Players()
        self.last5Form()
        self.topStatPlayers()
        self.predictedLineup()
        self.lastMeetings()

    def best5Players(self):
        ctk.CTkLabel(self.best5PlayersFrame, text = "Best players over the last 5 games", font = (APP_FONT, 15), fg_color = GREY_BACKGROUND).pack(expand = True, fill = "x", pady = 5, anchor = "nw")

        last5lineups = [TeamLineup.get_lineup_by_match_and_team(match.id, self.opponent.id) for match in self.oppLast5Matches if match]
        best5Players = self.getBest5Players(last5lineups)

        frame = ctk.CTkFrame(self.best5PlayersFrame, fg_color = GREY_BACKGROUND, width = 460, height = 15)
        frame.pack(expand = True, fill = "x", padx = 2, pady = (0, 5))

        ctk.CTkLabel(frame, text = "Player", font = (APP_FONT_BOLD, 12), text_color = "white", fg_color = GREY_BACKGROUND).place(relx = 0.02, rely = 0.5, anchor = "w")
        ctk.CTkLabel(frame, text = "Position", font = (APP_FONT_BOLD, 12), text_color = "white", fg_color = GREY_BACKGROUND).place(relx = 0.35, rely = 0.5, anchor = "center")
        ctk.CTkLabel(frame, text = "Avg. Rating", font = (APP_FONT_BOLD, 12), text_color = "white", fg_color = GREY_BACKGROUND).place(relx = 0.6, rely = 0.5, anchor = "center")
        ctk.CTkLabel(frame, text = "Goals / Assists", font = (APP_FONT_BOLD, 12), text_color = "white", fg_color = GREY_BACKGROUND).place(relx = 0.85, rely = 0.5, anchor = "center")

        for i in range(len(best5Players)):
            player = best5Players[i]['player']
            rating = best5Players[i]['average_rating']
            frame = ctk.CTkFrame(self.best5PlayersFrame, fg_color = GREY_BACKGROUND, width = 460, height = 15)
            frame.pack(expand = True, fill = "x", padx = 2, pady = (0, 5))

            PlayerProfileLink(frame, player, f"{player.first_name} {player.last_name}", "white", 0.02, 0.5, "w", GREY_BACKGROUND, self.parent, 12)
            ctk.CTkLabel(frame, text = player.position.capitalize(), font = (APP_FONT, 12), text_color = "white", fg_color = GREY_BACKGROUND).place(relx = 0.35, rely = 0.5, anchor = "center")
            ctk.CTkLabel(frame, text = str(rating), font = (APP_FONT, 12), text_color = "white", fg_color = GREY_BACKGROUND).place(relx = 0.6, rely = 0.5, anchor = "center")

            goals, assists = 0, 0
            for match in self.oppLast5Matches:
                playerEvents = MatchEvents.get_events_by_match_and_player(match.id, player.id)
                for event in playerEvents:
                    if event.event_type == "goal" or event.event_type == "penalty_goal":
                        goals += 1
                    elif event.event_type == "assist":
                        assists += 1

            ctk.CTkLabel(frame, text = f"{goals} / {assists}", font = (APP_FONT, 12), text_color = "white", fg_color = GREY_BACKGROUND).place(relx = 0.85, rely = 0.5, anchor = "center")

    def getBest5Players(self, lineups):
        players = {}
        for lineup in lineups:
            for player in lineup:
                playerData = Players.get_player_by_id(player.player_id)
                key = f"{playerData.first_name} {playerData.last_name}"
                if key in players:
                    players[key]['total_rating'] += player.rating
                    players[key]['matches'] += 1
                else:
                    players[key] = {'player': playerData, 'total_rating': player.rating, 'matches': 1}

        # Filter for players with at least 3 matches and calculate average rating
        qualified_players = {}
        for key, data in players.items():
            if data['matches'] >= 3:
                data['average_rating'] = round(data['total_rating'] / data['matches'], 2)
                qualified_players[key] = data

        # Sort qualified players by average rating
        sorted_players = sorted(qualified_players.values(), key = lambda x: x['average_rating'], reverse = True)
        return sorted_players[:4]

    def last5Form(self):
        ctk.CTkLabel(self.last5FormFrame, text = "Last games", font = (APP_FONT, 15), fg_color = GREY_BACKGROUND).pack(expand = True, fill = "x", pady = 5, anchor = "nw")

        for i, match in enumerate(self.oppLast5Matches):
            frame = ctk.CTkFrame(self.last5FormFrame, fg_color = DARK_GREY, width = 90, height = 110)
            frame.place(relx = 0.005 + i * 0.2, rely = 0.25, anchor = "nw")

            opponentID = match.away_id if match.home_id == self.opponent.id else match.home_id
            opponent = Teams.get_team_by_id(opponentID)
            src = Image.open(io.BytesIO(opponent.logo))
            src.thumbnail((50, 50))
            TeamLogo(frame, src, opponent, DARK_GREY, 0.5, 0.25, "center", self.parent)

            MatchProfileLink(frame, match, f"{match.score_home} - {match.score_away}", "white", 0.5, 0.6, "center", DARK_GREY, self.parent, 15, APP_FONT_BOLD)
            ctk.CTkLabel(frame, text = "H" if match.home_id == self.opponent.id else "A", font = (APP_FONT, 12), text_color = "white", fg_color = DARK_GREY, height = 0).place(relx = 0.5, rely = 0.75, anchor = "center")

            result = "draw"
            if match.home_id == self.opponent.id:
                if match.score_home > match.score_away:
                    result = "win"
                elif match.score_home < match.score_away:
                    result = "loss"
            else:
                if match.score_away > match.score_home:
                    result = "win"
                elif match.score_away < match.score_home:
                    result = "loss"

            if result == "win":
                colour = PIE_GREEN
            elif result == "loss":
                colour = PIE_RED
            else:
                colour = NEUTRAL_COLOR

            ctk.CTkCanvas(frame, bg = colour, height = 10, width = 120, bd = 0, highlightthickness = 0).place(relx = 0.5, rely = 0.98, anchor = "s")

    def topStatPlayers(self):
        pass

    def predictedLineup(self):
        pass

    def lastMeetings(self):
        pass
