#pragma once
#include <array>
#include <iostream>
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