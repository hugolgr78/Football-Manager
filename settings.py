import random

APP_SIZE = (1200, 700)
DARK_GREY = "#3b3b3b"
TKINTER_BACKGROUND = "#2b2b2b"
GREY = "#73696c"
GREY_BACKGROUND = "#333333"
CLOSE_RED = "#8a0606"
UNDERLINE_BLUE = "#1276ed"

PIE_RED = "#d61c0f"
PIE_GREY = "#b3b3b3"
PIE_GREEN = "#64e80c"

MORALE_GREEN = "#509917"
MORALE_YELLOW = "#dde20a"
MORALE_RED = "#c90d11"

INJURY_RED = "#ef4e42"

APP_BLUE = "#443de1"

APP_FONT = "Arial"
APP_FONT_BOLD = "Arial Bold"

TABLE_COLOURS = ["#C0392B", "#27AE60", "#2980B9", "#8E44AD", "#D35400", "#16A085", "#F39C12", "#E74C3C", "#3498DB", "#9B59B6", "#2ECC71", "#E67E22", "#1ABC9C", "#F1C40F", "#E74C3C", "#2980B9", "#8E44AD", "#27AE60", "#C0392B", "#D35400", "#9B59B6", "#2ECC71", "#E67E22", "#16A085"]

Europe = [
    "Albania", "Andorra", "Austria", "Belgium", 
    "Bosnia and Herzegovina", "Bulgaria", "Croatia", "Czech Republic", "Denmark", 
    "Estonia", "Finland", "France", "Germany", "Greece", 
    "Hungary", "Iceland", "Ireland", "Italy", "Latvia", 
    "Lithuania", "Luxembourg", "Malta", "Moldova", "Montenegro", 
    "Netherlands", "North Macedonia", "Norway", "Poland", "Portugal", 
    "Romania", "Serbia", "Slovakia", "Slovenia", "Spain", 
    "Sweden", "Switzerland", "Turkey", "Ukraine", "United Kingdom"
]

Africa = [
    "Algeria", "Cameroon", "Egypt", "Ethiopia", "Ghana", 
    "Ivory Coast", "Kenya", "Morocco", "Nigeria", "South Africa"
]

Americas = [
    "Argentina", "Brazil", "Bolivia", "Canada", "Chile", 
    "Colombia", "Ecuador", "Mexico", "Peru", "United States", 
    "Uruguay", "Venezuela"
]

Asia = [
    "China", "India", "Indonesia", "Iran", "Japan", 
    "Malaysia", "Saudi Arabia", "South Korea", "Thailand", "Vietnam",
    "Philippines"
]

continents = [Europe, Africa, Americas, Asia]
continentWeights = {"Europe": 0.7, "Africa": 0.05, "North/South America": 0.2, "Asia": 0.05}

mainCountries = ["France", "Germany", "Italy", "Netherlands", "Spain", "United Kingdom"]
westernEurope = ["Austria", "Belgium", "Denmark", "Finland", "Ireland", "Norway", "Portugal", "Sweden", "Switzerland"]
smallCountries = ["Andorra", "Luxembourg", "Malta", "Iceland"]
europeWeights = {
    country: 0.6 if country in mainCountries else (0.2 if country in westernEurope else (0.1 if country in smallCountries else 0.1))
    for country in Europe
}
africaWeights = {country: 0.1 for country in Africa}
americasWeights = {country: 0.083 for country in Americas}
asiaWeights = {country: 0.091 for country in Asia}

# Combining everything
COUNTRIES = {
    "Europe": (continentWeights["Europe"], europeWeights),
    "Africa": (continentWeights["Africa"], africaWeights),
    "North/South America": (continentWeights["North/South America"], americasWeights),
    "Asia": (continentWeights["Asia"], asiaWeights)
}

