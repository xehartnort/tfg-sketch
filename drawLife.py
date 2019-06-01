from libs.GoLv2 import GameOfLife
import os, sys
import argparse
import json
import hashlib

if __name__ == "__main__":
    ### BEGIN SCRIPT PARAMETERS ###
    description = "If you think about a processing pipeline, this part generates raw data, easy to cook, easy to plot"
    parser = argparse.ArgumentParser(description)
    #parser.add_argument("-o", default="name.png", type=str, dest="im_name", help='Image name')
    parser.add_argument('-i', nargs = '*', dest = 'input_files', help = '.rle files', default = argparse.SUPPRESS)
    #parser.add_argument("-i", default='file.rle', type=str, dest="input_file", help="File which contains the initial configuration", required=True)
    args = parser.parse_args(sys.argv[1:])
    file_paths = args.input_files
    for i in file_paths:
        if not os.path.isfile(i):
            print("Error: File supplied is not a file or it does not exist")
            exit(-1)
    ### END SCRIPT PARAMETERS ###
    for f in file_paths:
        gol = GameOfLife(initial_conf_file=f)
        im = gol.draw(30)
        im.save(f[:-4] + ".png", "PNG")

