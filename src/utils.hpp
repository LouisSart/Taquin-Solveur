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