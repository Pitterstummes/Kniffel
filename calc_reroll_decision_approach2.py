from itertools import combinations, combinations_with_replacement, permutations
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
        case 1:     # Ones 
            return calc_score_1_to_6(values, 1)
        case 2:     # Twos
            return calc_score_1_to_6(values, 2)
        case 3:     # Threes
            return calc_score_1_to_6(values, 3)
        case 4:     # Fours
            return calc_score_1_to_6(values, 4)
        case 5:     # Fives    
            return calc_score_1_to_6(values, 5)
        case 6:     # Sixes
            return calc_score_1_to_6(values, 6)
        case 10:    # One pair
            return calc_score_10(values)
        case 11:    # Two pairs
            return calc_score_11(values)
        case 12:    # Three of a kind
            return calc_score_12(values)
        case 13:    # Four of a kind
            return calc_score_13(values)
        case 14:    # Full house
            return calc_score_14(values)
        case 15:    # Small street
            return calc_score_15(values)
        case 16:    # Big street
            return calc_score_16(values)
        case 17:    # Kniffel
            return calc_score_17(values)
        case 18:    # Chance
            return calc_score_18(values)
        case _:     # Invalid field
            raise TypeError("Invalid field")

def get_states(n=5, k=6):
    # Calculate possible states of n dice with k sides
    states = []
    dice = range(1, k+1)  
    for state in combinations_with_replacement(dice, n):
        states.append(state)
    return states

def get_combinations(state):
    # Get all rerolls of the state
    rerolls = []
    for length in range(len(state) + 1):
        for combination in combinations(state, length):
            if combination not in rerolls:
                rerolls.append(combination)
    return rerolls

def get_reroll_state_propability(state, rerolls, states, n=5, k=6):
    # Calculate propabilities for each state after rerolling
    propability = np.ones((len(rerolls), len(states)))
    propability[0,:] = 0
    for i, reroll in enumerate(rerolls[:-1]): 
        if len(reroll) == 0:
            propability[i,states.index(state)] = 1
        else:
            keep_dice = list(state)
            for value in reroll:
                keep_dice.remove(value)
            for s in states:
                reach_dice = list(s)
                for element in keep_dice:
                    try:
                        reach_dice.remove(element)
                    except ValueError:
                        propability[i,states.index(s)] = 0
                        break 
                if propability[i,states.index(s)] != 0:
                    variants = set(permutations(reach_dice, len(reach_dice)))
                    propability[i,states.index(s)] = (1/k)**len(reach_dice)*len(variants)
    for s in states:
        variants = set(permutations(s, n))
        propability[-1,states.index(s)] = (1/k)**n*len(variants)
    return propability

def calculate_potential(currentpoints, maxpoints, field):
    return currentpoints / (maxpoints[field-1]**1) * currentpoints

def collect_decision_parameters(input_state, fields, maxpoints, n=5, k=6):
    states = get_states(n, k)
    rerolls = get_combinations(input_state)
    propabilities = get_reroll_state_propability(input_state, rerolls, states)
    decision_score_matrix = np.zeros_like(propabilities)
    decision_score = np.zeros(len(rerolls))
    for i, reroll in enumerate(rerolls):
        for j, state in enumerate(states):
            if propabilities[i,j] != 0:
                potential_points = 0
                for field in fields:
                    currentpoints = calc_score_field(state, field)
                    potential_points += calculate_potential(currentpoints, maxpoints, field)
                decision_score_matrix[i,j] = potential_points * propabilities[i,j]
        decision_score[i] = np.sum(decision_score_matrix[i,:])
        print(reroll, decision_score[i])
    index = np.argmax(decision_score)
    return rerolls[index]

# find the best calculate_potential method: highest score gives the reroll
maxpoints = [5, 10, 15, 20, 25, 30]
openfields = [1, 2, 3, 4, 5, 6]
reroll = collect_decision_parameters((3, 4, 4, 5, 5), openfields, maxpoints)  
print(reroll)