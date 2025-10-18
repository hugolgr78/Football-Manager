import threading, os, time, gc, logging
from settings import *
from data.database import *
from data.gamesDatabase import *
import concurrent.futures
from utils.util_functions import *

logger = logging.getLogger(__name__)
class Match():
    def __init__(self, match, auto = False, teamMatch = False):

        self.match = match
        self.auto = auto

        self.homeTeam = Teams.get_team_by_id(self.match.home_id)
        self.awayTeam = Teams.get_team_by_id(self.match.away_id)
        self.league = LeagueTeams.get_league_by_team(self.homeTeam.id)
        self.referee = Referees.get_referee_by_id(self.match.referee_id)

        self.homePlayersOBJ = {p.id: p for p in Players.get_all_players_by_team(self.homeTeam.id)}
        self.awayPlayersOBJ = {p.id: p for p in Players.get_all_players_by_team(self.awayTeam.id)}

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

        self.extraTimeHalf = 0
        self.extraTimeFull = 0
        self.halfTime = False
        self.fullTime = False

        self.homeFitness = {}
        self.awayFitness = {}

        self.homeStats = {stat: {} for stat in PLAYER_STATS}
        for stat in MATCH_STATS:
            if stat not in PLAYER_STATS:
                self.homeStats[stat] = 0

        # Order them as they in MATCH_STATS
        for stat in MATCH_STATS:
            if stat in self.homeStats:
                self.homeStats[stat] = self.homeStats.pop(stat)

        self.awayStats = {stat: {} for stat in PLAYER_STATS}
        for stat in MATCH_STATS:
            if stat not in PLAYER_STATS:
                self.awayStats[stat] = 0

        # Order them as they in MATCH_STATS
        for stat in MATCH_STATS:
            if stat in self.awayStats:
                self.awayStats[stat] = self.awayStats.pop(stat)

        self.homePassesAttempted = 0
        self.awayPassesAttempted = 0

        self.score = [0, 0]

        if self.auto:
            self.seconds, self.minutes = 0, 0

        if not teamMatch:
            self.createTeamLineup(self.homeTeam.id, True)
            self.createTeamLineup(self.awayTeam.id, False)

            self.homeRatings = {playerID: 6.0 for playerID in list(self.homeCurrentLineup.values()) + self.homeCurrentSubs}
            self.awayRatings = {playerID: 6.0 for playerID in list(self.awayCurrentLineup.values()) + self.awayCurrentSubs}

    def setUpRatings(self):
        self.homeRatings = {playerID: 6.0 for playerID in list(self.homeCurrentLineup.values()) + self.homeCurrentSubs}
        self.awayRatings = {playerID: 6.0 for playerID in list(self.awayCurrentLineup.values()) + self.awayCurrentSubs}

    def createTeamLineup(self, teamID, home):
        opponentID = self.match.away_id if home else self.match.home_id
        nonBanned = PlayerBans.get_all_non_banned_players_for_comp(teamID, self.league.league_id)
        nonBannedYouth = PlayerBans.get_all_non_banned_youth_players_for_comp(teamID, self.league.league_id)
        lineup = getProposedLineup(teamID, opponentID, self.league.league_id, Game.get_game_date(Managers.get_all_user_managers()[0].id), nonBanned, nonBannedYouth)
        substitutes = getSubstitutes(teamID, lineup, self.league.league_id, nonBanned, nonBannedYouth)

        if home:
            self.homeCurrentLineup = lineup
            self.homeCurrentSubs = substitutes
            self.homeStartLineup = lineup.copy()
            self.homeFitness = {playerID: self.homePlayersOBJ[playerID].fitness for playerID in list(lineup.values()) + substitutes}
        else:
            self.awayCurrentLineup = lineup
            self.awayCurrentSubs = substitutes
            self.awayStartLineup = lineup.copy()
            self.awayFitness = {playerID: self.awayPlayersOBJ[playerID].fitness for playerID in list(lineup.values()) + substitutes}

    def startGame(self):
        self.timerThread_running = True
        self.timerThread = threading.Thread(target = self.gameLoop)
        self.timerThread.daemon = True
        self.timerThread.start()

    def gameLoop(self):
        while self.timerThread_running:
            # prepare a bracketed match id prefix for logs
            prefix = f"[{getattr(self.match, 'id', None)}]"

            total_seconds = self.minutes * 60 + self.seconds
            logger.debug("%s gameLoop tick: minutes=%s seconds=%s total_seconds=%s", prefix, self.minutes, self.seconds, total_seconds)
            if self.seconds == 59:
                self.minutes += 1
                self.seconds = 0
            else:
                self.seconds += 1

            total_seconds = self.minutes * 60 + self.seconds
            if total_seconds % 90 == 0:
                for playerID, fitness in self.homeFitness.items():
                    if fitness > 0 and playerID in self.homeCurrentLineup.values():
                        self.homeFitness[playerID] = fitness - getFitnessDrop(self.homePlayersOBJ[playerID], fitness)

                        if self.homeFitness[playerID] < 0:
                            self.homeFitness[playerID] = 0

                        logger.debug("%s fitness reduced: player_id=%s new_fitness=%s", prefix, playerID, self.homeFitness[playerID])

                for playerID, fitness in self.awayFitness.items():
                    if fitness > 0 and playerID in self.awayCurrentLineup.values():
                        self.awayFitness[playerID] = fitness - getFitnessDrop(self.awayPlayersOBJ[playerID], fitness)

                        if self.awayFitness[playerID] < 0:
                            self.awayFitness[playerID] = 0

                        logger.debug("%s fitness reduced: player_id=%s new_fitness=%s", prefix, playerID, self.awayFitness[playerID])

            # ----------- half time ------------
            if self.minutes == 45 and self.seconds == 0:

                self.halfTime = True

                logger.info("%s Half time reached at %02d:%02d", prefix, self.minutes, self.seconds)

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

                logger.debug("%s Computed extraTimeHalf=%s", prefix, self.extraTimeHalf)

            if self.halfTime and self.minutes == 45 + self.extraTimeHalf and self.seconds == 0:
                self.halfTime = False
                self.minutes = 45
                self.seconds = 0

                logger.info("%s End of half time, resume at %02d:%02d", prefix, self.minutes, self.seconds)

            # ----------- full time ------------
            if self.minutes == 90 and self.seconds == 0:

                self.fullTime = True

                logger.info("%s Full time reached at %02d:%02d", prefix, self.minutes, self.seconds)

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

                logger.debug("%s Computed extraTimeFull=%s", prefix, self.extraTimeFull)

            if self.fullTime and self.minutes == 90 + self.extraTimeFull and self.seconds == 0:
                self.fullTime = False
                self.saveData()
            else:
                if total_seconds % TICK == 0:
                    logger.debug("%s TICK: generating events and updating possession at %02d:%02d", prefix, self.minutes, self.seconds)
                    self.generateEvents("home")
                    self.generateEvents("away")
                    passesAndPossession(self)

                # ----------- home events ------------
                for event_time, event_details in list(self.homeEvents.items()):
                    if event_time == str(self.minutes) + ":" + str(self.seconds) and event_time not in self.homeProcessedEvents:
                        logger.debug("%s Processing home event at %s: %s", prefix, event_time, event_details)
                        if event_details["extra"]:
                            if self.halfTime or self.fullTime:
                                self.getEventPlayer(event_details, True, event_time)
                                self.homeProcessedEvents[event_time] = event_details
                                logger.info("%s Processed extra home event: %s at %s", prefix, event_details.get("type"), event_time)
                        else:
                            if not (self.halfTime or self.fullTime):
                                self.getEventPlayer(event_details, True, event_time)
                                self.homeProcessedEvents[event_time] = event_details
                                logger.info("%s Processed home event: %s at %s", prefix, event_details.get("type"), event_time)

                # ----------- away events ------------
                for event_time, event_details in list(self.awayEvents.items()):
                    if event_time == str(self.minutes) + ":" + str(self.seconds) and event_time not in self.awayProcessedEvents:
                        logger.debug("%s Processing away event at %s: %s", prefix, event_time, event_details)
                        if event_details["extra"]:
                            if self.halfTime or self.fullTime:
                                self.getEventPlayer(event_details, False, event_time)
                                self.awayProcessedEvents[event_time] = event_details
                                logger.info("%s Processed extra away event: %s at %s", prefix, event_details.get("type"), event_time)
                        else:
                            if not (self.halfTime or self.fullTime):
                                self.getEventPlayer(event_details, False, event_time)
                                self.awayProcessedEvents[event_time] = event_details
                                logger.info("%s Processed away event: %s at %s", prefix, event_details.get("type"), event_time)

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
        ratings = self.homeRatings if side == "home" else self.awayRatings
        oppRatings = self.awayRatings if side == "home" else self.homeRatings

        playerOBJs = self.homePlayersOBJ if side == "home" else self.awayPlayersOBJ
        oppPlayersOBJs = self.awayPlayersOBJ if side == "home" else self.homePlayersOBJ

        sharpness = [playerOBJs[playerID].sharpness for playerID in lineup.values()]
        avgSharpnessWthKeeper = sum(sharpness) / len(sharpness)

        if "Goalkeeper" in lineup:
            avgSharpness = (sum(sharpness) - playerOBJs[lineup["Goalkeeper"]].sharpness) / (len(sharpness) - 1)
        else:
            avgSharpness = avgSharpnessWthKeeper

        avgFitness = sum(fitness[playerID] for playerID in lineup.values()) / len(lineup)

        morale = [playerOBJs[playerID].morale for pos, playerID in lineup.items() if pos != "Goalkeeper"]
        avgMorale = sum(morale) / len(morale)

        oppKeeper = oppPlayersOBJs.get(oppLineup["Goalkeeper"]) if "Goalkeeper" in oppLineup else None

        attackingPlayers = [playerID for pos, playerID in lineup.items() if pos in ATTACKING_POSITIONS]
        defendingPlayers = [playerID for pos, playerID in oppLineup.items() if pos in DEFENSIVE_POSITIONS]

        attackingLevel = teamStrength(attackingPlayers, "attack", playerOBJs)
        defendingLevel = teamStrength(defendingPlayers, "defend", oppPlayersOBJs)

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
        subsChosen = substitutionChances(lineup, subsCount, subs.copy(), events, self.minutes, fitness, playerOBJs, ratings)

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

            if stat in PLAYER_STATS:
                playerID, rating = getStatPlayer(stat, lineup, playerOBJs)
                ratings[playerID] = min(10, max(0, round(ratings.get(playerID, 0) + rating, 2)))

                if not playerID:
                    continue

                if not playerID in stats[stat]:
                    stats[stat][playerID] = 0

                stats[stat][playerID] += 1

                match stat:
                    case "Shots":
                        shotDirection = random.choices(population = list(SHOT_DIRECTION_CHANCES.keys()), weights = list(SHOT_DIRECTION_CHANCES.values()), k = 1)[0]
                        if not playerID in stats[shotDirection]:
                            stats[shotDirection][playerID] = 0

                        stats[shotDirection][playerID] += 1

                        shotOutcome = random.choices(population = list(SHOT_CHANCES.keys()), weights = list(SHOT_CHANCES.values()), k = 1)[0]
                        if shotOutcome != "wide":
                            stats[shotOutcome] += 1

                        if random.random() < SHOT_BIG_CHANCE:
                            if not playerID in stats["Big chances missed"]:
                                stats["Big chances missed"][playerID] = 0

                            stats["Big chances missed"][playerID] += 1

                            playerID, rating = getStatPlayer("Big chances created", lineup, playerOBJs)
                            ratings[playerID] = min(10, max(0, round(ratings.get(playerID, 0) + rating, 2)))

                            if not playerID in stats["Big chances created"]:
                                stats["Big chances created"][playerID] = 0

                            stats["Big chances created"][playerID] += 1

                        stats["xG"] += round(random.uniform(0.02, MAX_XG), 2)
                        stats["xG"] = round(stats["xG"], 2)
                    case "Shots on target":
                        if playerID not in stats["Shots"]:
                            stats["Shots"][playerID] = 0
                        
                        stats["Shots"][playerID] += 1

                        shotDirection = random.choices(population = list(SHOT_DIRECTION_CHANCES.keys()), weights = list(SHOT_DIRECTION_CHANCES.values()), k = 1)[0]
                        if not playerID in stats[shotDirection]:
                            stats[shotDirection][playerID] = 0

                        stats[shotDirection][playerID] += 1

                        if random.random() < SHOT_BIG_CHANCE:
                            if not playerID in stats["Big chances missed"]:
                                stats["Big chances missed"][playerID] = 0

                            stats["Big chances missed"][playerID] += 1

                            playerID, rating = getStatPlayer("Big chances created", lineup, playerOBJs)
                            ratings[playerID] = min(10, max(0, round(ratings.get(playerID, 0) + rating, 2)))

                            if not playerID in stats["Big chances created"]:
                                stats["Big chances created"][playerID] = 0

                            stats["Big chances created"][playerID] += 1

                        # Opponent keeper stats
                        playerID, rating = getStatPlayer("Saves", oppLineup, oppPlayersOBJs)
                        if playerID:
                            if playerID not in oppStats["Saves"]:
                                oppStats["Saves"][playerID] = 0
                            oppStats["Saves"][playerID] += 1

                            oppRatings[playerID] = min(10, max(0, round(oppRatings.get(playerID, 0) + rating, 2)))

                        stats["xG"] += round(random.uniform(0.02, MAX_XG), 2)
                        stats["xG"] = round(stats["xG"], 2)
            else:
                stats[stat] += 1

    def join(self):
        if self.timerThread:
            self.timerThread.join()

    def getEventPlayer(self, event, home, time, teamMatch = None, managing_team = False):

        lineup = self.homeCurrentLineup if home else self.awayCurrentLineup
        oppLineup = self.awayCurrentLineup if home else self.homeCurrentLineup
        subs = self.homeCurrentSubs if home else self.awayCurrentSubs
        finalLineup = self.homeFinalLineup if home else self.awayFinalLineup
        processedEvents = self.homeProcessedEvents if home else self.awayProcessedEvents
        events = self.homeEvents if home else self.awayEvents
        subsCount = self.homeSubs if home else self.awaySubs
        fitness = self.homeFitness if home else self.awayFitness
        stats = self.homeStats if home else self.awayStats
        oppStats = self.awayStats if home else self.homeStats
        ratings = self.homeRatings if home else self.awayRatings
        oppRatings = self.awayRatings if home else self.homeRatings

        playerOBJs = self.homePlayersOBJ if home else self.awayPlayersOBJ
        oppPlayerOBJs = self.awayPlayersOBJ if home else self.homePlayersOBJ

        # Fetch all players in the lineup with a single query
        players_dict = {p.id: p for p in playerOBJs.values() if p.id in lineup.values()}

        try:
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

                stats["xG"] += round(random.uniform(0.02, MAX_XG), 2)
                stats["xG"] = round(stats["xG"], 2)

                # Add rating for scoring
                rating = random.uniform(GOAL_RATINGS[0], GOAL_RATINGS[1])
                ratings[playerID] = min(10, max(0, round(ratings.get(playerID, 0) + rating, 2)))

                # Reduce rating for the opposition defence and keeper
                oppKeeperRating = random.uniform(GOAL_CONCEDED_KEEPER_RATING[0], GOAL_CONCEDED_KEEPER_RATING[1])
                if "Goalkeeper" in oppLineup:
                    oppKeeperID = oppLineup["Goalkeeper"]
                    oppRatings[oppKeeperID] = min(10, max(0, round(oppRatings.get(oppKeeperID, 0) + oppKeeperRating, 2)))

                for pos, playerID in oppLineup.items():
                    if pos in DEFENDER_POSITIONS:
                        defenderRating = random.uniform(GOAL_CONCEDED_DEFENCE_RATING[0], GOAL_CONCEDED_DEFENCE_RATING[1])
                        oppRatings[playerID] = min(10, max(0, round(oppRatings.get(playerID, 0) + defenderRating, 2)))

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

                rating = random.uniform(ASSIST_RATINGS[0], ASSIST_RATINGS[1])
                ratings[playerID] = min(10, max(0, round(ratings.get(playerID, 0) + rating, 2)))

            elif event["type"] == "penalty_goal" or event["type"] == "penalty_miss":
                penaltyPosition = random.choices(list(PENALTY_TAKER_CHANCES.keys()), weights = list(PENALTY_TAKER_CHANCES.values()), k = 1)[0]
                players = [player.id for player in players_dict.values() if player.position == penaltyPosition]

                while len(players) == 0:
                    penaltyPosition = random.choices(list(PENALTY_TAKER_CHANCES.keys()), weights = list(PENALTY_TAKER_CHANCES.values()), k = 1)[0]
                    players = [player.id for player in players_dict.values() if player.position == penaltyPosition]

                playerID = random.choices(players, k = 1)[0]
                event["player"] = playerID

                if playerID not in stats["Shots on target"]:
                    stats["Shots on target"][playerID] = 0
                
                stats["Shots on target"][playerID] += 1
            
                if playerID not in stats["Shots"]:
                    stats["Shots"][playerID] = 0

                stats["Shots"][playerID] += 1
            
                if event["type"] == "penalty_miss":
                    if event["keeper"] not in oppStats["Saves"]:
                        oppStats["Saves"][event["keeper"]] = 0
                
                    oppStats["Saves"][event["keeper"]] += 1
                    rating = PENALTY_MISS_RATING

                    keeperRating = PENALTY_SAVED_RATING
                    oppRatings[event["keeper"]] = min(10, max(0, round(oppRatings.get(event["keeper"], 0) + keeperRating, 2)))
                else:
                    rating = PENALTY_SCORE_RATING

                ratings[playerID] = min(10, max(0, round(ratings.get(playerID, 0) + rating, 2)))

                stats["xG"] += 0.8

            elif event["type"] == "own_goal":
                ownGoalPosition = random.choices(list(OWN_GOAL_CHANCES.keys()), weights = list(OWN_GOAL_CHANCES.values()), k = 1)[0]
                oppositionLineup = self.homeCurrentLineup if lineup == self.awayCurrentLineup else self.awayCurrentLineup
                
                players = [p for p in oppPlayerOBJs.values() if p.id in oppositionLineup.values()]
                players_in_position = [player for player in players if player.position == ownGoalPosition]

                if not players_in_position:
                    players_in_position = players
                    
                weights = [ownGoalFoulWeight(p) for p in players_in_position]
                playerID = random.choices(players_in_position, weights = weights, k = 1)[0].id

                event["player"] = playerID

                rating = random.uniform(OWN_GOAL_RATINGS[0], OWN_GOAL_RATINGS[1])
                oppRatings[playerID] = min(10, max(0, round(oppRatings.get(playerID, 0) + rating, 2)))

            elif event["type"] == "yellow_card":
                weights = [ownGoalFoulWeight(player) for player in players_dict.values()]
                playerID = random.choices(list(players_dict.values()), weights = weights, k = 1)[0].id
                event["player"] = playerID
                stats["Yellow cards"] += 1

                if random.random() < CARD_FOUL_CHANCE:
                    if playerID not in stats["Fouls"]:
                        stats["Fouls"][playerID] = 0
                    
                    stats["Fouls"][playerID] += 1

                secondYellow = False
                for _, processedEvent in processedEvents.items():
                    if processedEvent["type"] == "yellow_card" and processedEvent["player"] == playerID:
                        event["type"] = "red_card"
                        stats["Yellow cards"] -= 1
                        stats["Red cards"] += 1

                        secondYellow = True

                        playerPosition = list(lineup.keys())[list(lineup.values()).index(playerID)]
                        lineup.pop(playerPosition)
                        finalLineup.append((playerPosition, playerID))

                        event["position"] = playerPosition

                        if teamMatch:
                            self.updateTeamMatch(playerID, playerPosition, teamMatch, home)
                        
                        if playerPosition == "Goalkeeper" and not managing_team:
                            self.keeperSub(subsCount, lineup, players_dict, processedEvents, time, events, teamMatch, subs, home)

                        rating = random.uniform(RED_CARD_RATINGS[0], RED_CARD_RATINGS[1])
                        ratings[playerID] = min(10, max(0, round(ratings.get(playerID, 0) + rating, 2)))
                        break

                if not secondYellow:
                    rating = random.uniform(YELLOW_CARD_RATINGS[0], YELLOW_CARD_RATINGS[1])
                    ratings[playerID] = min(10, max(0, round(ratings.get(playerID, 0) + rating, 2)))

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

                rating = random.uniform(RED_CARD_RATINGS[0], RED_CARD_RATINGS[1])
                ratings[playerID] = min(10, max(0, round(ratings.get(playerID, 0) + rating, 2)))

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

                weights = [fitnessWeight(fitness[player.id]) for player in players_dict.values()]

                injuredPlayerID = random.choices(list(players_dict.values()), weights = weights, k = 1)[0].id
                event["player"] = injuredPlayerID

                playerPosition = list(lineup.keys())[list(lineup.values()).index(injuredPlayerID)]

                if not managing_team and subsCount < MAX_SUBS:
                    self.createSubEvent(lineup, players_dict, processedEvents, time, events, injuredPlayerID, subs, home, playerOBJs, playerPos = playerPosition)

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
        except Exception as e:
            logger.error("ERROR processing event %s at %s: %s", event, time, e)
            return None

        if teamMatch:
            return event

    def updateTeamMatch(self, playerOffID, oldPosition, teamMatch, home):

        playerOBJs = self.homePlayersOBJ if home else self.awayPlayersOBJ

        playerData = playerOBJs[playerOffID] or Players.get_player_by_id(playerOffID)
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
        playerOBJs = self.homePlayersOBJ if home else self.awayPlayersOBJ

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
                last_name = playerOBJs[newKeeper].last_name or Players.get_player_by_id(newKeeper).last_name
                if home:
                    teamMatch.homeLineupPitch.movePlayer(newKeeperPosition, "Goalkeeper", last_name)
                else:
                    teamMatch.awayLineupPitch.movePlayer(newKeeperPosition, "Goalkeeper", last_name)
        else:
            self.createSubEvent(lineup, players_dict, processedEvents, time, events, None, subs, home, playerOBJs, keeperSub = True)

    def createSubEvent(self, lineup, players_dict, processedEvents, time, events, playerOffID, subs, home, playerOBJs, keeperSub = False, playerPos = None):
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

            playerOffID = self.checkPlayerOff(playerOffID, processedEvents, time, lineup, home)
            playerPos = "Goalkeeper"

        subChoice = find_substitute(lineup, [(1, playerOffID, playerPos)], subs, 1, playerOBJs)[0]
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

    def checkPlayerOff(self, playerID, processEvents, time, lineup, home, checked_players = None):

        playerOBJs = self.homePlayersOBJ if home else self.awayPlayersOBJ

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

                    players_dict = {p.id: p for p in playerOBJs.values() if p.id in lineup.values()}

                    available_players = [player.id for player in players_dict.values() if player.position != "goalkeeper" and player.id not in checked_players]
                    if not available_players:
                        return random.choices(list(lineup.values()), k = 1)[0]  # No available players, return a random player
                    
                    new_player = random.choices(available_players, k = 1)[0]
                    return self.checkPlayerOff(new_player, processEvents, time, lineup, home, checked_players = checked_players)

        return playerID  # No substitution event found for the player

    def addPlayerToLineup(self, playerOnID, playerOffID, playerPosition, posOff, subs, lineup, teamMatch, home, managing_event = None):

        playerOBJs = self.homePlayersOBJ if home else self.awayPlayersOBJ

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
                playerOn = playerOBJs[playerOnID] or Players.get_player_by_id(playerOnID)
                if home:
                    teamMatch.homeLineupPitch.addPlayer(playerPosition, playerOn.last_name)
                else:
                    teamMatch.awayLineupPitch.addPlayer(playerPosition, playerOn.last_name)

    def saveData(self, managing_team = None):

        logger = logging.getLogger(__name__)
        prefix = f"[{getattr(self.match, 'id', None)}]:"

        try:
            currDate = Game.get_game_date(Managers.get_all_user_managers()[0].id)

            try:
                home_goals = sum(1 for ev in self.homeProcessedEvents.values() if ev.get("type") in ("goal", "penalty_goal", "own_goal"))
                away_goals = sum(1 for ev in self.awayProcessedEvents.values() if ev.get("type") in ("goal", "penalty_goal", "own_goal"))
                if [home_goals, away_goals] != self.score:
                    logger.warning("%s Score mismatch detected - events indicate %s:%s but self.score=%s. Reconciling to events.", prefix, home_goals, away_goals, self.score)
                    self.score = [home_goals, away_goals]
            except Exception:
                logger.exception("%s Error while reconciling score from events", prefix)

            logger.debug(f"{prefix} saveData START: match_id={self.match.id}, auto={self.auto}, managing_team={managing_team}, score = {self.score}")

            self.returnWinner()
            logger.debug(f"{prefix} Winner resolved: {self.winner.id if self.winner else None}")
            logger.debug(f"{prefix} Processed events counts: home={len(self.homeProcessedEvents)} away={len(self.awayProcessedEvents)}")
            try:
                self.payload = self.getPayload(currDate)
            except Exception:
                self.payload = None
                raise
        except Exception as e:
            logger.error(f"{prefix} Exception in saveData: {str(e)}", exc_info = True)
        finally:
            if self.auto:
                self.timerThread_running = False
            else:
                return self.payload

    def getPayload(self, currDate):
        prefix = f"[{getattr(self.match, 'id', None)}]:"

        try: 
            payload = {
                "team_updates": [],
                "manager_updates": [],
                "match_events": [],
                "player_bans": [],
                "yellow_card_checks": [],
                "score_updates": [],
                "fitness_updates": [],
                "sharpness_updates": [],
                "morale_updates": [],
                "lineup_updates": [],
                "stats_updates": [],
            }

            homeManager = Managers.get_manager_by_id(self.homeTeam.manager_id)
            awayManager = Managers.get_manager_by_id(self.awayTeam.manager_id)

            # LeagueTeams updates
            payload["team_updates"].append((
                self.homeTeam.id,
                3 if self.winner == self.homeTeam else 1 if self.winner is None else 0,
                1 if self.winner == self.homeTeam else 0,
                1 if self.winner is None else 0,
                1 if self.winner == self.awayTeam else 0,
                self.score[0],
                self.score[1]
            ))

            payload["team_updates"].append((
                self.awayTeam.id,
                3 if self.winner == self.awayTeam else 1 if self.winner is None else 0,
                1 if self.winner == self.awayTeam else 0,
                1 if self.winner is None else 0,
                1 if self.winner == self.homeTeam else 0,
                self.score[1],
                self.score[0]
            ))

            # Managers updates
            payload["manager_updates"].append((
                homeManager.id,
                1 if self.winner == self.homeTeam else 0,
                1 if self.winner == self.awayTeam else 0
            ))

            payload["manager_updates"].append((
                awayManager.id,
                1 if self.winner == self.awayTeam else 0,
                1 if self.winner == self.homeTeam else 0
            ))

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
                    logger.debug(f"{prefix} Home goal event queued: match={self.match.id} player={player_id} minute={minute}")
                elif event["type"] == "penalty_miss":
                    goalkeeper_id = event["keeper"]
                    events_to_add.append((self.match.id, "penalty_miss", minute, player_id))
                    events_to_add.append((self.match.id, "penalty_saved", minute, goalkeeper_id))
                    logger.debug(f"{prefix} Home penalty miss queued: match={self.match.id} player={player_id} minute={minute}")
                elif event["type"] == "substitution":
                    events_to_add.append((self.match.id, "sub_off", minute, player_off_id))
                    events_to_add.append((self.match.id, "sub_on", minute, player_on_id))
                elif event["type"] in ("injury", "red_card"):
                    events_to_add.append((self.match.id, event["type"], minute, player_id))
                    ban = get_player_ban(event["type"], currDate)
                    logger.debug(f"{prefix} Computed ban length={ban} for player={player_id} type={event['type']}")
                    payload["player_bans"].append((player_id, self.match.league_id if event["type"] == "red_card" else None, ban, event["type"], currDate))
                elif event["type"] == "yellow_card":
                    events_to_add.append((self.match.id, "yellow_card", minute, player_id))
                    payload["yellow_card_checks"].append((player_id, self.match.league_id, YELLOW_THRESHOLD, currDate))
                    logger.debug(f"{prefix} Home yellow card queued: match={self.match.id} player={player_id} minute={minute}")
                else:
                    events_to_add.append((self.match.id, event["type"], minute, player_id))
                    logger.debug(f"{prefix} Home event queued: event={event["type"]}, match={self.match.id}, player={player_id}, minute={minute}")

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
                    logger.debug(f"{prefix} Away goal event queued: match={self.match.id} player={player_id} minute={minute}")
                elif event["type"] == "penalty_miss":
                    goalkeeper_id = event["keeper"]
                    events_to_add.append((self.match.id, "penalty_miss", minute, player_id))
                    events_to_add.append((self.match.id, "penalty_saved", minute, goalkeeper_id))
                    logger.debug(f"{prefix} Away penalty miss queued: match={self.match.id} player={player_id} minute={minute}")
                elif event["type"] == "substitution":
                    events_to_add.append((self.match.id, "sub_off", minute, player_off_id))
                    events_to_add.append((self.match.id, "sub_on", minute, player_on_id))
                elif event["type"] in ("injury", "red_card"):
                    events_to_add.append((self.match.id, event["type"], minute, player_id))
                    ban = get_player_ban(event["type"], currDate)
                    logger.debug(f"{prefix} Computed ban length={ban} for player={player_id} type={event['type']}")
                    payload["player_bans"].append((player_id, self.match.league_id if event["type"] == "red_card" else None, ban, event["type"], currDate))
                elif event["type"] == "yellow_card":
                    events_to_add.append((self.match.id, "yellow_card", minute, player_id))
                    payload["yellow_card_checks"].append((player_id, self.match.league_id, YELLOW_THRESHOLD, currDate))
                    logger.debug(f"{prefix} Away yellow card queued: match={self.match.id} player={player_id} minute={minute}")
                else:
                    events_to_add.append((self.match.id, event["type"], minute, player_id))
                    logger.debug(f"{prefix} Away event queued: event={event["type"]}, match={self.match.id}, player={player_id}, minute={minute}")
                
            if self.homeCleanSheet:
                events_to_add.append((self.match.id, "clean_sheet", "90", self.homeCurrentLineup["Goalkeeper"]))

            if self.awayCleanSheet:
                events_to_add.append((self.match.id, "clean_sheet", "90", self.awayCurrentLineup["Goalkeeper"]))

            payload["match_events"] = events_to_add

            # Matches update
            logger.debug(f"{prefix} Submitting match score update: {self.score[0]} : {self.score[1]}")
            payload["score_updates"].append((self.match.id, self.score[0], self.score[1]))

            # Players updates
            fitness_to_update = []
            logger.debug(f"{prefix} Preparing player fitness updates")
            for playerID, fitness in self.homeFitness.items():
                fitness_to_update.append((playerID, round(fitness)))

            for playerID, fitness in self.awayFitness.items():
                fitness_to_update.append((playerID, round(fitness)))

            logger.debug(f"{prefix} Submitting fitness updates for {len(fitness_to_update)} players")
            payload["fitness_updates"] = fitness_to_update

            # Lineups and morales
            lineups_to_add = []
            morales_to_update = []
            sharpnesses_to_update = []

            for player in self.homePlayersOBJ.values():
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
                        rating=min(10, max(0, round(self.homeRatings[player.id], 2)), 10),
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
                        rating=min(10, max(0, round(self.homeRatings[player.id], 2)), 10),
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

            for player in self.awayPlayersOBJ.values():
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
                        rating=min(10, max(0, round(self.awayRatings[player.id], 2)), 10),
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
                        rating=min(10, max(0, round(self.awayRatings[player.id], 2)), 10),
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

            # submit morale updates
            logger.debug(f"{prefix} Submitting {len(morales_to_update)} morale updates")
            payload["morale_updates"] = morales_to_update
            payload["sharpness_updates"] = sharpnesses_to_update            

            # extra debug: how many rating entries we will store
            logger.debug(f"{prefix} Ratings stored: home={len(self.homeRatings)} away={len(self.awayRatings)}")

            # Stats
            stats_to_add = []
            for stat, data in self.homeStats.items():

                if stat not in SAVED_STATS:
                    continue

                if stat in PLAYER_STATS:
                    for player_id, value in data.items():
                        stats_to_add.append((self.match.id, stat, value, player_id, None))
                elif data != 0:
                    stats_to_add.append((self.match.id, stat, data, None, self.homeTeam.id))

            for stat, data in self.awayStats.items():

                if stat not in SAVED_STATS:
                    continue

                if stat in PLAYER_STATS:
                    for player_id, value in data.items():
                        stats_to_add.append((self.match.id, stat, value, player_id, None))
                elif data != 0:
                    stats_to_add.append((self.match.id, stat, data, None, self.awayTeam.id))

            if len(stats_to_add) > 0:
                logger.debug(f"{prefix} Submitting {len(stats_to_add)} match stats for insertion")
                payload["stats_updates"] = stats_to_add

            logger.debug(f"{prefix} Submitting {len(lineups_to_add)} lineups for insertion")
            payload["lineup_updates"] = lineups_to_add
        except Exception as e:
            logger.error(f"{prefix} Exception in getPayload: {str(e)}", exc_info = True)
        finally:
            return payload

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
                full_player = self.homePlayersOBJ[player.id] if team == self.homeTeam else self.awayPlayersOBJ[player.id]
                moraleChange = get_morale_decrease_role(full_player)
            else:
                # Morale based on result & performance
                result = "win" if winner == team else "draw" if winner is None else "loss"
                moraleChange = get_morale_change(result, rating, goal_diff)

            morales_to_update.append((player.id, moraleChange))

            sharpnessGain = game_time * SHARPNESS_GAIN_PER_MINUTE
            sharpnesses_to_update.append((player.id, sharpnessGain))

        elif reason == "benched":
            morales_to_update.append((player.id, get_morale_decrease_role(player)))

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

    def setRatingsBoost(self, team):
        self.ratingsBoost = team
    
    def setRatingsDecay(self, team):
        self.ratingsDecay = team