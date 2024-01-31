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

# pickle import to save class data
try:
    import cPickle as pickle
except ModuleNotFoundError:
    import pickle
import argparse

## import user functions
from utils.run_options import RunOpts
import utils.thermal_camera as tc_utils
import utils.async_measurement as ameas
import utils.arduino as ard_utils
from utils.oscilloscope import Oscilloscope
from utils.experiments import Experiment

## import picoscope settings
from picoscope_setup import *

plot_data = True  # [True/False] whether or not to plot the (2-input, 2-output) data after an experiment

data_file_label_default = "OL_multistep_TEST"
step_length_default = 30.0  # time to run experiment in seconds
P_max_default = 3.25  # max power setting for the treatment in Watts
P_min_default = 1.5  # min power setting for the treatment in Watts
q_max_default = 6.25  # max flow setting for the treatment in standard liters per minute (SLM)
q_min_default = 2.0  # min flow setting for the treatment in standard liters per minute (SLM)
dist_treat_default = 5.0  # jet-to-substrate distance in mm
int_time_default = 12000 * 6  # integration time for spectrometer measurement in microseconds
ts_default = 1.0  # sampling time to take measurements in seconds
# NOTE: sampling time should be greater than integration time by roughly double

################################################################################
## Set up argument parser
################################################################################
parser = argparse.ArgumentParser(description="Experiment Settings")
parser.add_argument(
    "-f",
    "--file_label",
    type=str,
    default=data_file_label_default,
    help="The extra string to append to the save file.",
)
parser.add_argument(
    "-s",
    "--step_length",
    type=float,
    default=step_length_default,
    help="The the length of a step change in seconds.",
)
parser.add_argument(
    "-px",
    "--P_max",
    type=float,
    default=P_max_default,
    help="The maximum power setting for the treatment in Watts.",
)
parser.add_argument(
    "-pn",
    "--P_min",
    type=float,
    default=P_min_default,
    help="The minimum power setting for the treatment in Watts.",
)
parser.add_argument(
    "-qx",
    "--q_max",
    type=float,
    default=q_max_default,
    help="The maximum flow rate setting for the treatment in SLM.",
)
parser.add_argument(
    "-qn",
    "--q_min",
    type=float,
    default=q_min_default,
    help="The minimum flow rate setting for the treatment in SLM.",
)
parser.add_argument(
    "-d",
    "--dist_treat",
    type=float,
    default=dist_treat_default,
    help="The jet-to-substrate distance in millimeters.",
)
parser.add_argument(
    "-it",
    "--int_time_treat",
    type=float,
    default=int_time_default,
    help="The integration time for the spectrometer in microseconds.",
)
parser.add_argument(
    "-ts",
    "--sampling_time",
    type=float,
    default=ts_default,
    help="The sampling time to take measurements in seconds.",
)

args = parser.parse_args()
file_label = args.file_label
step_length = args.step_length
P_max = args.P_max
P_min = args.P_min
q_max = args.q_max
q_min = args.q_min
dist_treat = args.dist_treat
int_time_treat = args.int_time_treat
ts = args.sampling_time

settings_str = (
    f"The settings for this treatment are:\n"
    f"Append to File:            _{file_label}\n"
    f"Step Length (s):            {step_length}\n"
    f"Max Power (W):              {P_max}\n"
    f"Min Power (W):              {P_min}\n"
    f"Max Flow Rate (SLM):        {q_max}\n"
    f"Min Flow Rate (SLM):        {q_min}\n"
    f"Separation Distance (mm):   {dist_treat}\n"
    f"Integration Time (us):      {int_time_treat}\n"
    f"Sampling Time (s):          {ts}\n"
)
print(settings_str)

if ts < 2 * int_time_treat * 1e-6:
    print(
        "Integration time too large! Please modify the integration time and/or the sampling time such that the sampling time is greater than double the integration time."
    )
    exit(1)

cfm = input("Confirm these are correct [Y/n]: ")
if cfm in ["Y", "y"]:
    pass
else:
    quit()

################################################################################
## Startup/prepare APPJ
################################################################################

## collect time stamp
timeStamp = datetime.now().strftime("%Y_%m_%d_%H" + "h%M" "m%S" + "s")
print("Timestamp for save files: ", timeStamp)
Nrep = 1

