
from PySide2 import QtCore, QtWidgets, QtGui
import time
from KKT_Module.KKTGraph.StemPlot import StemPlot
from KKT_Module.KKTUtility.qt_obj import InputThreshold


class DrawingResult_GS(QtWidgets.QWidget):
    def __init__(self, title='Stem Plot Test'):
        super(DrawingResult_GS, self).__init__()
        self._drawingTitle = title
        self._lastTime = None
        self._timer = QtCore.QTimer()
        self._timer.timeout.connect(lambda :self.detectGesTimeout())
        self.__setupUI()
        self.enableWidget(Gesture=True)


    def enableWidget(self, FPS=False, Threshold=False, Gesture=True):
        if Threshold:
            self._layout.addWidget(self.threshold, 3, 0, 1 ,2)

        if FPS:
            self._lb_fps = QtWidgets.QLabel('{:.2f} fps.'.format(0))
            self._layout.addWidget(self._lb_fps, 0,0)

        if Gesture:
            self._layout.addWidget(self._Gesture_lb, 1, 0, 1, 1)



    def __setupUI(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 10, 0, 10)
        grid_widget = QtWidgets.QWidget()
        layout.addWidget(grid_widget)

        self._layout = QtWidgets.QGridLayout(grid_widget)
        self._layout.setContentsMargins(6, 0, 6, 0)

        self._stemplot = StemPlot(self._drawingTitle)
        self._stemplot.setAxisRange([0, 1], [0, 1])
        self._layout.addWidget(self._stemplot, 2, 0)

        self.threshold = InputThreshold(threshold=[0.4, 0.4])
        self._Gesture_lb = QtWidgets.QLabel('Gesture = ')
        self._Gesture_lb.setFont(QtGui.QFont("Yu Gothic UI",12))

    def setGestureLabel(self, ges):
        self._timer.stop()
        self._Gesture_lb.setText('Gesture = {}'.format(ges))
        self._timer.start(700)
        pass

    def detectGesTimeout(self):
        self._timer.stop()
        self._Gesture_lb.setText('Gesture = ')

    def getThresholdList(self):
        return self.threshold.getThreshold()

    def setAxisRange(self, xaxisrange, yaxisrange):
        self._stemplot.setAxisRange(xaxisrange, yaxisrange)

    def setData(self, data):
        self._updatedFPS()
        self._stemplot.setYData(data)

    def clearData(self):
        self._stemplot.clearData()

    def _updatedFPS(self):
        if not hasattr(self, '_lb_fps'):
            return
        if self._lastTime == None:
            self._lastTime = time.time()
        else:
            now = time.time()
            dt = now - self._lastTime
            self._lastTime = now
            self._lb_fps.setText(" {:.2f} fps.".format(1.0/dt))

    def setThreshold(self, threshold):
        self.threshold.setThreshold(threshold)

def data_update():
    import numpy as np
    global stempw
    global count

    y = np.random.random(size=(16))
    # print(y)
    count += 1
    if count % 2 == 0:
        stempw.clearData()
    else:
        stempw.setData(y)


## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys

    # global stempw

    count = 0

    # atexit.register(cleanup_function)

    # pyqtgraph.examples.run()
    # exit()

    app = QtWidgets.QApplication([])
    app.setAttribute(QtCore.Qt.AA_Use96Dpi)
    # app.setAttribute(QtCore.Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

    ## Create window with ImageView widget
    win = QtWidgets.QMainWindow()
    win.resize(600,400)

    stempw = DrawingResult_GS()
    stempw.enableWidget(True,True)
    win.setCentralWidget(stempw)
    win.show()

    stempw.setAxisRange([-1, 16], [0, 1])

    qtimer = QtCore.QTimer()
    qtimer.timeout.connect(data_update)
    qtimer.start(500)

    # display_plot_image_with_minimal_setup()
    if sys.flags.interactive != 1 or not hasattr(QtCore, 'PYQT_VERSION'):
        QtWidgets.QApplication.instance().exec_()
