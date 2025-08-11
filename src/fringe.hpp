#pragma once
#include "taquin.hpp"
#include "utils.hpp"
#include <array>
#include <cstdint>
#include <deque>
#include <iomanip>
#include <iostream>
#include <memory>
#include <set>

template <unsigned N> struct Fringe {
  // Fringe includes the blank tile as well
  static constexpr unsigned N_TILES = 2 * N;
  static constexpr unsigned N_LAYOUT = binomial(Taquin<N>::N_TILES, N_TILES);
  static constexpr unsigned N_PERM = factorial(N_TILES);
  static constexpr unsigned TABLE_SIZE = N_LAYOUT * N_PERM;

  static bool is_fringe_tile(const unsigned &tile) {
    if ((tile - 1) % N == 0 || (tile - 1) / N == 0 || tile == 0)
      return true;
    return false;
  }
};

template <unsigned N> unsigned permutation_index(const Taquin<N> &ft) {
  unsigned c = 0, ki = 1, n = Fringe<N>::N_TILES;
  for (unsigned i = 1; i < N * N; ++i) {
    if (Fringe<N>::is_fringe_tile(ft[i - 1])) {
      c *= (n - ki + 1);
      ++ki;
      for (unsigned j = i + 1; j <= N * N; ++j) {
        if (Fringe<N>::is_fringe_tile(ft[j - 1]) && (ft[i - 1] > ft[j - 1])) {
          c += 1;
        }
      }
    }
  }
  return c;
}

template <unsigned N> unsigned layout_index(const Taquin<N> &ft) {
  // n: number of positions
  // r: number of pieces
  unsigned r = Fringe<N>::N_TILES;
  unsigned t = 0;
  for (unsigned i = N * N - 1; i > 0; --i) {
    if (Fringe<N>::is_fringe_tile(ft[i])) {
      t += binomial(i, r);
      r -= 1;
    }
  }
  return t;
}

template <unsigned N> unsigned fringe_index(const Taquin<N> &ft) {
  return layout_index(ft) * Fringe<N>::N_PERM + permutation_index(ft);
}

template <unsigned N> std::deque<Taquin<N>> init_queue() {
  // There are (N - 1) ** 2 states that are at depth 0
  // which are hard coded below
  std::deque<Taquin<N>> ret;
  if constexpr (N == 4) {
    ret.emplace_back("1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 0");
    ret.emplace_back("1 2 3 4 5 6 7 8 9 10 11 12 13 14 0 15");
    ret.emplace_back("1 2 3 4 5 6 7 8 9 10 11 12 13 0 14 15");
    ret.emplace_back("1 2 3 4 5 0 6 7 9 11 12 8 13 10 14 15");
    ret.emplace_back("1 2 3 4 5 6 0 7 9 11 12 8 13 10 14 15");
    ret.emplace_back("1 2 3 4 5 6 7 0 9 11 12 8 13 10 14 15");
    ret.emplace_back("1 2 3 4 5 6 7 8 9 11 12 0 13 10 14 15");
    ret.emplace_back("1 2 3 4 5 6 7 8 9 11 0 12 13 10 14 15");
    ret.emplace_back("1 2 3 4 5 6 7 8 9 0 11 12 13 10 14 15");
  } else if constexpr (N == 3) {
    ret.emplace_back("1 2 3 4 5 0 7 8 6");
    ret.emplace_back("1 2 3 4 0 5 7 8 6");
    ret.emplace_back("1 2 3 4 8 5 7 0 6");
    ret.emplace_back("1 2 3 4 5 6 7 8 0");
  }
  return ret;
}

template <unsigned N>
std::vector<Taquin<N>> get_children(const Taquin<N> &taquin) {
  std::vector<Taquin<N>> ret;
  for (auto move : taquin.possible_moves()) {
    Taquin<N> child = taquin;
    child.apply(move);
    ret.push_back(child);
  }
  return ret;
}

template <unsigned N, bool verbose = false>
auto generate_fringe_table(std::array<uint8_t, Fringe<N>::TABLE_SIZE> &table) {
  assert(table.size() == Fringe<N>::TABLE_SIZE);

  unsigned counter, search_depth = 0;
  const auto start{std::chrono::steady_clock::now()};

  Taquin<N> root;
  table.fill(UINT8_MAX);
  table[fringe_index(root)] = 0;
  std::deque<Taquin<N>> queue = init_queue<N>();
  counter = queue.size();

  for (auto root : queue) {
    table[fringe_index(root)] = 0;
  }

  while (queue.size() > 0) {
    auto taquin = queue.back();
    unsigned index = fringe_index(taquin);
    assert(index < Fringe<N>::TABLE_SIZE);
    unsigned depth = table[index];

    if constexpr (verbose) {
      if (depth == search_depth) {
        print(depth, counter, "/", Fringe<N>::TABLE_SIZE);
        ++search_depth;
      }
    }

    // Loop over children of that state
    for (Taquin<N> child : get_children(taquin)) {
      unsigned c_index = fringe_index(child);

      // If this child is a newly encountered state, store its depth
      // and put it in front of the queue
      if (table[c_index] == UINT8_MAX) {
        table[c_index] = depth + 1;
        queue.push_front(child);
        ++counter;
      }

      // The transposition conjugate of that position has to be
      // at the same depth in the tree. Let's add it before generating it
      // This makes almost no difference in terms of computation time
      // unsigned t_index = fringe_index(transpose_conjugate(child));
      // if (table[t_index] == UINT8_MAX) {
      //   table[t_index] = depth + 1;
      //   ++counter;
      // }
    }

    queue.pop_back();
  }

  if constexpr (verbose) {
    const auto end{std::chrono::steady_clock::now()};
    const std::chrono::duration<double> elapsed_seconds{end - start};
    print("Table generated in", elapsed_seconds.count());
  }
}

template <unsigned N> bool is_fringe_solved(const Taquin<N> &taquin) {
  for (unsigned k = 0; k < Taquin<N>::N_TILES; ++k) {
    if (Fringe<N>::is_fringe_tile(taquin[k]) && taquin[k] != 0) {
      if (taquin[k] != k + 1)
        return false;
    }
  }
  return true;
};

std::array<uint8_t, Fringe<3>::TABLE_SIZE> table3;
std::array<uint8_t, Fringe<4>::TABLE_SIZE> table4;

template <unsigned N>
void load_fringe_table(std::array<uint8_t, Fringe<N>::TABLE_SIZE> &table) {
  std::filesystem::path table_dir = "pruning_tables";

  auto filename = table_dir / ("fringe_" + std::to_string(N) + ".dat");

  if (fs::exists(filename)) {
    load_binary(filename, table.data(), table.size());
  } else {
    std::cout << "Pruning table not found, generating" << std::endl;
    generate_fringe_table<N>(table);
    fs::create_directories(table_dir);
    write_binary(filename, table.data(), table.size());
  }

  for (auto k : table) {
    assert(k >= 0);
    assert(k < UINT8_MAX);
  }
}

template <unsigned N> unsigned fringe_estimate(const Taquin<N> &taquin) {
  if constexpr (N == 3) {
    return table3[fringe_index(taquin)];
  } else if constexpr (N == 4) {
    return table4[fringe_index(taquin)];
  } else {
    assert(false);
  }
}

template <unsigned N> auto solve_fringe(std::string input) {
  Taquin<N> taquin(input);
  taquin.show();
  auto root = make_root(taquin);
  auto solutions = IDAstar<true>(root, fringe_estimate<N>, is_fringe_solved<N>);
  solutions.show();
}