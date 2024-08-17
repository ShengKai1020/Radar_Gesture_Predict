from datetime import datetime
import os
import shutil
import sys

import numpy as np
from PyQt5 import QtWidgets, QtCore, QtGui

from KKT_Module.ksoc_global import kgl
from KKT_Module.Configs import SettingConfigs
from KKT_Module.SettingProcess.SettingProccess import SettingProc, ConnectDevice, ResetDevice
from KKT_Module.DataReceive.DataReciever import FeatureMapReceiver
import time


class RadarApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.running = False

    def initUI(self):
        self.setWindowTitle('Radar Object Detection')
        self.setGeometry(100, 100, 400, 300)

        self.startButton = QtWidgets.QPushButton('Start Detection', self)
        self.startButton.clicked.connect(self.startDetection)

        self.stopButton = QtWidgets.QPushButton('Stop Detection', self)
        self.stopButton.clicked.connect(self.stopDetection)
        self.stopButton.setEnabled(False)

        self.statusButton = QtWidgets.QPushButton('Status: Not detecting', self)
        self.statusButton.setStyleSheet('background-color: red')
        self.statusButton.setEnabled(False)

        self.energyLabel = QtWidgets.QLabel('Energy: 0', self)
        self.energyLabel.setAlignment(QtCore.Qt.AlignCenter)

        self.bellImage = QtWidgets.QLabel(self)
        self.bellImage.setAlignment(QtCore.Qt.AlignCenter)
        self.updateBellImage(0)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.startButton)
        self.layout.addWidget(self.stopButton)
        self.layout.addWidget(self.statusButton)
        self.layout.addWidget(self.energyLabel)
        self.layout.addWidget(self.bellImage)

        self.setLayout(self.layout)

    def startDetection(self):
        self.running = True
        self.startButton.setEnabled(False)
        self.stopButton.setEnabled(True)
        self.statusButton.setText('Detecting...')
        self.statusButton.setStyleSheet('background-color: yellow')

        self.thread = DetectionThread()
        self.thread.data_signal.connect(self.updateStatus)
        self.thread.start()

    def stopDetection(self):
        self.running = False
        self.startButton.setEnabled(True)
        self.stopButton.setEnabled(False)
        self.thread.stop()
        self.statusButton.setText('Status: Not detecting')
        self.statusButton.setStyleSheet('background-color: red')
        self.energyLabel.setText('Energy: 0')
        self.updateBellImage(0)

    def updateStatus(self, total_energy):
        self.energyLabel.setText(f'Energy: {total_energy}')
        if total_energy > 40000:
            self.statusButton.setStyleSheet('background-color: yellow')
            self.statusButton.setText('Status: Object Detected')
            self.updateBellImage(1)
        else:
            self.statusButton.setStyleSheet('background-color: red')
            self.statusButton.setText('Status: No Object')
            self.updateBellImage(0)

    def updateBellImage(self, detected):
        if detected:
            pixmap = QtGui.QPixmap('img/bell_on.png')
        else:
            pixmap = QtGui.QPixmap('img/bell_off.png')
        self.bellImage.setPixmap(pixmap.scaled(100, 100, QtCore.Qt.KeepAspectRatio))


class DetectionThread(QtCore.QThread):
    data_signal = QtCore.pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.running = True

    def run(self):
        connect()
        startSetting()
        self.startLoop()

    def stop(self):
        self.running = False

    def startLoop(self):
        R = FeatureMapReceiver(chirps=32)  # Receiver for getting RDI PHD map
        R.trigger(chirps=32)  # Trigger receiver before getting the data
        time.sleep(0.5)

        while self.running:  # 無限循環以獲取數據
            res = R.getResults()  # 獲取接收器數據

            if res is None:
                continue

            power = np.abs(res[0])
            total_energy = np.sum(power)  # 計算總能量

            self.data_signal.emit(total_energy)


def connect():
    connect = ConnectDevice()
    connect.startUp()  # Connect to the device
    reset = ResetDevice()
    reset.startUp()  # Reset hardware register

def startSetting():
    SettingConfigs.setScriptDir("K60168-Test-00256-008-v0.0.8-20230717_120cm")  # Set the setting folder name
    ksp = SettingProc()  # Object for setting process to setup the Hardware AI and RF before receive data
    ksp.startUp(SettingConfigs)  # Start the setting process

def main():
    kgl.setLib()
    kgl.ksoclib.switchLogMode(False)

    app = QtWidgets.QApplication(sys.argv)
    radarApp = RadarApp()
    radarApp.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
