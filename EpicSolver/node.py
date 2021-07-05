
class Node:
    def __init__(self, puzzle, parent=None, move=None):
        self.puzzle = puzzle
        self.parent = parent
        self.h = None
        self.depth = parent.depth+1 if parent is not None else 0
        self.move = move

    def expand(self, heuristic):

        previous = self.move
        successors = []
        for move in self.puzzle.allowed_moves(previous):
            new_state = self.puzzle.copy()
            new_state.apply(move)
            child = Node(new_state, parent=self, move=move)
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
        return tuple(reversed(path))
