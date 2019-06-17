import numpy as np
import matplotlib.pyplot as plt
import os, argparse, sys
### BEGIN SIMULATION PARAMETERS ###
description = "If you think about a processing pipeline, this part does the math"
parser = argparse.ArgumentParser(description)
parser.add_argument('-i', '--input-dir', dest="inDirs", nargs='+', help="Files which contains raw data to be processed", required=True)
args = parser.parse_args(sys.argv[1:])
inDirs = args.inDirs

for inDir in inDirs:
    if not os.path.exists(inDir):
        os.makedirs(inDir)
    if inDir[-1] != '/':
        inDir += '/'
    plots_dict = dict()
    for filename in os.listdir(inDir):
        if filename.endswith(".data"):
            name = filename
            var_arr = name[:-5].split("_") # aquí está toda la info del archivo
            alpha = var_arr[2]
            mc = np.genfromtxt(inDir+filename, delimiter="\t", dtype=None, encoding="utf-8")
            names = mc.dtype.names
            iteraciones = mc[names[0]]
            means = mc[names[1]]
            tri_std = mc[names[2]]
            if var_arr[1] == "Clusteres":
                var_arr[1] = "Clústeres"
            elif var_arr[1] == "Celulas":
                var_arr[1] = "Nodos ocupados"
            elif var_arr[1] == "Fijas":
                var_arr[1] = "Vidas inmóviles"
            if var_arr[1] not in plots_dict:
                plots_dict[var_arr[1]] = []
            plots_dict[var_arr[1]].append((float(alpha), np.mean(means), np.std(means)))# x, y, std
    for k in plots_dict:
        print(k)
        fig = plt.figure(figsize = (10, 12))
        ax1 = fig.add_subplot(211)
        ax1.errorbar([i[0] for i in plots_dict[k]], [i[1] for i in plots_dict[k]], yerr=[i[2] for i in plots_dict[k]], fmt='o', capsize=3) #label=r'$\mu\in[\mu-3\sigma,\mu+3\sigma]$ con $p-value > 0.05$', fmt='o', capsize=3)
        ax1.grid(True, which='major', axis="both", linestyle="--", c="0.6", lw=0.35)
        plt.xlabel(r'$\alpha$')
        if var_arr[1] == "Clusteres":
            var_arr[1] = "Clústeres"
        elif var_arr[1] == "Celulas":
            var_arr[1] = "Nodos ocupados"
        plt.ylabel('{}'.format(var_arr[1]))
        #plt.legend(shadow=True, loc='best', fancybox=True)
        if var_arr[1] == "Clústeres":
            var_arr[1] = "Clusteres"
        fig.savefig(inDir+"alpha_{}.png".format(k), bbox_inches='tight')
        plt.close(fig=fig)
