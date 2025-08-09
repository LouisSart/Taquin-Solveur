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
  static constexpr std::array<unsigned, N_FRINGE_TILES> order = [] {
    std::array<unsigned, N_FRINGE_TILES> ret;
    for (unsigned k = 0; k < N; ++k) {
      ret[k] = k + 1;
    }
    for (unsigned k = N; k < N_FRINGE_TILES; ++k) {
      ret[k] = (k - N + 1) * N + 1;
    }
    return ret;
  }();

  static bool is_fringe_tile(const unsigned &tile) {
    if (tile >= N_TILES)
      return false;
    else
      return mask[tile];
  }
};

template <unsigned N> unsigned permutation_index(const Taquin<N> &ft) {
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

template <unsigned N>
void swap(Taquin<N> &taquin, const unsigned &pos, const unsigned &target) {
  unsigned buf = taquin[target];
  taquin[target] = taquin[pos];
  taquin[pos] = buf;
}

template <unsigned N> std::vector<unsigned> neighbours(const unsigned &pos) {
  std::vector<unsigned> ret;

  if (pos / N != 0)
    ret.push_back(pos - N);
  if (pos / N != N - 1)
    ret.push_back(pos + N);
  if (pos % N != 0)
    ret.push_back(pos - 1);
  if (pos % N != N - 1)
    ret.push_back(pos + 1);

  return ret;
}

template <unsigned N> unsigned layout_index(const Taquin<N> &ft) {
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

template <unsigned N> unsigned fringe_index(const Taquin<N> &ft) {
  return layout_index(ft) * Fringe<N>::N_PERM + permutation_index(ft);
}

// bool blank_was_seen(const uint16_t &h, const unsigned &blank) {
//   return (h / ipow(2, blank)) % 2;
// }

template <unsigned N, bool verbose = false>
auto generate_fringe_table(std::array<uint8_t, Fringe<N>::TABLE_SIZE> &table) {
  assert(table.size() == Fringe<N>::TABLE_SIZE);

  unsigned counter = 1, int_percent = 0;
  const auto start{std::chrono::steady_clock::now()};

  Taquin<N> root;
  table.fill(UINT8_MAX);
  table[fringe_index(root)] = 0;
  std::deque<Taquin<N>> queue{root};

  while (queue.size() > 0) {
    auto taquin = queue.back();
    unsigned index = fringe_index(taquin);
    unsigned depth = table[index];

    // Loop over fringe tile locations
    for (unsigned pos = 0; pos < Taquin<N>::NTILES; ++pos) {
      if (Fringe<N>::is_fringe_tile(taquin[pos])) {
        // Loop over "legal" targets for that fringe tile
        for (unsigned target : neighbours<N>(pos)) {
          if (!Fringe<N>::is_fringe_tile(taquin[target])) {
            // Generate a child by swapping the fringe tile at pos with its
            // neighbour at target
            Taquin<N> child = taquin;
            swap(child, pos, target);
            unsigned c_index = fringe_index(child);

            // If this child is a newly encountered state, store its depth
            // and put it in front of the queue
            if (table[c_index] == UINT8_MAX) {
              table[c_index] = depth + 1;
              queue.push_front(child);
              ++counter;
            }
          }
        }
      }
    }

    queue.pop_back();

    if constexpr (verbose) {
      auto percent = ((double)counter / Fringe<N>::TABLE_SIZE) * 100.0;
      if (percent > int_percent) {
        const auto end{std::chrono::steady_clock::now()};
        const std::chrono::duration<double> elapsed_seconds{end - start};
        ++int_percent;
        print(depth, int_percent, "%   ", elapsed_seconds.count());
      }
    }
  }

  write_binary("pruning_tables/fringe_" + std::to_string(N) + ".dat",
               table.data(), Fringe<N>::TABLE_SIZE);
}

// template <unsigned N> auto taquin_from_fringe_index(const unsigned &index) {
//   assert(index < Fringe<N>::TABLE_SIZE);
//   unsigned layout_index = index / Fringe<N>::N_PERM;
//   unsigned perm_index = index % Fringe<N>::N_PERM;

//   std::array<unsigned, Fringe<N>::N_TILES> layout;
//   std::array<unsigned, Fringe<N>::N_FRINGE_TILES> permutation;

//   layout_from_index(layout_index, layout, Fringe<N>::N_FRINGE_TILES);
//   permutation_from_index(perm_index, permutation);

//   FringeTaquin<N> ret;
//   ret.fill(Fringe<N>::N_TILES);
//   unsigned tile = 0;
//   for (unsigned k = 0; k < N * N; ++k) {
//     if (layout[k] == 1) {
//       ret[k] = Fringe<N>::order[permutation[tile]];
//       ++tile;
//     } else
//       ret.blank = k;
//   }
//   return ret;
// }

// template <unsigned N>
// void generate_fringe_table_backwards(
//     std::array<uint8_t, Fringe<N>::TABLE_SIZE> &table) {
//   assert(table.size() == Fringe<N>::TABLE_SIZE);
//   table.fill(UINT8_MAX);
//   table[fringe_index(FringeTaquin<N>())] = 0;
//   unsigned encountered = 1, depth = 1;

//   while (encountered < Fringe<N>::TABLE_SIZE) {
//     for (unsigned k = 0; k < Fringe<N>::TABLE_SIZE; ++k) {
//       if (table[k] == depth - 1) {
//         auto ft = taquin_from_fringe_index<N>(k);
//         for (unsigned b = 0; b < Fringe<N>::N_TILES; ++b) {
//           if (!Fringe<N>::is_fringe_tile(ft[b])) {
//             ft.blank = b;
//             for (auto move : ft.possible_moves()) {
//               auto child = ft;
//               child.apply(move);
//               auto kc = fringe_index(child);
//               if (table[kc] == UINT8_MAX) {
//                 table[kc] = depth + 1;
//                 ++encountered;
//                 break;
//               }
//             }
//           }
//         }
//       }
//     }
//     print(depth, encountered);
//     ++depth;
//     write_binary("pruning_tables/fringe_" + std::to_string(N) + ".dat",
//                  table.data(), SIZE);
//   }
// }