import datetime

APP_SIZE = (1200, 700)
DARK_GREY = "#3b3b3b"
TKINTER_BACKGROUND = "#2b2b2b"
GREY = "#73696c"
GREY_BACKGROUND = "#333333"
CLOSE_RED = "#8a0606"
UNDERLINE_BLUE = "#1276ed"

DELIGHTED_COLOR = "#4CAF50"  
HAPPY_COLOR = "#8BC34A"      
NEUTRAL_COLOR = "#FFC107"    
FRUSTRATED_COLOR = "#FF9800" 
ANGRY_COLOR = "#F44336"   

PIE_RED = "#d61c0f"
PIE_GREY = "#b3b3b3"
PIE_GREEN = "#64e80c"

MORALE_GREEN = "#509917"
MORALE_YELLOW = "#dde20a"
MORALE_RED = "#c90d11"

INJURY_RED = "#ef4e42"

APP_BLUE = "#443de1"
POTM_BLUE = "#1e90ff"

APP_FONT = "Arial"
APP_FONT_BOLD = "Arial Bold"

TABLE_COLOURS = ["#C0392B", "#27AE60", "#2980B9", "#8E44AD", "#D35400", "#16A085", "#F39C12", "#E74C3C", "#3498DB", "#9B59B6", "#2ECC71", "#E67E22", "#1ABC9C", "#F1C40F", "#E74C3C", "#2980B9", "#8E44AD", "#27AE60", "#C0392B", "#D35400", "#9B59B6", "#2ECC71", "#E67E22", "#16A085"]

SEASON_START_DATE = datetime.datetime(2025, 8, 10, 7, 0, 0, 0)

TOTAL_STEPS = 2111
PROGRESS = 0

PLANETS = ["Cryon", "Vorlis", "Zephyra", "Tauron", "Nerath", "Ecliptis", "Lyra", "Solara"]

PLANET_DESCRIPTIONS = {
    "Cryon": "Cryon is a frozen\nworld of endless ice\nplains and shimmering\nglaciers. Vast crystal\nformations stretch\nbeneath pale blue\nskies, and ancient\nstorms sculpt the\nfrozen surface into\never-changing\npatterns of frost.",
    "Vorlis": "Vorlis burns beneath\na crimson haze, its\nsurface split by\nrivers of lava and\nvolcanic spires. The\nair is thick with ash,\nand the ground\ntrembles with the\nheartbeat of the\nplanet’s molten\ncore.",
    "Zephyra": "Zephyra is a gas\ngiant where colossal\ncloud continents drift\nthrough violet skies.\nWinds coil and twist\nendlessly, forming\nluminous tempests\nthat dance around\nfloating cities\nsuspended in the\nupper atmosphere.",
    "Tauron": "Tauron is a\nmountainous planet\ncarved by time and\nweather. Towering\npeaks pierce the\nclouds, while valleys\necho with distant\navalanches. Ancient\nstone citadels cling\nto cliffs above\nroaring winds.",
    "Nerath": "Nerath is an ocean\nworld, its surface a\nvast expanse of deep\nblue water. Islands\nrise like emerald\njewels amid the sea,\nand bioluminescent\nlife glows beneath\nits tranquil waves,\nlighting the abyss\nbelow.",
    "Ecliptis": "Ecliptis orbits two\ndying stars, forever\nlocked in twilight.\nEmerald auroras\nshimmer across the\nskies, and the land\nglows faintly from\ncrystalline minerals\nthat absorb the\nscarce light\nreaching the\nsurface.",
    "Lyra": "Lyra resonates with\ncolor and sound, its\natmosphere alive\nwith harmonic\nenergy. The air\nhums softly, and\ncrystalline flora\nrespond to tones.\nCities shimmer like\nprisms under a sky\nthat sings with\nliving light.",
    "Solara": "Solara blazes with\nradiant intensity,\nits surface a land\nof golden deserts\nand luminous\nstorms. Energy flows\nthrough the air,\nlighting the horizon\nin arcs that paint\nthe world in dawn."
}

