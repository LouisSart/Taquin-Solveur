import numpy as np, pickle, collections
from .utils import HardQueue, valid_neighbours, perm_coord, factorial, binomial
from .taquin import Taquin
from .node import Node

class Pattern:
    def __init__(self, size, pattern_tiles):
        assert 0 not in pattern_tiles
        assert len(set(pattern_tiles)) == len(pattern_tiles)
        self.size = size
        self.tiles = tuple(sorted(pattern_tiles))
        self.ids = {k:i for i, k in enumerate(self.tiles)}
        non_pattern_tiles = tuple(i for i in range(size**2) if i not in self.tiles)
        self.order = tuple(k for k in self.tiles + non_pattern_tiles)

    def taquin_from_coord(self, coord, bt_pos):
        size = self.size
        n = len(self.tiles)
        N = size**2
        # This loop retrieves the flattened indices
        # of the pattern tiles positions from the first part
        # of the coordinate: coord//factorial(n)
        arr_count = coord//factorial(n)
        pattern_ids = []
        on_the_right = n
        for i in range(N):
            b = binomial(N-i-1, on_the_right)
            if arr_count - b >= 0:
                pattern_ids.append(i)
                arr_count -= b
                on_the_right -= 1

        # This loop computes the permutation
        # of the pattern tiles
        perm_coord = coord%factorial(n)
        icount = []
        for i in range(n):
            count = perm_coord%(i+1)
            perm_coord = perm_coord//(i+1)
            icount.append(count)
        perm = []
        rged = list(range(n))
        for k in reversed(icount):
            perm.append(rged.pop(len(rged)-k-1))
        perm = [self.tiles[k] for k in perm]

        # Setting the flat version of the puzzle
        # Non pattern tiles are set to -1
        flat = [-1]*N
        for idx, tile in zip(pattern_ids, perm):
            flat[idx] = tile
        # Setting it back to a size*size board
        tiles = [[-1]*size for i in range(size)]
        for ids, tile in zip(self.order, flat):
            i, j = ids
            tiles[i][j] = tile
        tiles[bt_pos[0]][bt_pos[1]] = 0
        return Taquin((size, size), tiles=tiles, bt_pos=bt_pos)


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
        self.bt_pos = taquin.bt_pos[0]*self.size + taquin.bt_pos[1]

    @property
    def coordinate(self):
        if self.c is not None:
            return self.c
        else:
            # Computes the coordinate of the input puzzle
            # First part is the arrangement counter :
            # For each tile i that belongs to the pattern, count the number x of
            # pattern tiles that come before it. Then this tile
            # contributes c_nk(i, x+1) to the position coordinate.
            # The sum of the contributions is the arrangement coordinate
            # This works if the solved state has all pattern tiles stored at the beginning
            # Second part is the coordinate of the permutation of the pattern tiles
            # Coordinate for the whole pattern is computed as : arr_count*size! + perm_coord
            arr_count = on_the_right = 0
            for i, k in enumerate(self.pattern.order):
                if self.layout[k]==1:
                    b = binomial(i, on_the_right+1)
                    arr_count += b
                    on_the_right += 1
            return arr_count*factorial(self.size) + perm_coord(self.permutation)

    def __str__(self):
        pattern_str = f"PatternTaquin(tiles={self.pattern.tiles})\n"
        it = iter(self.permutation)
        board = [next(it) if k else -1 for k in self.layout]
        board[self.bt_pos] = "o"
        board = [["x" if board[i*self.size+j]==-1 else str(board[i*self.size+j]) for j in range(self.size)] for i in range(self.size)]
        board_str = "\n".join(("  ".join(board[i])) for i in range(self.size))
        return pattern_str + board_str

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
                        if not (ptile, pswap) == (k, kk):
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
    # taquin.shuffle()
    print(taquin)
    pattern = Pattern(size, tiles)
    puzzle = PatternTaquin(pattern)
    puzzle.from_taquin(taquin)
    print("----------------")
    queue = HardQueue([Node(puzzle)])
    N = factorial(size**2)//factorial(size**2-len(pattern.tiles))
    table = bytearray(N)
    checked_bt_states = np.zeros((N, 2), dtype='uint8')
    counter = 0
    found=False

    while queue.is_not_empty():
        node = queue.pop() # Pop next node
        coord = node.puzzle.coordinate
        bt_pos = node.puzzle.bt_pos
        children = node.expand() # we do this in advance to compute adjacent_bt_pos before filling checked_bt_states
        adj = node.puzzle.adjacent_bt_pos
        chk_bts = np.unpackbits(checked_bt_states[coord])
        checked_bt_states[coord] = np.packbits([1 if a or b else 0 for a, b in zip(adj, chk_bts)]) # combine the bt_pos arrays
        if table[coord] == 0: # first time we see this pattern position
            table[coord] = node.depth # we store the depth
            counter += 1
            print(f"{counter/N*100:.2f}%", counter, node.depth)
            for child in children :
                queue.store(child) # store the children
        elif np.unpackbits(checked_bt_states[coord])[bt_pos] == 0: # if the pattern position has been seen but not with this bt_pos
            for child in children :
                queue.store(child) # store the children

    # When we do this we visit the solved position again at depth 2
    # Since its stored h value is 0 at this point, it gets set to 2,
    # so we need to reset it manually after the loop ends
    table[puzzle.coordinate] = 0

    for i, k in enumerate(table):
        if k==0: print(i)

    with open(f"{size}_pattern_table.pkl", "wb") as f:
        pickle.dump(table, f)
