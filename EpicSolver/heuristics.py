import pickle

class MaxCombo:
    def __init__(self, *heuristics):
        self.heuristics = heuristics

    def compute(self, puzzle):
        for h in self.heuristics : h.compute(puzzle)

    def update(self, node, move):
        for h in self.heuristics : h.update(node, move)

    @property
    def estimate(self):
        return max(h.estimate for h in self.heuristics)

    def copy(self):
        return MaxCombo(*(h.copy() for h in self.heuristics))

class NoneHeuristic:
    # The heuristic object that you would use when
    # running a search with no heuristic
    def __init__(self):
        self.estimate = 0

    def compute(self, puzzle):
        pass

    def update(self, node, move):
        pass

    def copy(self):
        return self

class Manhattan:
    def __init__(self, estimate=None):
        self.estimate = estimate or 0

    def compute(self, puzzle):
        # cumulated Manhattan ("taxicab") distance
        # between each tile and its solved position
        cumdist = 0
        tiles = puzzle.tiles
        m, n = puzzle.shape
        for i in range(m):
            for j in range(n):
                tile = tiles[i][j]
                I, J = tile//n, tile%n
                if tile: cumdist += abs(i-I) + abs(j-J)
        self.estimate = cumdist

    def update(self, node, move):
        # Updating value given the parent node
        # and the move to apply is cheaper
        size = node.puzzle.shape[0]
        i, j = node.puzzle.bt_pos
        si, sj = move.slide
        if si:
            I = node.puzzle.tiles[i+si][j+sj]//size
            curdist = abs(I-i-si)
            newdist = abs(I-i)
            step = newdist - curdist
        else:
            J = node.puzzle.tiles[i+si][j+sj]%size
            curdist = abs(J-j-sj)
            newdist = abs(J-j)
            step = newdist - curdist
        self.estimate += step

    def copy(self):
        return Manhattan(self.estimate)



