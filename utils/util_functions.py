from settings import *
import random

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