import pickle
from EpicSolver.heuristics import manhattan
from EpicSolver.taquin import Taquin

def manhattan_vs_outer_line_benchmark():
    with open("tables/outer_line_table.pkl", "rb") as f:
        outer_line_table = pickle.load(f)

    puzzle = Taquin((3,3))
    N = 10000
    idx = {0:0,2:1,5:2,6:3,7:4,8:5}
    m_wins, o_wins = 0, 0
    m_score, o_score = 0, 0
    h_dict = {}

    for k in range(N):
        puzzle.random_state()
        pos = [0,0,0,0,0,0]
        for i in range(3):
            for j in range(3):
                tile = puzzle.tiles[i][j]
                if tile in (0,2,5,6,7,8):
                    pos[idx[tile]] = (i,j)
        l = tuple(pos).__hash__()
        m, o = manhattan(puzzle), outer_line_table[l]
        if m>o:
            m_wins+=1
            m_score+=m-o
        elif o>m:
            o_wins+=1
            o_score+=o-m
        h_dict.update({l:(m, o)})

    print(f"Ran {N} heuristic computations")
    print("Manhattan wins:", m_wins, "Outer line wins:", o_wins, f"Ties : {N-m_wins-o_wins}")
    print("Manhattan mean :", sum([x[0] for x in h_dict.values()])/len(h_dict))
    print("Outer line mean :", sum([x[1] for x in h_dict.values()])/len(h_dict))
    print("Manhattan mean gain in wins", m_score/m_wins)
    print("Outer line mean gain in wins", o_score/o_wins)
    print("Manhattan score (total gain in wins/number of runs):", m_score/N)
    print("Outer line score (total gain in wins/number of runs):", o_score/N)

if __name__ == "__main__":
    manhattan_vs_outer_line_benchmark()
