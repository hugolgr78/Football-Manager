import customtkinter as ctk
from settings import *
from data.database import *
from data.gamesDatabase import *
from utils.frames import FootballPitchLineup, SubstitutePlayer, LineupPlayerFrame
from tabs.matchday import MatchDay

class Tactics(ctk.CTkFrame):
    def __init__(self, parent, session, manager_id):
        super().__init__(parent, fg_color = TKINTER_BACKGROUND, width = 1000, height = 700, corner_radius = 0)

        self.session = session
        self.manager_id = manager_id
        self.parent = parent
        self.selected_position = None

        self.team = Teams.get_teams_by_manager(self.session, self.manager_id)[0]
        self.players = Players.get_all_players_by_team(self.session, self.team.id)

        self.selectedLineup = {}
        self.substitutePlayers = []
        self.subCounter = 0

        self.positionsCopy = POSITION_CODES.copy()

        ctk.CTkLabel(self, text = "Lineup", font = (APP_FONT_BOLD, 35), text_color = "white", fg_color = TKINTER_BACKGROUND).place(relx = 0.03, rely = 0.05, anchor = "w")

        self.lineupPitch = FootballPitchLineup(self, 450, 675, 0.02, 0.08, "nw", TKINTER_BACKGROUND, "green")

        self.addFrame = ctk.CTkFrame(self, fg_color = GREY_BACKGROUND, width = 400, height = 50, corner_radius = 10)
        self.addFrame.place(relx = 0.02, rely = 0.98, anchor = "sw")

        ctk.CTkLabel(self.addFrame, text = "Add Position:", font = (APP_FONT, 20), text_color = "white", fg_color = GREY_BACKGROUND).place(relx = 0.05, rely = 0.5, anchor = "w")

        self.dropDown = ctk.CTkComboBox(self.addFrame, font = (APP_FONT, 15), fg_color = GREY_BACKGROUND, corner_radius = 10, dropdown_fg_color = GREY_BACKGROUND, dropdown_hover_color = DARK_GREY, width = 220, height = 30, state = "readonly", command = self.choosePlayer)
        self.dropDown.place(relx = 0.4, rely = 0.5, anchor = "w")
        self.dropDown.set("Choose Position")
        self.dropDown.configure(values = list(POSITION_CODES.keys()))

        self.resetButton = ctk.CTkButton(self, text = "Reset", font = (APP_FONT, 15), fg_color = GREY_BACKGROUND, corner_radius = 10, height = 50, width = 240, command = self.reset)
        self.resetButton.place(relx = 0.43, rely = 0.98, anchor = "sw")

        self.finishButton = ctk.CTkButton(self, text = "Matchday >>", font = (APP_FONT, 15), fg_color = APP_BLUE, corner_radius = 10, height = 50, width = 300, state = "disabled", command = self.finishLineup)
        self.finishButton.place(relx = 0.98, rely = 0.98, anchor = "se")

        self.substituteFrame = ctk.CTkScrollableFrame(self, fg_color = GREY_BACKGROUND, width = 520, height = 520, corner_radius = 10)
        self.substituteFrame.place(relx = 0.98, rely = 0.1, anchor = "ne")

        self.createChoosePlayerFrame()
        self.importLineup()

    def createChoosePlayerFrame(self):
        self.choosePlayerFrame = ctk.CTkFrame(self, fg_color = GREY_BACKGROUND, width = 400, height = 50, corner_radius = 0, border_color = APP_BLUE, border_width = 2)

        self.backButton = ctk.CTkButton(self.choosePlayerFrame, text = "Back", font = (APP_FONT, 15), fg_color = DARK_GREY, corner_radius = 10, height = 30, width = 100, hover_color = CLOSE_RED, command = self.stop_choosePlayer)
        self.backButton.place(relx = 0.95, rely = 0.5, anchor = "e")

        self.playerDropDown = ctk.CTkComboBox(self.choosePlayerFrame, font = (APP_FONT, 15), fg_color = GREY_BACKGROUND, corner_radius = 10, dropdown_fg_color = GREY_BACKGROUND, dropdown_hover_color = DARK_GREY, width = 220, height = 30, state = "readonly", command = self.choosePosition)
        self.playerDropDown.place(relx = 0.05, rely = 0.5, anchor = "w")
        self.playerDropDown.set("Choose Player")

    def importLineup(self):
        self.leagueTeams = LeagueTeams.get_league_by_team(self.session, self.team.id)
        self.league = League.get_league_by_id(self.session, self.leagueTeams.league_id)
        self.players = Players.get_all_players_by_team(self.session, self.team.id, youths = False)

        self.checkPositionsForYouth()

        lastMatchday = self.league.current_matchday - 1

        if lastMatchday == 0:
            self.addSubstitutePlayers()
            return
        
        self.matchdayMatches = Matches.get_matchday_for_league(self.session, self.league.id, lastMatchday)

        for match in self.matchdayMatches:
            if match.home_id == self.team.id or match.away_id == self.team.id:
                self.lastTeamMatch = match
                self.lineup = TeamLineup.get_lineup_by_match_and_team(self.session, match.id, self.team.id)

        playersCount = 0
        for playerData in self.lineup:
            position = playerData.position
            positionCode = POSITION_CODES[position]
            player = Players.get_player_by_id(self.session, playerData.player_id)

            # Remove any youths that arent in the players list as the position is now free
            if player.player_role == "Youth Team" and player not in self.players:
                continue

            events = MatchEvents.get_events_by_match_and_player(self.session, self.lastTeamMatch.id, player.id)
            
            # Remove any players that were subbed on
            if events:
                subOnEvents = [event for event in events if event.event_type == "sub_on" and event.player_id == player.id]

                if subOnEvents:
                    continue
            
            # Remove any players that are banned
            if PlayerBans.check_bans_for_player(self.session, player.id, self.league.id):
                continue

            playersCount += 1

            name = player.first_name + " " + player.last_name
            self.selectedLineup[position] = player

            LineupPlayerFrame(self.lineupPitch, 
                            POSITIONS_PITCH_POSITIONS[position][0], 
                            POSITIONS_PITCH_POSITIONS[position][1], 
                            "center", 
                            GREY_BACKGROUND,
                            65, 
                            65, 
                            name,
                            positionCode,
                            position,
                            self.removePlayer
                        )
            
        self.lineupPitch.set_counter(playersCount)

        if playersCount == 11:
            self.dropDown.configure(state = "disabled")

        ctk.CTkLabel(self.substituteFrame, text = "Substitutes", font = (APP_FONT_BOLD, 20), fg_color = GREY_BACKGROUND).pack(pady = 5)
        for player in self.players:
            name = player.first_name + " " + player.last_name
            if player not in self.selectedLineup.values():
                frame = SubstitutePlayer(self.substituteFrame, GREY_BACKGROUND, 20, 550, player, self.checkSubstitute, self.session, self, self.league.id) 

                if playersCount == 11:
                    frame.showCheckBox()

        for position in POSITION_CODES.keys():
            if position in self.selectedLineup:
                del self.positionsCopy[position]
            
        self.dropDown.configure(values = self.positionsCopy)

    def checkPositionsForYouth(self):
        nonBannedPlayers = PlayerBans.get_all_non_banned_players_for_comp(self.session, self.team.id, self.league.id)

        for position in POSITION_CODES.keys():

            playersForPosition = [player for player in nonBannedPlayers if POSITION_CODES[position] in player.specific_positions.split(",")]

            if position in DEFENSIVE_POSITIONS:
                overallPosition = "defender"
            elif position in MIDFIELD_POSITIONS:
                overallPosition = "midfielder"
            elif position in ATTACKING_POSITIONS:
                overallPosition = "forward"
            else:
                overallPosition = "goalkeeper"

            if len(playersForPosition) == 0:
                youths = PlayerBans.get_all_non_banned_youth_players_for_comp(self.session, self.team.id, self.league.id)
                youthForPosition = [youth for youth in youths if POSITION_CODES[position] in youth.specific_positions.split(",") and youth not in self.players]

                if len(youthForPosition) > 0:
                    self.players.append(youthForPosition[0])
                else:
                    newYouth = Players.add_player(self.session, self.team.id, overallPosition, position, "Youth Team")
                    self.players.append(newYouth)

                if position == "Goalkeeper":
                    newYouth = Players.add_player(self.session, self.team.id, overallPosition, position, "Youth Team")
                    self.players.append(newYouth)

            elif position == "Goalkeeper" and len(playersForPosition) == 1:
                youths = PlayerBans.get_all_non_banned_youth_players_for_comp(self.session, self.team.id, self.league.id)
                youthForPosition = [youth for youth in youths if POSITION_CODES[position] in youth.specific_positions.split(",") and youth not in self.players]

                if len(youthForPosition) > 0:
                    self.players.append(youthForPosition[0])
                else:
                    newYouth = Players.add_player(self.session, self.team.id, overallPosition, position, "Youth Team")
                    self.players.append(newYouth)

    def addSubstitutePlayers(self):
        ctk.CTkLabel(self.substituteFrame, text = "Substitutes", font = (APP_FONT_BOLD, 20), fg_color = GREY_BACKGROUND).pack(pady = 5)
        
        for player in self.players:
            SubstitutePlayer(self.substituteFrame, GREY_BACKGROUND, 20, 550, player, self.checkSubstitute, self.session, self, self.league.id)

    def choosePlayer(self, selected_position):
        self.selected_position = selected_position
        self.dropDown.configure(state = "disabled")
        self.resetButton.configure(state = "disabled")

        self.choosePlayerFrame.place(relx = 0.225, rely = 0.5, anchor = "center")

        values = []
        for player in self.players:
            playerName = player.first_name + " " + player.last_name
            if POSITION_CODES[selected_position] in player.specific_positions.split(",") and player not in self.selectedLineup.values() and not PlayerBans.check_bans_for_player(self.session, player.id, self.league.id):
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

        player = Players.get_player_by_name(self.session, selected_player.split(" ")[0], selected_player.split(" ")[1])
        self.selectedLineup[self.selected_position] = player

        LineupPlayerFrame(self.lineupPitch, 
                            POSITIONS_PITCH_POSITIONS[self.selected_position][0], 
                            POSITIONS_PITCH_POSITIONS[self.selected_position][1], 
                            "center", 
                            GREY_BACKGROUND,
                            65, 
                            65, 
                            selected_player,
                            POSITION_CODES[self.selected_position],
                            self.selected_position,
                            self.removePlayer
                        )

        for frame in self.substituteFrame.winfo_children():
            if frame.winfo_children()[1].cget("text") == selected_player:
                frame.destroy()

        if self.lineupPitch.get_counter() == 11:
            self.dropDown.configure(state = "disabled")

            for frame in self.substituteFrame.winfo_children():
                if isinstance(frame, SubstitutePlayer):
                    frame.showCheckBox()

    def removePlayer(self, frame, playerName, playerPosition):
        for position, selected_player in self.selectedLineup.items():
            if selected_player.first_name + " " + selected_player.last_name == playerName:
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

        player = Players.get_player_by_name(self.session, playerName.split(" ")[0], playerName.split(" ")[1])
        SubstitutePlayer(self.substituteFrame, GREY_BACKGROUND, 20, 550, player, self.checkSubstitute, self.session, self, self.league.id)

        self.dropDown.configure(values = list(self.positionsCopy.keys()))
        self.substitutePlayers = []

        self.subCounter = 0

        if self.lineupPitch.get_counter() < 11:
            self.dropDown.configure(state = "readonly")
            self.finishButton.configure(state = "disabled")

            for frame in self.substituteFrame.winfo_children():
                if isinstance(frame, SubstitutePlayer):
                    frame.hideCheckBox()
                    frame.uncheckCheckBox()

    def reset(self):
        self.lineupPitch.destroy()
        self.lineupPitch = FootballPitchLineup(self, 450, 675, 0.02, 0.08, "nw", TKINTER_BACKGROUND, "green")

        self.lineupPitch.reset_counter()
        self.dropDown.configure(state = "normal")
        self.dropDown.set("Choose Position")
        self.positionsCopy = POSITION_CODES.copy()
        self.dropDown.configure(values = list(self.positionsCopy.keys()))
        self.selectedLineup = {}
        self.finishButton.configure(state = "disabled")

        for frame in self.substituteFrame.winfo_children():
            frame.destroy()
        
        self.addSubstitutePlayers()

        self.choosePlayerFrame.destroy()
        self.createChoosePlayerFrame()

    def checkSubstitute(self, checkBox, player):
        if checkBox.get() == 0:
            del self.substitutePlayers[self.substitutePlayers.index(player)]
            self.subCounter -= 1

            if self.subCounter < MATCHDAY_SUBS:
                self.finishButton.configure(state = "disabled")

                for frame in self.substituteFrame.winfo_children():
                    if isinstance(frame, SubstitutePlayer):
                        frame.enableCheckBox()
        else:
            self.substitutePlayers.append(player)
            self.subCounter += 1

            if self.subCounter == MATCHDAY_SUBS:
                self.finishButton.configure(state = "normal")

                for frame in self.substituteFrame.winfo_children():
                    if isinstance(frame, SubstitutePlayer):
                        if frame.checkBox.get() == 0:
                            frame.disableCheckBox()

    def finishLineup(self):
        MatchDay(self.parent, self.session, self.selectedLineup, self.substitutePlayers, self.team, self.players)