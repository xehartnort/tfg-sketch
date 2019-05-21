#CUSTOM IMPORTS
import libs.utils as utils
import time as t

from PIL import Image, ImageDraw, ImageOps

#replace this one with python rand
utils.setSeed(-1*int(t.time()))

class GameOfLife:

    def __init__(self, initial_conf_file, prob = 1) -> None:
        self.prob = prob
        self.__load_conf__(initial_conf_file)

# Adapt this, so that .rle files can be input
    def _parse_row_(self, row_pos, input_row) -> list:
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

    def __load_conf__(self, filename) -> None:
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
                self.width = width
                self.height = height
                rows = raw_pattern.split("$")
                assert len(rows) <= height
                row_pos = 0
                for r in rows:
                    new_cells, skip = self._parse_row_(row_pos, r)
                    self.init_world |= new_cells
                    row_pos += skip
                self.current_world = self.init_world

    @property
    def currentWorld(self) -> set:
        return self.current_world
    
    @property
    def dim(self)-> tuple:
        return (self.width, self.height)

    def reset(self) -> None:
        self.current_world = self.init_world

    def countLife(self) -> int:
        return len(self.current_world)

    def run(self, steps=1) -> None:
        self.current_world = utils.__run__(self.current_world, self.prob, steps)

    def computeClusters(self) -> list:
        return utils.computeClusters(self.current_world)

    def __generate_squares__(self, image_width, image_height, side_length) -> list:
        """Generate coordinates for a tiling of unit squares."""
        for x in range(image_width):
            for y in range(image_height):
                yield [(x * side_length, y * side_length) for (x, y) in [(x, y), (x + 1, y + 1)]]

    def draw(self, side_length) -> Image:
        im = Image.new('L', size=(self.width*side_length, self.height*side_length))
        im = ImageOps.expand(im, border = 1, fill="#C6C6C6")
        for square in self.__generate_squares__(self.width, self.height, side_length):
            if (square[0][0]/side_length, square[0][1]/side_length) in self.current_world:
                ImageDraw.Draw(im).rectangle(square, outline="#C6C6C6", width = 2, fill="black")
            else:
                ImageDraw.Draw(im).rectangle(square, outline="#C6C6C6", width = 2, fill="white")
        return im