import numpy as np, pickle, itertools as it
from .taquin import Taquin
from .solver import IDAstar
from .cube2 import Cube2

def build_22CO_table():
    """
    suboptimal way of generating the corner orientation optimals
    for 2x2x2 cubes
    """
    class COCube2(Cube2):
        @property
        def is_solved(self):
            return np.array_equal(self.CO, np.array([0, 0, 0, 0, 0, 0, 0, 0]))
        def copy(self):
            return COCube2((self.CP, self.CO))

    solver = IDAstar(find_all=False, heuristic=lambda puzzle:0, verbose=False)
    s = {}
    counter = 0

    for i0 in range(3):
        for i1 in range(3):
            for i2 in range(3):
                for i3 in range(3):
                    for i4 in range(3):
                        for i5 in range(3):
                            co_tuple = (i0,i1,i2,0,i3,i4,i5) + (-(i0+i1+i2+i3+i4+i5)%3,)
                            puzzle = COCube2((np.array([0,1,2,3,4,5,6,7]), np.array(co_tuple)))
                            sol = solver.solve(puzzle)[-1]
                            s.update({co_tuple.__hash__():sol.depth})
                            counter+=1
                            print(counter, "/ 729", sol.depth)

    with open("22CO_table.pkl", "wb") as f:
        pickle.dump(s, f)


def build_outer_line_table():

    """
    suboptimal way of generating the outer line optimals
    for every of the 60480 positions for the 3x3 puzzle
    """

    class OuterLineTaquin(Taquin):
        @property
        def is_solved(self):
            t = self.tiles
            res = (t[0][2], t[1][2], t[2][0], t[2][1], t[2][2]) == (2,5,6,7,8)
            return res
        def copy(self):
            return OuterLineTaquin(self.shape, [line[:] for line in self.tiles], self.bt_pos)
        @property
        def is_solvable(self):
            return True

    def outer_line_manhattan(puzzle):
        """
        manhattan distance for a 3x3 taquin outer line
        """
        cumdist = 0
        tiles = puzzle.tiles
        for i in range(3):
            for j in range(3):
                tile = tiles[i][j]
                if tile in (2,5,6,7,8):
                    I, J = tile//3, tile%3
                    cumdist += abs(i-I) + abs(j-J)
        return cumdist

    def outer_tiles_pos(K):
        return K//3, K%3

    h_table = {}
    counter = 0
    solver = IDAstar(heuristic=outer_line_manhattan, find_all=False, verbose=False)

    for i0 in range(9):
        for i2 in range(9):
            if i2 != i0:
                for i5 in range(9):
                    if i5 not in (i0, i2):
                        for i6 in range(9):
                            if i6 not in (i0, i2, i5):
                                for i7 in range(9):
                                    if i7 not in (i0, i2, i5, i6):
                                        for i8 in range(9):
                                            if i8 not in (i0, i2, i5, i6, i7):

                                                t = [-1,-1,-1,-1,-1,-1,-1,-1,-1]
                                                t[i0], t[i2], t[i5], t[i6], t[i7], t[i8] = 0, 2, 5, 6, 7, 8
                                                tiles = [t[i*3:(i+1)*3] for i in range(3)]
                                                puzzle = OuterLineTaquin(shape=(3,3), tiles=tiles)
                                                pos = tuple(outer_tiles_pos(i) for i in (i0,i2,i5,i6,i7,i8))
                                                label = pos.__hash__()
                                                sols = solver.solve(puzzle)
                                                h_table.update({label:sols[-1].depth,})
                                                print(len(h_table), "/ 60480",{label:sols[-1].depth,})

    with open("outer_line_table.pkl", "wb") as f:
        pickle.dump(h_table, f)
