# Kevin Moy, 7/24/2020
# Uses IEEE 13-bus system to scale loads and determine state space for RL agent learning
# Produces CSV of load names and load magnitudes in kW for later testing

import win32com.client
import pandas as pd
import os
import numpy as np
from generate_state_space import load_states

currentDirectory = os.getcwd()  # Will switch to OpenDSS directory after OpenDSS Object is instantiated!

MAX_NUM_CONFIG = 30
MIN_BUS_VOLT = 0.8
MAX_BUS_VOLT = 1.2

# Instantiate the OpenDSS Object
try:
    DSSObj = win32com.client.Dispatch("OpenDSSEngine.DSS")
except:
    print("Unable to start the OpenDSS Engine")
    raise SystemExit
print("OpenDSS Engine started\n")

# Set up the Text, Circuit, and Solution Interfaces
DSSText = DSSObj.Text
DSSCircuit = DSSObj.ActiveCircuit
DSSSolution = DSSCircuit.Solution

# Load in an example circuit
DSSText.Command = r"Compile 'C:\Program Files\OpenDSS\IEEETestCases\13Bus\IEEE13Nodeckt.dss'"

# Disable voltage regulators
DSSText.Command = "Disable regcontrol.Reg1"
DSSText.Command = "Disable regcontrol.Reg2"
DSSText.Command = "Disable regcontrol.Reg3"

loadNames = np.array(DSSCircuit.Loads.AllNames)
loadKwdf = pd.DataFrame(loadNames)

numConfig = 0
iters = 0
while numConfig < MAX_NUM_CONFIG:
    loadKws = load_states(loadNames, DSSCircuit, DSSSolution)

    if loadKws is not None:
        # print("Voltages within acceptable range")
        loadKwdf[numConfig+1] = loadKws
        numConfig += 1
    # else:
    #     # print("Voltages not within acceptable range [" + str(MIN_BUS_VOLT) + ", " + str(MAX_BUS_VOLT) +
    #     #       "] p.u., not saving")

    iters += 1

print("\nLoad configurations complete")
print("Total iterations to reach " + str(MAX_NUM_CONFIG) + ": " + str(iters))
loadKwdf.set_index(0, inplace=True)
loadKwdf.to_csv(currentDirectory + "\\loadkW.csv", index_label='Load Name')
print("\nsaved to "+ currentDirectory + "\\loadkW.csv")

