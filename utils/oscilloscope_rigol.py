import usbtmc
import numpy as np


class Oscilloscope:
    def __init__(self):
        pass

    # Method that initializes the oscilloscope
    def initialize(self, retry=10):
        oscilloscopeStr = ""
        nAttempts = 0
        while (oscilloscopeStr == "") & (nAttempts < retry):
            try:
                instr = usbtmc.Instrument(0x1AB1, 0x04CE)
                instr.open()
                oscilloscopeStr = instr.ask("*IDN?\n")
                # rm = visa.ResourceManager()
                # devices = rm.list_resources()
                # instr = rm.open_resource(devices[1])
                # oscilloscopeStr = instr.query("*IDN?\n")
            except Exception as e:
                nAttempts += 1
                print("{} in oscilloscope check loop".format(e))
                # If initialization fails, close and restart the oscilloscope connection
                instr.close()

        print("Oscilloscope info: {}".format(oscilloscopeStr))
        print("Oscilloscope timeout: {}".format(instr.timeout))

        return instr

    # Method that records the measurements
    def measurement(self, instr):
        # Measurement from channel 1 (voltage)
        instr.write(":MEAS:SOUR CHAN1")
        Vrms = float(instr.ask("MEAS:ITEM? PVRMS"))
        # Vmax=float(instr.ask("MEAS:VMAX?"))
        # Vp2p = float(instr.ask("MEAS:VPP?"))
        # Freq=float(instr.ask("MEAS:FREQ?"))
        # o.Vwave=oscilloscope.ask(':WAV:DATA?')

        # Measurement from channel 2 (current)
        instr.write(":MEAS:SOUR CHAN2")
        Irms = float(instr.ask("MEAS:ITEM? PVRMS"))
        # Imax = float(instr.ask("MEAS:VMAX?"))*1000
        # Ip2p=float(instr.ask("MEAS:VPP?"))*1000
        # o.Iwave=oscilloscope.ask(':WAV:DATA?')

        # Measurement from math channel (V*I)
        instr.write(":MEAS:SOUR MATH")
        Pavg = float(instr.ask("MEAS:VAVG?"))
        # Prms=float(instr.ask("MEAS:ITEM? PVRMS"))
        Prms = Vrms * Irms

        # out = np.array([Vrms, Vmax, Vp2p, Freq, Irms, Imax, Ip2p, Pavg, Prms])
        out = np.array([Vrms, Irms, Pavg, Prms])

        return out
