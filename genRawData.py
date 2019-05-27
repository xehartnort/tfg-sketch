from libs.GoLv2 import GameOfLife
import libs.utils as utils
import os, sys
import argparse
import json
import hashlib
from multiprocessing import Pool

def genSeed():
    random_data = os.urandom(8)
    return int.from_bytes(random_data, byteorder="big")

if __name__ == "__main__":
    ### BEGIN SIMULATION PARAMETERS ###
    description = "If you think about a processing pipeline, this part generates raw data, easy to cook, easy to plot"
    parser = argparse.ArgumentParser(description)
    parser.add_argument("-n", default="default", type=str, dest="sim_name", help='Simulation name')
    parser.add_argument("-p", default=0.1, type=float, dest="run_prob", help='Probability of applying current rules in each run')
    parser.add_argument("-nr", default=1000, type=int, dest="number_of_runs", help='Number of runs')
    parser.add_argument("-rs", default=100, type=int, dest="run_steps", help="Run steps")
    parser.add_argument("-i", default='a', type=str, dest="inputFile", help="File which contains the first state of every run", required=True)
    parser.add_argument("-o", default='default.json', type=str, dest="outputFile", help="Output file, the format is JSON, so it is expected to end with .json" )
    args = parser.parse_args(sys.argv[1:])
    file_path = args.inputFile
    if not os.path.isfile(file_path):
        print("Error: File supplied is not a file or it does not exist")
        exit(-1)
    simName = args.sim_name
    runSteps = args.run_steps
    number_of_runs = args.number_of_runs
    run_prob = args.run_prob
    ### END SIMULATION PARAMETERS ###
    def runStep (GoL):
        initWorld = GoL.currentWorld.copy()
        origHash = GoL.hashify()
        GoL.run()
        return (GoL, {'fatherHash': [origHash],
                'hash': GoL.hashify(),
                'ncells': GoL.countLife(),
                'nclusters': len (GoL.computeClusters()),
                'heat': len (initWorld^GoL.currentWorld),
                'ocurrences': 1
            })

    seeds = [genSeed() for i in range(number_of_runs)]
    experiment = {
        'pattern': simName, 
        'runProb': run_prob,
        'runSteps': runSteps,
        'NumberOfruns': number_of_runs,
        'seeds': seeds,
        'runs': []
    }
    one = GameOfLife(initial_conf_file = file_path)
    initWorld = one.current_world
    GoLs = [GameOfLife(world = initWorld.copy(), prob = run_prob, seed = seeds[i]) for i in range(number_of_runs)] 
    chunkSize = 1+int(len(GoLs)/4)
    with Pool(processes=4) as p:
        for i in range(runSteps):
            tmpDict = dict()
            nGoLs = []
            for GoL, info in p.imap(runStep, GoLs, chunkSize):
                nGoLs.append(GoL)
                if info['hash'] in tmpDict:
                    tmpDict[info['hash']]['ocurrences'] += 1
                    tmpDict[info['hash']]['fatherHash'] += info['fatherHash']
                else:
                    tmpDict[info['hash']] = info
            experiment['runs'].append(list(tmpDict.values()))
            GoLs = nGoLs

    # Write output
    with open(args.outputFile, 'w+') as outfile:
        json.dump(experiment, outfile, indent=1)


