
def manhattan(puzzle):

    cumdist = 0
    tiles = puzzle.tiles
    for i in range(3):
        for j in range(3):
            tile = tiles[3*i+j]
            I, J = tile//3, tile%3
            if tile: cumdist += abs(i-I) + abs(j-J)
    return cumdist
