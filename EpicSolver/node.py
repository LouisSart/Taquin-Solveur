from .heuristics import NoneHeuristic

class Node:
    def __init__(self, puzzle, heuristic=NoneHeuristic()):
        self.puzzle = puzzle
        self.parent = None
        self.heuristic = heuristic
        self.heuristic.compute(self.puzzle)
        self.depth = 0
        self.move = None

    def expand(self):

        previous = self.move
        successors = []
        for move in self.puzzle.allowed_moves(previous):
            child = Child(self, move)
            successors.append(child)
        return sorted(successors, key=lambda node: node.depth + node.h)

    @property
    def h(self):
        return self.heuristic.estimate

    @property
    def is_goal_state(self):
        if self.heuristic.estimate == 0:
            return self.puzzle.is_solved
        else: return False

    @property
    def path(self):

        path = []
        node = self
        while node is not None:
            path.append(node)
            node = node.parent
        return tuple(reversed(path))

class Child(Node):
    def __init__(self, parent, move):
        self.parent = parent
        self.move = move
        self.puzzle = parent.puzzle.copy()
        self.puzzle.apply(move)
        self.depth = parent.depth+1
        self.heuristic = parent.heuristic.copy()
        self.heuristic.update(self, move)
