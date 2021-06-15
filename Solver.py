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
                return node, node.depth

            for child in node.expand():
                queue.appendleft(child)


def breadth_first_search(root, max_depth=30, verbose=True):

    if not root.puzzle.is_solvable:
        if verbose : print(f"Position\n{root.puzzle}\nis not solvable")
        return None, None
    found = False
    solutions = []
    queue = collections.deque([root])
    node = root
    depth = 0
    while node.depth <= max_depth:
        if node.depth > depth:
            depth = node.depth
            if verbose : print(f"Searching at depth {depth:>5}")
        node = queue.popleft()

        if node.is_goal_state:
            solutions.append(node)
            if not found:
                if verbose : print(f"{node.depth}-move solution(s) found !")
                found, max_depth = True, node.depth
        for child in node.expand() : queue.append(child)
    if found:
        return solutions, depth
        if verbose : print(f"Depth {depth:2} completed")
    if verbose : print(f"BFS: No solution found up to depth {max_depth} for position\n{root.puzzle}")
    return None, None
