# Code for running APPJ experiments

This code was used for the open-loop collection of data from the atmospheric pressure plasma jet (APPJ).

## File Descriptions

`utils` provides some general utilities for running experiments. Additional details regarding the files are detailed as follows:

  * `APPJPythonFunctions.py` contains most of the functions that allow for data retrieval from the APPJ
  * `experiments.py` contains an `Experiments` class that can be used to run open-loop (no controller) or closed-loop (with controller) experiments. This repository only required the use of the open-loop data collection functionality. Open loop data may be provided by sending a sequence of power and/or flow rate inputs.
  * `uvcRadiometry.py` and `uvtypes.py` are additional files that are used to obtain measurements from the thermal camera
  * `uvcRadiometry_test.py` is used to test operation of the thermal camera. This file should be run in the `utils` directory

`appj_requirements.txt` contains the necessary Python dependencies/libraries that are needed to operate the data acquisition from the APPJ. More information regarding the Python dependencies and connection from the APPJ setup to your computer may be found in this repository.

`appj_warmup.py` is used to warm up the APPJ. Generally, it is recommended to run the APPJ at some nominal settings for 10-15 minutes to allow for consistent data acquisitions afterwards. This script will do this as long as your device is set up properly.

`run_exp.py` is the script used to run an experiment and perform the data acquisition

`spectroscopyLive.py` is a script to test the spectroscopy (optical emission spectra) measurement. It requires an additional argument when you run the `python3 spectroscopyLive.py [time\s]` command. The additional argument is how long you would like to run the test in terms of seconds, i.e., 100 would run the test for roughly 100 seconds.

## How to run an experiment

**Before running any experiments on the plasma jet, experimentalists should acquire the appropriate training to work with the plasma jet.**

1. The gas and amplifier will need to be turned on according to the training and instructions provided in the laboratory manual.
2. The plasma jet should be warmed up using `appj_warmup.py`.
3. Experiments can be run using `run_exp.py`. For this repository, we modified treatment time, power, flow rate, and separation distance. These settings may be specified to the script in order to set the appropriate values to the plasma jet. There are two ways to modify these settings:

    1. [Recommended] specify the values as command-line arguments to the call to the Python script, e.g.:
    ```
    python3 run_exp.py -n 0 -t 30 -p 2.0 -q 3.0 -d 4.0
    ```
    OR
    ```
    python3 run_exp.py --sample_num 0 --time_treat 30 --P_treat 2.0 --q_treat 3.0 --dist_treat 4.0
    ```
    for a treatment time of 30 seconds, power of 2 Watts, flow rate of 3 SLM, treatment distance of 3 mm. The additional argument `-n` or `--sample_num` describes the sample number of the collected data. This can be used to keep track of the experiments.
    *Note: Treatment distance must be adjusted manually; the amplifier should be turned off when doing so.*
    
    2. Specify the values by changing Lines 42-48 in the `run_exp.py` script.
    
If the settings are not modified using the above, then the default values for each setting are used (see Lines 42-48). It is not necessary to set each of the settings if they do not differ from the default values, i.e., `python3 run_exp.py -n 0 -t 30 -q 3.0` is equivalent to `python3 run_exp.py -n 0 -t 30 -q 3.0 -p 2.0 -d 4.0` since the default values of power and separation distance are 2 W and 4 mm, respectively.
    
**[UPDATE 2023-06-11] Additional features to change the integration time of the spectrometer and the sampling time of the measurement collection have been added to the command-line interface. The flags to changes these settings are `-it` and `-ts` or `--int_time` and `--sampling_time` for integration time (in units of microseconds) and sampling time (in units of seconds), respectively.**

i.e., the command with all options is:
```
python3 run_exp.py -n 0 -t 30 -p 2.0 -q 3.0 -d 4.0 -it 50000 -ts 1
```
OR
```
python3 run_exp.py --sample_num 0 --time_treat 30 --P_treat 2.0 --q_treat 3.0 --dist_treat 4.0 --int_time 50000 --sampling_time 1
```

