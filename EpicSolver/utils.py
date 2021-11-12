import math, collections
from .taquin import Taquin

factorial = math.factorial
binomial = lambda n,k: math.comb(n,k) if n>=k else 0

def perm_coord(perm):
    # Computes the coordinate of a permutation
    # Works if the sorted position has increasing values
    icount = []
    for i, k in enumerate(perm):
        count = 0
        for l in perm[:i]:
            if l>k: count+=1
        icount.append(count)
    return sum(k*factorial(i) for i, k in enumerate(icount))

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
