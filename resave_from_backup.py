# python script to save segregated data files 
# in the event that a JSON file was saved but 
# the script errored out during segregated save

from utils.experiments import *
from utils.run_options import RunOpts
import json

plot_data = True
# save_folder = "/home/mesbahappj/Desktop/PlasmaBOChemistry-ExperimentalData/2024_02_01_11h04m59s_OL_multistep_SHORT"
# save_folder = "/home/mesbahappj/Desktop/PlasmaBOChemistry-ExperimentalData/2024_02_01_13h14m12s_OL_multistep_LONG"
# save_folder = "/home/mesbahappj/Desktop/PlasmaBOChemistry-ExperimentalData/2024_02_05_18h20m01s_OL_multistep_SHORT"
# save_folder = "/home/mesbahappj/Desktop/PlasmaBOChemistry-ExperimentalData/2024_02_06_16h19m42s_OL_multistep_SHORT"
# save_folder = "/home/mesbahappj/Desktop/PlasmaBOChemistry-ExperimentalData/2024_02_06_17h56m02s_OL_multistep_LONG"
save_folder = "/home/mesbahappj/Desktop/PlasmaBOChemistry-ExperimentalData/2024_02_28_14h47m22s-Sample10"

# copy from settings used during data collection
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
runOpts.tSampling = 0.5  # set the sampling time of the measurements

# grab exp_data saved in backup
with open(save_folder+"/Backup/OL_data_0.json") as f:
    exp_data = json.load(f)

# save
exp_data_saver(exp_data, save_folder+"/", "OL_data_0", runOpts)


# plot
if plot_data:
    import matplotlib.pyplot as plt

    fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=(8, 8), dpi=150)
    ax1.plot(exp_data["Tsave"][30:])
    ax1.set_ylabel("Maximum Surface\nTemperature ($^\circ$C)")
    ax2.plot(exp_data["Isave"][30:])
    ax2.set_ylabel("Total Optical\nEmission Intensity\n(arb. units)")
    ax3.plot(exp_data["Psave"][30:])
    ax3.set_ylabel("Power (W)")
    ax4.plot(exp_data["qSave"][30:])
    ax4.set_ylabel("Carrier Gas\nFlow Rate (SLM)")
    ax4.set_xlabel("Time Step")
    plt.tight_layout()
    plt.show()
