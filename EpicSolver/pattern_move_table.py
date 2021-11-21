import numpy as np, time
from .utils import layout_coordinate, permutation_coordinate, valid_neighbours
from .pattern_table import Pattern, PatternTaquin, PatternMove


def build_pattern_move_table(size, pattern):
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
    lidx_dt = np.dtype([('layout', np.uint8, (16,)), ('tile', ltile_dt, (len(pattern),))])
    layout_move_table = np.zeros(pattern.nlayt, dtype=lidx_dt)

    """
        permutation_move_table[idx]['permutation']:
            the permutation array corresponding to index idx
        permutation_move_table[idx]['pindex'][num_tile, pshift]:
            the new permutation table index resulting from applying shift pshift to tile num_tile
    """
    max_shift = min(pattern.size-1, len(pattern))
    pidx_dt = np.dtype([('permutation', np.uint8, (len(pattern),)), ('pindex', np.uint8, (len(pattern), 2*max_shift+1))])
    permutation_move_table = np.zeros(pattern.nperm, dtype=pidx_dt)

    slide = {'L':-1, 'R':+1, 'U':-size, 'D':+size}
    neighbours = {i*size+j:tuple(valid_neighbours(size, i,j)) for i in range(size) for j in range(size)}
    invalid_lindex = pattern.nlayt
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
    print(f"Building layout move table for pattern {pattern}")
    for idx in range(pattern.nlayt):
        layout = pattern.layout_from_coord(idx)
        layout_move_table[idx]['layout'] = layout
        tiles = (i for i, k in enumerate(layout) if k==1)
        for tile in tiles:
            pos = sum(layout[:tile])
            for move in slide:
                lindex, pshift = get_new_lindex_and_shift(layout, tile, move)
                layout_move_table[idx]['tile'][pos][move]['lindex'] = lindex
                layout_move_table[idx]['tile'][pos][move]['pshift'] = pshift

    invalid_pindex = pattern.nperm
    def get_new_pindex(permutation, tile, shift):
        if shift == 0 or tile+shift > len(permutation) or tile+shift < 0:
            return invalid_pindex
        else:
            p = permutation[:]
            p.insert(tile+shift, p.pop(tile))
            return permutation_coordinate(p)

    # Building the permutation table (about 10 s for an 8-tile pattern)
    print(f"Building permutation move table for pattern {pattern}")
    for idx in range(pattern.nperm):
        permutation = pattern.permutation_from_coord(idx)
        for tile in range(len(permutation)):
            for shift in range(-max_shift, max_shift+1):
                pindex = get_new_pindex(permutation, tile, shift)
                permutation_move_table[idx]['permutation'] = permutation
                permutation_move_table[idx]['pindex'][tile, shift] = pindex

    return layout_move_table, permutation_move_table
