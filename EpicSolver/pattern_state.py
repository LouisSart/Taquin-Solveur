from .utils import valid_neighbours
from .pattern_move_table import move_tables as mt
from .pattern_table import PatternTaquin, pattern_database as pdb


class PatternState:
    size = None
    bt_pos = None
    patterns = None
    puzzles = None

    def __init__(self, size, patterns):
        self.size = patterns[0].size
        self.patterns = tuple(patterns)
        assert all(len(set(p1.tiles) & set(p2.tiles)) == 0 for p1 in patterns for p2 in patterns if p2 is not p1),\
                "Patterns must have no common tiles for the database to be additive"
        assert all(p1.size == p2.size for p1 in patterns for p2 in patterns),\
                "Patterns must all have the same puzzle size"
        assert set(sum((p.tiles for p in patterns), tuple())) == set(range(1,self.size**2)),\
                "Patterns must cover all taquin tiles"

    def from_taquin(self, taquin):
        self.puzzles = []
        mt.empty()
        for p in self.patterns:
            puzzle = PatternTaquin()
            puzzle.from_taquin(taquin, p)
            self.puzzles.append(puzzle)
            mt.load(self.size, len(p))
        self.bt_pos = taquin.bt_pos


    def __str__(self):
        its = tuple(iter(p.permutation) for p in self.puzzles)
        l = [str(i+1)+str(next(its[i])) for k in range(self.size**2) for i, p in enumerate(self.puzzles) if p.layout[k]==1]
        l.insert(self.bt_pos[0]*self.size+self.bt_pos[1], " x")
        s = "\n".join(" ".join(ll for ll in l[i*self.size:(i+1)*self.size]) for i in range(self.size))
        return s
