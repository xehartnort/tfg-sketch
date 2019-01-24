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
    parser.add_argument("-p", default=0.7, type=float, dest="run_prob", help='Probability of applying current rules in each run')
    parser.add_argument("-nr", default=10000, type=int, dest="number_of_runs", help='Number of runs')
    parser.add_argument("-rs", default=105, type=int, dest="run_steps", help="Run steps")
    parser.add_argument("-ip", default='icons', type=str, dest="icon_path", help="Icon path")
    parser.add_argument("-i", default='a', type=str, dest="inputFile", help="File which contains the first state of every run" )
    parser.add_argument("-o", default='default.json', type=str, dest="outputFile", help="Output file, the format is JSON, so it is expected to end with .json" )
    args = parser.parse_args(sys.argv[1:])
    file_path = args.inputFile #"/home/xehartnort/Escritorio/Trabajo/tfg-sketch/patterns/oscilator.rle"
    if not os.path.isfile(file_path):
        print("Error: File supplied is not a file or it does not exist")
        exit(-1)
    icon_path = args.icon_path
    if not os.path.exists(icon_path):
        os.makedirs(icon_path)
    if icon_path[-1] != "/":
        icon_path += "/"
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
        'iconPath': icon_path,
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
            id_node = hashlib.blake2s(bytes(str(gol.getWorld()), 'utf-8')).hexdigest()
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