POSITION_CODES = {
    "Goalkeeper": "GK",
    "Left Back": "LB",
    "Right Back": "RB",
    "Center Back Right": "CB",
    "Center Back": "CB",
    "Center Back Left": "CB",
    "Defensive Midfielder": "DM",
    "Defensive Midfielder Right": "DM",
    "Defensive Midfielder Left": "DM",
    "Left Midfielder": "LM",
    "Central Midfielder Right": "CM",
    "Central Midfielder": "CM",
    "Central Midfielder Left": "CM",
    "Right Midfielder": "RM",
    "Left Winger": "LW",
    "Right Winger": "RW",
    "Attacking Midfielder": "AM",
    "Center Forward": "CF",
    "Striker Left": "CF",
    "Striker Right": "CF",
}

POSITIONS_PITCH_POSITIONS = {
    "Goalkeeper": (0.5, 0.9),  # Goalkeeper
    "Left Back": (0.15, 0.75),  # Left Back
    "Right Back": (0.85, 0.75),  # Right Back
    "Center Back Right": (0.675, 0.75),  # Center Back Right
    "Center Back": (0.5, 0.75),  # Center Back
    "Center Back Left": (0.325, 0.75),  # Center Back Left
    "Defensive Midfielder": (0.5, 0.6),  # Defensive Midfielder
    "Defensive Midfielder Right": (0.65, 0.6),  # Defensive Midfielder Right
    "Defensive Midfielder Left": (0.35, 0.6),  # Defensive Midfielder Left
    "Left Midfielder": (0.15, 0.45),  # Left Midfielder
    "Central Midfielder Right": (0.65, 0.45),  # Center Midfielder Right
    "Central Midfielder": (0.5, 0.45),  # Center Midfielder
    "Central Midfielder Left": (0.35, 0.45),  # Center Midfielder Left
    "Right Midfielder": (0.85, 0.45),  # Right Midfielder
    "Left Winger": (0.15, 0.3),  # Left Winger
    "Right Winger": (0.85, 0.3),  # Right Winger
    "Attacking Midfielder": (0.5, 0.3),  # Attacking Midfielder
    "Striker Left": (0.3, 0.15),  # Striker Left
    "Striker Right": (0.7, 0.15),  # Striker Right
    "Center Forward": (0.5, 0.1),  # Center Forward
}

RELATED_POSITIONS = {
    "Central Midfielder": ["Central Midfielder Right", "Central Midfielder Left"],
    "Central Midfielder Right": ["Central Midfielder"],
    "Central Midfielder Left": ["Central Midfielder"],
    "Defensive Midfielder": ["Defensive Midfielder Right", "Defensive Midfielder Left"],
    "Defensive Midfielder Right": ["Defensive Midfielder"],
    "Defensive Midfielder Left": ["Defensive Midfielder"],
}

FORMATIONS_CHANCES = {
    "4-4-2": 0.2,
    "4-3-3": 0.5,
    "4-5-1": 0.1,
    "3-4-3": 0.2,
}

FORMATIONS_POSITIONS = {
    "4-4-2": ["Goalkeeper", "Right Back", "Center Back Right", "Center Back Left", "Left Back", "Defensive Midfielder", "Central Midfielder", "Left Midfielder", "Right Midfielder", "Striker Left", "Striker Right"],
    "4-3-3": ["Goalkeeper", "Right Back", "Center Back Right", "Center Back Left", "Left Back", "Central Midfielder", "Left Midfielder", "Right Midfielder", "Left Winger", "Right Winger", "Center Forward"],
    "4-5-1": ["Goalkeeper", "Right Back", "Center Back Right", "Center Back Left", "Left Back", "Defensive Midfielder Right", "Defensive Midfielder Left", "Central Midfielder", "Left Midfielder", "Right Midfielder", "Center Forward"],
    "3-4-3": ["Goalkeeper", "Right Back", "Center Back", "Left Back", "Defensive Midfielder", "Central Midfielder", "Left Midfielder", "Right Midfielder", "Left Winger", "Right Winger", "Center Forward"],
}

