from numpy import eye
from itertools import product, permutations

def get_states(n, k):
    # Calculate the amount (output1) and possible states (output2) of n dice with k sides
    dice = range(1, k+1)  # Create a list of possible dice outcomes
    all_states = list(product(dice, repeat=n))  # Generate all states of n dice with repeated elements
    unique_states = set(tuple(sorted(comb)) for comb in all_states)  # Remove duplicates by sorting and converting to tuple
    return len(unique_states), sorted(unique_states)

def compare_states(start_state, goal_state):
    # Compare start and goal state (tuples), return number of dice to reroll (output1) and number of permutations (output2) for propability calculation
    goal_dice = list(goal_state)
    for element in start_state:
        if element in goal_dice:
            goal_dice.remove(element)
    
    all_permutations = set(list(permutations(goal_dice, len(goal_dice))))
    return len(goal_dice), len(all_permutations)

def calculate_propability_matrix(n=5, k=6):
    # Calculate the transition probability matrix for all states resulting from n dice with k sides
    number_of_states, states = get_states(n, k)
    transitionmatrix = eye(number_of_states, dtype=float) # Create a matrix with zeros and ones on the diagonal
    for row in range(number_of_states):
        for col in range(number_of_states):
            # Loop over non diagonal cells
            if row != col:
                number_of_reroll_dice, number_of_permutations = compare_states(states[row], states[col])
                transitionmatrix[row, col] = (1/k)**number_of_reroll_dice*number_of_permutations
    return transitionmatrix, states

matrix, states = calculate_propability_matrix()
print(states, matrix, sep="\n")
print("Done!, there are {} states".format(len(states)))