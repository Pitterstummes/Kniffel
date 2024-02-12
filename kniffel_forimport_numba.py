import random
from itertools import combinations_with_replacement
import numpy as np
from numba import jit, objmode
import time


@jit(nopython=True)
def init():
    # Initialize scoreboard, freefields and decisionlists
    scoreboard = np.empty(20, dtype=np.int16)
    scoreboard[:] = -1
    freefields = np.array(
        [0, 1, 2, 3, 4, 5, 9, 10, 11, 12, 13, 14, 15, 16, 17], dtype=np.uint8
    )
    maxpoints = np.array(
        [5, 10, 15, 20, 25, 30, 12, 22, 18, 24, 30, 25, 40, 50, 30], dtype=np.uint8
    )
    optimizer = np.array(
        [1, 1, 1, 1, 1, 1, 0.4, 0.8, 1, 1, 0.5, 0.4, 1, 1, 0.5], dtype=np.float32
    )
    return scoreboard, freefields, maxpoints  # optimizer


@jit(nopython=True)
def first_roll(n=5, k=6):
    # Generate random integers for the first roll
    return np.sort(np.random.randint(1, k + 1, n))


@jit(nopython=True)
def update_scoreboard(scoreboard, field, points):
    # Update the score for the given field
    if scoreboard[field] == -1:
        scoreboard[field] = points
    else:
        scoreboard[field] += points
    return scoreboard


@jit(nopython=True)
def update_freefields(freefields, field):
    # Find the index of the field to remove
    index = np.where(freefields == field)[0][0]
    # Remove the field from the list
    freefields = np.delete(freefields, index)
    return freefields


@jit(nopython=True)
def calculate_scores(fields):
    # Calculate the sum, bonus, and total scores based on the individual fields
    fields[6] = np.sum(fields[0:6])
    if fields[6] >= 63:
        fields[7] = 37
    else:
        fields[7] = 0
    fields[8] = fields[6] + fields[7]
    fields[18] = np.sum(fields[9:18])
    fields[19] = fields[8] + fields[18]
    return fields


@jit(nopython=True)
def calc_score_1_to_6(values, field):
    # Calculate the score for scoreboard indices 1 to 6: ones till sixes
    return np.sum(values[values == field])


@jit(nopython=True)
def calc_score_10(values):
    # Calculate the score for scoreboard index 10: one pair
    counts = np.zeros(6, dtype=np.uint8)
    for value in values:
        counts[value - 1] += 1
    max_value = 0
    for index in range(6):
        if counts[index] >= 2 and index + 1 > max_value:
            max_value = index + 1
    return 2 * max_value


@jit(nopython=True)
def calc_score_11(values):
    # Calculate the score for scoreboard index 11: two pairs
    counts = np.zeros(6, dtype=np.uint8)
    for value in values:
        counts[value - 1] += 1
    pairs = []
    for index in range(6):
        if counts[index] >= 2:
            pairs.append(index + 1)
    if len(pairs) == 2:
        return sum(pairs) * 2
    else:
        return 0


@jit(nopython=True)
def calc_score_12(values):
    # Calculate the score for scoreboard index 12: three of a kind
    counts = np.zeros(6, dtype=np.uint8)
    for value in values:
        counts[value - 1] += 1
    for i in range(6):
        if counts[i] >= 3:
            return (i + 1) * 3
    return 0


@jit(nopython=True)
def calc_score_13(values):
    # Calculate the score for scoreboard index 13: four of a kind
    counts = np.zeros(6, dtype=np.uint8)
    for value in values:
        counts[value - 1] += 1
    for i in range(6):
        if counts[i] >= 4:
            return (i + 1) * 4
    return 0


@jit(nopython=True)
def calc_score_14(values):
    # Calculate the score for scoreboard index 14: full house
    counts = np.zeros(6, dtype=np.uint8)
    for value in values:
        counts[value - 1] += 1
    if 3 in counts and 2 in counts:
        return 30
    return 0


@jit(nopython=True)
def calc_score_15(values):
    # Calculate the score for scoreboard index 16: small straight
    valid_values = np.array([[1, 2, 3, 4], [2, 3, 4, 5], [3, 4, 5, 6]])
    for group in valid_values:
        count = 0
        for element in group:
            if element in values:
                count += 1
        if count == 4:
            return 25
    return 0


