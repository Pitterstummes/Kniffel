from itertools import combinations_with_replacement, permutations
import numpy as np


def calc_score_1_to_6(values, field):
    # Calculate the score for scoreboard indices 1 to 6: ones till sixes
    return sum(value for value in values if value == field)


def calc_score_10(values):
    # Calculate the score for scoreboard index 10: one pair
    pairs = []
    for value in set(values):
        if values.count(value) >= 2:
            pairs.append(value)
    if pairs:
        highest_pair = max(pairs)
        return highest_pair * 2
    else:
        return 0


def calc_score_11(values):
    # Calculate the score for scoreboard index 11: two pairs
    pairs = []
    for value in set(values):
        if values.count(value) >= 2:
            pairs.append(value)
    if len(pairs) >= 2:
        return sum(pairs) * 2
    else:
        return 0


def calc_score_12(values):
    # Calculate the score for scoreboard index 12: three of a kind
    for value in set(values):
        if values.count(value) >= 3:
            return value * 3
    return 0


def calc_score_13(values):
    # Calculate the score for scoreboard index 13: four of a kind
    for value in set(values):
        if values.count(value) >= 4:
            return value * 4
    return 0


def calc_score_14(values):
    # Calculate the score for scoreboard index 14: full house
    for value in set(values):
        if values.count(value) == 3:
            for value2 in set(values):
                if value2 != value and values.count(value2) == 2:
                    return 30
    return 0


def calc_score_15(values):
    # Calculate the score for scoreboard index 15: small street
    if set(values) in [{1, 2, 3, 4}, {2, 3, 4, 5}, {3, 4, 5, 6}]:
        return 25
    else:
        return 0


def calc_score_16(values):
    # Calculate the score for scoreboard index 16: big street
    if set(values) in [{1, 2, 3, 4, 5}, {2, 3, 4, 5, 6}]:
        return 40
    else:
        return 0


def calc_score_17(values):
    # Calculate the score for scoreboard index 17: kniffel
    for value in set(values):
        if values.count(value) == 5:
            return 50
    return 0


def calc_score_18(values):
    # Calculate the score for scoreboard index 18: chance
    return sum(values)


def calc_score_field(values, field):
    # Calculate the score for the given values and field
    match field:
        case 1:  # Ones
            return calc_score_1_to_6(values, 1)
        case 2:  # Twos
            return calc_score_1_to_6(values, 2)
        case 3:  # Threes
            return calc_score_1_to_6(values, 3)
        case 4:  # Fours
            return calc_score_1_to_6(values, 4)
        case 5:  # Fives
            return calc_score_1_to_6(values, 5)
        case 6:  # Sixes
            return calc_score_1_to_6(values, 6)
        case 10:  # One pair
            return calc_score_10(values)
        case 11:  # Two pairs
            return calc_score_11(values)
        case 12:  # Three of a kind
            return calc_score_12(values)
        case 13:  # Four of a kind
            return calc_score_13(values)
        case 14:  # Full house
            return calc_score_14(values)
        case 15:  # Small street
            return calc_score_15(values)
        case 16:  # Big street
            return calc_score_16(values)
        case 17:  # Kniffel
            return calc_score_17(values)
        case 18:  # Chance
            return calc_score_18(values)
        case _:  # Invalid field
            raise TypeError("Invalid field")


def get_states(n, k):
    # Calculate the amount and possible states of n dice with k sides
    states = []
    dice = range(1, k + 1)
    for state in combinations_with_replacement(dice, n):
        states.append(state)
    return len(states), states


def compare_states(start_state, goal_state):
    # Compare start and goal state (tuples), return number of dice to reroll (output1) and number of permutations (output2) for propability calculation
    start_dice = list(start_state)
    goal_dice = list(goal_state)
    for element in start_state:
        if element in goal_dice:
            start_dice.remove(element)
            goal_dice.remove(element)

    all_permutations = set(permutations(goal_dice, len(goal_dice)))
    return len(goal_dice), start_dice, len(all_permutations)


def get_decision_parameters(input_state, fields, maxpoints, n=5, k=6):
    # Calculate the propability of the input state
    number_of_states, states = get_states(n, k)
    propability = [0.0 for _ in range(number_of_states)]
    reroll_dice_list = [[None] * 1 for _ in range(number_of_states)]
    for i, state in enumerate(states):
        number_of_reroll_dice, reroll_dice, number_of_permutations = compare_states(
            input_state, state
        )
        if number_of_reroll_dice == 0:
            propability[i] = 1.0
        else:
            propability[i] = (1 / k) ** number_of_reroll_dice * number_of_permutations
        reroll_dice_list[i] = reroll_dice
        potential_points = 0
        for field in fields:
            currentpoints = calc_score_field(state, field)
            potential_points += (
                currentpoints / (maxpoints[field - 1] ** 1) * currentpoints
            )
        propability[i] *= potential_points

    return propability, reroll_dice_list


def get_decision(propability, reroll_dice):
    # Calculate the decision based on the propability
    unique_reroll_dice = []
    for i in reroll_dice:
        if i not in unique_reroll_dice:
            unique_reroll_dice.append(i)
    propscores = [0] * len(unique_reroll_dice)
    for i in range(len(unique_reroll_dice)):
        indices = [
            index
            for index, value in enumerate(reroll_dice)
            if value == unique_reroll_dice[i]
        ]
        for matching_index in indices:
            propscores[i] += propability[matching_index]
    return unique_reroll_dice, propscores


# maxpoints = [5, 10, 15, 20, 25, 30]
# propability, reroll_dice = get_decision_parameters((5, 5, 5, 5, 4), [1], maxpoints)
# unique_reroll_dice, propscores = get_decision(propability, reroll_dice)
# for i,j in enumerate(unique_reroll_dice):
#     print(j, propscores[i])

## TODO: Find better algorithm for potential points! - or fix analog statements in transitions

maxpoints = [3, 6, 9]
propability, reroll_dice = get_decision_parameters(
    (1, 2, 3), [1, 2, 3], maxpoints, 3, 3
)
unique_reroll_dice, propscores = get_decision(propability, reroll_dice)
for i, j in enumerate(unique_reroll_dice):
    print(j, propscores[i])
