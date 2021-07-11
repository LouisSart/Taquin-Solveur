import pickle
from EpicSolver.heuristics import manhattan
from EpicSolver.taquin import Taquin
from EpicSolver.cube2 import Cube2

def CO22_vs_CP22_benchmark():
    with open("tables/22CO_table.pkl", "rb") as f:
        co_table = pickle.load(f)

    with open("tables/22CP_table.pkl", "rb") as f:
        cp_table = pickle.load(f)

    puzzle = Cube2()
    N = 10000
    values = []

    for k in range(N):

        puzzle.shuffle(23)
        cph = cp_table[tuple(puzzle.CP).__hash__()]
        coh = co_table[tuple(puzzle.CO).__hash__()]
        values.append((cph, coh))

    cp_wins = sum([int(cph>coh) for cph, coh in values])
    co_wins = sum([int(coh>cph) for cph, coh in values])
    cp_mean = sum([cph for cph, coh in values])/len(values)
    co_mean = sum([coh for cph, coh in values])/len(values)
    max_mean = sum(max(cph, coh) for cph, coh in values)/len(values)
    cp_dom  = sum([cph-coh if cph>coh else 0 for cph, coh in values])/cp_wins
    co_dom  = sum([coh-cph if coh>cph else 0 for cph, coh in values])/co_wins

    print(f"Ran {N} heuristic computations")
    print("CP wins:", cp_wins, "CO wins:", co_wins, f"Ties : {N-co_wins-cp_wins}")
    print("CP mean :", cp_mean)
    print("CO mean :", co_mean)
    print("Max mean :", max_mean)
    print("CP mean gain in wins", cp_dom)
    print("CO mean gain in wins", co_dom)
    print("CP score (total gain in wins/number of runs):", cp_dom*cp_wins/N)
    print("CO score (total gain in wins/number of runs):", co_dom*co_wins/N)

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
