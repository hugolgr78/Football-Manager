import customtkinter as ctk
import math
from settings import *
from data.database import *
from CTkMessagebox import CTkMessagebox
from data.gamesDatabase import *
from utils.frames import FootballPitchLineup, SubstitutePlayer, LineupPlayerFrame, TeamLogo, FootballPitchMatchDay, DataPolygon
from utils.playerProfileLink import PlayerProfileLink
from utils.matchProfileLink import MatchProfileLink
from utils.util_functions import *
from tabs.matchday import MatchDay
from PIL import Image
import io

class Tactics(ctk.CTkFrame):
    def __init__(self, parent):
        """
        Initialize the Tactics tab for managing team lineups and match analysis.
        
        Args:
            parent (ctk.CTkFrame): The parent tkinter widget (main menu).
        """
        
        super().__init__(parent, fg_color = TKINTER_BACKGROUND, width = 1000, height = 700, corner_radius = 0)

        self.manager_id = Managers.get_all_user_managers()[0].id
        self.parent = parent
        self.selected_position = None

        self.team = Teams.get_teams_by_manager(self.manager_id)[0]
        self.leagueID = LeagueTeams.get_league_by_team(self.team.id).league_id
        self.league = League.get_league_by_id(self.leagueID)
        self.matchday = League.get_league_by_id(self.leagueID).current_matchday

        gameTime = Matches.check_if_game_time(self.team.id, Game.get_game_date(self.manager_id))
        if gameTime:
            self.nextmatch = Matches.get_match_by_team_and_date(self.team.id, Game.get_game_date(self.manager_id))
        else:
            self.nextmatch = Matches.get_team_next_match(self.team.id, Game.get_game_date(self.manager_id))
            
        self.opponent = Teams.get_team_by_id(self.nextmatch.away_id if self.nextmatch.home_id == self.team.id else self.nextmatch.home_id)

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
        """
        Create the tab buttons for switching between Lineup and Analysis.
        """

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
        """
        Create a canvas for visual separation between tab buttons.
        
        Args:
            width (int): Width of the canvas.
            height (int): Height of the canvas.
            relx (float): Relative x position for placing the canvas.
        """
        
        canvas = ctk.CTkCanvas(self.tabsFrame, width = width, height = height, bg = GREY_BACKGROUND, bd = 0, highlightthickness = 0)
        canvas.place(relx = relx, rely = 0, anchor = "nw")

    def changeTab(self, index):
        """
        Change the active tab to the specified index.
        
        Args:
            index (int): The index of the tab to switch to.
        """
        
        self.buttons[self.activeButton].configure(state = "normal")
        self.tabs[self.activeButton].pack_forget()
        
        self.activeButton = index
        self.buttons[self.activeButton].configure(state = "disabled")

        if not self.tabs[self.activeButton]:
            self.tabs[self.activeButton] = globals()[self.classNames[self.activeButton].__name__](self, self.manager_id)

        self.tabs[self.activeButton].pack(expand = True, fill = "both")

    def turnSubsOn(self):
        """
        Activate substitutes in the lineup tab if it exists.
        """
        
        if getattr(self, 'lineupTab', None):
            try:
                self.lineupTab.turnSubsOn()
            except Exception:
                pass
            
    def activateProposed(self, lineup):
        """
        Activate the proposed lineup in the lineup tab.
        
        Args:
            lineup (dict): The proposed lineup to be set.
        """
        
        self.lineupTab.proposedLineup(lineup = lineup)
    
    def saveLineup(self):
        """
        Save the current lineup in the lineup tab.
        """
        
        self.lineupTab.saveLineup(current = True)

