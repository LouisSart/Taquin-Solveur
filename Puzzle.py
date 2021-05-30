import random
# Solved puzzle scheme
# blank tile is numbered 0
# -----------------
#  0  |  1  |  2  |
# -----------------
#  3  |  4  |  5  |
# -----------------
#  6  |  7  |  8  |
# -----------------

class Puzzle:

    def __init__(self, tiles=[0,1,2,3,4,5,6,7,8], bt_pos=None):

        self.tiles = tiles
        self.bt_pos = bt_pos or self.compute_blank_tile_pos()
        assert self.tiles[self.bt_pos] == 0

    def __repr__(self):
        return f"Puzzle(tiles={self.tiles})"

    def compute_blank_tile_pos(self):

        bt_pos = 0
        while self.tiles[bt_pos] != 0:
            bt_pos += 1
        return bt_pos

    def possible_swaps(self):

        bt_pos = self.bt_pos
        bt_ij_pos = (bt_pos//3, bt_pos%3)
        all_adjacents = [(bt_ij_pos[0]-move[0], bt_ij_pos[1]-move[1]) for move in [(1,0),(0,1),(-1,0),(0,-1)]]
        possible_adjacents = [adj for adj in all_adjacents if (0<=adj[0]<3 and 0<=adj[1]<3)]
        possible_swaps = [3*x[0]+x[1] for x in possible_adjacents]

        return tuple(possible_swaps)

    def swap(self, pos):

        self.tiles[pos], self.tiles[self.bt_pos] = self.tiles[self.bt_pos], self.tiles[pos]
        self.bt_pos = pos

    def shuffle(self, N=100):

        for move in range(N):
            assert self.tiles[self.bt_pos] == 0
            poss = self.possible_swaps()
            choice = random.randint(0, len(poss)-1)
            adj = poss[choice]
            self.swap(adj)

if __name__ == "__main__":
    puzzle = Puzzle()
    puzzle.shuffle()
    print(puzzle)
