from .utils import valid_neighbours
from .taquin import taquin_moves
from .pattern_move_table import move_tables as mt
from .pattern_table import PatternTaquin, pattern_database as pdb, moves as pattern_moves, PatternMove


class PatternState:
    size = None
    bt_pos = None
    patterns = None
    puzzles = None

    def from_taquin(self, taquin, patterns):
        self.size = patterns[0].size
        self.patterns = tuple(patterns)
        assert all(len(set(p1.tiles) & set(p2.tiles)) == 0 for p1 in patterns for p2 in patterns if p2 is not p1),\
                "Patterns must have no common tiles for the database to be additive"
        assert all(p1.size == p2.size for p1 in patterns for p2 in patterns),\
                "Patterns must all have the same puzzle size"
        assert set(sum((p.tiles for p in patterns), tuple())) == set(range(1,self.size**2)),\
                "Patterns must cover all taquin tiles"
        pdb.empty()
        for p in self.patterns:
            pdb.load(p.size, p.tiles)
        self.puzzles = []
        mt.empty()
        for p in self.patterns:
            puzzle = PatternTaquin()
            puzzle.from_taquin(taquin, p)
            self.puzzles.append(puzzle)
            mt.load(self.size, len(p))
        self.bt_pos = taquin.bt_pos

    @property
    def estimate(self):
        return sum(pdb[(ptn.size, ptn.tiles)][pzl.lindex, pzl.pindex] for ptn, pzl in zip(self.patterns, self.puzzles))

    @property
    def is_solved(self):
        return self.estimate == 0

    def valid_moves(self, previous=None):
        forbidden = previous.forbidden_next if previous else None
        return tuple(m for m in taquin_moves[(self.size, self.size)][self.bt_pos] if m is not forbidden)

    def update(self, move):
        i, j = self.bt_pos
        ii, jj = move.slide
        tile = (i+ii)*self.size + (j+jj)
        for p in self.puzzles:
            if p.layout[tile] == 1:
                p.apply(PatternMove(bt=i*self.size+j, tile=tile, str=str(move)))
                break
        self.bt_pos = i+ii, j+jj
    def copy(self):
        r = PatternState()
        r.patterns = self.patterns
        r.puzzles = tuple(p.copy() for p in self.puzzles)
        r.size = self.size
        r.bt_pos = self.bt_pos
        return r

    def __str__(self):
        its = tuple(iter(p.permutation) for p in self.puzzles)
        l = [str(i+1)+str(next(its[i])) for k in range(self.size**2) for i, p in enumerate(self.puzzles) if p.layout[k]==1]
        l.insert(self.bt_pos[0]*self.size+self.bt_pos[1], " x")
        s = "\n".join(" ".join(ll for ll in l[i*self.size:(i+1)*self.size]) for i in range(self.size))
        return s
