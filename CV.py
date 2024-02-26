import sys
sys.path.append('/home/pi/FreiStat-Framework/Python')
sys.path.append('/usr/lib/python3/dist-packages')
from gpiozero import LED
import serial
#serialPort=serial.Serial(port="/dev/ttyACM0",baudrate=9600,bytesize=8, timeout=2, stopbits=serial.STOPBITS_ONE)
Relay = LED(26)

Relay.on()


from FreiStat.Methods.run_cyclic_voltammetry import Run_CV
from FreiStat.Serial_communication.serial_communication import Communication
from FreiStat.Data_storage.constants import*

run_CV = Run_CV(commnicationMode= FREISTAT_SERIAL ,
                mode= FREISTAT_STANDALONE
                )

strExportPath = run_CV.start(StartVoltage= 0.3,
                             FirstVertex= 1.05,
                             SecondVertex= -0.65,
                             Stepsize= 0.002,
                             Scanrate= 0.1,
                             Cycle= 1,
                             CurrentRange= 45e-6,
                             FixedWEPotential= True,
                             MainsFilter= True,
                             Sinc2_Oversampling= 222,
                             Sinc3_Oversampling= 2,
                             EnableOptimizer= True,
                             LowPerformanceMode= False
                             )
