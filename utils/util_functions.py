import calendar
from datetime import timedelta
from settings import *
import random
import math

def get_objective_for_level(teamAverages, teamID):
    sorted_teams = sorted(teamAverages.items(), key = lambda x: x[1]["avg_ca"], reverse = True)
    teamRank = next((rank for rank, (tid, _) in enumerate(sorted_teams, start = 1) if tid == teamID), None)

    for (min_rank, max_rank), objective in OBJECTIVES.items():
        if min_rank <= teamRank <= max_rank:
            return objective

def generate_lower_div_objectives(min_level, max_level):
    range_size = (max_level - min_level) // 3
    return {
        (max_level, max_level - range_size): "secure promotion",
        (max_level - range_size - 1, max_level - 2 * range_size): "finish in the top half",
        (max_level - 2 * range_size - 1, min_level): "avoid relegation",
    }

def get_fan_reaction(result, expectation):
    """ Get the fan reaction based on match result and expectation level. """

    index = EXPECTATION_LEVELS.index(expectation)
    return FAN_REACTIONS.get(result, ["Unknown"] * 5)[index]

def get_expectation(team_avg, opponent_avg):
    """Determine expectation level based on team level difference."""
    level_diff = team_avg - opponent_avg
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

def get_player_ban(ban_type, curr_date):
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

    if role == "Star Player":
        return -5
    elif role == "First Team":
        return -3
    elif role == "Rotation":
        return -1
    
    return 0 # Backup keepers and youth players

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
    if time_str == "N/A":
        return float("inf") if not reverse else -float("inf")
    
    time_str = time_str.replace("'", "")

    parts = time_str.split("+")
    main_time = int(parts[0].strip())
    stoppage_time = int(parts[1].strip()) if len(parts) > 1 else 0
    return main_time + stoppage_time

def player_reaction(score_for: int, score_against: int, player_events: dict) -> str:
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
    for cond, color in REACTION_COLOURS:
        if cond(score):
            return color

def get_reaction_text(score):
    for cond, text in REACTION_TEXTS:
        if cond(score):
            return text
    return "N/A"

def get_prompt_reaction(prompt, score_for: int, score_against: int):
    if score_for > score_against:
        result = "win"
    elif score_for < score_against:
        result = "lose"
    else:
        result = "draw"

    return PROMPT_REACTIONS[prompt][result]

def reset_available_positions(lineup):
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
    if 10 <= number % 100 <= 20:
        return "th"
    else:
        return {1: "st", 2: "nd", 3: "rd"}.get(number % 10, "th")
    
def sort_time(time_str):
    """Convert time string to sortable number"""
    if "+" in time_str:
        # Handle injury time like "90+3"
        base_time, injury_time = time_str.split("+")
        return int(base_time) + int(injury_time) / 100  # Add injury time as decimal
    else:
        return int(time_str)
    
def create_rounded_rectangle(canvas, x1, y1, x2, y2, radius = 10, **kwargs):
    """Draw a rounded rectangle on the canvas."""
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

def generate_CA(age: int, team_strength: float, min_level: int = 150) -> int:
    """
    Generate a player's Current Ability (CA) based on age and team strength.
    Young players (<21) are very likely to be within +10 of min_level,
    but it's still (rarely) possible to exceed it.
    """
    max_level = min_level + 50
    CAs = list(range(min_level, max_level + 1))

    # Age factor & skew
    if age < 21:
        age_factor = 0.1 + 0.02 * age
        # Penalize CAs above +10 extra heavily
        def penalty(ca):
            if ca <= min_level + 10:
                return 1.0
            else:
                # exponential penalty for > +10
                return math.exp(-0.5 * (ca - (min_level + 10)))
        skew_power = 4  # strong bias toward low values
    elif age <= 25:
        age_factor = 1.15
        penalty = lambda ca: 1.0
        skew_power = 3
    elif age <= 30:
        age_factor = 1.05
        penalty = lambda ca: 1.0
        skew_power = 3
    else:
        age_factor = 0.9
        penalty = lambda ca: 1.0
        skew_power = 3

    # Skewed weights: lower CA more likely
    weights = [(max_level - ca + 1) ** skew_power * age_factor * penalty(ca)
               for ca in CAs]

    # Apply team strength: shift distribution toward higher CAs
    if team_strength != 1.0:
        scale = 15 * (team_strength - 1)
        weights = [w * math.exp(scale * ((ca - min_level) / (max_level - min_level)))
                   for ca, w in zip(CAs, weights)]

    level = random.choices(CAs, weights=weights, k=1)[0]
    return level

