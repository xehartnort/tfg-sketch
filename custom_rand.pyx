cdef extern from "my_rand.c":
    float ran2(long *idum)

cdef long seed = 0

def setSeed(long s):
    global seed
    seed = s

def rand():
    global seed
    return ran2(&seed)
    
