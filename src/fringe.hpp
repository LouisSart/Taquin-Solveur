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

template <unsigned N> struct FringeTaquin : std::array<unsigned, N * N> {
  unsigned blank, depth;

  FringeTaquin() : blank{N * N - 1}, depth{0} {
    this->fill(0);
    for (unsigned k = 0; k < N; ++k) {
      (*this)[k] = k + 1;
      (*this)[N * k] = N * k + 1;
    }
  }

  bool is_possible_move(const Move &move) const {
    if (move == U) {
      return (blank / N) != 0;
    } else if (move == D) {
      return (blank / N) != N - 1;
    } else if (move == L) {
      return (blank % N) != 0;
    } else if (move == R) {
      return (blank % N) != N - 1;
    } else if (move == NONE) {
      return false;
    }
    assert(false); // We shouldn't end up here
  }

  auto possible_moves(const unsigned &last_move = 4) const {
    std::vector<Move> ret;
    if (is_possible_move(U) && last_move != D)
      ret.push_back(U);
    if (is_possible_move(D) && last_move != U)
      ret.push_back(D);
    if (is_possible_move(L) && last_move != R)
      ret.push_back(L);
    if (is_possible_move(R) && last_move != L)
      ret.push_back(R);
    return ret;
  }

  void apply(const Move &move) {
    assert(is_possible_move(move));

    static int slide[4] = {
        [U] = -(int)N, [D] = (int)N, [L] = -(int)1, [R] = (int)1};

    unsigned new_blank = blank + slide[move];
    (*this)[blank] = (*this)[new_blank];
    (*this)[new_blank] = 0;
    blank = new_blank;
  }

  void apply(const Sequence &seq) {
    for (Move move : seq) {
      apply(move);
    }
  }

  void show() const {
    for (unsigned r = 0; r < N; ++r) {
      std::cout << "[";
      for (unsigned c = 0; c < N; ++c) {
        if (r * N + c == blank)
          std::cout << std::setw(2) << "x"
                    << " ";
        else if ((*this)[r * N + c] > 0) {

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
    if (ft[i - 1] > 0) {
      c *= (n - ki + 1);
      ++ki;
      for (unsigned j = i + 1; j <= N * N; ++j) {
        if ((ft[j - 1] > 0) && (ft[i - 1] > ft[j - 1])) {
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
  unsigned r = 2 * N - 1;
  unsigned t = 0;
  for (unsigned i = N * N - 1; i > 0; --i) {
    if (ft[i] > 0) {
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

template <unsigned N> auto generate_fringe_table() {
  constexpr unsigned N_LAYOUT = binomial(N * N, 2 * N - 1);
  constexpr unsigned N_PERM = factorial(2 * N - 1);
  constexpr unsigned TABLE_SIZE = N_LAYOUT * N_PERM;

  FringeTaquin<N> root;
  std::array<uint16_t, TABLE_SIZE> blank_tracker;
  blank_tracker.fill(0);
  std::deque<FringeTaquin<N>> queue{root};
  unsigned counter = 0;

  while (queue.size() > 0) {
    auto ft = queue.back();
    unsigned k = fringe_index(ft);
    assert(k < TABLE_SIZE);
    if (!blank_was_seen(blank_tracker[k], ft.blank)) {
      for (auto m : ft.possible_moves()) {
        auto child = ft;
        child.apply(m);
        queue.push_front(child);
      }
      blank_tracker[k] += (uint16_t)ipow(2, ft.blank);
      assert(blank_was_seen(blank_tracker[k], ft.blank));
      ++counter;
    }
    queue.pop_back();
  }

  // return blank_tracker;
}