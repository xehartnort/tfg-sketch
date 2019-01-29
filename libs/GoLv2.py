#CUSTOM IMPORTS
import libs.utils as utils
import time as t

utils.setSeed(-1*int(t.time()))

class GameOfLife:

    def __init__(self, initial_conf_file, prob = 1) -> None:
        self.prob = prob
        self.init_world = self.__load_conf__(initial_conf_file)
        self.current_world = self.init_world

    def __load_conf__(self, filename) -> set:
            with open(filename, 'r') as f:
                world = set()
                lines = f.readlines()
                self.name = lines[0]
                for l in lines[1:]:
                    x, y = l.split()
                    world.add ((int(x), int(y)))
                return world
    @property
    def currentWorld(self) -> set:
        return self.current_world

    def reset(self) -> None:
        self.current_world = self.init_world

    def countLife(self) -> int:
        return len(self.current_world)

    def run(self, steps=1) -> None:
        self.current_world = utils.__run__(self.current_world, self.prob, steps)

    def computeClusters(self) -> list:
        return utils.computeClusters(self.current_world)