DEFENSIVE_POSITIONS = ["Right Back", "Center Back Right", "Center Back", "Center Back Left", "Left Back"]
MIDFIELD_POSITIONS = ["Defensive Midfielder", "Central Midfielder", "Left Midfielder", "Right Midfielder", "Defensive Midfielder Right", "Defensive Midfielder Left"]
ATTACKING_POSITIONS = ["Left Winger", "Right Winger", "Attacking Midfielder", "Striker Left", "Striker Right", "Center Forward"]

SCORER_CHANCES = {
    'defender': 0.05,
    'midfielder': 0.25,
    'forward': 0.7
}

GOAL_TYPE_CHANCES = {
    "goal": 0.8,
    "penalty": 0.15,
    "own_goal": 0.05
}

PENALTY_SCORE_CHANCE = 0.8

OWN_GOAL_CHANCES = {
    'goalkeeper': 0.1,
    'defender': 0.8,
    'midfielder': 0.05,
    'forward': 0.05
}

ASSISTER_CHANCES = {
    'goalkeeper': 0.01,
    'defender': 0.3,
    'midfielder': 0.49,
    'forward': 0.2
}

PENALTY_TAKER_CHANCES = {
    'goalkeeper': 0.01,
    'defender': 0.05,
    'midfielder': 0.2,
    'forward': 0.74
}

RED_CARD_CHANCES = {
    'goalkeeper': 0.1,
    'defender': 0.05,
    'midfielder': 0.05,
    'forward': 0.8
}

INJURY_CHANCE = 0.1 # chance for a team to get an injury in a match

MATCHDAY_SUBS = 7
MAX_SUBS = 5

SHOUTS = ["Encourage", "Praise", "Focus", "Berate"]

OBJECTIVES = {
    (200, 190): "fight for the title",
    (189, 175): "finish in the top half",
    (174, 162): "avoid relegation",
}

def get_objective_for_level(level):
    for (max_level, min_level), objective in OBJECTIVES.items():
        if min_level <= level <= max_level:
            return objective
    return "no specific objective" 

def generate_lower_div_objectives(min_level, max_level):
    range_size = (max_level - min_level) // 3
    return {
        (max_level, max_level - range_size): "secure promotion",
        (max_level - range_size - 1, max_level - 2 * range_size): "finish in the top half",
        (max_level - 2 * range_size - 1, min_level): "avoid relegation",
    }

GOAL_RATINGS = [1.00, 1.12, 1.05, 1.15, 1.07, 1.01, 1.04, 1.11]
PENALTY_GOAL_RATINGS = [0.75, 0.78, 0.82, 0.84, 0.90, 0.94, 1.03, 1.08]
PENALTY_MISS_RATINGS = [-0.32, -0.42, -0.47, -0.51, -0.57, -0.63, -0.66, -0.72]
YELLOW_CARD_RATINGS = [-0.21, -0.28, -0.32, -0.37, -0.41, -0.45, -0.49, -0.53]
RED_CARD_RATINGS = [-1.46, -1.49, -1.52, -1.57, -1.60, -1.63, -1.69, -1.78]
ASSIST_RATINGS = [0.52, 0.58, 0.65, 0.69, 0.73, 0.78, 0.82, 0.86]
DEFENDER_GOALS_1 = [0.32, 0.42, 0.47, 0.63, 0.69, 0.78, 0.85, 0.98]
DEFENDER_GOALS_3 = [0.02, 0.08, 0.15, 0.19, 0.24, 0.29, 0.36, 0.45]
DEFENDER_GOALS_MORE = [0.89, 0.92, 0.97, 1.03, 1.09, 1.15, 1.22, 1.29]
NON_SCORER_RATINGS = [-0.56, -0.43, -0.32, -0.21, -0.19, 0.05, 0.09, 0.13, 0.17, 0.24, 0.31, 0.46, 0.49, 0.67]

