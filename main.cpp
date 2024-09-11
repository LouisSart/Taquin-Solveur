#include "src/taquin.hpp"

int main() {
  auto taquin = Taquin<4>();
  assert(taquin.is_possible(U));
  taquin.apply(U);
  taquin.apply(U);
  taquin.apply(U);
  taquin.show();
  assert(taquin.is_possible(L));
  for (Move move : taquin.possible_moves(U)) {
    std::cout << move << std::endl;
  }
  return 0;
}