#CUSTOM IMPORTS
import libs.utils as utils
import time as t
from copy import copy
utils.setSeed(-1*int(t.time()))

class GameOfLife:
    # TODO THIS IS ONLY FOR A FINITE BOARD
    def __init__(self, initial_conf_file, prob = 1) -> None:
        self.prob = prob
        self.init_world = self.__load_conf__(initial_conf_file)
        self.current_world = self.init_world

    def __load_conf__(self, filename) -> list:
            with open(filename, 'r') as f:
                world = []
                lines = f.readlines()
                self.name = lines[0]
                for l in lines[1:]:
                    x, y = l.split()
                    world.append((int(x),int(y)))
                return world

    def reset(self) -> None:
        self.current_world = self.init_world

    def countLife(self) -> int:
        return len(self.current_world)

    def getWorld(self) -> list:
        return self.current_world
        
    def run(self, steps=1) -> None:
        self.current_world = utils.__run__(self.current_world, self.prob, steps)

    def computeRleClusters(self) -> list:
        return utils.computeRleClusters(self.current_world)

'''
neighboring_cells = [
    (-1, 1), (0, 1), (1, 1), 
    (-1, 0),         (1, 0), 
    (-1,-1), (0,-1), (1,-1)]


def getNeighborhood(delta) -> dict:
    "Slide/offset all the cells by delta, a (dx, dy) vector."
    (dx, dy) = delta
    return {(x+dx, y+dy) for (x, y) in neighboring_cells}


    def __transition__(self, alive, num_neigh) -> bool:
        if rand() < self.prob:
            if (alive and num_neigh == 2) or num_neigh == 3: # survival rule
                alive = True
            else:
                alive = False
        return alive
'''