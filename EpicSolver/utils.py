import math
from .taquin import Taquin

factorial = math.factorial
binomial = lambda n,k: math.comb(n,k) if n>=k else 0

def perm_coord(perm):
    # Computes the coordinate of a permutation
    # Works if the sorted position has increasing values
    icount = []
    for i, k in enumerate(perm):
        count = 0
        for l in perm[:i]:
            if l>k: count+=1
        icount.append(count)
    return sum(k*factorial(i) for i, k in enumerate(icount))

class Pattern:
    def __init__(self, size, pattern_tiles):
        assert 0 not in pattern_tiles
        assert len(set(pattern_tiles)) == len(pattern_tiles)
        self.tiles = tuple(sorted(pattern_tiles))
        self.ids = {k:i for i, k in enumerate(self.tiles)}
        non_pattern_tiles = tuple(i for i in range(size**2) if i not in self.tiles)
        self.order = (k for k in self.tiles + non_pattern_tiles)

    # def coord(self, puzzle):
    #     # Computes the coordinate of the input puzzle
    #     # First part is the arrangement counter :
    #     # For each tile i that belongs to the pattern, count the number x of
    #     # pattern tiles that come before it. Then this tile
    #     # contributes c_nk(i, x+1) to the position coordinate.
    #     # The sum of the contributions is the arrangement coordinate
    #     # This works if the solved state has all pattern tiles stored at the beginning
    #     # In our case they are at the end, so we have to reverse the permutation
    #     # I can't make the from_coord function work otherwise XD
    #     # Second part is the coordinate of the permutation of the pattern tiles
    #     # Coordinate for the whole pattern is computed as : arr_count*size! + perm_coord
    #     flattened = [puzzle.tiles[i][j] for i in range(self.size) for j in range(self.size)]
    #     flattened = [flattened[i] for i in self.order]
    #     N = len(flattened)
    #     n = len(self.tiles)
    #     sub_perm = []
    #     arr_count = on_the_right = 0
    #     for i, k in enumerate(reversed(flattened)):
    #         if k in self.tiles:
    #             b = binomial(i, on_the_right+1)
    #             arr_count += b
    #             on_the_right += 1
    #             sub_perm.append(k)
    #     return arr_count*factorial(n) + perm_coord(sub_perm)

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
