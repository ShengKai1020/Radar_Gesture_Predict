import numpy as np
import pyqtgraph as pg
from PySide2 import QtWidgets, QtCore
from KKT_Module.KKTGraph.StemPlot import StemPlot
import time

##=====================================================================================
class DrawingRAW(pg.LayoutWidget):
    __Stemplot = None
    def __init__(self, title, chirp=32, parent=None, enableMenu=False):
        super(DrawingRAW, self).__init__()
        self._drawingTitle = title
        self._MaxX = chirp*128+200
        self._enableMenu = enableMenu
        self.__setupUI()

    def __setupUI(self):
        self.__Stemplot = StemPlot(self._drawingTitle, enableMenu=self._enableMenu)
        self.__Stemplot.setAxisRange([1, self._MaxX], [-2**15, 2**15])
        self.__Stemplot.setCurvepointSymbolSize(1)
        self.__Stemplot.setCurvepointSymbolVisible(False)
        self.__Stemplot.scale(2,3)
        self.addWidget(self.__Stemplot)

    def setYData(self, ydata):
        self.__Stemplot.setYData(ydata)

    def setAxisRange(self, Xrange, Yrange):
        self.__Stemplot.setAxisRange(Xrange, Yrange)

class RawDataGraph(pg.LayoutWidget):
    def __init__(self, chirp=32, parent=None):
        super(RawDataGraph, self).__init__(parent)
        self._chirp = chirp
        self.RawGraphs = []
        self._lb_fps = None
        self.__setupUI()
        # self.enableWidget(True)

    def enableWidget(self, FPS=False):
        if FPS:
            self._lb_fps = QtWidgets.QLabel('{:.2f} fps.'.format(0))
            layout_FPS = self.addLayout(0, 0)
            layout_FPS.addWidget(self._lb_fps)
            self.lastTime = None

    def setChirp(self, chirp):
        self._chirp = chirp

    def __setupUI(self):
        self.CH1 = DrawingRAW('CH1', self._chirp)
        self.CH2 = DrawingRAW('CH2', self._chirp)
        layout_graph = self.addLayout(1,0)
        layout_graph.addWidget(self.CH1)
        layout_graph.addWidget(self.CH2)

    def setData(self, raw1, raw2):
        self.CH1.setYData(raw1)
        self.CH2.setYData(raw2)
        self._updatedFPS()

    def _updatedFPS(self):
        if self._lb_fps is None:
            return

        if self.lastTime is None:
            self.lastTime = time.time()
            self.g_fps = None
        else:
            now = time.time()
            dt = now - self.lastTime
            self.lastTime = now
            g_fps = 1.0 / dt
            self._lb_fps.setText(" {:.2f} fps.".format(g_fps))

class FeatVectorGraph(pg.LayoutWidget):
    def __init__(self, chirp=32, parent=None):
        super(FeatVectorGraph, self).__init__(parent)
        self._chirp = chirp
        self.RawGraphs = []
        self._lb_fps = None
        self.__setupUI()
        # self.enableWidget(True)

    def enableWidget(self, FPS=False):
        if FPS:
            self._lb_fps = QtWidgets.QLabel('{:.2f} fps.'.format(0))
            layout_FPS = self.addLayout(0, 0)
            layout_FPS.addWidget(self._lb_fps)
            self.lastTime = None

    def __setupUI(self):
        self.CH1 = DrawingRAW('CH1', self._chirp)
        self.CH2 = DrawingRAW('CH2', self._chirp)
        layout_graph = self.addLayout(1,0)
        layout_graph.addWidget(self.CH1)
        layout_graph.addWidget(self.CH2)

    def setData(self, raw1, raw2):
        self.CH1.setYData(raw1)
        self.CH2.setYData(raw2)
        self._updatedFPS()

    def setCh1AxisRange(self, Xrange, Yrange):
        self.CH1.setAxisRange(Xrange, Yrange)

    def setCh2AxisRange(self, Xrange, Yrange):
        self.CH2.setAxisRange(Xrange, Yrange)

    def _updatedFPS(self):
        if self._lb_fps is None:
            return

        if self.lastTime is None:
            self.lastTime = time.time()
            self.g_fps = None
        else:
            now = time.time()
            dt = now - self.lastTime
            self.lastTime = now
            g_fps = 1.0 / dt
            self._lb_fps.setText(" {:.2f} fps.".format(g_fps))


 
##=============================  Unit Testing  ========================================
if __name__ == '__main__':
    import sys

    def data_update():
        global g_StempTemp
        y = np.random.randint(-2**11, 2**11, size=(4096))
        g_StempTemp.setData(y, y)

    # g_StempTemp = None

    app = QtWidgets.QApplication([])
    app.setAttribute(QtCore.Qt.AA_Use96Dpi)

    win = QtWidgets.QMainWindow()
    win.resize(600,300)

    g_StempTemp = RawDataGraph(64)

    win.setCentralWidget(g_StempTemp)
    win.show()
    win.setWindowTitle('Unit test')

    qtimer = QtCore.QTimer()
    qtimer.timeout.connect(data_update)
    qtimer.start(50)

    app.exec_()
    qtimer.stop()