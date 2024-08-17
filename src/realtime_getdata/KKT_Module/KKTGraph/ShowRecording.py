
from PySide2 import QtGui, QtCore, QtWidgets
import time
from KKT_Module.KKTGraph.StemPlotForLabeling import StemPlotForLabeling

class DrawingRecord(QtWidgets.QWidget):
    def __init__(self, title='Recording Test'):
        super(DrawingRecord, self).__init__()
        self._drawingTitle = title
        self.__setupUI()
        # self.enableWidget(True)

    def enableWidget(self, FPS=False):
        if FPS:
            self._lastTime = None
            self._lb_fps = QtWidgets.QLabel('{:.2f} fps.'.format(0))
            self._layout.addWidget(self._lb_fps,0,0)

    def setAxisRange(self, xaxisrange, yaxisrange):
        '''
        Set plot axis range.

        :param xaxisrange: plot X axis range
        :param yaxisrange: plot Y axis range
        '''
        self.stemplot.setAxisRange(xaxisrange, yaxisrange)

    def setFixLabel(self, label_info_list=None, label_string_list=None):
        '''
         Set gesture's labels name on plot

        :param label_info_list: Gesture information list, list(label start frame, label end frame, label y position)
        :param label_string_list: Gesture name list.
        '''
        if label_info_list is None:
            return
        count = 1
        for label_info in label_info_list:
            if label_string_list is not None:
                self.stemplot.addFixedStemGroup(
                    [label_info[0], label_info[1]],
                    label_info[2],
                    c=count,
                    label_string=str(label_string_list[count - 1]))
            else:
                self.stemplot.addFixedStemGroup(
                    [label_info[0], label_info[1]],
                    label_info[2],
                    c=count)
            count += 1

    def removeAllFixedStemGroup(self):
        self.stemplot.removeAllFixedStemGroup()

    def setDynamicStem(self, xrange, ylevel):
        '''
         Setup the recording timing graph axis.

        :param xrange: Stems increased when recording, list(start frames:0, number of record frames)
        :param ylevel: Stem's length on plot, list(shortest position, highest position)
        '''
        self.stemplot.setDynamicStem([xrange[0], xrange[1]], [ylevel[0] , ylevel[1]])

    def clearDynamicStem(self):
        '''
        Clear stems on the plot.
        '''
        self.stemplot.clearDynamicStem()

    def incDynamicStem(self, color=0, InRegion=1):
        '''
        Increase a stem per frame.
        :param color: Stem's color (0 ~ 15)
        :param InRegion: 0 for in the region, 1 for not in the region.
        :return:
        '''
        self.stemplot.incDynamicStem(color, region_flag=InRegion)
        self._updatedFPS()

    def __setupUI(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 10, 0, 10)
        grid_widget = QtWidgets.QWidget()
        layout.addWidget(grid_widget)

        self._layout = QtWidgets.QGridLayout(grid_widget)
        self._layout.setContentsMargins(6, 0, 6, 0)

        self.stemplot = StemPlotForLabeling(self._drawingTitle)
        # layout
        self._layout.addWidget(self.stemplot, 1, 0)


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

        
def data_update():
    global stempw
    global count
    if count == 100:
        stempw.removeAllFixedStemGroup()
        stempw.clearDynamicStem()
        stempw.setDynamicStem([0, 100], [0.8, 1])
        label_info_list = [
            [0,  3,  1],
            [6,  10, 1],
            [13, 16, 1],
        ]
        stempw.setFixLabel(label_info_list)
        count = 0

    stempw.incDynamicStem(InRegion=1)

    print(count)
    count = count + 1
    pass


## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    stempw = None
    count = 100

    app = QtWidgets.QApplication([])
    win = QtWidgets.QMainWindow()
    win.resize(600,400)

    stempw = DrawingRecord()
    stempw.show()
    win.setCentralWidget(stempw)
    win.show()
    win.setWindowTitle('pyqtgraph : ImageView')
    stempw.setAxisRange([-1, 100], [0, 1])
    qtimer = QtCore.QTimer()
    qtimer.timeout.connect(data_update)
    qtimer.start(50)

    # display_plot_image_with_minimal_setup()
    if sys.flags.interactive != 1 or not hasattr(QtCore, 'PYQT_VERSION'):
        QtWidgets.QApplication.instance().exec_()
