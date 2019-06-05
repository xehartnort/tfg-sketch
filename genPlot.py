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
            # gráfica para mostrar lo que pasa con los p_values
            fig = plt.figure(figsize = (10, 12))
            ax1 = fig.add_subplot(211)
            colores = np.zeros((p_values.size, 3))
            bad_pos = np.where(p_values < 0.05)
            bad_blue = (0, 0.5, 1) # blue
            good_pos = np.where(p_values >= 0.05)
            good_orange = (1, 0.4, 0) # orange
            err_c = (0.6, 0, 0.8) # purple
            pvalue_bar = (1, 0.4, 0) # orange
            err, = ax1.plot(iteraciones, means+tri_std, color=err_c, ls='--')
            good_mean = ax1.scatter([i+1 for i in good_pos], means[good_pos], color=good_orange)
            bad_mean = ax1.scatter([i+1 for i  in bad_pos], means[bad_pos], color=bad_blue)
            ax1.plot(iteraciones, means-tri_std, color=err_c, ls='--')
            ax1.grid(True, which='major', axis="both", linestyle="--", c="0.6", lw=0.35)
            plt.xlabel('Iteraciones')
            if var_arr[1] == "Clusteres":
                var_arr[1] = "Clústeres"
            elif var_arr[1] == "Celulas":
                var_arr[1] = "Células"
            plt.ylabel('{}'.format(var_arr[1]))
            #finally add legend
            plt.legend((err, good_mean, bad_mean), ("Intervalo de confianza $[\mu-3\sigma,\mu+3\sigma]$", "$\mu$ con $p-value > 0.05$", "$\mu$ con $p-value \leq 0.05$"), #title=u"Polinómios", 
                    shadow=True, loc='best', fancybox=True)
            plt.savefig(inDir+filename[:-5]+".png", bbox_inches='tight')