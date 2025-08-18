from settings import *
from data.database import *
from data.gamesDatabase import *
from utils.util_functions import *

class Score():
    def __init__(self, homeTeam, awayTeam, homeLineup, awayLineup):
    
        self.homeTeam = homeTeam
        self.awayTeam = awayTeam
        self.homeLineup = homeLineup
        self.awayLineup = awayLineup

        self.homeLevel = Teams.get_team_average_current_ability(self.homeTeam.id)
        self.awayLevel = Teams.get_team_average_current_ability(self.awayTeam.id)

        self.score = []
        self.winner = None

        self.decideWinner()
        self.generateScore()

    ## This function will need to append the level of each team based on the many factors that can affect it (morale, form, etc.)
    def decideWinner(self, advantage = True):
        if advantage: # home advantage
            homeAdvantage = 5  # Define the home advantage
            levelDiff = self.awayLevel - (self.homeLevel + homeAdvantage)  # Add the home advantage to team1's level
        else:
            levelDiff = self.awayLevel - self.homeLevel

        probDraw = self.getProbability(abs(levelDiff), "draw") # get the probability of a draw

        if levelDiff < 0:  # team1 has a higher level
            probTeam1 = self.getProbability(-levelDiff, "win")
            probTeam2 = 1 - probDraw - probTeam1
        else:  # team2 has a higher level or levels are equal
            probTeam2 = self.getProbability(levelDiff, "win")
            probTeam1 = 1 - probDraw - probTeam2

        rand_num = random.random() # generate a random number between 0 and 1

        # if the random number is less than the probability of team1 winning, team1 wins
        if rand_num < probTeam1:
            self.winner = self.homeTeam
        elif rand_num < probTeam1 + probDraw: # if the random number is less than the probability of a draw and team 1 winning, it's a draw
            self.winner = None
        else: # else team 2 wins
            self.winner = self.awayTeam
        
        self.winnerLevel = Teams.get_team_average_current_ability(self.winner.id) if self.winner else None
        
    ## This function will probably be left unchanged
    def getProbability(self, levelDiff, probType):
        # Define the points to interpolate between
        points = [(0, 33.3, 33.3), (10, 25, 60), (20, 15, 75), (30, 15, 70), (40, 10, 80), (50, 5, 90), (60, 2, 95), (70, 1, 98), (80, 0.5, 99), (90, 0.25, 99.5)]

        # Find the interval that level_diff falls into
        for i in range(len(points) - 1):
            x1, y1, z1 = points[i]
            x2, y2, z2 = points[i + 1]
            if x1 <= levelDiff < x2:
                # Linearly interpolate between the two points
                if probType == "draw":
                    return ((y2 - y1) * (levelDiff - x1) / (x2 - x1) + y1) / 100
                elif probType == "win":
                    return ((z2 - z1) * (levelDiff - x1) / (x2 - x1) + z1) / 100

        # If level_diff is greater than the largest x-value, return the y-value or z-value of the last point
        x, y, z = points[-1]
        if probType == "draw":
            return y / 100
        elif probType == "win":
            return z / 100

    ## Might change how the scores are generated
    def generateScore(self):

        levelDiff = abs(self.awayLevel - self.homeLevel)

        if self.winner == None:
            # If it's a draw, both teams score the same number of goals
            goalChoices = [0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 4, 5]
            goals = random.choice(goalChoices)
            self.score = [goals, goals]

            return

        losingTeam = self.homeTeam if self.winner == self.awayTeam else self.awayTeam

        # Check if the winning team has a lower level as if it does, it should realistically not score many goals
        if self.winnerLevel < Teams.get_team_average_current_ability(losingTeam.id):
            # Limit the maximum number of goals that the winning team can score
            winningGoalsChoices = [1, 2, 2, 2, 3, 3]
            losingGoalsChoices = [0, 1, 1, 1, 2]
        else:
            # Use different lists for winningGoalsChoices based on the level difference (the higher the difference, the possibility to score a lot of goals)
            if levelDiff < 10:
                winningGoalsChoices = [1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3]
                losingGoalsChoices = [0, 1, 1, 2]
            elif levelDiff <= 20:
                winningGoalsChoices = [1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 4]
                losingGoalsChoices = [0, 1, 1, 2, 2, 3]
            elif levelDiff < 30:
                winningGoalsChoices = [2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 4, 4, 5]
                losingGoalsChoices = [0, 0, 0, 1, 1, 2, 2]
            elif levelDiff > 100:
                winningGoalsChoices = [5, 5, 5, 5, 6, 6, 6, 7, 7]
                losingGoalsChoices = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]
            else:
                winningGoalsChoices = [2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 5, 6, 7, 7]
                losingGoalsChoices = [0, 0, 0, 1, 1, 2]
    
        # get the score
        winningGoals = random.choice(winningGoalsChoices)
        losingGoals = random.choice(losingGoalsChoices)

        # if the goals scored by the losing team is more than the winning team, get a score until it isn't
        while losingGoals >= winningGoals:
            losingGoals = random.choice(losingGoalsChoices)
    
        self.score = [winningGoals if self.winner == self.homeTeam else losingGoals, winningGoals if self.winner == self.awayTeam else losingGoals]

    def getScore(self):
        return self.score
    
    def getWinner(self):
        return self.winner
    
    def appendScore(self, value, home):
        if home:
            self.score[0] += value
        else:
            self.score[1] += value