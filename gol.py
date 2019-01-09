from libs.GoL import GameOfLife
import sys
import json
from math import ceil
from PIL import Image, ImageDraw

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

# Here we have our main
if len(sys.argv) >= 2:
    file_path = sys.argv[1] # "patterns/glider.rle"
    name = file_path.split("/")[-1].split('.')[0]
    experiment = []
    ### BEGIN SIMULATION PARAMETERS ###
    sim_steps = 100
    number_of_sims = 1000
    sim_size = 105
    sim_prob = 0.7
    sim_icon_path = "JS/icons/"
    ### END SIMULATION PARAMETERS ###
    gol = GameOfLife(file_path, size=sim_size, prob=sim_prob)
    # Generate as many colors as simulations
    axis_range = pow(number_of_sims, 1/3)
    gap_size = ceil(255/axis_range)
    axis_range = ceil(axis_range)
    colors = []
    for r in range(axis_range):
        for g in range(axis_range):
            for b in range(axis_range):
                rgb = (gap_size*r,gap_size*g,gap_size*b)
                colors.append('#%02x%02x%02x' % rgb)
    for j in range(number_of_sims):
        simulation = {
            'pattern':name, 
            'simulationNumber': j+1,
            'simulationSize': sim_size, 
            'simulationProb': sim_prob,
            'simulationSteps': sim_steps,
            'simulationIconPath': 'icons/',
            'NumberOfSimulations': number_of_sims,
            'color' : colors[j] , 'steps':[]}
        x1, y1, x2, y2 = gol.compute_smallest_square()
        icon_name = name+colors[j][1:]+'.png'
        step = { 
            'type':'root', 
            'icon': icon_name,
            'initX': x1, 
            'initY': y1, 
            'width': x2-x1, 'height': y2-y1, 
            'rawPattern': gol.getRawPattern(initPoint=(x1,y1),endPoint=(x2,y2))}
        drawLife(m=gol.get_current_state(),dim=(x1,y1,x2,y2),name=sim_icon_path+icon_name)
        simulation['steps'].append(step)
        for i in range(1,sim_steps+1):
            gol.run()
            if gol.countLife() == 0 or gol.get_limit_reached():
                break
            x1, y1, x2, y2 = gol.compute_smallest_square()
            #print(gol.get_current_state())
            #print(gol.getRawPattern(initPoint=(x1,y1),endPoint=(x2,y2)))
            icon_name = name+colors[j][1:]+str(i)+'.png'
            drawLife(m=gol.get_current_state(),dim=(x1,y1,x2,y2),name=sim_icon_path+icon_name)
            step = { 
                'type':'son',
                'icon': icon_name, 
                'initX': x1, 'initY': y1, 
                'width': x2-x1, 'height': y2-y1, 
                'rawPattern': gol.getRawPattern(initPoint=(x1,y1),endPoint=(x2,y2))}
            simulation['steps'].append(step)
        gol.reset()
        experiment.append(simulation)
    print(json.dumps(experiment))
else:
    print("[Python3] Usage: gol.py <pattern.rle>")

# Escenario 1
# Cada celula lanza un dado, se decide si se aplican o no las reglas
# Finding no: 1
# Cuando se alcanza un estado estable y se considera aplicar o no las reglas, se mantiene el estado estable
# Por lo tanto es muy interesante representar un grafo con todos los posibles resultados


# Escenario 2
# Cada celula lanza un dado, se decide si se aplican las reglas o sus opuestas