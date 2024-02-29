# this file runs the open loop data collection experiments for the APPJ testbed
# in the following paper:
#
#
# Requirements:
# * Python 3
# * several 3rd party packages including CasADi, NumPy, Scikit-Optimize for
# the implemented algorithms and Seabreeze, os, serial, etc. for connection to
# the experimental setup.
#
# Copyright (c) 2021 Mesbah Lab. All Rights Reserved.
# Contributor(s): Kimberly Chan
# Affiliation: University of California, Berkeley
#
# This file is under the MIT License. A copy of this license is included in the
# download of the entire code package (within the root folder of the package).

## import 3rd party packages
import sys
sys.dont_write_bytecode = True
import numpy as np
from seabreeze.spectrometers import Spectrometer, list_devices
import time
import os
import serial
from datetime import datetime
import asyncio

## import user functions
from utils.run_options import RunOpts
import utils.thermal_camera as tc_utils
import utils.async_measurement as ameas
import utils.arduino as ard_utils
from utils.oscilloscope import Oscilloscope
from utils.experiments import Experiment

## import picoscope settings
from picoscope_setup import *

## import arg_parse parser
from arg_parse import single_sample_parser as parser

plot_data = True # [True/False] whether or not to plot the (2-input, 2-output) data after an experiment

args = parser.parse_args()
sample_num = args.sample_num
time_treat = args.time_treat
P_treat = args.P_treat
q_treat = args.q_treat
dist_treat = args.dist_treat
int_time_treat = args.int_time_treat
ts = args.sampling_time

settings_str = f"The settings for this treatment are:\n"\
      f"Sample Number:              {sample_num}\n"\
      f"Treatment Time (s):         {time_treat}\n"\
      f"Power (W):                  {P_treat}\n"\
      f"Flow Rate (SLM):            {q_treat}\n"\
      f"Separation Distance (mm):   {dist_treat}\n"\
      f"Integration Time (us):      {int_time_treat}\n"\
      f"Sampling Time (s):          {ts}\n"
print(settings_str)

if ts < 2*int_time_treat*1e-6:
    print("Integration time too large! Please modify the integration time and/or the sampling time such that the sampling time is greater than double the integration time.")
    exit(1)

cfm = input("Confirm these are correct: [Y/n]\n")
if cfm in ['Y', 'y']:
    pass
else:
    quit()

################################################################################
## Startup/prepare APPJ
################################################################################

## collect time stamp
timeStamp = datetime.now().strftime('%Y_%m_%d_%H'+'h%M''m%S'+'s')
print('Timestamp for save files: ', timeStamp)
Nrep = 1

# configure run options
runOpts = RunOpts()
runOpts.collectData = True      # option to collect two-input, two-output data (power, flow rate); (max surface temperature, total intensity)
runOpts.collectEntireSpectra = True # option to collect full intensity spectra
runOpts.collectOscMeas = True # option to collect oscilloscope measurements (not functioning)
runOpts.collectSpatialTemp = False # option to collect spatial temperature (defined as temperature from 12 pixels away from max in the four cardinal directions)
# save options; correspond to the collection (two-input, two-output data is always saved)
runOpts.saveSpectra = True
runOpts.saveOscMeas = True
runOpts.saveSpatialTemp = False # limited functionality
runOpts.saveEntireImage = True
runOpts.tSampling = ts # set the sampling time of the measurements

## Set startup values
dutyCycleIn = 100
powerIn = P_treat
flowIn = q_treat

# set save location
directory = os.getcwd()
split_cwd = directory.split('/')
repo = split_cwd[-1]
saveDir = directory+f"/../{repo}-ExperimentalData/"+timeStamp+f"-Sample{sample_num}/"
print('\nData will be saved in the following directory:')
print(saveDir)

## connect to/open connection to devices in setup
# Arduino
arduinoAddress = ard_utils.getArduinoAddress(os="ubuntu")
print("Arduino Address: ", arduinoAddress) 
arduinoPI = serial.Serial(arduinoAddress, baudrate=38400, timeout=1)
s = time.time()

