import pyqtgraph as pg
import numpy as np
from PySide2 import QtWidgets,QtCore

class Histogram(pg.PlotWidget):
    def __init__(self):
        super(Histogram, self).__init__()
        self.Bar = None
        self.setXRange(-1, 1, padding=0.15)
        self.setYRange(0, 100, padding=0.01)
        self._stepUI()
        return
    def _stepUI(self):
        self.Bar = pg.PlotCurveItem()
        self.addItem(self.Bar)
        pass

    def setData(self, arry):
        y1, x = np.histogram(arry)
        self.Bar.setData(x=x,y=y1, stepMode=True, fillLevel=0, brush=(100,200,155), pen=pg.mkPen(None))

class HistogramWidget(pg.LayoutWidget):
    def __init__(self):
        super(HistogramWidget, self).__init__()
        self._stepUI()
        pass

    def _stepUI(self):
        layout_graph = self.addLayout(0,0)
        self.his = Histogram()
        layout_graph.addWidget(self.his)

    def setData(self, arry):
        self.his.setData(arry)

if __name__ == '__main__':
    def data_update():
        global g_map
        arry = np.random.randint(-100,100,500)/100
        g_map.setData(arry)

    app = QtWidgets.QApplication([])
    app.setAttribute(QtCore.Qt.AA_Use96Dpi)
    win = QtWidgets.QMainWindow()

    g_map = HistogramWidget()

    win.setCentralWidget(g_map)
    win.resize(1000, 1000)
    win.setWindowTitle('Unit test')
    win.show()

    qtimer = QtCore.QTimer()
    qtimer.timeout.connect(data_update)
    qtimer.start(50)

    app.exec_()

    # qtimer.stop()