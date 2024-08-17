import random
import numpy as np
import pyqtgraph as pg
from PySide2 import QtWidgets, QtCore, QtGui
import time
from KKT_Module.KKTUtility.qt_obj import MapLevelBar

##=====================================================================================
class DrawMap(pg.LayoutWidget):
    pg.setConfigOption('foreground', 'k')
    pg.setConfigOption('background', None)
    def __init__(self, title):
        super(DrawMap, self).__init__()
        # pg.setConfigOption('background', 'w')
        self._lb_title = title
        self._lb_border = QtWidgets.QLabel()
        self.setupUI()
        self._max_level = 1000
        self._min_level = 0
        self.setData(np.zeros((32, 32)))

    def setupUI(self):

        self._map = pg.ImageView()
        self._map.ui.histogram.hide()
        self._map.ui.roiBtn.hide()
        self._map.ui.menuBtn.hide()

        colors = [
                    (25, 25, 112, 255),
                    (0, 0, 255, 255),  # blue
                    (0, 255, 255, 255),  # Aqua
                    (0, 255, 0, 255),  # lime
                    (255, 255, 0, 255),  # yellow
                    (255, 0, 0, 255)  # Red
                  ]
        pos = [0.0, 0.1, 0.25, 0.45, 0.7, 1.0]
        # pos = [0.0, 0.15, 0.3, 0.5, 0.75, 1.0]

        cmap = pg.ColorMap(pos=pos, color=colors)
        self._map.setColorMap(cmap)
        self._lb_map = QtWidgets.QLabel(self._lb_title)
        self._lb_map.setFont(QtGui.QFont('Times', 10))
        self._lb_map.setAlignment(QtCore.Qt.AlignCenter)

        self.addWidget(self._lb_map, row=0, col=0)
        self.addWidget(self._map, row=1, col=0)
        self.addWidget(self._lb_border, row=1, col=0)

    def setData(self, data):
        self._map.setImage(data, axes={'x':1, 'y':0}, levels=[self._min_level, self._max_level])

    def setLevel(self, Max, Min=0):
        self._max_level = Max
        self._min_level = Min

    def setborder(self, border):
        if border == 1:
            self._lb_border.setStyleSheet("border: 6px solid lime;")
        else:
            self._lb_border.setStyleSheet("background:transparent")

