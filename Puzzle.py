import random
import numpy as np

# 3x3 Solved puzzle scheme
# blank tile is labeled x
# and numbered 0
# -----------------
#  x |  1  |  2  |
# -----------------
#  3  |  4  |  5  |
# -----------------
#  6  |  7  |  8  |
# -----------------

class Puzzle:

    def __init__(self, shape=(3,3), tiles=None, bt_pos=None):

        self.shape = shape
        m, n = self.shape
        self.tiles = tiles or [[n*i+j for j in range(n)]for i in range(m)]
        self.bt_pos = bt_pos or self.compute_blank_tile_pos()

    def compute_blank_tile_pos(self):

        m, n = self.shape
        bt_pos = 0
        for i in range(m):
            for j in range(n):
                if not self.tiles[i][j]:
                    bt_pos = (i,j)
        return bt_pos

    def __repr__(self):
        return f"Puzzle(tiles={self.tiles})"

    def __str__(self):
        strs = []
        m, n = self.shape
        for i in range(m):
            for j in range(n):
                if self.tiles[i][j] == n*i+j:
                    strs.append(f"\033[32m{self.tiles[i][j] or 'x':>2}")
                else:
                    strs.append(f"\033[31m{self.tiles[i][j] or 'x':>2}")
        str = ""
        for i in range(m):
            str += " ".join(strs[i*n:(i+1)*n]) + "\n"
        return (str[:-1] + "\033[m")

    @property
    def possible_swaps(self):

        bt_pos = self.bt_pos
        all_adjacents = [(bt_pos[0]-move[0], bt_pos[1]-move[1]) for move in [(1,0),(0,1),(-1,0),(0,-1)]]
        possible_adjacents = [adj for adj in all_adjacents if (0<=adj[0]<self.shape[0] and 0<=adj[1]<self.shape[1])]

        return tuple(possible_adjacents)

    def swap(self, pos):

        i, j = self.bt_pos
        I, J = pos
        self.tiles[I][J], self.tiles[i][j] = self.tiles[i][j], self.tiles[I][J]
        self.bt_pos = pos

    def shuffle(self, N=100):

        N += random.randint(0,1)
        for move in range(N):
            poss = self.possible_swaps
            choice = random.randint(0, len(poss)-1)
            adj = poss[choice]
            self.swap(adj)

    def copy(self):
        return Puzzle(self.shape, [line[:] for line in self.tiles], self.bt_pos)

    @property
    def bt_index(self):
        i,j = self.bt_pos
        return self.shape[1]*i+j

    @property
    def is_solved(self):
        m, n = self.shape
        return self.tiles == [[n*i+j for j in range(n)]for i in range(m)]

    @property
    def is_solvable(self):

        m, n = self.shape
        tiles_as_list = []
        for line in self.tiles: tiles_as_list.extend(line)
        counter = 0
        seen = set()
        for tile in tiles_as_list:
            seen.add(tile)
            me = tiles_as_list[tile]
            while me not in seen:
                counter += 1
                seen.add(me)
                me = tiles_as_list[me]

        return counter%2 == sum(self.bt_pos)%2
