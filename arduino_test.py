import serial
import time
import numpy as np

import utils.arduino as ard_utils

# Arduino
arduinoAddress = ard_utils.getArduinoAddress(os="ubuntu")
print("Arduino Address: ", arduinoAddress)
arduinoPI = serial.Serial(arduinoAddress, baudrate=38400, timeout=1)

print("Testing serial read from Arduino...\n")
print("The output should consist of a comma-separated line of values that do not change values with the exception of the first and last values.")
for i in range(20):
    out = ard_utils.getMeasArduino(arduinoPI)
    time.sleep(1)


print("Testing serial write to Arduino...\n")
print("The output should consist of a comma-separated line of values where some values are now changing.")
ard_utils.sendInputsArduino(arduinoPI, 1.5, 1.5, 100.0, arduinoAddress)
rand_power = (5.5-1.5) * np.random.random_sample(size=(20,)) + 1.5
rand_flow = (8.5-1.5) * np.random.random_sample(size=(20,)) + 1.5

for i in range(20):
    ard_utils.sendControlledInputsArduino(arduinoPI, rand_power[i], rand_flow[i], arduinoAddress)
    out = ard_utils.getMeasArduino(arduinoPI)
    time.sleep(0.5)
