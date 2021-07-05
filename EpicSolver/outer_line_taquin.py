from .taquin import Taquin

class OuterLineTaquin(Taquin):

    def __init__(self, shape=(3,3), pos=None):

        self.shape = shape
        m, n = self.shape
        if pos is None:
            self.pos = [(0,0)]
            for i in range(1,m):  self.pos.append((i-1,n-1))
            for j in range(n):    self.pos.append((m-1,j))
        else: self.pos = pos

    def __repr__(self):
        return f"OuterLineTaquin(pos={self.pos})"

    def __str__(self):
        return self.__repr__()

    @property
    def bt_pos(self):
        return self.pos[0]

    @property
    def possible_swaps(self):

        bt_pos = self.pos[0]
        all_adjacents = [(bt_pos[0]-move[0], bt_pos[1]-move[1]) for move in [(1,0),(0,1),(-1,0),(0,-1)]]
        possible_adjacents = [adj for adj in all_adjacents if (0<=adj[0]<self.shape[0] and 0<=adj[1]<self.shape[1])]

        return tuple(possible_adjacents)

    def swap(self, pos):

        if pos not in self.pos:
            self.pos[0]=pos
        else:
            for k, my_pos in enumerate(self.pos):
                if my_pos == pos:
                    self.pos[0], self.pos[k] = self.pos[k], self.pos[0]

    def copy(self):
        return OuterLineTaquin(self.shape, self.pos[:])

    @property
    def bt_index(self):
        i,j = self.pos[0]
        return self.shape[1]*i+j

    @property
    def is_solved(self):
        m, n = self.shape
        for i, pos in enumerate(self.pos[1:m]):
            if not pos == (i,n-1): return False
        for j, pos in enumerate(self.pos[m:]):
            if not pos == (m-1,j): return False
        return True

    @property
    def is_solvable(self):
        return True
