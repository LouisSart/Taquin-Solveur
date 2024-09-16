#include "src/manhattan.hpp"
#include "src/taquin.hpp"

void test_possible_moves() {
  Taquin<4> taquin;

  assert(taquin.is_solved());
  assert(taquin.is_possible_move(U));
  assert(taquin.is_possible_move(L));

  taquin.apply({U, U, U, L, L, L, D, R, D, R});
  assert(!taquin.is_solved());
  assert(taquin.blank == 10);

  assert(taquin.possible_moves(R).size() == 3);
}

void test_manhattan() {
  Taquin<4> taquin;

  assert(manhattan(taquin) == 0);
  taquin.apply(L);
  assert(manhattan(taquin) == 1);
  assert(taquin.is_possible_move(U));
  taquin.apply({U, L, D, L, U, U, R, U, R});
  assert(manhattan(taquin) == 10);
}

int main() {
  test_possible_moves();
  test_manhattan();
  return 0;
}