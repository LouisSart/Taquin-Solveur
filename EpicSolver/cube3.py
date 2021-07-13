import numpy as np
import random

class CubeState:

    def __init__(self, state_arrays=(np.array([0, 1, 2, 3, 4, 5, 6, 7]),
        np.array([0, 0, 0, 0, 0, 0, 0, 0]),
        np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]),
        np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]))):
        (CP,CO,EP,EO)=state_arrays
        self.CP = CP
        self.CO = CO
        self.EP = EP
        self.EO = EO

    def tofile(self, f):
        assert not f.closed
        assert f.mode[0] == 'a'
        self.CP.tofile(f)
        self.CO.tofile(f)
        self.EP.tofile(f)
        self.EO.tofile(f)

    def fromfile(self, f):
        assert not f.closed
        assert f.mode[0] == 'r'
        self.CP = np.fromfile(f, dtype=int, count=8)
        self.CO = np.fromfile(f, dtype=int, count=8)
        self.EP = np.fromfile(f, dtype=int, count=12)
        self.EO = np.fromfile(f, dtype=int, count=12)

    @property
    def I(self):
        # Calcul de l'inverse. Retourne un objet CubeState tel que self*self.i()=solved
        CP  =  np.arange(8)
        CO  =  np.zeros(8)
        EP  =  np.arange(12)
        EO  =  np.zeros(12)

        for i, p in enumerate(self.CP):
            CP[p] = i
        for i, p in enumerate(self.EP):
            EP[p] = i

        CO  =  np.remainder(-self.CO[CP], 3)
        EO  =  np.remainder(-self.EO[EP], 2)
        return CubeState((CP, CO, EP, EO))

    def isSolvable(self):

        if not np.remainder(np.sum(self.EO),2)==0: return False
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


        checked_edges=[]
        k=0
        n_edge_translations=0
        while len(checked_edges) < 12:
            if self.EP[k] in checked_edges :
                k+=1
            else:
                cycle_start=k
                i=self.EP[k]
                checked_edges += [k]
                while not i==cycle_start:
                    n_edge_translations+=1
                    checked_edges += [i]
                    i=self.EP[i]

        if not (-1)**(n_corner_translations+n_edge_translations)==1 : return False
        return True

    def applyAlg(self, alg):
        for move_int in alg:
            self *= all_moves[move_int]
        return self

    def mult(self, other):
        ''' Multiplication en place. Mêmes performances que l'autre... '''
        assert other.__class__ is CubeState, "Vous essayez de multiplier nimp"

        self.CP   =  self.CP[other.CP]
        self.CO   =  np.remainder(self.CO[other.CP] + other.CO, 3)
        self.EP   =  self.EP[other.EP]
        self.EO   =  np.remainder(self.EO[other.EP] + other.EO, 2)

    def copy(self):
        return CubeState((self.CP, self.CO, self.EP, self.EO))

    def __mul__(self, other):
        assert other.__class__ is CubeState, "Vous essayez de multiplier nimp"

        CP   =  self.CP[other.CP]
        CO   =  np.remainder(self.CO[other.CP] + other.CO, 3)
        EP   =  self.EP[other.EP]
        EO   =  np.remainder(self.EO[other.EP] + other.EO, 2)

        return CubeState((CP, CO, EP, EO))

    def __str__(self):
        return "CP = " + self.CP.__str__() + "\n" + \
               "CO = " + self.CO.__str__() + "\n" + \
               "EP = " + self.EP.__str__() + "\n" + \
               "EO = " + self.EO.__str__() + "\n"

class CubeMove:
    def __init__(self, turn, repr, forbidden_next=None):
        self.turn = turn
        self.repr = repr
        self.forbidden_next = forbidden_next
    def __str__(self):
        return self.repr
# Définition des mouvements autorisés du Cube
# Définition de R, R', R2

R_turn  = CubeState((np.array([0, 2, 6, 3, 4, 1, 5, 7]),
                np.array([0, 1, 2, 0, 0, 2, 1, 0]),
                np.array([0, 6, 2, 3, 4, 1, 9, 7, 8, 5, 10, 11]),
                np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])))
R = CubeMove(R_turn, "R")
R2 = CubeMove(R_turn*R_turn, "R2")
R3 = CubeMove(R_turn*R_turn*R_turn, "R'")
R.forbidden_next = (R, R2, R3)
R2.forbidden_next = (R, R3, R2)
R3.forbidden_next = (R, R2, R3)

# Définition de U, U', U2

