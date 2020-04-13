import os
import sys
import argparse
import ujson as json
import random
import pymongo

from libs.GoL import GameOfLife
from multiprocessing import Pool

def runStep (GoL):
    initWorld = GoL.currentWorld
    newGoL = GameOfLife(world = initWorld, randStateM=GoL.randState(), prob=GoL.alpha)
    newGoL.run()
    count = newGoL.count()
    area = 0
    if count != 0:
        area = newGoL.area()
    clusters = newGoL.clusters()    
    return (GoL, 
        {
            'ncells': count,
            'nstillLifes': sum(map(GameOfLife.isStillLife , clusters)),
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
    if args.sampler_seed:
        sampler_seed = float(args.sampler_seed)
    else:
        sampler_seed = None # watch out here
    alpha_list = [float(i) for i in args.alpha_list]
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
    ### END SIMULATION PARAMETERS ###
    mongoLocation = "mongodb://localhost:27017/"
    dbName = "GameOfLifeExperiments"
    myclient = pymongo.MongoClient(mongoLocation)
    dblist = myclient.list_database_names()
    collist = []
    # Base de datos grande -> GameOfLifeExperiments
    # Colección -> tipo_de_vida.rle
    # Cada elemento es un experimento
    mydb = myclient["GameOfLifeExperiments"] # No database is created until it has content
    fieldsWanted = { "runs": 0 }
    findObject = {"samplerSeed": sampler_seed, "numberOfSteps": number_of_steps, "numberOfRuns": number_of_runs}
    for fil in inList:
        filename = fil.split('/')[-1]
        currentColletion = mydb[filename]
        for alpha in alpha_list:
            # here we need to check if this experiment is inserted, that is
            # If there is an experiment with the same alpha, sampler_seed, numberOfSteps and numberOfRuns
            findObject["alpha"] = alpha
            experimentFound = currentColletion.find_one(findObject, fieldsWanted)
            if experimentFound: # this experiment already exists
                continue
            random.seed(sampler_seed)
            experiment = {
                'samplerSeed': sampler_seed,
                #'pattern': filename, 
                'alpha': alpha,
                'numberOfSteps': number_of_steps,
                'numberOfRuns': number_of_runs,
                'runs': [[] for _ in range(number_of_steps)]
            }
            # hay que añadir la iteración inicial
            one = GameOfLife(lifeFromFile = fil)
            initWorld = one.currentWorld
            GoLs = [ GameOfLife(world = initWorld, prob = alpha, seed = sampler_seed) for i in range(number_of_runs) ]
            chunkSize = 1+int(number_of_runs/2)
            inc = int(number_of_runs/10)
            with Pool(maxtasksperchild=chunkSize) as p:
                for i in range(number_of_steps):
                    nGoLs = []
                    for GoL, info in p.imap(runStep, GoLs, chunkSize):
                        nGoLs.append(GoL)
                        experiment['runs'][i].append(info)
                    GoLs = nGoLs
            # Write output to db :D
            currentColletion.insert_one(experiment)