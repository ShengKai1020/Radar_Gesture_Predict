from KKT_Module.ksoc_global import kgl
from KKT_Module.Configs import SettingConfigs
from KKT_Module.SettingProcess.SettingProccess import SettingProc, ConnectDevice, ResetDevice
from KKT_Module.DataReceive.DataReciever import RawDataReceiver, HWResultReceiver, FeatureMapReceiver
import time

def connect():
    connect = ConnectDevice()
    connect.startUp()                       # Connect to the device
    reset = ResetDevice()
    reset.startUp()                         # Reset hardware register

def startSetting():
    SettingConfigs.setScriptDir("K60168-Test-00256-008-v0.0.8-20230717_120cm")  # Set the setting folder name
    ksp = SettingProc()                 # Object for setting process to setup the Hardware AI and RF before receive data
    ksp.startUp(SettingConfigs)             # Start the setting process
    # ksp.startSetting(SettingConfigs)        # Start the setting process in sub_thread

def startLoop():
    # kgl.ksoclib.switchLogMode(True)
    # R = RawDataReceiver(chirps=32)

    # Receiver for getting Raw data
    R = FeatureMapReceiver(chirps=32)       # Receiver for getting RDI PHD map
    # R = HWResultReceiver()                  # Receiver for getting hardware results (gestures, Axes, exponential)
    # buffer = DataBuffer(100)                # Buffer for saving latest frames of data
    R.trigger(chirps=32)                             # Trigger receiver before getting the data
    time.sleep(0.5)
    print('# ======== Start getting gesture ===========')
    while True:                             # loop for getting the data
        res = R.getResults()                # Get data from receiver
        if res is None:
            continue
        print('data = {}'.format(res))          # Print results
        # time.sleep(0.05)
        '''
        Application for the data.
        '''

def main():
    kgl.setLib()

    # kgl.ksoclib.switchLogMode(True)

    connect()                               # First you have to connect to the device

    startSetting()                         # Second you have to set the setting configs

    startLoop()                             # Last you can continue to get the data in the loop

if __name__ == '__main__':
    main()
