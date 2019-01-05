cdef extern from "my_rand.c":
    float ran2(long *idum)

'''
Long period (> 2 × 10^18 ) random number generator of L’Ecuyer with Bays-Durham shuffle
and added safeguards. Returns a uniform random deviate between 0.0 and 1.0 (exclusive of
the endpoint values). Call with idum a negative integer to initialize; thereafter, do not alter
idum between successive deviates in a sequence. RNMX should approximate the largest floating
value that is less than 1.
'''

cdef long seed = -1

def setSeed(long s):
    global seed
    if s > 0:
        s = s*-1
    seed = s

def rand():
    global seed
    return ran2(&seed)
    