class DrawMap2(pg.GraphicsLayoutWidget):
    def __init__(self, title, whole_map=False):
        super(DrawMap2, self).__init__()
        self._lb_title = title
        self._max_level = 1500
        self._min_level = 0
        self.map_shape = (32,32)
        self.whole_map =whole_map
        self.axis = { 'x_len':0.3, 'y_len':34, 'x_start':-0.15, 'y_start':0}
        self.setupUI()
        self.initPlots()

    def setupUI(self):
        self.color_map = pg.ImageItem(image=np.zeros(self.map_shape))
        self.color_map.setBorder(b={'color': 'transparent', 'width':10})
        self._map = self.addPlot(title= self._lb_title)
        self._map.getViewBox().invertY(True)
        self._map.setMouseEnabled(x=False, y=False)
        self._map.addItem(self.color_map)
        self._map.getAxis('left').setLabel('Distance (cm)')
        self._map.getAxis('bottom').setLabel('Velocity (cm/s)')
        colors = [
                    (25, 25, 112, 255),
                    (0, 0, 255, 255),  # blue
                    (0, 255, 255, 255),  # Aqua
                    (0, 255, 0, 255),  # lime
                    (255, 255, 0, 255),  # yellow
                    (255, 0, 0, 255)  # Red
                  ]
        pos = [0.0, 0.1, 0.25, 0.45, 0.7, 1.0]
        cmap = pg.ColorMap(pos=pos, color=colors)
        self.bar = pg.ColorBarItem(interactive=False, colorMap=cmap, label='Level scale color bar')
        self.bar.setImageItem(self.color_map, insert_in=self._map)

    def initPlots(self):
        map = np.zeros(self.map_shape)
        self.setAxis(x_len=self.axis['x_len'], y_len=self.axis['y_len'], x_start=self.axis['x_start'],
                     y_start=self.axis['y_start'])
        self.color_map.setImage(map, autoLevels=False)
        self.color_map.setLevels(levels=(self._min_level, self._max_level))
        self.bar.setLevels(low=self._min_level, high=self._max_level)
        pass

    def setAxis(self, x_len=0.3, y_len=34, x_start=-0.15, y_start=0):
        tr = QtGui.QTransform()
        # if self.whole_map:
        #     self._map.setRange(xRange=(x_start, x_start + x_len), yRange=(y_start, y_start + y_len), padding=0)
        #     tr.scale(x_len / self.map_shape[1], y_len / self.map_shape[0])
        # else:
        #     self._map.setRange(xRange=(x_start, x_start+x_len), yRange=(y_start, y_start+y_len), padding=0)
        #     tr.scale(x_len / self.map_shape[1], y_len / self.map_shape[0])

        self._map.setRange(xRange=(x_start, x_start+x_len), yRange=(y_start, y_start+y_len), padding=0)
        tr.scale(x_len / self.map_shape[1], y_len / self.map_shape[0])

        tr.translate(x_start/x_len * self.map_shape[1], y_start/y_len*self.map_shape[0])
        self.color_map.setTransform(tr)
        self.axis['x_len']=x_len
        self.axis['y_len'] = y_len
        self.axis['x_start'] = x_start
        self.axis['y_start'] = y_start

    def setData(self, data):
        # assert np.shape(data.T) == self.map_shape, 'Input data shape not match!'
        if np.shape(data) != self.map_shape:
            self.setParameters(map_shape=np.shape(data))
            self.initPlots()
        self.color_map.setImage(data.T, autoLevels=False)

    def setLevel(self, max, min=0):
        self._max_level = max
        self._min_level = min
        self.bar.setLevels(low=self._min_level, high=self._max_level)

    def setBorder(self, border):
        if border == 1:
            self.color_map.setBorder(b={'color': 'lime', 'width':10})
        else:
            self.color_map.setBorder(b={'color': 'transparent', 'width':10})

    def setParameters(self,**kwargs):
        for k,v in kwargs.items():
            assert hasattr(self, k), 'No attribute : {}'.format(k)
            setattr(self, k , v)

class FeatureMapWidget(QtWidgets.QWidget):
    def __init__(self, map_name =['RDI Map','PHD Map']):
        super(FeatureMapWidget, self).__init__()
        self._level_slider = None
        self._lb_fps = None
        self._map_name = map_name
        self.MapLevelBar = None
        self._stepUi()

    def enableWidget(self, FPS=False, adjust=False):
        if adjust:
            self._layout.addWidget(self.MapLevelBar, 2, 0, 1, 2)
        if FPS:
            self._lb_fps = QtWidgets.QLabel('{:.2f} fps.'.format(0))
            self._layout.addWidget(self._lb_fps, 0, 0, 1, 1 )
            self.lastTime = None

    def _stepUi(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 10, 0, 10)
        grid_widget = QtWidgets.QWidget()
        layout.addWidget(grid_widget)

        self._layout = QtWidgets.QGridLayout(grid_widget)
        self._layout.setContentsMargins(6, 0, 6, 0)
        self._layout.setColumnStretch(0, 1)
        self._layout.setColumnStretch(1, 1)
        self._RDImap = DrawMap(self._map_name[0])
        self._PHDmap = DrawMap(self._map_name[1])

        self._layout.addWidget(self._RDImap, 1, 0, 1, 1)
        self._layout.addWidget(self._PHDmap, 1, 1, 1, 1)

        self.MapLevelBar = MapLevelBar(border=True)
        self.MapLevelBar.LevelChanged.connect(lambda: self._setLevel())

    def _setLevel(self):
        if self.MapLevelBar is None:
            return

        self._RDImap.setLevel(Max=self.MapLevelBar.getLevel())
        self._PHDmap.setLevel(Max=self.MapLevelBar.getLevel())

    def setData(self, RDI, PHD):
        self._RDImap.setData(RDI)
        self._PHDmap.setData(PHD)
        if self._lb_fps is None:
            return
        self._updatedFPS()

    def setBorder(self, RDI, PHD):
        self._RDImap.setborder(RDI)
        self._PHDmap.setborder(PHD)

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

