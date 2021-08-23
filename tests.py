import time
from EpicSolver.heuristics import *
from EpicSolver.solver import *
from EpicSolver.taquin import *

easy = Taquin((3,3), [[4, 3, 2], [1, 7, 5], [6, 8, 0]]) # Has two optimal solutions in 8 moves
hard = Taquin((3,3), [[4, 7, 6], [5, 1, 8], [0, 3, 2]]) # Has nine optimal solutions in 28 moves
hard44 = Taquin((4,4), [[2, 4, 7, 8], [10, 13, 6, 3], [5, 0, 1, 14], [12, 11, 9, 15]]) # Has five optimal solutions in 45 moves
easy44 = Taquin((4,4), [[14, 1, 9, 6], [4, 8, 12, 5], [7, 2, 3, 0], [10, 11, 13, 15]]) # Has one optimal solution in 45 moves

def time_puzzle_solve(puzzle, solver, heuristic):
    header = f"*  {solver.__class__.__name__} solver with {heuristic.__class__.__name__} heuristic  *"
    print("*"*len(header) + "\n" + header + "\n" + "*"*len(header))
    print(puzzle)
    tic = time.time()
    solver.solve(puzzle, heuristic)
    solver.print_solutions()
    tac = time.time()
    print("Total time:", tac - tic)
    print("Number of nodes:", solver.node_counter)
    print("Time per node:", (tac-tic)/solver.node_counter)



if __name__ == "__main__":
    time_puzzle_solve(easy, BFS(), NoneHeuristic())
    time_puzzle_solve(easy, Astar(), Manhattan())
    time_puzzle_solve(hard, Astar(), Manhattan())
    time_puzzle_solve(hard, DFS(), Manhattan())
    time_puzzle_solve(hard, Recursive_DFS(), Manhattan())
    # time_puzzle_solve(hard, IDAstar(), FringeHeuristic())
    time_puzzle_solve(hard, IDAstar(), Manhattan())
    time_puzzle_solve(hard, IDAstar(), WalkingDistance(3))
    time_puzzle_solve(easy44, IDAstar(), Manhattan())
    time_puzzle_solve(easy44, IDAstar(), InvertDistance(4))
    time_puzzle_solve(easy44, IDAstar(), WalkingDistance(4))
