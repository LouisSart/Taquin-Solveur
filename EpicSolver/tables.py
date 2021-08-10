import numpy as np, pickle, itertools as it, copy, collections
from .taquin import Taquin
from .solver import IDAstar
from .cube2 import Cube2
from .node import Node
from .heuristics import NoneHeuristic

def build_walking_distance_table(size):
    """
        a breadth-first generator for the walking distance table
    """

    class VerticalWalkingTaquin:

        """
            Pseudo taquin puzzle class for generating vertical walking distance heuristic
            Solved position :

            self.board =
                  from 0  from 1  from 2  from 3
            row 0 [[3       0       0       0]
            row 1  [0       4       0       0]
            row 2  [0       0       4       0]
            row 3  [0       0       0       4]]

            self.bt_pos = 0
        """

        def __init__(self, size, board=None):
            self.size = size
            self.board = board or [[0]*i + [size] + [0]*(size-i-1) for i in range(size)]
            self.board[0][0] -= 1
            self.bt_pos = 0


        def allowed_moves(self, previous=None):
            forbidden = previous.forbidden_next if previous else None
            return tuple(move for move in all_moves if move != forbidden and self.size>(self.bt_pos + move.step)>=0 and (self.board[self.bt_pos+move.step][move.col]))

        def apply(self, move):
            self.board[self.bt_pos+move.step][move.col] -=1
            self.board[self.bt_pos][move.col] += 1
            self.bt_pos += move.step

        def copy(self):
            return copy.deepcopy(self)

        def coord(self):
            return tuple(k for line in self.board for k in line) + (self.bt_pos,)

    class VerticalMove:
        """
            step = 1 for a down move, -1 for an up move
            col : the column to swap the blank tile with
            forbidden_next : a reference to the opposite VerticalMove object
        """
        def __init__(self, step, col):
            self.step = step
            self.col = col
            self.forbidden_next = None
        def __str__(self):
            return f"{self.step, self.col}"

    ups = [VerticalMove(-1, i) for i in range(size)]
    downs = [VerticalMove(1, i) for i in range(size)]
    # a swap with the same column in the opposite direction
    # comes back to the previous position so we forbid
    # this by linking opposite moves
    for up, down in zip(ups, downs):
        up.forbidden_next = down
        down.forbidden_next = up

    all_moves = tuple(ups + downs)

    # Starting from the solved position we generate new positions using breadth-first
    # Positions are stored in a dict with keys the hash of the tuple containing
    # the flattened puzzle board followed by the blank tile position
    # and values the depth at which the position was found
    # example for the solved state :
    # {(3,0,0,0,0,4,0,0,0,0,4,0,0,0,0,4,0).__hash__():0}
    # Horizontal value for a given taquin puzzle can be found in the vertical table
    # by reading the puzzle in columns and counting :
    # (4,8,12)    as from 1st
    # (1,5,9,13)  as from 2nd
    # (2,6,10,14) as from 3rd
    # (3,7,11,15) as from 4th
    puzzle = VerticalWalkingTaquin(size)
    root = Node(puzzle)
    queue = collections.deque([root])
    generated = {} # dict linking state hash to depth
    while queue:
        node = queue.popleft()
        state = node.puzzle.coord()
        if state.__hash__() not in generated:
            generated.update({state.__hash__():node.depth}) # store newly encountered positions
            print(len(generated), node.depth)
            for child in node.expand(NoneHeuristic) : queue.append(child) # and generate their children

    with open(f"vertical_{size}_wd_table.pkl", "wb") as f:
        pickle.dump(generated, f)


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
        (and the blank space). Solved position for the 15-Puzzle:
        0  x  2
        x  x  5
        6  7  8
        WARNING: size is set as a parameter but it is highly recommended
        to not use it for puzzles over size 3 because memory cost is huge
        (over 8GB of RAM for 4x4 which means program will crash)
    """
    fringe_tiles = (0,) + tuple((i+1)*size-1 for i in range(size-1)) + tuple(size*(size-1)+i for i in range(size))
    idx = {a:i for i, a in enumerate(fringe_tiles)}
    pos = [0]*2*size

    def coordinate(puzzle):
        for i in range(size):
            for j in range(size):
                tile = puzzle.tiles[i][j]
                if tile in fringe_tiles:
                    pos[idx[tile]] = (i,j)
        return tuple(pos).__hash__()

    puzzle = Taquin((size, size))
    root = Node(puzzle)
    queue = collections.deque([root])
    generated = {} # dict linking state hash to depth
    while queue:
        node = queue.popleft()
        coord = coordinate(node.puzzle)
        if coord not in generated:
            generated.update({coord:node.depth}) # store newly encountered positions
            print(len(generated), node.depth)
            for child in node.expand(NoneHeuristic) : queue.append(child) # and generate their children

    with open(f"{size}_fringe_table.pkl", "wb") as f:
        pickle.dump(generated, f)
