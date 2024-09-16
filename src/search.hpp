#pragma once
#include "taquin.hpp"
#include <algorithm> // std::reverse
#include <deque>
#include <memory>
#include <vector>

template <unsigned N>
struct Node : public std::enable_shared_from_this<Node<N>> {
  using sptr = std::shared_ptr<Node<N>>;

  Taquin<N> state;
  unsigned depth;
  Move last;
  sptr parent;

  Node(const Taquin<N> &t, const unsigned &d = 0, const Move &m = NONE,
       const sptr p = nullptr)
      : state{t}, depth{d}, last{m}, parent{p} {}

  auto expand() {
    std::vector<sptr> ret;
    for (auto move : state.possible_moves(last)) {
      auto child_state = Taquin<N>(state);
      child_state.apply(move);
      ret.emplace_back(
          new Node(child_state, depth + 1, move, this->shared_from_this()));
    }
    return ret;
  }

  Sequence get_path() {
    Sequence ret;
    sptr p = this->shared_from_this();
    while (p->parent != nullptr) {
      ret.push_back(p->last);
      p = p->parent;
    }
    std::reverse(ret.begin(), ret.end());
    return ret;
  }
};

template <unsigned N> typename Node<N>::sptr make_root(const Taquin<N> &t) {
  return typename Node<N>::sptr(new Node(t));
}

template <typename NodePtr> struct Solutions : public std::vector<NodePtr> {
  void sort_by_depth() {
    std::sort(this->begin(), this->end(),
              [](const NodePtr node1, const NodePtr node2) {
                return (node1->depth < node2->depth);
              });
  }

  void show() const {
    for (auto node : *this) {
      std::cout << node->get_path() << std::endl;
    }
  }
};

template <bool verbose = true, typename NodePtr>
Solutions<NodePtr> depth_first_search(const NodePtr root, const auto &estimate,
                                      const unsigned max_depth = 4) {
  Solutions<NodePtr> all_solutions;
  int node_counter = 0;
  std::deque<NodePtr> queue({root});

  while (queue.size() > 0) {
    auto node = queue.back();
    ++node_counter;
    if (node->state.is_solved()) {
      all_solutions.push_back(node);
      queue.pop_back();
    } else {
      queue.pop_back();
      if (node->depth + estimate(node->state) <= max_depth) {
        auto children = node->expand();
        for (auto &&child : children) {
          queue.push_back(child);
        }
      }
    }
    assert(queue.size() < 1000000); // Avoiding memory flood
  }
  if constexpr (verbose) {
    std::cout << "Nodes generated: " << node_counter << std::endl;
  }
  return all_solutions;
}

template <bool verbose = true, typename NodePtr>
Solutions<NodePtr> IDAstar(const NodePtr root, const auto &estimate,
                           const unsigned max_depth = 80) {
  unsigned search_depth = estimate(root->state);

  Solutions<NodePtr> solutions;
  while (solutions.size() == 0 && search_depth <= max_depth) {
    if constexpr (verbose) {
      std::cout << "Searching at depth " << search_depth << std::endl;
    }
    solutions = depth_first_search<verbose>(root, estimate, search_depth);
    ++search_depth;
  }

  if constexpr (verbose) {
    if (solutions.size() == 0) {
      std::cout << "IDA*: No solution found" << std::endl;
    }
  }
  return solutions;
}
