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
ALL_PLANETS = PLANETS + ["Aerilon", "Aether", "Boreas", "Calisto", "Drea", "Fiora", "Galatea", "Hesperia", "Icarus", "Kindra", "Lunaris", "Nyx", "Quirinius", "Rhea", "Seraph"]

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

BASE_NUMBERS = {
    "GK": [1],
    "LB": [2, 3],
    "RB": [2, 3],
    "CB": [4, 5],
    "DM": [6, 8],
    "LM": [15],
    "CM": [8, 10, 16],
    "RM": [12],
    "LW": [11, 7],
    "RW": [7, 11],
    "AM": [10],
    "CF": [9],
}

RESERVED_NUMBERS = [1, 2, 3, 4, 5, 6, 8, 7, 9, 10, 11, 16, 17, 19]


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

SEARCH_LIMIT = 20
RESULT_LIMIT = 12

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
    "Medium Training": (-10, 10),  
    "Intense Training": (-15, 15),   
    "Recovery": (20, 0),        
}

TEMPLATES_3 = [
    ["Intense Training", "Medium Training", "Light Training"],
    ["Medium Training", "Team Building", "Light Training"],
    ["Team Building", "Medium Training", "Intense Training"],
    ["Light Training", "Team Building", "Medium Training"]
]

TEMPLATES_2 = [
    ["Medium Training", "Light Training"],
    ["Team Building", "Medium Training"],
    ["Intense Training", "Medium Training"]
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

TIPS = [
    "Remember to rotate your squad to keep players fresh and avoid fatigue.",
    "Keep an eye on player morale; happy players perform better on the pitch.",
    "Use substitutions strategically to maintain energy levels during matches.",
    "Fitness drops during matches and in training, make sure your players get enough rest.",
    "Sharpness increases with match time but decreases when players are benched; manage your lineup accordingly.",
    "Low fitness can increase the risk of injuries; monitor your players closely.",
    "Adjust your tactics based on the opponent's formation for better results.",
    "Make sure to use the Tactics' analysis feature to create a good game plan.",
    "You can search for any player, match, manager, or team in the database from the search tab.",
    "Keep an eye on player stats to identify strengths and weaknesses in your squad.",
    "Remember to set calendar events for week. If you don't want to, delegate to your assistant manager.",
    "Check your emails regularly for important updates and messages from your staff or board.",
    "Shouts can affect the game in your favor if you use them wisely based on the situation.",
]

NEWS_TITLES = {
    "milestone": [
        "{player} hits {value} {milestone_type}.",
    ],
    "injury": [
        "{player} sidelined for {months} months.",
        "Injury blow: {player} out for {months} months.",
        "{player} faces {months}-month layoff."
    ],
    "big_win": [
        "{team1} {score} {team2}.",
    ],
    "big_score": [
        "{team1} and {team2} bring the show.",
    ],
    "transfer": [
        "{player} joins {team}.",
        "Transfer completed: {player} to {team}.",
        "{player} moves to {team}."
    ],
    "disciplinary": [
        "{number} cards in {team}'s match.",
    ],
    "lead_change": [
        "{team} takes the lead!"
    ],
    "planetary_change": [
        "{team} moves into the planetary spots.",
    ],
    "playoff_change": [
        "{team} moves into the playoff positions.",
    ],
    "relegation_change": [
        "{team} drops to the relegation zone."
    ],
    "overthrow": [
        "Upset: {team1} beats {team2}",
        "Shock result in {team1} vs {team2}.",
    ],
    "player_goals": [
        "{player} scores {value} goals vs {opponent}.",
        "{player} shines with {value} goals against {opponent}.",
    ],
    "winless_form" : [
        "{team} now winless in {value} games.",
        "{team} extends winless streak to {value} matches.",
    ],
    "unbeaten_form" : [
        "{team} extends unbeaten run to {value} games.",
        "{team} remains unbeaten for {value} matches.",
    ],
}

NEWS_DETAILS = {

    ## DONE
    "milestone": [
        "{player} has reached an impressive milestone of {value} {milestone_type} in the {comp}\n"
        "this season. The {position} has been instrumental for {team}, contributing\n"
        "consistently in front of goal and helping the side climb the table.",

        "With {value} {milestone_type} now to their name in the {comp}, {player} continues to\n"
        "shine as one of {team}'s key performers. Their form has been vital in\n"
        "maintaining {team}'s momentum this campaign.",

        "{player}'s {value} {milestone_type} in the {comp} marks another chapter in a\n"
        "standout season. The {position} has been in unstoppable form, earning praise\n"
        "from fans and pundits alike.",

        "{player} was in good form again against {opponent} and has now reached\n"
        "{value} {milestone_type} in the {comp} this season — a remarkable achievement that\n"
        "underlines their consistency and ability."
    ],

    ## DONE
    "injury": [
        "{player} suffered a serious setback in {team}'s {score} match against\n"
        "{opponent}. Scans later revealed a {injury_type}, ruling the {position} out for\n"
        "approximately {months} months. The injury comes at a difficult time as {team}\n"
        "fights for crucial league points.",

        "It was a worrying moment for {team} as {player} limped off during their\n"
        "clash with {opponent}. Medical reports confirmed the {position} faces {months}\n"
        "months out, leaving {manager} short on options ahead of a busy league schedule.",

        "Disaster for {team}: {player} picked up an injury during the {competition}\n"
        "fixture versus {opponent}. He is expected to be sidelined for {months} months -\n"
        "a blow that could prove costly for {team}.",

        "{player} has been ruled out for around {months} months after sustaining an injury\n"
        "in {team}'s {score} defeat to {opponent}. The {position} suffered a {injury_type},\n"
        "which will sideline them for a significant period. {team} will need to\n"
        "adapt quickly to overcome this setback."
    ],

    ## DONE
    "big_win": [
        "{team1} sent shockwaves through the league with a commanding {score}\n"
        "victory over {team2}. {potm} was the standout performer, leading by\n"
        "example in a dominant team display.",

        "A statement win from {team1}! The {score} triumph over {team2}\n"
        "showcased their attacking power and tactical precision under {manager}. Fans were\n"
        "treated to a superb performance from start to finish.",

        "{team1} produced a ruthless display to dismantle {team2} {score} at\n"
        "{stadium}. The performance was one of their best this season, with\n"
        "relentless energy and sharp finishing throughout."
    ],

    ## DONE
    "big_score": [
        "Fans were treated to a thrilling encounter as {team1} and\n"
        "{team2} battled in a {score} classic. Both teams showed relentless\n"
        "attacking spirit, creating chances from start to finish.",

        "Supporters witnessed a goal fest as {team1} and {team2}\n"
        "delivered a {score} spectacle. {player1} found the net first in a game packed with\n"
        "end-to-end action.",

        "It was an unforgettable contest as {team1} faced {team2}\n"
        "in a {score} showdown. The match had everything — intensity, momentum swings,\n"
        "and goals that kept the crowd on edge."
    ],

    "transfer": [
        "{player} has completed a high-profile move to {team} in a deal worth around {fee}.\n"
        "The {age}-year-old {position} joins ahead of the league’s second half\n"
        "and is expected to make an immediate impact under {manager}.",

        "After weeks of speculation, {player} has officially joined {team}.\n"
        "The {nationality} international arrives from {previous_team}, bringing top-flight experience\n"
        "and creativity to bolster {team}'s attack.",

        "{team} have confirmed the signing of {player} for {fee}.\n"
        "{player} expressed excitement at joining the club, stating that they 'can’t wait to help {team}\n"
        "climb the table' as they aim for a strong league finish."
    ],

    ## DONE
    "disciplinary": [
        "{team}'s {score} clash with {opponent} turned fiery as {number} cards were\n"
        "shown by the referee. {player} was among those booked in a match full of\n"
        "late tackles and rising tempers.",

        "A heated contest between {team} and {opponent} saw {number} cards\n"
        "handed out. {manager} voiced frustration post-match, admitting the team must\n"
        "show more composure if they’re to succeed in the league.",

        "{stadium} was the scene of chaos as {team} and\n"
        "{opponent} racked up {number} cards in total. The tension on the pitch reflected\n"
        "the high stakes of the league battle, with emotions running high from start to finish."
    ],

    ## DONE
    "lead_change": [
        "{team} have climbed to the top of the league table after the latest\n"
        "round of results. {manager}'s side have shown impressive consistency, and\n"
        "supporters are beginning to dream of lifting the trophy.",

        "{team} now sit at the summit following their recent performance\n"
        "against {opponent}. Momentum is building, and confidence in the camp\n"
        "couldn’t be higher as the title race heats up.",

        "{team} move into first place after a steady run of form. Key\n"
        "contributions from across the squad have been crucial in keeping them\n"
        "ahead of their closest rivals."
    ],

    # "planetary_change": [
    #     "A string of strong results sees {team} move into the planetary qualification spots.\n"
    #     "{manager} praised the squad’s discipline and teamwork after their latest {score}\n"
    #     "win against {opponent}.",

    #     "{team}'s {score} victory over {opponent} lifts them into contention for planetary football next season.\n"
    #     "The fans are beginning to believe a European return could be on the horizon.",

    #     "For the first time this season, {team} have broken into the planetary spots\n"
    #     "after their win against {opponent}. {manager}'s efforts to rebuild confidence\n"
    #     "seem to be paying off in style."
    # ],

    # "playoff_change": [
    #     "{team} has surged into the playoff positions following a crucial {score} win over {opponent}.\n"
    #     "The squad’s resilience and determination were on full display as they fought for every point.",

    #     "With their latest victory, {team} has climbed into the playoff spots.\n"
    #     "{manager} hailed the team’s character and focus after a hard-fought {score}\n"
    #     "result against {opponent}.",

    #     "{team} now finds themselves in the playoff positions after a string of impressive performances.\n"
    #     "The fans are hopeful that this momentum can be sustained as the season progresses."
    # ],

    ## DONE
    "relegation_change": [
        "{team} have slipped into the relegation zone after recent results against\n"
        "{opponent} and others went against them. {manager} has called for focus and\n"
        "determination to climb back to safety.",

        "After a tough run of form, including a setback against {opponent},\n"
        "{team} now find themselves in the bottom three. Pressure is\n"
        "mounting on {manager} to inspire a turnaround before it’s too late.",

        "Results elsewhere and a hard-fought match against {opponent} have seen\n"
        "{team} drop into the relegation zone. The squad will need to find\n"
        "consistency if the club is to avoid a tense end to the season."
    ],

    ## DONE
    "overthrow": [
        "A huge upset in the league as {team1} stunned {team2}\n"
        "with a {score} victory. The underdogs showed incredible resilience, frustrating\n"
        "their more fancied opponents for the full 90 minutes.",

        "Shockwaves through the league as {team1} beat {team2} {score}.\n"
        "{manager} praised the team's performance, highlighting their discipline and\n"
        "teamwork. The match captivated fans with impressive play and strategic\n"
        "mastery throughout.",

        "In one of the season’s biggest surprises, {team1} defeated\n"
        "{team2} {score}. The result shakes up the title race and highlights the\n"
        "unpredictable nature of this year’s competition."
    ],

    ## DONE
    "player_goals": [
        "{player} produced a remarkable performance in {team}'s\n"
        "{competition} clash with {opponent}, scoring {value} goals to leave\n"
        "the crowd in awe. The {position}'s finishing was clinicalthroughout,\n"
        "showcasing the attacking quality {manager} has nurtured this season.",

        "A memorable night for {player}, who struck {value} times against {opponent}\n"
        "in the {competition}. The {team} forward was unstoppable,\n"
        "linking up superbly with teammates and proving why {manager} values\n"
        "their sharp instincts in front of goal.",

        "{player} was at the heart of everything for {team} during their\n"
        "{competition} encounter with {opponent}. The {position}\n"
        "bagged {value} goals, displaying excellent movement and composure that\n"
        "delighted {manager} and the fans alike.",

        "There was no stopping {player} in {team}'s {competition} fixture\n"
        "against {opponent}. The {position} delivered a commanding attacking\n"
        "display, scoring {value} goals and constantly troubling the opposition defence\n"
        "with relentless pressure and precision."
    ],

    "winless_form": [
        "Frustration continues for {team}, who are now without a victory\n"
        "in their last {value} {competition} fixtures. {manager} will be eager to find a spark \n"
        "to turn performances into results as the {team} squad\n"
        "looks to regain confidence on the pitch.",

        "{team}’s struggle to secure a win stretched to {value} games\n"
        "following their recent encounter in the {competition}. Despite showing\n"
        "flashes of quality, {manager} knows the team must find greater consistency\n"
        "to end this difficult spell.",

        "It has been a testing run for {team}, who remain winless in {value}\n"
        "consecutive matches. The players continue to work under {manager}’s\n"
        "guidance to find the form to make them competitive in the {competition}.",

        "{team} extended their winless streak to {value} {competition} games,\n"
        "a sequence that has tested the resolve of both players and staff. {manager}\n"
        "will be hoping for a positive reaction in the upcoming fixtures."
    ],

    "unbeaten_form": [
        "Momentum remains strong for {team}, who have now gone\n"
        "{value} games unbeaten in the {competition}. {manager} praised the team’s\n"
        "discipline and togetherness as they continue to build on this solid run\n"
        "of performances.",

        "{team} extended their unbeaten streak to {value} matches, showing\n"
        "impressive resilience and composure in recent weeks. {manager}’s approach\n"
        "appears to be paying off as the squad grows in confidence with each game.",

        "Another positive display sees {team} remain unbeaten in {value}\n"
        "consecutive {competition} fixtures. {manager} has highlighted the unity within\n"
        "the camp as a key factor behind this consistent spell of form.",

        "The good form continues for {team}, who have yet to taste defeat\n"
        "in their last {value} matches. {manager} will look to maintain this momentum as\n"
        "the side aims to carry their confidence into future {competition} encounters."
    ]

}

OVERTHROW_THRESHOLD = 20

KEEPER_ATTRIBUTES = ["aerial_reach", "reflexes", "throwing", "handling", "kicking", "one_on_ones", "shot_stopping", "first_touch"]
MENTAL_ATTRIBUTES = ["teamwork", "composure", "decisions", "work_rate", "stamina", "pace", "jumping", "strength", "aggression", "acceleration", "balance", "creativity"]
OUTFIELD_ATTRIBUTES = ["corners", "crossing", "dribbling", "finishing", "first_touch", "free_kick", "heading", "long_shots", "marking", "passing", "penalty", "positioning", "tackling", "vision", "positioning"]

CORE_ATTRIBUTES = {
    "forward": [
        "finishing", "dribbling", "first_touch", "heading",
        "crossing", "composure", "decisions",
        "pace", "acceleration", "creativity"
    ],
    "midfielder": [
        "passing", "vision", "first_touch",
        "dribbling", "decisions", "teamwork",
        "composure", "stamina"
    ],
    "defender": [
        "tackling", "marking", "heading",
        "positioning", "strength", "jumping",
        "decisions", "aggression"
    ],
    "goalkeeper": [
        "shot_stopping", "reflexes", "handling",
        "aerial_reach", "one_on_ones", "positioning",
        "decisions"
    ]
}

SECONDARY_ATTRIBUTES = {
    "forward": [
        "vision", "positioning", "strength",
        "balance", "teamwork", "penalty",
        "free_kick", "long_shots"
    ],
    "midfielder": [
        "work_rate", "balance", "creativity",
        "strength", "positioning", "long_shots",
        "free_kick", "corners", "tackling", "crossing"
    ],
    "defender": [
        "pace", "balance", "composure",
        "work_rate", "passing", "first_touch",
        "vision", "long_shots", "free_kick", "crossing"
    ],
    "goalkeeper": [
        "throwing", "kicking", "first_touch",
        "composure", "strength", "jumping"
    ]
}

DEPTH_MULTIPLIER = {
    0: 1.40,
    1: 1.05,
    2: 0.70,
    3: 0.50
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