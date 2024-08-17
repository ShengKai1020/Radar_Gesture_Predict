import numpy as np
import pyqtgraph as pg
from PySide2 import QtGui, QtCore, QtWidgets


class StemPlot(pg.PlotWidget):
    def __init__(self, ptitle="Stem Plot Example", enableMenu=False):
        pg.setConfigOption('foreground', 'k')   # Default foreground color for text, lines, axes, etc.
        pg.setConfigOption('background', (0,0,0,0))  # Default background for GraphicsView.
        pg.setConfigOptions(antialias=True)     # Draw lines with smooth edges at the cost of reduced performance.
        super(StemPlot, self).__init__(enableMenu=enableMenu, title=ptitle)
        # pg.PlotWidget.__init__(self, enableMenu=False, title=ptitle)

        self.curvestem = None
        self.curvepoint = None
        self.__SymbolSize = 8
        self.__IsDrawPoint = True
        self.scale(3,4)

    def __creatCurve(self):

        if self.curvestem != None:
            self.removeItem(self.curvestem)

        if self.__IsDrawPoint == True and self.curvepoint != None:
            self.removeItem(self.curvepoint)

        x = np.arange(0,1)
        y = np.linspace(1, 1, 1)

        self.curvestem = self.plot(np.repeat(x, 2), np.dstack((np.zeros(y.shape[0], dtype=int), y)).flatten(), pen=pg.mkPen('b', width=0.5), connect='pairs', name='Stems')

        if self.__IsDrawPoint == True:
            self.curvepoint = self.plot(x, y, pen=None, symbol='o', symbolPen='b', symbolBrush=QtGui.QBrush(QtGui.QColor(20, 20, 200)), symbolSize=self.__SymbolSize, name='Points')
        

    def setAxisRange(self, xaxisrange, yaxisrange):
        self.setXRange(xaxisrange[0], xaxisrange[1], padding=.01)
        self.setYRange(yaxisrange[0], yaxisrange[1], padding=.02)


    def setYData(self, ydata):
        if self.curvestem == None:
            self.__creatCurve()

        x = np.arange(0, len(ydata))

        if self.__IsDrawPoint == True:
            self.curvepoint.setData(x, ydata)

        newx = np.insert(x.reshape(-1, 1), 1, x, axis=1).flatten()
        newy = np.insert(ydata.reshape(-1, 1), 0, 0, axis=1).flatten()
        self.curvestem.setData(newx, newy)

    def clearData(self):
        if self.curvestem != None:
            self.removeItem(self.curvestem)
            self.curvestem = None

        if self.curvepoint != None:
            self.removeItem(self.curvepoint)
            self.curvepoint = None

    def setCurvepointSymbolSize(self, size):
        self.__SymbolSize = size

    def setCurvepointSymbolVisible(self, isVisible):
        self.__IsDrawPoint = isVisible


##===================================  Unit Testing  ==============================================##


def data_update():
    global stempw
    global count

    y = np.random.randint(100, size=(16))
    count += 1
    if count % 2 == 0:
        stempw.clearData()
    else:
        stempw.setYData(y)


## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys

    count = 0

    app = QtWidgets.QApplication([])
    app.setAttribute(QtCore.Qt.AA_Use96Dpi)

    win = QtWidgets.QMainWindow()
    win.resize(600,400)

    w1 = pg.LayoutWidget()
    win.setCentralWidget(w1)
    win.show()
    win.setWindowTitle('pyqtgraph : ImageView')

    stempw = StemPlot()
    stempw.setCurvepointSymbolSize(1)
    stempw.setAxisRange([-1, 16], [0, 100])
    w1.addWidget(stempw, row=0, col=0)

    qtimer = QtCore.QTimer()
    # qtimer.timeout.connect(data_update)
    # qtimer.start(1000)
    data_update()

    if sys.flags.interactive != 1 or not hasattr(QtCore, 'PYQT_VERSION'):
       QtWidgets.QApplication.instance().exec_()
