
def array_manhattan(array_puzzle):

    cumdist = 0
    for i in range(3):
        for j in range(3):
            tile = array_puzzle.tiles[i,j]
            I, J = tile//3, tile%3
            cumdist += abs(i-I) + abs(j-J)
    return cumdist

def list_manhattan(list_puzzle):

    cumdist = 0
    for i in range(3):
        for j in range(3):
            tile = list_puzzle.tiles[3*i+j]
            I, J = tile//3, tile%3
            cumdist += abs(i-I) + abs(j-J)
    return cumdist
