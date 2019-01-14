#hacky
import sys, os
sys.path = [os.path.abspath(os.path.dirname(__file__))] + sys.path

import numpy as np
import numexpr as ne
#CUSTOM IMPORT
from custom_rand import *

setSeed(-1)

class GameOfLife:
    # TODO THIS IS ONLY FOR A FINITE BOARD
    def __init__(self, initial_conf_file, size = 20, prob = 1) -> None:
        # Game of Life size
        self.size = size
        self.min_x = self.size
        self.min_y = self.size
        self.max_x = 0
        self.max_y = 0
        self.prob = prob
        self.new_run = True 
        self.limit_reached = False # it checks if boundaries has been reached
        initial_conf = self.__load_conf__(initial_conf_file)
        self.m = initial_conf
        self.init_m = initial_conf

    def _parse_row_(self, input_row) -> list:
        run_count_str = ""
        new_row = []
        for i in range(len(input_row)):
            char = input_row[i]
            if char.isdigit():
                run_count_str += char
            else:
                cell_value = 1 if char == 'o' else 0
                if run_count_str == "":
                    new_row += [cell_value]
                else:
                    new_row += [cell_value]*int(run_count_str)
                run_count_str = ""
        if "!" in input_row[-1]:
            run_count_str = 0
        return (new_row, int(run_count_str) if run_count_str != "" else 1)

    def __load_conf__(self, filename) -> np.array:
            with open(filename, 'r') as f:
                m = np.zeros(shape=(self.size, self.size), dtype=np.uint8)
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
                    else:
                        raw_pattern += line.strip(" \n\r\t")
                assert width <= self.size
                assert height <= self.size 
                self.min_x = int(self.size/2) - int(width/2)
                self.min_y = int(self.size/2) - int(height/2)
                self.max_x = self.min_x + width
                self.max_y = self.min_y + height
                rows = raw_pattern.split("$")
                assert len(rows) <= height
                row_pos = self.min_y
                for r in rows:
                    n_row, skip = self._parse_row_(r)
                    for i in range(width):
                        m[row_pos, self.min_x+i] = n_row[i]
                    row_pos += skip
                return m
    '''
        Transition function
            current_state: cell's current state
            num_neigh: number of neighbors
    '''
    def __transition__(self, current_state, num_neigh) -> int:
        if rand() < self.prob:
            new_state = 0
            if current_state >= 1 and (num_neigh == 2 or num_neigh == 3): # survival rule
                new_state = 1
            elif current_state == 0 and num_neigh == 3: # born rule
                new_state = 1
        else:
            new_state = current_state
        return new_state

    def reset(self) -> None:
        self.min_x = self.size
        self.min_y = self.size
        self.max_x = 0
        self.max_y = 0
        self.new_run = True 
        self.limit_reached = False # it checks if boundaries has been reached
        self.m = self.init_m

    def countLife(self) -> int:
        return np.sum(self.m)

    def getRawPattern(self, initPoint=(0,0), endPoint=None) -> str:
        raw_pattern = ""
        len_o = 0
        len_b = 0
        if endPoint == None:
            endPoint = (self.size, self.size)
        for i in range(initPoint[0], endPoint[0]+1): 
            for j in range(initPoint[1], endPoint[1]+1):
                if self.m[i,j] >= 1:
                    if len_b > 0:
                        raw_pattern += (str(len_b) if len_b>1 else "")+'b'
                        len_b = 0
                    len_o += 1
                else:
                    if len_o > 0:
                        raw_pattern += (str(len_o) if len_o > 1 else "")+'o'
                        len_o = 0
                    len_b += 1
            if len_o > 0:
                raw_pattern += (str(len_o) if len_o > 1 else "")+'o'
                len_o = 0
            if len_b > 0:
                raw_pattern += (str(len_b) if len_b > 1 else "")+'b'
                len_b = 0
            if i != self.size-1:
                raw_pattern += "$"
        raw_pattern += "!"
        return raw_pattern

    def compute_smallest_square(self) -> tuple:
        if self.new_run:
            self.new_run = False
            if np.sum(self.m) != 0:
                self.min_x = 0
                while np.sum(self.m[self.min_x]) == 0:
                    self.min_x += 1
                if self.min_x != 0:
                    self.min_x -= 1
                else:
                    self.limit_reached = True
                self.max_x = self.size-1
                while np.sum(self.m[self.max_x]) == 0:
                    self.max_x -= 1
                if self.max_x != self.size-1:
                    self.max_x += 1
                else:
                    self.limit_reached = True
                self.min_y = 0
                while np.sum(self.m[:,self.min_y]) == 0:
                    self.min_y +=1
                if self.min_y != 0: 
                    self.min_y -= 1
                else:
                    self.limit_reached = True
                self.max_y = self.size-1
                while np.sum(self.m[:,self.max_y]) == 0:
                    self.max_y -= 1
                if self.max_y != self.size-1:
                    self.max_y += 1
                else:
                    self.limit_reached = True
            else:
                self.min_x = 0
                self.max_x = 0
                self.min_y = 0
                self.max_y = 0
        return (self.min_x, self.min_y, self.max_x, self.max_y)
        
    def get_current_state(self) -> np.array:
        return self.m
        
    def get_limit_reached(self) -> bool:
        return self.limit_reached
    
    def run(self, steps=1) -> None:
        # main loop
        for s in range(steps):
            #compute smallest square
            self.compute_smallest_square()
            if not self.limit_reached:
                m_next = np.zeros(shape=(self.size, self.size), dtype=np.uint8)
                # make shifted copies of the original array
                allW = np.c_[np.zeros(self.size, dtype=np.uint8), self.m[:, :-1]]
                allE = np.c_[ self.m[:, 1:], np.zeros(self.size, dtype=np.uint8) ] 
                allN = np.r_[ self.m[1:], [np.zeros(self.size, dtype=np.uint8)] ] 
                allS = np.r_[ [np.zeros(self.size, dtype=np.uint8)], self.m[:-1] ]
                allSE = np.r_[ [np.zeros(self.size, dtype=np.uint8)], 
                    np.c_[ np.zeros(self.size-1, dtype=np.uint8), self.m[:-1,:-1] ] ]
                allSW = np.r_[ [np.zeros(self.size, dtype=np.uint8)],  
                    np.c_[ self.m[:-1,1:], np.zeros(self.size-1, dtype=np.uint8) ] ]
                allNW = np.r_[ np.c_[ self.m[1:,1:], np.zeros(self.size-1, dtype=np.uint8) ],[np.zeros(self.size, dtype=np.uint8)] ]
                allNE = np.r_[ np.c_[ np.zeros(self.size-1, dtype=np.uint8), self.m[1:,:-1] ],[np.zeros(self.size, dtype=np.uint8)]]
                # parallel summation of the matrices
                m2 = ne.evaluate("allW + allNW + allN + allNE + allE + allSE + allS + allSW")

                # Apply GoL rule
                for i in range(self.min_x, self.max_x+1):
                    for j in range(self.min_y, self.max_y+1):
                        m_next[i,j] = self.__transition__(self.m[i,j], m2[i,j])
                self.m = m_next
        self.new_run = True