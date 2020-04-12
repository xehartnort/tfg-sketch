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

transition_table = {
    False: [False, False, False, True, False, False, False, False, 0],
    True: [False, False, True, True, False, False, False, False, 0]
}

def _hashify_(set world) -> str:
    return hashlib.blake2s (bytes (str (world), 'utf-8')).hexdigest()

def offset (tuple delta, dict offsetMemory) -> set:
    "Slide/offset all the cells by delta, a (dx, dy) vector."
    (dx, dy) = delta
    if delta not in offsetMemory:
        offsetMemory[delta] = {(x+dx, y+dy) for (x, y) in neighboring_cells}
    return offsetMemory[delta]

def computeClusters (set current_world, dict offsetMemory) -> list:
    cluster_list = []
    world = current_world.copy ()
    while world: # empty set is the boolean false
        cluster = set ()
        cell = world.pop ()
        cluster.add (cell)
        neighborhood = world & offset (cell, offsetMemory)
        while neighborhood: # empty set is the boolean false
            cell = neighborhood.pop ()
            world.remove (cell)
            cluster.add (cell)
            neighborhood |= world & offset (cell, offsetMemory)
        cluster_list.append (cluster)
    return cluster_list

def rleEncode (str rawStr) -> str:
    return sub (r'([bo])\1*', lambda m: str (len (m.group(0)))+m.group(1) if len (m.group(0))>1 else m.group(1), rawStr)

def genRleString (set world) -> str:
    '''
        Display the world as rle string of b and o characters.
    '''
    Xs, Ys = zip(*world)
    Xrange = range (min (Xs), max (Xs)+1)
    rawStr = []
    for y in range (min (Ys), max (Ys)+1):
        rawStr.append (''.join('o' if (x, y) in world else 'b' for x in Xrange))
    return rleEncode ('$'.join(rawStr))+"!"

def computeBoundingBox (set world) -> tuple:
    Xs, Ys = zip(*world)
    return (min(Xs), max(Xs), min(Ys), max(Ys))

def computeWH(set world) -> int:
    minX, maxX, minY, maxY = computeBoundingBox(world)
    w = maxX - minX + 1
    h = maxY - minY + 1
    return (w,h)

def computeClusterCenter (set cluster) -> tuple:
    Xs, Ys = zip(*cluster)
    return (round (sum (Xs)/len (cluster)), round (sum (Ys)/len (cluster)))

def transition (float rand, float prob, bint alive, unsigned int num_neigh) -> bool:
    '''
        alive: it states if the cell is alive or not
        int num_neigh: number of neighbors
    '''
    if rand < prob:
        alive = transition_table[alive][num_neigh]
    return alive

def __run__ (set current_world, float prob, unsigned int steps, dict offsetMemory, randstate) -> tuple:
    random.setstate(randstate)
    for s in range (steps):
        counts = Counter(n for cell in current_world for n in offset (cell, offsetMemory))
        current_world = {cell for cell in counts if transition (random.random(), prob, cell in current_world, counts[cell])}
    return current_world, random.getstate()
