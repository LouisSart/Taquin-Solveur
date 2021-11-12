import pickle, collections
from .node import Node


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
            ups = [WDMove(-1, i) for i in range(size)]
            downs = [WDMove(1, i) for i in range(size)]
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

def build_walking_distance_table(size):
    """
        a breadth-first generator for the walking distance table
    """

    # Starting from the solved position we generate new positions using breadth-first
    # Positions are stored in a dict with keys the coordinate of the tuple containing
    # the flattened puzzle board followed by the blank tile position
    # and values the depth at which the position was found
    # example for the solved state :
    # {(3,0,0,0,0,4,0,0,0,0,4,0,0,0,0,4,0):0}
    # A move table is also built, which is a dict mapping every state  to its possible children
    # Horizontal value for a given taquin puzzle can be found in the vertical table
    # by reading the puzzle in columns and counting :
    # (4,8,12)    as from 1st
    # (1,5,9,13)  as from 2nd
    # (2,6,10,14) as from 3rd
    # (3,7,11,15) as from 4th

    puzzle = WDTaquin(size)
    root = Node(puzzle)
    queue = collections.deque([root])
    generated = {} # dict linking state  to depth
    move_table = {} # dict mapping state  to move dict. Move dict maps move to child
    while queue:
        node = queue.popleft()
        state = node.puzzle.coord()
        if state not in generated:
            move_dict = {}
            generated.update({state:node.depth}) # store newly encountered positions
            for child in node.expand() :
                move_dict.update({child.move.coord:child.puzzle.coord()})
                queue.append(child) # and generate their children
            move_table.update({state:move_dict}) # and store move dict
            print(len(generated), node.depth)

    with open(f"vertical_{size}_wd_table.pkl", "wb") as f:
        pickle.dump(generated, f)

    with open(f"vertical_{size}_wd_move_table.pkl", "wb") as f:
        pickle.dump(move_table, f)
