from Node import Node

def breadth_first_search(root, max_depth):

    # This routine was unable to solve this position :
    #[[7 1 5]
    #[2 8 6]
    #[4 0 3]]

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