EVENT_RATINGS = {
    "goal": GOAL_RATINGS,
    "penalty_goal": PENALTY_GOAL_RATINGS,
    "penalty_miss": PENALTY_MISS_RATINGS,
    "yellow_card": YELLOW_CARD_RATINGS,
    "red_card": RED_CARD_RATINGS
}

FAN_REACTIONS = {
    "big_win":     ["Ecstatic", "Very Happy", "Happy", "Very Happy", "Ecstatic"],
    "win":         ["Neutral", "Happy", "Happy", "Very Happy", "Ecstatic"],
    "draw":        ["Angry", "Neutral", "Neutral", "Happy", "Very Happy"],
    "loss":        ["Furious", "Angry", "Neutral", "Neutral", "Neutral"],
    "big_loss":    ["Furious_2", "Furious", "Angry", "Angry", "Neutral"],
    "emb_loss":    ["Riot Mode", "Furious_2", "Furious", "Furious", "Angry"]
}

EXPECTATION_LEVELS = ["Clear Favorite", "Slight Favorite", "Even Match", "Slight Underdog", "Clear Underdog"]

TEAM_EXPECTATIONS = {
    range(9, 100): "Clear Favorite",   # Team is much stronger
    range(5, 9): "Slight Favorite",    # Team is slightly stronger
    range(-4, 5): "Even Match",        # Teams are evenly matched
    range(-8, -4): "Slight Underdog",  # Team is slightly weaker
    range(-100, -8): "Clear Underdog"  # Team is much weaker
}

RESULT_CATEGORIES = {
    "win": {
        range(4, 100): "big_win",     # Won by 4+ goals
        range(1, 4): "win",           # Won by 1-3 goals
    },
    "draw": {
        range(0, 1): "draw"           # A draw always has GD = 0
    },
    "loss": {
        range(-3, 0): "loss",         # Lost by 1-3 goals
        range(-6, -3): "big_loss",    # Lost by 4-6 goals
        range(-10, -6): "emb_loss",   # Lost by 7-9 goals
        range(-100, -10): "riot_loss" # Lost by 10+ goals (fans furious)
    }
}

FAN_MESSAGES = {
    "Ecstatic": "It was an unforgettable performance, and the fans are \nabsolutely ecstatic with the result!",
    "Very Happy": "The team delivered a great result, and the fans are \nthrilled with the performance.",
    "Happy": "This was a solid result, and the fans are pleased with \nthe team's efforts.",
    "Neutral": "It was a decent performance, but nothing too special. \nThe fans are neither excited nor disappointed.",
    "Angry": "It was a frustrating result, and the fans expected much \nbetter from the team.",
    "Furious": "The performance was unacceptable, and the fans are \nabsolutely furious about the outcome.",
    "Furious_2": "The fans are outraged by the team's display and are \ndemanding serious improvements.",
    "Riot Mode": "Chaos has erupted among the supporters! The fans have \ncompletely lost it, and protests are breaking out."
}

def get_fan_reaction(result, expectation):
    """ Get the fan reaction based on match result and expectation level. """

    index = EXPECTATION_LEVELS.index(expectation)
    return FAN_REACTIONS.get(result, ["Unknown"] * 5)[index]

def get_expectation(team_level, opponent_level):
    """Determine expectation level based on team level difference."""
    level_diff = team_level - opponent_level
    for diff_range, expectation in TEAM_EXPECTATIONS.items():
        if level_diff in diff_range:
            return expectation
    return "Even Match"

def get_result_category(game_result, goal_difference):
    """Determine result category based on game result and goal difference."""

    for gd_range, category in RESULT_CATEGORIES[game_result].items():
        if goal_difference in gd_range:
            return category

    return "unknown"  # Default case (should never happen)

def get_fan_message(fan_reaction):
    """Return a fan reaction message based on the given fan reaction."""
    return FAN_MESSAGES.get(fan_reaction, "The fans aren't sure how to react.")

def get_player_ban(ban_type):
    if ban_type == "injury":
        ban = random.randint(1, 15)
    else: # red card
        ban = random.randint(1,3)

    return ban

