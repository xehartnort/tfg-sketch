from libs.GoL import GameOfLife
import sys
import json

# Here we have our main
if len(sys.argv) > 1:
    file_path = sys.argv[1] # "patterns/glider.rle"
    experiment = []
    sim_steps = 25
    number_of_sims = 100
    sim_size = 50
    sim_prob = 0.7
    gol = GameOfLife(file_path, size=sim_size, prob=sim_prob)
    for j in range(number_of_sims):
        simulation = {'pattern':'nombre', 'steps':[]}
        x1, y1, x2, y2 = gol.compute_smallest_square()
        step = { 
            'type':'root', 
            'initX': x1, 
            'initY': y1, 
            'width': x2-x1, 'height': y2-y1, 
            'rawPattern': gol.getRawPattern(initPoint=(x1,y1),endPoint=(x2+1,y2+1))}
        simulation['steps'].append(step)
        for i in range(sim_steps):
            gol.run()
            if gol.countLife() == 0 or gol.get_limit_reached():
                break
            #print(gol.get_current_state())
            x1, y1, x2, y2 = gol.compute_smallest_square()
            step = { 
                'type':'son', 
                'initX': x1, 'initY': y1, 
                'width': x2-x1, 'height': y2-y1, 
                'rawPattern': gol.getRawPattern(initPoint=(x1,y1),endPoint=(x2+1,y2+1))}
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