import numpy as np, pickle
from .utils import factorial, binomial, perm_coord, HardQueue
from .taquin import Taquin
from .node import Node

def build_fringe_table(size=3):

    """
        breadth-first generator for the fringe heuristic
        Stores the distance to solving the "fringe", aka the right and bottom tiles
        (and the blank space). Solved position for the 8-Puzzle (3x3):
        0  x  2
        x  x  5
        6  7  8
        WARNING: takes over 12 hours to generate table for the 15-Puzzle (4x4)
        Probaby not a good idea to try it for the 5x5 puzzle
    """

    fringe_tiles = (0,) + tuple((i+1)*size-1 for i in range(size-1)) + tuple(size*(size-1)+i for i in range(size))
    non_fringe_tiles = tuple(k for k in range(size**2) if k not in fringe_tiles)
    fringe_ordering = tuple((k//size, k%size) for k in non_fringe_tiles + fringe_tiles)

    def fringe_coord(puzzle):
        # Computes the coordinate of the input puzzle
        # First part is the arrangement counter :
        # For each tile i that belongs to the fringe, count the number x of
        # fringe tiles that come before it. Then this tile
        # contributes c_nk(i, x+1) to the position coordinate
        # This works if the solved state has all fringe tiles stored at the beginning
        # In our case they are at the end, so we have to reverse the permutation
        # I can't make the from_coord function work otherwise XD
        flattened = [puzzle.tiles[i][j] for i, j in fringe_ordering]
        N = len(flattened)
        n = len(fringe_tiles)
        sub_perm = []
        arr_count = on_the_right = 0
        for i, k in enumerate(reversed(flattened)):
            if k in fringe_tiles:
                b = binomial(i, on_the_right+1)
                arr_count += b
                on_the_right += 1
                sub_perm.append(k)
        return arr_count*factorial(n) + perm_coord(sub_perm)

    def taquin_from_coord(coord):
        n = len(fringe_tiles)
        N = size**2
        # This loop retrieves the flattened indices
        # of the fringe tiles positions from the first part
        # of the coordinate: coord//factorial(n)
        arr_count = coord//factorial(n)
        fringe_ids = []
        on_the_right = n
        for i in range(N):
            b = binomial(N-i-1, on_the_right)
            if arr_count - b >= 0:
                fringe_ids.append(i)
                arr_count -= b
                on_the_right -= 1

        # This loop computes the permutation
        # of the fringe tiles
        perm_coord = coord%factorial(n)
        icount = []
        for i in range(n):
            count = perm_coord%(i+1)
            perm_coord = perm_coord//(i+1)
            icount.append(count)
        perm = []
        rged = list(range(n))
        for k in reversed(icount):
            perm.append(rged.pop(len(rged)-k-1))
        perm = [fringe_tiles[k] for k in perm]

        # Setting the flat version of the puzzle
        # Non fringe tiles are set to -1
        flat = [-1]*N
        for idx, tile in zip(fringe_ids, perm):
            flat[idx] = tile
        # Setting it back to a size*size board
        tiles = [[-1]*size for i in range(size)]
        for ids, tile in zip(fringe_ordering, flat):
            i, j = ids
            tiles[i][j] = tile
        return Taquin((size, size), tiles=tiles)

    puzzle = Taquin((size, size))
    queue = HardQueue([(0,fringe_coord(puzzle))])
    N = factorial(size**2)//factorial(size**2-len(fringe_tiles))
    table = bytearray(N)
    counter = 0

    while queue.is_not_empty():
        d, c = queue.pop()
        node = Node(taquin_from_coord(c))
        node.depth = d
        for child in node.expand() : # and generate their children
            coord = fringe_coord(child.puzzle)
            if table[coord]==0:
                queue.store((child.depth, coord))
                table[coord] = child.depth
                counter += 1
                print(f"{counter} nodes, {counter*100/N:.4}%, depth {node.depth}")

    # When we do this we visit the solved position again at depth 2
    # Since its h value is set to 0 at this point, it gets reset to 2,
    # meaning that we need to reset it manually after the loop ends
    table[fringe_coord(puzzle)] = 0

    with open(f"{size}_fringe_table.pkl", "wb") as f:
        pickle.dump(table, f)
