#pragma once
#include "utils.hpp"
#include <array>
#include <cassert>
#include <iomanip>
#include <iostream>
#include <string>
#include <vector>

enum Move : unsigned { U, D, L, R, NONE };

std::ostream &operator<<(std::ostream &os, const Move &move) {
  static std::string move_to_str[5] = {
      [U] = "U", [D] = "D", [L] = "L", [R] = "R", [NONE] = "X"};
  os << move_to_str[move];
  return os;
}

using Sequence = std::vector<Move>;

std::ostream &operator<<(std::ostream &os, const Sequence &seq) {
  for (auto move : seq)
    os << move << " ";
  os << "\b";
  os << " (" << seq.size() << ")";
  return os;
}

template <unsigned N> struct Taquin : std::array<unsigned, N * N> {
  static constexpr unsigned N_TILES = N * N;
  unsigned blank;

  Taquin() : blank{N_TILES - 1} {
    for (unsigned k = 0; k < N_TILES - 1; ++k)
      (*this)[k] = k + 1;
    (*this)[blank] = 0;
  }

  Taquin(const std::array<unsigned, N * N> &arr_in)
      : std::array<unsigned, N * N>{arr_in} {
    blank = 0;
    auto it = this->begin();
    while (*it != 0) {
      ++blank;
      ++it;
    }
  }
  Taquin(const std::string s) {
    auto str_list = split(s, ' ');
    assert(str_list.size() == N * N); // Wrong number of input values
    for (unsigned k = 0; k < N * N; ++k) {
      auto v = (unsigned)stoi(str_list[k]);
      assert(v < N * N);
      (*this)[k] = v;
    }

    blank = 0;
    auto it = this->begin();
    while (*it != 0) {
      ++blank;
      ++it;
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
    // A move consists of a sliding a tile to the blank spot.
    // A U move (resp D, L, R) takes the upper (resp down, left, right)
    // tile and slides it to the empty spot. Not every move is possible
    // depending on if the blank is adjacent to one of the board sides

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

  bool is_solved() const {
    if (blank != N_TILES - 1)
      return false;
    for (unsigned k = 0; k < N_TILES - 1; ++k) {
      if ((*this)[k] != k + 1)
        return false;
    }
    return true;
  }

  void show() const {
    for (unsigned r = 0; r < N; ++r) {
      std::cout << "[";
      for (unsigned c = 0; c < N; ++c) {
        if (r * N + c == blank)
          std::cout << std::setw(2) << " "
                    << " ";
        else
          std::cout << std::setw(2) << (*this)[r * N + c] << " ";
      }
      std::cout << "\b]" << std::endl;
    }
  };

  auto get_transposed() const {
    Taquin<N> ret;
    for (unsigned i = 0; i < N; ++i) {
      for (unsigned j = 0; j < N; ++j) {
        ret[i * N + j] = (*this)[j * N + i];
      }
    }
    unsigned bi = blank / N, bj = blank % N;
    ret.blank = bj * N + bi;

    assert(ret[ret.blank] == 0);

    return ret;
  }

  void scramble() {
    srand(time(NULL));
    unsigned nmoves = 1000 + rand() % 100;
    for (unsigned k = 0; k < nmoves; ++k) {
      auto moves = possible_moves();
      unsigned i = rand() % moves.size();
      apply(moves[i]);
    }
  }
};

template <unsigned N>
bool operator==(const Taquin<N> &t1, const Taquin<N> &t2) {
  for (unsigned k = 0; k < Taquin<N>::N_TILES; ++k) {
    if (t1[k] != t2[k])
      return false;
  }
  if (t1.blank != t2.blank)
    return false;
  return true;
}

template <unsigned N> auto compose(const Taquin<N> &t1, const Taquin<N> &t2) {
  Taquin<N> ret;

  auto ind = [](const unsigned &tile) {
    if (tile == 0) {
      return N * N - 1;
    }
    return tile - 1;
  };

  for (unsigned k = 0; k < N * N; ++k) {
    ret[k] = t1[ind(t2[k])];
    if (ret[k] == 0) {
      ret.blank = k;
    }
  }
  return ret;
}

template <unsigned N> auto transpose_conjugate(const Taquin<N> &taquin) {
  auto transpose = Taquin<N>().get_transposed();
  return compose(compose(transpose, taquin), transpose);
}

template <unsigned N> bool is_solved(const Taquin<N> &t) {
  return t.is_solved();
};
