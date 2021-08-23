import collections
from .node import Node

class Solver:

    def __init__(self, max_depth=None, find_all=None, verbose=None):

        if not max_depth is None: self.max_depth = max_depth
        if not find_all is None: self.find_all = find_all
        if not verbose is None: self.verbose = verbose
        self.solutions = []

    def print_solutions(self):

        if not self.solutions:
            print("Solver.print_solutions : No solution found")
        else:
            for sol in self.solutions:
                print(*(node.move for node in sol.path[1:]), f"({sol.depth})")

class BFS(Solver):
    """
    Simple breadth first search algorithm. It is very memory inefficient and
    shouldn't be used for 3x3 puzzles over 27 moves.
    """
    def __init__(self, max_depth=27, find_all=True, verbose=True):
        super().__init__(max_depth=max_depth, find_all=find_all, verbose=verbose)

    def solve(self, puzzle, heuristic=None):

        if not puzzle.is_solvable:
            print(f"Position\n{puzzle}\nis not solvable")
            return None

        root = Node(puzzle)
        found = False
        self.node_counter = 0
        self.solutions = []
        max_depth = self.max_depth
        queue = collections.deque([root])
        node = root
        depth = 0
        if self.verbose: print("Breadth first search : Running...")
        while node.depth <= max_depth:
            if node.depth > depth:
                depth = node.depth
                if self.verbose : print(f"Searching at depth {depth:>5}")
            node = queue.popleft()

            if node.is_goal_state:
                self.solutions.append(node)
                if not self.find_all : return tuple(self.solutions)
                if not found:
                    if self.verbose : print(f"{node.depth}-move solution(s) found !")
                    found, max_depth = True, node.depth
            for child in node.expand() :
                self.node_counter += 1
                queue.append(child)
        if found:
            return tuple(self.solutions)
            if self.verbose : print(f"Depth {depth:2} completed")
        if self.verbose : print(f"BFS: No solution found up to depth {max_depth} for position:\n{root.puzzle}")
        return None

class Astar(Solver):
    """
    janeHJY's "A*" algorithm. It is built like a breadth-first algorithm where the node
    queue is sorted at each iteration, but the memory occupation looks linear,
    just like a depth-first algorithm.
    Anyway the sorting is way too costly for paths over 30 moves and this algorithm
    will not perform as good as a depth first search with the same heuristic
    """
    def __init__(self, verbose=True):
        super().__init__(verbose=verbose)

    def solve(self, puzzle, heuristic):

        if not puzzle.is_solvable:
            print(f"Position \n{puzzle}\n is not solvable")
            return None

        root = Node(puzzle, heuristic)
        self.solutions = []
        self.node_counter = 0
        queue = collections.deque([root])
        if self.verbose: print("A* search : Running...")
        while queue:
            queue = collections.deque(sorted(list(queue), key=lambda node: node.depth + node.h))
            node = queue.popleft()
            if node.is_goal_state:
                if self.verbose: print(f"{node.depth}-move solution(s) found !")
                self.solutions.append(node)
                return tuple(self.solutions)

            for child in node.expand():
                self.node_counter += 1
                queue.appendleft(child)

class DFS(Solver):
    """
    A depth first search algorithm with a heuristic. It updates its max_depth parameter
    every time it finds a shorter solution until it finds every optimal.
    """
    def __init__(self, max_depth=30, find_all=True, verbose=True):
        super().__init__(max_depth=max_depth, find_all=find_all, verbose=verbose)

    def solve(self, puzzle, heuristic):

        if not puzzle.is_solvable:
            print(f"Position \n{puzzle}\n is not solvable")
            return None

        root = Node(puzzle, heuristic)
        queue = [root]
        self.solutions = []
        found = False
        self.node_counter=0
        estimate = float('inf')
        max_depth = self.max_depth
        if self.verbose: print("Depth first search : Running...")

        while queue:
            node = queue.pop()
            if node.depth + node.h <= max_depth:
                if node.is_goal_state:
                    if self.verbose and not found: print(f"{node.depth}-move solution(s) found !")
                    found = True
                    self.solutions.append(node)
                    if not self.find_all:
                        return tuple(self.solutions)
                    max_depth = node.depth
                else:
                    for child in node.expand():
                        queue.append(child)
                        self.node_counter+=1
            else:
                estimate = min(estimate, node.depth + node.h)

        return tuple(self.solutions) or estimate

class Recursive_DFS(Solver):
    """
    A recursive implementation of a depth first algorithm. I haven't figured out
    how to make it find every optimal solution, but it can still serve as an inner
    DFS algorithm for iterative deepening A*
    Shows to be around 20% slower than the standard DFS, which makes it pretty useless
    """
    def __init__(self, max_depth=30, verbose=True):
        super().__init__(max_depth=max_depth, verbose=verbose)

    def solve(self, puzzle, heuristic):

        def recursive_search(queue, max_depth):
            node = queue[-1]
            if node.depth + node.h > max_depth:
                return node.depth + node.h
            if node.is_goal_state:
                return (node,)
            estimate = float('inf')
            for child in node.expand():
                self.node_counter += 1
                queue.append(child)
                res = recursive_search(queue, max_depth)
                if isinstance(res, tuple): return res
                estimate = min(estimate, res)
                queue.pop()
            return estimate

        root = Node(puzzle)
        self.node_counter = 0
        queue = [root]
        self.solutions = []
        if self.verbose : print("Recursive_DFS : Running...")
        res = recursive_search(queue, self.max_depth)
        if isinstance(res, tuple):
            if self.verbose : print("Solution found !")
            self.solutions = res
        return res

class IDAstar(Solver):
    """
    Korf's iterative deepening A* search algorithm. The inner DFS is set
    to the standard one by default, but it can be changed by setting the df_solver attribute
    """
    def __init__(self, find_all=True, verbose=True):
        super().__init__(find_all=find_all, verbose=verbose)
        self.df_solver = DFS(None, find_all, False)

    def solve(self, puzzle, heuristic):

        if not puzzle.is_solvable:
            print(f"Position \n{puzzle}\n is not solvable")
            return None

        root = Node(puzzle, heuristic)
        self.df_solver.max_depth = root.h
        self.node_counter = 0
        if self.verbose: print(f"IDA* : Starting search at depth {self.df_solver.max_depth}")
        found = root.is_goal_state
        while not found:
            attempt = self.df_solver.solve(puzzle, heuristic)
            self.node_counter += self.df_solver.node_counter
            if self.verbose: print(f"Depth {self.df_solver.max_depth:2} completed, nodes: {self.df_solver.node_counter:>8}")
            if isinstance(attempt, tuple):
                found = True
                self.solutions = attempt
                return attempt
            self.df_solver.max_depth = attempt
        return tuple([root])
