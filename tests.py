import time
from EpicSolver.heuristics import *
from EpicSolver.solver import *
from EpicSolver.taquin import *

easy = Taquin((3,3), [[4, 3, 2], [1, 7, 5], [6, 8, 0]]) # Has two optimal solutions in 8 moves
hard = Taquin((3,3), [[4, 7, 6], [5, 1, 8], [0, 3, 2]]) # Has nine optimal solutions in 28 moves
hard44 = Taquin((4,4), [[2, 4, 7, 8], [10, 13, 6, 3], [5, 0, 1, 14], [12, 11, 9, 15]]) # Has five optimal solutions in 45 moves
easy44 = Taquin((4,4), [[14, 1, 9, 6], [4, 8, 12, 5], [7, 2, 3, 0], [10, 11, 13, 15]]) # Has one optimal solution in 45 moves

def time_solvers(puzzles, *solvers):

    def time_this_puzzle(puzzle, solvers):
        times = []
        for solver in solvers:
            tic = time.process_time()
            solver.solve(puzzle)
            tac = time.process_time()
            times.append(tac-tic)
        return tuple(times)

    times = []
    for puzzle in puzzles:
        times.append(time_this_puzzle(puzzle, solvers))
    return times

def run_solvers(puzzle, *solvers):

    for solver in solvers:

        solver.solve(puzzle)
        solver.print_solutions()


if __name__ == "__main__":
    print("Running solvers for easy 3x3 position :")
    print(easy)
    run_solvers(
        easy,
        BFS(),
        Astar(heuristic=Manhattan()),
    )
    print ("*"*30)
    print("\nRunning solvers for hard 3x3 position :")
    print(hard)
    run_solvers(
        hard,
        Astar(heuristic=Manhattan()),
        DFS(heuristic=Manhattan()),
        Recursive_DFS(heuristic=Manhattan())
    )
    print("\nRunning IDA* with heuristics (Fringe, Manhattan, Walking Distance) :")
    print(hard)
    run_solvers(
        hard,
        IDAstar(heuristic=FringeHeuristic()),
        IDAstar(heuristic=Manhattan()),
        IDAstar(heuristic=WalkingDistanceHeuristic(3)),
    )
    print ("*"*30)
    print("\nRunning IDA* for easy 4x4 with Manhattan and Walking Distance heuristics :")
    print(easy44)
    print(time_solvers(
        (easy44,),
        IDAstar(heuristic=Manhattan()),
        IDAstar(heuristic=WalkingDistanceHeuristic(4)),
    ))
