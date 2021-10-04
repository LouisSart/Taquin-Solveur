import math

factorial = math.factorial
binomial = lambda n,k: math.comb(n,k) if n>=k else 0

def perm_coord(perm):
    # Computes the coordinate of a permutation
    # Works if the sorted postition has increasing values
    icount = []
    for i, k in enumerate(perm):
        count = 0
        for l in perm[:i]:
            if l>k: count+=1
        icount.append(count)
    return sum(k*factorial(i) for i, k in enumerate(icount))