def generate_youth_player_level(max_level: int = 150) -> int:
    """
    Generate a youth player level between [max_level - 50, max_level].
    No role/age influence, just weighted by intervals (higher levels rarer).
    
    Args:
        max_level (int): The maximum possible level (capped at 200).
    
    Returns:
        int: The generated player level.
    """

    # Clamp max_level to 200
    max_level = min(max_level, 200)

    # Lower bound is max_level - 50, but not below 0
    min_level = max(max_level - 50, 0)

    # Build intervals of ~10 points
    intervals = []
    start = min_level
    while start < max_level:
        end = min(start + 10, max_level)
        intervals.append((start, end))
        start += 10

    # Default "youth" probability distribution (up to 5 intervals)
    base_probs = [30, 25, 20, 15, 10]  # favors lower end, rarer at the top

    # Trim to match number of intervals
    probs = base_probs[-len(intervals):]

    # Normalize to sum 1
    total = sum(probs)
    probs = [p / total for p in probs]

    # Choose interval
    chosen_interval = random.choices(intervals, weights = probs, k = 1)[0]

    # Pick uniformly inside interval
    return random.randint(chosen_interval[0], chosen_interval[1])

def calculate_potential_ability(age: int, CA: int) -> int:
    """
    Calculate Potential Ability (PA) based on age and CA.
    - Younger players can have huge jumps (wonderkids), but those are rarer.
    - Older players have small gaps.
    - PA capped at 200.
    """

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

    # Ensure min_gap never exceeds max_gap
    if min_gap > max_gap:
        min_gap = 0

    if max_gap <= 0:
        return CA  # already at cap or no growth possible

    # Build possible gaps
    gaps = list(range(min_gap, max_gap + 1))

    # Weighting: smaller gaps are more likely, big gaps rarer
    weights = [1 / (g + 1) for g in gaps]

    gap = random.choices(gaps, weights=weights, k=1)[0]

    return min(CA + gap, 200)

def star_images(star_rating: float):
    """
    Convert a star rating (0.5 to 5.0 in 0.5 increments) into counts of full, half, and empty stars.
    
    :param star_rating: float, e.g., 3.5
    :return: list of strings representing the stars, e.g., ["full", "full", "full", "half", "empty"]
    """

    full_stars = int(star_rating)
    half_star = 1 if (star_rating - full_stars) >= 0.5 else 0
    empty_stars = 5 - full_stars - half_star

    stars = []
    stars += ["star_full"] * full_stars
    stars += ["star_half"] * half_star
    stars += ["star_empty"] * empty_stars

    return stars

