# this starts up the APPJ testbed (for warm-up) can also check connection to
# measurement devices
#
# Requirements:
# * Python 3
# * several 3rd party packages including CasADi, NumPy, Scikit-Optimize for
# the implemented algorithms and Seabreeze, os, serial, etc. for connection to
# the experimental setup.
#
# Copyright (c) 2024 Mesbah Lab. All Rights Reserved.
# Contributor(s): Kimberly Chan
# Affiliation: University of California, Berkeley
#
# This file is under the MIT License. A copy of this license is included in the
# download of the entire code package (within the root folder of the package).

## import 3rd party packages
import sys
sys.dont_write_bytecode = True
import time
import serial

## import user functions
import utils.arduino as ard

################################################################################
## Startup/prepare APPJ
################################################################################
if __name__=="__main__":

    ## Set startup values
    dutyCycleIn = 100
    powerIn = 4.0
    flowIn = 3.0

    ## connect to/open connection to devices in setup
    # Arduino
    arduinoAddress = ard.getArduinoAddress(os="ubuntu")
    print("Arduino Address:", arduinoAddress)
    arduinoPI = serial.Serial(arduinoAddress, baudrate=38400, timeout=1)
    s = time.time()

    # send startup inputs
    time.sleep(2)
    ard.sendInputsArduino(arduinoPI, powerIn, flowIn, dutyCycleIn, arduinoAddress)
    time.sleep(2)
    input("Ensure plasma has ignited and press Return to begin.\n")

    # let APPJ run for a bit
    time.sleep(2)
    ard.sendInputsArduino(arduinoPI, 2.0, 2.0, dutyCycleIn, arduinoAddress)
    ard.sendInputsArduino(arduinoPI, 2.0, 2.0, dutyCycleIn, arduinoAddress)
    time.sleep(2)

    print("Waiting 15 minutes to warm up the plasma jet...\n")
    time.sleep(60*5)
    print("10 minutes left...")
    time.sleep(60*5)
    print("5 minutes left...")
    time.sleep(60*5)
    print("15 minutes have passed!")

    ard.sendInputsArduino(arduinoPI, 0.0, 0.0, dutyCycleIn, arduinoAddress)
