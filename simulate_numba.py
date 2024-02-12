from multiprocess import Pool
import numpy as np
import time
from kniffel_forimport_numba import get_states, run_game

""" Command for shell:
    import os
    os.chdir("C:\\Users\\paulk\\Documents\\Programmieren\\Python\\Kniffel")
    exec(open('simulate_numba.py').read())
"""

# start_time = time.time()


# n = 10000
# scores = np.empty(n, dtype=int)
# all_states = get_states()
# print("Simulating", n, "Kniffel games using @jit...")
# for i in range(n):
#     scores[i] = run_game(all_states)
#     if i == 1:
#         steptime1 = time.time()
#     if i == 2:
#         steptime2 = time.time()
#         compiletime = steptime1 - start_time - (steptime2 - steptime1)
#         print("Compiletime:", np.round(compiletime, 2), "seconds")

# stop_time = time.time()

# total_time = stop_time - start_time
# hours = int(total_time // 3600)
# minutes = int((total_time % 3600) // 60)
# seconds = int(total_time % 60)
# print("Total time:", f"{hours:02d}:{minutes:02d}:{seconds:02d}")
# print("Average score:", np.mean(scores))
# print("Highest score:", np.max(scores))
# print("Lowest score:", np.min(scores))
# print("Samples:", len(scores))
# print("Samples per second:", np.round(len(scores) / (total_time - compiletime), 2))

scores = []
all_states = get_states()
optimizer = np.array(
    [1, 1, 1, 1, 1.05, 1.1, 0.4, 0.8, 0.9, 1, 0.5, 0.4, 1, 1, 0.45], dtype=np.float32
)


def do_all(ins, states=all_states, optim=optimizer):
    # Load kniffel functions and run the game
    from kniffel_forimport_numba import run_game

    return run_game(states, optim)


if __name__ == "__main__":
    # Run the game in parallel
    n = 2000000
    print("Simulating", n, "Kniffel games in parallel using @jit...")
    start_time = time.time()
    iterations = [1 for _ in range(n)]
    p = Pool()
    scores = p.map(do_all, iterations)
    p.close()
    p.join()

    stop_time = time.time()
    total_time = stop_time - start_time
    hours = int(total_time // 3600)
    minutes = int((total_time % 3600) // 60)
    seconds = int(total_time % 60)
    print("Total time:", f"{hours:02d}:{minutes:02d}:{seconds:02d}")
    print("Average score:", np.round(np.mean(scores), 2))
    print("Median score:", np.median(scores))
    print("Highest score:", np.max(scores))
    print("Lowest score:", np.min(scores))
    print("Samples:", len(scores))
    print("Samples per second:", np.round(len(scores) / total_time, 2))
    np.savetxt("scores.txt", scores)
