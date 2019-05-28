import sys, json, math, os, argparse
import numpy as np
from scipy.stats import shapiro
from scipy.stats import normaltest
from multiprocessing import Pool

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
        # each element contains (run_number, mean, 3*std)
        nclusters_estimator = [] 
        heat_estimator = []
        ncells_estimator = []
        def computeStats(values):
            length = len(values)
            mean = sum(values) / length
            squared_mean = sum([i**2 for i in values]) / length
            values_std = math.sqrt((squared_mean - mean**2)/number_of_runs)
            accumulated = [sum(values[:i])/i for i in range(1, length+1)]
            i = 100
            w, p_value = normaltest(accumulated[i:])
            try:
                while p_value < 0.05:
                    w, p_value = normaltest(accumulated[i:])
                    i += 10
                    if length-i <20:
                        p_value = 0
                        break
                    
            except:
                p_value = 0
            return (i, p_value, mean, values_std)

    
        with open("{}_{}_nclusters.data".format(data['pattern'], data['runProb']), 'w+') as nclusters:
            with open("{}_{}_ncells.data".format(data['pattern'], data['runProb']), 'w+') as ncells:
                with open("{}_{}_heat.data".format(data['pattern'], data['runProb']), 'w+') as heat:
                    #nclusters.write("{}\t{}\t{}\n".format("run_number", "mean", "3std", "p-value"))
                    #ncells.write("{}\t{}\t{}\n".format("run_number", "mean", "3std", "p-value"))
                    #heat.write("{}\t{}\t{}\n".format("run_number", "mean", "3std", "p-value"))
                    with Pool(processes=3) as p:
                        for index, run in enumerate(runs_data):
                            heat_values = []
                            nclusters_values = []
                            ncells_values = []
                            for i in run:
                                for j in range(i['ocurrences']):
                                    heat_values.append(i['heat'])
                                    nclusters_values.append(i['nclusters'])
                                    ncells_values.append(i['ncells'])
                            r = p.map(computeStats, [heat_values, nclusters_values, ncells_values])#, ncells_values, nclusters])
                            nclusters.write("{}\t{}\t{}\t{}\t{}\n".format(index, r[2][2], 3*r[2][3], r[2][1], r[2][0]))
                            ncells.write("{}\t{}\t{}\t{}\t{}\n".format(index, r[1][2], 3*r[1][3], r[1][1], r[1][0]))
                            heat.write("{}\t{}\t{}\t{}\t{}\n".format(index, r[0][2], 3*r[0][3], r[0][1], r[0][0]))