@jit(nopython=True)
def calc_score_16(values):
    # Calculate the score for scoreboard index 16: big straight
    valid_values = np.array([[1, 2, 3, 4, 5], [2, 3, 4, 5, 6]])
    for group in valid_values:
        count = 0
        for element in group:
            if element in values:
                count += 1
        if count == 5:
            return 40
    return 0


@jit(nopython=True)
def calc_score_17(values):
    # Calculate the score for scoreboard index 17: kniffel
    counts = np.zeros(6, dtype=np.uint8)
    for value in values:
        counts[value - 1] += 1
    if 5 in counts:
        return 50
    return 0


@jit(nopython=True)
def calc_score_18(values):
    # Calculate the score for scoreboard index 18: chance
    return np.sum(values)


@jit(nopython=True)
def calc_score_field(values, field):
    # Calculate the score for the given values and field
    match field + 1:  # due to removed name in scoreboard at index 0
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
        case 15:  # Small straight
            return calc_score_15(values)
        case 16:  # Big straight
            return calc_score_16(values)
        case 17:  # Kniffel
            return calc_score_17(values)
        case 18:  # Chance
            return calc_score_18(values)


def get_states(n=5, k=6):
    # Calculate possible states of n dice with k sides
    states = np.empty((252, 5), dtype=np.uint8)
    dice = range(1, k + 1)
    for i, state in enumerate(combinations_with_replacement(dice, n)):
        states[i, :] = state
    return states


@jit(nopython=True)
def get_rerolls(state):
    # Get all rerolls of the state
    state_count = np.zeros((6), dtype=np.uint8)
    for roll in state:  # Get the counts of the state
        state_count[roll - 1] += 1
    # Initialize
    reroll_counts = np.zeros((1, 6), dtype=np.uint8)
    append_count = np.zeros(6, dtype=np.uint8)
    indices = np.where(state_count > 0)[0]
    limits = state_count[indices]
    append_count = np.zeros(6, dtype=np.uint8)
    current_index = 0
    max_index = 0
    while np.array_equal(append_count, state_count) == False:
        # Generate all unique reroll counts
        append_count[indices[current_index]] += 1
        for i, index in enumerate(indices):
            if append_count[index] > limits[i]:
                append_count[: index + 1] = 0
                append_count[indices[i + 1]] += 1
                current_index = 0
        if current_index == max_index:
            max_index += 1
            current_index = 0
        reroll_counts = np.concatenate(
            (reroll_counts, append_count.reshape(1, -1)), axis=0
        )
    # below works, TODO: review and optimize
    rerolls = np.zeros((len(reroll_counts), 5), dtype=np.uint8)
    for i, reroll_count in enumerate(reroll_counts):
        state = []
        for j, count in enumerate(reroll_count):
            state.extend([j + 1] * count)
        rerolls[i, : len(state)] = np.array(state, dtype=np.uint8)
    return rerolls


@jit(nopython=True)
def factorial(n):
    # Calculate the factorial of a number
    if n == 0:
        return 1
    else:
        return n * factorial(n - 1)


@jit(nopython=True)
def unique_permutations(state):
    # Calculate the number of unique permutations of the state
    counts = np.zeros((6), dtype=np.uint8)
    for roll in state:
        counts[roll - 1] += 1
    divider = 1
    for count in counts:
        if count > 1:
            divider *= factorial(count)
    return int(factorial(len(state)) / divider)


@jit(nopython=True)
def get_reroll_state_propability(state, rerolls, states, n=5, k=6):
    # Calculate propabilities for each state after rerolling
    propability = np.ones((len(rerolls), len(states)))
    propability[0, :] = 0
    for i, reroll in enumerate(rerolls[:-1]):
        # Reroll nothing
        if np.array_equal(reroll, np.array([0, 0, 0, 0, 0])):
            for j, s in enumerate(states):
                if np.array_equal(s, state):
                    propability[i, j] = 1
                    break
        else:  # Reroll not all
            keep_dice = np.copy(state)
            for value in reroll:
                if value != 0:
                    remove_index = np.argwhere(keep_dice == value)[0]
                    keep_dice = np.delete(keep_dice, remove_index)
            for j, s in enumerate(states):
                reach_dice = np.copy(s)
                for element in keep_dice:
                    if element in reach_dice:
                        remove_index = np.argwhere(reach_dice == element)[0]
                        reach_dice = np.delete(reach_dice, remove_index)
                    else:
                        propability[i, j] = 0
                        break
                if propability[i, j] != 0:
                    propability[i, j] = (1 / k) ** len(
                        reach_dice
                    ) * unique_permutations(reach_dice)
    # Reroll all
    for j, s in enumerate(states):
        propability[-1, j] = (1 / k) ** n * unique_permutations(s)
    return propability


