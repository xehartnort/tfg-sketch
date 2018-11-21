import numpy as np
import json

# TODO
# Si alcanza el borde, entonces acabamos
# Cargar estado inicial

# Python 3
class GameOfLife:
    # TODO THIS IS ONLY FOR INFINITE BOARD
    def __init__(self, initial_conf_file, size=100):
        # Game of Life size
        self.size = size
        # Big array which stores each step
        self.m_history = []
        # Load a configuration:
        initial_conf = __load_conf__(initial_conf_file)

        self.m_history.append(initial_conf)
        # L O A D I N G   S T A T E  O N  M
        # H E R E

    def __load_conf__(filename):
        with open(filename,'r') as f:
            m = np.zeros(shape=(size, size), type=np.int8)
            data = json.load(f)
            h = data['height']
            w = data['width']
            rle_str = data['rle']
            # 'b' off cell, 'o' on cell
            init_x = size/2 + h/2
            init_y = size/2 + w/2
            lastInt = False # last char was integer
            times = 1
            for i in range(len(rle_str)):
                char = rle_str[i]
                try:
                    if lastInt:
                        times = times*10 + int(char)
                    else:
                        times = int(char)
                        lastInt = True
                except ValueError:
                    if char == "b":
                        for i in range(times):
                            if i < w:
                                
                            else:
                                break
                    elif char == "o":

                    elif char == "$":
                        #end current line
                    elif char == "!":
                        break
                    lastInt = False
                    times = 1
            return m

    def __save_conf__(output_filename):

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
        

    def run(self, steps):
        m = self.m_history[-1]
        m_next = np.zeros(shape=(self.size, self.size), type=np.int8)
        # main loop
        for i in range(1,steps):
            # make the shifted copies of the original array
            allW = np.c_[ np.zeros(self.size), m[:, 1:]  ] 
            allE = np.c_[ m[:, :-1], np.zeros(self.size) ] 
            allN = np.r_[ [np.zeros(self.size)], m[1:] ] 
            allS = np.r_[ m[:-1], [np.zeros(self.size)] ]
            # pegar por arriba y por la izquierda
            allNW = np.r_[ [np.zeros(self.size)], 
                np.c_[ np.zeros(self.size-1), m[1:,1:] ] ]
            # pegar por arriba y por la derecha
            allNE = np.r_[ [np.zeros(self.size)],  
                    np.c_[ m[1:,:-1], np.zeros(self.size-1) ] ]
            # pegar por abajo y por la derecha
            allSE = np.r_[ np.c_[ m[:-1,:-1], np.zeros(self.size-1) ], 
                    [np.zeros(self.size)] ]
            # pegar por abajo y por la izquierda
            allSW = np.r_[ np.c_[ np.zeros(self.size-1), m[:-1,1:] ], 
                    [np.zeros(self.size)] ] 
            # summation of the matrices
            m2 = allW + allNW + allN + allNE + allE + allSE + allS + allSW
            # Apply GoL rule
            for i in range(self.size):
                for j in range(self.size):
                    m_next[i,j] = self.__transition__(m[i,j], m2[i,j])
            m = m_next
            self.m_history.append(m)
