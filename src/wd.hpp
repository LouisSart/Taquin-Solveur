#pragma once
#include "taquin.hpp"
#include "utils.hpp"
#include <cstdint>
#include <deque>
#include <map>

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
  unsigned depth;

  WDTaquin() : blank{N - 1}, depth{0} {
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

  std::vector<WDMove> possible_moves() {
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
    ++depth;
  }

  unsigned hash() const {
    unsigned ret = blank, p = N + 1;
    for (unsigned r = 0; r < N - 1; ++r) {
      for (unsigned c = 0; c < N - 1; ++c) {
        ret += p * (*this)[r * N + c];
        p *= N + 1;
      }
    }
    return ret;
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

template <unsigned N> auto vertical_wd(const Taquin<N> &taquin) {
  WDTaquin<N> ret;
  ret.fill(0);
  for (unsigned r = 0; r < N; ++r) {
    for (unsigned c = 0; c < N; ++c) {
      if (taquin.blank != r * N + c) {

        unsigned row_belong = (taquin[r * N + c] - 1) / N;
        ++ret[r * N + row_belong];
      }
    }
  }
  return ret;
}

template <unsigned N> auto horizontal_wd(const Taquin<N> &taquin) {
  WDTaquin<N> ret;
  ret.fill(0);
  for (unsigned c = 0; c < N; ++c) {
    for (unsigned r = 0; r < N; ++r) {
      if (taquin.blank != r * N + c) {
        unsigned col_belong = (taquin[r * N + c] - 1) % N;
        ++ret[c * N + col_belong];
      }
    }
  }
  return ret;
}

constexpr std::size_t TABLE_SIZES[5] = {
    [0] = 1, [1] = 1, [2] = 4, [3] = 105, [4] = 24964};

template <unsigned N> struct WDTable : std::array<uint8_t, TABLE_SIZES[N]> {
  std::map<unsigned, unsigned> hash_to_index;

  WDTable() { this->fill(UINT8_MAX); }

  auto get_estimator() {
    return [this](const Taquin<N> &taquin) {
      auto v_wd = vertical_wd(taquin);
      auto h_wd = horizontal_wd(taquin);

      return (*this)[hash_to_index[v_wd.hash()]] +
             (*this)[hash_to_index[h_wd.hash()]];
    };
  }
};

template <unsigned N> auto generate_table() {
  WDTaquin<N> root;
  std::deque<WDTaquin<N>> queue{root};
  unsigned index = 0;
  WDTable<N> table;

  while (queue.size() > 0) {
    auto wd = queue.back();
    unsigned h = wd.hash();
    if (!table.hash_to_index.contains(h)) {
      for (auto m : wd.possible_moves()) {
        auto child = wd;
        child.apply(m);
        queue.push_front(child);
      }
      table[index] = static_cast<uint8_t>(wd.depth);
      table.hash_to_index[h] = index;
      ++index;
    }
    queue.pop_back();
  }
  return table;
}
