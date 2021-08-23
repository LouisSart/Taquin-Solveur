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

taquin_moves = (left, right, up, down)

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

    def allowed_moves(self, previous):

        bt_pos = self.bt_pos
        forbidden = previous.forbidden_next if previous is not None else ()
        possible_moves = [move for move in taquin_moves if (
                0<=bt_pos[0]+move[0]<self.shape[0] and
                0<=bt_pos[1]+move[1]<self.shape[1] and
                move not in forbidden)]
        return tuple(possible_moves)

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

class WDTaquin:

    """
        Pseudo taquin puzzle class for generating row-wise
        walking distance heuristic
        Solved position :

        self.board =
              from 0  from 1  from 2  from 3
        row 0 [[3       0       0       0]
        row 1  [0       4       0       0]
        row 2  [0       0       4       0]
        row 3  [0       0       0       4]]

        self.bt_pos = 0
    """

    def __init__(self, size, board=None, bt_pos=None, metric=None):
        self.size = size
        if board is None:
            self.board = board or [[0]*i + [size] + [0]*(size-i-1) for i in range(size)]
            self.board[0][0] -= 1
        else:
            self.board = board

        if metric is None:
            ups = [WDMove("v", -1, i) for i in range(size)]
            downs = [WDMove("v", 1, i) for i in range(size)]
            # a swap with the same column in the opposite direction
            # comes back to the previous position so we forbid
            # this by linking opposite moves
            for up, down in zip(ups, downs):
                up.forbidden_next = down
                down.forbidden_next = up
            self.metric = tuple(ups + downs)
        else:
            self.metric = metric
        self.bt_pos = bt_pos or 0


    def allowed_moves(self, previous=None):
        forbidden = previous.forbidden_next if previous else None
        return tuple(move for move in self.metric \
                if self.size>(self.bt_pos + move.step)>=0 and \
                (self.board[self.bt_pos+move.step][move.col]))

    def apply(self, move):
        self.board[self.bt_pos+move.step][move.col] -=1
        self.board[self.bt_pos][move.col] += 1
        self.bt_pos += move.step

    def copy(self):
        return WDTaquin(self.size, [[k for k in line] for line in self.board], self.bt_pos, self.metric)

    def coord(self):
        return tuple(k for line in self.board for k in line) + (self.bt_pos,)

class WDMove:
    """
        The move class for the row-wise walking distance heuristic
        step = 1 for a down move, -1 for an up move
        col : the column to swap the blank tile with
        forbidden_next : a reference to the opposite WDMove object
    """
    def __init__(self, step, col):
        self.step = step
        self.col = col
        self.forbidden_next = None

    def __str__(self):
        return f"{self.step, self.col}"

    @property
    def coord(self):
        return (self.step, self.col)
