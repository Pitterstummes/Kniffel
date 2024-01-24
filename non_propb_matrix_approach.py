from itertools import combinations, combinations_with_replacement, permutations
import numpy as np

def get_states(n, k):
    # Calculate possible states of n dice with k sides
    states = []
    dice = range(1, k+1)  
    for state in combinations_with_replacement(dice, n):
        states.append(state)
    return states

def count_numbers(numbers, k=6):
    # Count the number of occurrences of each number
    counts = [0] * k
    for num in numbers:
        counts[num - 1] += 1
    return counts

def get_combinations(state):
    # Get all rerolls of the state
    rerolls = []
    for length in range(len(state) + 1):
        for combination in combinations(state, length):
            if combination not in rerolls:
                rerolls.append(combination)
    return rerolls

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

def get_reroll_state_mask(state, rerolls, states):
    # Create a mask (matrix) to check if a state is reachable by a reroll
    mask = np.full((len(rerolls), len(states)), True)
    mask[0,:] = False
    for i, reroll in enumerate(rerolls[:-1]): 
        if len(reroll) == 0:
            mask[i,states.index(state)] = True
        else:
            modified_state = list(state)
            for value in reroll:
                modified_state.remove(value)
            for s in states:
                temp_state = list(s)
                for element in modified_state:
                    try:
                        temp_state.remove(element)
                    except ValueError:
                        mask[i,states.index(s)] = False
                        break                        
    return mask

states = get_states(5,6)
state = (1, 1, 1, 1, 1)
rerolls = get_combinations(state)
print(state)
print(rerolls)
print(states)
mask = get_reroll_state_mask(state, rerolls, states)
print(mask) 

    
