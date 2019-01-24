from collections import Counter

cdef extern from "my_rand.c":
    float ran2(long *idum)

'''
Long period (> 2 × 10^18 ) random number generator of L’Ecuyer with Bays-Durham shuffle
and added safeguards. Returns a uniform random deviate between 0.0 and 1.0 (exclusive of
the endpoint values). Call with idum a negative integer to initialize; thereafter, do not alter
idum between successive deviates in a sequence. RNMX should approximate the largest floating
value that is less than 1.
'''

cdef long seed = -1

def setSeed(long s):
    global seed
    if s > 0:
        s = s*-1
    seed = s

def rand():
    global seed
    return ran2(&seed)

neighboring_cells = [
    (-1, 1), (0, 1), (1, 1), 
    (-1, 0),         (1, 0), 
    (-1,-1), (0,-1), (1,-1)
]

def offset(delta):
    "Slide/offset all the cells by delta, a (dx, dy) vector."
    (dx, dy) = delta
    return {(x+dx, y+dy) for (x, y) in neighboring_cells}

def transition(float rand, float prob, alive, unsigned int num_neigh):
    '''
        alive: it states if the cell is alive or not
        int num_neigh: number of neighbors
    '''
    if rand < prob:
        if (alive and num_neigh == 2) or num_neigh == 3:
            alive = True
        else:
            alive = False
    return alive

def __run__(current_world, prob, unsigned int steps):
    # main loop
    for s in range(steps):
        counts = Counter(n for cell in current_world for n in offset(cell))
        new_world = set()
        for cell in counts:
            if transition(rand(), prob, cell in current_world, counts[cell]):
                new_world.add(cell)
        current_world = new_world
    return current_world