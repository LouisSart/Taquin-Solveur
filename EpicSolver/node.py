
class Node:
    def __init__(self, puzzle, parent=None):
        self.puzzle = puzzle
        self.parent = parent
        self.depth = parent.depth+1 if parent is not None else 0
        self.h = None

    def expand(self, heuristic):

        previous_bt_pos = self.parent.puzzle.bt_pos if self.parent else None
        successors = []
        for pos in self.puzzle.possible_swaps:
            if pos != previous_bt_pos:
                new_state = self.puzzle.copy()
                new_state.swap(pos)
                child = Node(new_state, parent=self)
                child.compute_h(heuristic)
                successors.append(child)
        return sorted(successors, key=lambda node: node.depth + node.h)

    def compute_h(self, heuristic):
        self.h = heuristic(self.puzzle)

    @property
    def is_goal_state(self):
        return self.puzzle.is_solved

    @property
    def path(self):

        path = []
        node = self
        while node is not None:
            path.append(node)
            node = node.parent
        yield from reversed(path)
