import customtkinter as ctk
from settings import *
from data.database import *
from data.gamesDatabase import *
from utils.score import Score
from collections import defaultdict
import itertools, threading
from data.database import session_factory

class Match():
    def __init__(self, session, match):

        self.session = session
        self.match = match

        self.homeTeam = Teams.get_team_by_id(self.session, self.match.home_id)
        self.awayTeam = Teams.get_team_by_id(self.session, self.match.away_id)

        self.manager = Managers.get_all_user_managers(self.session)[0]
        self.managerName = f"{self.manager.first_name}{self.manager.last_name}"

        # As soon as a player is subbed in, the player is added to the current lineup and the subbed off player is removed
        # As soon as a player is subbed off, the player is added to the final lineup
        # At end of game, add all players in the current lineup to the final lineup and save the final lineup
        self.homeFinalLineup = {}
        self.awayFinalLineup = {}
        self.homeCurrentLineup = None
        self.awayCurrentLineup = None

        self.homeCurrentSubs = None
        self.awayCurrentSubs = None

        self.homeEvents = {}
        self.awayEvents = {}
        self.homeProcessedEvents = {}
        self.awayProcessedEvents = {}

        self.homeRatings = {}
        self.awayRatings = {}
        self.ratingsBoost = None
        self.ratingsDecay = None

        self.homeCleanSheet = False
        self.awayCleanSheet = False

        self.numHomeYellows = 0
        self.numAwayYellows = 0
        self.numHomeReds = 0
        self.numAwayReds = 0

        self.score = None

        self.extraTimeHalf = 0
        self.extraTimeFull = 0
        self.halfTime = False
        self.fullTime = False

    def createTeamLineup(self, teamID, home):

        lineup = {}
        substitutes = []

        formations = list(FORMATIONS_CHANCES.keys())
        weights = list(FORMATIONS_CHANCES.values())
        oppFormation = random.choices(formations, weights = weights, k = 1)[0]
        defNums, midNums, _ = map(int, oppFormation.split("-"))

        players = PlayerBans.get_all_non_banned_players_for_comp(self.session, teamID, self.match.league_id)
        goalkeepers = [player for player in players if player.position == "goalkeeper"]
        defenders = [player for player in players if player.position == "defender"]
        midfielders = [player for player in players if player.position == "midfielder"]
        attackers = [player for player in players if player.position == "forward"]

        # goalkeeper
        if len(goalkeepers) == 0:
            self.getYouthPlayer(teamID, "Goalkeeper", lineup = lineup)
        else:
            lineup["Goalkeeper"] = goalkeepers[0]

        # defenders
        self.choosePlayers(FORMATIONS_POSITIONS[oppFormation][1:defNums + 1], defenders, lineup, teamID)

        # midfielders
        self.choosePlayers(FORMATIONS_POSITIONS[oppFormation][defNums + 1:defNums + midNums + 1], midfielders, lineup, teamID)

        # attackers
        self.choosePlayers(FORMATIONS_POSITIONS[oppFormation][defNums + midNums + 1:], attackers, lineup, teamID)

        # substitutes
        if len(goalkeepers) > 1:
            substitutes.append(goalkeepers[1])
        else:
            self.getYouthPlayer(teamID, "Goalkeeper", substitutes = substitutes)

        # Add 2 defenders to substitutes
        defender_count = 0
        for defender in defenders:
            if defender not in lineup.values() and defender_count < 2:
                substitutes.append(defender)
                defender_count += 1

        if defender_count != 2:
            for _ in range(2 - defender_count):
                specific_position = random.choice(DEFENSIVE_POSITIONS)
                self.getYouthPlayer(teamID, specific_position, substitutes = substitutes)

        # Add 2 midfielders to substitutes
        midfielder_count = 0
        for midfielder in midfielders:
            if midfielder not in lineup.values() and midfielder_count < 2:
                substitutes.append(midfielder)
                midfielder_count += 1

        if midfielder_count != 2:
            for _ in range(2 - midfielder_count):
                specific_position = random.choice(MIDFIELD_POSITIONS)
                self.getYouthPlayer(teamID, specific_position, substitutes = substitutes)

        # Add 2 attackers to substitutes
        attacker_count = 0
        for attacker in attackers:
            if attacker not in lineup.values() and attacker_count < 2:
                substitutes.append(attacker)
                attacker_count += 1

        if attacker_count != 2:
            for _ in range(2 - attacker_count):
                specific_position = random.choice(ATTACKING_POSITIONS)
                self.getYouthPlayer(teamID, specific_position, substitutes = substitutes)

        if home:
            self.homeCurrentLineup = lineup
            self.homeCurrentSubs = substitutes
        else:
            self.awayCurrentLineup = lineup
            self.awayCurrentSubs = substitutes

    def choosePlayers(self, position_names, players, lineup, teamID):

        position_options = defaultdict(list)

        # for position in position_names:
        #     lineup[position] = None

        for position in position_names:
            position_options[position] = []
            for player in players:
                if POSITION_CODES[position] in player.specific_positions:
                    position_options[position].append(player)

        assigned_players = set()

        while position_options != {}:
            # Step 2: Sort full position names by scarcity (fewest available players first)
            sorted_positions = sorted(position_options.keys(), key = lambda pos: len(position_options[pos]))

            # Pick the position with the least available players
            position = sorted_positions[0]
            available_players = [p for p in position_options[position] if p not in assigned_players]

            if not available_players: # get a youth team player from db or create a new one
                self.getYouthPlayer(teamID, position, lineup = lineup)
                del position_options[position]
                continue

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

    def getYouthPlayer(self, teamID, position, lineup = None, substitutes = None):
        youthPlayers = PlayerBans.get_all_non_banned_youth_players_for_comp(self.session, teamID, self.match.league_id)

        if youthPlayers:
            for player in youthPlayers:
                if POSITION_CODES[position] in player.specific_positions and player not in lineup.values():
                    if lineup is not None:
                        lineup[position] = player
                    else:
                        substitutes.append(player)
                    return
                
        if position in DEFENSIVE_POSITIONS:
            overallPosition = "defender"
        elif position in MIDFIELD_POSITIONS:
            overallPosition = "midfielder"
        elif position in ATTACKING_POSITIONS:
            overallPosition = "forward"
        else:
            overallPosition = "goalkeeper"
                
        # list empty or no player found with the specific position
        newYouth = Players.add_player(self.session, teamID, overallPosition, position, "Youth Team")
        if lineup is not None: # if lineup is passed as None, then add to subs
            lineup[position] = newYouth
        else:
            substitutes.append(newYouth)

    def generateScore(self, teamMatch = False, home = False):
        self.score = Score(self.homeTeam, self.awayTeam, self.homeCurrentLineup, self.awayCurrentLineup)
        self.generateEventTypesAndTimes(teamMatch, home)

    def generateEventTypesAndTimes(self, teamMatch, home):

        self.getYellowsAndReds()
        self.getInjuries()
        self.getSubstitutions(teamMatch, home)

        scoreHome = self.score.getScore()[0]
        scoreAway = self.score.getScore()[1]

        for _ in range (scoreHome):
            type_ = random.choices(list(GOAL_TYPE_CHANCES.keys()), weights = [GOAL_TYPE_CHANCES[goalType] for goalType in GOAL_TYPE_CHANCES])[0]
            time, extra = self.generateTime()
            self.checkTime(time, self.homeEvents)

            if type_ == "penalty":
                if random.random() < PENALTY_SCORE_CHANCE:
                    type_ = "penalty_goal"
                else:
                    type_ = "penalty_miss"
                    self.score.appendScore(-1, True)

            self.homeEvents[time] = {
                "type": type_,
                "extra": extra
            }

        for _ in range (scoreAway):
            type_ = random.choices(list(GOAL_TYPE_CHANCES.keys()), weights = [GOAL_TYPE_CHANCES[goalType] for goalType in GOAL_TYPE_CHANCES])[0]
            time, extra = self.generateTime()
            self.checkTime(time, self.awayEvents)

            if type_ == "penalty":
                if random.random() < PENALTY_SCORE_CHANCE:
                    type_ = "penalty_goal"
                else:
                    type_ = "penalty_miss"
                    self.score.appendScore(-1, False)

            self.awayEvents[time] = {
                "type": type_,
                "extra": extra
            }

        self.add_events(self.homeEvents, self.numHomeYellows, "yellow_card")
        self.add_events(self.awayEvents, self.numAwayYellows, "yellow_card")

        # Add red card events
        self.add_events(self.homeEvents, self.numHomeReds, "red_card")
        self.add_events(self.awayEvents, self.numAwayReds, "red_card")

        if self.homeInjury:
            self.add_events(self.homeEvents, 1, "injury")
        if self.awayInjury:
            self.add_events(self.awayEvents, 1, "injury")

        if self.homeSubs:
            if home and teamMatch:
                self.add_events(self.homeEvents, self.homeSubs, "substitution", self.homeInjury, managing_team = True)
            else:
                self.add_events(self.homeEvents, self.homeSubs, "substitution", self.homeInjury)
        if self.awaySubs:
            if not home and teamMatch:
                self.add_events(self.awayEvents, self.awaySubs, "substitution", self.awayInjury, managing_team = True)
            else:
                self.add_events(self.awayEvents, self.awaySubs, "substitution", self.awayInjury)

        if teamMatch:
            print("Home Events: ", self.homeEvents)
            print("Away Events: ", self.awayEvents)

    def checkSubsitutionTime(self, time, events):
        # This function is here because i want the substitution after an injury to always be a minute after, so if there are any events at that time, add 5 mins to that event and check
        for event_time, _ in events.items():
            if event_time == time:
                minute = int(time.split(":")[0])
                event_time = str(minute + 5) + ":" + time.split(":")[1]
                self.checkTime(time, events)

    def checkTime(self, time, events):
        while time in events:
            seconds = int(time.split(":")[1])
            minutes = int(time.split(":")[0])

            if seconds + 10 > 60:
                minutes += 1
                seconds = 0
            else:
                seconds += 10

            time = str(minutes) + ":" + str(seconds)
        
        return time

    def getYellowsAndReds(self):
        self.referee = Referees.get_referee_by_id(self.session, self.match.referee_id)
        severity = self.referee.severity

        choices = len(LOW_YELLOW_CARD)

        if severity == "low":
            self.numHomeYellows = random.choices(range(0, choices), weights = LOW_YELLOW_CARD)[0]
            self.numAwayYellows = random.choices(range(0, choices), weights = LOW_YELLOW_CARD)[0]
            self.numHomeReds = random.choices(range(0, choices - 1), weights = LOW_RED_CARD)[0]
            self.numAwayReds = random.choices(range(0, choices - 1), weights = LOW_RED_CARD)[0]
        elif severity == "medium":
            self.numHomeYellows = random.choices(range(0, choices + 1), weights = MEDIUM_YELLOW_CARD)[0]
            self.numAwayYellows = random.choices(range(0, choices + 1), weights = MEDIUM_YELLOW_CARD)[0]
            self.numHomeReds = random.choices(range(0, choices), weights = MEDIUM_RED_CARD)[0]
            self.numAwayReds = random.choices(range(0, choices), weights = MEDIUM_RED_CARD)[0]
        else:
            self.numHomeYellows = random.choices(range(0, choices + 2), weights = HIGH_YELLOW_CARD)[0]
            self.numAwayYellows = random.choices(range(0, choices + 2), weights = HIGH_YELLOW_CARD)[0]
            self.numHomeReds = random.choices(range(0, choices + 1), weights = HIGH_RED_CARD)[0]
            self.numAwayReds = random.choices(range(0, choices + 1), weights = HIGH_RED_CARD)[0]

    def getInjuries(self):
        self.homeInjury = False
        self.injuredHomePlayer = None
        self.awayInjury = False
        self.injuredAwayPlayer = None

        if random.random() < INJURY_CHANCE:
            self.homeInjury = True
        if random.random() < INJURY_CHANCE:
            self.awayInjury = True

    def getSubstitutions(self, teamMatch, home):

        ## Create substition events for every match, and for the match of the managing team, create the substitutions for the opponent only 
        weights = [0.05, 0.1, 0.1, 0.3, 0.35, 0.1] # 0, 1, 2, 3, 4, 5 subs
        if not teamMatch:
            self.homeSubs = random.choices(range(0, MAX_SUBS + 1), weights = weights, k = 1)[0]
            self.awaySubs = random.choices(range(0, MAX_SUBS + 1), weights = weights, k = 1)[0]
        else:
            if not home:
                self.homeSubs = random.choices(range(0, MAX_SUBS + 1), weights = weights, k = 1)[0]
                self.awaySubs = None
            else:
                self.awaySubs = random.choices(range(0, MAX_SUBS + 1), weights = weights, k = 1)[0]
                self.homeSubs = None

    def generateTime(self, minute = None):

        if not minute:
            minute = str(random.choices(range(1, 91))[0])

        extra = False
        if int(minute) == 45 or int(minute) == 90:
            additionalTime = random.randint(0, 4)
            minute = str(int(minute) + additionalTime)
            extra = True

        second = str(random.choices(range(0, 60))[0])
        time = minute + ":" + second

        return time, extra

    def add_events(self, events_dict, num_events, event_type, injury = None, managing_team = False):
        new_events = []
        injurySub = False
        for _ in range(num_events):
            if event_type != "substitution":
                time, extra = self.generateTime()
                time = self.checkTime(time, events_dict)

                new_events.append((time, {"type": event_type, "extra": extra}))
            else:
                if injury and not managing_team and not injurySub:
                    for event_time, event in list(events_dict.items()):
                        if event["type"] == "injury":
                            minute = event_time.split(":")[0]
                            sub_time = str(int(minute) + 1) + ":30" 

                            new_events.append((sub_time, {"type": "substitution", "player": None, "player_off": None, "player_on": None, "injury": True, "extra": event["extra"]}))
                            self.checkSubsitutionTime(sub_time, events_dict)
                            injurySub = True
                else:
                    minute_ranges = list(range(46, 91))
                    weights = [2] * 19 + [3] * 11 + [1] * 15  # Weights for 46-65, 65-75, 75-90
                    minute = str(random.choices(minute_ranges, weights = weights, k = 1)[0])
                    time, extra = self.generateTime(minute = minute)
                    time = self.checkTime(time, events_dict)
                    new_events.append((time, {"type": "substitution", "player": None, "player_off": None, "player_on": None, "injury": False, "extra": extra}))

        for time, event in new_events:
            events_dict[time] = event
    
    def getEventPlayer(self, event, home, time, teamMatch = None, managing_team = False):

        if home:
            lineup = self.homeCurrentLineup
            subs = self.homeCurrentSubs
            finalLineup = self.homeFinalLineup
            events = self.homeEvents
            processedEvents = self.homeProcessedEvents
            subsCount = self.homeSubs     
        else:
            lineup = self.awayCurrentLineup
            subs = self.awayCurrentSubs
            finalLineup = self.awayFinalLineup
            events = self.awayEvents
            processedEvents = self.awayProcessedEvents
            subsCount = self.awaySubs

        if event["type"] == "goal":
            scorerPosition = random.choices(list(SCORER_CHANCES.keys()), weights = list(SCORER_CHANCES.values()), k = 1)[0]
            players = [player for player in lineup.values() if player.position == scorerPosition]

            while len(players) == 0:
                scorerPosition = random.choices(list(SCORER_CHANCES.keys()), weights = list(SCORER_CHANCES.values()), k = 1)[0]
                players = [player for player in lineup.values() if player.position == scorerPosition]

            player = random.choices(players, k = 1)[0]
            event["player"] = player

            assisterPosition = random.choices(list(ASSISTER_CHANCES.keys()), weights = list(ASSISTER_CHANCES.values()), k = 1)[0]
            players = [player for player in lineup.values() if player.position == assisterPosition]

            while len(players) == 0:
                assisterPosition = random.choices(list(ASSISTER_CHANCES.keys()), weights = list(ASSISTER_CHANCES.values()), k = 1)[0]
                players = [player for player in lineup.values() if player.position == assisterPosition]

            player = random.choices(players, k = 1)[0]

            if assisterPosition == scorerPosition and len([player for player in lineup.values() if player.position == assisterPosition]) == 1:
                available_positions = [pos for pos in ASSISTER_CHANCES.keys() if pos != assisterPosition]
                assisterPosition = random.choices(available_positions, weights = [ASSISTER_CHANCES[pos] for pos in available_positions], k = 1)[0]

            while player == event["player"]:
                player = random.choices([player for player in lineup.values() if player.position == assisterPosition], k = 1)[0]

            event["assister"] = player

        elif event["type"] == "penalty_goal" or event["type"] == "penalty_miss":
            penaltyPosition = random.choices(list(PENALTY_TAKER_CHANCES.keys()), weights = list(PENALTY_TAKER_CHANCES.values()), k = 1)[0]
            players = [player for player in lineup.values() if player.position == penaltyPosition]

            while len(players) == 0:
                penaltyPosition = random.choices(list(PENALTY_TAKER_CHANCES.keys()), weights = list(PENALTY_TAKER_CHANCES.values()), k = 1)[0]
                players = [player for player in lineup.values() if player.position == penaltyPosition]

            player = random.choices(players, k = 1)[0]
            event["player"] = player

        elif event["type"] == "own_goal":
            ownGoalPosition = random.choices(list(OWN_GOAL_CHANCES.keys()), weights=list(OWN_GOAL_CHANCES.values()), k=1)[0]
            oppositionLineup = self.homeCurrentLineup if lineup == self.awayCurrentLineup else self.awayCurrentLineup
            players_in_position = [player for player in oppositionLineup.values() if player.position == ownGoalPosition]

            if not players_in_position:
                player = random.choice(list(oppositionLineup.values()))
            else:
                player = random.choice(players_in_position)

            event["player"] = player

        elif event["type"] == "yellow_card":
            player = random.choices(list(lineup.values()), k = 1)[0]
            event["player"] = player

            for _, processedEvent in processedEvents.items():
                if processedEvent["type"] == "yellow_card" and processedEvent["player"] == player:
                    event["type"] = "red_card"
                    playerPosition = list(lineup.keys())[list(lineup.values()).index(player)]
                    lineup.pop(playerPosition)
                    finalLineup[playerPosition] = player

                    if teamMatch:
                        if home:
                            teamMatch.homeLineupPitch.removePlayer(playerPosition)
                        else:
                            teamMatch.awayLineupPitch.removePlayer(playerPosition)

        elif event["type"] == "red_card":
            redCardPosition = random.choices(list(RED_CARD_CHANCES.keys()), weights = list(RED_CARD_CHANCES.values()), k = 1)[0]
            players = [player for player in lineup.values() if player.position == redCardPosition]

            while len(players) == 0:
                redCardPosition = random.choices(list(RED_CARD_CHANCES.keys()), weights = list(RED_CARD_CHANCES.values()), k = 1)[0]
                players = [player for player in lineup.values() if player.position == redCardPosition]
            
            player = random.choices(players, k = 1)[0]
            event["player"] = player

            playerPosition = list(lineup.keys())[list(lineup.values()).index(player)]
            lineup.pop(playerPosition)
            finalLineup[playerPosition] = player

            if teamMatch:
                if home:
                    teamMatch.homeLineupPitch.removePlayer(playerPosition)
                else:
                    teamMatch.awayLineupPitch.removePlayer(playerPosition)

            if playerPosition == "Goalkeeper" and not managing_team:

                subPossible = False
                if subsCount == MAX_SUBS:
                    for event_time, event_data in events.items():
                        if event_data["type"] == "substitution" and not event_data["injury"] and event_time not in processedEvents:
                            subPossible = True
                            events.pop(event_time)
                            break

                else:
                    subPossible = True

                if not subPossible:
                    return

                minute = time.split(":")[0]
                newTime = str(int(minute) + 1) + ":" + time.split(":")[1]
                self.checkSubsitutionTime(newTime, events)

                minute = time.split(":")[0]
                seconds = time.split(":")[1]
                eventTime = str(int(minute) + 1) + ":" + seconds

                extra = False
                if self.halfTime or self.fullTime:
                    extra = True

                events[eventTime] = {
                    "type": "substitution",
                    "player": None,
                    "player_off": None,
                    "player_on": None,
                    "injury": False,
                    "extra": extra
                }

                player_off = random.choices(list(lineup.values()), k = 1)[0]
                player_off = self.checkPlayerOff(player_off, processedEvents, time, lineup)

                playerPositionOff = list(lineup.keys())[list(lineup.values()).index(player_off)]
                lineup.pop(playerPositionOff)
                finalLineup[playerPositionOff] = player_off

                self.findSubstitute(events[eventTime], player_off, playerPosition, lineup, subs, home, teamMatch = teamMatch)

        elif event["type"] == "injury":
            injuredPlayer = random.choices(list(lineup.values()), k = 1)[0]
            event["player"] = injuredPlayer

            playerPosition = list(lineup.keys())[list(lineup.values()).index(injuredPlayer)]
            if not managing_team:
                lineup.pop(playerPosition)
                finalLineup[playerPosition] = injuredPlayer

            if teamMatch:
                if home:
                    teamMatch.homeLineupPitch.removePlayer(playerPosition)
                else:
                    teamMatch.awayLineupPitch.removePlayer(playerPosition)

            # find the substitution event for the injured player
            if not managing_team:
                currMinute = int(time.split(":")[0])
                sub_time = str(currMinute + 1) + ":30"
                for event_time, event_data in events.items():
                    if event_data["type"] == "substitution" and event_time == sub_time:
                        self.findSubstitute(event_data, injuredPlayer, playerPosition, lineup, subs, home, teamMatch = teamMatch)

        elif event["type"] == "substitution" and not event["injury"] and not managing_team:
            players = [player for player in lineup.values() if player.position != "goalkeeper"]
            player_off = random.choices(list(players), k = 1)[0]

            player_off = self.checkPlayerOff(player_off, processedEvents, time, lineup)
            playerPosition = list(lineup.keys())[list(lineup.values()).index(player_off)]
            lineup.pop(playerPosition)
            finalLineup[playerPosition] = player_off

            if teamMatch:
                if home:
                    teamMatch.homeLineupPitch.removePlayer(playerPosition)
                else:
                    teamMatch.awayLineupPitch.removePlayer(playerPosition)

            self.findSubstitute(event, player_off, playerPosition, lineup, subs, home, teamMatch = teamMatch)
        
        if teamMatch:
            return event

    def checkPlayerOff(self, player, processEvents, time, lineup, checked_players = None):
        if checked_players is None:
            checked_players = set()

        for event_time, event_data in processEvents.items():
            if event_data["type"] == "substitution" and event_data["player_on"] == player:
                eventMinute = int(event_time.split(":")[0])
                currMinute = int(time.split(":")[0])
                if eventMinute < currMinute - 30:
                    return player  # Found a valid player
                else:
                    checked_players.add(player)
                    available_players = [p for p in lineup.values() if p.position != "goalkeeper" and p not in checked_players]
                    if not available_players:
                        return None  # No more players to check
                    new_player = random.choices(available_players, k = 1)[0]
                    return self.checkPlayerOff(new_player, processEvents, time, lineup, checked_players)

        return player  # No substitution event found for the player

    def findSubstitute(self, event, player_off, playerPosition, lineup, subs, home, teamMatch = None):
        for player in subs:
            if POSITION_CODES[playerPosition] in player.specific_positions.split(","):
                self.addPlayerToLineup(event, player, player_off, playerPosition, subs, lineup, teamMatch, home)
                return

        ## if no player was found to have a good position, add a player with the same overall position (defender, midfielder, forward)
        for player in subs:
            if player.position == player_off.position:
                self.addPlayerToLineup(event, player, player_off, playerPosition, subs, lineup, teamMatch, home)
                return
            
        ## if no player was found to have the same overall position, add a random player
        player = random.choices(subs, k = 1)[0]
        self.addPlayerToLineup(event, player, player_off, playerPosition, subs, lineup, teamMatch, home)

    def addPlayerToLineup(self, event, playerOn, playerOff, playerPosition, subs, lineup, teamMatch, home, managing_team = False):
        event["player_off"] = playerOff
        event["player_on"] = playerOn
        subs.remove(playerOn) # remove the player on from the subs list

        if not managing_team:
            lineup[playerPosition] = playerOn # add the player on to the lineup

        if teamMatch:
            teamMatch.updateSubFrame(home, playerOn, playerOff)
            if not managing_team:
                if home:
                    teamMatch.homeLineupPitch.addPlayer(playerPosition, playerOn.last_name)
                else:
                    teamMatch.awayLineupPitch.addPlayer(playerPosition, playerOn.last_name)

    def getPlayerRatings(self, team, finalLineup, currentLineup, events):

        oppositionEvents = self.awayEvents if team == self.homeTeam else self.homeEvents
        oppositionGoals = self.score.getScore()[1] if team == self.homeTeam else self.score.getScore()[0]

        ratingsDict = {}

        if team == self.homeTeam:
            venue = "home"
        else:
            venue = "away"
        
        if self.winner == team:
            rating = 7.00
        elif self.winner == None:
            rating = 6.50
        else:
            rating = 6.00

        if oppositionGoals == 0:
            if team == self.homeTeam:
                self.homeCleanSheet = True
            else:
                self.awayCleanSheet = True

        for i, (position, player) in enumerate(finalLineup.items()):
            self.getRating(venue, rating, ratingsDict, events, player, position, oppositionEvents, oppositionGoals, i)

        for i, (position, player) in enumerate(currentLineup.items()):
            self.getRating(venue, rating, ratingsDict, events, player, position, oppositionEvents, oppositionGoals, i + len(finalLineup))

        if team == self.homeTeam:
            self.homeRatings = ratingsDict
        else:
            self.awayRatings = ratingsDict

    def getRating(self, venue, rating, ratingsDict, events, player, position, oppositionEvents, oppositionGoals, i):

        defender_positions = ["Right Back", "Left Back", "Center Back", "Center Back Right", "Center Back Left"]

        scorerFlag = False
        for _, event in events.items():
            if event["player"] == player:
                if event["type"] in EVENT_RATINGS:
                    rating += random.choice(EVENT_RATINGS[event["type"]])
                    if event["type"] in ["goal", "penalty_goal"]:
                        scorerFlag = True

            if "assister" in event and event["assister"] == player:
                rating += random.choice(ASSIST_RATINGS)
        
        if not scorerFlag:
            if position == "Goalkeeper" or position in defender_positions:
                if oppositionGoals <= 1:
                    rating += random.choice(DEFENDER_GOALS_1)
                elif oppositionGoals <= 3:
                    rating += random.choice(DEFENDER_GOALS_3)
                else:
                    rating -= random.choice(DEFENDER_GOALS_MORE)
            else:  # mids and fwds that didn't score
                rating += random.choice(NON_SCORER_RATINGS)

        for _, event in oppositionEvents.items():
            if event["type"] == "own_goal" and event["player"] == player: # own goal
                rating -= random.choice([1.46, 1.49, 1.52, 1.57, 1.60, 1.63, 1.69, 1.78])

        finalRating = round(rating + 0.5, 2) if self.ratingsBoost == venue else round(rating - 0.5, 2) if self.ratingsDecay == venue else round(rating, 2)
        ratingsDict[player] = min(finalRating, 10)

    def saveData(self, managing_team = None):

        self.returnWinner()

        for player in itertools.chain(self.homeCurrentLineup.values(), self.awayCurrentLineup.values(), self.homeFinalLineup.values(), self.awayFinalLineup.values(), self.homeCurrentSubs, self.awayCurrentSubs):
            if player.age < 18:
                data = Players.get_player_by_id(self.session, player.id)

                if not data:
                    Players.add_player_entry(self.session, player)

        PlayerBans.reduce_all_player_bans_for_team(self.session, self.homeTeam.id, self.match.league_id)
        PlayerBans.reduce_all_player_bans_for_team(self.session, self.awayTeam.id, self.match.league_id)

        homeData = {
            "points": 3 if self.winner == self.homeTeam else 1 if self.winner is None else 0,
            "won": 1 if self.winner == self.homeTeam else 0,
            "drawn": 1 if self.winner == None else 0,
            "lost": 1 if self.winner == self.awayTeam else 0,
            "goals_scored": self.score.getScore()[0],
            "goals_conceded": self.score.getScore()[1]
        }
        
        awayData = {
            "points": 3 if self.winner == self.awayTeam else 1 if self.winner is None else 0,
            "won": 1 if self.winner == self.awayTeam else 0,
            "drawn": 1 if self.winner == None else 0,
            "lost": 1 if self.winner == self.homeTeam else 0,
            "goals_scored": self.score.getScore()[1],
            "goals_conceded": self.score.getScore()[0]
        }

        self.getPlayerRatings(self.homeTeam, self.homeFinalLineup, self.homeCurrentLineup, self.homeProcessedEvents)
        self.getPlayerRatings(self.awayTeam, self.awayFinalLineup, self.awayCurrentLineup, self.awayProcessedEvents)

        self.session.close()

        def update_league_teams():
            ## ------------- League Teams changes --------------- ##
            LeagueTeams.update_team(self.session, 
                                    self.homeTeam.id, 
                                    homeData["points"],
                                    homeData["won"],
                                    homeData["drawn"],
                                    homeData["lost"],
                                    homeData["goals_scored"],
                                    homeData["goals_conceded"]
                                )
            
            LeagueTeams.update_team(self.session,
                                    self.awayTeam.id, 
                                    awayData["points"],
                                    awayData["won"],
                                    awayData["drawn"],
                                    awayData["lost"],
                                    awayData["goals_scored"],
                                    awayData["goals_conceded"]
                                    )
        def update_managers():
            ## ------------- Managers changes --------------- ##
            homeManager = Managers.get_manager_by_id(self.session, self.homeTeam.manager_id)
            awayManager = Managers.get_manager_by_id(self.session, self.awayTeam.manager_id)

            Managers.update_games(self.session, homeManager.id, homeData["won"], homeData["lost"])
            Managers.update_games(self.session, awayManager.id, awayData["won"], awayData["lost"])

        def update_match_events():
            ## ------------- Match Events changes --------------- ##
            for time, event in self.homeProcessedEvents.items():
                minute = int(time.split(":")[0]) + 1

                if event["extra"]:
                    if minute < 50:
                        extraTime = minute - 45
                        minute = f"45 + {extraTime}'"
                    else:
                        extraTime = minute - 90
                        minute = f"90 + {extraTime}'"
                else:
                    minute = str(minute)

                if event["type"] == "goal":
                    MatchEvents.add_event(self.session, self.match.id, "goal", minute, event["player"].id)
                    MatchEvents.add_event(self.session, self.match.id, "assist", minute, event["assister"].id)
                elif event["type"] == "penalty_miss":
                    MatchEvents.add_event(self.session, self.match.id, "penalty_miss", minute, event["player"].id)
                    MatchEvents.add_event(self.session, self.match.id, "penalty_saved", minute, self.awayCurrentLineup["Goalkeeper"].id)
                elif event["type"] == "substitution":
                    MatchEvents.add_event(self.session, self.match.id, "sub_off", minute, event["player_off"].id) 
                    MatchEvents.add_event(self.session, self.match.id, "sub_on", minute, event["player_on"].id)
                elif event["type"] == "injury" or event["type"] == "red_card":
                    MatchEvents.add_event(self.session, self.match.id, event["type"], minute, event["player"].id)
                    ban = get_player_ban(event["type"])
                    PlayerBans.add_player_ban(self.session, event["player"].id, self.match.league_id if event["type"] == "red_card" else None, ban, event["type"])

                    if managing_team == "home" and event["type"] == "injury":
                        Emails.add_email(self.session, "player_injury", None, event["player"].id, ban, self.match.league_id)
                    elif managing_team == "home" and event["type"] == "red_card":
                        Emails.add_email(self.session, "player_ban", None, event["player"].id, ban, self.match.league_id)

                elif event["type"] == "yellow_card":
                    MatchEvents.add_event(self.session, self.match.id, "yellow_card", minute, event["player"].id)
                    MatchEvents.check_yellow_card_ban(self.session, event["player"].id, self.match.league_id, 5)
                else:
                    MatchEvents.add_event(self.session, self.match.id, event["type"], minute, event["player"].id)

            for time, event in self.awayProcessedEvents.items():
                minute = int(time.split(":")[0]) + 1

                if event["extra"]:
                    if minute <= 50:
                        extraTime = minute - 45
                        minute = f"45 + {extraTime}'"
                    else:
                        extraTime = minute - 90
                        minute = f"90 + {extraTime}'"
                else:
                    minute = str(minute)

                if event["type"] == "goal":
                    MatchEvents.add_event(self.session, self.match.id, "goal", minute, event["player"].id)
                    MatchEvents.add_event(self.session, self.match.id, "assist", minute, event["assister"].id)
                elif event["type"] == "penalty_miss":
                    MatchEvents.add_event(self.session, self.match.id, "penalty_miss", minute, event["player"].id)
                    MatchEvents.add_event(self.session, self.match.id, "penalty_saved", minute, self.homeCurrentLineup["Goalkeeper"].id)
                elif event["type"] == "substitution":
                    MatchEvents.add_event(self.session, self.match.id, "sub_off", minute, event["player_off"].id) 
                    MatchEvents.add_event(self.session, self.match.id, "sub_on", minute, event["player_on"].id)
                elif event["type"] == "injury" or event["type"] == "red_card":
                    MatchEvents.add_event(self.session, self.match.id, event["type"], minute, event["player"].id)
                    ban = get_player_ban(event["type"])
                    PlayerBans.add_player_ban(self.session, event["player"].id, self.match.league_id if event["type"] == "red_card" else None, ban, event["type"])

                    if managing_team == "away" and event["type"] == "injury":
                        Emails.add_email(self.session, "player_injury", None, event["player"].id, ban, self.match.league_id)
                    elif managing_team == "away" and event["type"] == "red_card":
                        Emails.add_email(self.session, "player_ban", None, event["player"].id, ban, self.match.league_id)

                elif event["type"] == "yellow_card":
                    MatchEvents.add_event(self.session, self.match.id, "yellow_card", minute, event["player"].id)
                    MatchEvents.check_yellow_card_ban(self.session, event["player"].id, self.match.league_id, 5)
                else:
                    MatchEvents.add_event(self.session, self.match.id, event["type"], minute, event["player"].id)

            if self.homeCleanSheet:
                MatchEvents.add_event(self.session, self.match.id, "clean_sheet", "90", self.homeCurrentLineup["Goalkeeper"].id)
            
            if self.awayCleanSheet:
                MatchEvents.add_event(self.session, self.match.id, "clean_sheet", "90", self.awayCurrentLineup["Goalkeeper"].id)

        def update_lineups():
            ## ------------- Matches changes --------------- ##
            Matches.update_score(self.session, self.match.id, self.score.getScore()[0], self.score.getScore()[1])

            ## ------------- Lineup changes --------------- ##
            for position, player in self.homeFinalLineup.items():
                TeamLineup.add_lineup_single(self.session, self.match.id, player.id, position, self.homeRatings[player])
                
                if not self.getGameTime(player, self.homeProcessedEvents):
                    # Player hasnt played more than 20 mins or at all -> decrease morale based on player role
                    moraleChange = get_morale_decrease_role(player)
                else:
                    # Change morale based on game outcome
                    moraleChange = get_morale_change("win" if self.winner == self.homeTeam else "draw" if self.winner == None else "loss", self.homeRatings[player], self.goalDiffHome)
                
                Players.update_morale(self.session, player.id, moraleChange)

            for position, player in self.homeCurrentLineup.items():
                TeamLineup.add_lineup_single(self.session, self.match.id, player.id, position, self.homeRatings[player])
                
                if not self.getGameTime(player, self.homeProcessedEvents):
                    moraleChange = get_morale_decrease_role(player)
                else:
                    moraleChange = get_morale_change("win" if self.winner == self.homeTeam else "draw" if self.winner == None else "loss", self.homeRatings[player], self.goalDiffHome)

                Players.update_morale(self.session, player.id, moraleChange)
            
            for position, player in self.awayFinalLineup.items():
                TeamLineup.add_lineup_single(self.session, self.match.id, player.id, position, self.awayRatings[player])
                
                if not self.getGameTime(player, self.awayProcessedEvents):
                    moraleChange = get_morale_decrease_role(player)
                else:
                    moraleChange = get_morale_change("win" if self.winner == self.awayTeam else "draw" if self.winner == None else "loss", self.awayRatings[player], self.goalDiffAway)

                Players.update_morale(self.session, player.id, moraleChange)
                
            for position, player in self.awayCurrentLineup.items():
                TeamLineup.add_lineup_single(self.session, self.match.id, player.id, position, self.awayRatings[player])
                
                if not self.getGameTime(player, self.awayProcessedEvents):
                    moraleChange = get_morale_decrease_role(player)
                else:
                    moraleChange = get_morale_change("win" if self.winner == self.awayTeam else "draw" if self.winner == None else "loss", self.awayRatings[player], self.goalDiffAway)

                Players.update_morale(self.session, player.id, moraleChange)

            homePlayers = Players.get_all_players_by_team(self.session, self.homeTeam.id, youths = False)
            awayPlayers = Players.get_all_players_by_team(self.session, self.awayTeam.id, youths = False)

            for player in homePlayers:
                if player not in self.homeCurrentLineup and player not in self.homeFinalLineup:
                    Players.update_morale(self.session, player.id, get_morale_decrease_role(player))

            for player in awayPlayers:
                if player not in self.awayCurrentLineup and player not in self.awayFinalLineup:
                        Players.update_morale(self.session, player.id, get_morale_decrease_role(player))

    def getGameTime(self, player, events):
        sub_off_time = None
        sub_on_time = None

        for time, event in events.items():
            if event["type"] == "sub_on" and event["player"] == player:
                sub_on_time = time

            if event["type"] == "sub_off" and event["player"] == player:
                sub_off_time = time

        if sub_on_time and sub_off_time:
            gameTime = int(sub_off_time) - int(sub_on_time)
            return True if gameTime >= 20 else False
        elif sub_on_time:
            gameTime = 90 - int(sub_on_time)
            return True if gameTime >= 20 else False
        elif sub_off_time:
            return True if sub_off_time >= 20 else False
        else:
            # Player hasnt played
            return False

    def returnWinner(self):
        finalScore = self.score.getScore()
        self.goalDiffHome = finalScore[0] - finalScore[1]
        self.goalDiffAway = finalScore[1] - finalScore[0]
        if finalScore[0] > finalScore[1]:
            self.winner = self.homeTeam
        elif finalScore[0] < finalScore[1]:
            self.winner = self.awayTeam
        else:
            self.winner = None

    def getEvents(self):
        return self.homeEvents, self.awayEvents
    
    def getScore(self):
        return self.score.getScore()

    def setRatingsBoost(self, team):
        self.ratingsBoost = team
    
    def setRatingsDecay(self, team):
        self.ratingsDecay = team