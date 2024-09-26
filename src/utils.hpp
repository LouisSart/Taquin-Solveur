#pragma once
#include <array>
#include <cassert>
#include <filesystem> // locate move table files
#include <fstream>    // write tabes into files
#include <iostream>
#include <unordered_map>
#include <vector>

template <typename T, std::size_t n, typename cast_t = T>
void print_array(const typename std::array<T, n> &a) {
  std::cout << "{";
  for (auto k : a) {
    std::cout << static_cast<cast_t>(k) << ", ";
  }
  if (n > 0)
    std::cout << "\b\b";
  std::cout << "}" << std::endl;
}

template <typename T, typename cast_t = T>
void print_vector(const typename std::vector<T> &v) {
  std::cout << "{";
  for (auto k : v) {
    std::cout << static_cast<cast_t>(k) << ", ";
  }
  if (v.size() > 0)
    std::cout << "\b\b";
  std::cout << "}" << std::endl;
}

template <typename T, typename... Ts>
void print(const T &truc, const Ts &...reste) {
  if constexpr (sizeof...(Ts) == 0) {
    std::cout << truc << std::endl;
  } else {
    std::cout << truc << " ";
    print(reste...);
  }
}

std::vector<std::string> split(std::string str, char splitter) {
  std::vector<std::string> result;
  std::string current = "";
  for (unsigned i = 0; i < str.size(); i++) {
    if (str[i] == splitter) {
      if (current != "") {
        result.push_back(current);
        current = "";
      }
      continue;
    }
    current += str[i];
  }
  if (current.size() != 0)
    result.push_back(current);
  return result;
}

namespace fs = std::filesystem;
template <typename value_type>
void load_binary(const std::filesystem::path &table_path, value_type *ptr,
                 size_t size) {
  assert(fs::exists(table_path));
  std::ifstream istrm(table_path, std::ios::binary);
  istrm.read(reinterpret_cast<char *>(ptr), sizeof(value_type) * size);
  istrm.close();
}

template <typename value_type>
void write_binary(const std::filesystem::path &table_path, value_type *ptr,
                  size_t size) {
  std::ofstream file(table_path, std::ios::binary);
  file.write(reinterpret_cast<char *>(ptr), sizeof(value_type) * size);
  file.close();
}

template <typename key_type, typename value_type, unsigned size>
void write_map_binary(
    const std::filesystem::path &map_path,
    const std::unordered_map<key_type, value_type> &hash_to_index) {

  std::array<key_type, size> linearized;

  for (auto item : hash_to_index) {
    linearized[item.second] = item.first;
  }

  write_binary(map_path, linearized.data(), size);
}

template <typename key_type, typename value_type, unsigned size>
auto load_map_binary(const std::filesystem::path &map_path) {
  assert(fs::exists(map_path));
  std::array<key_type, size> linearized;
  load_binary(map_path, linearized.data(), size);

  std::unordered_map<key_type, value_type> ret;
  for (unsigned k = 0; k < size; ++k) {
    ret[linearized[k]] = k;
  }

  return ret;
}

constexpr int ipow(int k, unsigned n) {
  // integer power
  // computes ret = k^n
  // k can be negative hence using int
  unsigned ret{1};
  for (unsigned i = 0; i < n; i++) {
    ret *= k;
  }
  return ret;
};

static constexpr unsigned N_PRECOMP = 16;

constexpr auto factorial_table = [] {
  std::array<unsigned, N_PRECOMP + 1> arr = {};
  arr[0] = 1;
  for (unsigned n = 1; n <= N_PRECOMP; ++n) {
    arr[n] = n * arr[n - 1];
  }
  return arr;
}();

constexpr unsigned factorial(unsigned n) {
  assert(n <= N_PRECOMP);
  return factorial_table[n];
}

constexpr auto binomial_table = [] {
  // Using constexpr lambda to fill up binomial table
  // at compile time
  std::array<unsigned, (N_PRECOMP + 1) * (N_PRECOMP + 1)> arr = {};
  for (unsigned n = 0; n <= N_PRECOMP; ++n) {
    for (unsigned k = 0; k <= N_PRECOMP; ++k) {
      if (n < k) {
        arr[n * N_PRECOMP + 1 + k] = 0;
      } else if (k == 0 || k == n) {
        arr[n * N_PRECOMP + 1 + k] = 1;
      } else {
        arr[n * N_PRECOMP + 1 + k] = arr[(n - 1) * N_PRECOMP + 1 + k - 1] +
                                     arr[(n - 1) * N_PRECOMP + 1 + k];
      }
    }
  }
  return arr;
}();

constexpr unsigned binomial(unsigned n, unsigned k) {
  // The function just does a lookup in the table for better performance
  assert(n >= 0 && k >= 0); // "No negative values"
  assert(n < N_PRECOMP + 1 &&
         k < N_PRECOMP + 1); // "Binomial numbers computed up to n=16"
  return binomial_table[n * N_PRECOMP + 1 + k];
}

template <std::size_t n>
void permutation_from_index(unsigned c, std::array<unsigned, n> &perm) {
  perm[n - 1] = 0;
  for (unsigned i = n - 1; i > 0; --i) {
    perm[i - 1] = (c % (n - i + 1));
    c = c / (n - i + 1);
    for (auto j = i + 1; j <= n; ++j) {
      if (perm[j - 1] >= perm[i - 1]) {
        perm[j - 1] = perm[j - 1] + 1;
      }
    }
  }
}

template <std::size_t n>
void layout_from_index(unsigned c, std::array<unsigned, n> &layout,
                       unsigned r) {
  // n: number of positions
  // r: number of pieces
  assert(r <= n);
  assert(c < binomial(n, r));
  for (int i = n - 1; i >= 0; --i) {
    if (c >= binomial(i, r)) {
      c = c - binomial(i, r);
      layout[i] = 1;
      r = r - 1;
    } else {
      layout[i] = 0;
    }
  }
}