class FeatureMapWidget2(QtWidgets.QWidget):
    def __init__(self, map_name =['RDI Map','PHD Map']):
        super(FeatureMapWidget2, self).__init__()
        self._level_slider = None
        self._lb_fps = None
        self._map_name = map_name
        self.MapLevelBar = None
        self.max_distance=68.7
        self.setupGUI()


    def enableWidget(self, FPS=False, adjust=False):
        if adjust:
            self._layout.addWidget(self.MapLevelBar, 2, 0, 1, 2)
        if FPS:
            self._lb_fps = QtWidgets.QLabel('{:.2f} fps.'.format(0))
            self._layout.addWidget(self._lb_fps, 0, 0, 1, 1 )
            self.lastTime = None

    def setupGUI(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 10, 0, 10)
        grid_widget = QtWidgets.QWidget()
        layout.addWidget(grid_widget)

        self._layout = QtWidgets.QGridLayout(grid_widget)
        self._layout.setContentsMargins(6, 0, 6, 0)
        self._layout.setColumnStretch(0, 1)
        self._layout.setColumnStretch(1, 1)
        self._RDImap = DrawMap2(self._map_name[0])
        self._RDImap.setParameters(axis = { 'x_len':0.3,
                                            'y_len':self.max_distance/2,
                                            'x_start':-0.15,
                                            'y_start':0
                                            },
                                   _max_level = 1500,
                                   _min_level = 0
                                   )
        self._PHDmap = DrawMap2(self._map_name[1])
        self._RDImap.setParameters(axis = { 'x_len':0.3,
                                            'y_len':self.max_distance/2,
                                            'x_start':-0.15,
                                            'y_start':0
                                            },
                                   _max_level = 1500,
                                   _min_level = 0
                                   )
        self._RDImap.initPlots()
        self._PHDmap.initPlots()

        self._layout.addWidget(self._RDImap, 1, 0, 1, 1, alignment=QtCore.Qt.AlignCenter)
        self._layout.addWidget(self._PHDmap, 1, 1, 1, 1, alignment=QtCore.Qt.AlignCenter)

        self.MapLevelBar = MapLevelBar(border=True)
        self.MapLevelBar.LevelChanged.connect(lambda: self._setLevel())
        self._setLevel()

    def _setLevel(self):
        if self.MapLevelBar is None:
            return
        self._RDImap.setLevel(self.MapLevelBar.getLevel(),0)
        self._PHDmap.setLevel(self.MapLevelBar.getLevel(),0)

    def setAxis(self, x_len=0.3, y_len=None, x_start=-0.15, y_start=0, x_ratio=2, y_ratio=2):
        if y_len is not None:
            self.max_distance = y_len*2

        y_len = self.max_distance/2*y_ratio/2
        x_len = x_len / 2 * x_ratio
        x_start = x_start / 2 * x_ratio

        self._RDImap.setAxis(x_len=x_len, y_len=y_len, x_start=x_start, y_start=y_start)
        self._PHDmap.setAxis(x_len=x_len, y_len=y_len, x_start=x_start, y_start=y_start)

    def setData(self, RDI, PHD):
        self._RDImap.setData(RDI)
        self._PHDmap.setData(PHD)
        if self._lb_fps is None:
            return
        self._updatedFPS()

    def setBorder(self, RDI, PHD):
        self._RDImap.setBorder(RDI)
        self._PHDmap.setBorder(PHD)

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

    def setParameters(self,**kwargs):
        self.FFT.setParameters(**kwargs)
        self._RDImap.setParameters(**kwargs)
        self._PHDmap.setParameters(**kwargs)

##=============================  Unit Testing  ========================================
if __name__ == '__main__':
    def data_update():
        global g_map
        # time.sleep(0.05)
        m = np.random.randint(0, 70, size=(32,32))
        g_map.setData(m,m)
        l = random.randint(0,1)
        g_map.setBorder(l,l)
        # m = random.randint(200,1000)
        # g_map.setLevel(m,m)

    # g_map = None
    app = QtWidgets.QApplication([])
    win = QtWidgets.QMainWindow()
    win.resize(800,600)

    g_map = FeatureMapWidget2()
    g_map.setAxis(y_len=32)
    g_map.enableWidget(adjust=True)

    win.setCentralWidget(g_map)
    win.setWindowTitle('Unit test')
    win.show()

    qtimer = QtCore.QTimer()
    qtimer.timeout.connect(data_update)
    qtimer.start(40)
    app.exec_()
    qtimer.stop()