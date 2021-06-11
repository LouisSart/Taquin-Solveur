import random
import numpy as np
# Solved puzzle scheme
# blank tile is labeled x
# -----------------
#  x |  1  |  2  |
# -----------------
#  3  |  4  |  5  |
# -----------------
#  6  |  7  |  8  |
# -----------------

class Puzzle:

    def __init__(self, tiles=np.array([[0,1,2],[3,4,5],[6,7,8]]), bt_pos=None):

        self.tiles = tiles
        self.bt_pos = bt_pos or self.compute_blank_tile_pos()
        assert self.tiles[self.bt_pos] == 0

    def __repr__(self):
        return f"Puzzle({self.tiles[0]}\n       {self.tiles[1]}\n       {self.tiles[2]})"

    def __str__(self):
        return str(self.tiles)

    def compute_blank_tile_pos(self):

        for i in range(3):
            for j in range(3):
                if not self.tiles[i,j]:
                    return (i,j)

    def possible_swaps(self):

        bt_pos = self.bt_pos
        all_adjacents = [(bt_pos[0]-move[0], bt_pos[1]-move[1]) for move in [(1,0),(0,1),(-1,0),(0,-1)]]
        for adj in all_adjacents:
            if (0<=adj[0]<3 and 0<=adj[1]<3):
                yield adj

    def swap(self, pos):

        self.tiles[pos], self.tiles[self.bt_pos] = self.tiles[self.bt_pos], self.tiles[pos]
        self.bt_pos = pos

    def shuffle(self, N=100):

        # Note that this is a very bad way of shuffling the puzzle
        # Pseudo-randomness relies on N being large enough, I would say 100 is safe
        for move in range(N):
            assert self.tiles[self.bt_pos] == 0
            for adj in self.possible_swaps():
                choice = random.randint(0, 1)
                if choice : self.swap(adj)

    @property
    def is_solved(self):
        return np.array_equal(self.tiles, np.array([[0,1,2],[3,4,5],[6,7,8]]))
