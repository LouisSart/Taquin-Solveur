#include "src/fringe.hpp"
#include "src/manhattan.hpp"
#include "src/search.hpp"
#include "src/taquin.hpp"
#include "src/twophase.hpp"
#include "src/utils.hpp"
#include "src/wd.hpp"

template <unsigned N> void solve(std::string input) {
  auto wd_table = load_wd_table<N>();

  auto wd_estimate = wd_table.get_estimator();

  Taquin<N> taquin(input);
  taquin.show();
  auto root = make_root(taquin);
  auto solutions = IDAstar<true>(root, wd_estimate, is_solved<N>);
  solutions.show();
}

int main(int argc, const char *argv[]) {
  unsigned N = std::stoi(argv[1]);
  bool fringe = find_option("-f", argc, argv);
  bool twophase = find_option("-2p", argc, argv);

  if (N == 3) {
    load_fringe_table<3>(table3);
    if (fringe) {
      solve_fringe<3>(argv[argc - 1]);
    } else {
      solve<3>(argv[argc - 1]);
    }
  } else if (N == 4) {
    load_fringe_table<4>(table4);
    if (fringe) {
      solve_fringe<4>(argv[argc - 1]);
    } else if (twophase) {
      solve_two_phase(argv[argc - 1]);
    } else {
      solve<4>(argv[argc - 1]);
    }
  } else {
    print("Wrong input, use ./solve [N] [options] [scramble]");
    print("with N = {3, 4}");
    print("options : -f  only solve the fringe");
    print("          -2p two phase solver (only for N = 4)");
  }

  return 0;
}