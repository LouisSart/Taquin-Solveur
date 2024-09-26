#pragma once
#include "taquin.hpp"
#include "utils.hpp"
#include <array>
#include <cstdint>
#include <deque>
#include <iomanip>
#include <iostream>
#include <memory>
#include <unordered_map>

template <unsigned N> struct Fringe {
  static constexpr unsigned N_TILES = N * N;
  static constexpr unsigned N_FRINGE_TILES = 2 * N - 1;
  static constexpr unsigned N_LAYOUT = binomial(N * N, 2 * N - 1);
  static constexpr unsigned N_PERM = factorial(2 * N - 1);
  static constexpr unsigned TABLE_SIZE = N_LAYOUT * N_PERM;
  static constexpr std::array<bool, N_TILES> mask = [] {
    std::array<bool, N * N> ret;
    ret[0] = false;
    for (unsigned k = 1; k < N_TILES; ++k) {
      if ((k - 1) % N == 0 || (k - 1) / N == 0) {
        ret[k] = true;
      } else {
        ret[k] = false;
      }
    }
    return ret;
  }();

  static bool is_fringe_tile(const unsigned &tile) { return mask[tile]; }
};

template <unsigned N> struct FringeTaquin : Taquin<N> {
  unsigned depth;

  void show() const {
    for (unsigned r = 0; r < N; ++r) {
      std::cout << "[";
      for (unsigned c = 0; c < N; ++c) {
        if (r * N + c == this->blank)
          std::cout << std::setw(2) << "x"
                    << " ";
        else if (Fringe<N>::is_fringe_tile((*this)[r * N + c])) {
          std::cout << std::setw(2) << (*this)[r * N + c] << " ";
        } else {
          std::cout << std::setw(2) << "__"
                    << " ";
        }
      }
      std::cout << "\b]" << std::endl;
    }
  };
};

template <unsigned N> unsigned permutation_index(const FringeTaquin<N> &ft) {
  unsigned c = 0, ki = 1, n = 2 * N - 1;
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

template <unsigned N> unsigned layout_index(const FringeTaquin<N> &ft) {
  // n: number of positions
  // r: number of pieces
  unsigned r = Fringe<N>::N_FRINGE_TILES;
  unsigned t = 0;
  for (unsigned i = N * N - 1; i > 0; --i) {
    if (Fringe<N>::is_fringe_tile(ft[i])) {
      t += binomial(i, r);
      r -= 1;
    }
  }
  return t;
}

template <unsigned N> unsigned fringe_index(const FringeTaquin<N> &ft) {
  static unsigned N_PERM = factorial(2 * N - 1);
  return layout_index(ft) * N_PERM + permutation_index(ft);
}

bool blank_was_seen(const uint16_t &h, const unsigned &blank) {
  return (h / ipow(2, blank)) % 2;
}

template <unsigned N, bool verbose = false>
auto generate_fringe_table(std::array<uint8_t, Fringe<N>::TABLE_SIZE> &table) {

  auto SIZE = Fringe<N>::TABLE_SIZE;

  FringeTaquin<N> root;
  table.fill(0);
  std::unique_ptr<uint16_t[]> blank_tracker{new uint16_t[SIZE]};
  for (unsigned k = 0; k < SIZE; ++k) {
    blank_tracker[k] = 0;
  }
  std::deque<FringeTaquin<N>> queue{root};
  unsigned counter = 0, int_percent = 0;
  const auto start{std::chrono::steady_clock::now()};

  while (queue.size() > 0) {
    auto ft = queue.back();
    unsigned k = fringe_index(ft);
    assert(k < SIZE);
    if (table[k] == 0)
      table[k] = ft.depth;
    if (!blank_was_seen(blank_tracker[k], ft.blank)) {
      for (auto m : ft.possible_moves()) {
        auto child = ft;
        child.apply(m);
        child.depth = ft.depth + 1;
        queue.push_front(child);
      }
      blank_tracker[k] += (uint16_t)ipow(2, ft.blank);
      assert(blank_was_seen(blank_tracker[k], ft.blank));
      ++counter;
    }
    queue.pop_back();
    if constexpr (verbose) {
      auto percent = ((double)counter / (SIZE * (N - 1) * (N - 1))) * 100.0;
      if (percent > int_percent) {
        const auto end{std::chrono::steady_clock::now()};
        const std::chrono::duration<double> elapsed_seconds{end - start};
        ++int_percent;
        print(int_percent, "%   ", elapsed_seconds.count());
      }
    }
  }
  write_binary("pruning_tables/fringe_" + std::to_string(N) + ".dat",
               table.data(), SIZE);
}