class Lineup(ctk.CTkFrame):
    def __init__(self, parent, manager_id):
        """
        Initialize the Lineup tab for managing team lineups.
        
        Args:
            parent (ctk.CTkFrame): The parent tkinter widget (Tactics tab).
            manager_id (int): The ID of the manager.
        """
        
        super().__init__(parent, fg_color = TKINTER_BACKGROUND, width = 1000, height = 630, corner_radius = 0) 

        self.parent = parent
        self.manager_id = manager_id
        self.mainMenu = self.parent.parent
        self.team = self.parent.team
        self.leagueID = self.parent.leagueID
        self.matchday = self.parent.matchday
        self.nextmatch = self.parent.nextmatch
        self.opponent = self.parent.opponent

        self.selectedLineup = {}
        self.substitutePlayers = []
        self.subCounter = 0

        self.gameTime = Matches.check_if_game_time(self.team.id, Game.get_game_date(self.manager_id))

        self.positionsCopy = POSITION_CODES.copy()

        self.addFrame = ctk.CTkFrame(self, fg_color = GREY_BACKGROUND, width = 340, height = 50, corner_radius = 10)
        self.addFrame.place(relx = 0.086, rely = 0.98, anchor = "sw")

        src = Image.open("Images/settings.png")
        src.thumbnail((30, 30))
        img = ctk.CTkImage(src, None, (src.width, src.height))
        self.settingsButton = ctk.CTkButton(self, text = "", image = img, width = 50, height = 50, fg_color = GREY_BACKGROUND, hover_color = DARK_GREY, corner_radius = 10, command = self.lineupSettings)
        self.settingsButton.place(relx = 0.023, rely = 0.98, anchor = "sw")

        self.settingsFrame = ctk.CTkFrame(self, fg_color = GREY_BACKGROUND, width = 400, height = 300, corner_radius = 10, border_color = APP_BLUE, border_width = 2, background_corner_colors = ["green", DARK_GREY, DARK_GREY, "green"])
        self.createSettingsFrame()

        ctk.CTkLabel(self.addFrame, text = "Add Position:", font = (APP_FONT, 18), text_color = "white", fg_color = GREY_BACKGROUND).place(relx = 0.04, rely = 0.5, anchor = "w")

        self.dropDown = ctk.CTkComboBox(self.addFrame, font = (APP_FONT, 15), fg_color = DARK_GREY, border_color = DARK_GREY, button_color = DARK_GREY, button_hover_color = DARK_GREY, dropdown_fg_color = DARK_GREY, dropdown_hover_color = DARK_GREY, corner_radius = 10, width = 190, height = 30, state = "readonly", command = self.choosePlayer)
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

        if SavedLineups.has_current_lineup():
            current_lineup = SavedLineups.get_current_lineup()
            self.importLineup(auto = current_lineup)
        else:
            self.importLineup()

    def createChoosePlayerFrame(self):
        """
        Create the frame for choosing a player for a selected position.
        """
        
        self.choosePlayerFrame = ctk.CTkFrame(self, fg_color = GREY_BACKGROUND, width = 400, height = 50, corner_radius = 0, border_color = APP_BLUE, border_width = 2)

        self.backButton = ctk.CTkButton(self.choosePlayerFrame, text = "Back", font = (APP_FONT, 15), fg_color = DARK_GREY, corner_radius = 10, height = 30, width = 100, hover_color = CLOSE_RED, command = self.stop_choosePlayer)
        self.backButton.place(relx = 0.95, rely = 0.5, anchor = "e")

        self.playerDropDown = ctk.CTkComboBox(self.choosePlayerFrame, font = (APP_FONT, 15), fg_color = DARK_GREY, border_color = DARK_GREY, button_color = DARK_GREY, button_hover_color = DARK_GREY, dropdown_fg_color = DARK_GREY, dropdown_hover_color = DARK_GREY, corner_radius = 10, width = 220, height = 30, state = "readonly", command = self.choosePosition)
        self.playerDropDown.place(relx = 0.05, rely = 0.5, anchor = "w")
        self.playerDropDown.set("Choose Player")

    def createSettingsFrame(self):
        """
        Create the settings frame for saving, loading, and managing lineups.
        """
        
        ctk.CTkButton(self.settingsFrame, text = "Back", font = (APP_FONT, 15), fg_color = DARK_GREY, corner_radius = 10, height = 30, width = 100, hover_color = CLOSE_RED, command = self.settingsFrame.place_forget).place(relx = 0.95, rely = 0.05, anchor = "ne")

        ctk.CTkLabel(self.settingsFrame, text = "Save lineup", font = (APP_FONT, 15), text_color = "white", fg_color = GREY_BACKGROUND).place(relx = 0.05, rely = 0.15, anchor = "w")
        self.saveBox = ctk.CTkEntry(self.settingsFrame, width = 250, height = 30, font = (APP_FONT, 10), fg_color = GREY_BACKGROUND, corner_radius = 10, border_color = GREY, border_width = 2)
        self.saveBox.place(relx = 0.05, rely = 0.28, anchor = "w")
        ctk.CTkButton(self.settingsFrame, text = "OK", fg_color = DARK_GREY, corner_radius = 10, height = 30, width = 30, command = self.saveLineup).place(relx = 0.95, rely = 0.28, anchor = "e")

        ctk.CTkLabel(self.settingsFrame, text = "Load lineup", font = (APP_FONT, 15), text_color = "white", fg_color = GREY_BACKGROUND).place(relx = 0.05, rely = 0.4, anchor = "w")
        self.loadBox = ctk.CTkComboBox(self.settingsFrame, width = 250, height = 30, font = (APP_FONT, 15), fg_color = DARK_GREY, border_color = DARK_GREY, button_color = DARK_GREY, button_hover_color = DARK_GREY, dropdown_fg_color = DARK_GREY, dropdown_hover_color = DARK_GREY, corner_radius = 10)
        self.loadBox.place(relx = 0.05, rely = 0.53, anchor = "w")
        ctk.CTkButton(self.settingsFrame, text = "OK", fg_color = DARK_GREY, corner_radius = 10, height = 30, width = 30, command = self.loadLineup).place(relx = 0.95, rely = 0.53, anchor = "e")

        ctk.CTkLabel(self.settingsFrame, text = "Automatic lineup", font = (APP_FONT, 15), text_color = "white", fg_color = GREY_BACKGROUND).place(relx = 0.05, rely = 0.65, anchor = "w")
        self.autoBox = ctk.CTkComboBox(self.settingsFrame, width = 250, height = 30, font = (APP_FONT, 15), fg_color = DARK_GREY, border_color = DARK_GREY, button_color = DARK_GREY, button_hover_color = DARK_GREY, dropdown_fg_color = DARK_GREY, dropdown_hover_color = DARK_GREY, corner_radius = 10)
        self.autoBox.place(relx = 0.05, rely = 0.78, anchor = "w")
        ctk.CTkButton(self.settingsFrame, text = "OK", fg_color = DARK_GREY, corner_radius = 10, height = 30, width = 30, command = self.autoLineup).place(relx = 0.95, rely = 0.78, anchor = "e")

        self.autoBox.configure(values = FORMATIONS_POSITIONS.keys())

        self.proposedLineupButton = ctk.CTkButton(self.settingsFrame, text = "Proposed Lineup", font = (APP_FONT, 15), text_color = "white", fg_color = DARK_GREY, corner_radius = 10, height = 30, width = 200, command = self.proposedLineup)
        self.proposedLineupButton.place(relx = 0.5, rely = 0.97, anchor = "s")

    def getDropdownValues(self):
        """
        Update the dropdown values for available positions based on the current lineup.
        """
        
        self.positionsCopy = {}
        for position, position_code in POSITION_CODES.items():
            if position not in self.selectedLineup.keys():
                self.positionsCopy[position] = position_code

        for position in self.selectedLineup.keys():
            if position in RELATED_POSITIONS:
                for related_position in RELATED_POSITIONS[position]:
                    if related_position in self.positionsCopy.keys():
                        del self.positionsCopy[related_position]

    def importLineup(self, loaded = None, auto = None):
        """
        Import a lineup either from a saved lineup or automatically generated.
        
        Args:
            loaded (dict, optional): A saved lineup to load. Defaults to None.
            auto (dict, optional): An automatically generated lineup. Defaults to None.
        """
        
        self.leagueTeams = LeagueTeams.get_league_by_team(self.team.id)
        self.league = League.get_league_by_id(self.leagueTeams.league_id)
        self.players = [player.id for player in Players.get_all_players_by_team(self.team.id, youths = False)]
        self.checkPositionsForYouth()

        playerData = [Players.get_player_by_id(player_id) for player_id in self.players]
        self.starRatings = Players.get_players_star_ratings(playerData, self.leagueID)

        if not loaded and not auto:
            # If neither, load from last match
            self.lastTeamMatch = Matches.get_team_last_match(self.team.id, Game.get_game_date(self.manager_id))

            if not self.lastTeamMatch:
                self.addSubstitutePlayers()
                return
            
            self.lineup = TeamLineup.get_lineup_by_match_and_team(self.lastTeamMatch.id, self.team.id)
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
                            self.swapLineupPositions,
                            self.starRatings[player.id]
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
        """
        Ensure all positions have enough players by adding youth players if necessary.
        """

        for position in POSITION_CODES.keys():
            playersForPosition = []
            for playerID in self.players:
                player = Players.get_player_by_id(playerID)
                if POSITION_CODES[position] not in player.specific_positions.split(","):
                    continue

                if not PlayerBans.check_bans_for_player(player.id, self.league.id):
                    playersForPosition.append(playerID)

            if POSITION_CODES[position] in POSITIONS_MAX.keys():
                maxPlayers = POSITIONS_MAX[POSITION_CODES[position]]
            else:
                maxPlayers = 1

            if len(playersForPosition) < maxPlayers:
                youths = PlayerBans.get_all_non_banned_youth_players_for_comp(self.team.id, self.league.id)
                youthForPosition = [youth for youth in youths if POSITION_CODES[position] in youth.specific_positions.split(",") and youth.id not in self.players]
                youthForPosition.sort(key = effective_ability, reverse = True)

                if len(youthForPosition) > 0:
                    self.players.append(youthForPosition[0].id)

                # If we had no keepers, add a second youth to give the player a substitute keeper
                if position == "Goalkeeper" and len(youthForPosition) > 1:
                    self.players.append(youthForPosition[1].id)

            elif position == "Goalkeeper" and len(playersForPosition) == 1:
                # If we only have one keeper, attempt to get a youth player to act as a sub
                youths = PlayerBans.get_all_non_banned_youth_players_for_comp(self.team.id, self.league.id)
                youthForPosition = [youth for youth in youths if POSITION_CODES[position] in youth.specific_positions.split(",") and youth.id not in self.players]
                youthForPosition.sort(key = effective_ability, reverse = True)

                if len(youthForPosition) > 0:
                    self.players.append(youthForPosition[0].id)

    def addSubstitutePlayers(self, importing = False, playersCount = None):
        """
        Add substitute players to the substitutes frame.
        
        Args:
            importing (bool, optional): Whether the lineup is being imported. Defaults to False.
            playersCount (int, optional): The number of players currently in the lineup. Defaults to None.
        """
        
        ctk.CTkLabel(self.substituteFrame, text = "Substitutes", font = (APP_FONT_BOLD, 20), fg_color = DARK_GREY).pack(pady = 5)
        
        players_per_row = 4

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
                sub_frame = SubstitutePlayer(frame, GREY_BACKGROUND, 100, 100, player, self.parent, self.league.id, row, col, self.starRatings[player.id], self.checkSubstitute)

                if importing and playersCount == 11 and self.gameTime:
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

    def turnSubsOn(self):
        """
        Enable substitutes if the lineup is complete and it's game time.
        """
        
        self.gameTime = True
        
        if self.lineupPitch.get_counter() == 11:
            for frame in self.substituteFrame.winfo_children():
                for child in frame.winfo_children():
                    if isinstance(child, SubstitutePlayer):
                        child.uncheckCheckBox()
                        child.showCheckBox() 

    def choosePlayer(self, selected_position):
        """
        Handle the selection of a position and display available players for that position.
        
        Args:
            selected_position (str): The position selected from the dropdown.
        """
        
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
        """
        Close the choose player frame and reset the dropdowns.
        """
        
        self.choosePlayerFrame.place_forget()
        self.dropDown.configure(state = "normal")
        self.resetButton.configure(state = "normal")
        self.playerDropDown.set("Choose Player")

    def choosePosition(self, selected_player):
        """
        Handle the selection of a player for the chosen position and update the lineup.

        Args:
            selected_player (str): The player selected from the dropdown. 
        """

        self.stop_choosePlayer()
        
        self.getDropdownValues()
        self.dropDown.configure(values = list(self.positionsCopy.keys()))

        self.lineupPitch.increment_counter()

        player = Players.get_player_by_name(selected_player.split(" ")[0], selected_player.split(" ")[1], self.team.id)
        self.selectedLineup[self.selected_position] = player.id

        for child in self.substituteFrame.winfo_children():
            child.destroy()

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
                            self.swapLineupPositions,
                            self.starRatings[player.id]
                        )


        self.addSubstitutePlayers(importing = True, playersCount = self.lineupPitch.get_counter())

    def removePlayer(self, frame, playerName, playerPosition):
        """
        Remove a player from the lineup and update the substitutes.

        Args:
            frame (ctk.CTkFrame): The frame of the player to be removed.
            playerName (str): The name of the player to be removed.
            playerPosition (str): The position of the player to be removed.
        """
        
        playerData = Players.get_player_by_name(playerName.split(" ")[0], playerName.split(" ")[1], self.team.id)
        for position, playerID in self.selectedLineup.items():
            if playerID == playerData.id:
                del self.selectedLineup[position]
                break
        
        self.lineupPitch.decrement_counter()
        frame.place_forget()

        for widget in self.substituteFrame.winfo_children():
            widget.destroy()

        self.addSubstitutePlayers(importing = True, playersCount = self.lineupPitch.get_counter())

        self.getDropdownValues()
        self.dropDown.configure(values = list(self.positionsCopy.keys()))

        # Reset the substitutes chosen
        self.substitutePlayers = []
        self.subCounter = 0

    def updateLineup(self, player, old_position, new_position):
        """
        Update the lineup when a player changes position.
        
        Args:
            player (Player): The player changing position.
            old_position (str): The old position of the player.
            new_position (str): The new position of the player.
        """
        
        if old_position in self.selectedLineup:
            del self.selectedLineup[old_position]

        self.selectedLineup[new_position] = player.id

        self.getDropdownValues()
        self.dropDown.configure(values = list(self.positionsCopy.keys()))

    def swapLineupPositions(self, position_1, position_2):
        """
        Swap two players' positions in the lineup.
        
        Args:
            position_1 (str): The first position to swap.
            position_2 (str): The second position to swap.
        """
        
        temp = self.selectedLineup[position_1]
        self.selectedLineup[position_1] = self.selectedLineup[position_2]
        self.selectedLineup[position_2] = temp

    def reset(self, addSubs = True):
        """
        Reset the lineup to an empty state.
        
        Args:
            addSubs (bool, optional): Whether to add substitute players after reset. Defaults to True.
        """
        
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
        """
        Handle the selection or deselection of a substitute player.
        
        Args:
            checkBox (ctk.CheckBox): The checkbox variable indicating selection.
            player (Player): The player being checked or unchecked.
        """
        
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
        """
        Finalize the lineup and proceed to the matchday.
        """
        
        players = [Players.get_player_by_id(playerID) for playerID in self.players]
        MatchDay(self.mainMenu, self.selectedLineup, self.substitutePlayers, self.team, players)

    def lineupSettings(self):
        """
        Display the lineup settings frame for saving, loading, and managing lineups.
        """
        
        self.settingsFrame.place(relx = 0.5, rely = 0.4, anchor = "center")
        self.settingsFrame.lift()

        currDate = Game.get_game_date(self.manager_id)
        canChooseProposed = Emails.check_email_sent("matchday_preview", self.matchday, currDate)

        if not canChooseProposed:
            self.proposedLineupButton.configure(state = "disabled")
        else:
            self.proposedLineupButton.configure(state = "normal")

        lineupNames = SavedLineups.get_all_lineup_names()
        self.loadBox.set("Choose Lineup")
        self.loadBox.configure(values = lineupNames)

        self.autoBox.set("Choose Lineup")

    def saveLineup(self, current = False):
        """
        Save the current lineup either as the current lineup or with a specified name.
        
        Args:
            current (bool, optional): Whether to save as the current lineup. Defaults to False.
        """

        if current:
            SavedLineups.add_current_lineup(self.selectedLineup)
            return

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

    def loadLineup(self):
        """
        Load a saved lineup by name.
        """
        
        lineupName = self.loadBox.get()
        if lineupName and lineupName != "Choose Lineup":
            self.settingsFrame.place_forget()
            self.reset(addSubs = False)

            chosenLineup = SavedLineups.get_lineup_by_name(lineupName)
            self.importLineup(loaded = chosenLineup)

    def autoLineup(self):
        """
        Automatically generate a lineup based on the selected formation.
        """
        
        lineupName = self.autoBox.get()
        if lineupName and lineupName != "Choose Lineup":
            self.settingsFrame.place_forget()
            self.reset(addSubs = False)

            lineupPositions = FORMATIONS_POSITIONS[lineupName]
            players = [Players.get_player_by_id(playerID) for playerID in self.players if not PlayerBans.check_bans_for_player(playerID, self.league.id)]
            sortedPlayers = sorted(players, key = effective_ability, reverse = True)

            youths = PlayerBans.get_all_non_banned_youth_players_for_comp(self.team.id, self.league.id)
            _, _, lineup = score_formation(sortedPlayers, lineupPositions, youths)
            lineup = {position: Players.get_player_by_id(pid) for position, pid in lineup.items()}

            self.importLineup(auto = lineup)

    def proposedLineup(self, lineup = None):
        """
        Activate the proposed lineup for the upcoming match.
        
        Args:
            lineup (dict, optional): The proposed lineup to be set. Defaults to None.
        """
        
        if lineup is None:
            lineup = getProposedLineup(self.team.id, self.opponent.id, self.league.id, Game.get_game_date(self.manager_id))
            
        lineup = {position: Players.get_player_by_id(pid) for position, pid in lineup.items()}
        self.settingsFrame.place_forget()
        self.reset(addSubs = False)
        self.importLineup(auto = lineup)

