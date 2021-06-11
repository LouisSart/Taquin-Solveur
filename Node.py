from Puzzle import Puzzle

class Node:
    def __init__(self, puzzle, parent=None):
        self.puzzle = puzzle
        self.parent = parent

    def expand(self):

        previous_bt_pos = self.parent.puzzle.bt_pos if self.parent else None
        successors = []
        for pos in self.puzzle.possible_swaps():
            if pos != previous_bt_pos:
                new_state = Puzzle(self.puzzle.tiles.copy(), self.puzzle.bt_pos)
                new_state.swap(pos)
                successors.append(Node(new_state, parent=self))
        return successors

    @property
    def is_goal_state(self):
        return self.puzzle.is_solved

    def path(self):

        path = []
        node = self
        while node is not None:
            path.append(node)
            node = node.parent
        yield from reversed(path)
