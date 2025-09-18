import threading
import logging
from settings import *
from data.database import *
from data.gamesDatabase import *
import concurrent.futures
from utils.util_functions import *

class Match():
    def __init__(self, match, auto = False, teamMatch = False):

        self.match = match
        self.auto = auto

        self.homeTeam = Teams.get_team_by_id(self.match.home_id)
        self.awayTeam = Teams.get_team_by_id(self.match.away_id)
        self.league = LeagueTeams.get_league_by_team(self.homeTeam.id)
        self.referee = Referees.get_referee_by_id(self.match.referee_id)

        self.homeFinalLineup = []
        self.awayFinalLineup = []
        self.homeCurrentLineup = None
        self.awayCurrentLineup = None

        self.homeCurrentSubs = None
        self.awayCurrentSubs = None
        self.homeSubs = 0
        self.awaySubs = 0

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

        self.homeFitness = {}
        self.awayFitness = {}
        # Initialize per-player stats (dicts) and match-level stats (ints)
        self.homeStats = {stat: {} for stat in PLAYER_STATS}
        for stat in MATCH_STATS:
            if stat not in PLAYER_STATS:
                self.homeStats[stat] = 0

        self.awayStats = {stat: {} for stat in PLAYER_STATS}
        for stat in MATCH_STATS:
            if stat not in PLAYER_STATS:
                self.awayStats[stat] = 0

        self.score = [0, 0]

        if self.auto:
            self.seconds, self.minutes = 0, 0

        if not teamMatch:
            self.createTeamLineup(self.homeTeam.id, True)
            self.createTeamLineup(self.awayTeam.id, False)

    def createTeamLineup(self, teamID, home):
        opponentID = self.match.away_id if home else self.match.home_id
        lineup = getProposedLineup(teamID, opponentID, self.league.league_id, Game.get_game_date(Managers.get_all_user_managers()[0].id))
        substitutes = getSubstitutes(teamID, lineup, self.league.league_id)
        
        if home:
            self.homeCurrentLineup = lineup
            self.homeCurrentSubs = substitutes
            self.homeStartLineup = lineup.copy()
            self.homeFitness = {playerID: Players.get_player_by_id(playerID).fitness for playerID in list(lineup.values()) + substitutes}
        else:
            self.awayCurrentLineup = lineup
            self.awayCurrentSubs = substitutes
            self.awayStartLineup = lineup.copy()
            self.awayFitness = {playerID: Players.get_player_by_id(playerID).fitness for playerID in list(lineup.values()) + substitutes}

    def startGame(self):
        self.timerThread_running = True
        self.timerThread = threading.Thread(target = self.gameLoop)
        self.timerThread.daemon = True
        self.timerThread.start()

    def gameLoop(self):
        while self.timerThread_running:

            if self.seconds == 59:
                self.minutes += 1
                self.seconds = 0
            else:
                self.seconds += 1

            total_seconds = self.minutes * 60 + self.seconds
            if total_seconds % 90 == 0:
                for playerID, fitness in self.homeFitness.items():
                    if fitness > 0 and playerID in self.homeCurrentLineup.values():
                        self.homeFitness[playerID] = fitness - getFitnessDrop(Players.get_player_by_id(playerID), fitness)

                        if self.homeFitness[playerID] < 0:
                            self.homeFitness[playerID] = 0

                for playerID, fitness in self.awayFitness.items():
                    if fitness > 0 and playerID in self.awayCurrentLineup.values():
                        self.awayFitness[playerID] = fitness - getFitnessDrop(Players.get_player_by_id(playerID), fitness)

                        if self.awayFitness[playerID] < 0:
                            self.awayFitness[playerID] = 0

            # ----------- half time ------------
            if self.minutes == 45 and self.seconds == 0:

                self.halfTime = True

                eventsExtraTime, firstHalfEvents, maxMinute = 0, 0, 0
                combined_events = {**self.homeEvents, **self.awayEvents}
                for event_time, event_details in list(combined_events.items()):
                    minute = int(event_time.split(":")[0])
                    if event_details["extra"] and minute < 90: # first half extra time events
                        eventsExtraTime += 1
                        
                        if minute + 1 > maxMinute:
                            maxMinute = minute + 1

                    elif minute < 45 and event_details["type"] != "substitution":
                        firstHalfEvents += 1

                if maxMinute - 45 < firstHalfEvents:
                    extraTime = min(firstHalfEvents, 5)
                else:
                    extraTime = maxMinute - 45

                self.extraTimeHalf = extraTime

            if self.halfTime and self.minutes == 45 + self.extraTimeHalf and self.seconds == 0:
                self.halfTime = False
                self.minutes = 45
                self.seconds = 0

            # ----------- full time ------------
            if self.minutes == 90 and self.seconds == 0:

                self.fullTime = True

                eventsExtraTime, secondHalfEvents, maxMinute = 0, 0, 0
                combined_events = {**self.homeEvents, **self.awayEvents}
                for event_time, event_details in list(combined_events.items()):
                    minute = int(event_time.split(":")[0])
                    if event_details["extra"] and minute > 90: # second half extra time events
                        eventsExtraTime += 1
                        
                        if minute + 1 > maxMinute:
                            maxMinute = minute + 1

                    elif minute > 45 and not event_details["extra"] and event_details["type"] != "substitution":
                        secondHalfEvents += 1

                if maxMinute - 90 < secondHalfEvents:
                    extraTime = min(secondHalfEvents, 5)
                else:
                    extraTime = maxMinute - 90

                self.extraTimeFull = extraTime

            if self.fullTime and self.minutes == 90 + self.extraTimeFull and self.seconds == 0:
                self.fullTime = False
                self.saveData()
            else:
                if total_seconds % TICK == 0:
                    self.generateEvents("home")
                    self.generateEvents("away")

                # ----------- home events ------------
                for event_time, event_details in list(self.homeEvents.items()):
                    if event_time == str(self.minutes) + ":" + str(self.seconds) and event_time not in self.homeProcessedEvents:
                        if event_details["extra"]:
                            if self.halfTime or self.fullTime:
                                self.getEventPlayer(event_details, True, event_time)
                                self.homeProcessedEvents[event_time] = event_details
                        else:
                            if not (self.halfTime or self.fullTime):
                                self.getEventPlayer(event_details, True, event_time)
                                self.homeProcessedEvents[event_time] = event_details

                # ----------- away events ------------
                for event_time, event_details in list(self.awayEvents.items()):
                    if event_time == str(self.minutes) + ":" + str(self.seconds) and event_time not in self.awayProcessedEvents:
                        if event_details["extra"]:
                            if self.halfTime or self.fullTime:
                                self.getEventPlayer(event_details, False, event_time)
                                self.awayProcessedEvents[event_time] = event_details
                        else:
                            if not (self.halfTime or self.fullTime):
                                self.getEventPlayer(event_details, False, event_time)
                                self.awayProcessedEvents[event_time] = event_details

    def generateEvents(self, side):
        eventsToAdd = []
        statsToAdd = []

        lineup = self.homeCurrentLineup if side == "home" else self.awayCurrentLineup
        oppLineup = self.awayCurrentLineup if side == "home" else self.homeCurrentLineup
        matchEvents = self.homeEvents if side == "home" else self.awayEvents
        fitness = self.homeFitness if side == "home" else self.awayFitness
        subsCount = self.homeSubs if side == "home" else self.awaySubs
        stats = self.homeStats if side == "home" else self.awayStats
        oppStats = self.awayStats if side == "home" else self.homeStats
        subs = self.homeCurrentSubs if side == "home" else self.awayCurrentSubs
        events = self.homeProcessedEvents if side == "home" else self.awayProcessedEvents

        sharpness = [Players.get_player_by_id(playerID).sharpness for playerID in lineup.values()]
        avgSharpnessWthKeeper = sum(sharpness) / len(sharpness)

        if "Goalkeeper" in lineup:
            avgSharpness = (sum(sharpness) - Players.get_player_by_id(lineup["Goalkeeper"]).sharpness) / (len(sharpness) - 1)
        else:
            avgSharpness = avgSharpnessWthKeeper

        avgFitness = sum(fitness[playerID] for playerID in lineup.values()) / len(lineup)
        
        morale = [Players.get_player_by_id(playerID).morale for pos, playerID in lineup.items() if pos != "Goalkeeper"]
        avgMorale = sum(morale) / len(morale)

        oppKeeper = Players.get_player_by_id(oppLineup["Goalkeeper"]) if "Goalkeeper" in oppLineup else None

        attackingPlayers = [playerID for pos, playerID in lineup.items() if pos in ATTACKING_POSITIONS]
        defendingPlayers = [playerID for pos, playerID in oppLineup.items() if pos in DEFENSIVE_POSITIONS]

        attackingLevel = teamStrength(attackingPlayers, role = "attack")
        defendingLevel = teamStrength(defendingPlayers, role = "defend")

        # ------------------ GOALS ------------------
        event = goalChances(attackingLevel, defendingLevel, avgSharpness, avgMorale, oppKeeper)

        if event == "goal":

            goalType = random.choices(list(GOAL_TYPE_CHANCES.keys()), weights = list(GOAL_TYPE_CHANCES.values()), k = 1)[0]

            if goalType == "penalty":
                if random.random() < PENALTY_SCORE_CHANCE or "Goalkeeper" not in oppLineup:
                    goalType = "penalty_goal"
                    self.appendScore(1, True if side == "home" else False)
                else:
                    goalType = "penalty_miss"
                    statsToAdd.append("Saved")
            elif event == "own_goal":
                self.appendScore(1, False if side == "home" else True)
            else:
                self.appendScore(1, True if side == "home" else False)

            eventsToAdd.append(goalType)

            if random.random() < GOAL_BIG_CHANCE:
                statsToAdd.append("Big chances created")
        elif event != "nothing":
            statsToAdd.append(event)

        # ------------------ FOULS ------------------
        event = foulChances(avgSharpnessWthKeeper, self.referee.severity)

        if event in ["yellow_card", "red_card"]:
            eventsToAdd.append(event)
        elif event == "Fouls":
            statsToAdd.append(event)
        else:
            # If nothing, get tackles and interceptions
            tacklesInterceptions = random.choices(population = list(DEFENSIVE_ACTIONS_CHANCES.keys()), weights = list(DEFENSIVE_ACTIONS_CHANCES.values()), k = 1)[0]

            if tacklesInterceptions != "nothing":
                statsToAdd.append(tacklesInterceptions)

        # ------------------ INJURIES ------------------
        event = injuryChances(avgFitness)

        if event == "injury":
            eventsToAdd.append(event)

        # ------------------ SUBSTITUTIONS ------------------
        subsChosen = substitutionChances(lineup, subsCount, subs.copy(), events, self.minutes, fitness)

        for _ in range(len(subsChosen)):
            eventsToAdd.append("substitution")

        # ------------------ TIMES and ADDING ------------------
        currMin, currSec = self.minutes, self.seconds
        extraTime = self.halfTime or self.fullTime
        
        currTotalSecs = currMin * 60 + currSec
        futureTotalSecs = currTotalSecs + 30

        if extraTime:
            maxMinute = self.extraTimeHalf if self.halfTime else self.extraTimeFull
            finalMinute = 45 if self.halfTime else 90
            maxTotalSecs = (finalMinute + maxMinute) * 60
        else:
            maxMinute = 45 if self.halfTime else 90
            maxTotalSecs = maxMinute * 60

        endTotalSecs = min(futureTotalSecs, maxTotalSecs)

        subsChosenCount = 0
        for event in eventsToAdd:
            try:
                eventTotalSecs = random.randint(currTotalSecs + 10, endTotalSecs)
            except ValueError:
                break

            # Convert back to mm:ss
            eventMin = eventTotalSecs // 60
            eventSec = eventTotalSecs % 60
            eventTime = f"{eventMin}:{eventSec:02d}"

            if event == "substitution":
                matchEvents[eventTime] = {"type": "substitution", "extra": extraTime, "player_off": subsChosen[subsChosenCount][0], "player_on": subsChosen[subsChosenCount][2], "old_position": subsChosen[subsChosenCount][1], "new_position": subsChosen[subsChosenCount][3]}
                subsChosenCount += 1
            elif event == "penalty_miss":
                matchEvents[eventTime] = {"type": event, "extra": extraTime, "keeper": oppLineup["Goalkeeper"] if "Goalkeeper" in oppLineup else None}
            else:
                matchEvents[eventTime] = {"type": event, "extra": extraTime}

        for stat in statsToAdd:

            statsDict = stats if stat != "Saves" else oppStats
            lineup = lineup if stat != "Saves" else oppLineup
            if stat in PLAYER_STATS:
                playerID = self.getStatPlayer(stat, lineup)

                if not playerID:
                    continue

                if not playerID in stats[stat]:
                    statsDict[stat][playerID] = 0

                statsDict[stat][playerID] += 1

                match stat:
                    case "Shots":

                        if playerID not in statsDict["Shots"]:
                            statsDict["Shots"][playerID] = 0
                        
                        statsDict["Shots"][playerID] += 1

                        shotDirection = random.choices(population = list(SHOT_DIRECTION_CHANCES.keys()), weights = list(SHOT_DIRECTION_CHANCES.values()), k = 1)[0]
                        if not playerID in statsDict[shotDirection]:
                            statsDict[shotDirection][playerID] = 0

                        statsDict[shotDirection][playerID] += 1

                        shotOutcome = random.choices(population = list(SHOT_CHANCES.keys()), weights = list(SHOT_CHANCES.values()), k = 1)[0]
                        if shotOutcome != "wide":
                            statsDict[shotOutcome] += 1

                        if random.random() < SHOT_BIG_CHANCE:
                            if not playerID in statsDict["Big chances missed"]:
                                statsDict["Big chances missed"][playerID] = 0

                            statsDict["Big chances missed"][playerID] += 1

                            playerID = self.getStatPlayer("Big chances created", lineup)
                            if not playerID in statsDict["Big chances created"]:
                                statsDict["Big chances created"][playerID] = 0

                            statsDict["Big chances created"][playerID] += 1
                    case "Shots on target":
                        if playerID not in statsDict["Shots"]:
                            statsDict["Shots"][playerID] = 0
                        
                        statsDict["Shots"][playerID] += 1

                        playerID = self.getStatPlayer("Saves", oppLineup)
                        if playerID not in statsDict["Saves"]:
                            statsDict["Saves"][playerID] = 0
                        
                        statsDict["Saves"][playerID] += 1

                        shotDirection = random.choices(population = list(SHOT_DIRECTION_CHANCES.keys()), weights = list(SHOT_DIRECTION_CHANCES.values()), k = 1)[0]
                        if not playerID in statsDict[shotDirection]:
                            statsDict[shotDirection][playerID] = 0
                        
                        statsDict[shotDirection][playerID] += 1

                        if random.random() < SHOT_BIG_CHANCE:
                            if not playerID in statsDict["Big chances missed"]:
                                statsDict["Big chances missed"][playerID] = 0

                            statsDict["Big chances missed"][playerID] += 1

                            playerID = self.getStatPlayer("Big chances created", lineup)
                            if not playerID in statsDict["Big chances created"]:
                                statsDict["Big chances created"][playerID] = 0

                            statsDict["Big chances created"][playerID] += 1
            else:
                statsDict[stat] += 1

    def join(self):
        if self.timerThread:
            self.timerThread.join()

    def getEventPlayer(self, event, home, time, teamMatch = None, managing_team = False):

        lineup = self.homeCurrentLineup if home else self.awayCurrentLineup
        subs = self.homeCurrentSubs if home else self.awayCurrentSubs
        finalLineup = self.homeFinalLineup if home else self.awayFinalLineup
        processedEvents = self.homeProcessedEvents if home else self.awayProcessedEvents
        events = self.homeEvents if home else self.awayEvents
        subsCount = self.homeSubs if home else self.awaySubs
        fitness = self.homeFitness if home else self.awayFitness
        stats = self.homeStats if home else self.awayStats
        oppStats = self.awayStats if home else self.homeStats

        # Fetch all players in the lineup with a single query
        player_ids = list(lineup.values())
        players = Players.get_players_by_ids(player_ids)
        players_dict = {player.id: player for player in players}

        if event["type"] == "goal":
            ## scorer
            scorerPosition = random.choices(list(SCORER_CHANCES.keys()), weights = list(SCORER_CHANCES.values()), k = 1)[0]
            players = [player.id for player in players_dict.values() if player.position == scorerPosition]

            while len(players) == 0:
                scorerPosition = random.choices(list(SCORER_CHANCES.keys()), weights = list(SCORER_CHANCES.values()), k = 1)[0]
                players = [player.id for player in players_dict.values() if player.position == scorerPosition]

            weights = [effective_ability(players_dict[playerID]) for playerID in players]
            if sum(weights) == 0:
                weights = [1] * len(players)

            playerID = random.choices(players, weights = weights, k = 1)[0]
            event["player"] = playerID

            # Add the stats for the scorer
            if playerID not in stats["Shots on target"]:
                stats["Shots on target"][playerID] = 0
            
            stats["Shots on target"][playerID] += 1
        
            if playerID not in stats["Shots"]:
                stats["Shots"][playerID] = 0
            
            stats["Shots"][playerID] += 1

            shotDirection = random.choices(population = list(SHOT_DIRECTION_CHANCES.keys()), weights = list(SHOT_DIRECTION_CHANCES.values()), k = 1)[0]
            if playerID not in stats[shotDirection]:
                stats[shotDirection][playerID] = 0
            
            stats[shotDirection][playerID] += 1

            ## assister
            assisterPosition = random.choices(list(ASSISTER_CHANCES.keys()), weights = list(ASSISTER_CHANCES.values()), k = 1)[0]
            players = [player.id for player in players_dict.values() if player.position == assisterPosition]

            while len(players) == 0:
                assisterPosition = random.choices(list(ASSISTER_CHANCES.keys()), weights = list(ASSISTER_CHANCES.values()), k = 1)[0]
                players = [player.id for player in players_dict.values() if player.position == assisterPosition]
            
            weights = [effective_ability(players_dict[playerID]) for playerID in players]
            if sum(weights) == 0:
                weights = [1] * len(players)

            playerID = random.choices(players, weights = weights, k = 1)[0]

            # make sure player doesnt assist themselves
            if assisterPosition == scorerPosition and len(players) == 1: 
                available_positions = [pos for pos in ASSISTER_CHANCES.keys() if pos != assisterPosition]
                assisterPosition = random.choices(available_positions, weights = [ASSISTER_CHANCES[pos] for pos in available_positions], k = 1)[0]
            while playerID == event["player"]:
                players = [player.id for player in players_dict.values() if player.position == assisterPosition]

                weights = [effective_ability(players_dict[playerID]) for playerID in players]
                if sum(weights) == 0:
                    weights = [1] * len(players)

                playerID = random.choices(players, weights = weights, k = 1)[0]

            event["assister"] = playerID

        elif event["type"] == "penalty_goal" or event["type"] == "penalty_miss":
            penaltyPosition = random.choices(list(PENALTY_TAKER_CHANCES.keys()), weights = list(PENALTY_TAKER_CHANCES.values()), k = 1)[0]
            players = [player.id for player in players_dict.values() if player.position == penaltyPosition]

            if playerID not in stats["Shots on target"]:
                stats["Shots on target"][playerID] = 0
            
            stats["Shots on target"][playerID] += 1
        
            if playerID not in stats["Shots"]:
                stats["Shots"][playerID] = 0

            stats["Shots"][playerID] += 1
        
            if event["type"] == "penalty_miss" and event["keeper"] not in oppStats["Saves"]:
                oppStats["Saves"][event["keeper"]] = 0
            
            oppStats["Saves"][event["keeper"]] += 1

            while len(players) == 0:
                penaltyPosition = random.choices(list(PENALTY_TAKER_CHANCES.keys()), weights = list(PENALTY_TAKER_CHANCES.values()), k = 1)[0]
                players = [player.id for player in players_dict.values() if player.position == penaltyPosition]

            playerID = random.choices(players, k = 1)[0]
            event["player"] = playerID

        elif event["type"] == "own_goal":
            ownGoalPosition = random.choices(list(OWN_GOAL_CHANCES.keys()), weights = list(OWN_GOAL_CHANCES.values()), k = 1)[0]
            oppositionLineup = self.homeCurrentLineup if lineup == self.awayCurrentLineup else self.awayCurrentLineup
            
            players = Players.get_players_by_ids(list(oppositionLineup.values()))
            players_in_position = [player for player in players if player.position == ownGoalPosition]

            if not players_in_position:
                players_in_position = players
                
            weights = [ownGoalFoulWeight(p) for p in players_in_position]
            playerID = random.choices(players_in_position, weights = weights, k = 1)[0].id

            event["player"] = playerID

        elif event["type"] == "yellow_card":
            weights = [ownGoalFoulWeight(player) for player in players_dict.values()]
            playerID = random.choices(list(players_dict.values()), weights = weights, k = 1)[0].id
            event["player"] = playerID
            stats["Yellow cards"] += 1

            if random.random() < CARD_FOUL_CHANCE:
                if playerID not in stats["Fouls"]:
                    stats["Fouls"][playerID] = 0
                
                stats["Fouls"][playerID] += 1

            for _, processedEvent in processedEvents.items():
                if processedEvent["type"] == "yellow_card" and processedEvent["player"] == playerID:
                    event["type"] = "red_card"
                    stats["Yellow cards"] -= 1
                    stats["Red cards"] += 1

                    playerPosition = list(lineup.keys())[list(lineup.values()).index(playerID)]
                    lineup.pop(playerPosition)
                    finalLineup.append((playerPosition, playerID))

                    event["position"] = playerPosition

                    if teamMatch:
                        self.updateTeamMatch(playerID, playerPosition, teamMatch, home)
                    
                    if playerPosition == "Goalkeeper" and not managing_team:
                        self.keeperSub(subsCount, lineup, players_dict, processedEvents, time, events, teamMatch, subs, home)

        elif event["type"] == "red_card":
            
            redCardPosition = random.choices(list(RED_CARD_CHANCES.keys()), weights = list(RED_CARD_CHANCES.values()), k = 1)[0]
            players = [player for player in players_dict.values() if player.position == redCardPosition]

            while len(players) == 0:
                redCardPosition = random.choices(list(RED_CARD_CHANCES.keys()), weights = list(RED_CARD_CHANCES.values()), k = 1)[0]
                players = [player for player in players_dict.values() if player.position == redCardPosition]

            weights = [ownGoalFoulWeight(player) for player in players]

            playerID = random.choices(players, weights = weights, k = 1)[0].id
            event["player"] = playerID
            stats["Red cards"] += 1

            if random.random() < CARD_FOUL_CHANCE:
                if playerID not in stats["Fouls"]:
                    stats["Fouls"][playerID] = 0
                
                stats["Fouls"][playerID] += 1

            playerPosition = list(lineup.keys())[list(lineup.values()).index(playerID)]
            lineup.pop(playerPosition)
            finalLineup.append((playerPosition, playerID))
            event["position"] = playerPosition

            if teamMatch:
                self.updateTeamMatch(playerID, playerPosition, teamMatch, home)

            if playerPosition == "Goalkeeper" and not managing_team:
                self.keeperSub(subsCount, lineup, players_dict, processedEvents, time, events, teamMatch, subs, home)

        elif event["type"] == "injury":

            weights = [fitnessWeight(player, fitness[player.id]) for player in players_dict.values()]

            injuredPlayerID = random.choices(list(players_dict.values()), weights = weights, k = 1)[0].id
            event["player"] = injuredPlayerID

            playerPosition = list(lineup.keys())[list(lineup.values()).index(injuredPlayerID)]

            if not managing_team and subsCount < MAX_SUBS:
                self.createSubEvent(lineup, players_dict, processedEvents, time, events, injuredPlayerID, subs, playerPos = playerPosition)

            elif not managing_team and subsCount == MAX_SUBS:
                lineup.pop(playerPosition)
                finalLineup.append((playerPosition, injuredPlayerID))

                if teamMatch:
                    self.updateTeamMatch(injuredPlayerID, playerPosition, teamMatch, home)
                
                if playerPosition == "Goalkeeper":
                    self.keeperSub(subsCount, lineup, players_dict, processedEvents, time, events, teamMatch, subs, home)

        elif event["type"] == "substitution" and not managing_team:

            playerOffID = event["player_off"]
            playerOnID = event["player_on"]
            oldPosition = event["old_position"]
            newPosition = event["new_position"]

            lineup.pop(oldPosition)
            finalLineup.append((oldPosition, playerOffID))

            if home:
                self.homeSubs += 1
            else:
                self.awaySubs += 1

            if teamMatch:
                self.updateTeamMatch(playerOffID, oldPosition, teamMatch, home)

            self.addPlayerToLineup(playerOnID, playerOffID, newPosition, oldPosition, subs, lineup, teamMatch, home)
        
        if teamMatch:
            return event

    def getStatPlayer(self, stat, lineup):
        match stat:
            case "Saves":
                return lineup["Goalkeeper"] if "Goalkeeper" in lineup else None
            case "Shots" | "Shots on target" | "Shots in the box" | "Shots outside the box":
                return self.choosePlayerFromDict(lineup, SCORER_CHANCES)
            case "Fouls":
                weights = [ownGoalFoulWeight(Players.get_player_by_id(playerID)) for playerID in lineup.values()]
                return random.choices(list(lineup.values()), weights = weights, k = 1)[0]
            case "Tackles" | "Interceptions":
                return self.choosePlayerFromDict(lineup, DEFENSIVE_ACTION_POSITIONS)
            case "Big chances created" | "Big chances missed":
                return self.choosePlayerFromDict(lineup, BIG_CHANCES_POSITIONS)

    def choosePlayerFromDict(self, lineup, dict_):
        playerPosition = random.choices(list(dict_.keys()), weights = list(dict_.values()), k = 1)[0]
        players = [playerID for playerID in lineup.values() if Players.get_player_by_id(playerID).position == playerPosition]

        while len(players) == 0:
            playerPosition = random.choices(list(dict_.keys()), weights = list(dict_.values()), k = 1)[0]
            players = [playerID for playerID in lineup.values() if Players.get_player_by_id(playerID).position == playerPosition]

        weights = [effective_ability(Players.get_player_by_id(playerID)) for playerID in players]
        if sum(weights) == 0:
            weights = [1] * len(players)

        return random.choices(players, weights = weights, k = 1)[0]

    def getStatNum(self, stat):
        return sum(playerValue for playerValue in stat.values())

    def updateTeamMatch(self, playerOffID, oldPosition, teamMatch, home):
        playerData = Players.get_player_by_id(playerOffID)
        if home:
            teamMatch.homeLineupPitch.removePlayer(oldPosition, playerData.last_name)
            frame = [f for f in teamMatch.homePlayersFrame.winfo_children() if f.playerID == playerOffID]

            if len(frame) == 0:
                frame = teamMatch.addPlayerFrame(teamMatch.homePlayersFrame, playerOffID)
            else:
                frame = frame[0]

            frame.removeFitness()
        else:
            teamMatch.awayLineupPitch.removePlayer(oldPosition, playerData.last_name)
            frame = [f for f in teamMatch.awayPlayersFrame.winfo_children() if f.playerID == playerOffID]

            if len(frame) == 0:
                frame = teamMatch.addPlayerFrame(teamMatch.awayPlayersFrame, playerOffID)
            else:
                frame = frame[0]

            frame.removeFitness()

    def keeperSub(self, subsCount, lineup, players_dict, processedEvents, time, events, teamMatch, subs, home):
        subPossible = subsCount < MAX_SUBS

        if not subPossible:
            players = [player.id for player in players_dict.values() if player.position == "forward"]

            if len(players) == 0:
                newKeeper = random.choices(list(lineup.values()), k = 1)[0]
            else:
                newKeeper = random.choices(list(players), k = 1)[0]

            newKeeperPosition = list(lineup.keys())[list(lineup.values()).index(newKeeper)]
            lineup.pop(newKeeperPosition)
            lineup["Goalkeeper"] = newKeeper

            if teamMatch:
                if home:
                    teamMatch.homeLineupPitch.movePlayer(newKeeperPosition, "Goalkeeper", Players.get_player_by_id(newKeeper).last_name)
                else:
                    teamMatch.awayLineupPitch.movePlayer(newKeeperPosition, "Goalkeeper", Players.get_player_by_id(newKeeper).last_name)
        else:
            self.createSubEvent(lineup, players_dict, processedEvents, time, events, None, subs, keeperSub = True)

    def createSubEvent(self, lineup, players_dict, processedEvents, time, events, playerOffID, subs, keeperSub = False, playerPos = None):
        # Create the substitution event
        minute = int(time.split(":")[0])
        seconds = int(time.split(":")[1])
        currTotalSecs = minute * 60 + seconds
        extraTime = self.halfTime or self.fullTime

        if extraTime:
            maxMinute = self.extraTimeHalf if self.halfTime else self.extraTimeFull
            maxTotalSecs = currTotalSecs + (maxMinute * 60)
        else:
            maxMinute = 45 if self.halfTime else 90
            maxTotalSecs = maxMinute * 60

        subTotalSecs = currTotalSecs + 10
        next_tick = ((currTotalSecs // TICK) + 1) * TICK

        if subTotalSecs > next_tick:
            subTotalSecs = next_tick + 10

        # Create the substitution event
        if subTotalSecs <= maxTotalSecs:
            subMin = subTotalSecs // 60
            subSec = subTotalSecs % 60
            sub_time = f"{subMin}:{subSec:02d}"
        elif (extraTime and self.halfTime) or maxTotalSecs == 45*60:
            sub_time = "45:10"

        if keeperSub:
            players = [player.id for player in players_dict.values() if player.position == "forward"]

            if len(players) == 0:
                playerOffID = random.choices(list(lineup.values()), k = 1)[0]
            else:
                playerOffID = random.choices(list(players), k = 1)[0]

            playerOffID = self.checkPlayerOff(playerOffID, processedEvents, time, lineup)
            playerPos = "Goalkeeper"

        subChoice = find_substitute(lineup, [(1, playerOffID, playerPos)], subs, 1)[0]
        playerOnID = subChoice[2]
        newPosition = subChoice[3]

        events[sub_time] = {
            "type": "substitution",
            "player": None,
            "player_off": playerOffID,
            "player_on": playerOnID,
            "old_position": list(lineup.keys())[list(lineup.values()).index(playerOffID)],
            "new_position": newPosition,
            "extra": extraTime,
        }

    def checkPlayerOff(self, playerID, processEvents, time, lineup, checked_players = None):
        if checked_players is None:
            checked_players = set()

        for event_time, event_data in processEvents.items():
            if event_data["type"] == "substitution" and event_data["player_on"] == playerID:
                eventMinute = int(event_time.split(":")[0])
                currMinute = int(time.split(":")[0])
                if eventMinute < currMinute - 30:
                    return playerID  # Found a valid player
                else:
                    checked_players.add(playerID)

                    players = Players.get_players_by_ids(list(lineup.values()))
                    players_dict = {player.id: player for player in players}

                    available_players = [player.id for player in players_dict.values() if player.position != "goalkeeper" and player.id not in checked_players]
                    if not available_players:
                        return random.choices(list(lineup.values()), k = 1)[0]  # No available players, return a random player
                    
                    new_player = random.choices(available_players, k = 1)[0]
                    return self.checkPlayerOff(new_player, processEvents, time, lineup, checked_players)

        return playerID  # No substitution event found for the player

    def addPlayerToLineup(self, playerOnID, playerOffID, playerPosition, posOff, subs, lineup, teamMatch, home, managing_event = None):

        # remove the player from the subs list
        for playerID in subs:
            if playerID == playerOnID:
                subs.remove(playerID)
                break

        if not managing_event:
            lineup[playerPosition] = playerOnID # add the player on to the lineup
        else:
            managing_event["player_on"] = playerOnID
            managing_event["new_position"] = playerPosition
            managing_event["player_off"] = playerOffID
            managing_event["old_position"] = posOff

        if teamMatch:
            teamMatch.updateSubFrame(home, playerOnID, playerOffID)
            playersFrame = teamMatch.homePlayersFrame if home else teamMatch.awayPlayersFrame
            frame = [f for f in playersFrame.winfo_children() if f.playerID == playerOffID]

            if len(frame) == 0:
                frame = teamMatch.addPlayerFrame(playersFrame, playerOffID)
            else:
                frame = frame[0]

            frame.removeFitness()

            if not managing_event:
                playerOn = Players.get_player_by_id(playerOnID)
                if home:
                    teamMatch.homeLineupPitch.addPlayer(playerPosition, playerOn.last_name)
                else:
                    teamMatch.awayLineupPitch.addPlayer(playerPosition, playerOn.last_name)

    def getPlayerRatings(self, team, finalLineup, currentLineup, events):

        oppositionEvents = self.awayEvents if team == self.homeTeam else self.homeEvents
        oppositionGoals = self.score[1] if team == self.homeTeam else self.score[0]

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

        for i, (position, playerID) in enumerate(finalLineup):
            self.getRating(venue, rating, ratingsDict, events, playerID, position, oppositionEvents, oppositionGoals, i)

        for i, (position, playerID) in enumerate(currentLineup.items()):
            self.getRating(venue, rating, ratingsDict, events, playerID, position, oppositionEvents, oppositionGoals, i + len(finalLineup))

        if team == self.homeTeam:
            self.homeRatings = ratingsDict
        else:
            self.awayRatings = ratingsDict

    def getRating(self, venue, rating, ratingsDict, events, playerID, position, oppositionEvents, oppositionGoals, i):

        scorerFlag = False
        for _, event in events.items():
            if "player" in event and event["player"] == playerID:
                if event["type"] in EVENT_RATINGS:
                    rating += random.choice(EVENT_RATINGS[event["type"]])
                    if event["type"] in ["goal", "penalty_goal"]:
                        scorerFlag = True

            if "assister" in event and event["assister"] == playerID:
                rating += random.choice(ASSIST_RATINGS)
        
        if not scorerFlag:
            if position == "Goalkeeper" or position in DEFENDER_POSITIONS:
                if oppositionGoals <= 1:
                    rating += random.choice(DEFENDER_GOALS_1)
                elif oppositionGoals <= 3:
                    rating += random.choice(DEFENDER_GOALS_3)
                else:
                    rating -= random.choice(DEFENDER_GOALS_MORE)
            else:  # mids and fwds that didn't score
                rating += random.choice(NON_SCORER_RATINGS)

        for _, event in oppositionEvents.items():
            if event["type"] == "own_goal" and event["player"] == playerID: # own goal
                rating -= random.choice([1.46, 1.49, 1.52, 1.57, 1.60, 1.63, 1.69, 1.78])

        finalRating = round(rating + 0.5, 2) if self.ratingsBoost == venue else round(rating - 0.5, 2) if self.ratingsDecay == venue else round(rating, 2)
        ratingsDict[playerID] = min(finalRating, 10)

    def saveData(self, managing_team = None):

        logger = logging.getLogger(__name__)

        try:
            currDate = Game.get_game_date(Managers.get_all_user_managers()[0].id)
            logger.debug(f"saveData START: match_id={self.match.id} auto={self.auto} managing_team={managing_team}")

            self.returnWinner()
            logger.debug(f"Winner resolved: {self.winner.id if self.winner else None}")

            logger.debug(f"Reducing suspensions for home={self.homeTeam.id} away={self.awayTeam.id} league={self.match.league_id}")
            PlayerBans.reduce_suspensions_for_team(self.homeTeam.id, self.match.league_id)
            PlayerBans.reduce_suspensions_for_team(self.awayTeam.id, self.match.league_id)

            logger.debug("Calculating player ratings for home and away teams")
            self.getPlayerRatings(self.homeTeam, self.homeFinalLineup, self.homeCurrentLineup, self.homeProcessedEvents)
            self.getPlayerRatings(self.awayTeam, self.awayFinalLineup, self.awayCurrentLineup, self.awayProcessedEvents)

            homeManager = Managers.get_manager_by_id(self.homeTeam.manager_id)
            awayManager = Managers.get_manager_by_id(self.awayTeam.manager_id)

            # debug counts
            logger.debug(f"Processed events counts: home={len(self.homeProcessedEvents)} away={len(self.awayProcessedEvents)}")

            logger.debug("Submitting DB update tasks to ThreadPoolExecutor")
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = []

                # LeagueTeams updates
                futures.append(executor.submit(
                    LeagueTeams.update_team,
                    self.homeTeam.id,
                    3 if self.winner == self.homeTeam else 1 if self.winner is None else 0,
                    1 if self.winner == self.homeTeam else 0,
                    1 if self.winner is None else 0,
                    1 if self.winner == self.awayTeam else 0,
                    self.score[0],
                    self.score[1]
                ))

                futures.append(executor.submit(
                    LeagueTeams.update_team,
                    self.awayTeam.id,
                    3 if self.winner == self.awayTeam else 1 if self.winner is None else 0,
                    1 if self.winner == self.awayTeam else 0,
                    1 if self.winner is None else 0,
                    1 if self.winner == self.homeTeam else 0,
                    self.score[1],
                    self.score[0]
                ))

                # Managers updates
                futures.append(executor.submit(Managers.update_games, homeManager.id,
                                                1 if self.winner == self.homeTeam else 0,
                                                1 if self.winner == self.awayTeam else 0))

                futures.append(executor.submit(Managers.update_games, awayManager.id,
                                                1 if self.winner == self.awayTeam else 0,
                                                1 if self.winner == self.homeTeam else 0))

                # Match events
                events_to_add = []
                for t, event in self.homeProcessedEvents.items():
                    player_id = event.get("player") or None
                    assister_id = event.get("assister") or None
                    player_off_id = event.get("player_off") or None
                    player_on_id = event.get("player_on") or None
                    minute = int(t.split(":")[0]) + 1

                    if event["extra"]:
                        if minute <= 50:
                            extraTime = minute - 45
                            minute = f"45 + {extraTime}"
                        else:
                            extraTime = minute - 90
                            minute = f"90 + {extraTime}"
                    else:
                        minute = str(minute)

                    if event["type"] == "goal":
                        events_to_add.append((self.match.id, "goal", minute, player_id))
                        events_to_add.append((self.match.id, "assist", minute, assister_id))
                        logger.debug(f"Home goal event queued: match={self.match.id} player={player_id} minute={minute}")
                    elif event["type"] == "penalty_miss":
                        goalkeeper_id = event["keeper"]
                        events_to_add.append((self.match.id, "penalty_miss", minute, player_id))
                        events_to_add.append((self.match.id, "penalty_saved", minute, goalkeeper_id))
                        logger.debug(f"Home penalty miss queued: match={self.match.id} player={player_id} minute={minute}")
                    elif event["type"] == "substitution":
                        events_to_add.append((self.match.id, "sub_off", minute, player_off_id))
                        events_to_add.append((self.match.id, "sub_on", minute, player_on_id))
                    elif event["type"] in ("injury", "red_card"):
                        events_to_add.append((self.match.id, event["type"], minute, player_id))
                        ban = get_player_ban(event["type"], Game.get_game_date(Managers.get_all_user_managers()[0].id))
                        logger.debug(f"Computed ban length={ban} for player={player_id} type={event['type']}")
                        sendEmail, _ = PlayerBans.add_player_ban(player_id, self.match.league_id if event["type"] == "red_card" else None, ban, event["type"], currDate)

                        if sendEmail:
                            emailDate = currDate + timedelta(days = 1)
                            if managing_team == "home" and event["type"] == "injury":
                                Emails.add_email("player_injury", None, player_id, ban, self.match.league_id, emailDate.replace(hour = 8, minute = 0, second = 0, microsecond = 0))
                            elif managing_team == "home" and event["type"] == "red_card":
                                Emails.add_email("player_ban", None, player_id, ban, self.match.league_id, emailDate.replace(hour = 8, minute = 0, second = 0, microsecond = 0))

                    elif event["type"] == "yellow_card":
                        events_to_add.append((self.match.id, "yellow_card", minute, player_id))
                        MatchEvents.check_yellow_card_ban(player_id, self.match.league_id, YELLOW_THRESHOLD, Game.get_game_date(Managers.get_all_user_managers()[0].id))
                    else:
                        events_to_add.append((self.match.id, event["type"], minute, player_id))

                for t, event in self.awayProcessedEvents.items():
                    player_id = event.get("player") or None
                    assister_id = event.get("assister") or None
                    player_off_id = event.get("player_off") or None
                    player_on_id = event.get("player_on") or None
                    minute = int(t.split(":")[0]) + 1

                    if event["extra"]:
                        if minute <= 50:
                            extraTime = minute - 45
                            minute = f"45 + {extraTime}"
                        else:
                            extraTime = minute - 90
                            minute = f"90 + {extraTime}"
                    else:
                        minute = str(minute)

                    if event["type"] == "goal":
                        events_to_add.append((self.match.id, "goal", minute, player_id))
                        events_to_add.append((self.match.id, "assist", minute, assister_id))
                        logger.debug(f"Away goal event queued: match={self.match.id} player={player_id} minute={minute}")
                    elif event["type"] == "penalty_miss":
                        goalkeeper_id = event["keeper"]
                        events_to_add.append((self.match.id, "penalty_miss", minute, player_id))
                        events_to_add.append((self.match.id, "penalty_saved", minute, goalkeeper_id))
                        logger.debug(f"Away penalty miss queued: match={self.match.id} player={player_id} minute={minute}")
                    elif event["type"] == "substitution":
                        events_to_add.append((self.match.id, "sub_off", minute, player_off_id))
                        events_to_add.append((self.match.id, "sub_on", minute, player_on_id))
                    elif event["type"] in ("injury", "red_card"):
                        events_to_add.append((self.match.id, event["type"], minute, player_id))
                        ban = get_player_ban(event["type"], Game.get_game_date(Managers.get_all_user_managers()[0].id))
                        logger.debug(f"Computed ban length={ban} for player={player_id} type={event['type']}")
                        sendEmail, _ = PlayerBans.add_player_ban(player_id, self.match.league_id if event["type"] == "red_card" else None, ban, event["type"], currDate)

                        if sendEmail:
                            emailDate = currDate + timedelta(days = 1)
                            if managing_team == "away" and event["type"] == "injury":
                                Emails.add_email("player_injury", None, player_id, ban, self.match.league_id, emailDate.replace(hour = 8, minute = 0, second = 0, microsecond = 0))
                            elif managing_team == "away" and event["type"] == "red_card":
                                Emails.add_email("player_ban", None, player_id, ban, self.match.league_id, emailDate.replace(hour = 8, minute = 0, second = 0, microsecond = 0))
                                
                    elif event["type"] == "yellow_card":
                        events_to_add.append((self.match.id, "yellow_card", minute, player_id))
                        MatchEvents.check_yellow_card_ban(player_id, self.match.league_id, YELLOW_THRESHOLD, Game.get_game_date(Managers.get_all_user_managers()[0].id))
                    else:
                        events_to_add.append((self.match.id, event["type"], minute, player_id))

                if self.homeCleanSheet:
                    events_to_add.append((self.match.id, "clean_sheet", "90", self.homeCurrentLineup["Goalkeeper"]))

                if self.awayCleanSheet:
                    events_to_add.append((self.match.id, "clean_sheet", "90", self.awayCurrentLineup["Goalkeeper"]))

                logger.debug(f"Submitting {len(events_to_add)} match events for insertion")
                futures.append(executor.submit(MatchEvents.batch_add_events, events_to_add))

                # Matches update
                logger.debug(f"Submitting match score update: {self.score[0]} -> {self.score[1]}")
                futures.append(executor.submit(Matches.update_score, self.match.id, self.score[0], self.score[1]))

                # Players updates
                fitness_to_update = []
                logger.debug("Preparing player fitness updates")
                for playerID, fitness in self.homeFitness.items():
                    fitness_to_update.append((playerID, round(fitness)))

                for playerID, fitness in self.awayFitness.items():
                    fitness_to_update.append((playerID, round(fitness)))

                logger.debug(f"Submitting fitness updates for {len(fitness_to_update)} players")
                futures.append(executor.submit(Players.batch_update_fitness, fitness_to_update))

                # Lineups and morales
                lineups_to_add = []
                morales_to_update = []
                sharpnesses_to_update = []

                homePlayers = Players.get_all_players_by_team(self.homeTeam.id)
                awayPlayers = Players.get_all_players_by_team(self.awayTeam.id)

                for player in homePlayers:
                    final_ids = {pl_id for _, pl_id in self.homeFinalLineup}
                    playerAdded = False

                    # Player was in final lineup (substituted off)
                    if player.id in final_ids:
                        playerAdded = True
                        if player.id in self.homeStartLineup.values():
                            start_position = list(self.homeStartLineup.keys())[list(self.homeStartLineup.values()).index(player.id)]
                        else:
                            start_position = None

                        self.add_player_lineup(
                            player=player,
                            start_position=start_position,
                            end_position=None,
                            rating=self.homeRatings[player.id],
                            reason=None,  # was selected
                            morales_to_update=morales_to_update,
                            lineups_to_add=lineups_to_add,
                            sharpnesses_to_update=sharpnesses_to_update,
                            processed_events=self.homeProcessedEvents,
                            winner=self.winner,
                            team=self.homeTeam,
                            goal_diff=self.goalDiffHome
                        )

                    # Player was in current lineup (finished on pitch)
                    if player.id in self.homeCurrentLineup.values():
                        playerAdded = True
                        if player.id in self.homeStartLineup.values():
                            start_position = list(self.homeStartLineup.keys())[list(self.homeStartLineup.values()).index(player.id)]
                        else:
                            start_position = None

                        end_position = list(self.homeCurrentLineup.keys())[list(self.homeCurrentLineup.values()).index(player.id)]

                        self.add_player_lineup(
                            player=player,
                            start_position=start_position,
                            end_position=end_position,
                            rating=self.homeRatings[player.id],
                            reason=None,  # was selected
                            morales_to_update=morales_to_update,
                            lineups_to_add=lineups_to_add,
                            sharpnesses_to_update=sharpnesses_to_update,
                            processed_events=self.homeProcessedEvents,
                            winner=self.winner,
                            team=self.homeTeam,
                            goal_diff=self.goalDiffHome
                        )

                    # Player not in final lineup OR current lineup
                    if player.id not in self.homeCurrentLineup.values() and player.id not in final_ids and player.id in self.homeCurrentSubs:
                        playerAdded = True
                        
                        # Player benched
                        self.add_player_lineup(
                            player=player,
                            start_position=None,
                            end_position=None,
                            rating=None,
                            reason="benched",
                            morales_to_update=morales_to_update,
                            lineups_to_add=lineups_to_add,
                            sharpnesses_to_update=sharpnesses_to_update,
                            processed_events=self.homeProcessedEvents,
                            winner=self.winner,
                            team=self.homeTeam,
                            goal_diff=self.goalDiffHome
                        )

                        if player.player_role != "Youth Team" and not playerAdded:
                            if PlayerBans.check_bans_for_player(player.id, self.league.league_id):
                                # Player unavailable (injury, suspension, etc.)
                                reason = "unavailable"
                            else:
                                reason = "not_in_squad"

                            self.add_player_lineup(
                                player=player,
                                start_position=None,
                                end_position=None,
                                rating=None,
                                reason=reason,
                                morales_to_update=morales_to_update,
                                lineups_to_add=lineups_to_add,
                                sharpnesses_to_update=sharpnesses_to_update,
                                processed_events=self.homeProcessedEvents,
                                winner=self.winner,
                                team=self.homeTeam,
                                goal_diff=self.goalDiffHome
                            )

                for player in awayPlayers:
                    final_ids = {pl_id for _, pl_id in self.awayFinalLineup}
                    playerAdded = False

                    # Player was in final lineup (substituted off)
                    if player.id in final_ids:
                        playerAdded = True
                        if player.id in self.awayStartLineup.values():
                            start_position = list(self.awayStartLineup.keys())[list(self.awayStartLineup.values()).index(player.id)]
                        else:
                            start_position = None

                        self.add_player_lineup(
                            player=player,
                            start_position=start_position,
                            end_position=None,
                            rating=self.awayRatings[player.id],
                            reason=None,  # was selected
                            morales_to_update=morales_to_update,
                            lineups_to_add=lineups_to_add,
                            sharpnesses_to_update=sharpnesses_to_update,
                            processed_events=self.awayProcessedEvents,
                            winner=self.winner,
                            team=self.awayTeam,
                            goal_diff=self.goalDiffAway
                        )

                    # Player was in current lineup (finished on pitch)
                    if player.id in self.awayCurrentLineup.values():
                        playerAdded = True
                        if player.id in self.awayStartLineup.values():
                            start_position = list(self.awayStartLineup.keys())[list(self.awayStartLineup.values()).index(player.id)]
                        else:
                            start_position = None

                        end_position = list(self.awayCurrentLineup.keys())[list(self.awayCurrentLineup.values()).index(player.id)]

                        self.add_player_lineup(
                            player=player,
                            start_position=start_position,
                            end_position=end_position,
                            rating=self.awayRatings[player.id],
                            reason=None,  # was selected
                            morales_to_update=morales_to_update,
                            lineups_to_add=lineups_to_add,
                            sharpnesses_to_update=sharpnesses_to_update,
                            processed_events=self.awayProcessedEvents,
                            winner=self.winner,
                            team=self.awayTeam,
                            goal_diff=self.goalDiffAway
                        )

                    # Player not in final lineup OR current lineup
                    if player.id not in self.awayCurrentLineup.values() and player.id not in final_ids and player.id in self.awayCurrentSubs:
                        playerAdded = True
                        
                        # Player benched
                        self.add_player_lineup(
                            player=player,
                            start_position=None,
                            end_position=None,
                            rating=None,
                            reason="benched",
                            morales_to_update=morales_to_update,
                            lineups_to_add=lineups_to_add,
                            sharpnesses_to_update=sharpnesses_to_update,
                            processed_events=self.awayProcessedEvents,
                            winner=self.winner,
                            team=self.awayTeam,
                            goal_diff=self.goalDiffAway
                        )

                    if player.player_role != "Youth Team" and not playerAdded:
                        if PlayerBans.check_bans_for_player(player.id, self.league.league_id):
                            # Player unavailable (injury, suspension, etc.)
                            reason = "unavailable"
                        else:
                            reason = "not_in_squad"

                        self.add_player_lineup(
                            player=player,
                            start_position=None,
                            end_position=None,
                            rating=None,
                            reason=reason,
                            morales_to_update=morales_to_update,
                            lineups_to_add=lineups_to_add,
                            sharpnesses_to_update=sharpnesses_to_update,
                            processed_events=self.awayProcessedEvents,
                            winner=self.winner,
                            team=self.awayTeam,
                            goal_diff=self.goalDiffAway
                        )

                # submit morales update
                futures.append(executor.submit(Players.batch_update_morales, morales_to_update))
                futures.append(executor.submit(Players.batch_update_sharpnesses, sharpnesses_to_update))

                # extra debug: how many rating entries we will store
                logger.debug(f"Ratings stored: home={len(self.homeRatings)} away={len(self.awayRatings)}")

                # debug total DB tasks
                logger.debug(f"Total DB tasks submitted: {len(futures)}")

                logger.debug(f"Submitting {len(lineups_to_add)} lineups for insertion")
                futures.append(executor.submit(TeamLineup.batch_add_lineups, lineups_to_add))

                logger.debug(f"Submitting {len(morales_to_update)} morale updates")

                concurrent.futures.wait(futures)
                logger.debug("All DB futures completed")
        except Exception as e:
            logger.error(f"Exception in saveData: {str(e)}", exc_info = True)
        finally:
            if self.auto:
                self.timerThread_running = False

    def getGameTime(self, playerID, events):
        sub_off_time = None
        sub_on_time = None
        red_card_time = None
        injury_time = None

        for time, event in events.items():
            if event["type"] == "sub_on" and event["player"] == playerID:
                sub_on_time = parse_time(time.split(":")[0])

            if event["type"] == "sub_off" and event["player"] == playerID:
                sub_off_time = parse_time(time.split(":")[0])

            if event["type"] == "red_card" and event["player"] == playerID:
                red_card_time = parse_time(time.split(":")[0])

            if event["type"] == "injury" and event["player"] == playerID:
                injury_time = parse_time(time.split(":")[0])

        playedEnough = False
        game_time = 0

        if not red_card_time and not injury_time:
            if sub_on_time and sub_off_time:
                game_time = sub_off_time - sub_on_time
            elif sub_on_time:
                game_time = 90 - sub_on_time
            elif sub_off_time:
                game_time = sub_off_time
            else:
                game_time = 90
        elif red_card_time and not injury_time:
            if sub_on_time:
                game_time = red_card_time - sub_on_time
            else:
                game_time = red_card_time
        else:
            if sub_on_time:
                game_time = injury_time - sub_on_time
            else:
                game_time = injury_time

        playedEnough = True if game_time >= 20 else False

        return playedEnough, game_time

    def add_player_lineup(self, player, start_position, end_position, rating, reason, morales_to_update, lineups_to_add, sharpnesses_to_update, processed_events, winner, team, goal_diff):
        """
        Add player lineup entry and apply morale changes depending on reason.
        """
        lineups_to_add.append((self.match.id, player.id, start_position, end_position, rating, reason))

        if reason is None:  # player played
            playedEnough, game_time = self.getGameTime(player.id, processed_events)
            if not playedEnough:
                # Played <20 minutes
                full_player = Players.get_player_by_id(player.id)
                moraleChange = get_morale_decrease_role(full_player)
            else:
                # Morale based on result & performance
                result = "win" if winner == team else "draw" if winner is None else "loss"
                moraleChange = get_morale_change(result, rating, goal_diff)

            morales_to_update.append((player.id, moraleChange))

            sharpnessGain = game_time * SHARPNESS_GAIN_PER_MINUTE
            sharpnesses_to_update.append((player.id, sharpnessGain))

        elif reason == "benched":
            # Benched but available -> morale decrease by role
            morales_to_update.append((player.id, get_morale_decrease_role(player)))

        # reason == "unavailable": no morale change, just log the lineup entry

    def returnWinner(self):
        finalScore = self.score
        self.goalDiffHome = finalScore[0] - finalScore[1]
        self.goalDiffAway = finalScore[1] - finalScore[0]
        if finalScore[0] > finalScore[1]:
            self.winner = self.homeTeam
        elif finalScore[0] < finalScore[1]:
            self.winner = self.awayTeam
        else:
            self.winner = None

    def appendScore(self, value, home):
        if home:
            self.score[0] += value
        else:
            self.score[1] += value

    def getEvents(self):
        return self.homeEvents, self.awayEvents
    
    def setRatingsBoost(self, team):
        self.ratingsBoost = team
    
    def setRatingsDecay(self, team):
        self.ratingsDecay = team