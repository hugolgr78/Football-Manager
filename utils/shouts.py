import customtkinter as ctk
from settings import *
from data.database import *
from data.gamesDatabase import *
from utils.util_functions import *

class ShoutFrame(ctk.CTkFrame):
    def __init__(self, parent, width, height, corner_radius, fgColor, shout, matchFrame, home, time, shoutMadeFunction, closeFunction):
        super().__init__(parent, fg_color = fgColor, width = width, height = height, corner_radius = corner_radius)
        self.pack(fill = "both", padx = 10, pady = 5)

        self.parent = parent
        self.matchFrame = matchFrame
        self.home = home
        self.time = str(time)
        self.currMinute = int(self.time.split(":")[0])
        self.shoutMadeFunction = shoutMadeFunction
        self.closeFunction = closeFunction

        self.score = self.matchFrame.getCurrentScore()
        self.match = self.matchFrame.matchInstance

        self.shout = SHOUT_CLASSES[shout](self)

        self.button = ctk.CTkButton(self, text = shout, width = width, font = (APP_FONT, 20), fg_color = fgColor, hover_color = GREY_BACKGROUND, command = self.shout.shoutAction)
        self.button.place(relx = 0.5, rely = 0.5, anchor = "center")

    def addGoal(self, home):
        events = self.match.homeEvents if home else self.match.awayEvents
        addEvent = True
        for event_time, event_data in events.items():
            eventMinute = int(event_time.split(":")[0])
            if eventMinute < self.currMinute + 10 and eventMinute > self.currMinute and (event_data["type"] == "goal" or event_data["type"] == "penalty_goal" or event_data["type"] == "own_goal"):
                addEvent = False
                break
        
        if addEvent:
            type_ = random.choices(list(GOAL_TYPE_CHANCES.keys()), weights = [GOAL_TYPE_CHANCES[goalType] for goalType in GOAL_TYPE_CHANCES])[0]
            if type_ == "penalty":
                type_ = "penalty_goal"

            minute = self.currMinute + random.randint(1, 10)
            second = random.randint(0, 59)

            extra = False
            if minute >= 90:
                extra = True

            events[str(minute) + ":" + str(second)] = {"type": type_, "extra": extra}
            self.match.score.appendScore(1, home)

    def removeGoal(self, home):
        events = self.match.homeEvents if home else self.match.awayEvents
        
        for event_time, event_data in events.items():
            eventMinute = int(event_time.split(":")[0])
            if eventMinute < self.currMinute + 10 and eventMinute > self.currMinute and (event_data["type"] == "goal" or event_data["type"] == "penalty_goal" or event_data["type"] == "own_goal"):
                del events[event_time]
                self.match.score.appendScore(-1, home)
                break

    def getCurrResult(self, score):
        if score[0] > score[1]:
            return "win" if self.home else "lose"
        elif score[0] < score[1]:
            return "lose" if self.home else "win"
        else:
            return "draw"

    def getGoalDiff(self, score):
        return abs(int(score[0]) - int(score[1]))

    def getWinThenDraw(self, managingTeam):
        teamEvents = self.match.homeEvents if self.home else self.match.awayEvents
        oppEvents = self.match.awayEvents if self.home else self.match.homeEvents

        teamScore = 0
        oppScore = 0
        wasWinning = False

        if managingTeam:
            for time in sorted(teamEvents.keys()):
                minute = int(time.split(":")[0])
                if minute < self.currMinute - 10: # only check the last 10 minutes
                    continue
                if minute >= self.currMinute: # stop checking when the shout was made
                    break

                if teamEvents[time]["type"] in ["goal", "penalty_goal", "own_goal"]:
                    teamScore += 1
                if oppEvents.get(time) and oppEvents[time]["type"] in ["goal", "penalty_goal", "own_goal"]:
                    oppScore += 1

                if teamScore > oppScore:
                    wasWinning = True
                elif teamScore == oppScore and wasWinning:
                    return True

            return False
        else:
            for time in sorted(oppEvents.keys()):
                minute = int(time.split(":")[0])
                if minute < self.currMinute - 10: # only check the last 10 minutes
                    continue
                if minute >= self.currMinute: # stop checking when the shout was made
                    break

                if oppEvents[time]["type"] in ["goal", "penalty_goal", "own_goal"]:
                    oppScore += 1
                if teamEvents.get(time) and teamEvents[time]["type"] in ["goal", "penalty_goal", "own_goal"]:
                    teamScore += 1

                if oppScore > teamScore:
                    wasWinning = True
                elif oppScore == teamScore and wasWinning:
                    return True

            return False

    def opponentScoredLast5(self):
        oppEvents = self.match.awayEvents if self.home else self.match.homeEvents

        for time in sorted(oppEvents.keys(), reverse = True):
            minute = int(time.split(":")[0])
            if minute < self.currMinute - 5:
                break
            if oppEvents[time]["type"] in ["goal", "penalty_goal", "own_goal"]:
                return True

        return False