def expected_finish(team_name: str, team_scores: list) -> int:
    """
    Calculate expected league finish based on team scores.
    
    Args:
        team_name (str): Name of the team to calculate for.
        team_scores (list): List of tuples [(team_name, score), ...]
        
    Returns:
        int: Expected finishing position (1 = first place).
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
    days_ahead = (0 - date.weekday() + 7) % 7
    return date + timedelta(days = days_ahead)

def calculate_age(dob, today):
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

def player_gametime(avg_minutes, player):

    roles = {
        "Star Player": 50,
        "First Team": 30,
        "Rotation": 20
    }

    if avg_minutes < roles[player.player_role]:
        return True

    return False

def getFitnessDrop(player, fitness):

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
    day, _, _ = format_datetime_split(date)
    return list(calendar.day_name).index(day)

def ownGoalFoulWeight(p):
    # Lower ability and sharpness → higher chance
    ability_factor = (200 - p.current_ability) / 200.0
    sharpness_factor = (100 - p.sharpness) / 100.0

    # Combine factors
    base = 0.5 * ability_factor + 0.5 * sharpness_factor
    return max(base, 0.01)  # avoid zero probability

def fitnessWeight(p, fitness):
    # Low fitness → higher chance
    fitness_factor = (100 - fitness) / 100.0
    return max(fitness_factor, 0.01)  # avoid 0 prob

def goalChances(attackingLevel, defendingLevel, avgSharpness, avgMorale, oppKeeper):
    attackRatio = attackingLevel / max(1, defendingLevel)
    attackModifier = (avgSharpness / 100 + avgMorale / 100) / 2

    if oppKeeper:
        if oppKeeper.position == "goalkeeper":
            keeperModifier = (oppKeeper.current_ability / 200) * (oppKeeper.sharpness / 100)

            shot_base = BASE_SHOT * attackRatio * attackModifier
            shotProb = min(max(shot_base, 0.05), MAX_SHOT_PROB)

            onTarget_base = BASE_ON_TARGET * attackModifier
            onTargetProb = min(max(onTarget_base, 0.25), MAX_TARGET_PROB)

            goal_base = BASE_GOAL * attackModifier
            goalProb = goal_base * (1 - keeperModifier)
            goalProb = min(max(goalProb, 0.05), MAX_GOAL_PROB)
        else:
            # Outfield player in goal
            shotProb = min(max(BASE_SHOT * attackRatio * attackModifier * 1.2, 0.15), 0.7)
            onTargetProb = min(max(BASE_ON_TARGET * attackModifier * 1.2, 0.40), 0.8)
            goalProb = min(max(BASE_GOAL * attackModifier * 1.5, 0.50), 0.9)
    else:
        shotProb = min(max(BASE_SHOT * attackRatio * attackModifier * 1.5, 0.25), 0.75)
        onTargetProb = min(max(BASE_ON_TARGET * attackModifier * 1.5, 0.60), 0.85)
        goalProb = min(max(BASE_GOAL * attackModifier * 2.0, 0.80), 0.95)

    # Final distribution
    pNothing   = 1 - shotProb
    pShotOff   = shotProb * (1 - onTargetProb)
    pShotSaved = shotProb * onTargetProb * (1 - goalProb)
    pGoal      = shotProb * onTargetProb * goalProb

    events = ["nothing", "shot", "shot on target", "goal"]
    probs  = [pNothing, pShotOff, pShotSaved, pGoal]

    return random.choices(events, weights = probs, k = 1)[0]

def foulChances(avgSharpnessWthKeeper, severity):
    severity_map = {"low": 0.95, "medium": 1.0, "high": 1.05}
    severity = severity_map.get(severity, 1.0)

    gamma = 0.5
    sf = ((100.0 - max(0.0, min(99.9, avgSharpnessWthKeeper))) / 20.0) ** gamma

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

    events = ["nothing", "foul", "yellow_card", "red_card"]
    probs = [pNothing, foulProb, yellowProb, redProb]

    return random.choices(events, weights = probs, k = 1)[0]

def injuryChances(avgFitness):

    injuryProb = BASE_INJURY * (100 / avgFitness)
    injuryProb = min(max(injuryProb, 0.0001), MAX_INJURY_PROB)

    # --- Final event distribution ---
    pNothing = 1 - injuryProb
    pInjury = injuryProb

    events = ["nothing", "injury"]
    probs = [pNothing, pInjury]

    return random.choices(events, weights = probs, k = 1)[0]

def substitutionChances(lineup, subsMade, subs, events, currMinute, fitness):
    from data.database import Players
    subsAvailable = MAX_SUBS - subsMade

    # No substitutions possible
    if subsAvailable <= 0:
        return []

    # --- Step 1: build candidates ---
    candidates = []
    for pos, playerID in lineup.items():
        # check if this player has been on the pitch > 30 mins
        played_minutes = 0
        for event_time, event_data in events.items():
            if event_data["type"] == "substitution" and event_data["player_on"] == playerID:
                eventMinute = int(event_time.split(":")[0])
                played_minutes = currMinute - eventMinute
                break
        else:
            # started the match
            played_minutes = currMinute

        if played_minutes >= 30:
            prob = sub_probability(fitness[playerID])
            if prob > 0:
                has_replacement = any(POSITION_CODES[pos] in Players.get_player_by_id(pID).specific_positions.split(",") for pID in subs)

                if has_replacement:
                    candidates.append((prob, playerID, pos))

    if not candidates:
        return []
    
    # --- Step 2: sort by lowest fitness first ---
    candidates.sort(key = lambda x: fitness[x[1]])

    # --- Step 3: decide how many subs to attempt ---
    outcomes = [1, 2, 3]
    weights = [0.65, 0.25, 0.10]
    num_to_sub = random.choices(outcomes, weights = weights, k = 1)[0]

    # cannot sub more than available players or slots
    num_to_sub = min(num_to_sub, subsAvailable, len(candidates))

    # --- Step 4: roll substitutions ---
    chosen = []
    for prob, playerID, pos in candidates:
        if len(chosen) >= num_to_sub:
            break
        if random.random() < prob:
            chosen.append(playerID)

    return chosen

def sub_probability(fitness: float) -> float:
    if fitness > 50:
        return 0.0
    elif fitness > 20:
        # scales 50 -> 0%, 20 -> 60%
        return (50 - fitness) / 30 * 0.6
    elif fitness > 10:
        # scales 20 -> 60%, 10 -> 85%
        return 0.6 + (20 - fitness) / 10 * 0.25
    else:
        # below 10 -> 85–100%
        return 0.85 + (10 - max(fitness, 0)) / 10 * 0.15