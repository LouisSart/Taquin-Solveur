import pickle

def max_combo(*heuristics):
    def h(puzzle):
        return max((h(puzzle) for h in heuristics))
    return h

def manhattan(puzzle):

    cumdist = 0
    tiles = puzzle.tiles
    m, n = puzzle.shape
    for i in range(m):
        for j in range(n):
            tile = tiles[i][j]
            I, J = tile//n, tile%n
            if tile: cumdist += abs(i-I) + abs(j-J)
    return cumdist

class OuterLineHeuristic():

    def __init__(self):
        with open("tables/outer_line_table.pkl", "rb") as f:
            self.outer_line_dict = pickle.load(f)
        self.idx = {0:0,2:1,5:2,6:3,7:4,8:5}
        self.pos = [0,0,0,0,0,0]


    def __call__(self, puzzle):
        for i in range(3):
            for j in range(3):
                tile = puzzle.tiles[i][j]
                if tile in (0,2,5,6,7,8):
                    self.pos[self.idx[tile]] = (i,j)
        return self.outer_line_dict[tuple(self.pos).__hash__()]

class CO22Heuristic():

    def __init__(self):
        with open("tables/22CO_table.pkl", "rb") as f:
            self.CO_dict = pickle.load(f)

    def __call__(self, puzzle):
        return self.CO_dict[tuple(puzzle.CO).__hash__()]
