import csv
import sys
import argparse
import time
#from itertools import islice



###########################
#Read in Arguments & set default parameters
###########################
parser = argparse.ArgumentParser(description='Simulate realtime PPG data')
parser.add_argument("--ipFile",default='19-05-2020_09-40-05_clean_with_2_breath_holds.csv',help="--ipFile='path_to_file'")

parser.add_argument("--opFile",default='ppg.csv',help="--opFile='path_to_file'")

args = parser.parse_args()


SMP_FREQ = 1000.0
AVERAGING = 4.0
SMP_BATCH = 17.0

freq = SMP_FREQ/AVERAGING
period = 1/freq
batch_period = SMP_BATCH * period


rowCount =0
loopCount = 0
tLoopStart = time.time()

with open(args.opFile, 'wb') as g:
    csvwriter = csv.writer(g, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    while True:
        with open(args.ipFile, 'rb') as f:
            csvreader = csv.reader(f, delimiter=',', quotechar='|')

            for row in csvreader:
                csvwriter.writerow(row)
                
                rowCount +=1
                if rowCount % SMP_BATCH == 0:
                    loopCount = loopCount +1
                    rowCount =0
                    g.flush()
                    while time.time() < (tLoopStart + loopCount * batch_period):
                        time.sleep(0.01)  
                    #print (time.time())
                    sys.stdout.write(".")
                    sys.stdout.flush()
                
            if loopCount > 1000000: #if you forget it in the background
                break
         
