import csv
import sys
import argparse
import time
import numpy as np
import matplotlib.pyplot as plt
from collections import deque
from matplotlib.animation import FuncAnimation

###########################
# Read in Arguments & set default parameters
###########################
parser = argparse.ArgumentParser(description='Simulate realtime PPG data')
parser.add_argument("--ipFile", default='ppg.csv',
                    help="--ipFile='path_to_file'")

args = parser.parse_args()

BUFF_SIZE = 2000
UPDATE_DELAY = 1.0
DISP_LENGTH = 100

loopCount = 1
tLoopStart = time.time()



temp_red = np.zeros(BUFF_SIZE,dtype=float)
temp_ir = np.zeros(BUFF_SIZE,dtype=float)
temp_green = np.zeros(BUFF_SIZE,dtype=float)

spo2_store = np.zeros(DISP_LENGTH,dtype=float)
increment = 2.6e05

xData = np.arange(DISP_LENGTH)


readPos = 0 #could speed startup by seeking nearer the end (if filesize > x*BUFF_SIZE, seek to end - x*BUFF_SIZE, search for \n and move just past it


#read through all the lines and load the last BUFF_SIZE into memory
def readPpgData(): 
    global readPos, temp_red, temp_ir, temp_green, args
    
    with open(args.ipFile, 'rb') as f:
        csvreader = csv.reader(f, delimiter=',', quotechar='|')
        f.seek(readPos,0)
        for row in csvreader:
            if len(row)==3:
                readPos = f.tell()
                
                #What does this increment do???
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
            




fig,ax = plt.subplots()
ln, = plt.plot([],[])

def initPlt():
    global ax, ln
    #pass
    ax.set_xlim(0,DISP_LENGTH)
    ax.set_ylim(50,100)
    return ln,
    
def updatePlt(i):
    global spo2_store, temp_red, temp_ir, temp_green, ln
    #pass
    readPpgData()
    
    dc_red = np.mean(temp_red)
    dc_ir = np.mean(temp_ir)
    ac_red = np.max(temp_red) - np.min(temp_red)
    ac_ir = np.max(temp_ir) - np.min(temp_ir)
    spo2 = 104 - 17.0*((ac_red/dc_red)/(ac_ir/dc_ir))
    print(dc_red,dc_ir,ac_red,ac_ir,spo2)
    
    spo2_store = np.roll(spo2_store,-1)
    spo2_store[-1] =  spo2
    
    ln.set_data(xData, spo2_store)
    return ln,
    
    


readPpgData() #do initial read

ani = FuncAnimation(fig, updatePlt, init_func=initPlt, blit=True)
plt.show()



