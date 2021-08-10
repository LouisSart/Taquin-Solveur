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
