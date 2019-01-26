from libs.GoLv2 import GameOfLife
import os, sys
import argparse
import json
import hashlib

if __name__ == "__main__":
    ### BEGIN SIMULATION PARAMETERS ###
    description = "So far I don't know what should I write here"
    parser = argparse.ArgumentParser(description)
    parser.add_argument("-n", default="default", type=str, dest="sim_name", help='Simulation name')
    parser.add_argument("-p", default=1, type=float, dest="run_prob", help='Probability of applying current rules in each run')
    parser.add_argument("-nr", default=1, type=int, dest="number_of_runs", help='Number of runs')
    parser.add_argument("-rs", default=10, type=int, dest="run_steps", help="Run steps")
    #parser.add_argument("-ip", default='icons', type=str, dest="icon_path", help="Icon path")
    parser.add_argument("-i", default='a', type=str, dest="inputFile", help="File which contains the first state of every run" )
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
    gol = GameOfLife(file_path, prob=run_prob)
    experiment = {
        'pattern': simName, 
        'runProb': run_prob,
        'runSteps': runSteps,
        'NumberOfruns': number_of_runs,
        'runs': []
    }
    for i in range(number_of_runs):
        run = {
            'runNumber': i,
            'steps':[]
        }
        step = { 
            'id' : '0',
            'type':'root', 
            'ncells': gol.countLife(), 
            'weight': 1,
            'step': 0,
        }
        run['steps'].append(step)
        for j in range(1,runSteps+1):
            gol.run()
            clusters = gol.computeClusters()
            # cluster postprocess
            normClusters = list()


            id_node = hashlib.sha1(bytes(str(gol.getWorld()), 'utf-8')).hexdigest()
            step = { 
                'id' : id_node,
                'type' : 'node', 
                'ncells': gol.countLife(), 
                'step': j,
            }
            run['steps'].append(step)
            if gol.countLife() == 0:
                break
        gol.reset()
        experiment['runs'].append(run)
# Write output
with open(args.outputFile, 'w+') as outfile:
    json.dump(experiment,outfile, indent=2)