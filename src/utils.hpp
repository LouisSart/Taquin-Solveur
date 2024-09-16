#pragma once

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