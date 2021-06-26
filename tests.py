from Puzzle import Puzzle
from Node import Node
from heuristics import *
from Solver import *

easy = Puzzle((3,3), [[4, 3, 2], [1, 7, 5], [6, 8, 0]]) # Has two optimal solutions
hard = Puzzle((3,3), [[4, 7, 6], [5, 1, 8], [0, 3, 2]])

def run_solvers(puzzle, *solvers):

    def bt_index(pos):
        i,j = pos
        return 3*i+j
    for solver in solvers:
        print ("*"*30)
        sols = solver(Node(puzzle))
        for sol in sols:
            print([bt_index(node.puzzle.bt_pos) for node in sol.path], sol.depth)

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
