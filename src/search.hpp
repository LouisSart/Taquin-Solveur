#pragma once
#include "taquin.hpp"
#include <memory>
#include <vector>

template <unsigned N>
struct Node : public std::enable_shared_from_this<Node<N>> {
  using sptr = std::shared_ptr<Node<N>>;

  Taquin<N> taquin;
  unsigned depth;
  Move last;
  sptr parent;

  Node(const Taquin<N> &t, const unsigned &d = 0, const Move &m = U,
       const sptr p = nullptr)
      : taquin{t}, depth{d}, last{m}, parent{p} {}

  auto expand() {
    std::vector<sptr> ret;
    for (auto move : taquin.possible_moves(last)) {
      auto child_taquin = Taquin<N>(taquin);
      child_taquin.apply(move);
      ret.emplace_back(
          new Node(child_taquin, depth + 1, move, this->shared_from_this()));
    }
    return ret;
  }
};

template <unsigned N> typename Node<N>::sptr make_root(const Taquin<N> &t) {
  return typename Node<N>::sptr(new Node(t));
}