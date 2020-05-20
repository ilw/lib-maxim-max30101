import csv
import sys
import argparse
import time
import numpy as np
# import matplotlib.pyplot as plt
from collections import deque


###########################
# Read in Arguments & set default parameters
###########################
parser = argparse.ArgumentParser(description='Simulate realtime PPG data')
parser.add_argument("--ipFile", default='ppg.csv',
                    help="--ipFile='path_to_file'")

args = parser.parse_args()

BUFF_SIZE = 250
UPDATE_DELAY = 1.0

loopCount = 1
tLoopStart = time.time()



temp_red = np.zeros(BUFF_SIZE,dtype=float)
temp_ir = np.zeros(BUFF_SIZE,dtype=float)
temp_green = np.zeros(BUFF_SIZE,dtype=float)

spo2_store = np.zeros(1,dtype=float)
increment = 2.6e05


class FileTailer(object):
    def __init__(self, file, delay=0.1):
        self.file = file
        self.delay = delay
    def __iter__(self):
        while True:
            where = self.file.tell()
            line = self.file.readline()
            if line and line.endswith('\n'): # only emit full lines
                yield line
            else:                            # for a partial line, pause and back up
                time.sleep(self.delay)       # ...not actually a recommended approach.
                self.file.seek(where)


#read through all the lines and load the last BUFF_SIZE into memory
with open(args.ipFile, 'rb') as f:
    csvreader = csv.reader(FileTailer(f, delay=0.2*UPDATE_DELAY), delimiter=',', quotechar='|')

        
    while True:

        for row in csvreader:
            readPos = f.tell()
            
            #What does this do???
            new_red = float(row[0]) - (np.floor(float(row[0])/increment))*increment
            new_ir = float(row[1]) - (np.floor(float(row[1]) / increment)) * increment
            new_green = float(row[2]) - (np.floor(float(row[1]) / increment)) * increment
            
            # new_red = float(row[0])
            # new_ir = float(row[1])
            # new_green = float(row[2])             
            
            temp_red = np.roll(temp_red,-1)
            temp_ir = np.roll(temp_ir,-1)
            temp_green = np.roll(temp_green,-1)
            
            temp_red[-1] = new_red
            temp_ir[-1] = new_ir
            temp_green[-1] = new_green
                
            if time.time() > tLoopStart + loopCount *UPDATE_DELAY :
                loopCount +=1

                dc_red = np.mean(temp_red)
                dc_ir = np.mean(temp_ir)
                ac_red = np.max(temp_red) - np.min(temp_red)
                ac_ir = np.max(temp_ir) - np.min(temp_ir)
                spo2 = 104 - 17.0*((ac_red/dc_red)/(ac_ir/dc_ir))
                spo2_store = np.append(spo2_store, spo2)
                print(dc_red,dc_ir,ac_red,ac_ir,spo2)        
                

