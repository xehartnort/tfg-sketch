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
for i in inList:
    if not os.path.isfile(i):
        print("Error: File supplied is not a file or it does not exist")
        exit(-1)
    filename = i.split('/')[-1]
    ncell_estimator = dict()
    ncluster_estimator = dict()
    pos_estimator = dict()
    ncell_cluster_estimator = dict()
    clusters_estimator = dict()
    with open(i, 'r') as fil:
        data = json.load(fil)
        runs = data['runs']
        for r in runs:
            steps = r['steps']
            runNumber = r['runNumber']
            if runNumber not in clusters_estimator:
                clusters_estimator[runNumber] = set()
            # Per Step
            for s in steps:
                # ncell_estimation
                if s['step'] not in ncell_estimator:
                    ncell_estimator[s['step']] = []
                ncell_estimator[s['step']].append(s['ncells'])
                # ncluster_estimation
                if s['step'] not in ncluster_estimator:
                    ncluster_estimator[s['step']] = []
                ncluster_estimator[s['step']].append(len(s['clusters']))
                # pos_estimation and ncell_cluster_estimation
                if s['step'] not in pos_estimator:
                    pos_estimator[s['step']] = []
                if s['step'] not in ncell_cluster_estimator:
                    ncell_cluster_estimator[s['step']] = []
                for c in s['clusters']:
                    pos_estimator[s['step']].append(c['center'])
                    ncell_cluster_estimator[s['step']].append(c['ncells'])
                    clusters_estimator[runNumber].add(c['rleEncondig'])
        stats = {
            'NumberOfCellsPerStep': {
                'mean': [],
                'std': []
            }, 
            'NumberOfCellsPerClusterPerStep': {
                'mean': [],
                'std': []
            },
            'NumberOfClustersPerStep': {
                'mean': [],
                'std': []
            },
            'NumberOfDifClustersPerRun': {
                'mean': [],
                'std': []
            }
        }
        # Stats per step
        for k in range(data['runSteps']+1):
            ncell_estimator[k] = np.array(ncell_estimator[k], dtype=np.int64)
            ncluster_estimator[k] = np.array(ncluster_estimator[k], dtype=np.int64)
            ncell_cluster_estimator[k] = np.array(ncell_cluster_estimator[k], dtype=np.int64)
            stats['NumberOfCellsPerStep']['mean'].append( 
                ncell_estimator[k].mean() )
            stats['NumberOfCellsPerStep']['std'].append( 
                ncell_estimator[k].std()/math.sqrt(len(ncell_estimator[k])) )
            stats['NumberOfCellsPerClusterPerStep']['mean'].append( 
                ncell_cluster_estimator[k].mean() )
            stats['NumberOfCellsPerClusterPerStep']['std'].append( 
                ncell_cluster_estimator[k].std()/math.sqrt(len(ncell_cluster_estimator[k])) )
            stats['NumberOfClustersPerStep']['mean'].append( 
                ncluster_estimator[k].mean() )
            stats['NumberOfClustersPerStep']['std'].append( 
                ncluster_estimator[k].std()/math.sqrt(len(ncluster_estimator[k])) )
        # Stats per run
        clustersPerRun = np.array([len(clusters_estimator[k]) for k in range(data['NumberOfruns'])], dtype=np.uint64)
        stats['NumberOfDifClustersPerRun']['mean'].append(clustersPerRun.mean())
        stats['NumberOfDifClustersPerRun']['std'].append(clustersPerRun.std()/math.sqrt(len(clustersPerRun)))
        with open(outDir+filename[:-5]+'_stats.json', 'w+') as out:
            json.dump(stats, out, indent=1)