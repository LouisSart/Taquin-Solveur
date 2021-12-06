import os, numpy as np
from tempfile import mkdtemp
from .taquin import Taquin


def valid_neighbours(size, i,j):
    for h, v in ((0,1), (0,-1), (1,0), (-1,0)):
        if h:
            x = i+h
            if (-1 < x < size): yield x*size+j
        else:
            y = j+v
            if (-1 < y < size): yield i*size+y


class HardQueue:

    def __init__(self, shape, dtype):
        self.shape = shape
        filename = os.path.join(mkdtemp(), "numpy_memmap.dat")
        self.dtype = dtype
        self.mmap = np.memmap(filename, dtype=dtype, mode="w+", shape=self.shape)
        self.pop_chunk = 0
        self.store_chunk = 0
        self.pop_idx = 0
        self.store_idx = 0
        self.left_end = self.mmap[self.pop_chunk].view()
        self.right_end = self.mmap[self.store_chunk].view()

    def is_not_empty(self):
        return not (self.pop_chunk==self.store_chunk and self.pop_idx==self.store_idx)

    def store(self, state):
        self.right_end[self.store_idx] = state
        self.store_idx += 1
        if self.store_idx == len(self.right_end):
            self.store_idx = 0
            self.store_chunk += 1
            self.right_end = self.mmap[self.store_chunk].view()


    def pop(self):
        ret = self.left_end[self.pop_idx]
        self.pop_idx += 1
        if self.pop_idx==len(self.left_end):
            self.pop_idx = 0
            self.pop_chunk += 1
            self.left_end = self.mmap[self.pop_chunk].view()
        return ret
