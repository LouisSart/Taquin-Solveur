#pragma once
#include "fringe.hpp"
#include "taquin.hpp"
#include "wd.hpp"

WDTable<4> wd_table;

template <typename Node>
auto phase_two(Solutions<Node> p1_sols, unsigned max_depth) {

  Solutions<Node> ret;
  for (auto sol1 : p1_sols) {
    auto sol2 =
        IDAstar<false>(sol1, wd_table.get_estimator(), is_solved<4>, max_depth);
    ret.insert(ret.end(), sol2.begin(), sol2.end());
    if (sol2.size() > 0)
      max_depth = std::min(max_depth, sol2[0]->depth);
  }

  ret.erase(std::remove_if(ret.begin(), ret.end(),
                           [max_depth](const Node &node) {
                             return node->depth > max_depth;
                           }),
            ret.end());

  return ret;
}

template <typename Node> auto two_phase(Node &root) {
  // Most of the computation time is spent loading the fringe table lol
  const auto start{std::chrono::steady_clock::now()};

  load_fringe_table<4>(table4);
  wd_table = load_wd_table<4>();
  auto p1_sols = IDAstar<false>(root, fringe_estimate<4>, is_fringe_solved<4>);
  assert(p1_sols.size() > 0);
  auto p2_sols = phase_two(p1_sols, 150);

  const auto end{std::chrono::steady_clock::now()};
  const std::chrono::duration<double> elapsed_seconds{end - start};
  print("Solution(s) found in", elapsed_seconds.count(), "s");

  return p2_sols;
}