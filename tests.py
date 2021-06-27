from Puzzle import Puzzle
from Node import Node
from heuristics import *
from Solver import *

easy = Puzzle((3,3), [[4, 3, 2], [1, 7, 5], [6, 8, 0]]) # Has two optimal solutions in 8 moves
hard = Puzzle((3,3), [[4, 7, 6], [5, 1, 8], [0, 3, 2]]) # Has nine optimal solutions in 28 moves
hard44 =  Puzzle((4,4), [[2, 4, 7, 8], [10, 13, 6, 3], [5, 0, 1, 14], [12, 11, 9, 15]]) # Has five optimal solutions in 45 moves
easy44 = Puzzle((4,4), [[14, 1, 9, 6], [4, 8, 12, 5], [7, 2, 3, 0], [10, 11, 13, 15]]) # Has one optimal solution in 45 moves

def print_solutions(sols):

    for sol in sols:
        print([node.puzzle.bt_index for node in sol.path], f"({sol.depth})")


def run_solvers(puzzle, *solvers):

    for solver in solvers:
        print ("*"*30)
        sols = solver(Node(puzzle))
        print_solutions(sols)

if __name__ == "__main__":
    print("Running solvers for easy 3x3 position :")
    print(easy)
    run_solvers(
        easy,
        breadth_first_search,
        Astar_search,
        depth_first_search,
    )
    print("\nRunning solvers for hard 3x3 position :")
    print(hard)
    run_solvers(
        hard,
        Astar_search,
        depth_first_search,
    )
    print("\nRunning IDA* for easy 4x4 position :")
    print(easy44)
    run_solvers(
        easy44,
        iterative_deepening_search,
    )
