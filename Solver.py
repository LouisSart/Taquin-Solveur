from Node import Node
from Puzzle import Puzzle

def breadth_first_search(root, max_depth):

    last_layer_nodes = [root]
    for depth in range(max_depth):
        this_layer_nodes = []
        for node in last_layer_nodes:
            children = node.expand()
            for child in children:
                if child.is_goal_state():
                    print(f"{depth+1}-move solution found !")
                    return child, depth+1
                this_layer_nodes.append(child)
        last_layer_nodes = this_layer_nodes
    print(f"No solution found up to depth {max_depth}")
    return None, None

if __name__ == "__main__":
    initial_state = Puzzle()
    initial_state.shuffle(100)
    print(f"Scrambled state : {initial_state}")
    root = Node(initial_state)
    solution, move_count = breadth_first_search(root, 30)
    node = solution
    while node is not None:
        print(node.puzzle)
        node = node.parent
