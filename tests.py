from Puzzle import Puzzle
from Node import Node
from heuristics import *
from Solver import *

easy = Puzzle((3,3), [[4, 3, 2], [1, 7, 5], [6, 8, 0]]) # Has two optimal solutions
hard = Puzzle((3,3), [[4, 7, 6], [5, 1, 8], [0, 3, 2]])

def print_solutions(sols):

    for sol in sols:
        print([node.puzzle.bt_index for node in sol.path], f"({sol.depth})")


def run_solvers(puzzle, *solvers):

    for solver in solvers:
        print ("*"*30)
        sols = solver(Node(puzzle))
        print_solutions(sols)

if __name__ == "__main__":
    print("Running solvers for easy position :")
    print(easy)
    run_solvers(
        easy,
        breadth_first_search,
        Astar_search,
        depth_first_search,
    )
    print("\nRunning solvers for hard position :")
    print(hard)
    run_solvers(
        hard,
        Astar_search,
        depth_first_search,
    )
