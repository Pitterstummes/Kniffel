from multiprocess import Pool
import numpy as np
import time
from kniffel_forimport_numba import get_states

""" Simulate games and optimize the weights for the kniffel game
    -> changes in the average seem to be too noisy, median changes are small, try other approach
    
"""

all_states = get_states()
if __name__ == "__main__":
    # Run the game in parallel
    n = 100000
    iterations = [1 for _ in range(n)]
    # Initialize variables
    print("Initializing variables")
    scores = []
    optimizer = np.array(
        [1, 1, 1, 1, 1, 1, 0.4, 0.8, 1, 1, 0.5, 0.4, 1, 1, 0.5], dtype=np.float32
    )
    positions = np.array(
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14], dtype=np.int32
    )
    position = 0
    remove_count = np.zeros(15, dtype=np.int32)
    initial_median = 243.0
    initial_mean = 253.95
    increase = True

    def do_all(ins, states=all_states, optim=optimizer):
        # Load kniffel functions and run the game
        from kniffel_forimport_numba import run_game

        return run_game(states, optim)

    print("Starting optimization")
    while True:
        # Optimize the weights for each run of n iterations
        start_time = time.time()
        optimvalue = optimizer[positions[position]]
        if increase:
            optimizer[positions[position]] = optimvalue * 1.2
            increase = False
        else:
            optimizer[positions[position]] = optimvalue * 0.8
            increase = True
        p = Pool()
        scores = p.map(do_all, iterations)
        p.close()
        p.join()
        # Calculate median and mean of scores and update if better
        median_score = np.round(np.median(scores), 2)
        mean_score = np.round(np.mean(scores), 2)
        # Create new array with median, mean, and optimizer values
        avg_optim_array = np.concatenate(([median_score], [mean_score], optimizer))
        avg_optim_array = np.around(avg_optim_array, 2)
        deleted = False
        stop_time = time.time()
        print(
            f"Median: {median_score}, Mean: {mean_score}, Time: {int((stop_time - start_time)//60)}m {int(np.round((stop_time - start_time)%60, 0))}s"
        )
        print(optimizer)
        if median_score <= initial_median:
            optimizer[positions[position]] = optimvalue
            remove_count[positions[position]] += 1
            # print(f"Remove count: {remove_count[positions[position]]}")
            if remove_count[positions[position]] == 2:
                deleted = True
                # print("Positions before delete: ", positions)
                # print("Old position: ", position, "of positions: ", positions[position])
                positions = np.delete(positions, position)
                # print("Positions after delete: ", positions)
                # print("New position: ", position, "of positions: ", positions[position])
        else:
            initial_median = median_score
            initial_mean = mean_score
            if not increase:
                increase = True

        # Open file in append mode
        with open("avg_optimizer.txt", "a") as file:
            # Write array to file
            np.savetxt(file, [avg_optim_array], delimiter=",")

        # Close the file
        file.close()

        # Update position
        if increase:
            if not deleted:
                position += 1
            if position >= len(positions):
                position = 0
            remove_count = np.zeros(15, dtype=np.int32)
