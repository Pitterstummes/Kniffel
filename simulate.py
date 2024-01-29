from multiprocess import Pool
import numpy as np
import time

scores = []


def do_all(input):
    # Load kniffel functions and run the game
    from kniffel_forimport import run_game

    return run_game(printscoreboard=False)


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
