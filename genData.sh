#!/bin/zsh

python3 genRawData.py -i patterns/glider.rle patterns/lightweightspaceship.rle patterns/blinker.rle -d rawResults -a 0.1 0.3 0.6 0.9 -nr 5000 -rs 50
python3 analyzeData.py -i rawResults/*.json -d processedData
python3 genPlot.py -i processedData/*