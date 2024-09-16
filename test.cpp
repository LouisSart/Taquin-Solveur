#include "src/manhattan.hpp"
#include "src/search.hpp"
#include "src/taquin.hpp"
#include "src/wd.hpp"

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

void test_search() {
  Taquin<3> taquin({8, 0, 6, 5, 4, 7, 2, 3, 1});

  auto root = make_root(taquin);
  auto solutions = IDAstar<false>(root, manhattan<3>);
  assert(solutions.size() == 1);
  assert(solutions[0]->get_path().size() == 27);
}

void test_wd() {

  auto wd3 = WDTaquin<3>();
  wd3.apply({U, 1});
  wd3.apply({U, 0});
  wd3.apply({D, 1});
  wd3.apply({D, 2});

  assert(generate_table<4>().size() == 24964);
  assert(generate_table<3>().size() == 105);
}

int main() {
  test_possible_moves();
  test_manhattan();
  test_search();
  test_wd();
  return 0;
}