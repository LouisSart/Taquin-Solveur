#include "src/fringe.hpp"
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
  Taquin<3> taquin("8 0 6 5 4 7 2 3 1");

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

  auto table3 = generate_wd_table<3>();

  Taquin<3> t3("8 0 4 3 1 5 6 2 7");
  auto root = make_root(t3);
  auto solutions = IDAstar<false>(root, table3.get_estimator());
  assert(solutions.size() == 1);
  assert(solutions[0]->get_path().size() == 23);
}

void test_fringe() {
  auto t = FringeTaquin<4>();
  assert(permutation_index(t) == 0);
  t.apply({U, U, L, L, L, D, D, R, R, U, U, L, L, D});
  t.show();
  assert(layout_index(t) == 0);
  assert(permutation_index(t) == 5);
}

std::array<uint8_t, FringeConstants<4>::TABLE_SIZE> table;

int main() {
  test_possible_moves();
  test_manhattan();
  test_search();
  test_wd();
  test_fringe();

  generate_fringe_table<4, true>(table);

  return 0;
}