class InvertDistance:
    def __init__(self, size, inversions=None, transposer=None):
        self.h_inv, self.v_inv = inversions or (0, 0)
        self.size = size
        self.transposer = transposer

    def inversion_counter(self, flattened):
        inversions = 0
        for i, tile in enumerate(flattened):
            if tile:
                for I in range(i+1, self.size**2):
                    further_tile = flattened[I]
                    if further_tile and further_tile < tile:
                        # Counting an inversion if the tile that comes after
                        # in the puzzle has a lower number than the current tile
                        inversions += 1
        return inversions

    def compute(self, puzzle):
        # Number of inversions on the puzzle board
        # A horizontal inversion is accounted for when two given tiles
        # are in the wrong order relative to each other
        # in reading direction (left to right, top to bottom)
        size = self.size
        flattened = [puzzle.tiles[i][j] for i in range(size) for j in range(size)]
        h_inversions = self.inversion_counter(flattened)

        # Same can be done for vertical inversions by transposing the board
        self.transposer = {(j*size+i):i*size+j for i in range(size) for j in range(size)}
        transposed_flattened = [self.transposer[puzzle.tiles[j][i]] for i in range(size) for j in range(size)]
        v_inversions = self.inversion_counter(transposed_flattened)

        self.h_inv, self.v_inv = h_inversions, v_inversions

    def update(self, parent, move):
        counter = 0
        size = parent.puzzle.shape[0]
        row, col = parent.puzzle.bt_pos
        tiles = parent.puzzle.tiles
        if move[0] == 1: # Down move
            swapped = tiles[row+1][col]
            for k in range(col+1, col+size):
                if tiles[row+k//size][k%size] < swapped:
                    self.h_inv += 1
                else:
                    self.h_inv -= 1
        elif move[0] == -1: # Up move
            swapped = tiles[row-1][col]
            for k in range(col+1, col+size):
                if tiles[row-1+k//size][k%size] > swapped:
                    self.h_inv += 1
                else:
                    self.h_inv -= 1
        elif move[1] == 1: # Right move
            swapped = tiles[row][col+1]
            for k in range(row+1, row+size):
                if self.transposer[tiles[k%size][col+k//size]] < self.transposer[swapped]:
                    self.v_inv += 1
                else:
                    self.v_inv -= 1
        elif move[1] == -1: # Left move
            swapped = tiles[row][col-1]
            for k in range(row+1, row+size):
                if self.transposer[tiles[k%size][col-1+k//size]] > self.transposer[swapped]:
                    self.v_inv += 1
                else:
                    self.v_inv -= 1


    @property
    def estimate(self):
        # Since vertical (e.g. horizontal) moves can affect the number of horizontal (e.g. vertical)
        # inversions by at most size-1, the number of moves required to solve the horizontal inversions
        # (e.g. vertical) is at least inversions/(size-1). If the result has a remainder, it can be added (no idea why but nice)
        # Vertical and horizontal contributions can be summed up to get the total value for the heuristic
        h_inversions, v_inversions = self.h_inv, self.v_inv
        v_moves_lower_bound = h_inversions//(self.size-1) + h_inversions%(self.size-1)
        h_moves_lower_bound = v_inversions//(self.size-1) + v_inversions%(self.size-1)

        return v_moves_lower_bound + h_moves_lower_bound

    def copy(self):
        return InvertDistance(self.size, (self.h_inv, self.v_inv), self.transposer)


class FringeHeuristic():

    def __init__(self):
        with open("tables/3_fringe_table.pkl", "rb") as f:
            self.fringe_line_dict = pickle.load(f)
        self.idx = {0:0,2:1,5:2,6:3,7:4,8:5}
        self.pos = [0,0,0,0,0,0]
        self.estimate = 0

    def compute(self, puzzle):
        for i in range(3):
            for j in range(3):
                tile = puzzle.tiles[i][j]
                if tile in (0,2,5,6,7,8):
                    self.pos[self.idx[tile]] = (i,j)
        return self.fringe_line_dict[tuple(self.pos).__hash__()]

    def update(self, node, move):
        # Not implemented yet
        raise NotImplementedError

    def copy(self):
        return self

class CO22Heuristic():

    def __init__(self):
        with open("tables/22CO_table.pkl", "rb") as f:
            self.CO_dict = pickle.load(f)

    def compute(self, puzzle):
        return self.CO_dict[tuple(puzzle.CO).__hash__()]

    def update(self, node, move):
        # Not implemented yet
        raise NotImplementedError

class CP22Heuristic():

    def __init__(self):
        with open("tables/22CP_table.pkl", "rb") as f:
            self.CP_dict = pickle.load(f)

    def compute(self, puzzle):
        return self.CP_dict[tuple(puzzle.CP).__hash__()]

    def update(self, node, move):
        # Not implemented yet
        raise NotImplementedError

class WalkingDistance:
    def __init__(self, size, estimate=None, coords=(None,None), estimate_table=None, move_table=None):
        self.size = size
        self.estimate = estimate or 0
        self.row_coord, self.col_coord = coords
        if estimate_table is None:
            with open(f"tables/vertical_{size}_wd_table.pkl", "rb") as f:
                self.estimate_table = pickle.load(f)
        else:
            self.estimate_table = estimate_table
        if move_table is None:
            with open(f"tables/vertical_{size}_wd_move_table.pkl", "rb") as f:
                self.move_table = pickle.load(f)
        else:
            self.move_table = move_table

    def compute(self, puzzle):
        board = []
        bt_pos = 0
        for i, line in enumerate(puzzle.tiles):
            froms = [0]*self.size
            for tile in line:
                if tile == 0:
                    bt_pos = i
                else:
                    row = tile//self.size
                    froms[row] += 1
            board += froms
        self.row_coord = tuple(board) + (bt_pos,)

        board = []
        for j in range(self.size):
            froms = [0]*self.size
            for i in range(self.size):
                tile = puzzle.tiles[i][j]
                if tile == 0:
                    bt_pos = j
                else:
                    col = tile%self.size
                    froms[col] += 1
            board += froms
        self.col_coord = tuple(board) + (bt_pos,)
        self.estimate = self.estimate_table[self.row_coord] +\
                        self.estimate_table[self.col_coord]

    def update(self, parent, move):
        si, sj = move
        i, j = parent.puzzle.bt_pos
        swapped = parent.puzzle.tiles[i+si][j+sj]
        if si: # Vertical move
            move_coord = si, swapped//self.size # tile swapped belongs to line swapped//size
            self.row_coord = self.move_table[self.row_coord][move_coord]
        elif sj: # Horizontal move
            move_coord = sj, swapped%self.size # tile swapped belongs to column swapped%size
            self.col_coord = self.move_table[self.col_coord][move_coord]
        self.estimate = self.estimate_table[self.row_coord] + self.estimate_table[self.col_coord]

    def copy(self):
        return WalkingDistance(self.size,
                                    self.estimate,
                                    (self.row_coord, self.col_coord),
                                    self.estimate_table,
                                    self.move_table)
