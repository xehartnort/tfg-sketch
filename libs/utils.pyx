from collections import Counter
from re import sub
import random
import hashlib
import numpy as np

neighboring_cells = [
    (-1, 1), (0, 1), (1, 1), 
    (-1, 0),         (1, 0), 
    (-1,-1), (0,-1), (1,-1)
]

transition_table = np.array([
    [0, 0, 0, 1, 0, 0, 0, 0, 0],
    [0, 0, 1, 1, 0, 0, 0, 0, 0]
], dtype=np.bool)


def _hashify_(world) -> str:
    return hashlib.blake2s (bytes (str (world), 'utf-8')).hexdigest()

def offset (delta) -> set:
    "Slide/offset all the cells by delta, a (dx, dy) vector."
    (dx, dy) = delta
    return {(x+dx, y+dy) for (x, y) in neighboring_cells}

def computeClusters (current_world) -> list:
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

def computeBoundingBox (world) -> tuple:
    Xs, Ys = zip(*world)
    return (min(Xs), max(Xs), min(Ys), max(Ys))

def computeWH(world) -> float:
    minX, maxX, minY, maxY = computeBoundingBox(world)
    w = maxX - minX + 1
    h = maxY - minY + 1
    return (w,h)

def computeClusterCenter (cluster) -> tuple:
    Xs, Ys = zip(*cluster)
    return (round (sum (Xs)/len (cluster)), round (sum (Ys)/len (cluster)))

def transition (float rand, float prob, alive, unsigned int num_neigh) -> bool:
    '''
        alive: it states if the cell is alive or not
        int num_neigh: number of neighbors
    '''
    if rand < prob:
        alive = transition_table[int(alive)][num_neigh]
    return alive

def __run__ (current_world, float prob, unsigned int steps, randstate) -> tuple:
    random.setstate(randstate)
    # main loop
    for s in range (steps):
        counts = Counter(n for cell in current_world for n in offset (cell))
        current_world = {cell for cell in counts if transition (random.random(), prob, cell in current_world, counts[cell])}
    return current_world, random.getstate()
