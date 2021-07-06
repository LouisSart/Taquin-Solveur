import numpy as np
import random
from .cube3 import CubeMove

class CubeState2:

    def __init__(self, state_arrays=(np.array([0, 1, 2, 3, 4, 5, 6, 7]),
                                    np.array([0, 0, 0, 0, 0, 0, 0, 0]))):
        (CP,CO)=state_arrays
        self.CP = CP
        self.CO = CO

    def tofile(self, f):
        assert not f.closed
        assert f.mode[0] == 'a'
        self.CP.tofile(f)
        self.CO.tofile(f)

    def fromfile(self, f):
        assert not f.closed
        assert f.mode[0] == 'r'
        self.CP = np.fromfile(f, dtype=int, count=8)
        self.CO = np.fromfile(f, dtype=int, count=8)

    @property
    def I(self):
        # Calcul de l'inverse. Retourne un objet CubeState2 tel que self*self.i()=solved
        CP  =  np.arange(8)
        CO  =  np.zeros(8)

        for i, p in enumerate(self.CP):
            CP[p] = i

        CO  =  np.remainder(-self.CO[CP], 3)

        return CubeState2((CP, CO))

    def isSolvable(self):

        if not np.remainder(np.sum(self.CO),3)==0: return False

        checked_corners=[]
        k=0
        n_corner_translations=0
        while len(checked_corners) < 8:
            if self.CP[k] in checked_corners :
                k+=1
            else:
                cycle_start=k
                i=self.CP[k]
                checked_corners += [k]
                while not i==cycle_start:
                    n_corner_translations+=1
                    checked_corners += [i]
                    i=self.CP[i]

        if not (-1)**n_corner_translations==1 : return False
        return True

    def mult(self, other):
        ''' Multiplication en place. Mêmes performances que l'autre... '''
        assert other.__class__ is CubeState2, "Vous essayez de multiplier nimp"

        self.CP   =  self.CP[other.CP]
        self.CO   =  np.remainder(self.CO[other.CP] + other.CO, 3)

    def copy(self):
        return CubeState2((self.CP, self.CO))

    def __mul__(self, other):
        assert other.__class__ is CubeState2, "Vous essayez de multiplier nimp"

        CP   =  self.CP[other.CP]
        CO   =  np.remainder(self.CO[other.CP] + other.CO, 3)

        return CubeState2((CP, CO))

    def __str__(self):
        return "CP = " + self.CP.__str__() + "\n" + \
               "CO = " + self.CO.__str__() + "\n"
# Définition des mouvements autorisés du Cube
# Définition de R, R', R2

R_turn  = CubeState2((np.array([0, 2, 6, 3, 4, 1, 5, 7]),
                np.array([0, 1, 2, 0, 0, 2, 1, 0]),))
R = CubeMove(R_turn, "R")
R2 = CubeMove(R_turn*R_turn, "R2")
R3 = CubeMove(R_turn*R_turn*R_turn, "R'")
R.forbidden_next = (R, R2, R3)
R2.forbidden_next = (R, R3, R2)
R3.forbidden_next = (R, R2, R3)

# Définition de U, U', U2

U_turn  = CubeState2((np.array([0, 1, 2, 3, 5, 6, 7, 4]),
                np.array([0, 0, 0, 0, 0, 0, 0, 0])))
U = CubeMove(U_turn, "U")
U2 = CubeMove(U_turn*U_turn, "U2")
U3 = CubeMove(U_turn*U_turn*U_turn, "U'")
U.forbidden_next = (U, U2, U3)
U2.forbidden_next = (U, U3, U2)
U3.forbidden_next = (U, U2, U3)

# Définition de F, F', F2

F_turn  = CubeState2((np.array([1, 5, 2, 3, 0, 4, 6, 7]),
                np.array([1, 2, 0, 0, 2, 1, 0, 0])))
F = CubeMove(F_turn, "F")
F2 = CubeMove(F_turn*F_turn, "F2")
F3 = CubeMove(F_turn*F_turn*F_turn, "F'")
F.forbidden_next = (F, F2, F3)
F2.forbidden_next = (F, F3, F2)
F3.forbidden_next = (F, F2, F3)

cube2_moves = (R, R2, R3, U, U2, U3, F, F2, F3)

class Cube2(CubeState2):
    """
    The 2x2x2 cube puzzle implementation
    For now a wrapper class to use the solvers.
    """
    def allowed_moves(self, previous):

        forbidden = previous.forbidden_next if previous is not None else ()
        possible_moves = [move for move in cube2_moves if (move not in forbidden)]
        return tuple(possible_moves)

    def apply(self, move):

        self.mult(move.turn)

    def shuffle(self, N=100):

        previous = None
        moves = []
        for move in range(N):
            poss = self.allowed_moves(previous)
            choice = random.choice(poss)
            self.apply(choice)
            previous = choice
            moves.append(choice)
        return moves

    @property
    def is_solved(self):
        return np.array_equal(self.CP, np.array([0, 1, 2, 3, 4, 5, 6, 7])) and \
                np.array_equal(self.CO, np.array([0, 0, 0, 0, 0, 0, 0, 0]))

    def copy(self):
        return Cube2((self.CP, self.CO))

    def is_solvable(self):
        return self.isSolvable()
