import random
import numpy as np
from heuristics import *
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
        return (f"{strs[0]} {strs[1]} {strs[2]}\n"
        f"{strs[3]} {strs[4]} {strs[5]}\n"
        f"{strs[6]} {strs[7]} {strs[8]}\033[m")

    def heuristic(self):
        return manhattan(self.tiles)

    def compute_blank_tile_pos(self):

        bt_pos = 0
        while self.tiles[bt_pos] != 0:
            bt_pos += 1
        return bt_pos

    @property
    def possible_swaps(self):

        bt_pos = self.bt_pos
        bt_ij_pos = (bt_pos//3, bt_pos%3)
        all_adjacents = [(bt_ij_pos[0]-move[0], bt_ij_pos[1]-move[1]) for move in [(1,0),(0,1),(-1,0),(0,-1)]]
        possible_adjacents = [adj for adj in all_adjacents if (0<=adj[0]<3 and 0<=adj[1]<3)]
        possible_swaps = [3*x[0]+x[1] for x in possible_adjacents]

        return tuple(possible_swaps)

    @property
    def is_solvable(self):

        counter = 0
        for i in range(9):
            tile = self.tiles[i]
            for t in self.tiles[i+1:]:
                if tile and t:
                    if tile > t: counter += 1
        return counter%2 == 0

    def swap(self, pos):

        self.tiles[pos], self.tiles[self.bt_pos] = self.tiles[self.bt_pos], self.tiles[pos]
        self.bt_pos = pos

    def shuffle(self, N=100):

        for move in range(N):
            assert self.tiles[self.bt_pos] == 0
            poss = self.possible_swaps
            choice = random.randint(0, len(poss)-1)
            adj = poss[choice]
            self.swap(adj)

    def copy(self):
        return Puzzle([tile for tile in self.tiles], self.bt_pos)

    @property
    def is_solved(self):
        return self.tiles == [0,1,2,3,4,5,6,7,8]

class ArrayPuzzle(Puzzle):

    def __init__(self, tiles=np.array([[0,1,2],[3,4,5],[6,7,8]]), bt_pos=None):

        self.tiles = np.reshape(tiles, (3,3))
        self.bt_pos = bt_pos or self.compute_blank_tile_pos()
        assert self.tiles[self.bt_pos] == 0

    def __repr__(self):
        return f"Puzzle({self.tiles[0]}\n       {self.tiles[1]}\n       {self.tiles[2]})"

    def __str__(self):
        is_in_place = lambda tile, pos: (3*pos[0]+pos[1]) == tile
        strs = []
        for i in range(3):
            for j in range(3):
                if is_in_place(self.tiles[i,j], (i,j)):
                    strs.append(f"\033[32m{self.tiles[i,j] or 'x'}")
                else:
                    strs.append(f"\033[31m{self.tiles[i,j] or 'x'}")
        return (f"{strs[0]} {strs[1]} {strs[2]}\n"
                f"{strs[3]} {strs[4]} {strs[5]}\n"
                f"{strs[6]} {strs[7]} {strs[8]}\033[m")

    def compute_blank_tile_pos(self):

        for i in range(3):
            for j in range(3):
                if not self.tiles[i,j]:
                    return (i,j)

    def heuristic(self):
        return manhattan(self.tiles.reshape(9))

    @property
    def possible_swaps(self):

        bt_pos = self.bt_pos
        all_adjacents = [(bt_pos[0]-move[0], bt_pos[1]-move[1]) for move in [(1,0),(0,1),(-1,0),(0,-1)]]
        return tuple(adj for adj in all_adjacents if (0<=adj[0]<3 and 0<=adj[1]<3))

    @property
    def is_solvable(self):

        self.tiles = np.reshape(self.tiles, (9,))
        is_solvable = super().is_solvable
        self.tiles = np.reshape(self.tiles, (3,3))
        return is_solvable

    @property
    def is_solved(self):
        return np.array_equal(self.tiles, np.array([[0,1,2],[3,4,5],[6,7,8]]))

    def copy(self):
        return ArrayPuzzle(self.tiles.copy(), self.bt_pos)
