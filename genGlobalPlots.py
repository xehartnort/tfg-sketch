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
alpha_color = dict()
color_Arr = plt.rcParams['axes.prop_cycle'].by_key()['color']
i = 0
j = 0
l = len(color_Arr)
while i < 1:
    alpha_color['{:.2f}'.format(i)] = color_Arr[j%l]
    i += 0.05
    j += 1
alpha_color['{:.2f}'.format(0.99)] = color_Arr[j%l]
alpha_color['{:.2f}'.format(0.01)] = color_Arr[j%l]

for inDir in inDirs:
    if not os.path.exists(inDir):
        os.makedirs(inDir)
    if inDir[-1] != '/':
        inDir += '/'
    plots_dict = dict()
    for filename in os.listdir(inDir):
        if filename.endswith(".data"):
            name = filename
            var_arr = name[:-5].split("_")
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
                plots_dict[var_arr[1]] = plt.subplots() # part_fig, part_ax
                plots_dict[var_arr[1]][1].set_xlabel('Iteraciones')
                plots_dict[var_arr[1]][1].set_ylabel('{}'.format(var_arr[1]))
            plots_dict[var_arr[1]][1].errorbar(iteraciones, means, yerr=tri_std, label=r'$\alpha={}$'.format(alpha), fmt='.', capsize=3, color=alpha_color[alpha]) 
    for k in plots_dict:
        fig, ax = plots_dict[k]
        handles, labels = ax.get_legend_handles_labels()
        # sort both labels and handles by labels
        labels, handles = zip(*sorted(zip(labels, handles), key=lambda t: t[0]))
        fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.49, 1), ncol = 4, fancybox=True)
        if k == "Clústeres":
            k = "Clusteres"
        elif k == "Vidas inmóviles":
            k = "Fijas"
        fig.savefig(inDir+"{}_multiple_alpha.png".format(k), bbox_inches='tight')
        plt.close(fig=fig)
