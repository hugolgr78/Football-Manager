import calendar, math, random, os, zipfile
from datetime import timedelta
from settings import *

def get_objective_for_level(teamAverages, teamID):
    """
    Determine the objective for a team based on their average team level.
    
    Args:
        teamAverages (dict): A dictionary where keys are team IDs and values are dictionaries containing team stats, including "avg_ca".
        teamID (str): The ID of the team for which to determine the objective.
    """
    
    sorted_teams = sorted(teamAverages.items(), key = lambda x: x[1]["avg_ca"], reverse = True)
    teamRank = next((rank for rank, (tid, _) in enumerate(sorted_teams, start = 1) if tid == teamID), None)

    for (min_rank, max_rank), objective in OBJECTIVES.items():
        if min_rank <= teamRank <= max_rank:
            return objective


def append_overlapping_profile(start, profile):
    """
    Safely append a profile frame to the nearest overlappingProfiles container.

    Walks up common parent attributes (parent, parentTab) looking for an
    object with an 'overlappingProfiles' list. If none is found, creates the
    list on the top-most parent and appends there. This centralises the logic
    so other modules don't have to repeat parent-walking code.

    Args:
        start: The starting object to begin the search from.
        profile: The profile frame to append.
    """
   
    c = start
    visited = set()
    while c is not None and id(c) not in visited:
        if hasattr(c, 'overlappingProfiles'):
            try:
                c.overlappingProfiles.append(profile)
                return
            except Exception:
                break
        visited.add(id(c))
        c = getattr(c, 'parent', None) or getattr(c, 'parentTab', None)

    # Not found: attach to the top-most parent
    c = start
    last = c
    visited = set()
    while c is not None and id(c) not in visited:
        visited.add(id(c))
        nextc = getattr(c, 'parent', None) or getattr(c, 'parentTab', None)
        if not nextc:
            break
        last = nextc
        c = nextc

    try:
        if not hasattr(last, 'overlappingProfiles'):
            last.overlappingProfiles = []
        last.overlappingProfiles.append(profile)
        return
    except Exception:
        # Final fallback: attach to the original start object
        if not hasattr(start, 'overlappingProfiles'):
            start.overlappingProfiles = []
        start.overlappingProfiles.append(profile)

def generate_lower_div_objectives(min_level, max_level):
    """
    Generate objectives for lower division teams based on min and max team levels.
    
    Args:
        min_level (int): The minimum team level in the division.
        max_level (int): The maximum team level in the division.
    """
    
    range_size = (max_level - min_level) // 3
    return {
        (max_level, max_level - range_size): "secure promotion",
        (max_level - range_size - 1, max_level - 2 * range_size): "finish in the top half",
        (max_level - 2 * range_size - 1, min_level): "avoid relegation",
    }

def get_fan_reaction(result, expectation):
    """ 
    Get the fan reaction based on match result and expectation level. 
    
    Args:
        result (str): The match result ("win", "draw", "lose").
        expectation (str): The expectation level ("Must Win", "Should Win", "Even Match", "Should Avoid Defeat", "Must Avoid Defeat").
    """

    index = EXPECTATION_LEVELS.index(expectation)
    return FAN_REACTIONS.get(result, ["Unknown"] * 5)[index]

def get_expectation(team_avg, opponent_avg):
    """
    Determine expectation level based on team level difference.
    
    Args:
        team_avg (float): The average level of the team.
        opponent_avg (float): The average level of the opponent team.
    """

    level_diff = team_avg - opponent_avg
    for diff_range, expectation in TEAM_EXPECTATIONS.items():
        if level_diff in diff_range:
            return expectation
    return "Even Match"

def get_result_category(game_result, goal_difference):
    """
    Determine result category based on game result and goal difference.
    
    Args:
        game_result (str): The game result ("win", "draw", "lose").
        goal_difference (int): The goal difference in the match.
    """

    for gd_range, category in RESULT_CATEGORIES[game_result].items():
        if goal_difference in gd_range:
            return category

    return "unknown"  # Default case (should never happen)

def get_fan_message(fan_reaction):
    """
    Return a fan reaction message based on the given fan reaction.
    
    Args:
        fan_reaction (str): The fan reaction category.
    """

    return FAN_MESSAGES.get(fan_reaction, "The fans aren't sure how to react.")

def get_player_ban(ban_type, curr_date):
    """
    Generate a ban duration based on the type of ban.
    
    Args:
        ban_type (str): The type of ban ("injury" or "red card").
        curr_date (datetime): The current date to calculate the ban end date from.
    """
    
    if ban_type == "injury":
        # Range: 14 days to ~180 days
        min_days = 14
        max_days = 180  

        # Bias toward smaller durations by squaring a uniform random
        r = random.random() ** 2   # 0..1, but skewed toward 0
        days = min_days + int(r * (max_days - min_days))

        return (curr_date + datetime.timedelta(days = days)).replace(hour = 0, minute = 0, second = 0, microsecond = 0)

    else:  # red card
        games = random.randint(1, 3)
        return games
    
def get_morale_change(match_result, player_rating, goal_difference):
    """
    Calculate morale change based on match result, player rating, and goal difference.
    
    Args:
        match_result (str): The match result ("win", "draw", "lose").
        player_rating (float): The player's rating in the match (0 to 10).
        goal_difference (int): The goal difference in the match.
    """
    
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
    """
    Get morale decrease based on player role.
    
    Args:
        player (Player): The player object with a 'player_role' attribute.
    """
    
    role = player.player_role

    if role == "Star Player":
        return -5
    elif role == "First Team":
        return -3
    elif role == "Rotation":
        return -1
    
    return 0 # Backup keepers and youth players

