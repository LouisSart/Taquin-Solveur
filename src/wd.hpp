#pragma once
#include "taquin.hpp"
#include "utils.hpp"

struct WDMove {
  Move m;
  unsigned col;
};

std::ostream &operator<<(std::ostream &os, const WDMove &wd_move) {
  os << "(" << wd_move.m << ", " << wd_move.col << ")";
  return os;
}

template <unsigned N> constexpr auto make_move_array() {
  std::array<WDMove, 2 * N> ret;
  for (Move m : {U, D}) {
    for (unsigned col = 0; col < N; ++col) {
      ret[col * 2 + m] = WDMove{m, col};
    }
  }
  return ret;
}

template <unsigned N> struct WDTaquin : std::array<unsigned, N * N> {
  static constexpr unsigned NTILES = N * N;
  static constexpr std::array<WDMove, 2 *N> wd_moves = make_move_array<N>();
  static constexpr WDMove WDNONE{NONE, N};

  unsigned blank;

  WDTaquin() : blank{N - 1} {
    this->fill(0);
    for (unsigned k = 0; k < N; ++k) {
      (*this)[k * N + k] = N;
    }
    this->back() -= 1;
  }

  bool is_possible_move(const WDMove &move) const {
    if (move.m == U) {
      return (blank > 0) && (*this)[(blank - 1) * N + move.col] > 0;
    } else if (move.m == D) {
      return (blank < N - 1) && (*this)[(blank + 1) * N + move.col] > 0;
    }
    assert(false);
  }

  std::vector<WDMove> possible_moves(const WDMove &last = WDNONE) {
    std::vector<WDMove> ret;
    for (WDMove m : wd_moves) {
      if (is_possible_move(m)) {
        ret.push_back(m);
      }
    }
    return ret;
  }

  void apply(const WDMove &move) {
    assert(is_possible_move(move));
    if (move.m == U) {
      (*this)[(blank - 1) * N + move.col] -= 1;
      (*this)[blank * N + move.col] += 1;
      blank -= 1;
    } else if (move.m == D) {
      (*this)[(blank + 1) * N + move.col] -= 1;
      (*this)[blank * N + move.col] += 1;
      blank += 1;
    }
  }

  void show() const {
    for (unsigned r = 0; r < N; ++r) {
      std::cout << "[";
      for (unsigned c = 0; c < N; ++c) {
        std::cout << std::setw(2) << (*this)[r * N + c] << " ";
      }
      std::cout << "\b] ";
      if (r == blank) {
        std::cout << "<-";
      }
      std::cout << std::endl;
    };
  }
};