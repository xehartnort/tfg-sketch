#!/bin/bash
# We are going to fix number of simulations at 1000 and prob at 0.7
# And move run steps
for step in {100..1000..100}
do
    opt="gol.py -ss $step -rs $step -p 0.7 -nr 1000 -i patterns/oscilator.rle -o oscilator_run_steps_$step.json"
    python3 $opt
done