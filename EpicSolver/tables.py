import numpy as np, pickle, itertools as it, copy, collections
from .utils import factorial, binomial, perm_coord
from .taquin import Taquin, WDTaquin
from .solver import IDAstar
from .cube2 import Cube2
from .node import Node

def build_walking_distance_table(size):
    """
        a breadth-first generator for the walking distance table
    """

    # Starting from the solved position we generate new positions using breadth-first
    # Positions are stored in a dict with keys the coordinate of the tuple containing
    # the flattened puzzle board followed by the blank tile position
    # and values the depth at which the position was found
    # example for the solved state :
    # {(3,0,0,0,0,4,0,0,0,0,4,0,0,0,0,4,0):0}
    # A move table is also built, which is a dict mapping every state  to its possible children
    # Horizontal value for a given taquin puzzle can be found in the vertical table
    # by reading the puzzle in columns and counting :
    # (4,8,12)    as from 1st
    # (1,5,9,13)  as from 2nd
    # (2,6,10,14) as from 3rd
    # (3,7,11,15) as from 4th

    puzzle = WDTaquin(size)
    root = Node(puzzle)
    queue = collections.deque([root])
    generated = {} # dict linking state  to depth
    move_table = {} # dict mapping state  to move dict. Move dict maps move to child
    while queue:
        node = queue.popleft()
        state = node.puzzle.coord()
        if state not in generated:
            move_dict = {}
            generated.update({state:node.depth}) # store newly encountered positions
            for child in node.expand() :
                move_dict.update({child.move.coord:child.puzzle.coord()})
                queue.append(child) # and generate their children
            move_table.update({state:move_dict}) # and store move dict
            print(len(generated), node.depth)

    with open(f"vertical_{size}_wd_table.pkl", "wb") as f:
        pickle.dump(generated, f)

    with open(f"vertical_{size}_wd_move_table.pkl", "wb") as f:
        pickle.dump(move_table, f)


def build_22CP_table():
    """
    suboptimal way of generating the corner permutation optimals
    for 2x2x2 cubes
    """
    class CPCube2(Cube2):
        @property
        def is_solved(self):
            return np.array_equal(self.CP, np.array([0, 1, 2, 3, 4, 5, 6, 7]))
        def copy(self):
            return CPCube2((self.CP, self.CO))

    solver = IDAstar(find_all=False, heuristic=lambda puzzle:0, verbose=False)
    s = {}

    for perm in it.permutations([0,1,2,4,5,6,7]):
        actual_cp = perm[0:3] + (3,) + perm[3:]
        puzzle = CPCube2((np.array(actual_cp), np.array([0,0,0,0,0,0,0,0])))
        sol = solver.solve(puzzle)[-1]
        s.update({actual_cp.__hash__():sol.depth})
        print(len(s), '/ 5040', sol.depth)

    with open("22CP_table.pkl", "wb") as f:
        pickle.dump(s, f)


def build_22CO_table():
    """
    suboptimal way of generating the corner orientation optimals
    for 2x2x2 cubes
    """
    class COCube2(Cube2):
        @property
        def is_solved(self):
            return np.array_equal(self.CO, np.array([0, 0, 0, 0, 0, 0, 0, 0]))
        def copy(self):
            return COCube2((self.CP, self.CO))

    solver = IDAstar(find_all=False, heuristic=lambda puzzle:0, verbose=False)
    s = {}
    counter = 0

    for i0 in range(3):
        for i1 in range(3):
            for i2 in range(3):
                for i3 in range(3):
                    for i4 in range(3):
                        for i5 in range(3):
                            co_tuple = (i0,i1,i2,0,i3,i4,i5) + (-(i0+i1+i2+i3+i4+i5)%3,)
                            puzzle = COCube2((np.array([0,1,2,3,4,5,6,7]), np.array(co_tuple)))
                            sol = solver.solve(puzzle)[-1]
                            s.update({co_tuple.__hash__():sol.depth})
                            counter+=1
                            print(counter, "/ 729", sol.depth)

    with open("22CO_table.pkl", "wb") as f:
        pickle.dump(s, f)


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

    class HardQueue(collections.deque):
        filenames_queue = collections.deque([])
        queue_trail = collections.deque([])
        n_files = 0

        def is_not_empty(self):
            return self.__bool__() or self.queue_trail.__bool__() or self.filenames_queue.__bool__()

        def store(self, node):
            self.queue_trail.append(node)

            if len(self.queue_trail) > 1000000:
                filename = f"chunk_{self.n_files}.pkl"
                with open(filename, "wb") as f:
                    print("Dumping queue trail...")
                    pickle.dump(self.queue_trail, f)
                self.queue_trail.clear()
                self.n_files += 1
                self.filenames_queue.append(filename)

        def pop(self):
            if not self:
                if self.filenames_queue:
                    next_file = self.filenames_queue.popleft()
                    with open(next_file, "rb") as f:
                        print("Loading chunk...")
                        self.extend(pickle.load(f))
                    os.remove(next_file)
                elif self.queue_trail:
                    self.extend(self.queue_trail)
                    self.queue_trail.clear()
                else:
                    raise IndexError
            return self.popleft()

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
