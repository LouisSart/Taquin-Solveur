#pragma once
#include "taquin.hpp"
#include "utils.hpp"
#include <array>
#include <algorithm> // std::all_of
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

  static unsigned nth_fringe_tile(const unsigned &n) {
    // return the global number of the nth fringe tile
    if (n <= N) return n; // first row
    else if (n == 2 * N) return 0; // blank is last
    else return N * (n % N) + 1; // first column
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

template<unsigned N> void taquin_from_index(const unsigned index, Taquin<N> &taquin) {
  unsigned p_index = index % Fringe<N>::N_PERM;
  unsigned l_index = index / Fringe<N>::N_PERM;

  std::array<unsigned, N * N> layout;
  layout_from_index(l_index, layout, 2 * N);
  
  std::array<unsigned, 2 * N> perm;
  permutation_from_index(p_index, perm);

  unsigned i = 0;
  for (unsigned k = 0; k < N * N; ++k){
    if (layout[k] == 1){
      taquin[k] = Fringe<N>::nth_fringe_tile(perm[i]);
      if (taquin[k] == 0) taquin.blank = k;
      ++i;
    } else {
      taquin[k] = N * N;
    }
  }
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
auto generate_fringe_BFS(std::array<uint8_t, Fringe<N>::TABLE_SIZE> &table, unsigned &counter, unsigned max_depth = 62) {
  assert(table.size() == Fringe<N>::TABLE_SIZE);
  assert(std::all_of(table.begin(), table.end(), [](const unsigned &i){return i == UINT8_MAX;}));

  unsigned search_depth = 0;

  Taquin<N> root;
  unsigned depth = 0;
  std::deque<Taquin<N>> queue = init_queue<N>();
  counter = queue.size();

  for (auto root : queue) {
    table[fringe_index(root)] = 0;
  }

  while (queue.size() > 0 && search_depth < max_depth) {
    auto taquin = queue.back();
    unsigned index = fringe_index(taquin);
    assert(index < Fringe<N>::TABLE_SIZE);
    depth = table[index];

    if constexpr (verbose) {
      if (depth == search_depth) {
        print("Depth", depth, ":", counter, "nodes");
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
    }

    queue.pop_back();
  }


}

template <unsigned N, bool verbose = false>
void forward_scan_fringe(std::array<uint8_t, Fringe<N>::TABLE_SIZE> &table, unsigned &counter, unsigned start_depth = 0, unsigned max_depth = 62) {
  unsigned depth = start_depth;
  Taquin<N> dummy;
  while (depth < max_depth){
    for (unsigned k = 0; k < Fringe<N>::TABLE_SIZE; ++k){
      if (table[k] == depth - 1){
        taquin_from_index(k, dummy);
        auto children = get_children(dummy);
        for (auto child : children) {
          unsigned c = fringe_index(child);
          if (table[c] == UINT8_MAX){
            table[c] = depth;
            ++counter;
          }
        }
      }
    }
    if constexpr (verbose) print("Depth", depth, ":", counter, "nodes");
    depth++;
  }
}

template <unsigned N, bool verbose = false>
void backward_scan_fringe(std::array<uint8_t, Fringe<N>::TABLE_SIZE> &table, unsigned &counter, unsigned start_depth = 0, unsigned max_depth = 62) {
  unsigned depth = start_depth;
  Taquin<N> dummy;
  while (depth < max_depth){
    for (unsigned k = 0; k < Fringe<N>::TABLE_SIZE; ++k){
      if (table[k] == UINT8_MAX){
        taquin_from_index(k, dummy);
        auto children = get_children(dummy);
        for (auto child : children) {
          unsigned c = fringe_index(child);
          if (table[c] == depth - 1){
            table[k] = depth;
            ++counter;
            break;
          }
        }
      }
    }
    if constexpr (verbose) print("Depth", depth, ":", counter, "nodes");
    depth++;
  }
}

template <unsigned N, bool verbose = false>
void generate_fringe_table(std::array<uint8_t, Fringe<N>::TABLE_SIZE> &table) {
  // Generating the fringe table is done in three phases :
  // BFS on the first few levels, forward scan in the middle part
  // and finally a backward scan on the last few levels.
  // It feels like the switch to forward scan doesn't make a great difference in 
  // computation time.
  // However the key part is to tune second switch at the level where 96%
  // of the table entries are populated. This accelerates the process most
  
  unsigned first_switch, second_switch, max_depth;
  if constexpr (N == 3){
    first_switch = 20;
    second_switch = 24;
    max_depth = 29;
  }
  if constexpr (N == 4){
    first_switch = 40;
    second_switch = 47;
    max_depth = 62;
  }
  
  unsigned counter = 0;
  const auto start{std::chrono::steady_clock::now()};
  std::chrono::duration<double> elapsed_seconds;
  table.fill(UINT8_MAX);

  generate_fringe_BFS<N, verbose>(table, counter, first_switch);

  if constexpr (verbose) {
    elapsed_seconds = std::chrono::steady_clock::now() - start;
    print("Duration", elapsed_seconds.count());
    print("Switching to forward scan");
  }

  forward_scan_fringe<N, verbose>(table, counter, first_switch, second_switch);

  if constexpr (verbose) {
    elapsed_seconds = std::chrono::steady_clock::now() - start;
    print("Duration", elapsed_seconds.count());
    print("Switching to backward scan");
  }

  backward_scan_fringe<N, verbose>(table, counter, second_switch, max_depth);

  if constexpr (verbose) {
    elapsed_seconds = std::chrono::steady_clock::now() - start;
    print("Table generated in", elapsed_seconds.count());
  }

  assert(std::all_of(table.begin(), table.end(), [](const unsigned &i){return i != UINT8_MAX;}));
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

template <unsigned N, bool verbose = false>
auto fringe_table_statistics(std::array<uint8_t, Fringe<N>::TABLE_SIZE> &table) {
  std::array<unsigned, 70> distribution;
  distribution.fill(0);

  for (unsigned k : table) {
    distribution[k] += 1;
  }

  if constexpr (verbose){
    for(unsigned i = 0; i < distribution.size(); ++i){
      std::cout << i << " " << distribution[i] << std::endl;;
    }
  }
  return distribution;
};

std::array<uint8_t, Fringe<3>::TABLE_SIZE> table3;
std::array<uint8_t, Fringe<4>::TABLE_SIZE> table4;

template <unsigned N>
void load_fringe_table(std::array<uint8_t, Fringe<N>::TABLE_SIZE> &table) {
  std::filesystem::path table_dir = "pruning_tables";

  auto filename = table_dir / ("fringe_" + std::to_string(N) + ".dat");

  if (fs::exists(filename)) {
    load_binary(filename, table.data(), table.size());
    // fringe_table_statistics<N, true>(table);
  } else {
    std::cout << "Pruning table not found, generating" << std::endl;
    generate_fringe_table<N, true>(table);
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