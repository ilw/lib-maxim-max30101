forking to run this from a raspberry pi and remove reference to the rest of zerynth's code

max30101.py is the library, example.py is an example of how to run it and get data


basically create an instance of the class, init it, set up the interrupt & set up something to process the interrupt. 
NB you either  need to set up the interrupt handler before initialising the max30101 or read the interrupts straight away to clear the pin. 

