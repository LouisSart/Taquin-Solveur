Compile with:

g++ -Wall -std=c++20 main.cpp


Solve with:

./solve [N] [scramble]

where N is the puzzle size (for a 4x4, N=4) and the scramble is the sequence of tile numbers, row by row from left to right, with blank spaces as separator

Examples (computation times may vary):

$./solve 3 "0 8 1 7 2 6 3 5 4"
[ x  8  1]
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
[ x 10  9  5]
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
