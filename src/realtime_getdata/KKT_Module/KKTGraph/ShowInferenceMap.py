import numpy as np
import pyqtgraph as pg
from PySide2 import QtCore, QtGui,QtWidgets

##=====================================================================================
class InferenceMap(pg.LayoutWidget):
    def __init__(self, title='Inference Map', Xrange=[0,110], Yrange=[0,12]):
        super(InferenceMap, self).__init__()
        self.label = title
        self._Xrange = Xrange
        self._Yrange = Yrange
        self._height = (self._Yrange[1]-2)*12
        self._width = 450
        self._setupUI()


    def _setupUI(self):
        wg = QtWidgets.QWidget()
        p = pg.GraphicsLayoutWidget(parent=wg)
        # p.setGeometry(QtCore.QRect(0, 0, 0, 700))

        tr = QtGui.QTransform()  # prepare ImageItem transformation:
        tr.scale(1, 1)  # scale horizontal and vertical axes
        tr.translate(0, 0.5)  # move 3x3 image to locate center at axis origin

        self.img = pg.ImageItem(image=np.random.randint(0,100,size=(100,1))/100)  # create example image
        self.img.setTransform(tr)  # assign transform
        self.vb = pg.ViewBox()
        self.vb.addItem(self.img)

        self.plot = pg.PlotItem(viewBox=self.vb)
        self.plot.setFixedHeight(self._height)
        self.plot.setFixedWidth(self._width)
        self.plot.setLabel(axis='left', text='gesture')
        self.plot.setLabel(axis='bottom', text='frame')
        self.plot.setTitle(self.label)
        self.plot.showGrid(y= True, alpha=0.6)

        p.addItem(self.plot)

        self.hist = pg.HistogramLUTItem()
        self.hist.setFixedHeight(self._height+30)
        self.hist.setFixedWidth(50)
        self.hist.setImageItem(self.img)
        self.hist.setLevels(0, 1)
        ticks =[(0.0  ,(0, 0, 0, 0)),
                (0.25 ,(0, 0, 255, 255)),
                (0.5  ,(0, 255, 0, 255)),
                (0.75 ,(255, 255, 0, 255)),
                (1.0  ,(255, 255, 255, 255))]
        self.hist.gradient.restoreState({'mode': 'rgb',
         'ticks': ticks})

        p.addItem(self.hist)
        self.vb.setXRange(self._Xrange[0],self._Xrange[1])
        self.vb.setYRange(self._Yrange[0],self._Yrange[1])
        self.vb.setFixedHeight(self._height)
        self.vb.setFixedWidth(self._width)
        self.addWidget(p)



    def setImage(self, image, levels=[0, 1]):
        self.img.setImage(image=image, levels=(levels[0],levels[1])) # create example image

class DrawInferenceMap(pg.LayoutWidget):

    def __init__(self, label='Map Status :'):
        super(DrawInferenceMap, self).__init__()
        self.drawing_label = label
        self.label = QtWidgets.QLabel()
        self.n_cls_data1 = 12
        self.n_cls_data2 = 42
        self.n_time = 100
        self.roll_data1 = np.zeros([self.n_time, self.n_cls_data1])
        self.roll_data2 = np.zeros([self.n_time, self.n_cls_data2])
        self.setupUI()
        self._init_timer = QtCore.QTimer()
        self._init_timer.timeout.connect(lambda :self._stopTimer())


    def setupUI(self):

        self._inference_map1 = InferenceMap(Yrange=[0, self.n_cls_data1])
        self._inference_map2 = InferenceMap(Yrange=[0, self.n_cls_data2])

        self.lb_map = QtWidgets.QLabel(self.drawing_label)
        self.lb_map.setFont(QtGui.QFont('Times', 10))
        # self.lb_map.setAlignment(QtCore.Qt.AlignBottom)

        layout_lb = self.addLayout(0,0, rowspan=1)
        layout_graph = self.addLayout(1,0,rowspan=30)
        layout_lb.addWidget(self.lb_map)
        layout_graph.addWidget(self._inference_map1, 0, 0, rowspan=2)
        layout_graph.addWidget(self._inference_map2, 2, 0, rowspan=5)


    def setData(self, data1=np.zeros([40]), data2=np.zeros([40])):

        data1 = np.pad(data1, [0, self.n_cls_data1 - len(data1)], 'constant', constant_values=(0, 0))
        data2 = np.pad(data2, [0, self.n_cls_data2 - len(data2)], 'constant', constant_values=(0, 0))

        self.roll_data1 = np.roll(self.roll_data1, shift=-1, axis=0)
        self.roll_data1[self.n_time-1, :] = data1
        self.roll_data2 = np.roll(self.roll_data2, shift=-1, axis=0)
        self.roll_data2[self.n_time-1 :] = data2

        self._inference_map1.setImage(self.roll_data1, levels=[0, 1])
        self._inference_map2.setImage(self.roll_data2, levels=[0, 1])

    def setborder(self, border):
        if border == 1:
            self.label.setStyleSheet("border: 5px solid lime;")
        else:
            self.label.setStyleSheet("background:transparent")

    def setMapStatus(self, status):
        self.lb_map.setText('Map Status : {}'.format(status))
        self._init_timer.start(1500)

    def _stopTimer(self):
        self._init_timer.stop()
        self.lb_map.setText('Map Status : ')

##=============================  Unit Testing  ========================================
if __name__ == '__main__':
    import sys

    import time


    def data_update():
        # return
        global g_map
        g_map.setData(np.random.randint(0,100,10)/100, np.random.randint(0,100,40)/100)



    g_map = None
    app = QtWidgets.QApplication([])
    app.setAttribute(QtCore.Qt.AA_Use96Dpi)
    win = QtWidgets.QMainWindow()

    g_map = DrawInferenceMap()

    win.setCentralWidget(g_map)
    win.resize(700, 900)
    win.setWindowTitle('Unit test')
    win.show()

    qtimer = QtCore.QTimer()
    qtimer.timeout.connect(data_update)
    qtimer.start(50)

    app.exec_()

    qtimer.stop()
