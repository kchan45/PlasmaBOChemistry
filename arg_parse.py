import argparse

data_file_label_default = "OL_multistep_LONG"
step_length_default = 30.0  # time to run experiment in seconds
P_max_default = 3.25  # max power setting for the treatment in Watts
P_min_default = 1.5  # min power setting for the treatment in Watts
P_step_default = 0.25 # step size of power in Watts
q_max_default = 6.5  # max flow setting for the treatment in standard liters per minute (SLM)
q_min_default = 2.5  # min flow setting for the treatment in standard liters per minute (SLM)
q_step_default = 0.5 # step size of flow rate in standard liters per minute
dist_treat_default = 5.0  # jet-to-substrate distance in mm
int_time_default = 12000 * 6  # integration time for spectrometer measurement in microseconds
ts_default = 1.0  # sampling time to take measurements in seconds
surface_default = "copper tape on glass" # surface material
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
    "-ps",
    "--P_step",
    type=float,
    default=P_step_default,
    help="The step size of the power setting for the treatment in Watts.",
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
    "-qs",
    "--q_step",
    type=float,
    default=q_step_default,
    help="The step size of the flow rate setting for the treatment in SLM.",
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
parser.add_argument(
    "-m",
    "--surface_material",
    type=str,
    default=surface_default,
    help="The surface material in which the plasma is impinging on. Assumed to be placed on top of the metal base plate.",
)