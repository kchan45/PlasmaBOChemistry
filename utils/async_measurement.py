# asynchronous measurement

import asyncio
import time
import cv2
import numpy as np

from utils.thermal_camera import *
from utils.arduino import *


async def async_measure(ard, osc, spec, runOpts):
    """
    function to get measurements from all devices asynchronously to optimize
    time to get measurements

    Inputs:
    ard         Arduino device reference
    spec        Spectrometer device reference
    runOpts     run options; if data should be saved, then measurements will be
                taken, otherwise the task will return None

    Outputs:
    tasks        completed list of tasks containing data measurements; the first
                task obtains temperature measurements, second task obtains
                spectrometer measurements, third task gets oscilloscope
                measurements, and the fourth (final) task gets embedded
                measurements from the Arduino output
    runTime     run time to complete all tasks
    """
    # create list of tasks to complete asynchronously
    tasks = [
        asyncio.create_task(async_get_temp(runOpts)),
        asyncio.create_task(async_get_spectra(spec, runOpts)),
        asyncio.create_task(async_get_osc(osc, runOpts)),
        asyncio.create_task(async_get_emb(ard, runOpts)),
    ]

    startTime = time.time()
    await asyncio.wait(tasks)
    # await asyncio.gather(*tasks)
    endTime = time.time()
    runTime = endTime - startTime
    # print time to complete measurements
    print("...completed data collection tasks after {} seconds".format(runTime))
    return tasks, runTime


async def async_get_temp(runOpts):
    """
    asynchronous definition of surface temperature measurement. Assumes the
    camera device has already been initialized. Also can include spatial
    temperature measurements. If spatial temperatures are not desired, then the
    spatial measurements output by this function are -300.

    Inputs:
    runOpts     run options
    **assumes thermal camera device has been successfully opened prior

    Outputs:
    Ts        surface temperature (max temperature from thermal camera) in Celsius
    Ts2        average spatial temperature from 2 pixels away from Ts in Celsius
    Ts3     average spatial temperature from 12 pixels away from Ts in Celsius
    data    raw data matrix of the image captured
    if data collection is specified otherwise, outputs None
    """
    if runOpts.collectData:
        # run the data capture
        run = True
        while run:
            Ts_max, Ts_spatial, img_data = getSurfaceTemperature(True, True)
            run = False
        # print('temperature measurement done!')
        # return [Ts, Ts2, Ts3, data]
        return [Ts_max, *Ts_spatial, img_data]
    else:
        return None


async def async_get_spectra(spec, runOpts):
    """
    asynchronous definition of optical emission spectra data

    Inputs:
    spec         Spectrometer device
    runOpts     run options

    Outputs:
    totalIntensity        total intensity measurement
    intensitySpectrum    intensity spectrum
    wavelengths            wavelengths that correspond to the intensity spectrum
    if data collection is specified otherwise, outputs None
    """
    if runOpts.collectData and spec is not None:
        intensitySpectrum = spec.intensities()
        meanShift = np.mean(intensitySpectrum[-20:-1])
        intensitySpectrum = intensitySpectrum - meanShift
        totalIntensity = sum(intensitySpectrum[20:])

        if runOpts.collectEntireSpectra:
            wavelengths = spec.wavelengths()
        else:
            wavelengths = None
        # print('spectra recorded!')
        return [totalIntensity, intensitySpectrum, wavelengths, meanShift]
    else:
        return None


async def async_get_emb(dev, runOpts, prevTime=0.0):
    """
    asynchronous definition to get embedded measurements from the Arduino
    (microcontroller)

    Inputs:
    dev         device object for Arduino
    runOpts     run options

    Outputs:
    Outputs:
    Is            embedded surface intensity measurement
    U            inputs (applied peak to peak Voltage, frequency, flow rate)
    x_pos        X position
    y_pos        Y position
    dsep        separation distance from jet tip to substrate (Z position)
    T_emb        embedded temperature measurement
    P_emb        embedded power measurement
    Pset        power setpoint
    Dc            duty cycle
    elec        electrical measurements (embedded voltage and current)
    if data collection is specified otherwise, outputs None
    """
    if runOpts.collectEmbedded and dev is not None:
        # set default values for data/initialize data values
        Is = 0
        U = [0, 0, 0]  # inputs (applied Voltage, frequency, flow rate)
        x_pos = 0
        y_pos = 0
        dsep = 0
        T_emb = 0
        elec = [0, 0]  # electrical measurements (embedded voltage and current)
        P_emb = 0
        Pset = 0
        Dc = 0

        # run the data capture
        run = True
        while run:
            try:
                # dev.reset_input_buffer()
                # dev.readline()
                line = dev.readline().decode("ascii")
                if is_line_valid(line):
                    # print(line)
                    data = line.split(",")
                    timeStamp = float(data[0])
                    if True:
                        # if (timeStamp-prevTime)/1e3 >= runOpts.tSampling-0.025:
                        run = False
                        # data read from line indexed as programmed on the Arduino
                        V = float(data[1])  # p2p Voltage
                        f = float(data[2])  # frequency
                        q = float(data[3])  # Helium flow rate
                        dsep = float(data[4])  # Z position
                        Dc = float(data[5])  # duty cycle
                        Is = float(data[6])  # embedded intensity
                        V_emb = float(data[7])  # embedded voltage
                        T_emb = float(data[8])  # embedded temperature
                        I_emb = float(data[9])  # embedded current
                        x_pos = float(data[10])  # X position
                        y_pos = float(data[11])  # Y position
                        # q2 = float(data[12])        # Oxygen flow rate
                        Pset = float(data[13])  # power setpoint
                        P_emb = float(data[14])  # embedded power

                        U = [V, f, q]
                        elec = [V_emb, I_emb]
                else:
                    print("CRC8 failed. Invalid line!")
            except Exception as e:
                print(e)
                pass
        print(line)
        # print('embedded measurement done!')
        return np.array(
            [timeStamp, Is, *U, x_pos, y_pos, dsep, T_emb, P_emb, Pset, Dc, *elec]
        )
    else:
        return None


async def async_get_osc(osc, runOpts):
    """asynchronous definition to get embedded measurements from the Arduino
    (microcontroller)

    Inputs:
    osc         custom object for oscilloscope
    runOpts     run options

    Outputs:
    t            time vector for the data collected
    ch_data      dictionary of data from each channel
    if data collection is specified otherwise, outputs None
    """
    if runOpts.collectOscMeas and osc is not None:
        t, ch_datas = osc.collect_data_streaming()
        return [t, ch_datas]
    else:
        return None
