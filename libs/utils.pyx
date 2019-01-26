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

def setSeed(long s) -> None:
    global seed
    if s > 0:
        s = s*-1
    seed = s

def rand() -> float:
    global seed
    return ran2(&seed)

neighboring_cells = [
    (-1, 1), (0, 1), (1, 1), 
    (-1, 0),         (1, 0), 
    (-1,-1), (0,-1), (1,-1)
]

def offset(delta) -> set:
    "Slide/offset all the cells by delta, a (dx, dy) vector."
    (dx, dy) = delta
    return {(x+dx, y+dy) for (x, y) in neighboring_cells}

def computeClusters(current_world) -> set:
    cluster_list = []
    world = current_world.copy()
    while world: # empty set is the boolean false    
        cluster = set()
        cell = world.pop()
        cluster.add(cell)
        neighborhood = world & offset(cell)
        while neighborhood: # empty set is the boolean false
            cell = neighborhood.pop()
            world.remove(cell)
            cluster.add(cell)
            neighborhood |= world & offset(cell)
        cluster_list.append(cluster)
    return cluster_list

def normalizeClusters(clusters) -> list:
    normClusters = list()
    cdef int x_mean, dx, norm_x 
    cdef int y_mean, dy, norm_y
    for cluster in clusters:
        x_mean = 0
        y_mean = 0
        nCluster = set()
        for i in cluster:
            x_mean += i[0]
            y_mean += i[1]
        dx = abs (round (x_mean/len(cluster)))
        dy = abs (round (y_mean/len(cluster)))
        for i in cluster:
            norm_x, norm_y = i
            if i[0] > 0:
                norm_x -= dx
                if i[1] > 0: # primer cuadrante
                    norm_y -= dy
                else: # cuarto cuadrante
                    norm_y += dy
            else:
                norm_x += dx
                if i[1] > 0: # segundo cuadrante
                    norm_y -= dx
                else: # tercer cuadrante
                    norm_y += dy
            nCluster.add((norm_x, norm_y))
        normClusters.append(nCluster)
    return normClusters

def transition(float rand, float prob, alive, unsigned int num_neigh) -> bool:
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

def __run__(current_world, prob, unsigned int steps) -> set:
    # main loop
    for s in range(steps):
        counts = Counter(n for cell in current_world for n in offset(cell))
        new_world = set()
        for cell in counts:
            if transition(rand(), prob, cell in current_world, counts[cell]):
                new_world.add(cell)
        current_world = new_world
    return current_world