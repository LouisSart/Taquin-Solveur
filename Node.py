
class Node:
    def __init__(self, puzzle, parent=None):
        self.puzzle = puzzle
        self.parent = parent
        self.depth = parent.depth+1 if parent is not None else 0

    def expand(self):

        previous_bt_pos = self.parent.puzzle.bt_pos if self.parent else None
        successors = []
        for pos in self.puzzle.possible_swaps:
            if pos != previous_bt_pos:
                new_state = self.puzzle.copy()
                new_state.swap(pos)
                successors.append(Node(new_state, parent=self))
        return successors

    @property
    def h(self):
        return self.puzzle.heuristic()

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
