from Puzzle import Puzzle
from Node import Node
from heuristics import *
from Solver import *

def run_solvers():

    easy = [4, 3, 2, 1, 7, 5, 6, 8, 0] # Has two optimal solutions
    puzzle = Puzzle(easy)
    sols, d = Astar_search(Node(puzzle), heuristic=manhattan)
    for sol in sols:
        print([node.puzzle.bt_pos for node in sol.path], d)
    print ("*"*30)
    sols, d = breadth_first_search(Node(puzzle))
    for sol in sols:
        print([node.puzzle.bt_pos for node in sol.path], d)

if __name__ == "__main__":
    run_solvers()