# Normal scenario
LOW_YELLOW_CARD = [0.7, 0.2, 0.1]
LOW_RED_CARD = [0.95, 0.05]

MEDIUM_YELLOW_CARD = [0.6, 0.2, 0.1, 0.1]
MEDIUM_RED_CARD = [0.88, 0.08, 0.03]

HIGH_YELLOW_CARD = [0.5, 0.3, 0.1, 0.05, 0.05]
HIGH_RED_CARD = [0.84, 0.1, 0.05, 0.01]

# Extra yellows scenario
YELLOWS_EXTRA = [0.1] * 10

# 100% red card scenario
RED_100 = [1.0]

def get_morale_change(match_result, player_rating, goal_difference):
    # Base morale change based on match result
    if match_result == "win":
        base_morale = 5
    elif match_result == "draw":
        base_morale = 1
    else:  # loss
        base_morale = -5
    
    # Adjust based on player rating (ratings above 7 improve morale, below 7 decrease it)
    rating_factor = (player_rating - 7) * 0.5
    
    # Adjust based on goal difference (larger goal difference in favor of the team increases morale)
    goal_diff_factor = goal_difference * 0.5
    
    # Calculate final morale change and limit it between -10 and 10
    final_morale_change = round(base_morale + rating_factor + goal_diff_factor)
    final_morale_change = max(-10, min(10, final_morale_change))
    
    return final_morale_change

def get_morale_decrease_role(player):
    role = player.player_role

    if role == "Star player":
        return -5
    elif role == "First Team":
        return -3
    elif role == "Rotation":
        return -1
    
    return 0 # Backup keepers and youth players

INTRODUCTORY_TEXTS = [
    "Hey Boss, what did you want to see me for?",
    "Gaffer, everything alright? What’s on your mind?",
    "Coach, you wanted to speak to me?",
    "Boss, I wasn’t expecting this. What’s up?",
    "Hey Boss, is something up?"
]

CONGRATULATE = "I just wanted to say, fantastic job out there!\nYou were outstanding, and your effort made a\nreal difference. Keep it up!"
INJURY = "I know injuries are tough, but don’t let this get\nyou down. Focus on your recovery, and we’ll be here\nto support you every step of the way. You’ll\ncome back even stronger!"
CRITIZE = "I have to be honest with you — your performance\nwasn’t up to the standard I expect. I know you can do\nbetter, and I need you to step up next time. Let’s\nwork on what went wrong and put things right."
MOTIVATE = "I know you’ve got more to give, and I want to see\nthat hunger in the next match. You’ve got the\ntalent — now go out there and prove it to everyone!"

PROMPT_TO_TEXT = {
    "Congratulate": CONGRATULATE,
    "Injury": INJURY,
    "Criticize": CRITIZE,
    "Motivate": MOTIVATE
}

def get_player_response(prompt, rating, is_injured):
    responses = {
        "Congratulate": {
            "accept": [
                "Thanks, Boss! Means a lot coming from you.",
                "Appreciate that, Coach! I'll keep giving my best."
            ],
            "challenge": [
                "I think I could have done even better, to be honest.",
                "Glad you think so, but I know I’ve got more in me."
            ]
        },
        "Injury": {
            "thankful": [
                "Thanks, Boss. I really needed that.",
                "Appreciate it, Coach. I'll do everything to come back stronger."
            ],
            "confused": [
                "Wait, am I injured? Did I miss something?",
                "Uh... I’m not injured, Boss. Is there something wrong?"
            ]
        },
        "Criticize": {
            "accept": [
                "You're right, Boss. I need to step up.",
                "I know I wasn’t good enough. I’ll work harder."
            ],
            "challenge": [
                "I don’t think I was that bad, to be honest.",
                "I see where you’re coming from, but I disagree."
            ]
        },
        "Motivate": {
            "accept": [
                "I hear you, Boss. I’ll push myself harder.",
                "Got it, Coach! I’ll prove myself."
            ],
            "challenge": [
                "I’m already giving my all, Boss. What more do you want?",
                "I thought I played well, but I guess I’ll try harder."
            ]
        }
    }
    
    if prompt == "Congratulate":
        response_type = "accept" if rating >= 7.5 else "challenge"
        accepted = response_type == "accept"
    elif prompt == "Injury":
        response_type = "thankful" if is_injured else "confused"
        accepted = response_type == "thankful"
    elif prompt == "Criticize":
        response_type = "accept" if rating < 5.5 else "challenge"
        accepted = response_type == "accept"
    elif prompt == "Motivate":
        response_type = "accept" if rating < 7.5 else "challenge"
        accepted = response_type == "accept"
    else:
        return "I’m not sure what to say to that, Boss."
    
    return random.choice(responses[prompt][response_type]), accepted