class Analysis(ctk.CTkFrame):
    def __init__(self, parent, manager_id):
        """
        Initialize the Analysis frame to display opponent team analysis.
        
        Args:
            parent (ctk.CTkFrame): The parent frame.
            manager_id (int): The manager ID for the current user.
        """
        
        super().__init__(parent, fg_color = TKINTER_BACKGROUND, width = 1000, height = 630, corner_radius = 0) 

        self.parent = parent
        self.manager_id = manager_id
        self.team = self.parent.team
        self.matchday = self.parent.matchday
        self.nextmatch = self.parent.nextmatch
        self.opponent = self.parent.opponent
        self.league = self.parent.league

        self.oppLastMatch = Matches.get_team_last_match(self.opponent.id, Game.get_game_date(self.manager_id))
        self.oppLast5Matches = Matches.get_team_last_5_matches(self.opponent.id, Game.get_game_date(self.manager_id))

        currDate = Game.get_game_date(self.manager_id)
        canSeeAnaylsis = Emails.check_email_sent("matchday_preview", self.matchday, currDate)

        if not self.oppLastMatch:
            ctk.CTkLabel(self, text = "No analysis available for this team.", font = (APP_FONT, 20), fg_color = TKINTER_BACKGROUND).place(relx = 0.5, rely = 0.5, anchor = "center")
            return
        
        if not canSeeAnaylsis:
            ctk.CTkLabel(self, text = "Analysis will be available 2 days before the game.", font = (APP_FONT, 20), fg_color = TKINTER_BACKGROUND).place(relx = 0.5, rely = 0.5, anchor = "center")
            return

        canvas = ctk.CTkCanvas(self, width = 5, height = 770, bg = GREY_BACKGROUND, bd = 0, highlightthickness = 0)
        canvas.place(relx = 0.5, rely = 0, anchor = "n")

        ctk.CTkLabel(self, text = f"{self.opponent.name} Analysis", font = (APP_FONT_BOLD, 30), fg_color = TKINTER_BACKGROUND).place(relx = 0.25, rely = 0.03, anchor = "center")

        self.best5PlayersFrame = ctk.CTkFrame(self, fg_color = GREY_BACKGROUND, width = 480, height = 170, corner_radius = 10)
        self.best5PlayersFrame.place(relx = 0.25, rely = 0.1, anchor = "n")
        self.best5PlayersFrame.pack_propagate(False)

        self.last5FormFrame = ctk.CTkFrame(self, fg_color = GREY_BACKGROUND, width = 480, height = 170, corner_radius = 10)
        self.last5FormFrame.place(relx = 0.25, rely = 0.4, anchor = "n")
        self.last5FormFrame.pack_propagate(False)

        self.topStatPlayersFrame = ctk.CTkFrame(self, fg_color = GREY_BACKGROUND, width = 480, height = 170, corner_radius = 10)
        self.topStatPlayersFrame.place(relx = 0.25, rely = 0.7, anchor = "n")
        self.topStatPlayersFrame.pack_propagate(False)

        self.predictedLineupFrame = ctk.CTkFrame(self, fg_color = GREY_BACKGROUND, width = 460, height = 460, corner_radius = 10)
        self.predictedLineupFrame.place(relx = 0.74, rely = 0.02, anchor = "n")
        self.predictedLineupFrame.pack_propagate(False)

        self.polyDataFrame = ctk.CTkFrame(self, fg_color = GREY_BACKGROUND, width = 460, height = 595, corner_radius = 10)

        self.dropDown = ctk.CTkComboBox(
            self,
            font = (APP_FONT, 12),
            fg_color = DARK_GREY,
            border_color = DARK_GREY,
            button_color = DARK_GREY,
            button_hover_color = DARK_GREY,
            corner_radius = 10,
            dropdown_fg_color = DARK_GREY,
            dropdown_hover_color = DARK_GREY,
            width = 210,
            height = 20,
            state = "readonly",
            values = ["Predicted Lineup & Last Meetings", "Polygraph Data"],
            command = self.changeFrame,
        )
        self.dropDown.set("Predicted Lineup & Last Meetings")
        self.dropDown.place(relx = 0.96, rely = 0, anchor = "ne")

        self.lastMeetingsFrame = ctk.CTkFrame(self, fg_color = GREY_BACKGROUND, width = 460, height = 130, corner_radius = 10)
        self.lastMeetingsFrame.place(relx = 0.74, rely = 0.76, anchor = "n")
        self.lastMeetingsFrame.pack_propagate(False)

        self.best5Players()
        self.last5Form()
        self.topStatPlayers()
        self.predictedLineup()
        self.polyData()
        self.lastMeetings()

    def best5Players(self):
        """
        Display the best 5 players of the opponent team over the last 5 games.
        """

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
        """
        Get the best 5 players based on average rating over the provided lineups.
        
        Args:
            lineups (list): A list of TeamLineup objects.
        """
        
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
            if data['matches'] >= len(lineups) - 2:
                data['average_rating'] = round(data['total_rating'] / data['matches'], 2)
                qualified_players[key] = data

        # Sort qualified players by average rating
        sorted_players = sorted(qualified_players.values(), key = lambda x: x['average_rating'], reverse = True)
        return sorted_players[:5]

    def last5Form(self):
        """
        Display the last 5 matches form of the opponent team.
        """
        
        
        ctk.CTkLabel(self.last5FormFrame, text = "Last games", font = (APP_FONT, 15), fg_color = GREY_BACKGROUND).pack(expand = True, fill = "x", pady = 5, anchor = "nw")

        for i, match in enumerate(self.oppLast5Matches):
            frame = ctk.CTkFrame(self.last5FormFrame, fg_color = DARK_GREY, width = 90, height = 120)
            frame.place(relx = 0.005 + i * 0.2, rely = 0.25, anchor = "nw")

            opponentID = match.away_id if match.home_id == self.opponent.id else match.home_id
            opponent = Teams.get_team_by_id(opponentID)
            src = Image.open(io.BytesIO(opponent.logo))
            src.thumbnail((60, 60))
            TeamLogo(frame, src, opponent, DARK_GREY, 0.5, 0.3, "center", self.parent)

            MatchProfileLink(frame, match, f"{match.score_home} - {match.score_away}", "white", 0.5, 0.65, "center", DARK_GREY, self.parent, 15, APP_FONT_BOLD)
            ctk.CTkLabel(frame, text = "H" if match.home_id == self.opponent.id else "A", font = (APP_FONT, 12), text_color = "white", fg_color = DARK_GREY, height = 0).place(relx = 0.5, rely = 0.8, anchor = "center")

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

            ctk.CTkCanvas(frame, bg = colour, height = 10, width = 120, bd = 0, highlightthickness = 0).place(relx = 0.5, rely = 0.99, anchor = "s")

    def topStatPlayers(self):
        """
        Display the leading players in key statistics for the opponent team.
        """
        
        ctk.CTkLabel(self.topStatPlayersFrame, text = "Leading players", font = (APP_FONT, 15), fg_color = GREY_BACKGROUND).pack(expand = True, fill = "x", pady = 5, anchor = "nw")

        stats = StatsManager.get_team_top_stats(self.opponent.id, 1)

        for i, (stat, players) in enumerate(stats.items()):
            frame = ctk.CTkFrame(self.topStatPlayersFrame, fg_color = DARK_GREY, width = 90, height = 120)
            frame.place(relx = 0.005 + i * 0.2, rely = 0.25, anchor = "nw")

            if len(players) == 0:
                ctk.CTkLabel(frame, text = "N/A", font = (APP_FONT, 12), text_color = "white", fg_color = DARK_GREY, height = 0).place(relx = 0.5, rely = 0.65, anchor = "center")
                ctk.CTkLabel(frame, text = "-", font = (APP_FONT_BOLD, 20), text_color = "white", fg_color = DARK_GREY, height = 0).place(relx = 0.5, rely = 0.85, anchor = "center")
            else:
                playerID, value = players[0]
                player = Players.get_player_by_id(playerID)
                PlayerProfileLink(frame, player, f"{player.first_name} {player.last_name}", "white", 0.5, 0.65, "center", DARK_GREY, self.parent, 12)
                ctk.CTkLabel(frame, text = value, font = (APP_FONT_BOLD, 20), text_color = "white", fg_color = DARK_GREY, height = 0).place(relx = 0.5, rely = 0.85, anchor = "center")
             
            src = Image.open(f"Images/{stat}.png")
            src.thumbnail((60, 60))
            img = ctk.CTkImage(src, None, (src.width, src.height))
            ctk.CTkLabel(frame, image = img, text = "", width = 50, height = 50, fg_color = DARK_GREY).place(relx = 0.5, rely = 0.3, anchor = "center")

    def predictedLineup(self):
        """
        Display the predicted lineup of the opponent team for the upcoming match.
        """
        
        ctk.CTkLabel(self.predictedLineupFrame, text = "Predicted lineup", font = (APP_FONT, 15), fg_color = GREY_BACKGROUND).pack(expand = True, fill = "x", pady = 5, anchor = "nw")

        playersFrame = ctk.CTkFrame(self.predictedLineupFrame, fg_color = GREY_BACKGROUND, width = 160, height = 400)
        playersFrame.place(relx = 0.01, rely = 0.08, anchor = "nw")

        ctk.CTkLabel(playersFrame, text = "Players", font = (APP_FONT_BOLD, 12), fg_color = GREY_BACKGROUND).pack(pady = 5, anchor = "center")

        lineupPitch = FootballPitchMatchDay(self.predictedLineupFrame, 340, 510, 0.99, 0.08, "ne", GREY_BACKGROUND, GREY_BACKGROUND)
        lineup = getPredictedLineup(self.opponent.id, Game.get_game_date(self.manager_id))
        
        for position, playerID in lineup.items():
            player = Players.get_player_by_id(playerID)
            lineupPitch.addPlayer(position, player.last_name)

            frame = ctk.CTkFrame(playersFrame, fg_color = GREY_BACKGROUND, width = 150, height = 15)
            frame.pack(expand = True, fill = "x", padx = 2, pady = (0, 5))

            ctk.CTkLabel(frame, text = f"{POSITION_CODES[position]}", font = (APP_FONT, 12), text_color = "white", fg_color = GREY_BACKGROUND).place(relx = 0.02, rely = 0.5, anchor = "w")
            ctk.CTkLabel(frame, text = "-", font = (APP_FONT, 12), text_color = "white", fg_color = GREY_BACKGROUND).place(relx = 0.18, rely = 0.5, anchor = "w")
            PlayerProfileLink(frame, player, f"{player.first_name} {player.last_name}", "white", 0.24, 0.5, "w", GREY_BACKGROUND, self.parent, 12)

    def polyData(self):
        """
        Fetches data to create data polygons and displays them in the polyDataFrame.
        """
        
        self.league_stats = MatchStats.get_league_best_avg_stats(self.league.id)
        self.league_averages = MatchStats.get_league_avg_stats(self.league.id)

        data1, data2, data3, overall_count, attacking_count, defending_count = self.get_poly_data(self.opponent.id)
        team_data1, team_data2, team_data3, _, _, _ = self.get_poly_data(self.team.id)
        
        self.poly1 = DataPolygon(self.polyDataFrame, data1, 250, 400, GREY_BACKGROUND, "white", format_ = 1, analysis = True, extra = team_data1)
        self.poly1.place(relx = 0.05, rely = 0.2, anchor = "w")

        self.poly3 = DataPolygon(self.polyDataFrame, data3, 250, 350, GREY_BACKGROUND, "white", format_ = 1, analysis = True, extra = team_data3)
        self.poly3.place(relx = 0.05, rely = 0.8, anchor = "w")

        self.poly2 = DataPolygon(self.polyDataFrame, data2, 250, 320, GREY_BACKGROUND, "white", format_ = 1, analysis = True, extra = team_data2)
        self.poly2.place(relx = 1, rely = 0.5, anchor = "e")

        ctk.CTkLabel(self.polyDataFrame, text = "Overall, attacking and defensive\ndata per match compared to league", font = (APP_FONT, 10), fg_color = GREY_BACKGROUND, height = 0).place(relx = 0.98, rely = 0.98, anchor = "se")

        src, text = self.text_src(overall_count)

        img_src = Image.open(src)
        img_src.thumbnail((60, 60))
        img = ctk.CTkImage(img_src, None, (img_src.width, img_src.height))
        ctk.CTkLabel(self.polyDataFrame, image = img, text = "", width = 50, height = 50, fg_color = GREY_BACKGROUND).place(relx = 0.67, rely = 0.2, anchor = "center")
        ctk.CTkLabel(self.polyDataFrame, text = text, font = (APP_FONT, 12), fg_color = GREY_BACKGROUND).place(relx = 0.83, rely = 0.2, anchor = "center")

        src, text = self.text_src(defending_count)

        img_src = Image.open(src)
        img_src.thumbnail((60, 60))
        img = ctk.CTkImage(img_src, None, (img_src.width, img_src.height))
        ctk.CTkLabel(self.polyDataFrame, image = img, text = "", width = 50, height = 50, fg_color = GREY_BACKGROUND).place(relx = 0.17, rely = 0.5, anchor = "center")
        ctk.CTkLabel(self.polyDataFrame, text = text, font = (APP_FONT, 12), fg_color = GREY_BACKGROUND).place(relx = 0.33, rely = 0.5, anchor = "center")

        src, text = self.text_src(attacking_count)

        img_src = Image.open(src)
        img_src.thumbnail((60, 60))
        img = ctk.CTkImage(img_src, None, (img_src.width, img_src.height))
        ctk.CTkLabel(self.polyDataFrame, image = img, text = "", width = 50, height = 50, fg_color = GREY_BACKGROUND).place(relx = 0.67, rely = 0.8, anchor = "center")
        ctk.CTkLabel(self.polyDataFrame, text = text, font = (APP_FONT, 12), fg_color = GREY_BACKGROUND).place(relx = 0.83, rely = 0.8, anchor = "center")

        ctk.CTkLabel(self.polyDataFrame, text = "Compare with\nteam averages", font = (APP_FONT, 12), fg_color = GREY_BACKGROUND, width = 0).place(relx = 0.8, rely = 0.05, anchor = "center")
        self.checkBox = ctk.CTkCheckBox(self.polyDataFrame, text = "", fg_color = GREY_BACKGROUND, checkbox_height = 25, checkbox_width = 25, border_width = 2, border_color = "white", corner_radius = 5, command = self.checkBox)
        self.checkBox.place(relx = 1, rely = 0.05, anchor = "center")

    def get_poly_data(self, team_id):
        """
        Calculate overall, attacking, and defending counts based on team statistics compared to league averages.

        Args:
            team_id (str): The ID of the team to analyze.
        """

        overall_count = 0
        attacking_count = 0
        defending_count = 0

        matches = Matches.get_all_played_matches_by_team_and_comp(team_id, self.league.id)
        stats = MatchStats.get_team_stats_matches(team_id, [m.id for m in matches])

        shots_per_match = [m["Shots"] for m in stats.values()]
        avg_shots = sum(shots_per_match) / len(shots_per_match) if shots_per_match else 0

        if avg_shots >= self.league_averages["Shots"]:
            overall_count += 1
            attacking_count += 1

        possession_per_match = [m["Possession"] for m in stats.values()]
        avg_possession = sum(possession_per_match) / len(possession_per_match) if possession_per_match else 0

        if avg_possession >= self.league_averages["Possession"]:
            overall_count += 1

        xg_per_match = [m["xG"] for m in stats.values()]
        avg_xg = sum(xg_per_match) / len(xg_per_match) if xg_per_match else 0

        if avg_xg >= self.league_averages["xG"]:
            attacking_count += 1

        big_chances_created_per_match = [m["Big chances created"] for m in stats.values()]
        avg_big_chances_created = sum(big_chances_created_per_match) / len(big_chances_created_per_match) if big_chances_created_per_match else 0

        if avg_big_chances_created >= self.league_averages["Big chances created"]:
            attacking_count += 1

        # big_chances_missed_per_match = [m["Big chances missed"] for m in stats.values()]
        # avg_big_chances_missed = sum(big_chances_missed_per_match) / len(big_chances_missed_per_match) if big_chances_missed_per_match else 0

        fouls_per_match = [m["Fouls"] for m in stats.values()]
        avg_fouls = sum(fouls_per_match) / len(fouls_per_match) if fouls_per_match else 0

        if avg_fouls <= self.league_averages["Fouls"]:
            defending_count += 1

        interceptions_per_match = [m["Interceptions"] for m in stats.values()]
        avg_interceptions = sum(interceptions_per_match) / len(interceptions_per_match) if interceptions_per_match else 0

        if avg_interceptions >= self.league_averages["Interceptions"]:
            defending_count += 1

        passes_per_match = [m["Passes"] for m in stats.values()]
        avg_passes = sum(passes_per_match) / len(passes_per_match) if passes_per_match else 0
        
        if avg_passes >= self.league_averages["Passes"]:
            overall_count += 1
            attacking_count += 1

        saves_per_match = [m["Saves"] for m in stats.values()]
        avg_saves = sum(saves_per_match) / len(saves_per_match) if saves_per_match else 0

        if avg_saves >= self.league_averages["Saves"]:
            defending_count += 1

        shots_on_target_per_match = [m["Shots on target"] for m in stats.values()]
        avg_shots_on_target = sum(shots_on_target_per_match) / len(shots_on_target_per_match) if shots_on_target_per_match else 0

        if avg_shots_on_target >= self.league_averages["Shots on target"]:
            attacking_count += 1

        shots_in_box_per_match = [m["Shots in the box"] for m in stats.values()]
        avg_shots_in_box = sum(shots_in_box_per_match) / len(shots_in_box_per_match) if shots_in_box_per_match else 0

        if avg_shots_in_box >= self.league_averages["Shots in the box"]:
            attacking_count += 1

        shots_out_box_per_match = [m["Shots outside the box"] for m in stats.values()]
        avg_shots_out_box = sum(shots_out_box_per_match) / len(shots_out_box_per_match) if shots_out_box_per_match else 0

        if avg_shots_out_box >= self.league_averages["Shots outside the box"]:
            attacking_count += 1

        tackles_per_match = [m["Tackles"] for m in stats.values()]
        avg_tackles = sum(tackles_per_match) / len(tackles_per_match) if tackles_per_match else 0

        if avg_tackles >= self.league_averages["Tackles"]:
            overall_count += 1
            defending_count += 1

        goals_scored = LeagueTeams.get_team_by_id(team_id).goals_scored
        avg_goals_scored = goals_scored / len(matches) if matches else 0

        max_scored = LeagueTeams.get_max_goals_scored(self.league.id)
        avg_max_scored = max_scored / len(matches) if matches else 0

        total_scored = LeagueTeams.get_total_goals_scored(self.league.id)
        total_matches = LeagueTeams.get_total_of_matches_played(self.league.id)
        league_avg_scored = total_scored / total_matches if total_matches > 0 else 0
    
        if avg_goals_scored >= league_avg_scored:
            overall_count += 1
            attacking_count += 1

        goals_conceded = LeagueTeams.get_team_by_id(team_id).goals_conceded
        avg_goals_conceded = goals_conceded / len(matches) if matches else 0

        max_conceded = LeagueTeams.get_max_goals_conceded(self.league.id)
        avg_max_conceded = max_conceded / len(matches) if matches else 0

        total_conceded = LeagueTeams.get_total_goals_conceded(self.league.id)
        league_avg_conceded = total_conceded / total_matches if total_matches > 0 else 0

        if avg_goals_conceded <= league_avg_conceded:
            overall_count += 1
            defending_count += 1

        clean_sheets = MatchEvents.get_team_clean_sheets(team_id, self.league.id)
        avg_clean_sheets = clean_sheets / len(matches) if matches else 0

        max_clean_sheets = MatchEvents.get_max_clean_sheets(self.league.id)
        avg_max_clean_sheets = max_clean_sheets / len(matches) if matches else 0

        total_clean_sheets = MatchEvents.get_total_clean_sheets(self.league.id)
        league_avg_clean_sheets = total_clean_sheets / total_matches if total_matches > 0 else 0

        if avg_clean_sheets >= league_avg_clean_sheets:
            defending_count += 1

        xg_against = MatchStats.get_team_xg_against(team_id, [m.id for m in matches])
        avg_xg_against = xg_against / len(matches) if matches else 0

        max_xg_against = MatchStats.get_league_max_xg_against(self.league.id)
        avg_max_xg_against = max_xg_against / len(matches) if matches else 0    

        total_xg_against = MatchStats.get_league_total_xg_against(self.league.id)
        league_avg_xg_against = total_xg_against / total_matches if total_matches > 0 else 0

        if avg_xg_against <= league_avg_xg_against:
            overall_count += 1
            defending_count += 1

        data1 = {
            f"Passes {avg_passes}" : [avg_passes, self.league_stats["Passes"]],
            f"Possession {avg_possession}" : [avg_possession, self.league_stats["Possession"]],
            f"Tackles {avg_tackles}" : [avg_tackles, self.league_stats["Tackles"]],
            f"Goals {avg_goals_scored}": [avg_goals_scored, avg_max_scored],
            f"Conceded {avg_goals_conceded}": [avg_goals_conceded, avg_max_conceded, True],
            f"xGA {avg_xg_against}": [avg_xg_against, avg_max_xg_against, True],
            f"Shots {avg_shots}": [avg_shots, self.league_stats["Shots"]],
        }

        data2 = {
            f"Passes {avg_passes}" : [avg_passes, self.league_stats["Passes"]],
            f"Goals {avg_goals_scored}": [avg_goals_scored, avg_max_scored],
            f"In Box {avg_shots_in_box}": [avg_shots_in_box, self.league_stats["Shots in the box"]],
            f"Shots {avg_shots}": [avg_shots, self.league_stats["Shots"]],
            f"Chances Created {avg_big_chances_created}": [avg_big_chances_created, self.league_stats["Big chances created"]],
            f"On Target {avg_shots_on_target}": [avg_shots_on_target, self.league_stats["Shots on target"]],
            f"xG {avg_xg}": [avg_xg, self.league_stats["xG"]],
            f"Out Box {avg_shots_out_box}": [avg_shots_out_box, self.league_stats["Shots outside the box"]],
        }

        data3 = {
            f"Conceded {avg_goals_conceded}": [avg_goals_conceded, avg_max_conceded, True],
            f"Interceptions {avg_interceptions}": [avg_interceptions, self.league_stats["Interceptions"]],
            f"Saves {avg_saves}": [avg_saves, self.league_stats["Saves"]],
            f"Tackles {avg_tackles}" : [avg_tackles, self.league_stats["Tackles"]],
            f"Clean Sheets {avg_clean_sheets}": [avg_clean_sheets, avg_max_clean_sheets],
            f"xGA {avg_xg_against}": [avg_xg_against, avg_max_xg_against, True],
            f"Fouls {avg_fouls}": [avg_fouls, self.league_stats["Fouls"], True],
        }

        return data1, data2, data3, overall_count, attacking_count, defending_count

    def text_src(self, count):
        """
        Helper function to create return text source based on count.

        Args:
            count (int): The count to be checked
        """

        if count >= 5:
            return "Images/player_good.png", "Above\naverage"
        elif count <= 2:
            return "Images/player_bad.png", "Below\naverage"
        else:
            return "Images/player_mid.png", "Average"    

    def checkBox(self):
        """
        Toggle to compare with team averages.
        """

        if self.checkBox.get() == 1:
            self.poly1.add_extra_data()
            self.poly2.add_extra_data()
            self.poly3.add_extra_data()
        else:
            self.poly1.remove_extra_data()
            self.poly2.remove_extra_data()
            self.poly3.remove_extra_data()

    def lastMeetings(self):
        """
        Display the last meetings between the opponent team and the user's team.
        """
        
        ctk.CTkLabel(self.lastMeetingsFrame, text = "Last meetings", font = (APP_FONT, 15), fg_color = GREY_BACKGROUND).pack(expand = True, fill = "x", pady = 5, anchor = "nw")

        lastMeetings = Matches.get_last_encounter(self.opponent.id, self.team.id)

        scrollable = False
        if len(lastMeetings) > 5:
            meetingsFrame = ctk.CTkScrollableFrame(self.lastMeetingsFrame, fg_color = GREY_BACKGROUND, width = 440, height = 80, orientation = "horizontal", scrollbar_button_color = GREY_BACKGROUND, scrollbar_button_hover_color = GREY_BACKGROUND)
            
            def _on_mousewheel(event):
                meetingsFrame._parent_canvas.xview_scroll(-10 * int(event.delta/120), "units")
                return "break"

            # Bind to the frame and its canvas
            meetingsFrame.bind('<MouseWheel>', _on_mousewheel)
            meetingsFrame._parent_canvas.bind('<MouseWheel>', _on_mousewheel)
            meetingsFrame.place(relx = 0.01, rely = 0.25, anchor = "nw")
            scrollable = True
        else:
            meetingsFrame = ctk.CTkFrame(self.lastMeetingsFrame, fg_color = GREY_BACKGROUND, width = 450, height = 90)
            meetingsFrame.place(relx = 0.01, rely = 0.25, anchor = "nw")
            meetingsFrame.pack_propagate(False)

        for i, match in enumerate(lastMeetings):
            frame = ctk.CTkFrame(meetingsFrame, fg_color = DARK_GREY, width = 80, height = 80)
            frame.pack(side = "left", padx = 5) if scrollable else frame.grid(row = 0, column  = i, padx = 5)

            league = League.get_league_by_id(match.league_id)
            MatchProfileLink(frame, match, f"{match.score_home} - {match.score_away}", "white", 0.5, 0.3, "center", DARK_GREY, self.parent, 20, APP_FONT_BOLD)
            ctk.CTkLabel(frame, text = league.name, font = (APP_FONT, 10), text_color = "white", fg_color = DARK_GREY, height = 0).place(relx = 0.5, rely = 0.6, anchor = "center")
            ctk.CTkLabel(frame, text = "H" if match.home_id == self.opponent.id else "A", font = (APP_FONT, 12), text_color = "white", fg_color = DARK_GREY, height = 0).place(relx = 0.5, rely = 0.85, anchor = "center")

            if scrollable:
                frame.bind('<MouseWheel>', _on_mousewheel)
                for child in frame.winfo_children():
                    child.bind('<MouseWheel>', _on_mousewheel)

    def changeFrame(self, selected):
        """
        Change the displayed frame between predicted lineup and polygraph data.

        Args:
            selected (str): The selected option from the dropdown.
        """
        
        if selected == "Predicted Lineup & Last Meetings":
            self.polyDataFrame.place_forget()
            self.predictedLineupFrame.place(relx = 0.74, rely = 0.02, anchor = "n")
            self.lastMeetingsFrame.place(relx = 0.74, rely = 0.76, anchor = "n")
        else:
            self.predictedLineupFrame.place_forget()
            self.lastMeetingsFrame.place_forget()
            self.polyDataFrame.place(relx = 0.74, rely = 0.02, anchor = "n")