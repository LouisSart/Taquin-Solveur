import pickle

class MaxCombo:
    def __init__(self, *heuristics):
        self.heuristics = heuristics

    def compute(self, puzzle):
        return max(h.compute(puzzle) for h in self.heuristics)

    def update_iterator(self, node, move):
        for h in self.heuristics:
            h.update(node, move)
            yield node.h

    def update(self, node, move):
        node.h = max(self.update_iterator(node, move))

class NoneHeuristic:
    # The heuristic object that you would use when
    # running a search with no heuristic
    def compute(puzzle):
        return 0
    def update(node, move):
        node.h = 0

class Manhattan:
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
        return cumdist

    def update(self, node, move):
        # Updating value given the parent node
        # and the move to apply is cheaper
        parent = node.parent
        size = parent.puzzle.shape[0]
        i, j = parent.puzzle.bt_pos
        si, sj = move.slide
        if si:
            I = parent.puzzle.tiles[i+si][j+sj]//size
            curdist = abs(I-i-si)
            newdist = abs(I-i)
            step = newdist - curdist
        else:
            J = parent.puzzle.tiles[i+si][j+sj]%size
            curdist = abs(J-j-sj)
            newdist = abs(J-j)
            step = newdist - curdist
        node.h = parent.h + step

class InvertDistance:
    def __init__(self, size, inversions=None):
        self.h_inv, self.v_inv = inversions or (0, 0)
        self.size = size
        self.transposer = {(j*size+i):i*size+j for i in range(size) for j in range(size)}

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
        return InvertDistance(self.size, (self.h_inv, self.v_inv))


class FringeHeuristic():

    def __init__(self):
        with open("tables/3_fringe_table.pkl", "rb") as f:
            self.fringe_line_dict = pickle.load(f)
        self.idx = {0:0,2:1,5:2,6:3,7:4,8:5}
        self.pos = [0,0,0,0,0,0]

    def compute(self, puzzle):
        for i in range(3):
            for j in range(3):
                tile = puzzle.tiles[i][j]
                if tile in (0,2,5,6,7,8):
                    self.pos[self.idx[tile]] = (i,j)
        return self.fringe_line_dict[tuple(self.pos).__hash__()]

    def update(self, node, move):
        # Not implemented yet
        node.h = self.compute(node.puzzle)

class CO22Heuristic():

    def __init__(self):
        with open("tables/22CO_table.pkl", "rb") as f:
            self.CO_dict = pickle.load(f)

    def compute(self, puzzle):
        return self.CO_dict[tuple(puzzle.CO).__hash__()]

    def update(self, node, move):
        # Not implemented yet
        node.h = self.compute(node.puzzle)

class CP22Heuristic():

    def __init__(self):
        with open("tables/22CP_table.pkl", "rb") as f:
            self.CP_dict = pickle.load(f)

    def compute(self, puzzle):
        return self.CP_dict[tuple(puzzle.CP).__hash__()]

    def update(self, node, move):
        # Not implemented yet
        node.h = self.compute(node.puzzle)

class WalkingDistanceHeuristic:
    def __init__(self, size):
        self.size = size
        with open(f"tables/vertical_{size}_wd_table.pkl", "rb") as f:
            self.table = pickle.load(f)

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
        vertical_coord = tuple(board) + (bt_pos,)

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
        horizontal_coord = tuple(board) + (bt_pos,)
        return self.table[vertical_coord.__hash__()] + self.table[horizontal_coord.__hash__()]

    def update(self, node, move):
        # Not implemented yet
        node.h = self.compute(node.puzzle)
