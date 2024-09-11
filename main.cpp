#include "src/taquin.hpp"

Taquin<4> taquin;
Sequence sequence{U, U, U, L, L, L, D, R, D, R};

int main() {
  std::cout << sequence << std::endl;

  assert(taquin.is_possible(U));
  taquin.apply(sequence);
  taquin.show();

  for (Move move : taquin.possible_moves(sequence.back())) {
    std::cout << move << " ";
  }
  std::cout << std::endl;
  return 0;
}