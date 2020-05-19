Forking Zerynth code to run this from a raspberry pi and remove reference to the rest of zerynth's code

max30101.py is the library, example.py is an example of how to run it and get data

Main library usage:
Basically create an instance of the class, init it, set up the interrupt & set up something to process the interrupt. 
NB you either  need to set up the interrupt handler before initialising the max30101 or read the interrupts straight away to clear the pin. 


Example.py 
Goes through the steps above to set up the interrupt and initialise the max30101


ppgLoop.py
ppgLoop will mimic the output of the raspberrry pi - continuously dumping data to a csv file in batches of 17 samples every 68ms. The source for the data and output file can be specified using --ipfile and --opfile
There are 2 example csv files, one has 2 breath holding events and i had my finger on the whole time. The other i didn't have my finger on until a few seconds into the recording






Raspberry pi setup:
This setup is referred to max30101 on a Heartrate 4 click board  connected to raspberry pi i2c pins sda - 3 & scl - 5), interrupt on pin 26,  3.3V & 5V from appropriate pins

enable i2c:
`sudo raspi-config`
then navigate to interfaces and enable it (may need to restart)

install i2c tools
`sudo apt-get install i2c-tools`

wire the board up and test whether communication is happening:
`i2cdetect -y 1`

get the necessary python packages:

`pip install smbus2 csv gpiozero`

 
