from Puzzle import Puzzle
from Node import Node
from heuristics import *
from Solver import *

def run_solvers():

    easy = [[4, 3, 2], [1, 7, 5], [6, 8, 0]] # Has two optimal solutions
    puzzle = Puzzle((3,3), easy)
    sols = Astar_search(Node(puzzle), heuristic=manhattan)
    for sol in sols:
        print([node.puzzle.bt_pos for node in sol.path], sol.depth)
    print ("*"*30)
    sols = breadth_first_search(Node(puzzle))
    for sol in sols:
        print([node.puzzle.bt_pos for node in sol.path], sol.depth)
    print ("*"*30)
    sols = depth_first_search(Node(puzzle), max_depth=15)
    for sol in sols:
        print([node.puzzle.bt_pos for node in sol.path], sol.depth)

if __name__ == "__main__":
    run_solvers()
