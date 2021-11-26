import numpy as np, pickle, collections
from .utils import *
from .taquin import Taquin
from .node import Node
from .pattern_move_table import factorial, binomial, permutation_coordinate, layout_coordinate, move_table as mt

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

def valid_shift(size, i,j):
    slides = ((0,1), (0,-1), (1,0), (-1,0))
    for v, h in slides:
        if h:
            x = j+h
            if (0 <= x < size): yield h
        else:
            y = i+v
            if (0 <= y < size): yield v*size

shifts = tuple({i*size+j:tuple(valid_shift(size, i,j)) for i in range(size) for j in range(size)} for size in range(5))
PatternMove = collections.namedtuple('PatternMove', ('tile', 'shift', 'bt', 'str'))
opposite = {'R':'L', 'L':'R', 'U':'D', 'D':'U'}
forbidden = lambda p: (p.bt-p.shift, opposite[p.str]) if p else (None, None)
named_moves = tuple({1:'R', -1:'L', size:'D', -size:'U'} for size in range(5))

class PatternTaquin:

    def __init__(self, size=4, lindex=0, pindex=0, bt_pos=0):
        self.size = size
        self.lindex, self.pindex, self.bt_pos = lindex, pindex, bt_pos


    def allowed_moves(self, previous=None):
        layout = mt.lmt[self.lindex]['layout']
        queue = collections.deque([self.bt_pos])
        moves = []
        seen = set()
        counter = 0

        while queue:
            k = queue.popleft()
            if k not in seen:
                for s in shifts[self.size][k]:
                    kk = k+s
                    if layout[kk]==1:
                        tile = sum(layout[:kk])
                        if not (k, named_moves[self.size][s]) == forbidden(previous):
                            moves.append(PatternMove(tile, s, k, named_moves[self.size][s]))
                    else:
                        queue.append(kk)
                counter+=1
            seen.add(k)

        self.checked_bt_states = [1 if k in seen else 0 for k in range(self.size**2)]
        return tuple(moves)

    def apply(self, move):
        permutation = mt.pmt[self.pindex]
        new_lindex = mt.lmt[self.lindex]['tile'][move.tile][move.str]['lindex']
        pshift = mt.lmt[self.lindex]['tile'][move.tile][move.str]['pshift']
        self.lindex = new_lindex
        self.pindex = mt.pmt[self.pindex]['pindex'][move.tile, pshift]
        self.bt_pos = move.bt + move.shift

    def copy(self):
        return PatternTaquin(self.size, self.lindex, self.pindex, self.bt_pos)

    def from_taquin(self, taquin, pattern):
        layout = [1 if k in pattern.tiles else 0 for line in taquin.tiles for k in line]
        permutation = [pattern.tiles.index(k) for line in taquin.tiles for k in line if k in pattern.tiles]
        i, j = taquin.bt_pos
        self.lindex = layout_coordinate(layout)
        self.pindex = permutation_coordinate(permutation)
        self.bt_pos = self.size*i+j

    def __str__(self):
        layout = mt.lmt[self.lindex]['layout']
        lstr = "\n".join(f"  {layout[i*self.size:(i+1)*self.size]}" for i in range(self.size))
        pstr = str(mt.pmt[self.pindex]['permutation'])
        return "\n".join((lstr, pstr))

def build_pattern_table(size, tiles, prefix=None):

    mt.load(size, len(tiles))

    taquin = Taquin((size, size))
    pattern = Pattern(size, tiles)
    puzzle = PatternTaquin(size)
    puzzle.from_taquin(taquin, pattern)
    queue = HardQueue([Node(puzzle)])
    table = np.zeros((pattern.nlayt, pattern.nperm), dtype=np.uint8)
    checked_bt_states = np.zeros((pattern.nlayt, pattern.nperm, 2), dtype=np.uint8)
    useless_counter, counter, d = 0, 0, 0
    print(f"Generating table {pattern}")
    print(" d,     %, nodes")
    print("-"*15)

    while queue.is_not_empty():
        node = queue.pop() # Pop next node
        lindex, pindex = node.puzzle.lindex, node.puzzle.pindex
        this_bts = checked_bt_states[lindex, pindex]
        if table[lindex, pindex] == 0: # first time we see this pattern position
            table[lindex, pindex] = node.depth # we store the depth
            counter += 1
            for child in node.expand():
                queue.store(child) # store the children
            adj = node.puzzle.checked_bt_states
            chk_bts = np.unpackbits(this_bts)
            checked_bt_states[lindex, pindex] = np.packbits([1 if a or b else 0 for a, b in zip(adj, chk_bts)]) # combine the bt_pos arrays
            if node.depth>d:
                print(f"{node.depth:2}", f"{(counter-1)/pattern.table_size*100:5.2f}%", counter-1)
                d = node.depth
        elif np.unpackbits(this_bts)[node.puzzle.bt_pos] == 0: # if the pattern position has been seen but not with this bt_pos
            for child in node.expand():
                queue.store(child) # store the children
            adj = node.puzzle.checked_bt_states
            chk_bts = np.unpackbits(this_bts)
            checked_bt_states[lindex, pindex] = np.packbits([1 if a or b else 0 for a, b in zip(adj, chk_bts)]) # combine the bt_pos arrays
    print(f"{(counter-1)/pattern.table_size*100:5.2f}%", counter-1)
    # When we do this we visit the solved position again at depth 2
    # Since its stored h value is 0 at this point, it gets set to 2,
    # so we need to reset it manually after the loop ends
    table[puzzle.lindex, puzzle.pindex] = 0

    print("Table generated")

    if prefix == None:
        prefix = f"tables/{size}_{len(pattern)}"
    with open(f"{prefix}_pattern_table.pkl", "wb") as f:
        pickle.dump(table, f)