# Oscilloscope
mode = "streaming"  # or "block"
# Create an instance of the oscilloscope
osc = Oscilloscope(
    mode=mode,
    single_buff_size=single_buffer_size,
    n_buffs=n_buffers,
    pretrigger_size=pretrigger_size,
    posttrigger_size=posttrigger_size,
)
# Open the oscilloscope
status = osc.open_device()
print(status)
status = osc.initialize_device(channels, buffers)

# Spectrometer
devices = list_devices()
print(devices)
spec = Spectrometer(devices[0])
spec.integration_time_micros(int_time_treat) ## change integration time (units of microseconds)

# Thermal Camera
dev, ctx = tc_utils.openThermalCamera()
print("Devices opened/connected to sucessfully!")

devices = {}
devices["arduinoPI"] = arduinoPI
devices["arduinoAddress"] = arduinoAddress
devices["osc"] = osc
devices["spec"] = spec

# send startup inputs
time.sleep(2)
ard_utils.sendInputsArduino(arduinoPI, 2.0, 2.0, dutyCycleIn, arduinoAddress)
input("Ensure plasma has ignited and press return/enter to begin.\n")

## Startup asynchronous measurement
if os.name == 'nt':
    ioloop = asyncio.ProactorEventLoop() # for subprocess' pipes on Windows
    asyncio.set_event_loop(ioloop)
else:
    ioloop = asyncio.get_event_loop()
# run once to initialize measurements
prevTime = (time.time()-s)*1e3
tasks, runTime = ioloop.run_until_complete(
    ameas.async_measure(arduinoPI, osc, spec, runOpts)
)
print('measurement devices ready!')

# get initial measurements
tasks, runTime = ioloop.run_until_complete(
    ameas.async_measure(arduinoPI, osc, spec, runOpts)
)
if runOpts.collectData:
    thermalCamOut = tasks[0].result()
    Ts0 = thermalCamOut[0]
    specOut = tasks[1].result()
    I0 = specOut[0]
    oscOut = tasks[2].result()
    arduinoOut = tasks[3].result()
    outString = "Measured Outputs: Temperature: %.2f, Intensity: %.2f" % (Ts0, I0)
    print(outString)
else:
    Ts0 = 37
    I0 = 100

s = time.time()

################################################################################
## Begin Experiment:
################################################################################
Nsim = int(time_treat/runOpts.tSampling)
exp = Experiment(Nsim, saveDir)

f = open(saveDir+"notes.txt", 'a')
f.write(settings_str)

for i in range(Nrep):
    # create input sequences
    pseq = P_treat*np.ones((Nsim,))
    qseq = q_treat*np.ones((Nsim,))
    print(pseq)
    print(qseq)

    # additional information to save
    opt_dict = {}
    opt_dict["exp_settings"] = settings_str

    exp_data = exp.run_open_loop(
        ioloop,
        power_seq=pseq,
        flow_seq=qseq,
        runOpts=runOpts,
        devices=devices,
        prevTime=prevTime,
        opt_dict=opt_dict,
    )

    arduinoPI.close()

    # reconnect Arduino
    arduinoPI = serial.Serial(arduinoAddress, baudrate=38400, timeout=1)
    devices['arduinoPI'] = arduinoPI

# turn off plasma jet (programmatically)
ard_utils.sendInputsArduino(arduinoPI, 0.0, 0.0, dutyCycleIn, arduinoAddress)
arduinoPI.close()

if plot_data:
    import matplotlib.pyplot as plt

    fig, (ax1, ax2, ax3, ax4) = plt.subplots(4,1, figsize=(8,8), dpi=150, layout="constrained")
    ax1.plot(exp_data['Tsave'])
    ax1.set_ylabel('Maximum Surface\nTemperature ($^\circ$C)')
    ax2.plot(exp_data['Isave'])
    ax2.set_ylabel('Total Optical\nEmission Intensity\n(arb. units)')
    ax3.plot(exp_data['Psave'])
    ax3.set_ylabel('Power (W)')
    ax4.plot(exp_data['qSave'])
    ax4.set_ylabel('Carrier Gas\nFlow Rate (SLM)')
    ax4.set_xlabel('Time Step')
    plt.show()
    
print("Experiment complete!\n"+
    "################################################################################################################\n"+
    "IF FINISHED WITH EXPERIMENTS, PLEASE FOLLOW THE SHUT-OFF PROCEDURE FOR THE APPJ\n"+
    "################################################################################################################\n")
