import numpy as np
import json
import numexpr as ne

# TODO
# Si alcanza el borde, entonces acabamos
# Guardar ultimo estado
# Implementar mi propio rand

# Python 3
class GameOfLife:
    # TODO THIS IS ONLY FOR A FINITE BOARD
    # Maybe here we should add a "seed" argument for the randomness
    def __init__(self, initial_conf_file, size=7, seed=None):
        # Game of Life size
        self.size = size
        # Big array which stores each step
        self.m_history = []
        # Smallest square which contains the pattern
        self.min_x = self.size
        self.min_y = self.size
        self.max_x = 0
        self.max_y = 0
        # Load a configuration:
        initial_conf = self.__load_conf__(initial_conf_file)
        self.m_history.append(initial_conf)

    def _parse_row_(self, input_row):
        run_count_str = ""
        new_row = []
        for i in range(len(input_row)):
            char = input_row[i]
            if char.isdigit():
                if run_count_str != "":
                    run_count_str += char
                else:
                    run_count_str = char
            else:
                cell_value = 1 if char == 'o' else 0
                if run_count_str == "":
                    new_row += [cell_value]
                else:
                    new_row += [cell_value]*int(run_count_str)
                # Set everything to default
                run_count_str = ""
        if "!" in input_row[-1]:
            run_count_str = 0
        return (new_row, int(run_count_str) if run_count_str != "" else 1)

    def __load_conf__(self, filename):
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
                # Si el tamanio es el mismo, 
                #if width == self.size and height == self.size:
                #    self.min_x = 0
                #    self.min_y = 0
                #    self.max_x = self.size
                #    self.max_y = self.size
                #else:
                self.min_x = int(self.size/2) - int(width/2)
                self.min_y = int(self.size/2) - int(height/2)
                self.max_x = self.min_x + width
                self.max_y = self.min_y + height
                rows = raw_pattern.split("$")
                assert len(rows) <= height
                row_pos = self.min_y
                for r in rows:
                    n_row, skip = self._parse_row_(r)
                    row_pos += skip
                    print("row_pos: {}, skip: {}".format(row_pos,skip))
                    for i in range(width):
                        assert row_pos < self.size
                        m[row_pos, self.min_x+i] = n_row[i]
                return m
    # it saves the state in a new way jiji
    def save_state_to_file(self, output_filename):
        m = self.m_history[-1] # get last history
        # self.compute_smallest_square()
        # now iterate throught the smallest square
        raw_pattern = ""
        len_o = 0
        len_b = 0
        for i in range(self.size): 
            for j in range(self.size):
                if m[i,j] == 1:
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
        with open(output_filename, 'w+') as f:
            f.write("#N {}".format(self.name)+"\n")
            f.write("x = {}, y = {}".format(self.size, self.size)+"\n")
            f.write(raw_pattern+"\n")


    def compute_smallest_square(self):
        m = self.m_history[-1]
        self.min_x = None
        self.min_y = None
        for i in range(self.size):
            if 1 in m[i] and not self.min_y:
                self.min_y = i
            if 1 in m[self.size-1-i] and not self.max_y:
                self.max_y = self.size-1-i
        for i in range(self.size):
            if 1 in m[:,i] and not self.min_x:
                self.min_x = i
            if 1 in m[:,self.size-i-1] and not self.max_x:
                self.max_x = self.size-i-1
        return (self.min_x, self.min_y, self.max_x, self.max_y)
        
    def get_history(self):
        return self.m_history

    def get_current_state(self):
        return self.m_history[-1]

    # TODO figure out what type should be prob
    def __transition__(self, current_state, num_neigh, prob=None):
        new_state = 0
        if current_state==1 and (num_neigh == 2 or num_neigh == 3):
            new_state = 1
        elif current_state == 0 and num_neigh == 3:
            new_state = 1
        return new_state
        
    def run(self, steps=1):
        # main loop
        for s in range(steps):
            m = self.m_history[-1]
            m_next = np.zeros(shape=(self.size, self.size), dtype=np.uint8)
            # make shifted copies of the original array
            allW = np.c_[np.zeros(self.size, dtype=np.uint8), m[:, :-1]]
            allE = np.c_[ m[:, 1:], np.zeros(self.size, dtype=np.uint8) ] 
            allN = np.r_[ m[1:], [np.zeros(self.size, dtype=np.uint8)] ] 
            allS = np.r_[ [np.zeros(self.size, dtype=np.uint8)], m[:-1] ]
            allSE = np.r_[ [np.zeros(self.size, dtype=np.uint8)], 
                np.c_[ np.zeros(self.size-1, dtype=np.uint8), m[:-1,:-1] ] ]
            allSW = np.r_[ [np.zeros(self.size, dtype=np.uint8)],  
                np.c_[ m[:-1,1:], np.zeros(self.size-1, dtype=np.uint8) ] ]
            # pegar por abajo y por la derecha
            allNW = np.r_[ np.c_[ m[1:,1:], np.zeros(self.size-1) ],[np.zeros(self.size, dtype=np.uint8)] ]
            # pegar por abajo y por la izquierda
            allNE = np.r_[ np.c_[ np.zeros(self.size-1, dtype=np.uint8), m[1:,:-1] ],[np.zeros(self.size, dtype=np.uint8)]]
            # parallel summation of the matrices
            m2 = allW + allNW + allN + allNE + allE + allSE + allS + allSW
            # Apply GoL rule
            for i in range(self.size):
                for j in range(self.size):
                    m_next[i,j] = self.__transition__(m[i,j], m2[i,j])
            self.m_history.append(m_next)



# Here we have our main
if __name__ == "__main__":
    gol = GameOfLife("/home/xehartnort/Escritorio/Trabajo/tfg-sketch/oscilator.rle")
    m = gol.get_current_state()
    print("Archivo cargado: ")
    print(m)
    # La transicion no funciona
    for i in range(3):
        print("Iteracion {}".format(i))
        gol.run(steps=1)
        print(gol.get_current_state())
    gol.save_state_to_file("/home/xehartnort/Escritorio/Trabajo/tfg-sketch/new_state")
    golLoaded = GameOfLife("/home/xehartnort/Escritorio/Trabajo/tfg-sketch/new_state")
    print("Archivo cargado")
    print(golLoaded.get_current_state())
    gol.run(steps=1)

    gol.save_state_to_file("/home/xehartnort/Escritorio/Trabajo/tfg-sketch/new_state")
    golLoaded = GameOfLife("/home/xehartnort/Escritorio/Trabajo/tfg-sketch/new_state")
    print("Archivo cargado")
    print(golLoaded.get_current_state())
    gol.run(steps=1)

    gol.save_state_to_file("/home/xehartnort/Escritorio/Trabajo/tfg-sketch/new_state")
    golLoaded = GameOfLife("/home/xehartnort/Escritorio/Trabajo/tfg-sketch/new_state")
    print("Archivo cargado")
    print(golLoaded.get_current_state())
    gol.run(steps=1)

    gol.save_state_to_file("/home/xehartnort/Escritorio/Trabajo/tfg-sketch/new_state")
    golLoaded = GameOfLife("/home/xehartnort/Escritorio/Trabajo/tfg-sketch/new_state")
    print("Archivo cargado")
    print(golLoaded.get_current_state())
