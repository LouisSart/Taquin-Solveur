import time
from Solver import *


def time_algorithms(puzzle, algorithms):
    times = []
    for algorithm in algorithms:
        tic = time.time()
        solutions = algorithm(Node(puzzle))
        tac = time.time()
        times.append(tac-tic)
    return tuple(times)
