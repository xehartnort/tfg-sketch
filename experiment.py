from libs.GoL import GameOfLife
import sys
import json
from math import ceil
from PIL import Image, ImageDraw
import os 
import hashlib
import argparse

def drawLife(m, dim, name, fullMode=False):
    if fullMode:
        x1,y1,x2,y2 = dim
        w = m.shape[0]
        h = m.shape[1]
        img = Image.new('RGB', (w, h), color=(0,0,0))
        b = img.load()  
        for i in range(x1,x2+1):
            for j in range(y1,y2+1):
                    b[i,j] = (m[i,j]*255,m[i,j]*255,m[i,j]*255)
    else:
        x1,y1,x2,y2 = dim
        w = x2-x1+1
        h = y2-y1+1
        img = Image.new('RGB', (w, h), color=(0,0,0))
        b = img.load()
        for i in range(w):
            for j in range(h):
                b[i,j] = (m[x1+i,y1+j]*255,m[x1+i,y1+j]*255,m[x1+i,y1+j]*255)
    img = img.resize((w*5,h*5)) # key?
    img.save(name)

def gen_colors(number_of_runs):
    axis_range = pow(number_of_runs, 1/3)
    gap_size = ceil(255/axis_range)
    axis_range = ceil(axis_range)
    colors = []
    for r in range(axis_range):
        for g in range(axis_range):
            for b in range(axis_range):
                rgb = (gap_size*r,gap_size*g,gap_size*b)
                colors.append('#%02x%02x%02x' % rgb)
    return colors

# Here we have our main

### BEGIN SIMULATION PARAMETERS ###
description = "So far I don't know what should I write here"
parser = argparse.ArgumentParser(description)
parser.add_argument("-n", default="default", type=str, dest="sim_name", help='Simulation name')
parser.add_argument("-p", default=0.7, type=float, dest="run_prob", help='Probability of applying current rules in each run')
parser.add_argument("-ss", default=100, type=int, dest="state_size", help='State size')
parser.add_argument("-nr", default=1000, type=int, dest="number_of_runs", help='Number of runs')
parser.add_argument("-rs", default=105, type=int, dest="run_steps", help="Run steps")
parser.add_argument("-ip", default='icons', type=str, dest="icon_path", help="Icon path")
parser.add_argument("-i", default=None, type=str, dest="inputFile", help="File which contains the first state of every run" )
parser.add_argument("-o", default='default.json', type=str, dest="outputFile", help="Output file, the format is JSON, so it is expected to end with .json" )
args = parser.parse_args(sys.argv[1:])
file_path = args.inputFile #"/home/xehartnort/Escritorio/Trabajo/tfg-sketch/patterns/oscilator.rle"
if not os.path.isfile(file_path):
    print("Error: File supplied is not a file or it does not exist")
    exit(-1)
icon_path = args.icon_path
if not os.path.exists(icon_path):
    os.makedirs(icon_path)
if icon_path[-1] != "/":
    icon_path += "/"
sim_name = args.sim_name
run_steps = args.run_steps
number_of_runs = args.number_of_runs
state_size = args.state_size
run_prob = args.run_prob
### END SIMULATION PARAMETERS ###
# we will deal with this object
gol = GameOfLife(file_path, size=state_size, prob=run_prob)
# Generate as many colors as simulations
# colors = gen_colors(number_of_runs)
experiment = {'pattern':sim_name, 
        'stateSize': state_size, 
        'runProb': run_prob,
        'runSteps': run_steps,
        'NumberOfruns': number_of_runs,
        'iconPath': icon_path,
        'nodeSet': {},
        'vertexSet': {}}
preComputedIds = {}
node_set = {}
vertex_set = {}
for j in range(number_of_runs):
    x1, y1, x2, y2 = gol.compute_smallest_square()
    rle_pattern = gol.getRawPattern(initPoint=(x1,y1),endPoint=(x2,y2))
    id_b = bytes(rle_pattern+str(x1)+","+str(y1), 'utf-8')
    if id_b not in preComputedIds:
        preComputedIds[id_b] = hashlib.sha1(id_b).hexdigest()
    id_ = preComputedIds[id_b]
    icon_name = id_+'.png'
    if not os.path.isfile(icon_path+icon_name):
        drawLife(m=gol.get_current_state(),dim=(x1,y1,x2,y2),name=icon_path+icon_name)
    node = { 
        'id': id_,
        'type':'root', 
        'x': x1, 'y': y1, 
        'area': (x2-x1)*(y2-y1), 
        'weight': 1,
        'step': 1,
        'rawPattern': rle_pattern
    }
    node_set[id_] = node
    lastNone = node
    for i in range(1,run_steps+1):
        gol.run()
        if gol.countLife() == 0 or gol.get_limit_reached():
            rle_pattern = 'o'
            step = { 
                'id': hashlib.sha1(bytes(rle_pattern+str(x1)+","+str(y1), 'utf-8')).hexdigest(),
                'type':'end',
                'x': -1, 'y': -1, 
                'area': 0, 
                'step': i,
                'rawPattern': rle_pattern
            }
            if not os.path.isfile(icon_path+icon_name):
                drawLife(m=gol.get_current_state(),dim=(0,0,1,1),name=icon_path+'.png')
            break
        else:
            x1, y1, x2, y2 = gol.compute_smallest_square()
            rle_pattern = gol.getRawPattern(initPoint=(x1,y1),endPoint=(x2,y2))
            id_b = bytes(rle_pattern+str(x1)+","+str(y1), 'utf-8')
            if id_b not in preComputedIds:
                preComputedIds[id_b] = hashlib.sha1(id_b).hexdigest()
            id_ = preComputedIds[id_b]
            icon_name = id_+'.png'
            if not os.path.isfile(icon_path+icon_name):
                drawLife(m=gol.get_current_state(),dim=(x1,y1,x2,y2),name=icon_path+icon_name)
            currentNode = { 
                'id': id_,
                'type': '',
                'x': x1, 'y': y1, 
                'area': (x2-x1)*(y2-y1), 
                'weight': 1,
                'step': i,
                'rawPattern': rle_pattern
            }
            if id_ not in node_set:
                node_set[id_] = currentNode
            else:
                node_set[id_]['weight'] += 1
            vertex = {
                'id' : lastNone['id']+id_,
                'source':lastNone['id'],
                'target': id_,
                'weight': 1
            }
            if vertex['id'] not in vertex_set:
                vertex_set[vertex['id']] = vertex
            else:
                vertex_set['weight'] += 1
            lastNode = node
    gol.reset()
    
    #experiment['runs'].append(run)

# Write output
with open(args.outputFile, 'w+') as outfile:
    json.dump(experiment, outfile)
    

# Escenario 1
# Cada celula lanza un dado, se decide si se aplican o no las reglas
# Finding no: 1
# Cuando se alcanza un estado estable y se considera aplicar o no las reglas, se mantiene el estado estable
# Por lo tanto es muy interesante representar un grafo con todos los posibles resultados


# Escenario 2
# Cada celula lanza un dado, se decide si se aplican las reglas o sus opuestas