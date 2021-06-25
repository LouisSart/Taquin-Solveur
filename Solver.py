from Node import Node
import collections
from heuristics import manhattan

def depth_first_search(root, max_depth=30, heuristic=manhattan, verbose=True):

    if not root.puzzle.is_solvable:
        print(f"Position \n{root.puzzle}\n is not solvable")
        return None

    queue = [root]
    solutions = []
    found = False
    root.compute_h(heuristic)
    if verbose: print("Depth first search : Running...")

    while queue:
        node = queue.pop()
        if node.depth + node.h <= max_depth:
            if node.is_goal_state:
                if verbose and not found: print(f"{node.depth}-move solution(s) found !")
                found = True
                solutions.append(node)
                max_depth = node.depth
            else:
                for child in node.expand():
                    child.compute_h(heuristic)
                    queue.append(child)

    return tuple(solutions)

def Astar_search(root, heuristic=manhattan, find_all=False, verbose=True):

        if not root.puzzle.is_solvable:
            print(f"Position \n{root.puzzle}\n is not solvable")
            return None
        root.compute_h(heuristic)
        queue = collections.deque([root])
        if verbose: print("A* search : Running...")
        while queue:
            queue = collections.deque(sorted(list(queue), key=lambda node: node.depth + node.h))
            node = queue.popleft()
            if node.is_goal_state:
                optimal_depth = node.depth
                if verbose: print(f"{optimal_depth}-move solution(s) found !")
                return (node,)

            for child in node.expand():
                child.compute_h(heuristic)
                queue.appendleft(child)


def breadth_first_search(root, max_depth=30, verbose=True):

    if not root.puzzle.is_solvable:
        print(f"Position\n{root.puzzle}\nis not solvable")
        return None
    found = False
    solutions = []
    queue = collections.deque([root])
    node = root
    depth = 0
    if verbose: print("Breadth first search : Running...")
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
        return tuple(solutions)
        if verbose : print(f"Depth {depth:2} completed")
    if verbose : print(f"BFS: No solution found up to depth {max_depth} for position\n{root.puzzle}")
    return None
