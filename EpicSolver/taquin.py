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

class TaquinMove:
    def __init__(self, slide, repr, forbidden_next=None):
        self.slide = slide
        self.repr = repr
        self.forbidden_next = forbidden_next
    def __str__(self):
        return self.repr
    def __getitem__(self, key):
        return self.slide[key]

left  = TaquinMove((0,-1),"L")
right = TaquinMove((0,1),"R", (left,))
left.forbidden_next = (right,)
up    = TaquinMove((-1,0),"U")
down  = TaquinMove((1,0),"D", (up,))
up.forbidden_next = (down,)

taquin_moves = {(h,w):{(i,j):tuple(m for m in (left, right, up, down) if 0<=i+m[0]<h and 0<=j+m[1]<w)\
                for i in range(h) for j in range(w)}\
                for h in range(2,5) for w in range(2,5)}


class Taquin:

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
        return f"Taquin(tiles={self.tiles})"

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

    def allowed_moves(self, previous=None):
        forbidden = previous.forbidden_next if previous else None
        return tuple(m for m in taquin_moves[self.shape][self.bt_pos] if m is not forbidden)

    def apply(self, move):

        i, j = self.bt_pos
        si, sj = move.slide
        I, J = i+si, j+sj
        self.tiles[I][J], self.tiles[i][j] = self.tiles[i][j], self.tiles[I][J]
        self.bt_pos = (I, J)

    def shuffle(self, N=100):

        N += random.randint(0,1)
        move = None
        for i in range(N):
            choice = random.choice(self.allowed_moves(move))
            self.apply(choice)
            move = choice

    def copy(self):
        return Taquin(self.shape, [[tile for tile in line] for line in self.tiles], self.bt_pos)

    def random_state(self):
        m, n = self.shape
        scramble = [tile for tile in range(m*n)]
        random.shuffle(scramble)
        self.tiles = [[scramble[n*i+j] for j in range(n)] for i in range(m)]
        self.bt_pos = self.compute_blank_tile_pos()
        if not self.is_solvable:
            self.random_state()

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
