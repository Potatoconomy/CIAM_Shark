#!/usr/bin/env python


import sys
sys.path.append('/home/pi/FreiStat-Framework/Python')  #adds dependencies
sys.path.append('/usr/lib/python3/dist-packages')
sys.path.append('/home/pi/FreiStat-Framework')

import time                                                                                          
import mcp342x   
from datetime import datetime
import csv                                                                  
import matplotlib.pyplot as plt

from FreiStat.Methods.run_chronoamperometry import Run_CA
from FreiStat.Serial_communication.serial_communication import Communication
from FreiStat.Data_storage.constants import*

import os
import RPi.GPIO as GPIO
import matplotlib.pyplot as plt


"""
Circuit specific values:
    INA Gain = 5.87
"""
INA_GAIN = 5.87


"""
Relay Control:
    Normally Closed NC: INA recordings -> HIGH
    Normally Open   NO: Freistat       -> LOW
"""
RELAY = 26
GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY, GPIO.OUT)
GPIO.output(RELAY, GPIO.LOW)


"""
Freistat
    run_CA: wrapper for RUN_CA() method from FreiStat.Methods. ChronoAmperometry
    CV?
"""
run_CA = Run_CA(commnicationMode= FREISTAT_SERIAL ,
                mode= FREISTAT_STANDALONE
                )


"""
i2c Communications
    communication with MCP3246 ADC
"""
# get access to a specific device on a bus                                                            
i2c_bus_number = 1
device_address = 0x68
my_adc = mcp342x.Mcp3426(i2c_bus_number, device_address)


"""
MCP3246 ADC Settings
    SPS: 15, 60, or 240 
    pga_gain: 1, 2, 4, or 8
    mode:   one shot: continuous = False
            continuous: continuous = True
"""
sps = 15
pga_gain = 1
mode = 'continuous'
recording_freq = 1/sps

"""
Create Channel class
"""
def read_adc_ch1(channel=0, sample_rate=15, pga_gain=1, continuous=True, mode='voltage'):
    first_input = mcp342x.Channel(my_adc, channel)
    first_input.sample_rate = sample_rate
    first_input.pga_gain = pga_gain
    first_input.continuous = continuous
    first_input.start_conversion() # update device with current channel state and start acquisition   
    time.sleep(first_input.conversion_time)
    if mode == 'voltage':
        value = first_input.get_conversion_volts()/INA_GAIN
    elif mode == 'bits':
        value = first_input.get_conversion_raw()
    return value
    
def read_adc_ch2(channel=1, sample_rate=15, pga_gain=1, continuous=True, mode='voltage'):
    channel_number = 1
    second_input = mcp342x.Channel(my_adc, channel_number)
    second_input.sample_rate = sample_rate
    second_input.pga_gain = pga_gain
    second_input.continuous = continuous
    second_input.start_conversion() # update device with current channel state and start acquisition   
    time.sleep(second_input.conversion_time)
    #timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if mode == 'voltage':
        value = second_input.get_conversion_volts()/INA_GAIN
    elif mode == 'bits':
        value = second_input.get_conversion_raw()
    return value    
        
	
    
def save_reading_to_file(a, b, c, file_path):
    """Saves a reading with a label to a specified file."""
    
    with open(file_path, "a") as file:
        # Format the string with label and reading
        file.write(f"{a} {b} {c}\n")


def do_ca():
    GPIO.output(RELAY, GPIO.HIGH)        
    time.sleep(0.1)
    strExportPath = run_CA.start(Potential_Steps=[-0.3,0.8,-0.3,0.8,-0.3,0.8,-0.3,0.8,-0.3,.3],
							Pulse_Lengths=[10,10,10,10,10,10,10,10,10,50],
							Sampling_Rate=0.003,
							Cycle= 1,
							CurrentRange= 45e-3,
							FixedWEPotential= True,
							MainsFilter= True,
							Sinc2_Oversampling= 222,
							Sinc3_Oversampling= 2,
							EnableOptimizer= True,
							LowPerformanceMode= True
        )
    GPIO.output(RELAY, GPIO.LOW)   
            
            
def plotter(file_path, file_name, file_formatted):
    with open(file_path) as f:
        lines = f.readlines()
        t = [line.split()[0] for line in lines]
        y1 = [line.split()[1] for line in lines]
        y2 = [line.split()[2] for line in lines]

    t = [int(i) for i in t]
    t = [item - t[0] for item in t]
    y1 = [float(i) for i in y1]
    y2 = [float(i) for i in y2]
    plt.plot(t, y1)
    plt.plot(t, y2)
    plt.savefig(file_name)
    
    combined_data = list(zip(t,y1,y2))
    with open(file_formatted, "w") as f:
        for a,b,c in combined_data:
            f.write(f"{a}\t{b}\t{c}\n")
            
            
def main():
    file_path_ = "/home/pi/Patrick_Circuittesting/FG00800mV"  # Update this to your desired file path
    file_path = file_path_ + '.txt'
    file_path_2 = file_path_ + 'formatted.txt'
    file_path_png = file_path_ + '.png'
    print('collecting data')
    
    def get_ms_timestamp():
        return int(time.time() * 1000)
    
    def desired_time(t):
        return t * sps/2 # /2 if doing both channels
        
    i = 0
    while i <= desired_time(5):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        reading1 = read_adc_ch1()
        reading2 = read_adc_ch2()
        save_reading_to_file(get_ms_timestamp(), reading1, reading2, file_path)
        i = i+1
        
    plotter(file_path, file_path_png, file_path_2)
    
    
if __name__ == "__main__":
    main()