class Encourage():
    def __init__(self, parent):
        self.parent = parent
        self.home = self.parent.home
        self.score = self.parent.score

    def shoutAction(self):
        self.parent.shoutMadeFunction()
        result = self.parent.getCurrResult(self.score)

        if result == "win":
            if random.random() < 0.1: # opponnent scores a goal
                self.parent.addGoal(not self.home)

        else:
            if random.random() < 0.05: # team scores a goal
                self.parent.addGoal(self.home)

        self.parent.closeFunction() 

class Praise():
    def __init__(self, parent):
        self.parent = parent
        self.home = self.parent.home
        self.score = self.parent.score
        self.match = self.parent.match

        self.str = "home" if self.home else "away"

    def shoutAction(self):
        self.parent.shoutMadeFunction()
        result = self.parent.getCurrResult(self.score)
        goalDiff = self.parent.getGoalDiff(self.score)

        if result == "win" and goalDiff >= 2:
            if random.random() < 0.1: 
                self.match.setRatingsBoost(self.str)
            
        elif result == "lose":
            if random.random() < 0.5:
                self.parent.addGoal(not self.home)
                self.match.setRatingsDecay(self.str)

        elif result == "draw" and self.parent.getWinThenDraw(False):
            if random.random() < 0.2:
                self.match.setRatingsBoost(self.str)

        self.parent.closeFunction() 

class Focus():
    def __init__(self, parent):
        self.parent = parent
        self.home = self.parent.home
        self.score = self.parent.score

    def shoutAction(self):
        self.parent.shoutMadeFunction()
        result = self.parent.getCurrResult(self.score)
        goalDiff = self.parent.getGoalDiff(self.score)

        if result == "win" and goalDiff >= 2: # if the team is winning by more than two goals (2-0, 3-1), chance to add opponent goal
            if random.random() < 0.2:
                self.parent.addGoal(not self.home)
        
        elif result == "win" and self.parent.opponentScoredLast5(): # if the team isnt winning by more than two goals (2-1, 3-2), and the opponenet scored in the last 5 minutes, chance to remove opponent goal
            if random.random() < 0.2:
                self.parent.removeGoal(not self.home)
            
        elif result == "lose" and goalDiff == 1: # if the team is losing by one goal, chance to add team goal
            if random.random() < 0.2: 
                self.parent.addGoal(self.home)

        elif result == "draw" and self.parent.getWinThenDraw(True): # if opponent came back to a draw, chance to remove opponent goal
            if random.random() < 0.1: 
                self.parent.removeGoal(not self.home)

        self.parent.closeFunction() 

class Berate():
    def __init__(self, parent):
        self.parent = parent
        self.home = self.parent.home
        self.score = self.parent.score
        self.match = self.parent.match

    def shoutAction(self):
        self.parent.shoutMadeFunction()
        result = self.parent.getCurrResult(self.score)
        goalDiff = self.parent.getGoalDiff(self.score)

        if result == "win":
            if random.random() < 0.5:
                self.parent.removeGoal(not self.home)
                self.match.setRatingsDecay("home" if self.home else "away")

        elif result == "draw" and self.parent.getWinThenDraw(True):
            if random.random() < 0.1:
                self.parent.addGoal(self.home)

        elif result == "lose"and goalDiff >= 2:
            if random.random() < 0.1: 
                self.parent.addGoal(self.home)

        self.parent.closeFunction()

SHOUT_CLASSES = {
    "Encourage": Encourage,
    "Praise": Praise,
    "Focus": Focus,
    "Berate": Berate
}