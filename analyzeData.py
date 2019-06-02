import sys, math, os, argparse
import ujson as json
import numpy as np
from scipy.stats import normaltest
from multiprocessing import Pool

def computeStats(values):
    length = values.shape[0]
    mean = np.sum(values) / length
    squared_mean = np.sum(values*values) / length
    values_std = math.sqrt((squared_mean - mean**2) / length)
    accumulated = np.array([np.sum(values[:i])/i for i in range(1, length+1)])
    i = length-20
    w, p_value = normaltest(accumulated[i:])
    return (mean, values_std, p_value)

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
    with open(fil, 'r') as fileIn:
        data = json.load(fileIn)
        outDir2 = outDir + data['pattern'] +"/"
        if not os.path.exists(outDir2):
            os.makedirs(outDir2)
        runs_data = data['runs']
        number_of_runs = data['numberOfruns']
        number_of_steps = data['numberOfsteps']
        alpha = data['alpha']
        # csv like style
        # each element contains (run_number, mean, 3*std)
        nclusters = open(outDir2+"{}_{}_{}_{}_{}.data".format('iteración', 'Clusters', alpha, number_of_runs, number_of_steps), 'w+')
        ncells = open(outDir2+"{}_{}_{}_{}_{}.data".format('iteración', 'Células', alpha, number_of_runs, number_of_steps), 'w+')
        heat = open(outDir2+"{}_{}_{}_{}_{}.data".format('iteración', 'Calor', alpha, number_of_runs, number_of_steps), 'w+')
        area = open(outDir2+"{}_{}_{}_{}_{}.data".format('iteración', 'Área', alpha, number_of_runs, number_of_steps), 'w+')
        with Pool(processes=2) as p:
            for index, run in enumerate(runs_data):
                area_values = np.array([i['area'] for i in run for j in range(i['ocurrences'])])
                heat_values = np.array([i['heat'] for i in run for j in range(i['ocurrences'])])
                nclusters_values = np.array([i['nclusters'] for i in run for j in range(i['ocurrences'])])
                ncells_values = np.array([i['ncells'] for i in run for j in range(i['ocurrences'])])
                r = p.map(computeStats, [heat_values, nclusters_values, ncells_values, area_values])
                nclusters.write("{}\t{}\t{}\t{}\n".format(index, r[2][0], 3*r[2][1], r[2][2]))
                ncells.write("{}\t{}\t{}\t{}\n".format(index, r[1][0], 3*r[1][1], r[1][2]))
                heat.write("{}\t{}\t{}\t{}\n".format(index, r[0][0], 3*r[0][1], r[0][2]))
                area.write("{}\t{}\t{}\t{}\n".format(index, r[3][0], 3*r[3][1], r[3][2]))
        nclusters.close()
        ncells.close()
        heat.close()
        area.close()
    