Compile with:

g++ -Wall -std=c++20 main.cpp -o solve


Solve with:

./solve [N] [options] [scramble]

N is the puzzle size (e.g. N = 4 for the 15-puzzle). Only sizes 3 and 4 are implemented
scramble is the sequence of tile numbers, row by row from left to right, with blank spaces as separator. The empty slot is numbered 0.
Solved state for the 8-puzzle : "1 2 3 4 5 6 7 8 0"

Move interpretation : 
"R" means slide the right tile into the empty slot
"L" means slide the left tile into the empty slot
"U" means slide the upper tile into the empty slot
"D" means slide the bottom tile into the empty slot

Options : -f will only solve the fringe, that is the first row and first column only
          -2p will use the two phase solver, it finds close-to-optimal solutions very fast see below for info. (only for N = 4) 

Examples (computation times may vary):

$./solve 3 "0 8 1 7 2 6 3 5 4"
[    8  1]
[ 7  2  6]
[ 3  5  4]
Searching at depth 18, nodes: 9, 2.13e-05
Searching at depth 20, nodes: 59, 0.000130601
Searching at depth 22, nodes: 240, 0.000559204
Searching at depth 24, nodes: 1098, 0.00224632
D D R U U R D L L U R D D R U U L D D L U R D R (24)


$./solve 4 "1 2 7 4 6 14 3 11 0 10 9 5 13 15 12 8"
[ 1  2  7  4]
[ 6 14  3 11]
[   10  9  5]
[13 15 12  8]
Searching at depth 22, nodes: 15, 4.02e-05
Searching at depth 24, nodes: 67, 0.000195501
Searching at depth 26, nodes: 441, 0.00105221
Searching at depth 28, nodes: 2146, 0.0144328
Searching at depth 30, nodes: 9910, 0.0261356
Searching at depth 32, nodes: 44263, 0.112801
Searching at depth 34, nodes: 191470, 0.448967
R U U R D D R D L L U R U R U L L D L D R R U L L D R U R U R D D D (34)
U U R R D D R D L L U R U L U L D D R R U R D D L U U L L D R D R R (34)

$./solve 3 -f "0 1 2 3 4 5 6 7 8"
[    1  2]
[ 3  4  5]
[ 6  7  8]
Searching at depth 19, nodes: 36, 5.2241e-05
D R R U L L D D R U U R D L L U R R D (19)


Two phase solver

Phase one : solve the fringe (e.g. the top row and left column)
Phase two : solve the remaining 8-puzzle in the bottom right corner
Note that the pieces of the fringe are allowed to move in phase two,
if it gives a shorter path to solved.

I tried to build a two phase solver in the fashion of Kociemba. That is : try
to find fringe solutions of increasing lengths until you find a finish of
length 0. Unfortunately this doesn't work well because a longer fringe
solution almost never leads to a shorter finish (which is the case for Domino
reduction in Kociemba's algorithm).

However, because god's number for phases 1 and 2 is way smaller than for the
whole 15-puzzle, we can just generate every phase one optimal path, and then use a standard optimal
solver on the resulting states. This gives close-to-optimal solutions in a very short amount of time
(in fact, the bottleneck here is the loading of the pruning table for phase one, by a huge margin)

Solutions lengths of the two phase algorithm on 80 optimal positions (17 antipodes for the 15 puzzle):
        {82 80 86 86 84 86 88 88 86 84 86 86 88 80 88 82 80}

TO DO:
Use the fringe table to improve pruning in optimal solver
Use symmetry conjugation in pruning table building to accelerate generation