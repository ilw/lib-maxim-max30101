import csv
import sys
import argparse
import time
import numpy as np
from collections import deque
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore, QtWidgets, uic
import os
from pyqtgraph import PlotWidget, plot

###########################
# Read in Arguments & set default parameters
###########################
parser = argparse.ArgumentParser(description='Simulate realtime PPG data')
parser.add_argument("--ipFile", default='ppg.csv',
                    help="--ipFile='path_to_file'")

args = parser.parse_args()



###########################
#Configurable parameters
###########################

BUFF_SIZE = 250
UPDATE_DELAY = 1  #update period in seconds
DISP_LENGTH = 100
LINE_SIZE = 30  #max csv line length with safety margin. Its usually 17 for spo2
SPO2_AVERAGING = 3


###########################
# Initialise variables
###########################

loopCount = 1
tLoopStart = time.time()

temp_red = np.zeros(BUFF_SIZE,dtype=float)
temp_ir = np.zeros(BUFF_SIZE,dtype=float)
temp_green = np.zeros(BUFF_SIZE,dtype=float)
spo2_store = np.zeros(DISP_LENGTH,dtype=float)
spo2_smooth_store = np.zeros(DISP_LENGTH,dtype=float)
increment = 2.6e05

ptr = -DISP_LENGTH                      # set first x position

readPos = 0

#############################
# QT Window
#############################

class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        #Load the UI Page
        uic.loadUi('mainwindow.ui', self)





##############################
### QtApp Initialisation #####
##############################

app = QtWidgets.QApplication(sys.argv)
main = MainWindow()


rawPen = pg.mkPen(color=(0, 120, 0))   #set up the line colour
raw_curve = main.graphWidget.plot(pen=rawPen)           # create an empty "plot" (a curve to plot)

smoothPen = pg.mkPen(color=(255, 255, 0), width=2)
smooth_curve = main.graphWidget.plot(pen=smoothPen)        

main.graphWidget.setYRange(50, 100, padding=0)
main.graphWidget.showGrid(x=False, y=True, alpha=0.5)


main.show()


#read through the new data lines and load values into memory
def readPpgData(): 
    global readPos, temp_red, temp_ir, temp_green, args
    
    with open(args.ipFile, 'r') as f:
        csvreader = csv.reader(f, delimiter=',', quotechar='|')
        f.seek(readPos,os.SEEK_SET)
        for row in csvreader:
            if len(row)==3:
                
                #Output of the PPG has weird step increments, this removes any multiples of that increment.
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
            
        readPos = f.tell() #Accuracy of this depends on how csvreader deals with incomplete lines

    
def updatePlt():
    global spo2_store, temp_red, temp_ir, temp_green, ptr, raw_curve, spo2_smooth_store, smooth_curve
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
    spo2_smooth = np.mean(spo2_store[-SPO2_AVERAGING:-1])
    spo2_smooth_store = np.roll(spo2_smooth_store,-1)
    spo2_smooth_store[-1] = spo2_smooth
    
    
    ptr += 1                              # update x position for displaying the curve
    raw_curve.setData(spo2_store)                     # set the curve with this data
    smooth_curve.setData(spo2_smooth_store)                     
    raw_curve.setPos(ptr,0)                   # set x position in the graph to 0
    smooth_curve.setPos(ptr,0)      
    QtGui.QApplication.processEvents()    # you MUST process the plot now
    
    


######################
### SETUP  #####    
######################

#Seek to near the end of the file (in case a large recording has been done)

with open(args.ipFile, 'r') as f:
    f.seek(0,os.SEEK_END)
    fileSize = f.tell()
    if fileSize > BUFF_SIZE * LINE_SIZE:
        pos = f.tell() - BUFF_SIZE * LINE_SIZE
        f.seek(pos, os.SEEK_SET)   # go backwards 3 bytes
        s=f.read(LINE_SIZE)
        offset = s.find("\r\n") #b'\x0D\x0A')  #\r\n
        readPos = pos+offset+2


timer  = pg.QtCore.QTimer()
timer.timeout.connect(updatePlt)
timer.start(UPDATE_DELAY*1000)





##################
### END QtApp ####
##################
if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()

##################

