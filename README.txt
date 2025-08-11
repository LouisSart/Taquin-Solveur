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


Fringe heuristic:

Pattern database where you look at the positions of the fringe tiles and the blank. An N*N-puzzle has (N²)!/(N² - 2N)²! distinct "fringe cosets".
Here are the distributions of fringe states for the 8-puzzle and 15-puzzle:

8-puzzle:
0 4 / 60480
1 8 / 60480
2 14 / 60480
3 22 / 60480
4 38 / 60480
5 70 / 60480
6 115 / 60480
7 182 / 60480
8 295 / 60480
9 483 / 60480
10 783 / 60480
11 1256 / 60480
12 1997 / 60480
13 3133 / 60480
14 4872 / 60480
15 7375 / 60480
16 10916 / 60480
17 15535 / 60480
18 21395 / 60480
19 28321 / 60480
20 35987 / 60480
21 43483 / 60480
22 50039 / 60480
23 54948 / 60480
24 58191 / 60480
25 59792 / 60480
26 60334 / 60480
27 60458 / 60480
28 60480 / 60480

15-puzzle
0 9 / 518918400
1 15 / 518918400
2 25 / 518918400
3 41 / 518918400
4 75 / 518918400
5 155 / 518918400
6 300 / 518918400
7 547 / 518918400
8 978 / 518918400
9 1776 / 518918400
10 3241 / 518918400
11 5862 / 518918400
12 10434 / 518918400
13 18481 / 518918400
14 32435 / 518918400
15 56303 / 518918400
16 96581 / 518918400
17 164124 / 518918400
18 275351 / 518918400
19 455911 / 518918400
20 743446 / 518918400
21 1195491 / 518918400
22 1892256 / 518918400
23 2947133 / 518918400
24 4511011 / 518918400
25 6788210 / 518918400
26 10030491 / 518918400
27 14558600 / 518918400
28 20742284 / 518918400
29 29015206 / 518918400
30 39817168 / 518918400
31 53623362 / 518918400
32 70812961 / 518918400
33 91757647 / 518918400
34 116577186 / 518918400
35 145271970 / 518918400
36 177478238 / 518918400
37 212680288 / 518918400
38 249935028 / 518918400
39 288212027 / 518918400
40 326180658 / 518918400
41 362598592 / 518918400
42 396168668 / 518918400
43 425921281 / 518918400
44 451154060 / 518918400
45 471616760 / 518918400
46 487397344 / 518918400
47 498959137 / 518918400
48 506949910 / 518918400
49 512161729 / 518918400
50 515339279 / 518918400
51 517156373 / 518918400
52 518113102 / 518918400
53 518583302 / 518918400
54 518790636 / 518918400
55 518875810 / 518918400
56 518905548 / 518918400
57 518915231 / 518918400
58 518917726 / 518918400
59 518918308 / 518918400
60 518918390 / 518918400
61 518918400 / 518918400
Table generated in 309.022

TO DO:
Use the fringe table to improve pruning in optimal solver
Use symmetry conjugation in pruning table building to accelerate generation