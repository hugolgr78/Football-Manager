import calendar, math, random, json
from datetime import timedelta
from settings import *

def get_objective_for_level(teamAverages, teamID):
    sorted_teams = sorted(teamAverages.items(), key = lambda x: x[1]["avg_ca"], reverse = True)
    teamRank = next((rank for rank, (tid, _) in enumerate(sorted_teams, start = 1) if tid == teamID), None)

    for (min_rank, max_rank), objective in OBJECTIVES.items():
        if min_rank <= teamRank <= max_rank:
            return objective


def append_overlapping_profile(start, profile):
    """Safely append a profile frame to the nearest overlappingProfiles container.

    Walks up common parent attributes (parent, parentTab) looking for an
    object with an 'overlappingProfiles' list. If none is found, creates the
    list on the top-most parent and appends there. This centralises the logic
    so other modules don't have to repeat parent-walking code.
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

def fitnessWeight(fitness):
    # Low fitness → higher chance
    fitness_factor = (100 - fitness) / 100.0
    return max(fitness_factor, 0.01)  # avoid 0 prob

def goalChances(attackingLevel, defendingLevel, avgSharpness, avgMorale, oppKeeper, goalBoost = 1.0):
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

    return random.choices(events, weights=probs, k=1)[0]

def foulChances(avgSharpnessWthKeeper, severity):
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

def sub_probability(fitness: float, rating: float) -> float:
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
    # weights: morale 20%, fitness 40%, sharpness 40%
    weighted = (0.2 * p.morale + 0.4 * p.fitness + 0.4 * p.sharpness) / 100.0
    multiplier = 0.75 + (weighted * 0.5)
    return p.current_ability * multiplier

def getStatNum(stat):
    return sum(playerValue for playerValue in stat.values())

def passesAndPossession(matchInstance):
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

    for k, v in values_dict.items():
        new_val = v + amount

        if min_value is not None and new_val < min_value:
            new_val = min_value
        if max_value is not None and new_val > max_value:
            new_val = max_value

        values_dict[k] = int(round(new_val))

    return values_dict

def update_fitness_dict_values(values_dict, amount, min_value = None, max_value = None):

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
    teamOBJs = []

    for team in jsonData:
        if team["league"] == leagueName:
            teamOBJs.append(team)

    return teamOBJs

def run_match_simulation(interval, currDate, exclude_leagues = []):
    from data.database import Matches, Managers, League, LeagueTeams, PlayerBans, TeamHistory, process_payload, check_player_games_happy
    from concurrent.futures import ProcessPoolExecutor, as_completed
    import os, time, logging, glob, traceback

    _logger = logging.getLogger(__name__)

    matchesToSim = Matches.get_matches_time_frame(interval[0], interval[1], exclude_leagues)
    worker_payloads = []
    if matchesToSim:
        total_to_sim = len(matchesToSim)
        _logger.info("Preparing to simulate %d matches", total_to_sim)
        _logger.info("Starting match initialization")

        CHUNK_SIZE = min(len(matchesToSim), os.cpu_count())
        total_batches = (total_to_sim + CHUNK_SIZE - 1) // CHUNK_SIZE

        _logger.info("Starting parallel match simulation in up to %d batches (chunk=%d)", total_batches, CHUNK_SIZE)

        sim_start = time.perf_counter()

        # Run batches sequentially to respect the maximum worker count
        matches = []
        teams = {}
        mgr = Managers.get_all_user_managers()[0]
        base_name = f"{mgr.first_name}{mgr.last_name}"

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
                for team in LeagueTeams.get_teams_by_league(id_):
                    matchday = League.get_current_matchday(id_)
                    TeamHistory.add_team(matchday, team.team_id, team.position, team.points)

                League.update_current_matchday(id_)
            _logger.debug(f"Updated league standings and matchdays for league {id_}")

        _logger.debug("Starting suspension reductions for %d leagues", len(teams))
        PlayerBans.reduce_suspensions_for_teams(teams)
        _logger.debug("Completed suspension reductions for teams")

def _init_worker(base_name):
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