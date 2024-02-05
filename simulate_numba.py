from multiprocess import Pool
import numpy as np
import time
from kniffel_forimport_numba import get_states, run_game
import pstats
import cProfile

""" Command for shell:
    import os
    os.chdir("C:\\Users\\paulk\\Documents\\Programmieren\\Python\\Kniffel")
    exec(open('simulate_numba.py').read())
"""

# start_time = time.time()


# def runall(n, stime=start_time):
#     scores = np.empty(n, dtype=int)
#     all_states = get_states()
#     print("Simulating", n, "Kniffel games using @jit...")
#     for i in range(n):
#         scores[i] = run_game(all_states)
#         if i == 1:
#             steptime1 = time.time()
#         if i == 2:
#             steptime2 = time.time()
#     compiletime = steptime1 - stime - (steptime2 - steptime1)
#     print("Compiletime:", np.round(compiletime, 2), "seconds")
#     return scores, stime, compiletime


# with cProfile.Profile() as pr:
#     scores, start_time, compiletime = runall(100)
# stats = pstats.Stats(pr)
# stats.sort_stats(pstats.SortKey.TIME)
# stats.print_stats()

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


def do_all(ins, states=all_states):
    # Load kniffel functions and run the game
    from kniffel_forimport_numba import run_game

    return run_game(states)


if __name__ == "__main__":
    # Run the game in parallel
    n = 1000
    print("Simulating", n, "Kniffel games in parallel...")
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
    print("Average score:", np.mean(scores))
    print("Highest score:", np.max(scores))
    print("Lowest score:", np.min(scores))
    print("Samples:", len(scores))
    print("Samples per second:", np.round(len(scores) / total_time, 2))
