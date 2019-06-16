from libs.GoLv2 import GameOfLife
import os, sys, math
import argparse
import ujson as json
from functools import reduce
from itertools import combinations
from multiprocessing import Pool
import numpy as np
from scipy.stats import normaltest
import random
import matplotlib.pyplot as plt

def genSeed():
    random_data = os.urandom(8)
    return int.from_bytes(random_data, byteorder="big")

def runStep (GoL):
    initWorld = GoL.currentWorld.copy()
    newGoL = GameOfLife(world = initWorld, randState=GoL.getRandState(), prob=GoL.getAlpha())
    newGoL.run()
    count = newGoL.countLife()
    area = 0
    if count != 0:
        area = newGoL.computeArea()
    clusters = newGoL.computeClusters()
    nstill = 0
    for i in range(len(clusters)+1):
        for j in combinations(clusters, i):
            nstill += sum(map(GameOfLife.isStillLife , j))
    
    return (GoL, 
        {
            'ncells': count,
            'nstillLifes': nstill,
            'nclusters': len (clusters),
            'heat': len (initWorld^newGoL.currentWorld),
            'area': area,
        })

if __name__ == "__main__":
    description = "If you think about a processing pipeline, this part generates raw data, easy to cook, easy to plot"
    parser = argparse.ArgumentParser(description)
    parser.add_argument("-nr", default=1000, type=int, dest="number_of_runs", help='Number of runs')
    parser.add_argument("-rs", default=100, type=int, dest="run_steps", help="Run steps")
    parser.add_argument('-d', '--output-dir', type=str, dest="outDir", help="dir where I will export the data", required=True)
    parser.add_argument('-ss', '--sampler-seed', dest="sampler_seed", type=int, help="Seed used to reproduce results")
    parser.add_argument('-i', '--input-list', dest="inList", nargs='+', help="Files which contains raw data to be processed", required=True)
    parser.add_argument("-a", '--alpha-list', dest="alpha_list", nargs='+', help='List of probabilities of applying current rules in each run', required=True)
    args = parser.parse_args(sys.argv[1:])
    outDir = args.outDir
    inList = args.inList
    ### BEGIN SIMULATION PARAMETERS ###
    number_of_steps = args.run_steps
    number_of_runs = args.number_of_runs
    if args.sampler_seed == None:
        sampler_seed = genSeed()
    else: 
        sampler_seed = args.sampler_seed
    alpha_list = [float(i) for i in args.alpha_list]
    ### END SIMULATION PARAMETERS ###
    if not os.path.exists(outDir):
        os.makedirs(outDir)
    if outDir[-1] != '/':
        outDir += '/'
    for fil in inList:
        if not os.path.isfile(fil):
            print("Error: File: {} is not a file or it does not exist".format(fil))
            exit(-1)
    for i in alpha_list:
        if i > 1 or i <= 0:
            print("Error: alpha values must be in the interval (0,1]") 
            exit(-1)
    for fil in inList:
        for alpha in alpha_list:
            filename = fil.split('/')[-1][:-4]
            random.seed(sampler_seed)
            experiment = {
                'samplerSeed': sampler_seed,
                'pattern': filename, 
                'alpha': alpha,
                'numberOfsteps': number_of_steps,
                'numberOfruns': number_of_runs,
                'runs': [[] for _ in range(number_of_steps)]
            }
            # hay que añadir la iteración inicial
            one = GameOfLife(initial_conf_file = fil)
            initWorld = one.current_world
            GoLs = [GameOfLife(world = initWorld.copy(), prob = alpha, seed = random.random()) for i in range(number_of_runs)] 
            chunkSize = 1+int(len(GoLs)/2)
            inc = int(number_of_runs/10)
            with Pool(maxtasksperchild=chunkSize) as p:
                for i in range(number_of_steps):
                    nGoLs = []
                    for GoL, info in p.imap(runStep, GoLs, chunkSize):
                        nGoLs.append(GoL)
                        experiment['runs'][i].append(info)
                    GoLs = nGoLs
            # Write output
            with open(outDir+filename+'_{}.json'.format(alpha), 'w+') as outfile:
                json.dump(experiment, outfile)
        
