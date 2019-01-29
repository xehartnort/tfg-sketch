from collections import Counter
from re import sub

cdef extern from "my_rand.c":
    float ran2 (long *idum)

'''
Long period (> 2 × 10^18 ) random number generator of L’Ecuyer with Bays-Durham shuffle
and added safeguards. Returns a uniform random deviate between 0.0 and 1.0 (exclusive of
the endpoint values). Call with idum a negative integer to initialize; thereafter, do not alter
idum between successive deviates in a sequence. RNMX should approximate the largest floating
value that is less than 1.
'''

cdef long seed = -1

def setSeed (long s) -> None:
    global seed
    if s > 0:
        s = s*-1
    seed = s

def rand () -> float:
    global seed
    return ran2(&seed)

neighboring_cells = [
    (-1, 1), (0, 1), (1, 1), 
    (-1, 0),         (1, 0), 
    (-1,-1), (0,-1), (1,-1)
]

def offset (delta) -> set:
    "Slide/offset all the cells by delta, a (dx, dy) vector."
    (dx, dy) = delta
    return {(x+dx, y+dy) for (x, y) in neighboring_cells}

def computeClusters (current_world) -> set:
    '''
        Compute clusters in current_world and return them in a list in rle format
    '''
    cluster_list = []
    world = current_world.copy ()
    while world: # empty set is the boolean false    
        cluster = set ()
        cell = world.pop ()
        cluster.add (cell)
        neighborhood = world & offset (cell)
        while neighborhood: # empty set is the boolean false
            cell = neighborhood.pop ()
            world.remove (cell)
            cluster.add (cell)
            neighborhood |= world & offset (cell)
        cluster_list.append (cluster)
    return cluster_list

def rleEncode (rawStr) -> str:
    return sub (r'([bo])\1*', lambda m: str (len (m.group(0)))+m.group(1) if len (m.group(0))>1 else m.group(1), rawStr)

def genRleString (world) -> str:
    '''
        Display the world as rle string of b and o characters.
    '''
    Xs, Ys = zip(*world)
    Xrange = range (min (Xs), max (Xs)+1)
    rawStr = []
    for y in range (min (Ys), max (Ys)+1):
        rawStr.append (''.join('o' if (x, y) in world else 'b' for x in Xrange))
    return rleEncode ('$'.join(rawStr))+"!"

def computeClusterCenter (cluster) -> tuple:
    cdef int x, x_mean=0, y, y_mean=0
    for cell in cluster:
        x ,y = cell
        x_mean += x
        y_mean += y
    x_mean = round (x_mean/len (cluster))
    y_mean = round (y_mean/len (cluster))
    return (x_mean, y_mean)

def transition (float rand, float prob, alive, unsigned int num_neigh) -> bool:
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

def __run__ (current_world, prob, unsigned int steps) -> set:
    # main loop
    for s in range (steps):
        counts = Counter(n for cell in current_world for n in offset (cell))
        new_world = set ()
        for cell in counts:
            if transition (rand(), prob, cell in current_world, counts[cell]):
                new_world.add (cell)
        current_world = new_world
    return current_world