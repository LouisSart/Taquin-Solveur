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

class ArrayPuzzle:

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

    def copy(self):
        return ArrayPuzzle(self.tiles.copy(), self.bt_pos)

class ListPuzzle:

    def __init__(self, tiles=[0,1,2,3,4,5,6,7,8], bt_pos=None):

        self.tiles = tiles
        self.bt_pos = bt_pos or self.compute_blank_tile_pos()
        assert self.tiles[self.bt_pos] == 0

    def __repr__(self):
        return f"Puzzle(tiles={self.tiles})"

    def __str__(self):
        strs = []
        for i, t in enumerate(self.tiles):
            if self.tiles[i] == i:
                strs.append(f"\033[32m{self.tiles[i] or 'x'}")
            else:
                strs.append(f"\033[31m{self.tiles[i] or 'x'}")
        return (f"\n{strs[0]} {strs[1]} {strs[2]}\n"
                f"{strs[3]} {strs[4]} {strs[5]}\n"
                f"{strs[6]} {strs[7]} {strs[8]}\033[m")

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

    def copy(self):
        return ListPuzzle([tile for tile in self.tiles], self.bt_pos)

    @property
    def is_solved(self):
        return self.tiles == [0,1,2,3,4,5,6,7,8]
