class StateNode:
    def __init__(self, state):
        self.state = state
        self.parent = None
        self.depth = 0
        self.move = None
        self.h = state.estimate

    def expand(self):

        previous = self.move
        successors = []
        for move in self.state.valid_moves(previous):
            child = StateChild(self, move)
            successors.append(child)
        return sorted(successors, key=lambda node: node.depth + node.h)

    @property
    def is_goal_state(self):
        if self.state.estimate == 0:
            return self.state.is_solved
        else: return False

    @property
    def path(self):

        path = []
        node = self
        while node is not None:
            path.append(node)
            node = node.parent
        return tuple(reversed(path))

class StateChild(Node):
    def __init__(self, parent, move):
        self.parent = parent
        self.move = move
        self.depth = parent.depth+1
        self.state = parent.state.copy()
        self.state.update(move)
        self.h = self.state.estimate
