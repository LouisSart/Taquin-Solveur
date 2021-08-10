
class Node:
    def __init__(self, puzzle, heuristic=None, parent=None, move=None):
        self.puzzle = puzzle
        self.parent = parent
        self.h = heuristic.compute(self.puzzle) if heuristic is not None else 0
        self.depth = parent.depth+1 if parent is not None else 0
        self.move = move

    def expand(self, heuristic):

        previous = self.move
        successors = []
        for move in self.puzzle.allowed_moves(previous):
            new_state = self.puzzle.copy()
            new_state.apply(move)
            child = Node(new_state, parent=self, move=move)
            heuristic.update(child, move)
            successors.append(child)
        return sorted(successors, key=lambda node: node.depth + node.h)

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