def get_player_response(prompt, rating, is_injured):
    """
    Generate a player's response based on the prompt, rating, and injury status.
    
    Args:
        prompt (str): The type of prompt ("Congratulate", "Injury", "Criticize", "Motivate").
        rating (float): The player's rating in the match (0 to 10).
        is_injured (bool): Whether the player is injured or not.
    """
    
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
                "Appreciate it, Coach. I'll come back stronger."
            ],
            "confused": [
                "Are you alright Boss? I feel fine.",
                "I’m not injured, Boss. Is there something wrong?"
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
                "I’m already giving my all. What more do you want?",
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

def parse_time(time_str, reverse = False):
    """
    Parse a time string like "45+2" into a sortable integer.
    Args:
        time_str (str): The time string to parse.
        reverse (bool): If True, return negative for sorting in reverse order.
    """

    if time_str == "N/A":
        return float("inf") if not reverse else -float("inf")
    
    time_str = time_str.replace("'", "")

    parts = time_str.split("+")
    main_time = int(parts[0].strip())
    stoppage_time = int(parts[1].strip()) if len(parts) > 1 else 0
    return main_time + stoppage_time

def player_reaction(score_for, score_against, player_events):
    """
    Calculate player reaction score based on match outcome and individual events for the half time talks.
    
    Args:
        score_for (int): The number of goals scored by the player's team.
        score_against (int): The number of goals conceded by the player's team.
        player_events (dict): A dictionary of events involving the player (e.g., goals, cards).
    """
    
    reaction_score = 0
    
    # Adjust based on team performance
    goal_diff = score_for - score_against
    if goal_diff > 2:
        reaction_score += 2  # Comfortable win
    elif goal_diff > 0:
        reaction_score += 1  # Narrow win
    elif goal_diff == 0:
        reaction_score += 0  # Draw
    elif goal_diff >= -2:
        reaction_score -= 1  # Narrow loss
    else:
        reaction_score -= 2  # Heavy defeat

    if len(player_events) > 0 :
        for event in player_events:
            if event["type"] == "goal" or event["type"] == "penalty_goal" or event["type"] == "penalty_saved":
                reaction_score += 1
            elif event["type"] == "own_goal" or event["type"] == "red_card":
                reaction_score -= 2
            elif event["type"] == "penalty_missed" or event["type"] == "yellow_card":
                reaction_score -= 1

    # Determine final reaction
    if reaction_score >= 3:
        return reaction_score
    elif reaction_score == 2:
        return reaction_score
    elif reaction_score == 1 or reaction_score == 0:
        return reaction_score
    elif reaction_score == -1:
        return reaction_score
    else:
        return reaction_score
    
def get_reaction_colour(score):
    """
    Get the reaction colour based on the reaction score.
    
    Args:
        score (int): The reaction score.
    """
    
    for cond, color in REACTION_COLOURS:
        if cond(score):
            return color

def get_reaction_text(score):
    """
    Get the reaction text based on the reaction score.
    
    Args:
        score (int): The reaction score.
    """
    
    for cond, text in REACTION_TEXTS:
        if cond(score):
            return text
    return "N/A"

def get_prompt_reaction(prompt, score_for, score_against):
    """
    Get the player's reaction to a prompt based on match outcome.
    
    Args:
        prompt (str): The type of prompt ("Congratulate", "Injury", "Criticize", "Motivate").
        score_for (int): The number of goals scored by the player's team.
        score_against (int): The number of goals conceded by the player's team.
    """
    
    if score_for > score_against:
        result = "win"
    elif score_for < score_against:
        result = "lose"
    else:
        result = "draw"

    return PROMPT_REACTIONS[prompt][result]

def reset_available_positions(lineup):
    """
    Reset available positions based on current lineup.
    
    Args:
        lineup (dict): A dictionary representing the current lineup with positions as keys.
    """
    
    new_values = []
    # Add any positions that are not occupied in the lineup
    for position in POSITION_CODES.keys():
        if position not in lineup.keys():
            new_values.append(position)
    
    # Remove any related positions to the ones currently occupied in the lineup
    for position in lineup.keys():
        if position in RELATED_POSITIONS:
            for related_position in RELATED_POSITIONS[position]:
                if related_position in new_values:
                    new_values.remove(related_position)
    
    return new_values

def getSuffix(number):
    """
    Get the ordinal suffix for a given number.
    
    Args:
        number (int): The number to get the suffix for.
    """
    
    if 10 <= number % 100 <= 20:
        return "th"
    else:
        return {1: "st", 2: "nd", 3: "rd"}.get(number % 10, "th")
    
def sort_time(time_str):
    """
    Convert time string to sortable number
    
    Args:
        time_str (str): The time string to convert (e.g., "45+2").
    """

    if "+" in time_str:
        # Handle injury time like "90+3"
        base_time, injury_time = time_str.split("+")
        return int(base_time) + int(injury_time) / 100  # Add injury time as decimal
    else:
        return int(time_str)
    
def create_rounded_rectangle(canvas, x1, y1, x2, y2, radius = 10, **kwargs):
    """
    Draw a rounded rectangle on the canvas.
    
    Args:
        canvas: The Tkinter canvas to draw on.
        x1, y1: Top-left corner coordinates.
        x2, y2: Bottom-right corner coordinates.
        radius: The radius of the rounded corners.
        **kwargs: Additional options to pass to create_polygon.
    """

    points = [
        x1 + radius, y1,
        x2 - radius, y1,
        x2, y1,
        x2, y1 + radius,
        x2, y2 - radius,
        x2, y2,
        x2 - radius, y2,
        x1 + radius, y2,
        x1, y2,
        x1, y2 - radius,
        x1, y1 + radius,
        x1, y1
    ]
    return canvas.create_polygon(points, smooth = True, splinestep = 36, **kwargs)

def generate_attributes(age, team_strength, depth, position):
    """
    Generate player attributes based on age, team strength, league depth, and position.
    Attributes are rated from 1 to 20.
    """

    # --------- HELPERS ----------
    def clamp(x, low = 1, high = 20):
        """
        Clamp value x to be within [lo, hi] and convert to int.
        """
        
        return max(low, min(high, int(x)))

    def strength_adjust(val, team_strength):
        """
        Apply +1 or -1 depending on team strength.
        team_strength:
            < 1.0  => more likely -1
            = 1.0  => no bias
            > 1.0  => more likely +1
        """

        # Convert team_strength (0.5–1.6) into bias -0.5 → +0.6
        bias = team_strength - 1.0

        # Probability of +1 shift
        prob_up = 0.5 + bias * 0.5

        r = random.random()

        if r < prob_up:
            return clamp(val + 1)
        elif r > (1 - prob_up):
            return clamp(val - 1)
        else:
            return clamp(val)

    # AGE modifiers
    if age < 18:
        age_mod_tech = 0.55
        age_mod_phys = 0.95
        age_mod_mental = 0.55

    elif age < 21:
        age_mod_tech = 0.75
        age_mod_phys = 1.00
        age_mod_mental = 0.75

    elif age < 25:
        age_mod_tech = 0.95
        age_mod_phys = 1.00
        age_mod_mental = 0.90

    elif age < 29:
        age_mod_tech = 1.05
        age_mod_phys = 0.95
        age_mod_mental = 1.00

    elif age < 33:
        age_mod_tech = 1.05
        age_mod_phys = 0.90
        age_mod_mental = 1.10

    elif age < 36:
        age_mod_tech = 0.95
        age_mod_phys = 0.80
        age_mod_mental = 1.10

    else:
        age_mod_tech = 0.85
        age_mod_phys = 0.70
        age_mod_mental = 1.05

    league_factor = DEPTH_MULTIPLIER.get(depth, 1.0)

    attrs = {}

    tech_list = KEEPER_ATTRIBUTES if position == "goalkeeper" else OUTFIELD_ATTRIBUTES

    # --- TECHNICAL attributes: stronger base range so top league produces 15-18 commonly ---
    for a in tech_list:
        # base range raised: 8..16 (so top league *1.4 → effective ~11.2..22.4, clamped to 20)
        base = random.uniform(8.0, 16.0)
        val = base * league_factor * age_mod_tech
        val = clamp(val)
        val = strength_adjust(val, team_strength)
        attrs[a] = val

    # --- Mental & Physical: use slightly higher base ranges than before so top players can be high ---
    for a in MENTAL_ATTRIBUTES:
        base = random.uniform(7.0, 15.0)
        if a in ["pace", "stamina", "acceleration", "strength", "jumping", "balance"]:
            val = base * age_mod_phys
        else:
            val = base * age_mod_mental
        val = clamp(val)
        val = strength_adjust(val, team_strength)
        attrs[a] = val

    if position == "goalkeeper":
        if "jumping" in attrs:
            jump = attrs["jumping"]

            # aerial reach depends 80% on jumping + noise
            reach = jump * 0.8 + random.uniform(-2, 2)

            # apply clamp + strength adjust
            reach = clamp(reach)
            reach = strength_adjust(reach, team_strength)

            attrs["aerial reach"] = reach

    return attrs

def generate_CA(player_attributes, position):
    """
    Generate Current Ability (CA) based on player attributes and position.
    CA is scaled 0–200, with core attributes weighted more than secondary.
    """

    # Get the relevant attributes for this position
    core = CORE_ATTRIBUTES[position]
    secondary = SECONDARY_ATTRIBUTES[position]

    # Define weights (core counts more)
    core_weight = 4.0
    sec_weight = 0.4

    # Calculate max possible points for scaling
    max_score = (len(core) * 20 * core_weight) + (len(secondary) * 20 * sec_weight)

    # Compute actual score
    actual_score = 0
    for attr in core:
        actual_score += player_attributes.get(attr, 0) * core_weight
    for attr in secondary:
        actual_score += player_attributes.get(attr, 0) * sec_weight

    # Scale to 0–200
    ca = (actual_score / max_score) * 200

    return int(ca)

def calculate_potential_ability(age, CA):
    """
    Calculate Potential Ability (PA) based on age and CA.
    - Younger players can have huge jumps (wonderkids), but those are rarer.
    - Older players have smaller growth potential.
    - PA capped at 200.
    - Ensures minimum improvement based on CA:
        * CA < 100 → at least +50
        * 100 ≤ CA < 150 → at least +25
        * CA ≥ 150 → no forced minimum (uses normal logic)
    
    Args:
        age (int): The age of the player.
        CA (int): The current ability of the player.
    """

    # Base growth logic by age
    if age <= 18:
        max_gap = 200 - CA
        min_gap = 25
    elif age <= 21:
        max_gap = min(60, 200 - CA)
        min_gap = 15
    elif age <= 24:
        max_gap = min(40, 200 - CA)
        min_gap = 10
    elif age <= 27:
        max_gap = min(25, 200 - CA)
        min_gap = 5
    elif age <= 30:
        max_gap = min(15, 200 - CA)
        min_gap = 0
    else:
        max_gap = min(5, 200 - CA)
        min_gap = 0

    # Extra rule based on CA
    if CA < 100:
        min_gap = max(min_gap, 50)
    elif CA < 150:
        min_gap = max(min_gap, 25)

    # Ensure min_gap does not exceed max_gap
    if min_gap > max_gap:
        min_gap = max_gap

    if max_gap <= 0:
        return CA  # already at cap or no growth possible

    # Build possible gaps
    gaps = list(range(min_gap, max_gap + 1))

    # Weighting: smaller gaps are more likely, big gaps rarer
    weights = [1 / (g - min_gap + 1) for g in gaps]

    gap = random.choices(gaps, weights=weights, k=1)[0]

    return min(CA + gap, 200)

def star_images(star_rating):
    """
    Convert a star rating (0.5 to 5.0 in 0.5 increments) into counts of full, half, and empty stars.
    
    Args:
        star_rating (float): The star rating to convert.
    """

    full_stars = int(star_rating)
    half_star = 1 if (star_rating - full_stars) >= 0.5 else 0
    empty_stars = 5 - full_stars - half_star

    stars = []
    stars += ["star_full"] * full_stars
    stars += ["star_half"] * half_star
    stars += ["star_empty"] * empty_stars

    return stars

def expected_finish(team_name, team_scores):
    """
    Calculate expected league finish based on team scores.
    
    Args:
        team_name (str): Name of the team to calculate for.
        team_scores (list): List of tuples [(team_name, score), ...].
    """

    # Sort teams by score descending
    sorted_teams = sorted(team_scores, key = lambda x: x[1], reverse = True)
    
    # Find the position of the requested team
    for position, (name, _) in enumerate(sorted_teams, start = 1):
        if name == team_name:
            return position
    
    # Team not found
    return None

def format_datetime_split(dt):
    """
    Format a datetime object into day of the week, date string, and time string.
    
    Args:
        dt (datetime): The datetime object to format.
    """
    
    # Day with correct suffix (st, nd, rd, th)
    day = dt.day
    if 10 <= day % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
    
    day_of_week = dt.strftime("%A")                     # e.g. "Wednesday"
    date_str = dt.strftime(f"{day}{suffix} %B %Y")      # e.g. "20th August 2025"
    time_str = dt.strftime("%H:%M")                     # e.g. "14:30"
    
    return day_of_week, date_str, time_str

def get_next_monday(date):
    """
    Get the date of the next Monday from the given date.
    
    Args:   
        date (datetime): The starting date.
    """
    
    days_ahead = (0 - date.weekday() + 7) % 7
    return date + timedelta(days = days_ahead)

def calculate_age(dob, today):
    """
    Calculate age based on date of birth and current date.
    
    Args:
        dob (datetime): The date of birth.
        today (datetime): The current date.
    """
    
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

def player_gametime(avg_minutes, player):
    """
    Determine if a player is getting sufficient game time based on their role.
    
    Args:
        avg_minutes (float): The average minutes played by the player.
        player (Player): The player object with a 'player_role' attribute.
    """

    roles = {
        "Star Player": 50,
        "First Team": 30,
        "Rotation": 20
    }

    if avg_minutes < roles[player.player_role]:
        return True

    return False

def getFitnessDrop(player, fitness):
    """
    Calculate fitness drop during a match based on player position and fitness level.
    
    Args:
        player (Player): The player object with a 'position' attribute.
        fitness (float): The current fitness level of the player (0 to 100).
    """

    position_ranges = {
        "goalkeeper": (0.1, 0.35),
        "defender": (0.4, 0.7),
        "midfielder": (0.7, 1.1),
        "forward": (0.7, 1.2)
    }

    # return a random float in the range for that position
    drop = random.uniform(*position_ranges[player.position])
    scaled_drop = drop * (fitness / 100.0) ** 0.25
    return scaled_drop

def getDayIndex(date):
    """
    Get the index of the day of the week for a given date.

    Args:
        date (datetime): The date to get the day index for. 
    """
    
    day, _, _ = format_datetime_split(date)
    return list(calendar.day_name).index(day)

def ownGoalFoulWeight(p):
    """
    Calculate weight for own goal or foul based on player's ability and sharpness.
    
    Args:
        p (Player): The player object with 'current_ability' and 'sharpness'
    """
    
    # Lower ability and sharpness → higher chance
    ability_factor = (200 - p.current_ability) / 200.0
    sharpness_factor = (100 - p.sharpness) / 100.0

    # Combine factors
    base = 0.5 * ability_factor + 0.5 * sharpness_factor
    return max(base, 0.01)  # avoid zero probability

def fitnessWeight(fitness):
    """
    Calculate weight for events based on player's fitness.
    
    Args:
        fitness (float): The current fitness level of the player (0 to 100).
    """
    
    # Low fitness → higher chance
    fitness_factor = (100 - fitness) / 100.0
    return max(fitness_factor, 0.01)  # avoid 0 prob

def goalChances(attackingLevel, defendingLevel, avgSharpness, avgMorale, oppKeeper, goalBoost = 1.0):
    """
    Calculate the chances of scoring a goal based on team levels, sharpness, morale, and opponent keeper.
    
    Args:
        attackingLevel (float): The attacking team's level.
        defendingLevel (float): The defending team's level.
        avgSharpness (float): The average sharpness of the attacking team (0 to 100).
        avgMorale (float): The average morale of the attacking team (0 to 100).
        oppKeeper (Player or None): The opponent's goalkeeper player object, or None if no keeper.
        goalBoost (float): A multiplier for goal chances (default is 1.0).
    """
    
    # attackRatio = min(attackingLevel / max(1, defendingLevel), 2.0)
    attackRatio = 0.5 + 1 / (1 + math.exp(-(attackingLevel - defendingLevel) / 20))

    # Sharpness has less weight now
    combined_form = (0.25 * (avgSharpness / 100)) + (0.75 * (avgMorale / 100))
    attackModifier = min(combined_form ** 0.5, 1.05)

    # Dampening factor for even matchups
    ratio_factor = attackRatio / (attackRatio + 1) if attackRatio > 0 else 0.5

    # Attack ratio dominates
    weight_ratio = 0.8
    weight_modifier = 1 - weight_ratio
    effective_attack = attackRatio * weight_ratio + attackModifier * weight_modifier * goalBoost

    if oppKeeper:
        if oppKeeper.position == "goalkeeper":
            keeperModifier = (oppKeeper.current_ability / 200) * (oppKeeper.sharpness / 100)

            # Much lower shot base now
            shot_base = BASE_SHOT * effective_attack * 0.4
            shotProb = shot_base * (1 - keeperModifier * 0.3)
            shotProb = min(max(shotProb, 0.01), MAX_SHOT_PROB)  # very low floor

            onTarget_base = BASE_ON_TARGET * effective_attack * 0.7
            onTargetProb = onTarget_base * (1 - keeperModifier * 0.25)
            onTargetProb = min(max(onTargetProb, 0.10), MAX_TARGET_PROB)

            goal_base = BASE_GOAL * effective_attack * ratio_factor
            goalProb = goal_base * (1 - keeperModifier)
            goalProb = min(max(goalProb, 0.01), MAX_GOAL_PROB)
        else:
            # Outfield keeper (more shots, but still tuned down)
            shotProb = min(max(BASE_SHOT * effective_attack * 0.6, 0.08), 0.55)
            onTargetProb = min(max(BASE_ON_TARGET * effective_attack * 0.9, 0.25), 0.7)
            goalProb = min(max(BASE_GOAL * effective_attack * 1.2, 0.35), 0.8)
    else:
        # No keeper
        shotProb = min(max(BASE_SHOT * effective_attack * 0.7, 0.15), 0.6)
        onTargetProb = min(max(BASE_ON_TARGET * effective_attack * 1.0, 0.40), 0.75)
        goalProb = min(max(BASE_GOAL * effective_attack * 1.5, 0.65), 0.9)

    # Final distribution
    pNothing   = 1 - shotProb
    pShotOff   = shotProb * (1 - onTargetProb)
    pShotSaved = shotProb * onTargetProb * (1 - goalProb)
    pGoal      = shotProb * onTargetProb * goalProb

    events = ["nothing", "Shots", "Shots on target", "goal"]
    probs  = [pNothing, pShotOff, pShotSaved, pGoal]

    return random.choices(events, weights = probs, k = 1)[0]

def foulChances(avgSharpnessWthKeeper, severity):
    """
    Calculate the chances of fouls, yellow cards, and red cards based on average sharpness and severity.
    
    Args:
        avgSharpnessWthKeeper (float): The average sharpness of the team including the goalkeeper (0 to 100).
        severity (str): The severity level ("low", "medium", "high").
    """
    
    severity_map = {"low": 0.8, "medium": 1.0, "high": 1.2}
    severity = severity_map.get(severity, 1.0)

    gamma = 0.5
    sf = ((100.0 - avgSharpnessWthKeeper) / 50.0) ** gamma
    sf = max(0.5, min(sf, 2.0))  # keep it realistic

    foulProb   = BASE_FOUL   * sf
    yellowProb = BASE_YELLOW * sf * severity
    redProb    = BASE_RED    * sf * severity

    # realistic clamps
    foulProb   = min(max(foulProb, 0.01), 0.20)
    yellowProb = min(max(yellowProb, 0.002), 0.05)
    redProb    = min(max(redProb, 0.0001), 0.02)

    # ensure total <= 1
    total = foulProb + yellowProb + redProb
    if total > 1:
        scale = 1.0 / total
        foulProb *= scale
        yellowProb *= scale
        redProb *= scale

    pNothing = 1.0 - (foulProb + yellowProb + redProb)

    events = ["nothing", "Fouls", "yellow_card", "red_card"]
    probs = [pNothing, foulProb, yellowProb, redProb]

    return random.choices(events, weights = probs, k = 1)[0]

def injuryChances(avgFitness):
    """
    Calculate the chances of injury based on average fitness.
    
    Args:
        avgFitness (float): The average fitness level of the team (0 to 100).
    """

    if avgFitness == 0:
        return

    injuryProb = BASE_INJURY * (100 / avgFitness)
    injuryProb = min(max(injuryProb, 0.0001), MAX_INJURY_PROB)

    # --- Final event distribution ---
    pNothing = 1 - injuryProb
    pInjury = injuryProb

    events = ["nothing", "injury"]
    probs = [pNothing, pInjury]

    return random.choices(events, weights = probs, k = 1)[0]

def substitutionChances(lineup, subsMade, subs, events, currMinute, fitness, playerOBJs, ratings):
    """
    Determine substitutions to make during a match based on player fitness and ratings.
    
    Args:
        lineup (dict): Current lineup with positions as keys and player IDs as values.
        subsMade (int): Number of substitutions already made.
        subs (list): List of available substitute player IDs.   
        events (dict): Dictionary of match events with timestamps as keys.
        currMinute (int): Current minute of the match.
        fitness (dict): Dictionary mapping player IDs to their fitness levels.
        playerOBJs (dict): Dictionary mapping player IDs to Player objects.
        ratings (dict): Dictionary mapping player IDs to their ratings.
    """
    
    subsAvailable = MAX_SUBS - subsMade
    if subsAvailable <= 0:
        return []

    candidates = get_sub_candidates(lineup, currMinute, events, fitness, ratings)

    if not candidates:
        return []

    # sort lowest fitness first
    candidates.sort(key = lambda x: fitness[x[1]])

    # how many subs
    outcomes = [1, 2, 3]
    weights = [0.65, 0.25, 0.10]
    num_to_sub = random.choices(outcomes, weights=weights, k=1)[0]
    num_to_sub = min(num_to_sub, subsAvailable, len(candidates))

    chosen = find_substitute(lineup, candidates, subs, num_to_sub, playerOBJs)

    return chosen

def get_sub_candidates(lineup, currMinute, events, fitness, ratings):
    """
    Get list of substitution candidates based on fitness and ratings.
    
    Args:
        lineup (dict): Current lineup with positions as keys and player IDs as values.
        currMinute (int): Current minute of the match.
        events (dict): Dictionary of match events with timestamps as keys.
        fitness (dict): Dictionary mapping player IDs to their fitness levels.
        ratings (dict): Dictionary mapping player IDs to their ratings.
    """
    
    candidates = []
    for pos, playerID in lineup.items():
        played_minutes = currMinute
        for event_time, event_data in events.items():
            if event_data["type"] == "substitution" and event_data["player_on"] == playerID:
                eventMinute = int(event_time.split(":")[0])
                played_minutes = currMinute - eventMinute
                break

        if played_minutes >= 30:  # don’t sub too early
            prob = sub_probability(fitness[playerID], ratings[playerID])
            if prob > 0:
                candidates.append((prob, playerID, pos))

    return candidates

def find_substitute(lineup, candidates, subs, num_to_sub, playerOBJs):
    """
    Find suitable substitutes for the candidates.
    
    Args:
        lineup (dict): Current lineup with positions as keys and player IDs as values.
        candidates (list): List of tuples (probability, playerID, position) for substitution candidates.
        subs (list): List of available substitute player IDs.   
        num_to_sub (int): Number of substitutions to make.
        playerOBJs (dict): Dictionary mapping player IDs to Player objects.
    """
    
    chosen = []
    # make substitutions
    for prob, playerID, pos in candidates:
        if len(chosen) >= num_to_sub:
            break
        if random.random() < prob:
            out_code = POSITION_CODES[pos]

            replacement_id = None
            replacement_pos = None
            reason = None

            # --- Exact / compatible replacement ---
            for subID in subs:
                player = playerOBJs[subID]
                subPositions = [s for s in player.specific_positions.split(",")]

                # Direct match: outgoing code is explicitly listed in sub's positions
                if out_code in subPositions:
                    replacement_id = subID
                    replacement_pos = pos
                    reason = "direct"
                    break

                # Compatible match: sub can play a compatible position
                compatible_codes = COMPATIBLE_POSITIONS.get(out_code, [])
                compatible_subs = [sp for sp in subPositions if sp in compatible_codes]
                if compatible_subs:
                    replacement_id = subID
                    replacement_pos = pos
                    reason = "compatible"
                    break

            # --- Fallback if no compatible found ---
            if not replacement_id and subs:
                for subID in subs:
                    sub_player = playerOBJs[subID]
                    subPositions = [REVERSE_POSITION_CODES[s][0] for s in sub_player.specific_positions.split(",")]

                    # pick the first full position not already in lineup.keys()
                    for full_pos in subPositions:
                        if full_pos not in lineup:
                            replacement_id = subID
                            replacement_pos = full_pos
                            reason = "formation_change"
                            break

                    if replacement_id:
                        break

            if replacement_id:
                chosen.append((playerID, pos, replacement_id, replacement_pos, reason))
                subs.remove(replacement_id)

    return chosen

def sub_probability(fitness, rating):
    """
    Calculate the probability of substituting a player based on fitness and rating.
    
    Args:
        fitness (float): The current fitness level of the player (0 to 100).
        rating (float): The current rating of the player (1 to 10).
    """
    
    # Base probability from fitness
    if fitness > 50:
        base_prob = 0.0
    elif fitness > 20:
        # scales 50 -> 0%, 20 -> 60%
        base_prob = (50 - fitness) / 30 * 0.6
    elif fitness > 10:
        # scales 20 -> 60%, 10 -> 85%
        base_prob = 0.6 + (20 - fitness) / 10 * 0.25
    else:
        # below 10 -> 85–100%
        base_prob = 0.85 + (10 - max(fitness, 0)) / 10 * 0.15

    # Rating adjustment (assume 1–10 scale)
    # Rating < 5 increases chance, rating > 5 decreases chance
    # Clamp between -0.2 and +0.2 for balance
    rating_adjustment = (5 - rating) * 0.04  # 1 rating point ≈ 4% effect
    prob = base_prob + rating_adjustment

    # Clamp to [0, 1]
    return max(0.0, min(1.0, prob))
    
def getPasses(homeOBJs, awayOBJs):
    """
    Determine number of passes for home and away teams based on effective abilities.

    Args:
        homeOBJs (dict): Dictionary of home team player objects.
        awayOBJs (dict): Dictionary of away team player objects.
    """

    overallHome = sum(effective_ability(p) for p in homeOBJs.values())
    overallAway = sum(effective_ability(p) for p in awayOBJs.values())

    total_passes = random.randint(3, 5)
    # soften big differences (alpha = 0.5)
    alpha = 0.5
    home_weight = overallHome ** alpha
    away_weight = overallAway ** alpha
    p_home = home_weight / (home_weight + away_weight)

    # allocate passes stochastically
    home_passes = sum(random.random() < p_home for _ in range(total_passes))
    away_passes = total_passes - home_passes

    # cap dominance (max 80% of passes)
    cap = 0.8
    max_home = int(total_passes * cap)
    min_home = total_passes - max_home
    home_passes = max(min(home_passes, max_home), min_home)
    away_passes = total_passes - home_passes

    return home_passes, away_passes

def effective_ability(p):
    """
    Calculate the effective ability of a player based on morale, fitness, and sharpness.
    
    Args:
        p (Player): The player object with 'current_ability', 'morale', 'fitness', and 'sharpness' attributes.
    """
    
    # weights: morale 20%, fitness 40%, sharpness 40%
    weighted = (0.2 * p.morale + 0.4 * p.fitness + 0.4 * p.sharpness) / 100.0
    multiplier = 0.75 + (weighted * 0.5)
    return p.current_ability * multiplier

def getStatNum(stat):
    """
    Sum the values in a stat dictionary.
    
    Args:
        stat (dict): A dictionary mapping player IDs to their stat values.
    """
    
    return sum(playerValue for playerValue in stat.values())

def passesAndPossession(matchInstance):
    """
    Simulate passes and possession for both teams in a match instance.
    
    Args:
        matchInstance (Match): The match instance containing all relevant data.
    """
    
    homeLineup = matchInstance.homeCurrentLineup
    awayLineup = matchInstance.awayCurrentLineup
    homeStats = matchInstance.homeStats
    awayStats = matchInstance.awayStats
    homePassesAttempted = matchInstance.homePassesAttempted
    awayPassesAttempted = matchInstance.awayPassesAttempted
    homeRatings = matchInstance.homeRatings
    homePlayersOBJs = matchInstance.homePlayersOBJ
    awayPlayersOBJs = matchInstance.awayPlayersOBJ

    homeOBJs = {pid: p for pid, p in homePlayersOBJs.items() if pid in homeLineup.values()}
    awayOBJs = {pid: p for pid, p in awayPlayersOBJs.items() if pid in awayLineup.values()}

    awayRatings = matchInstance.awayRatings

    homePasses, awayPasses = getPasses(homeOBJs, awayOBJs)
    matchInstance.homePassesAttempted = homePassesAttempted + homePasses
    matchInstance.awayPassesAttempted = awayPassesAttempted + awayPasses

    # Compute pass completion probability from sharpness with a lower baseline and an upper cap
    # We scale sharpness into a range [0.60, 0.90] so even low-sharpness players have at least 60%
    # and very high sharpness caps at ~90%.
    for _ in range(homePasses):
        playerID = choosePlayerFromDict(homeLineup, PASSING_POSITIONS, homeOBJs)

        raw = homeOBJs[playerID].sharpness / 100.0
        passCompleteProb = 0.60 + raw * (0.90 - 0.60)

        if random.random() < passCompleteProb:
            # ensure the Passes dict exists and the player key is initialized
            homeStats.setdefault("Passes", {})
            homeStats["Passes"].setdefault(playerID, 0)
            homeStats["Passes"][playerID] += 1

            rating = random.uniform(PASS_RATING[0], PASS_RATING[1])
            homeRatings[playerID] = round(homeRatings.get(playerID, 0) + rating, 2)

    for _ in range(awayPasses):
        playerID = choosePlayerFromDict(awayLineup, PASSING_POSITIONS, awayOBJs)

        raw = awayOBJs[playerID].sharpness / 100.0
        passCompleteProb = 0.60 + raw * (0.90 - 0.60)

        if random.random() < passCompleteProb:
            # ensure the Passes dict exists and the player key is initialized
            awayStats.setdefault("Passes", {})
            awayStats["Passes"].setdefault(playerID, 0)
            awayStats["Passes"][playerID] += 1

            rating = random.uniform(PASS_RATING[0], PASS_RATING[1])
            awayRatings[playerID] = round(awayRatings.get(playerID, 0) + rating, 2)

    homeCompleted = getStatNum(homeStats["Passes"])
    awayCompleted = getStatNum(awayStats["Passes"])
    totalCompleted = homeCompleted + awayCompleted

    if totalCompleted == 0:
        homeStats["Possession"] = 50
        awayStats["Possession"] = 50
    else:
        homeStats["Possession"] = round((homeCompleted / totalCompleted) * 100)
        awayStats["Possession"] = 100 - homeStats["Possession"]

def choosePlayerFromDict(lineup, dict_, playerOBJs):
    """
    Choose a player from the lineup based on position weights and effective ability.
    
    Args:
        lineup (dict): Current lineup with positions as keys and player IDs as values.
        dict_ (dict): Dictionary mapping positions to their selection weights.
        playerOBJs (dict): Dictionary mapping player IDs to Player objects.
    """
    
    playerPosition = random.choices(list(dict_.keys()), weights = list(dict_.values()), k = 1)[0]
    players = [playerID for playerID in lineup.values() if playerOBJs[playerID].position == playerPosition]

    while len(players) == 0:
        playerPosition = random.choices(list(dict_.keys()), weights = list(dict_.values()), k = 1)[0]
        players = [playerID for playerID in lineup.values() if playerOBJs[playerID].position == playerPosition]

    weights = [effective_ability(playerOBJs[playerID]) for playerID in players]
    if sum(weights) == 0:
        weights = [1] * len(players)

    return random.choices(players, weights = weights, k = 1)[0]

def getStatPlayer(stat, lineup, playerOBJs):
    """
    Get a player responsible for a specific stat event based on lineup and player abilities.
    
    Args:
        stat (str): The type of stat event (e.g., "Saves", "Shots", "Fouls").
        lineup (dict): Current lineup with positions as keys and player IDs as values.
        playerOBJs (dict): Dictionary mapping player IDs to Player objects.
    """
    
    if playerOBJs is None:
        from data.database import Players
        playerOBJs = {pid: Players.get_player_by_id(pid) for pid in lineup.values()}
    
    match stat:
        case "Saves":
            rating = random.uniform(SAVE_RATING[0], SAVE_RATING[1])
            return lineup["Goalkeeper"] if "Goalkeeper" in lineup else None, rating if "Goalkeeper" in lineup else 0
        case "Shots" | "Shots on target" | "Shots in the box" | "Shots outside the box":
            rating = random.uniform(SHOT_RATING[0], SHOT_RATING[1]) if stat != "Shots on target" else random.uniform(SHOT_TARGET_RATING[0], SHOT_TARGET_RATING[1])
            return choosePlayerFromDict(lineup, SCORER_CHANCES, playerOBJs), rating
        case "Fouls":
            weights = [ownGoalFoulWeight(playerOBJs[playerID]) for playerID in lineup.values()]
            rating = random.uniform(FOUL_RATING[0], FOUL_RATING[1])
            return random.choices(list(lineup.values()), weights = weights, k = 1)[0], rating
        case "Tackles" | "Interceptions":
            rating = random.uniform(DEFENSIVE_ACTION_RATING[0], DEFENSIVE_ACTION_RATING[1])
            return choosePlayerFromDict(lineup, DEFENSIVE_ACTION_POSITIONS, playerOBJs), rating
        case "Big chances created" | "Big chances missed":
            rating = random.uniform(BIG_CHANCE_CREATED_RATING[0], BIG_CHANCE_CREATED_RATING[1]) if stat == "Big chances created" else random.uniform(BIG_CHANCE_MISSED_RATING[0], BIG_CHANCE_MISSED_RATING[1])
            return choosePlayerFromDict(lineup, BIG_CHANCES_POSITIONS, playerOBJs), rating
    
def apply_attribute_changes(fitness_map, sharpness_map, time_in_between):
    """
    Apply attribute changes to player fitness and sharpness over a time interval.
    
    Args:
        fitness_map (dict): A dictionary mapping player IDs to [fitness, injured] lists.
        sharpness_map (dict): A dictionary mapping player IDs to sharpness values.
        time_in_between (timedelta): The time interval over which to apply changes.
    """

    hours = int(time_in_between.total_seconds() // 3600)
    if hours <= 0:
        return

    # factors
    hourly_sharpness_decay = DAILY_SHARPNESS_DECAY / 24.0
    sharpness_decay_factor = (1 - hourly_sharpness_decay) ** hours

    hourly_fitness_recovery = DAILY_FITNESS_RECOVERY_RATE / 24.0
    fitness_recovery_factor = (1 - hourly_fitness_recovery) ** hours

    # update sharpness
    for pid, sharpness in sharpness_map.items():
        new_sharpness = sharpness * sharpness_decay_factor
        if new_sharpness < MIN_SHARPNESS:
            new_sharpness = MIN_SHARPNESS
        sharpness_map[pid] = int(round(new_sharpness))

    # update fitness
    for pid, (fitness, injured) in fitness_map.items():
        if injured:
            continue  

        new_fitness = 100 - (100 - fitness) * fitness_recovery_factor
        fitness_map[pid] = [int(math.ceil(min(100, new_fitness))), injured]

def update_dict_values(values_dict, amount, min_value = None, max_value = None):
    """
    Update values in a dictionary by a specified amount, with optional min and max bounds.
    
    Args:
        values_dict (dict): A dictionary with numeric values to update.
        amount (float): The amount to add to each value.
        min_value (float, optional): Minimum bound for the updated values.
        max_value (float, optional): Maximum bound for the updated values.
    """

    for k, v in values_dict.items():
        new_val = v + amount

        if min_value is not None and new_val < min_value:
            new_val = min_value
        if max_value is not None and new_val > max_value:
            new_val = max_value

        values_dict[k] = int(round(new_val))

    return values_dict

def update_fitness_dict_values(values_dict, amount, min_value = None, max_value = None):
    """
    Update fitness values in a dictionary by a specified amount, with optional min and max bounds.
    
    Args:
        values_dict (dict): A dictionary with [fitness, injured] lists to update.
        amount (float): The amount to add to each fitness value.
        min_value (float, optional): Minimum bound for the updated fitness values. Defaults to None.
        max_value (float, optional): Maximum bound for the updated fitness values. Defaults to None.
    """

    for k, (v, injured) in values_dict.items():

        if injured:
            continue

        new_val = v + amount

        if min_value is not None and new_val < min_value:
            new_val = min_value
        if max_value is not None and new_val > max_value:
            new_val = max_value

        values_dict[k] = [int(round(new_val)), injured]

    return values_dict

def get_all_league_teams(jsonData, leagueName):
    """
    Get all teams belonging to a specific league from JSON data.
    
    Args:
        jsonData (list): List of team data in JSON format.
        leagueName (str): The name of the league to filter teams by.
    """
    
    teamOBJs = []

    for team in jsonData:
        if team["league"] == leagueName:
            teamOBJs.append(team)

    return teamOBJs

def run_match_simulation(interval, currDate, exclude_leagues = [], progress_callback = None):
    """
    Run match simulations in parallel for matches within a specified time frame.
    
    Args:
        interval (tuple): A tuple containing start and end datetime objects for the simulation period.
        currDate (datetime): The current date for the simulation context.
        exclude_leagues (list, optional): List of league IDs to exclude from simulation. Defaults to [].
        progress_callback (function, optional): A callback function to report progress. Defaults to None.
    """
    
    from data.database import Matches, Managers, Teams, League, Emails, LeagueTeams, PlayerBans, TeamHistory, LeagueNews, process_payload, check_player_games_happy
    from data.gamesDatabase import Game
    from concurrent.futures import ProcessPoolExecutor, as_completed
    import os, time, logging, glob, traceback

    _logger = logging.getLogger(__name__)

    matchesToSim = Matches.get_matches_time_frame(interval[0], interval[1], exclude_leagues)
    worker_payloads = []
    if matchesToSim:
        total_to_sim = len(matchesToSim)
        _logger.info("Preparing to simulate %d matches", total_to_sim)
        _logger.info("Starting match initialization")

        CHUNK_SIZE = min(len(matchesToSim), os.cpu_count() - 1)
        total_batches = (total_to_sim + CHUNK_SIZE - 1) // CHUNK_SIZE

        _logger.info("Starting parallel match simulation in up to %d batches (chunk=%d)", total_batches, CHUNK_SIZE)

        sim_start = time.perf_counter()

        # Run batches sequentially to respect the maximum worker count
        matches = []
        teams = {}
        mgr = Managers.get_all_user_managers()[0]
        managerTeam = Teams.get_teams_by_manager(mgr.id)[0]
        managerLeague = LeagueTeams.get_league_by_team(managerTeam.id)
        base_name = Game.get_games_by_manager_id(mgr.id)[0].save_name

        # Create the pool once, outside the batch loop
        with ProcessPoolExecutor(max_workers=CHUNK_SIZE, initializer=_init_worker, initargs=(base_name,)) as ex:
            for batch_index in range(0, total_to_sim, CHUNK_SIZE):
                batch = matchesToSim[batch_index:batch_index + CHUNK_SIZE]
                workers = min(len(batch), CHUNK_SIZE)
                batch_no = (batch_index // CHUNK_SIZE) + 1
                _logger.info(
                    "Simulating batch %d/%d: %d matches with %d workers",
                    batch_no, total_batches, len(batch), workers
                )

                # Submit tasks to the already-running pool
                _logger.info("Submitting %d match tasks...", len(batch))
                futures = [ex.submit(_simulate_match, g.id) for g in batch]
                _logger.info("All match tasks submitted.")

                for fut in as_completed(futures):
                    try:
                        result = fut.result()
                        match = Matches.get_match_by_id(result["id"])
                        matches.append(Matches.get_match_by_id(result["id"]))
                        _logger.info("Finished match %s with score %s", result["id"], result["score"])

                        worker_payload = result.get("payload")
                        if worker_payload:

                            _logger.debug("Checking player game happiness for match %s", match.id)
                            homePayload = check_player_games_happy(match.home_id, currDate)
                            awayPayload = check_player_games_happy(match.away_id, currDate)
        
                            _logger.debug("Updating worker payload for match %s", match.id)
                            worker_payload["players_to_update"] = homePayload["players_to_update"]
                            worker_payload["players_to_update"] = awayPayload["players_to_update"]
                            worker_payload["emails_to_send"] = homePayload["emails_to_send"]
                            worker_payload["emails_to_send"] = awayPayload["emails_to_send"]

                            if not match.league_id in teams:
                                teams[match.league_id] = []

                            teams[match.league_id].append(match.home_id)
                            teams[match.league_id].append(match.away_id)

                            worker_payloads.append(worker_payload)

                            if progress_callback:
                                progress_callback()

                    except Exception:
                        _logger.exception("Match worker raised an exception")
                        traceback.print_exc()

        # Remove worker DB copies
        for f in glob.glob(f"data/{base_name}_copy_*.db"):
            try:
                os.remove(f)
                _logger.debug("Removed worker DB copy %s", f)
            except Exception:
                _logger.warning("Could not remove DB copy %s", f)

        sim_end = time.perf_counter()
        elapsed = sim_end - sim_start
        _logger.info("Match simulation completed in %.3f seconds for %d matches", elapsed, total_to_sim)
        print(f"Match simulation completed in {elapsed:.3f} seconds for {total_to_sim} matches")

        # After all batches complete, aggregate pooled payloads (no computation, just concatenation)
        pooled = {
            "team_updates": [],
            "manager_updates": [],
            "match_events": [],
            "player_bans": [],
            "yellow_card_checks": [],
            "score_updates": [],
            "fitness_updates": [],
            "lineup_updates": [],
            "sharpness_updates": [],
            "morale_updates": [],
            "stats_updates": [],
            "players_to_update": [],
            "emails_to_send": [],
            "news_to_add": [],
            "player_goals_to_check": [],
            "player_assists_to_check": [],
            "player_clean_sheets_to_check": [],
            "form_to_check": []
        }

        for p in worker_payloads:
            for k in pooled.keys():
                val = p.get(k)
                if not val:
                    continue
                # If list-like, extend; otherwise set (defensive)
                if isinstance(p[k], list):
                    pooled[k].extend(p[k])
                else:
                    # unexpected type: append the value
                    pooled[k].append(p[k])

        # attach to the MainMenu instance for further processing by caller
        pooled_payload = pooled

        _logger.debug("Aggregated pooled payload from %d workers", len(worker_payloads))
        process_payload(pooled_payload)
        _logger.debug("Processed pooled payload")

        leagueIDs = list({match.league_id for match in matches})
        for id_ in leagueIDs:
            LeagueTeams.update_team_positions(id_)
            if League.check_all_matches_complete(id_, currDate):

                matchday = League.get_current_matchday(id_)
                for team in LeagueTeams.get_teams_by_league(id_):
                    TeamHistory.add_team(matchday, team.team_id, team.position, team.points)

                if id_ == managerLeague.league_id:
                    _, email = League.team_of_the_week(id_, matchday, team = managerTeam.id)
 
                    if email:
                        Emails.add_email("team_of_the_week", matchday, None, None, managerLeague.league_id, (currDate + timedelta(days = 1)).replace(hour = 8, minute = 0, second = 0, microsecond = 0))

                # Check for lead changes, relegation changes here
                if matchday > 20:
                    check_league_changes(id_, matchday, currDate)

                League.update_current_matchday(id_)
            _logger.debug(f"Updated league standings and matchdays for league {id_}")

        _logger.debug("Starting suspension reductions for %d leagues", len(teams))
        PlayerBans.reduce_suspensions_for_teams(teams)
        _logger.debug("Completed suspension reductions for teams")

def _init_worker(base_name):
    """
    Initialize a worker process with its own database copy.
    
    Args:
        base_name (str): The base name of the database to copy.
    """
    
    from data.database import DatabaseManager
    import os
    import logging

    _logger = logging.getLogger(__name__)

    global _worker_dbm, _worker_base_name, _worker_db_copy_path
    _worker_base_name = base_name
    _worker_dbm = DatabaseManager()
    _worker_dbm.set_database(base_name)

    # Each worker gets its own database copy
    pid = os.getpid()
    copy_path = f"data/{base_name}_copy_{pid}.db"
    _worker_dbm.copy_path = copy_path

    try:
        _worker_dbm.start_copy()
    except Exception:
        _logger.exception("Failed to start DB copy for worker %d", pid)
        _worker_dbm = None
        _worker_db_copy_path = None
        return

    _worker_db_copy_path = copy_path
    _logger.debug("Worker %d ready with DB copy %s", pid, copy_path)

def _simulate_match(gameID):
    """
    Simulate a single match given its game ID.
    
    Args:
        gameID (int): The ID of the match to simulate.
    """
    
    global _worker_dbm, _worker_db_copy_path
    from utils.match import Match
    from data.database import Matches
    import logging, gc

    _logger = logging.getLogger(__name__)

    if _worker_dbm is None:
        _logger.error("Worker database manager not initialized.")
        return {"id": getattr(gameID, "id", None), "score": None, "payload": None}

    game = Matches.get_match_by_id(gameID)
    match = Match(game, auto=True)
    match.startGame()
    match.join()

    # cleanup session for next match (but not engine or db copy)
    try:
        if _worker_dbm.scoped_session:
            _worker_dbm.scoped_session.remove()
    except Exception:
        pass
    gc.collect()

    result = {
        "id": getattr(game, "id", None),
        "score": match.score,
        "payload": getattr(match, "payload", None),
    }

    return result

def get_planet_percentage(depth):
    """
    Gets the percentage of players to be from a certain planet based on league depth.
    
    Args:
        depth (int): The depth level of the league.
    """

    if depth == 0:
        return random.uniform(0.35, 0.45)
    elif depth == 1:
        return random.uniform(0.50, 0.70)
    elif depth == 2:
        return random.uniform(0.65, 0.85)
    else:
        return random.uniform(0.80, 0.95)
    
def add_file_with_progress(zipf, file_path, arcname, progress_callback=None):
    """
    Add a file to zip with progress reporting.
    """

    file_size = os.path.getsize(file_path)
    with open(file_path, "rb") as f:
        # Start a new file entry in the zip
        zipinfo = zipfile.ZipInfo(arcname)
        zipinfo.compress_type = zipfile.ZIP_DEFLATED
        with zipf.open(zipinfo, "w") as dest:
            read_bytes = 0
            while True:
                chunk = f.read(1024 * 1024)  # 1 MB chunks
                if not chunk:
                    break
                dest.write(chunk)
                read_bytes += len(chunk)
                if progress_callback:
                    progress_callback(read_bytes, file_size)

def get_best_player_for_position(matches, position):
    """
    Finds the best player for a given position from a list of matches.
    """

    from data.database import TeamLineup

    bestRating = -1
    bestPlayerID = None

    for match in matches:
        lineup = TeamLineup.get_lineup_by_match(match.id)

        for entry in lineup:
            if entry.start_position == position:
                if entry.rating and entry.rating > bestRating:
                    bestRating = entry.rating
                    bestPlayerID = entry.player_id
            elif not entry.start_position and entry.end_position == position:
                if entry.rating and entry.rating > bestRating:
                    bestRating = entry.rating
                    bestPlayerID = entry.player_id

    return bestPlayerID, bestRating 

def generate_news_title(news_type, **kwargs):
    """
    Generates a random news title for the given news_type.
    
    Args:
        news_type (str): The type of news ("milestone", "big_score", etc.).
        kwargs: Data to fill placeholders like player, team, score, etc.
    """
    templates = NEWS_TITLES.get(news_type, ["Unknown news"])
    template = random.choice(templates)

    return template.format(**kwargs)

def generate_news_detail(news_type, **kwargs):
    """
    Generates a random news detail for the given news_type.

    Args:
        news_type (str): The type of news ("milestone", "big_score", etc.).
        kwargs: Data to fill placeholders like player, team, score, etc.
    """
    templates = NEWS_DETAILS.get(news_type, ["Unknown news"])
    template = random.choice(templates)
    
    return template.format(**kwargs)

def check_league_changes(league_id, matchday, currDate):
    """
    Check for lead changes and relegation changes in a league.
    
    Args:
        league_id (int): The ID of the league to check.
    """

    from data.database import TeamHistory, Matches, LeagueNews, League
    
    changes = TeamHistory.check_league_changes(matchday, league_id)
                
    for change in changes:
        if change[2] == 1 and change[1] != 1:
            # Lead change
            match = Matches.get_team_last_match(change[0], currDate)
            LeagueNews.add_news("lead_change", (match.date + timedelta(days = 1)).replace(hour = 8, minute = 0, second = 0, microsecond = 0), league_id, match_id = match.id, team_id = change[0])

        elif change[2] > 17 and change[1] < 18 and League.calculate_league_depth(league_id) != 4:
            # Relegation change
            match = Matches.get_team_last_match(change[0], currDate)
            LeagueNews.add_news("relegation_change", (match.date + timedelta(days = 1)).replace(hour = 8, minute = 0, second = 0, microsecond = 0), league_id, match_id = match.id, team_id = change[0])

def get_overthrow_threshold(league_id):
    """
    Get a random threshold for overthrow events.
    """

    from data.database import Teams

    averages = Teams.get_average_current_ability_per_team(league_id)
    avg_ca = [e["avg_ca"] for e in averages.values()]

    league_spread = max(avg_ca) - min(avg_ca)
    overthrow_threshold = 0.55 * league_spread

    return overthrow_threshold