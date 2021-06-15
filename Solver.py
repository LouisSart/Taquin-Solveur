from Node import Node
import collections

def Astar_search(root, h):

        if not root.puzzle.is_solvable:
            print(f"Position \n{root.puzzle}\n is not solvable")
            return
        queue = collections.deque([root])
        while queue:
            queue = collections.deque(sorted(list(queue), key=lambda node: node.depth + h(node.puzzle)))
            node = queue.popleft()
            if node.is_goal_state:
                return node.path

            for child in node.expand():
                queue.appendleft(child)


def breadth_first_search(root, max_depth):

    if not root.puzzle.is_solvable:
        print(f"Position \n{root.puzzle}\n is not solvable")
        return
    solution_found = False
    solutions = []
    last_layer_nodes = [root]
    node_counter = []
    for depth in range(max_depth):
        this_layer_nodes = []
        this_layer_node_counter = 0
        for node in last_layer_nodes:
            children = node.expand()
            for child in children:
                if child.is_goal_state:
                    solutions.append(child)
                    if not solution_found:
                        print(f"{depth+1}-move solution(s) found !")
                        solution_found = True
                this_layer_nodes.append(child)
                this_layer_node_counter += 1
        last_layer_nodes = this_layer_nodes
        node_counter.append(this_layer_node_counter)
        if solution_found:
            return solutions, depth+1
        print(f"Depth {depth+1:2} completed : {this_layer_node_counter:8} nodes")
    print(f"No solution found up to depth {max_depth}")
    return None, None
