#pragma once
#include "taquin.hpp"
#include "utils.hpp"
#include <cstdlib>

template <unsigned N> unsigned manhattan(const Taquin<N> &taquin) {
  unsigned NTILES = Taquin<N>::NTILES;
  unsigned ret = 0;
  int i_is, j_is, i_belongs, j_belongs;

  for (unsigned k = 0; k < NTILES; ++k) {
    auto t = taquin[k];
    if (k != taquin.blank) {
      i_is = k / N;
      j_is = k % N;
      i_belongs = (t - 1) / N;
      j_belongs = (t - 1) % N;
      ret += std::abs(i_is - i_belongs) + std::abs(j_is - j_belongs);
    }
  }
  return ret;
}
