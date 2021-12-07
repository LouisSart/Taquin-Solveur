import numpy as np, pickle, collections, time, os
from .utils import *
from .taquin import Taquin
from .node import Node
from .pattern_move_table import factorial, binomial, permutation_coordinate, layout_coordinate, move_tables as mt

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

    def __len__(self):
        return len(self.tiles)

    def __str__(self):
        return f"Pattern(({self.size},{self.size}), {self.tiles})"

PatternMove = collections.namedtuple('PatternMove', ('str', 'bt', 'tile'))

def valid_moves(size, i,j):
    slides = {(0,1):'R', (0,-1):'L', (1,0):'D', (-1,0):'U'}
    for v, h in slides.keys():
        x, y = i+v, j+h
        if (0 <= x < size) and (0 <= y < size):
            yield PatternMove(bt=i*size+j, tile=x*size+y, str=slides[(v,h)])

moves = {size:{i*size+j:tuple(valid_moves(size, i, j)) for i in range(size) for j in range(size)} for size in range(3,5)}

class PatternTaquin:
    lindex = 0
    pindex = 0
    size = None
    ntiles = None
    bt_pos = None

    def allowed_moves(self, previous=None):
        layout = mt[(self.size, self.ntiles)][0][self.lindex]['layout']
        return tuple(mv for k in range(self.size**2) for mv in moves[self.size][k] if self.reached[k]==1 and layout[mv.tile]==1)

    def reachable_bt_pos(self, previous=None):
        layout = mt[(self.size, self.ntiles)][0][self.lindex]['layout']
        queue = collections.deque([self.bt_pos])
        my_moves = []
        self.reached = [0]*self.size**2
        seen = set()

        while queue:
            k = queue.popleft()
            for m in moves[self.size][k]:
                kk = m.tile
                if layout[kk]==1:
                    self.reached[k] = 1
                    # my_moves.append((k, kk))
                else:
                    if kk not in seen:
                        queue.append(kk)
            seen.add(k)
        # self.moves = my_moves
        return self.reached

    def apply(self, move):
        lmt, pmt = mt[(self.size, self.ntiles)]
        tile_idx = sum(lmt[self.lindex]['layout'][:move.tile])
        pshift = lmt[self.lindex]['tile'][tile_idx][move.str]['pshift']
        self.lindex = lmt[self.lindex]['tile'][tile_idx][move.str]['lindex']
        self.pindex = pmt[self.pindex]['pindex'][tile_idx, pshift]
        self.bt_pos = move.tile

    def copy(self):
        cpy = PatternTaquin()
        cpy.lindex, cpy.pindex = self.lindex, self.pindex
        cpy.size, cpy.ntiles = self.size, self.ntiles
        cpy.bt_pos = self.bt_pos
        return cpy

    def from_taquin(self, taquin, pattern):
        self.size = pattern.size
        self.ntiles = len(pattern)
        i, j = taquin.bt_pos
        self.bt_pos = self.size*i+j
        layout = [1 if k in pattern.tiles else 0 for line in taquin.tiles for k in line]
        permutation = [pattern.tiles.index(k) for line in taquin.tiles for k in line if k in pattern.tiles]
        self.lindex = layout_coordinate(layout)
        self.pindex = permutation_coordinate(permutation)

    def __str__(self):
        layout = mt[(self.size, self.ntiles)][0][self.lindex]['layout']
        lstr = "\n".join(f"  {layout[i*self.size:(i+1)*self.size]}" for i in range(self.size))
        pstr = str(mt[(self.size, self.ntiles)][1][self.pindex]['permutation'])
        return "\n".join((lstr, pstr))

def combine(current, new):
    current = np.unpackbits(current)
    return np.packbits([1 if a or b else 0 for a, b in zip(current, new)])

def build_pattern_table(size, tiles, prefix=None):

    mt.empty()
    mt.load(size, len(tiles))

    taquin = Taquin((size, size))
    pattern = Pattern(size, tiles)
    puzzle = PatternTaquin()
    puzzle.from_taquin(taquin, pattern)
    queue = HardQueue((10**3, 10**6), np.dtype('u2, u2, u1, 2u1')) # 2-byte integers for lindex and pindex, one byte for the depth and 2 bytes for the (packed) layout array
    table = np.zeros((pattern.nlayt, pattern.nperm), dtype=np.uint8) # ex for 8-tile pattern: 40320*12870 = 500 Mo
    checked_bt_states = np.zeros((pattern.nlayt, pattern.nperm, 2), dtype=np.uint8) # ex for 8-tile pattern : 2*12870*40320 = 1,0 Go
    checked_bt_states[puzzle.lindex, puzzle.pindex] = np.packbits(puzzle.reachable_bt_pos())
    queue.store((puzzle.lindex, puzzle.pindex, 0, np.packbits(puzzle.reachable_bt_pos())))
    counter, d = 1, 0
    useless_counter = 0
    start = time.time()
    print(f"Generating table {pattern}")
    print(" d |%      |nodes    |time (s)")
    print("-"*28)

    while queue.is_not_empty():
        lindex, pindex, depth, bts = queue.pop() # Pop next node
        p = PatternTaquin()
        p.lindex, p.pindex, p.reached = lindex, pindex, np.unpackbits(bts)
        p.size, p.ntiles = size, len(pattern)
        node = Node(p)
        node.depth = depth
        if node.depth>d:
            print(f"{node.depth:2}", f"{counter/pattern.table_size*100:6.2f}% {counter:<9} {time.time()-start:<9.2f}")
            d = node.depth
        for child in node.expand():
            lindex, pindex = child.puzzle.lindex, child.puzzle.pindex
            if table[lindex, pindex] == 0 and not (lindex, pindex) == (puzzle.lindex, puzzle.pindex): # first time we see this pattern position
                table[lindex, pindex] = child.depth # we store the depth
                reached = np.packbits(child.puzzle.reachable_bt_pos())
                checked_bt_states[lindex, pindex] = reached # check reached bt pos
                queue.store((child.puzzle.lindex, child.puzzle.pindex, child.depth, reached)) # store the child
                counter += 1
            elif np.unpackbits(checked_bt_states[lindex, pindex])[child.puzzle.bt_pos] == 0: # if the pattern position has been seen but not with this bt_pos
                reached = child.puzzle.reachable_bt_pos()
                checked_bt_states[lindex, pindex] = combine(checked_bt_states[lindex, pindex], reached) # combine the bt_pos arrays
                queue.store((lindex, pindex, child.depth, np.packbits(reached))) # store the child

    print("-"*28)

    filename = f"tables/pattern/{size}x{size}/db/" + "_".join(str(k) for k in pattern.tiles)
    with open(filename + ".pkl", "wb") as f:
        pickle.dump(table, f)

    mt.empty()

    return table


class PatternDatabase(dict):

    def load(self, size, tiles):
        tiles_str = "_".join(str(t) for t in tiles)
        filename = f"tables/pattern/{size}x{size}/db/{tiles_str}.pkl"
        assert len(self) < 4, "Cannot load more than 3 move tables to prevent memory overflow"

        if os.path.isfile(filename):
            print(f"Size {size} pattern database found for tiles {tiles}")

            with open(filename, "rb") as f:
                self.update({(size, tiles):pickle.load(f)})
        else:
            table = build_pattern_table(size, tiles)
            self.update({(size, tiles):table})

    def empty(self):
        self = {}

pattern_database = PatternDatabase()