U_turn  = CubeState((np.array([0, 1, 2, 3, 5, 6, 7, 4]),
                np.array([0, 0, 0, 0, 0, 0, 0, 0]),
                np.array([0, 1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 8]),
                np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])))
U = CubeMove(U_turn, "U")
U2 = CubeMove(U_turn*U_turn, "U2")
U3 = CubeMove(U_turn*U_turn*U_turn, "U'")
U.forbidden_next = (U, U2, U3)
U2.forbidden_next = (U, U3, U2)
U3.forbidden_next = (U, U2, U3)

# Définition de F, F', F2

F_turn  = CubeState((np.array([1, 5, 2, 3, 0, 4, 6, 7]),
                np.array([1, 2, 0, 0, 2, 1, 0, 0]),
                np.array([5, 1, 2, 3, 0, 8, 6, 7, 4, 9, 10, 11]),
                np.array([1, 0, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0])))
F = CubeMove(F_turn, "F")
F2 = CubeMove(F_turn*F_turn, "F2")
F3 = CubeMove(F_turn*F_turn*F_turn, "F'")
F.forbidden_next = (F, F2, F3)
F2.forbidden_next = (F, F3, F2)
F3.forbidden_next = (F, F2, F3)
# Définition de L, L', L2

L_turn  = CubeState((np.array([4, 1, 2, 0, 7, 5, 6, 3]),
                np.array([2, 0, 0, 1, 1, 0, 0, 2]),
                np.array([0, 1, 2, 4, 11, 5, 6, 3, 8, 9, 10, 7]),
                np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])))
L = CubeMove(L_turn, "L")
L2 = CubeMove(L_turn*L_turn, "L2")
L3 = CubeMove(L_turn*L_turn*L_turn, "L'")
L.forbidden_next = (L, L2, L3, R, R2, R3)
L2.forbidden_next = (L, L3, L2, R, R2, R3)
L3.forbidden_next = (L, L2, L3, R, R2, R3)

# Définition de D, D', D2

D_turn  = CubeState((np.array([3, 0, 1, 2, 4, 5, 6, 7]),
                np.array([0, 0, 0, 0, 0, 0, 0, 0]),
                np.array([3, 0, 1, 2, 4, 5, 6, 7, 8, 9, 10, 11]),
                np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])))
D = CubeMove(D_turn, "D")
D2 = CubeMove(D_turn*D_turn, "D2")
D3 = CubeMove(D_turn*D_turn*D_turn, "D'")
D.forbidden_next = (D, D2, D3, U, U2, U3)
D2.forbidden_next = (D, D3, D2, U, U2, U3)
D3.forbidden_next = (D, D2, D3, U, U2, U3)

# Définition de B, B', B2

B_turn  = CubeState((np.array([0, 1, 3, 7, 4, 5, 2, 6]),
                np.array([0, 0, 1, 2, 0, 0, 2, 1]),
                np.array([0, 1, 7, 3, 4, 5, 2, 10, 8, 9, 6, 11]),
                np.array([0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 1, 0])))
B = CubeMove(B_turn, "B")
B2 = CubeMove(B_turn*B_turn, "B2")
B3 = CubeMove(B_turn*B_turn*B_turn, "B'")
B.forbidden_next = (B, B2, B3, F, F2, F3)
B2.forbidden_next = (B, B3, B2, F, F2, F3)
B3.forbidden_next = (B, B2, B3, F, F2, F3)

cube_moves = (R, R2, R3, L, L2, L3, U, U2, U3, D, D2, D3, F, F2, F3, B, B2, B3)

class Cube3(CubeState):
    """
    The 3x3x3 cube puzzle implementation
    For now a wrapper class to use the solvers.
    """
    def allowed_moves(self, previous):

        forbidden = previous.forbidden_next if previous is not None else ()
        possible_moves = [move for move in cube_moves if (move not in forbidden)]
        return tuple(possible_moves)

    def apply(self, move):

        self.mult(move.turn)

    def shuffle(self, N=100):

        previous = None
        for move in range(N):
            poss = self.allowed_moves(previous)
            choice = random.choice(poss)
            self.apply(choice)
            previous = choice

    @property
    def is_solved(self):
        return np.array_equal(self.CP, np.array([0, 1, 2, 3, 4, 5, 6, 7])) and \
                np.array_equal(self.CO, np.array([0, 0, 0, 0, 0, 0, 0, 0])) and \
                np.array_equal(self.EP, np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])) and \
                np.array_equal(self.EO, np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]))

    def copy(self):
        return Cube3((self.CP, self.CO, self.EP, self.EO))

    def is_solvable(self):
        return self.isSolvable()
        return True
