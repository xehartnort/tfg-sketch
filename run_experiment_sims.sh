#!/bin/bash
# We are going to fix prob at 0.7 and run_steps at 105
# And move number of simulations
for sim in {1000..10000..1000}
do
    opt="gol.py -ss 100 -rs 105 -p 0.7 -nr $sim -i patterns/oscilator.rle -o oscilator_sims_$sim.json"
    python3 $opt
done
