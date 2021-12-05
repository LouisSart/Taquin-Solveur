import numpy as np, pickle, collections
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
        ret = []
        for k, kk in self.moves:
            k_mvs = moves[self.size][k]
            for k_mv in k_mvs:
                if k_mv.tile == kk:
                    ret.append(k_mv)
        return ret

    def reachable_bt_pos(self, previous=None):
        layout = mt[(self.size, self.ntiles)][0][self.lindex]['layout']
        queue = collections.deque([self.bt_pos])
        my_moves = []
        reached = [0]*self.size**2
        seen = set()

        while queue:
            k = queue.popleft()
            for m in moves[self.size][k]:
                kk = m.tile
                if layout[kk]==1:
                    reached[k] = 1
                    my_moves.append((k, kk))
                else:
                    if kk not in seen:
                        queue.append(kk)
            seen.add(k)
        self.moves = my_moves
        return reached

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

def build_pattern_table(size, tiles, prefix=None):

    mt.empty()
    mt.load(size, len(tiles))

    taquin = Taquin((size, size))
    pattern = Pattern(size, tiles)
    puzzle = PatternTaquin()
    puzzle.from_taquin(taquin, pattern)
    queue = HardQueue([Node(puzzle)])
    table = np.zeros((pattern.nlayt, pattern.nperm), dtype=np.uint8) # ex for 8-tile pattern: 40320*12870 = 500 Mo
    checked_bt_states = np.zeros((pattern.nlayt, pattern.nperm, 2), dtype=np.uint8) # ex for 8-tile pattern : 2*12870*40320 = 1,0 Go
    checked_bt_states[puzzle.lindex, puzzle.pindex] = np.packbits(puzzle.reachable_bt_pos()) # combine the bt_pos arrays
    counter, d = 0, 0
    print(f"Generating table {pattern}")
    print(" d,     %, nodes")
    print("-"*15)

    while queue.is_not_empty():
        node = queue.pop() # Pop next node
        if node.depth>d:
            print(f"{node.depth:2}", f"{counter/pattern.table_size*100:5.2f}%", counter)
            d = node.depth
        for child in node.expand():
            lindex, pindex = child.puzzle.lindex, child.puzzle.pindex
            this_bts = checked_bt_states[lindex, pindex]
            if table[lindex, pindex] == 0: # first time we see this pattern position
                table[lindex, pindex] = node.depth # we store the depth
                adj = child.puzzle.reachable_bt_pos()
                queue.store(child) # store the child
                chk_bts = np.unpackbits(this_bts)
                checked_bt_states[lindex, pindex] = np.packbits([1 if a or b else 0 for a, b in zip(adj, chk_bts)]) # combine the bt_pos arrays
                counter += 1
            elif np.unpackbits(this_bts)[child.puzzle.bt_pos] == 0: # if the pattern position has been seen but not with this bt_pos
                adj = child.puzzle.reachable_bt_pos()
                queue.store(child) # store the children
                chk_bts = np.unpackbits(this_bts)
                checked_bt_states[lindex, pindex] = np.packbits([1 if a or b else 0 for a, b in zip(adj, chk_bts)]) # combine the bt_pos arrays
    print(f"{(counter-1)/pattern.table_size*100:5.2f}%", counter-1)
    # When we do this we visit the solved position again at depth 2
    # Since its stored h value is 0 at this point, it gets set to 2,
    # so we need to reset it manually after the loop ends
    table[puzzle.lindex, puzzle.pindex] = 0

    print("Table generated")

    filename = f"tables/pattern/{size}x{size}/db/" + "_".join(str(k) for k in pattern.tiles)
    with open(filename + ".pkl", "wb") as f:
        pickle.dump(table, f)

    mt.empty()
