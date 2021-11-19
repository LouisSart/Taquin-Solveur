import numpy as np, pickle, collections
from .utils import *
from .taquin import Taquin
from .node import Node

class Pattern:
    def __init__(self, size, pattern_tiles):
        assert len(set(pattern_tiles)) == len(pattern_tiles)
        self.size = size
        self.tiles = tuple(sorted(pattern_tiles))
        self.ids = {k:i for i, k in enumerate(self.tiles)}
        non_pattern_tiles = tuple(i for i in range(size**2) if i not in self.tiles)
        self.order = tuple(k for k in self.tiles + non_pattern_tiles)
        self.nperm = factorial(len(pattern_tiles))
        self.nlayt = binomial(size**2, len(pattern_tiles))
        self.table_size = self.nperm*self.nlayt
        assert self.table_size == factorial(size**2)//factorial(size**2-len(pattern_tiles))

    def layout_from_coord(self, coord):
        # Builds the layout state that corresponds to coord
        N = self.size**2
        layout = [0]*N
        c = coord
        x = len(self)
        for i in range(N):
            b = binomial(N-1-i, x)
            if c-b >= 0:
                layout[self.order[N-1-i]] = 1
                x -= 1
                c -= b
        return layout

    def permutation_from_coord(self, coord):
        # Builds the permutation corresponding to param coord
        c = coord
        n = len(self)
        icount = [0]*n
        k = 2
        while c > 0:
            icount[k-1] = c%k
            c = c//k
            k += 1
        # We now compute the actual permutation from the icount array
        perm = [0]*n
        rged = list(range(len(self)))
        for i, k in enumerate(reversed(icount)):
            perm[n-i-1] = rged.pop(len(rged)-k-1)
        return perm

    def __len__(self):
        return len(self.tiles)

    def __str__(self):
        return f"Pattern(({self.size},{self.size}), {self.tiles})"


PatternMove = collections.namedtuple('PatternMove', ('tile', 'swap'))


class PatternTaquin:
    def __init__(self, pattern=None, pattern_taquin=None):
        self.c = None
        if pattern is not None:
            self.size = pattern.size
            self.pattern = pattern
            self.permutation = bytearray(i for i in range(len(pattern.tiles)))
            self.layout = bytearray([1 if k in pattern.tiles else 0 for k in range(self.size**2)])
            self.bt_pos = 0
            self.adjacent_bt_pos = [0]*self.size**2
            self.neighbours = {i*self.size+j:tuple(valid_neighbours(self.size, i,j)) for i in range(self.size) for j in range(self.size)}
            self.allowed_moves() # this sets up the adjacent_bt_pos attribute
        else:
            # This assumes pattern_taquin is not None
            self.size = pattern_taquin.size
            self.pattern = pattern_taquin.pattern
            self.permutation = pattern_taquin.permutation[:]
            self.layout = pattern_taquin.layout[:]
            self.adjacent_bt_pos = [0]*self.size**2
            self.bt_pos = pattern_taquin.bt_pos
            self.neighbours = pattern_taquin.neighbours


    def from_taquin(self, taquin):
        flattened = [k for l in taquin.tiles for k in l]
        sub_perm = []
        layout = [0]*self.size**2
        for i, k in enumerate(flattened):
            if k in self.pattern.tiles:
                layout[i] = 1
                sub_perm.append(self.pattern.ids[k])
        self.permutation = bytearray(sub_perm)
        self.layout = bytearray([1 if k in self.pattern.tiles else 0 for l in taquin.tiles for k in l])
        self.adjacent_bt_pos = [0]*self.size**2
        self.bt_pos = taquin.bt_pos[0]*self.size + taquin.bt_pos[1]
        self.c = None

    def from_coordinate(self, coord, bt_pos=None):
        self.c = coord
        nlayt = self.pattern.nlayt
        lc, pc = coord%nlayt, coord//nlayt
        self.layout = bytearray(self.pattern.layout_from_coord(lc))
        self.permutation = bytearray(self.pattern.permutation_from_coord(pc))
        self.adjacent_bt_pos = [0]*self.size**2
        self.bt_pos = bt_pos
        if bt_pos==None:
            self.bt_pos = 0
            k = self.layout[0]
            while k==1:
                self.bt_pos += 1
                k = self.layout[self.bt_pos]

    @property
    def coordinate(self):
        if self.c is not None:
            return self.c
        else:
            # Computes the coordinate of the input puzzle
            # First part is the layout coordinate
            # Second part is the coordinate of the permutation of the pattern tiles
            # Coordinate for the whole pattern is computed as : perm_coord*(nlayt) + lay_coord
            reordered_layout = (self.layout[self.pattern.order[i]] for i in range(self.size**2))
            lc = layout_coordinate(reordered_layout)
            pc = permutation_coordinate(self.permutation)
            nlayt = self.pattern.nlayt
            return pc*nlayt + lc


    def __str__(self):
        it = iter(self.permutation)
        board = [self.pattern.tiles[next(it)] if k else -1 for k in self.layout]
        board[self.bt_pos] = "o"
        board = [["x" if board[i*self.size+j]==-1 else str(board[i*self.size+j]) for j in range(self.size)] for i in range(self.size)]
        board_str = "\n".join(("  ".join(board[i])) for i in range(self.size))
        return board_str

    def allowed_moves(self, previous=None):

        moves = []
        k = self.bt_pos
        queue = collections.deque([self.bt_pos])
        seen = set([self.bt_pos])
        adj = self.adjacent_bt_pos
        ptile, pswap = (previous.tile, previous.swap) if previous else (None, None)

        while queue:
            k = queue.popleft()
            for kk in self.neighbours[k]:
                if kk not in seen:
                    if self.layout[kk]==1:
                        adj[k] = 1
                        # if not (ptile, pswap) == (k, kk):
                        moves.append(PatternMove(tile=kk, swap=k))
                    else:
                        queue.append(kk)
                        seen.add(kk)
        return tuple(moves)

    def apply(self, move):
        p = self.permutation
        tile, swap = move.tile, move.swap
        if swap<tile:
            pre_swap, pre_tile = 0, 0
            for k in self.layout[:swap]:
                if k == 1:
                    pre_swap += 1
                    pre_tile += 1
            for k in self.layout[swap:tile]:
                if k == 1:
                    pre_tile += 1
            p.insert(pre_swap, p.pop(pre_tile))
        else:
            pre_swap, pre_tile = 0,0
            for k in self.layout[:tile]:
                if k == 1:
                    pre_swap += 1
                    pre_tile += 1
            for k in self.layout[tile:swap]:
                if k == 1:
                    pre_swap += 1
            p.insert(pre_swap-1, p.pop(pre_tile))

        self.bt_pos = tile
        self.layout[tile], self.layout[swap] = 0, 1

    def copy(self):
        return PatternTaquin(pattern_taquin=self)


