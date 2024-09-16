#pragma once
#include <array>
#include <cassert>
#include <iomanip>
#include <iostream>
#include <string>
#include <vector>

enum Move : unsigned { U, D, L, R };

std::ostream &operator<<(std::ostream &os, const Move &move) {
  static std::string move_to_str[4] = {
      [U] = "U", [D] = "D", [L] = "L", [R] = "R"};
  os << move_to_str[move];
  return os;
}

using Sequence = std::vector<Move>;

std::ostream &operator<<(std::ostream &os, const Sequence &seq) {
  for (auto move : seq)
    os << move << " ";
  os << "\b";
  return os;
}

template <unsigned N> struct Taquin : std::array<unsigned, N * N> {
  static constexpr unsigned NTILES = N * N;
  unsigned blank;

  Taquin() : blank{NTILES - 1} {
    for (unsigned k = 0; k < NTILES - 1; ++k)
      (*this)[k] = k + 1;
    (*this)[blank] = 0;
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
    if (blank != NTILES - 1)
      return false;
    for (unsigned k = 0; k < NTILES - 1; ++k) {
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
          std::cout << std::setw(2) << "x"
                    << " ";
        else
          std::cout << std::setw(2) << (*this)[r * N + c] << " ";
      }
      std::cout << "\b]" << std::endl;
    }
  };
};