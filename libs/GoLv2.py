#CUSTOM IMPORTS
import libs.utils as utils
import time as t
import random

from PIL import Image, ImageDraw, ImageOps

class GameOfLife:

    def __init__(self, seed=1, initial_conf_file=None, world={}, prob = 1):
        self.seed = seed
        random.seed(seed)
        self.prob = prob
        if initial_conf_file:
            self.__load_conf__(initial_conf_file)
        else:
            self.init_world = world
            self.current_world = world

    def _parse_row_(self, row_pos, input_row):
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
            #print(char)
            #print(cells)
        if "!" in input_row[-1]: # this is the end
            run_count_str = ""
        return (cells, int(run_count_str) if len(run_count_str) != 0 else 1)

    def __load_conf__(self, filename):
            with open(filename, 'r') as f:
                self.init_world = set()
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
                    new_cells, skip = self._parse_row_(row_pos, r)
                    self.init_world |= new_cells
                    row_pos += skip
                self.current_world = self.init_world

    @property
    def currentWorld(self):
        return self.current_world
    
    def getSeed(self):
        return self.seed
    
    def hashify(self):
        return utils._hashify_(self.current_world)
    
    def computeArea(self):
        w, h = utils.computeWH(self.current_world)
        return w*h

#    def resetTo(self, world) -> None:
#        self.current_world = world

    def reset(self):
        self.current_world = self.init_world

    def countLife(self):
        return len(self.current_world)

    def run(self, steps=1):
        self.current_world, randstate = utils.__run__(self.current_world, self.prob, steps, random.getstate())
        random.setstate(randstate)

    def computeClusters(self):
        return utils.computeClusters(self.current_world)

    def draw(self, side_length=30):
        Xs, Ys = zip(*self.current_world)
        minx, maxx, miny, maxy = min(Xs), max(Xs), min(Ys), max(Ys)
        height = maxy - miny + 1 + 2 
        width = maxx - minx + 1 + 2
        im = Image.new('L', size=(width*side_length, height*side_length))
        im = ImageOps.expand(im, border = 1, fill="#C6C6C6")
        for y in range(miny-2, maxy+2):
            for x in range(minx-2, maxx+2):
                square = [(x+1-minx)* side_length, (y+1-miny)* side_length, (x+2-minx)* side_length, (y+2-miny)* side_length]
                if (x, y) in self.current_world:
                    fillColor = "black"
                else: 
                    fillColor = "white"
                ImageDraw.Draw(im).rectangle(square, outline="#C6C6C6", width = 2, fill=fillColor)
        return im