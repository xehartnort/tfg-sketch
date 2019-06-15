import numpy as np
import matplotlib.pyplot as plt
import os, argparse, sys


plt.rcParams['mathtext.fontset'] = 'custom'
plt.rcParams['mathtext.rm'] = 'Bitstream Vera Sans'
plt.rcParams['mathtext.it'] = 'Bitstream Vera Sans:italic'
plt.rcParams['mathtext.bf'] = 'Bitstream Vera Sans:bold'

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
    for filename in os.listdir(inDir):
        if filename.endswith(".data"):
            name = filename
            var_arr = name[:-5].split("_")
            mc = np.genfromtxt(inDir+filename, delimiter="\t", dtype=None, encoding="utf-8")
            names = mc.dtype.names
            iteraciones = mc[names[0]]
            means = mc[names[1]]
            tri_std = mc[names[2]]
            p_values = mc[names[3]]
            fig = plt.figure(figsize = (10, 12))
            ax1 = fig.add_subplot(211)
            bad_pos = np.where(p_values < 0.05)
            good_pos = np.where(p_values >= 0.05)
            ax1.errorbar(iteraciones[good_pos], means[good_pos], yerr=tri_std[good_pos], label=r'$\mu\in[\mu-3\sigma,\mu+3\sigma]$ con $p-value > 0.05$', fmt='o', capsize=3)
            ax1.errorbar(iteraciones[bad_pos], means[bad_pos], yerr=tri_std[bad_pos], label=r'$\mu\in[\mu-3\sigma,\mu+3\sigma]$ con $p-value \leq 0.05$', fmt='o', capsize=3)
            ax1.grid(True, which='major', axis="both", linestyle="--", c="0.6", lw=0.35)
            plt.xlabel('Iteraciones')
            if var_arr[1] == "Clusteres":
                var_arr[1] = "Clústeres"
            elif var_arr[1] == "Celulas":
                var_arr[1] = "Nodos ocupados"
            plt.ylabel('{}'.format(var_arr[1]))
            plt.legend(shadow=True, loc='best', fancybox=True)
            if var_arr[1] == "Clústeres":
                var_arr[1] = "Clusteres"
            plt.savefig(inDir+filename[:-5]+".png", bbox_inches='tight')
            plt.close(fig=fig)