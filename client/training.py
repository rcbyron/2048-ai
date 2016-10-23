""" Used for training hyperparameters and running multiple simulations """
import time

from threading import Thread
from ai import simulate, show

# # Tuning parameters and weights
# MAX_DEPTH = 4
# EMPTY_TILE_POINTS = 12
# SMOOTHNESS_WEIGHT = 30
# EDGE_WEIGHT = 30
# LOSS_PENALTY = -200000
# MONOTONICITY_POWER = 3.0
# MONOTONICITY_WEIGHT = 27.0
# SUM_POWER = 3.5
# SUM_WEIGHT = 11.0
# EMPTY_WEIGHT = 270.0

test_cases = 10
best_board = 0
best_score = 0
best_moves = 0
avg_score = 0
avg_moves = 0
prog = 0


def progress_bar():
    """ Increments the progress indicator """
    global prog
    prog += 1
    print(str((prog/test_cases)*100)+"%")


def worker():
    """ Runs a simulation on a seprate thread and records statistics """
    global avg_moves, avg_score, best_board, best_score, best_moves
    board, s, m = simulate()
    avg_score += s
    avg_moves += m
    if s > best_score:
        best_board = board
        best_score = s
        best_moves = m
    progress_bar()


def multi_simulate():
    """ Runs multiple simulation worker threads and reports results """
    start_time = time.clock()
    workers = []
    print("0%")
    for i in range(0, test_cases):
        t = Thread(target=worker, args=())
        t.start()
        workers.append(t)

    """ Block until all threads finished """
    for w in workers:
        w.join()

    print("\nBest Score:", best_score, "Best Moves:", best_moves)
    show(best_board, show_best_tile=True)
    print("\nAvg Score:", (avg_score/test_cases), "Avg Moves:", (avg_moves/test_cases))
    print("Time:", (time.clock()-start_time), "seconds")

multi_simulate()
