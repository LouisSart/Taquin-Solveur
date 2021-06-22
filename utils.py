from Solver import breadth_first_search, Astar_search
from Puzzle import Puzzle
from Node import Node
import time
from heuristics import manhattan

def compare_algorithms(N):
    puzzle = Puzzle()
    scrambles = []
    astar_times, bfs_times = [], []
    for i in range(N):
        puzzle.shuffle()
        astar, bfs, move_count = time_algorithms(puzzle)
        scrambles.append((puzzle.copy(), move_count))
        astar_times.append(astar)
        bfs_times.append(bfs)
        print(f"{i+1:>5}|{astar:>20.10}|{bfs:>20.10}|{bfs/astar:>20.10}")
    return astar_times, bfs_times, scrambles

def time_algorithms(puzzle):
    tic = time.time()
    astar = Astar_search(Node(puzzle), list_manhattan)
    tac = time.time()
    bfs = breadth_first_search(Node(puzzle), max_depth=25, verbose=False)
    toc = time.time()
    return tac-tic, toc-tac, bfs[1]

def time_puzzle_implementations(position):
    tic = time.time()
    puzzle = ArrayPuzzle(position)
    root = Node(puzzle)
    solution = [node.puzzle.bt_pos for node in Astar_search(root, array_manhattan)]
    tac = time.time()
    puzzle = Puzzle(position)
    root = Node(puzzle)
    solution = [node.puzzle.bt_pos for node in Astar_search(root, list_manhattan)]
    toc = time.time()
    array_time, list_time = tac-tic, toc-tac
    return array_time, list_time

    print(f"np.array([]) : {tac-tic}\n list() : {toc-tac}")
    print(f"ratio : {(tac-tic)/(toc-tac)}")

def compare_puzzle_implementations(N):

    array_cumtime, list_cumtime = 0, 0
    print(f"{'#':>5} {'np.array([])':>20} {'list()':>20} {'ratio':>20}")
    for i in range(N):
        puzzle = Puzzle()
        puzzle.shuffle()
        array_time, list_time = time_puzzle_implementations(puzzle.tiles)
        array_cumtime += array_time
        list_cumtime += list_time
        print(f"{i+1:>5}|{array_time:>20.10}|{list_time:>20.10}|{array_time/list_time:>20.10}")

    return array_cumtime, list_cumtime
