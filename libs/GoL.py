#CUSTOM IMPORTS
import libs.utils as utils
import time as t
import random

from PIL import Image, ImageDraw, ImageOps

class GameOfLife:

    @staticmethod
    def isStillLife(world) -> bool:
        tmp = GameOfLife(world = world.copy())
        tmp.run()
        return len((world - tmp.currentWorld)) == 0 # this can be notoriously simplified

    def __init__(self, seed=None, randState=None, lifeFromFile=None, world=None, prob = 1):
        #inherit random status or start a new one
        if randState:
            random.setstate(randState)
        elif seed:
            self._seed = seed
            random.seed(seed)
        self.prob = prob
        # read from a file or inherit world
        if lifeFromFile:
            self._loadLifeFromFile_(lifeFromFile)
        elif world:
            self._initialWorld = world
            self._currentWorld = world
        self._offsetMemory = dict()
        assert self._initialWorld != None

    def _parseRow_(self, row_pos, input_row):
        run_count_str = ""
        cells = set()
        row_length = len(input_row)
        column_pos = 0
        for i in range(row_length):
            char = input_row[i]
            if char.isdigit():
                run_count_str += char
            elif char == 'o':
                if len(run_count_str) == 0:
                    cells.add((column_pos, row_pos))
                    column_pos +=1
                else:
                    for j in range(int(run_count_str)):
                        cells.add((column_pos+j, row_pos))
                    column_pos += int(run_count_str)
                run_count_str = ""
            elif char == 'b':
                if len(run_count_str) == 0:
                    column_pos += 1
                else:
                    column_pos += int(run_count_str)
                run_count_str = ""
        if "!" in input_row[-1]: # this is the end
            run_count_str = ""
        return (cells, int(run_count_str) if len(run_count_str) != 0 else 1)

    def _loadLifeFromFile_(self, filename):
            with open(filename, 'r') as f:
                self._initialWorld = set()
                raw_pattern = ""
                for line in f:
                    # Name of the pattern
                    if line.startswith("#N"):
                        self.name = line.lstrip("#N ").rstrip()
                    # Grid sizes and rules
                    elif line.startswith("x"):
                        data = line.split(",")
                        for d in data:
                            # Grid sizes
                            if d.strip().startswith("x"):
                                _, x = d.split("=")
                                width = int(x.strip())
                            elif d.strip().startswith("y"):
                                _, y = d.split("=")
                                height = int(y.strip())
                    # Other lines should contain the actual pattern
                    elif not line.startswith('#'):
                        raw_pattern += line.strip(" \n\r\t")
                # we fill the first cuadrant
                rows = raw_pattern.split("$")
                assert len(rows) <= height
                row_pos = 0
                for r in rows:
                    newCells, skip = self._parseRow_(row_pos, r)
                    self._initialWorld |= newCells
                    row_pos += skip
                self._currentWorld = self._initialWorld
    
    @property
    def currentWorld(self) -> set:
        return self._currentWorld

    @property
    def seed(self) -> float:
        return self._seed
    
    @property
    def alpha(self) -> float:
        return self.prob

    def randState(self):
        return random.getstate()

    def hashify(self):
        return utils._hashify_(self._currentWorld)
    
    def toRLE(self) -> str:
        return utils.genRleString(self._currentWorld)

    def area(self) -> int:
        w, h = utils.computeWH(self._currentWorld)
        return w*h

    def reset(self):
        self._currentWorld = self._initialWorld

    def count(self) -> int:
        return len(self._currentWorld)

    def run(self, steps=1):
        (self._currentWorld, randstate) = utils.__run__(self._currentWorld, self.prob, steps, self._offsetMemory, random.getstate())
        random.setstate(randstate)

    def clusters(self) -> list:
        return utils.computeClusters(self._currentWorld, self._offsetMemory)

    def draw(self, side_length=30):
        Xs, Ys = zip(*self._currentWorld)
        minx, maxx, miny, maxy = min(Xs), max(Xs), min(Ys), max(Ys)
        height = maxy - miny + 1 + 2 # wrap it with empty cells
        width = maxx - minx + 1 + 2 # wrap it with empty cells
        im = Image.new('L', size=(width*side_length, height*side_length))
        im = ImageOps.expand(im, border = 1, fill="#C6C6C6")
        for y in range(miny-2, maxy+2):
            for x in range(minx-2, maxx+2):
                square = [(x+1-minx)* side_length, (y+1-miny)* side_length, (x+2-minx)* side_length, (y+2-miny)* side_length]
                fillColor = "white"
                if (x, y) in self._currentWorld:
                    fillColor = "black"
                ImageDraw.Draw(im).rectangle(square, outline="#C6C6C6", width = 2, fill=fillColor)
        return im