PLANET_LEAGUES = {
    "Cryon": ["Cryonese Primera", "Cryonese Segunda", "Cryonese Tercera", "Cryonese Cuarta"],
    "Vorlis": ["Vorlis Liga", "Vorlis National", "Vorlis Continental", "Vorlis Regional"],
    "Zephyra": ["Zephyra Pro", "Zephyra Challenge", "Zephyra Series", "Zephyra B"],
    "Tauron": ["Tauron Premier", "Tauron Elite", "Tauron Division 2", "Tauron Division 3"],
    "Nerath": ["Nerathoul", "Nerathoul Prime", "Nerathoul Ascend", "Nerathoul Minor"],
    "Ecliptis": ["Ecliptus", "Ecliptus B", "Ecliptus C", "Ecliptus D"],
    "Lyra": ["Lyraxis", "Lyraxis Nova", "Lyraxis Minor", "Lyraxis Rising"],
    "Solara": ["Solarion", "Solarion 2", "Solarion 3", "Solarion 4"]
}

STATES = ["preview", "matchday", "review"]

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

REVERSE_POSITION_CODES = {}
for full, code in POSITION_CODES.items():
    REVERSE_POSITION_CODES.setdefault(code, []).append(full)

POSITION_ORDER = {
    "goalkeeper": 0,
    "defender": 1,
    "midfielder": 2,
    "forward": 3
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

COMPATIBLE_POSITIONS = {
    "CB": ["CB", "LB", "RB", "DM"],
    "LB": ["LB", "CB", "LM"],
    "RB": ["RB", "CB", "RM"],
    "DM": ["DM", "CM", "CB"],
    "CM": ["CM", "DM", "AM"],
    "AM": ["AM", "CM", "ST"],
    "LM": ["LM", "LW", "CM"],
    "RM": ["RM", "RW", "CM"],
    "LW": ["LW", "LM", "ST"],
    "RW": ["RW", "RM", "ST"],
    "ST": ["ST", "AM", "LW", "RW"],
}

POSITIONS_MAX = {
    "CB": 3,
    "DM": 3,
    "CM": 3,
    "CF": 3
}

RELATED_POSITIONS = {
    "Central Midfielder": ["Central Midfielder Right", "Central Midfielder Left"],
    "Central Midfielder Right": ["Central Midfielder"],
    "Central Midfielder Left": ["Central Midfielder"],
    "Defensive Midfielder": ["Defensive Midfielder Right", "Defensive Midfielder Left"],
    "Defensive Midfielder Right": ["Defensive Midfielder"],
    "Defensive Midfielder Left": ["Defensive Midfielder"],
}

FORMATIONS_POSITIONS = {
    "4-4-2 CM": ["Goalkeeper", "Right Back", "Center Back Right", "Center Back Left", "Left Back",
              "Defensive Midfielder", "Central Midfielder", "Left Midfielder", "Right Midfielder",
              "Striker Left", "Striker Right"],

    "4-4-2 DM": ["Goalkeeper", "Right Back", "Center Back Right", "Center Back Left", "Left Back",
            "Defensive Midfielder Right",
            "Left Midfielder", "Defensive Midfielder Left", "Right Midfielder",
            "Striker Left", "Striker Right"],

    "4-3-3 CM": ["Goalkeeper", "Right Back", "Center Back Right", "Center Back Left", "Left Back",
                 "Left Midfielder", "Central Midfielder", "Right Midfielder",
                 "Left Winger", "Right Winger", "Center Forward"],

    "4-3-3 DM": ["Goalkeeper", "Right Back", "Center Back Right", "Center Back Left", "Left Back",
                 "Defensive Midfielder Left", "Central Midfielder", "Defensive Midfielder Right",
                 "Left Winger", "Right Winger", "Center Forward"],

    "3-3-4": ["Goalkeeper", "Right Back", "Center Back", "Left Back",
              "Defensive Midfielder", "Left Midfielder", "Right Midfielder",
              "Left Winger", "Right Winger", "Striker Left", "Striker Right"],

    "3-4-3": ["Goalkeeper", "Right Back", "Center Back", "Left Back",
              "Defensive Midfielder", "Central Midfielder", "Left Midfielder", "Right Midfielder",
              "Left Winger", "Right Winger", "Center Forward"],

    "4-2-4": ["Goalkeeper", "Right Back", "Center Back Right", "Center Back Left", "Left Back",
              "Defensive Midfielder Right", "Defensive Midfielder Left",
              "Left Winger", "Right Winger", "Striker Left", "Striker Right"],

    "4-5-1 DM": ["Goalkeeper", "Right Back", "Center Back Right", "Center Back Left", "Left Back",
              "Defensive Midfielder Right", "Defensive Midfielder Left", "Central Midfielder",
              "Left Midfielder", "Right Midfielder", "Center Forward"],

    "4-5-1 AM": ["Goalkeeper", "Right Back", "Center Back Right", "Center Back Left", "Left Back",
                "Defensive Midfielder Right", "Defensive Midfielder Left",
                "Left Midfielder", "Attacking Midfielder", "Right Midfielder", "Center Forward"],

    "4-5-1 CM": ["Goalkeeper", "Right Back", "Center Back Right", "Center Back Left", "Left Back",
                "Defensive Midfielder",
                "Left Midfielder", "Central Midfielder Right", "Central Midfielder Left", "Right Midfielder",
                "Center Forward"],

    "3-5-2 CM": ["Goalkeeper", "Right Back", "Center Back", "Left Back",
              "Left Midfielder", "Right Midfielder", "Defensive Midfielder",
              "Central Midfielder Right", "Central Midfielder Left",
              "Striker Left", "Striker Right"],

    "3-5-2 AM": ["Goalkeeper", "Right Back", "Center Back", "Left Back",
                "Left Midfielder", "Right Midfielder", "Defensive Midfielder", "Central Midfielder",
                "Attacking Midfielder", "Striker Left", "Striker Right"],

    "5-3-2": ["Goalkeeper", "Right Back", "Center Back Right", "Center Back", "Center Back Left", "Left Back",
              "Right Midfielder", "Central Midfielder", "Left Midfielder",
              "Striker Left", "Striker Right"],

    "5-4-1": ["Goalkeeper", "Right Back", "Center Back Right", "Center Back", "Center Back Left", "Left Back",
              "Left Midfielder", "Central Midfielder Right", "Central Midfielder Left", "Right Midfielder",
              "Center Forward"],
}

DEFENDER_POSITIONS = ["Right Back", "Center Back Right", "Center Back", "Center Back Left", "Left Back"]
DEFENSIVE_POSITIONS = DEFENDER_POSITIONS + ["Goalkeeper", "Defensive Midfielder", "Defensive Midfielder Right", "Defensive Midfielder Left"]
MIDFIELD_POSITIONS = ["Defensive Midfielder", "Central Midfielder", "Central Midfielder Left", "Central Midfielder Right", "Left Midfielder", "Right Midfielder", "Defensive Midfielder Right", "Defensive Midfielder Left", "Attacking Midfielder"]
FORWARD_POSITIONS = ["Left Winger", "Right Winger", "Striker Left", "Striker Right", "Center Forward"]
ATTACKING_POSITIONS = FORWARD_POSITIONS + ["Attacking Midfielder"]

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

# GOAL_TYPE_CHANCES = {
#     "goal": 0.05,
#     "penalty": 0.15,
#     "own_goal": 0.8
# }

BASE_SHOT = 0.2
MAX_SHOT_PROB = BASE_SHOT + 0.1
BASE_ON_TARGET = 0.6
MAX_TARGET_PROB = BASE_ON_TARGET + 0.1
BASE_GOAL = 0.7
MAX_GOAL_PROB = BASE_GOAL + 0.1

BASE_FOUL = 0.07 
BASE_YELLOW = 0.02 
BASE_RED = 0.001

BASE_INJURY = 0.0005
MAX_INJURY_PROB = 0.0015 # This gives P(X = 1) = 20%, P(X > 1) = 3%

TICK = 30

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
YELLOW_THRESHOLD = 5

SHOUTS = ["Encourage", "Praise", "Focus", "Berate"]

OBJECTIVES = {
    (1, 5): "fight for the title",
    (6, 14): "finish in the top half",
    (15, 20): "avoid relegation",
}

GOAL_RATINGS = (0.7, 1.00)
ASSIST_RATINGS = (0.45, 0.7)
PENALTY_SCORE_RATING = 0.7
PENALTY_MISS_RATING = -0.3
PENALTY_SAVED_RATING = 0.7
OWN_GOAL_RATINGS = (-0.7, -0.4)
YELLOW_CARD_RATINGS = (-0.5, -0.2)
RED_CARD_RATINGS = (-1.5, -1.00)
SAVE_RATING = (0.1, 0.2)
SHOT_RATING = (0.1, 0.2)
SHOT_TARGET_RATING = (0.15, 0.3)
FOUL_RATING = (-0.1, -0.05)
DEFENSIVE_ACTION_RATING = (0.05, 0.1)
BIG_CHANCE_CREATED_RATING = (0.2, 0.4)
BIG_CHANCE_MISSED_RATING = (-0.2, -0.1)
PASS_RATING = (0.005, 0.01)
GOAL_CONCEDED_KEEPER_RATING = (-0.6, -0.3)
GOAL_CONCEDED_DEFENCE_RATING = (-0.3, -0.15)
    
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
    range(10, 200): "Clear Favorite",   # Team is much stronger
    range(5, 10): "Slight Favorite",    # Team is slightly stronger
    range(-5, 5): "Even Match",        # Teams are evenly matched
    range(-10, -5): "Slight Underdog",  # Team is slightly weaker
    range(-200, -10): "Clear Underdog"  # Team is much weaker
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

# Normal scenario
LOW_YELLOW_CARD = [0.7, 0.2, 0.1]
LOW_RED_CARD = [0.95, 0.05]

MEDIUM_YELLOW_CARD = [0.6, 0.2, 0.1, 0.1]
MEDIUM_RED_CARD = [0.895, 0.1, 0.005]

HIGH_YELLOW_CARD = [0.5, 0.3, 0.1, 0.05, 0.05]
HIGH_RED_CARD = [0.894, 0.1, 0.005, 0.001]

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

ATTACK_STATS = ["Attack", "Goals scored", "Penalties scored", "Goals scored in the first 15", "Goals scored in the last 15", "Goals by substitutes", "Fastest goal scored", "Latest goal scored", "Highest Possession", "Lowest Possession", "Highest xG", "Lowest xG"]
DEFENSIVE_STATS = ["Defense", "Goals conceded", "Clean sheets", "Yellow cards", "Red cards", "Own goals", "Penalties saved", "Goal conceded in the first 15", "Goal conceded in the last 15", "Fastest goal conceded", "Latest goal conceded"]
MISC_STATS = ["Misc", "Goal difference", "Winning from losing position", "Losing from winning position", "Biggest win", "Biggest loss", "Home performance", "Away performance"]
STREAK_STATS = ["Streaks", "Longest unbeaten run", "Longest winning streak", "Longest losing streak", "Longest winless streak", "Longest scoring streak", "Longest scoreless streak"]

TEAM_STATS = [ATTACK_STATS, DEFENSIVE_STATS, MISC_STATS, STREAK_STATS]

REACTION_COLOURS = [
    (lambda x: x >= 3, DELIGHTED_COLOR),
    (lambda x: x == 2, HAPPY_COLOR),
    (lambda x: x in (0, 1), NEUTRAL_COLOR),
    (lambda x: x == -1, FRUSTRATED_COLOR),
    (lambda x: x <= -2, ANGRY_COLOR),
]

REACTION_TEXTS = [
    (lambda x: x >= 3, "Ecstatic"),
    (lambda x: x == 2, "Very Happy"),
    (lambda x: x == 1, "Happy"),
    (lambda x: x == 0, "Content"),
    (lambda x: x == -1, "Upset"),
    (lambda x: x <= -2, "Angry"),
]

HALF_TIME_PROMPTS = {
    "Encourage": (
        "Keep your heads up — we’re still in this. One good moment changes everything.",
        "I know it’s tough, but we can turn this around. Let’s show some fight in the second half.",
        "I believe in you. Let’s go out there and show them what we’re made of."
    ),
    "Berate": (
        "Wake up! Some of you look like you don’t even want to be out there.",
        "This is unacceptable. I expect you to show me more in the second half.",
        "You need to do better. I won’t accept this kind of performance."
    ),
    "Neutral": (
        "Decent first half. Let’s stay composed and keep doing the basics right.",
        "We’ve done okay, but we can do better. Let’s keep our focus and finish strong.",
        "We’re in a good position, but we can’t let our guard down. Let’s keep pushing."
    ),
    "Happy": (
        "Good first half, lads. Let’s keep it going and finish the job.",
        "I’m pleased with that performance. Let’s keep the momentum going in the second half.",
        "Solid first half. Let’s build on this and secure the win."
    ),
    "Dissapointed": (
        "I expected more from you boys. Let’s put it right in the second half.",
        "We need to step it up. I want to see more fight and determination in the second half.",
        "This isn’t good enough. I need to see a reaction in the second half."
    )
}

PROMPT_REACTIONS = {
    "Encourage": {"win": -1 , "draw": 0, "lose": 1},
    "Berate": {"win": -2, "draw": -1, "lose": 1},
    "Neutral": {"win": 0, "draw": 1, "lose": 0},
    "Happy": {"win": 1, "draw": 0, "lose": -1},
    "Dissapointed": {"win": -1, "draw": 0, "lose": 1}
}

SEARCH_LIMIT = 12

EVENTS_TO_ICONS = {
    "substitution": "Sub",
    "goal": "Goals",
    "penalty_goal": "Goals",
    "own_goal": "Goals",
    "penalty_saved": "Goals",
    "assist": "Assists",
    "yellow_card": "Cards",
    "red_card": "Cards",
    "penalty_miss": "Missed Pens"
}

goal_group = ["goal", "penalty_goal", "own_goal", "penalty_saved"]
card_group = ["yellow_card", "red_card"]

EVENT_GROUPS = {
    **{k: goal_group for k in goal_group},
    **{k: card_group for k in card_group},
    "assist": ["assist"],
    "substitution": ["substitution"],
    "penalty_missed": ["penalty_missed"],
}

MATCHES_ROLES = {
    "Star Player": 5,
    "First Team": 7,
    "Rotation": 10
}

DAILY_FITNESS_RECOVERY_RATE = 0.0125
SHARPNESS_GAIN_PER_MINUTE = 0.2
DAILY_SHARPNESS_DECAY = 0.04
MIN_SHARPNESS = 10

MAX_EVENTS = {
    "Light Training": 3,
    "Medium Training": 3,
    "Intense Training": 3,
    "Team Building": 2,
    "Recovery": 2
}

EVENT_COLOURS = {
    "Light Training": "#90EE90",   # light green
    "Medium Training": "#32CD32",  # lime green
    "Intense Training": "#006400", # dark green
    "Team Building": "#FFD700",    # gold
    "Recovery": "#1E90FF",         # dodger blue
    "Match Preparation": "#FF8C00", # dark orange
    "Match Review": "#FF69B4",     # hot pink
    "Rest": "#B0C4DE",
    "Travel": "#D3D3D3"
}

MORNING_EVENT_TIMES = (9, 12)
AFTERNOON_EVENT_TIMES = (12, 15)
EVENING_EVENT_TIMES = (15, 18)

EVENT_TIMES = [MORNING_EVENT_TIMES, AFTERNOON_EVENT_TIMES, EVENING_EVENT_TIMES]

EVENT_CHANGES = {
    "Light Training": (-5, 5),   
    "Medium Training": (-12, 10),  
    "Intense Training": (-20, 15),   
    "Recovery": (20, 0),        
}

TEMPLATES_3 = [
    ["Intense Training", "Medium Training", "Light Training"],
    ["Medium Training", "Team Building", "Recovery"],
    ["Light Training", "Recovery", "Intense Training"],
    ["Team Building", "Medium Training", "Recovery"],
    ["Recovery", "Team Building", "Medium Training"]
]

TEMPLATES_2 = [
    ["Medium Training", "Light Training"],
    ["Intense Training", "Recovery"],
    ["Team Building", "Medium Training"],
    ["Recovery", "Light Training"],
    ["Intense Training", "Team Building"]
]

MATCH_STATS = [
    "Possession",
    "xG",
    "Shots",
    "Shots on target",
    "Big chances created",
    "Big chances missed",
    "Shots in the box",
    "Shots outside the box",
    "Shots blocked",
    "Shots on woodwork",
    "Passes",
    "Tackles",
    "Interceptions",
    "Saves",
    "Fouls",
    "Yellow cards",
    "Red cards"
]

SAVED_STATS = [
    "Possession",
    "xG",
    "Shots",
    "Shots on target",
    "Big chances created",
    "Big chances missed",
    "Shots in the box",
    "Shots outside the box",
    "Passes",
    "Tackles",
    "Interceptions",
    "Saves",
    "Fouls",
]

PLAYER_STATS = [
    "Shots",
    "Shots on target",
    "Big chances created",
    "Big chances missed",
    "Shots in the box",
    "Shots outside the box",
    "Passes",
    "Tackles",
    "Interceptions",
    "Saves",
    "Fouls"
]

NEGATIVE_STATS = [
    "Big chances missed",
    "Fouls",
    "Yellow cards",
    "Red cards"
]

DEFENSIVE_ACTION_POSITIONS = {
    "goalkeeper": 0.15,
    "defender": 0.7,
    "midfielder": 0.1,
    "forward": 0.05
}

BIG_CHANCES_POSITIONS = {
    "goalkeeper": 0.01,
    "defender": 0.1,
    "midfielder": 0.45,
    "forward": 0.44
}

MAX_XG = 0.15

CARD_FOUL_CHANCE = 0.7

SHOT_CHANCES = {"Shots blocked": 0.3, "Shots on woodwork": 0.05, "wide": 0.65}
SHOT_DIRECTION_CHANCES = {"Shots in the box": 0.7, "Shots outside the box": 0.3}
DEFENSIVE_ACTIONS_CHANCES = {"Tackles": 0.0833, "Interceptions": 0.05, "nothing": 0.8667}

SHOT_BIG_CHANCE = 0.3
SHOT_TARGET_BIG_CHANCE = 0.5
GOAL_BIG_CHANCE = 0.8

PASSING_POSITIONS = {
    "£goalkeeper": 0.03,
    "defender": 0.3,
    "midfielder": 0.5,
    "forward": 0.17
}

from data.database import StatsManager

STAT_FUNCTIONS = {
    "Goals scored": StatsManager.get_goals_scored,
    "Penalties scored": StatsManager.get_penalties_scored,
    "Goals scored in the first 15": StatsManager.get_goals_scored_in_first_15,
    "Goals scored in the last 15": StatsManager.get_goals_scored_in_last_15,
    "Goals by substitutes": StatsManager.get_goals_by_substitutes,
    "Fastest goal scored": StatsManager.get_fastest_goal_scored,
    "Latest goal scored": StatsManager.get_latest_goal_scored,
    "Highest Possession": StatsManager.get_highest_possession,
    "Lowest Possession": StatsManager.get_lowest_possession,
    "Highest xG": StatsManager.get_highest_xg,
    "Lowest xG": StatsManager.get_lowest_xg,
    "Goals conceded": StatsManager.get_goals_conceded,
    "Clean sheets": StatsManager.get_clean_sheets,
    "Yellow cards": StatsManager.get_yellow_cards,
    "Red cards": StatsManager.get_red_cards,
    "Own goals": StatsManager.get_own_goals,
    "Penalties saved": StatsManager.get_penalties_saved,
    "Goal conceded in the first 15": StatsManager.get_goals_conceded_in_first_15,
    "Goal conceded in the last 15": StatsManager.get_goals_conceded_in_last_15,
    "Fastest goal conceded": StatsManager.get_fastest_goal_conceded,
    "Latest goal conceded": StatsManager.get_latest_goal_conceded,
    "Goal difference": StatsManager.get_goal_difference,
    "Winning from losing position": StatsManager.get_winning_from_losing_position,
    "Losing from winning position": StatsManager.get_losing_from_winning_position,
    "Biggest win": StatsManager.get_biggest_win,
    "Biggest loss": StatsManager.get_biggest_loss,
    "Home performance": StatsManager.get_home_performance,
    "Away performance": StatsManager.get_away_performance,
    "Longest unbeaten run": StatsManager.get_longest_unbeaten_run,
    "Longest winning streak": StatsManager.get_longest_winning_streak,
    "Longest losing streak": StatsManager.get_longest_losing_streak,
    "Longest winless streak": StatsManager.get_longest_winless_streak,
    "Longest scoring streak": StatsManager.get_longest_scoring_streak,
    "Longest scoreless streak": StatsManager.get_longest_scoreless_streak,
}

## ANYTHING HERE WILL NOT BE IMPORTED CORRECTLY DUE TO THE STATSMANAGER IMPORT