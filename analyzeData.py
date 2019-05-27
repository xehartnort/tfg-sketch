import sys, json, math, os, argparse
import numpy as np

### BEGIN SIMULATION PARAMETERS ###
description = "If you think about a processing pipeline, this part does the math"
parser = argparse.ArgumentParser(description)
parser.add_argument('-i', '--input-list', dest="inList", nargs='+', help="Files which contains raw data to be processed", required=True)
parser.add_argument('-d', '--output-dir', type=str, dest="outDir", help="dir where I will export the data", required=True)
args = parser.parse_args(sys.argv[1:])
outDir = args.outDir
inList = args.inList
if not os.path.exists(outDir):
    os.makedirs(outDir)
if outDir[-1] != '/':
    outDir += '/'
for fil in inList:
    if not os.path.isfile(fil):
        print("Error: File supplied is not a file or it does not exist")
        exit(-1)
    filename = fil.split('/')[-1]
    ncell_estimator = dict()
    ncluster_estimator = dict()
    pos_estimator = dict()
    ncell_cluster_estimator = dict()
    clusters_estimator = dict()
    with open(fil, 'r') as fileIn:
        data = json.load(fileIn)
        runs_data = data['runs']
        number_of_runs = data['NumberOfruns']
        # csv like style
        # each element contains (run_number, mean, std)
        nclusters_estimator = [] 
        heat_estimator = []
        ncells_estimator = []
        with open("{}_{}_nclusters.data".format(data['pattern'], data['runProb']), 'w+') as nclusters:
            with open("{}_{}_ncells.data".format(data['pattern'], data['runProb']), 'w+') as ncells:
                with open("{}_{}_heat.data".format(data['pattern'], data['runProb']), 'w+') as heat:
                    #nclusters.write("{}\t{}\t{}\n".format("run_number", "mean", "std"))
                    #ncells.write("{}\t{}\t{}\n".format("run_number", "mean", "std"))
                    #heat.write("{}\t{}\t{}\n".format("run_number", "mean", "std"))
                    for index, run in enumerate(runs_data):
                        nclusters_mean = sum([i['nclusters']*i['ocurrences'] for i in run]) / number_of_runs
                        ncells_mean = sum([i['ncells']*i['ocurrences'] for i in run]) / number_of_runs
                        heat_mean = sum([i['heat']*i['ocurrences'] for i in run]) / number_of_runs
                        ############################################################################## MAL MAL MAL MAL Y MAL
                        nclusters_squared_mean = sum([i['nclusters']**2 for i in run for j in range(i['ocurrences'])]) / number_of_runs
                        ncells_squared_mean = sum([i['ncells']**2 for i in run for j in range(i['ocurrences'])]) / number_of_runs
                        heat_squared_mean = sum([i['heat']**2 for i in run for j in range(i['ocurrences'])]) / number_of_runs
                        #######################################################################################
                        nclusters_std = math.sqrt((nclusters_squared_mean - nclusters_mean**2)/number_of_runs)
                        ncells_std = math.sqrt((ncells_squared_mean - ncells_mean**2)/number_of_runs)
                        heat_std = math.sqrt((heat_squared_mean - heat_mean**2)/number_of_runs)
                        nclusters.write("{}\t{}\t{}\n".format(index, nclusters_mean, 3*nclusters_std))
                        ncells.write("{}\t{}\t{}\n".format(index, ncells_mean, 3*ncells_std))
                        heat.write("{}\t{}\t{}\n".format(index, heat_mean, 3*heat_std))