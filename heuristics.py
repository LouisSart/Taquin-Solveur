
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

def outer_line_manhattan(puzzle):
    """
    manhattan distance for an m*n outerline subpuzzle
    Argument puzzle should be an OuterLinePuzzle instance
    """
    m, n = puzzle.shape
    counter = 0
    for i, pos in enumerate(puzzle.pos[1:m]):
        I, J = pos
        counter += sum((abs(I-i),abs(n-1-J)))
    for j, pos in enumerate(puzzle.pos[m:]):
        I, J = pos
        counter += sum((abs(m-1-I),abs(j-J)))
    return counter
