#!/bin/bash
# We are going to fix number of simulations at 1000 and run_steps at 105
# And move prob
for prob in {1..9}
do
    opt="gol.py -ss 100 -rs 105 -p 0.$prob -i patterns/oscilator.rle -o oscilator_prob-0$prob.json -nr 1000"
    python3 $opt
done