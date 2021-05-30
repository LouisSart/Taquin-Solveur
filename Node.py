from Puzzle import Puzzle


class Node:
    def __init__(self, puzzle, parent=None):
        self.puzzle = puzzle
        self.parent = parent

    def expand(self):

        previous_bt_pos = self.parent.puzzle.bt_pos if self.parent is not None else None
        successors = []
        for pos in self.puzzle.possible_swaps():
            if pos != previous_bt_pos:
                new_state = Puzzle([tile for tile in self.puzzle.tiles], self.puzzle.bt_pos)
                new_state.swap(pos)
                successors.append(Node(new_state, parent=self))

        return successors

    def is_goal_state(self):
        return self.puzzle.tiles == [0,1,2,3,4,5,6,7,8]

if __name__ == "__main__":
    puzzle = Puzzle()
    puzzle.shuffle()
    root = Node(puzzle)
    print(root.puzzle, root.puzzle.possible_swaps())
    successors = root.expand()
    print([succ.puzzle for succ in successors])
    print(root.puzzle, root.puzzle.possible_swaps())
