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
    'goalkeeper': 0.01,
    'defender': 0.049,
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
PENALTY_MISS_RATINGS = [0.32, 0.42, 0.47, 0.51, 0.57, 0.63, 0.66, 0.72]
YELLOW_CARD_RATINGS = [0.21, 0.28, 0.32, 0.37, 0.41, 0.45, 0.49, 0.53]
RED_CARD_RATINGS = [1.46, 1.49, 1.52, 1.57, 1.60, 1.63, 1.69, 1.78]
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