@jit(nopython=True)
def collect_decision_parameters(
    input_state, fields, maxpoints, optimizer, states, n=5, k=6
):
    # Collect decision parameters for the reroll decision
    rerolls = get_rerolls(input_state)
    propabilities = get_reroll_state_propability(input_state, rerolls, states)
    decision_score_matrix = np.zeros_like(propabilities)
    decision_score = np.zeros(len(rerolls))
    for i, reroll in enumerate(rerolls):
        for j, state in enumerate(states):
            if propabilities[i, j] != 0:
                potential_points = 0
                for field in fields:
                    currentpoints = calc_score_field(state, field)
                    potential_points += calculate_potential(
                        currentpoints, maxpoints, field, optimizer
                    )
                decision_score_matrix[i, j] = potential_points * propabilities[i, j]
        decision_score[i] = np.sum(decision_score_matrix[i, :])
    index = np.argmax(decision_score)
    return rerolls[index]


@jit(nopython=True)
def reroll_state(state, reroll_dice, n=5, k=6):
    # Reroll the state given the dice to reroll
    for element in reroll_dice:
        if element != 0:
            remove_index = np.argwhere(state == element)[0]
            state[remove_index] = random.randint(1, k)
    return np.sort(state)


@jit(nopython=True)
def find_best_score(freefields, roll, maxpoints, optimizer):
    # Find the best score for the given roll, output points and field
    current_points = np.zeros(len(freefields))
    potential_points = np.zeros(len(freefields))
    for i, field in enumerate(freefields):
        points = calc_score_field(roll, field)
        current_points[i] = points
        potential_points[i] += calculate_potential(points, maxpoints, field, optimizer)
    index = np.argmax(potential_points)
    return int(current_points[index]), freefields[index]


@jit(nopython=True)
def run_game(
    all_states,
    optimizer,
    throws=3,
    n=5,
    k=6,
):
    # Run a game of Kniffel
    scoreboard, freefields, maxpoints = init()  # optimizer
    count_round = 0
    while count_round < 15:
        count_round += 1
        roll = first_roll(n, k)
        for i in range(throws - 1):
            reroll_dice = collect_decision_parameters(
                roll, freefields, maxpoints, optimizer, all_states
            )
            roll = reroll_state(roll, reroll_dice)
        writepoints, field = find_best_score(freefields, roll, maxpoints, optimizer)
        scoreboard = update_scoreboard(scoreboard, field, writepoints)
        if writepoints == 50:
            if scoreboard[field] > 50:
                kniffelindex = np.argwhere(freefields == 16)[0][0]
                nokniffel_freefields = np.copy(freefields)
                nokniffel_freefields = np.delete(nokniffel_freefields, kniffelindex)
                writepoints, field = find_best_score(
                    nokniffel_freefields,
                    roll,
                    maxpoints,
                    optimizer,
                )
                scoreboard = update_scoreboard(scoreboard, field, writepoints)
                freefields = update_freefields(freefields, field)
        else:
            freefields = update_freefields(freefields, field)
    scoreboard = calculate_scores(scoreboard)
    if scoreboard[19] >= 616 or scoreboard[19] <= 75:
        with objmode:
            file = open("kniffel_scoreboard.csv", "a")
            np.savetxt(file, scoreboard, delimiter=",")
            file.close()
    return scoreboard[19]


@jit(nopython=True)
def calculate_potential(currentpoints, maxpoints, field, optimizer):
    # Calculate the potential points for the given field
    if field > 5:
        field = field - 3
    return currentpoints**2 / (maxpoints[field] ** 1) * optimizer[field]
