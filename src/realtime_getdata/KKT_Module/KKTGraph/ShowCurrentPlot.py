from PySide2 import QtWidgets, QtCore, QtGui
import pyqtgraph as pg
import numpy as np


class CurrentDistance(pg.PlotWidget):
    pg.setConfigOption('foreground', 'k')  # Default foreground color for text, lines, axes, etc.
    pg.setConfigOption('background', None)  # Default background for GraphicsView.
    pg.setConfigOptions(antialias=True)  # Draw lines with smooth edges at
    def __init__(self):
        super(CurrentDistance, self).__init__()
        self.peak = np.zeros(3600)
        self.x =(np.asarray([i for i in range(3600)])-3600)/20
        self.XRange =[-3600/20-1, 0]
        self.setRange(xRange=[-3600/20-1, -1], yRange=[5, 70])
        self.setLimits(xMax = 0, xMin=-180, yMin=0)
        self.setupGUI()
        self.proportion = None
        pass

    def setupGUI(self):
        self.current = pg.PlotCurveItem(pen={'color':'b', 'width': 3})
        self.getAxis('left').setLabel('Distance (cm)')
        self.getAxis('bottom').setLabel('time (s)')
        self.setMenuEnabled(False)
        self.showGrid(x = False, y = True, alpha = 0.3)
        self.current.setData(x=self.x, y=self.peak)
        self.addItem(self.current)
        # self.sigRangeChanged.connect(lambda :self.fixAxis())


        pass
    def initPeak(self):
        self.XRange[0] = self.getAxis('bottom').range[0]
        self.setYData(0)

    def setYData(self, data):
        self.peak = np.roll(self.peak, -1)
        self.peak[-1] = self.proportion[data]
        self.current.setData(x=self.x ,y=self.peak)
        self.setYRange(max = np.max(self.peak) + 20, min = 5)
        if np.abs(self.XRange[0] - self.getAxis('bottom').range[0]) > 3:
            self.setXRange(max=self.XRange[1], min=self.getAxis('bottom').range[0])
            self.XRange[0] = self.getAxis('bottom').range[0]

    def setTimes(self, time_per_sec):
        buffer_len = 180*time_per_sec
        self.peak = np.zeros(buffer_len)
        self.x = np.linspace(-180, 0, buffer_len)
        self.XRange = [-180, 0]


    def fixAxis(self):
        self.setXRange(max=self.XRange[1], min=self.XRange[0])


    def setProportion(self, proportion):
        self.proportion = proportion


if __name__ == '__main__':
    def data_update():
        global g_map
        # time.sleep(0.05)
        l = np.random.randint(0,60, 1)
        g_map.setYData(l)


    # g_map = None
    app = QtWidgets.QApplication([])
    win = QtWidgets.QMainWindow()
    win.resize(800,600)

    g_map = CurrentDistance()


    win.setCentralWidget(g_map)
    win.setWindowTitle('Unit test')
    win.show()

    qtimer = QtCore.QTimer()
    qtimer.timeout.connect(data_update)
    qtimer.start(40)
    app.exec_()
    qtimer.stop()