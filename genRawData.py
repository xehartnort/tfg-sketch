from libs.GoLv2 import GameOfLife
import os, sys, math
import argparse
import ujson as json
import copy
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
    origHash = GoL.hashify()
    GoL.run()
    count = GoL.countLife()
    if count == 0:
        area = 0
    else:
        area = GoL.computeArea()
    return (GoL, 
        {'fatherHash': [origHash],
            'hash': GoL.hashify(),
            'ncells': count,
            'nclusters': len (GoL.computeClusters()),
            'heat': len (initWorld^GoL.currentWorld),
            'area': area,
            'ocurrences': 1
        })

def computeStats(values):
    length = len(values)
    mean = sum(values) / length
    squared_mean = sum([i**2 for i in values]) / length
    values_std = math.sqrt((squared_mean - mean**2)/number_of_runs)
    accumulated = [sum(values[:i])/i for i in range(1, length+1)]
    i = length-20
    w, p_value = normaltest(accumulated[i:])
    return (mean, values_std, p_value)

if __name__ == "__main__":
    description = "If you think about a processing pipeline, this part generates raw data, easy to cook, easy to plot"
    parser = argparse.ArgumentParser(description)
    parser.add_argument("-nr", default=1000, type=int, dest="number_of_runs", help='Number of runs')
    parser.add_argument("-rs", default=100, type=int, dest="run_steps", help="Run steps")
    parser.add_argument('-d', '--output-dir', type=str, dest="outDir", help="dir where I will export the data", required=True)
    parser.add_argument('-ss', '--seed-list', dest="seed_list", nargs='*', help="Files which contains raw data to be processed")
    parser.add_argument('-i', '--input-list', dest="inList", nargs='+', help="Files which contains raw data to be processed", required=True)
    parser.add_argument("-a", '--alpha-list', dest="alpha_list", nargs='+', help='List of probabilities of applying current rules in each run', required=True)
    args = parser.parse_args(sys.argv[1:])
    outDir = args.outDir
    inList = args.inList
    ### BEGIN SIMULATION PARAMETERS ###
    number_of_steps = args.run_steps
    number_of_runs = args.number_of_runs
    if args.seed_list != None:
        seed_list = [int(i) for i in args.seed_list]
    else: 
        seed_list = []
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
    if len(seed_list) != number_of_runs and len(seed_list)>0:
        print("Error: the number of seeds, {}, must be equal to the number of runs, {}".format(len(seed_list), number_of_runs))
        exit(-1)
    for fil in inList:
        for alpha in alpha_list:
            filename = fil.split('/')[-1][:-4]
            if len(seed_list) > 0:
                seeds = seed_list
            else:
                seeds = [genSeed() for i in range(number_of_runs)]
            samplerSeed = genSeed()
            random.seed(samplerSeed)
            experiment = {
                'samplerSeed': samplerSeed,
                'pattern': filename, 
                'alpha': alpha,
                'numberOfsteps': number_of_steps,
                'numberOfruns': number_of_runs,
                'seeds': seeds,
                'runs': [None for _ in range(number_of_steps)]
            }
            one = GameOfLife(initial_conf_file = fil)
            initWorld = one.current_world
            GoLs = [GameOfLife(world = initWorld.copy(), prob = alpha, seed = seeds[i]) for i in range(number_of_runs)] 
            chunkSize = 2+int(len(GoLs)/2)
            for i in range(number_of_steps):
                with Pool(processes=2, maxtasksperchild=chunkSize) as p:
                    tmpDict = dict()
                    nGoLs = []
                    for GoL, info in p.imap(runStep, GoLs, chunkSize):
                        nGoLs.append(GoL)
                        if info['hash'] in tmpDict:
                            tmpDict[info['hash']]['ocurrences'] += 1
                            tmpDict[info['hash']]['fatherHash'] += info['fatherHash']
                        else:
                            tmpDict[info['hash']] = info
                    experiment['runs'][i] = list(tmpDict.values())
                    GoLs = nGoLs + copy.deepcopy(random.sample(nGoLs, 200*i+1))
            # Write output
            with open(outDir+filename+'_{}.json'.format(alpha), 'w+') as outfile:
                json.dump(experiment, outfile)
        