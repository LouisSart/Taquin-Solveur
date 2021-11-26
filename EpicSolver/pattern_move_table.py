import numpy as np, math, os, pickle
from .utils import valid_neighbours

factorial = math.factorial
binomial = lambda n,k: math.comb(n,k) if n>=k else 0

def permutation_coordinate(perm):
    # Computes the coordinate of a permutation
    # Works if the sorted position has increasing values
    icount = []
    for i, k in enumerate(perm):
        count = 0
        for l in perm[:i]:
            if l>k: count+=1
        icount.append(count)
    return sum(k*factorial(i) for i, k in enumerate(icount))

def layout_coordinate(layout):
    # Param layout : an iterable of zeros (non pattern tiles) and ones (pattern tiles)
    # Computes the coordinate of the input pattern layout
    # For each tile i that belongs to the pattern, count the number x of
    # pattern tiles that come before it. Then this tile
    # contributes c_nk(i, x+1) to the coordinate.
    # The sum of the contributions is the layout coordinate
    # This works if the solved state has all pattern tiles stored at the beginning (coord=0)
    c = 0
    x = 0
    for i, k in enumerate(layout):
        if k == 1:
            c += binomial(i, x+1)
            x += 1
    return c

def layout_from_coord(size, ntiles, coord):
    # Builds the layout state that corresponds to coord
    N = size**2
    layout = [0]*N
    c = coord
    x = ntiles
    for i in range(N):
        b = binomial(N-1-i, x)
        if c-b >= 0:
            layout[N-1-i] = 1
            x -= 1
            c -= b
    return layout

def permutation_from_coord(ntiles, coord):
    # Builds the permutation corresponding to param coord
    c = coord
    n = ntiles
    icount = [0]*n
    k = 2
    while c > 0:
        icount[k-1] = c%k
        c = c//k
        k += 1
    # We now compute the actual permutation from the icount array
    perm = [0]*n
    rged = list(range(ntiles))
    for i, k in enumerate(reversed(icount)):
        perm[n-i-1] = rged.pop(len(rged)-k-1)
    return perm


def build_pattern_move_table(size, ntiles):

    nlayt, nperm = binomial(size**2, ntiles), factorial(ntiles)
    """
        layout_move_table[idx]['layout']:
            the layout for coordinate idx
        layout_move_table[idx]['tile'][num_tile][move_str]['lindex']:
            the new layout table index resulting from applying move move_str to tile num_tile
        layout_move_table[idx]['tile'][num_tile][move_str]['pshift']:
            the shift (signed integer) to apply to tile num_tile within
            the permutation array when applying move named 'move_str' to tile num_tile
    """
    lmove_dt = np.dtype([('lindex', np.uint16), ('pshift', np.int8)])
    ltile_dt = np.dtype([('L', lmove_dt), ('R', lmove_dt), ('U', lmove_dt), ('D', lmove_dt)])
    lidx_dt = np.dtype([('layout', np.uint8, (16,)), ('tile', ltile_dt, (ntiles,))])
    layout_move_table = np.zeros(nlayt, dtype=lidx_dt)

    """
        permutation_move_table[idx]['permutation']:
            the permutation array corresponding to index idx
        permutation_move_table[idx]['pindex'][num_tile, pshift]:
            the new permutation table index resulting from applying shift pshift to tile num_tile
    """
    max_shift = min(size-1, ntiles)
    pidx_dt = np.dtype([('permutation', np.uint8, (ntiles,)), ('pindex', np.uint16, (ntiles, 2*max_shift+1))])
    permutation_move_table = np.zeros(nperm, dtype=pidx_dt)


    slide = {'L':1, 'R':-1, 'U':size, 'D':-size} # moves are seen from the blank spot perspective
    # A tile moving down means the blank spot moving up
    neighbours = {i*size+j:tuple(valid_neighbours(size, i,j)) for i in range(size) for j in range(size)}
    invalid_lindex = nlayt
    def get_new_lindex_and_shift(layout, tile, move):
        assert layout[tile] == 1
        s = slide[move]
        swap = tile + s
        if swap not in neighbours[tile]:
            return invalid_lindex, 0
        elif layout[swap] == 1:
            return invalid_lindex, 0
        else:
            a, b = tuple(sorted([tile, swap]))
            in_between = sum(layout[a+1:b])
            shift = in_between if s>0 else -in_between
            l = layout[:]
            l[tile], l[swap] = 0, 1
            lindex = layout_coordinate(l)
            return lindex, shift

    # Building the layout table (about 2.5 s for an 8-tile pattern)
    print(f"Building layout move table for {ntiles}-pattern")
    for idx in range(nlayt):
        layout = layout_from_coord(size, ntiles, idx)
        layout_move_table[idx]['layout'] = layout
        tiles = (i for i, k in enumerate(layout) if k==1)
        for tile in tiles:
            pos = sum(layout[:tile])
            for move in slide:
                lindex, pshift = get_new_lindex_and_shift(layout, tile, move)
                layout_move_table[idx]['tile'][pos][move]['lindex'] = lindex
                layout_move_table[idx]['tile'][pos][move]['pshift'] = pshift

    invalid_pindex = nperm
    def get_new_pindex(permutation, tile, shift):
        if shift == 0 : # no shift
            return None
        elif tile+shift > len(permutation) or tile+shift < 0: # invalid shift
            return invalid_pindex
        else:
            p = permutation[:]
            p.insert(tile+shift, p.pop(tile))
            return permutation_coordinate(p)

    # Building the permutation table (about 10 s for an 8-tile pattern)
    print(f"Building permutation move table for {ntiles}-pattern")
    for idx in range(nperm):
        permutation = permutation_from_coord(ntiles, idx)
        for tile in range(len(permutation)):
            for shift in range(-max_shift, max_shift+1):
                pindex = get_new_pindex(permutation, tile, shift)
                if pindex is None: # no shift applied
                    pindex = idx
                permutation_move_table[idx]['permutation'] = permutation
                permutation_move_table[idx]['pindex'][tile, shift] = pindex

    with open(f"tables/{size}_{ntiles}_layout_move_table.pkl", "wb") as f:
        pickle.dump(layout_move_table, f)

    with open(f"tables/{size}_{ntiles}_permutation_move_table.pkl", "wb") as f:
        pickle.dump(permutation_move_table, f)

    return layout_move_table, permutation_move_table

built_move_tables = [[False]*9]*5
for size in range(5):
    for ntiles in range(8):
        built_move_tables[size][ntiles] = os.path.isfile(f"tables/{size}_{ntiles}_layout_move_table.pkl")

class MoveTable:
    lmt, pmt = None, None

    def load(self, size, ntiles):
        lfilename = f"tables/{size}_{ntiles}_layout_move_table.pkl"
        pfilename = f"tables/{size}_{ntiles}_permutation_move_table.pkl"
        if built_move_tables[size][ntiles]:
            print(f"Size {size} {ntiles}-pattern move tables found")

            with open(lfilename, "rb") as f:
                self.lmt = pickle.load(f)
            with open(pfilename, "rb") as f:
                self.pmt = pickle.load(f)
        else:
            self.lmt, self.pmt = build_pattern_move_table(size, ntiles)

move_table = MoveTable()
