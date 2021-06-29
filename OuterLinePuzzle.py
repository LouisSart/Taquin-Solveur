from Solver import *
from Puzzle import Puzzle
import cProfile

class OuterLinePuzzle(Puzzle):

    def __init__(self, shape=(3,3), pos=None):

        self.shape = shape
        m, n = self.shape
        if pos is None:
            self.pos = [(0,0)]
            for i in range(1,m):  self.pos.append((i-1,n-1))
            for j in range(n):    self.pos.append((m-1,j))
        else: self.pos = pos

    def __repr__(self):
        return f"OuterLinePuzzle(pos={self.pos})"

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
        return OuterLinePuzzle(self.shape, self.pos[:])

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

def outer_line_manhattan(puzzle):
    m, n = puzzle.shape
    counter = 0
    for i, pos in enumerate(puzzle.pos[1:m]):
        I, J = pos
        counter += sum((abs(I-i),abs(n-1-J)))
    for j, pos in enumerate(puzzle.pos[m:]):
        I, J = pos
        counter += sum((abs(m-1-I),abs(j-J)))
    return counter


if __name__ == "__main__":
    puzzle = OuterLinePuzzle(shape=(3,4))
    puzzle.shuffle(300)
    print(puzzle)
    solver=IDAstar(heuristic=outer_line_manhattan)
    # cProfile.run("solver.solve(puzzle)")
    solver.solve(puzzle)
    solver.print_solutions()
