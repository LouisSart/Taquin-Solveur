
def manhattan(puzzle):

    cumdist = 0
    tiles = puzzle.tiles
    m, n = puzzle.shape
    for i in range(m):
        for j in range(n):
            tile = tiles[i][j]
            I, J = tile//n, tile%n
            if tile: cumdist += abs(i-I) + abs(j-J)
    return cumdist
