################################################################################
# Heart Rate Example
#
# Created: 19/5/2020
#
################################################################################
#
#import streams
import max30101
import csv
from time import sleep
from datetime import datetime
from gpiozero import Button  # A button is a good approximation for what we need, a digital active-low trigger
import numpy as np
import sys

buff_red=[]
buff_ir=[]
buff_green=[]
mode = max30101.MAX30101_MODE_SPO2

max = max30101.MAX30101()
now = datetime.now()
filename = now.strftime("%d-%m-%Y_%H-%M-%S") + ".csv"



def read_data():
    data_red = []
    data_ir = []
    data_green = []
    
    interrupts = max.read_triggered_interrupt()
    #print(interrupts)
    
    #when fifo almost_full is triggered there should be at least 17 samples from each active LED 
    
    if max.led_mode == max30101.MAX30101_MODE_HR:
        raw = max.read_raw_samples(17*3)
        #rawArray = np.asarray(raw)
        for i in range(len(rawArray)/3):
            data_red.append(rawArray[i*3]*65536 + rawArray[i*3+1]*256 + rawArray[i*3+2]) #TODO could be written more elegantly...
            
    elif max.led_mode == max30101.MAX30101_MODE_SPO2:
        raw = max.read_raw_samples(17*3*2)
        rawArray = np.asarray(raw)
        for i in range(len(rawArray)/6):
            data_red.append(rawArray[i*6]*65536 + rawArray[i*6+1]*256 + rawArray[i*6+2])
            data_ir.append(rawArray[i*6+3]*65536 + rawArray[i*6+4]*256 + rawArray[i*6+5])
            
    else : 
        raw = max.read_raw_samples(17*3*3)
        rawArray = np.asarray(raw)
        for i in range(len(rawArray)/9):
            data_red.append(rawArray[i*9]*65536 + rawArray[i*9+1]*256 + rawArray[i*9+2])
            data_ir.append(rawArray[i*9+3]*65536 + rawArray[i*9+4]*256 + rawArray[i*9+5])
            data_green.append(rawArray[i*9+6]*65536 + rawArray[i*9+7]*256 + rawArray[i*9+8])
    
    
    #pad the lists to the same length
    if len(data_ir) < len(data_red):
        data_ir.extend([0]*len(data_red))
    if len(data_green) < len(data_red):
        data_green.extend([0]*len(data_red))    
    #print(data_red)
    #print(data_ir)
    #print(data_green)
    with open(filename, 'a') as csvfile:
        datawriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for i in range(len(data_red)):
            datawriter.writerow([data_red[i] ,data_ir[i] ,data_green[i]])
    sys.stdout.write( ".")
    
# create an instance of the MAX30101 class
try:
    # Setup sensor
    # This setup is referred to max30101 on a Heartrate 4 click board 
    # connected to raspberry pi i2c pins sda - 3 & scl - 5), interrupt on pin 26
    # 3.3V & 5V from appropriate pins
    
    print("start...")
    
    interrupt = Button(26,pull_up = True)  # Setup the interrup pin
    interrupt.when_activated = read_data  # Connect the interrupt
    
    print("init...")
    max.init()
    # start a thread that reads and process raw data from the sensor
    #thread(detect_pulse,max)
    print("Ready!")
    print("---------------------------")
    max.set_fifo_afv(15) #set fifo almost full value to max to minimise number of reads 
    max.enable_interrupt(sources=["full"])  # Set up a trigger to fire when the FIFO buffer (on the MAX30100) fills up.
                                             # You could also use INTERRUPT_HR to get a trigger on every measurement.



except Exception as e:
    print(e)

while True:
    sleep(1)
    sys.stdout.flush()
    
