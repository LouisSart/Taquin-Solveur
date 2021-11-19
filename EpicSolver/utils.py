import math, collections
from .taquin import Taquin

factorial = math.factorial
binomial = lambda n,k: math.comb(n,k) if n>=k else 0

def permutation_coordinate(perm):
    # Computes the coordinate of a permutation
    # Works if the sorted position has increasing values
    icount = []
    for i, k in enumerate(perm):
        count = 0
        for l in perm[:i]:
            if l>k: count+=1
        icount.append(count)
    return sum(k*factorial(i) for i, k in enumerate(icount))

def layout_coordinate(layout):
    # Param layout : an iterable of zeros (non pattern tiles) and ones (pattern tiles)
    # Computes the coordinate of the input pattern layout
    # For each tile i that belongs to the pattern, count the number x of
    # pattern tiles that come before it. Then this tile
    # contributes c_nk(i, x+1) to the coordinate.
    # The sum of the contributions is the layout coordinate
    # This works if the solved state has all pattern tiles stored at the beginning (coord=0),
    # which is why we need the self.order attribute
    c = 0
    x = 0
    for i, k in enumerate(layout):
        if k == 1:
            c += binomial(i, x+1)
            x += 1
    return c

def valid_neighbours(size, i,j):
    for h, v in ((0,1), (0,-1), (1,0), (-1,0)):
        if h:
            x = i+h
            if (-1 < x < size): yield x*size+j
        else:
            y = j+v
            if (-1 < y < size): yield i*size+y


class HardQueue(collections.deque):
    filenames_queue = collections.deque([])
    queue_trail = collections.deque([])
    n_files = 0

    def is_not_empty(self):
        return self.__bool__() or self.queue_trail.__bool__() or self.filenames_queue.__bool__()

    def store(self, node):
        self.queue_trail.append(node)

        if len(self.queue_trail) > 1000000:
            filename = f"chunk_{self.n_files}.pkl"
            with open(filename, "wb") as f:
                print("Dumping queue trail...")
                pickle.dump(self.queue_trail, f)
                self.queue_trail.clear()
                self.n_files += 1
                self.filenames_queue.append(filename)

    def pop(self):
        if not self:
            if self.filenames_queue:
                next_file = self.filenames_queue.popleft()
                with open(next_file, "rb") as f:
                    print("Loading chunk...")
                    self.extend(pickle.load(f))
                    os.remove(next_file)
            elif self.queue_trail:
                self.extend(self.queue_trail)
                self.queue_trail.clear()
            else:
                raise IndexError
        return self.popleft()