def build_pattern_table(size, tiles):


    taquin = Taquin((size, size))
    pattern = Pattern(size, tiles)
    puzzle = PatternTaquin(pattern)
    puzzle.from_taquin(taquin)
    queue = HardQueue([Node(puzzle)])
    N = pattern.table_size
    table = bytearray(N)
    checked_bt_states = np.zeros((N, 2), dtype='uint8')
    counter, d = 0, 0
    seen = set()
    print(f"Generating table {pattern}")
    print(" d,     %, nodes")
    print("-"*15)

    while queue.is_not_empty():
        node = queue.pop() # Pop next node
        coord = node.puzzle.coordinate
        seen.add(coord)
        children = node.expand() # we do this in advance to compute adjacent_bt_pos before filling checked_bt_states
        if table[coord] == 0: # first time we see this pattern position
            table[coord] = node.depth # we store the depth
            counter += 1
            for child in node.expand():
                queue.store(child) # store the children
            adj = node.puzzle.adjacent_bt_pos
            chk_bts = np.unpackbits(checked_bt_states[coord])
            checked_bt_states[coord] = np.packbits([1 if a or b else 0 for a, b in zip(adj, chk_bts)]) # combine the bt_pos arrays
            if node.depth>d:
                print(f"{node.depth:2}", f"{counter/N*100:5.2f}%", counter-1)
                d = node.depth
        elif np.unpackbits(checked_bt_states[coord])[node.puzzle.bt_pos] == 0: # if the pattern position has been seen but not with this bt_pos
            for child in node.expand():
                queue.store(child) # store the children
            adj = node.puzzle.adjacent_bt_pos
            chk_bts = np.unpackbits(checked_bt_states[coord])
            checked_bt_states[coord] = np.packbits([1 if a or b else 0 for a, b in zip(adj, chk_bts)]) # combine the bt_pos arrays

    # When we do this we visit the solved position again at depth 2
    # Since its stored h value is 0 at this point, it gets set to 2,
    # so we need to reset it manually after the loop ends
    table[puzzle.coordinate] = 0

    print("Table generated")

    with open(f"{size}_pattern_table.pkl", "wb") as f:
        pickle.dump(table, f)