# configure run options
runOpts = RunOpts()
runOpts.collectData = True  # option to collect two-input, two-output data (power, flow rate); (max surface temperature, total intensity)
runOpts.collectEntireSpectra = True  # option to collect full intensity spectra
runOpts.collectOscMeas = (
    True  # option to collect oscilloscope measurements (using PicoScope)
)
runOpts.collectSpatialTemp = False  # option to collect spatial temperature (defined as temperature from 12 pixels away from max in the four cardinal directions)
# save options; correspond to the collection (two-input, two-output data is always saved)
runOpts.saveSpectra = True
runOpts.saveOscMeas = True
runOpts.saveSpatialTemp = False  # limited functionality
runOpts.saveEntireImage = True
runOpts.tSampling = ts  # set the sampling time of the measurements

## Set startup values
dutyCycleIn = 100
powerIn = P_min
flowIn = q_min

# set save location
directory = os.getcwd()
split_cwd = directory.split("/")
repo = split_cwd[-1]
saveDir = directory + f"/../{repo}-ExperimentalData/" + timeStamp + f"_{file_label}/"
print("\nData will be saved in the following directory:")
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
spec.integration_time_micros(int_time_treat)  ## change integration time (units of microseconds)

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
input("Ensure plasma has ignited and press Return to begin.\n")

## Startup asynchronous measurement
if os.name == "nt":
    ioloop = asyncio.ProactorEventLoop()  # for subprocess' pipes on Windows
    asyncio.set_event_loop(ioloop)
else:
    ioloop = asyncio.get_event_loop()
# run once to initialize measurements
prevTime = (time.time() - s) * 1e3
tasks, runTime = ioloop.run_until_complete(
    ameas.async_measure(arduinoPI, osc, spec, runOpts)
)
print("measurement devices ready!")
s = time.time()

prevTime = (time.time() - s) * 1e3
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
# create input sequences
uvec1 = np.arange(start=P_min, stop=P_max, step=0.25)  # for power
uvec2 = np.arange(start=q_min, stop=q_max, step=0.25)  # for flow rate
uu1, uu2 = np.meshgrid(uvec1, uvec2)
uvec1 = uu1.reshape(-1,)
uvec2 = uu2.reshape(-1,)
rng = np.random.default_rng(0)
rng.shuffle(uvec1)
pseq = np.copy(uvec1)
p_nom = (P_max+P_min)/2
pseq = np.insert(pseq, 0, [0.0, p_nom, p_nom, p_nom])
rng.shuffle(uvec2)
qseq = np.copy(uvec2)
q_nom = (q_max+q_min)/2
qseq = np.insert(qseq, 0, [0.0, q_nom, q_nom, q_nom])
print(pseq)
print(qseq)
n_steps = int(step_length / runOpts.tSampling)
pseq = [0.0, 2.0]
qseq = [0.0, 2.0]

pseq = np.repeat(pseq, n_steps).reshape(-1,)
qseq = np.repeat(qseq, n_steps).reshape(-1,)
print(pseq.shape[0])

Nsim = len(pseq)

exp = Experiment(Nsim, saveDir)

f = open(saveDir + "notes.txt", "a")
f.write(settings_str)

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

# turn off plasma jet (programmatically)
ard_utils.sendInputsArduino(arduinoPI, 0.0, 0.0, dutyCycleIn, arduinoAddress)
arduinoPI.close()

if plot_data:
    import matplotlib.pyplot as plt

    fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=(8, 8), dpi=150)
    ax1.plot(exp_data["Tsave"])
    ax1.set_ylabel("Maximum Surface\nTemperature ($^\circ$C)")
    ax2.plot(exp_data["Isave"])
    ax2.set_ylabel("Total Optical\nEmission Intensity\n(arb. units)")
    ax3.plot(exp_data["Psave"])
    ax3.set_ylabel("Power (W)")
    ax4.plot(exp_data["qSave"])
    ax4.set_ylabel("Carrier Gas\nFlow Rate (SLM)")
    ax4.set_xlabel("Time Step")
    plt.tight_layout()
    plt.show()

print(
    "Experiment complete!\n"
    + "################################################################################################################\n"
    + "IF FINISHED WITH EXPERIMENTS, PLEASE FOLLOW THE SHUT-OFF PROCEDURE FOR THE APPJ\n"
    + "################################################################################################################\n"
)