ATTACK_STATS = ["Attack", "Goals scored", "Penalties scored", "Goals scored in the first 15", "Goals scored in the last 15", "Goals by substitutes", "Fastest goal scored", "Latest goal scored"]
DEFENSIVE_STATS = ["Defense", "Yellow cards", "Red cards", "Clean sheets", "Goals conceeded", "Own goals", "Penalties saved", "Goal conceeded in the first 15", "Goal conceeded in the last 15", "Fastest goal conceeded", "Latest goal conceeded"]
MISC_STATS = ["Misc", "Goal difference", "Winning from losing position", "Losing from winning position", "Biggest win", "Biggest loss", "Home performance", "Away performance"]
STREAK_STATS = ["Streaks", "Longest unbeaten run", "Longest winning streak", "Longest losing streak", "Longest winless streak"]

TEAM_STATS = [ATTACK_STATS, DEFENSIVE_STATS, MISC_STATS, STREAK_STATS]

from data.database import StatsManager

STAT_FUNCTIONS = {
    "Goals scored": StatsManager.get_goals_scored,
    "Penalties scored": StatsManager.get_penalties_scored,
    "Goals scored in the first 15": StatsManager.get_goals_scored_in_first_15,
    "Goals scored in the last 15": StatsManager.get_goals_scored_in_last_15,
    "Goals by substitutes": StatsManager.get_goals_by_substitutes,
    "Fastest goal scored": StatsManager.get_fastest_goal_scored,
    "Latest goal scored": StatsManager.get_latest_goal_scored,
#     "Yellow cards": StatsManager.get_yellow_cards,
#     "Red cards": StatsManager.get_red_cards,
#     "Clean sheets": StatsManager.get_clean_sheets,
#     "Goals conceeded": StatsManager.get_goals_conceeded,
#     "Own goals": StatsManager.get_own_goals,
#     "Penalties saved": StatsManager.get_penalties_saved,
#     "Goal conceeded in the first 15": StatsManager.get_goals_conceeded_in_first_15,
#     "Goal conceeded in the last 15": StatsManager.get_goals_conceeded_in_last_15,
#     "Fastest goal conceeded": StatsManager.get_fastest_goal_conceeded,
#     "Latest goal conceeded": StatsManager.get_latest_goal_conceeded,
#     "Goal difference": StatsManager.get_goal_difference,
#     "Winning from losing position": StatsManager.get_winning_from_losing_position,
#     "Losing from winning position": StatsManager.get_losing_from_winning_position,
#     "Biggest win": StatsManager.get_biggest_win,
#     "Biggest loss": StatsManager.get_biggest_loss,
#     "Home performance": StatsManager.get_home_performance,
#     "Away performance": StatsManager.get_away_performance,
#     "Longest unbeaten run": StatsManager.get_longest_unbeaten_run,
#     "Longest winning streak": StatsManager.get_longest_winning_streak,
#     "Longest losing streak": StatsManager.get_longest_losing_streak,
#     "Longest winless streak": StatsManager.get_longest_winless_streak
}