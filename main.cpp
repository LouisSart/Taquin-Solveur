#include "src/manhattan.hpp"
#include "src/search.hpp"
#include "src/taquin.hpp"
#include "src/utils.hpp"
#include "src/wd.hpp"

template <unsigned N> void solve(std::string input) {
  auto table = load_wd_table<N>();
  Taquin<N> taquin(input);
  taquin.show();
  auto root = make_root(taquin);
  auto solutions = IDAstar<true>(root, table.get_estimator());
  solutions.show();
}

int main(int argc, const char *argv[]) {
  unsigned N = std::stoi(argv[1]);

  if (N == 3) {
    solve<3>(argv[argc - 1]);
  } else if (N == 4) {
    solve<4>(argv[argc - 1]);
  } else {
    print("Wrong input, use ./solve [N] [scramble]");
    print("with N = {3, 4}");
  }

  return 0;
}