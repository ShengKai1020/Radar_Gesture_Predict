
import numpy as np
import time
import pyqtgraph as pg
from PySide2 import  QtCore, QtWidgets
##=====================================================================================


class DrawingPosition(pg.PlotWidget):
    pg.setConfigOption('foreground', 'k')  # Default foreground color for text, lines, axes, etc.
    pg.setConfigOption('background', None)  # Default background for GraphicsView.
    def __init__(self, title='Tracking', xRange=[-10, 10], yRange=[0, 30]):
        pg.PlotWidget.__init__(self)
        self.setRange(xRange=xRange, yRange=yRange)
        self.scale(1,1)
        self.setAspectLocked()
        self._title = title
        self.getAxis('bottom').setLabel(text=title[0].lower())
        self.getAxis('left').setLabel(text=title[1].lower())
        self._sector = False
        self._X_pos = np.zeros(40)
        self._Y_pos = np.zeros(40)
        self._Z_pos = np.zeros(40)
        self._setupUI()
        self.setData(np.asarray([0]), np.asarray([0]))

    def _setupUI(self):

        self.pattern = pg.PlotCurveItem(pen={'color':'k', 'width': 2})
        self.addItem(self.pattern)
        self.__Position = pg.ScatterPlotItem(pen='w', size=25)
        self.addItem(self.__Position)
        self.sector_l = pg.PlotCurveItem()
        self.sector_r = pg.PlotCurveItem()
        self.sector_t = pg.PlotCurveItem()
        self.sector_d = pg.PlotCurveItem()
        self.addItem(self.sector_l)
        self.addItem(self.sector_r)
        self.addItem(self.sector_d)
        self.addItem(self.sector_t)
        # self.setSectorRegion()

    def setSectorRegion(self, R=17, r=4, angle=60, pts=100):
        self.R = R
        self.r = r
        self.elevation = 90-angle/2

        elevation = 90-angle/2
        down_x = r*np.cos(elevation*np.pi/180)
        up_x = R*np.cos(elevation*np.pi/180)

        left_x = np.linspace(-up_x, -down_x, pts)
        left_y = left_x * np.tan(-elevation*np.pi/180)
        self.sector_l.setData(x=left_x, y=left_y)

        right_x = np.linspace(down_x, up_x, pts)
        right_y = right_x * np.tan(elevation*np.pi/180)
        self.sector_r.setData(x=right_x, y=right_y)

        down_x = np.linspace(-down_x, down_x, pts)
        down_y = np.absolute(np.sqrt((r**2)-(down_x)**2))
        self.sector_d.setData(x=down_x, y=down_y)

        top_x = np.linspace(-up_x, up_x, pts)
        top_y = np.absolute(np.sqrt((R**2)-(top_x)**2))
        self.sector_t.setData(x=top_x, y=top_y)
        self._sector = True

    def _visible(self, X, Y):

        if Y < np.sqrt(np.absolute((self.r**2)-(X)**2)):
            return False
        if Y > np.sqrt(np.absolute((self.R**2)-(X)**2)):
            return False
        if Y < np.absolute(X * np.tan(self.elevation*np.pi/180)):
            return False
        return True


    def setData(self, XX, YY):
        color = 'g'
        self._X_pos = np.roll(self._X_pos, -1)
        self._Y_pos = np.roll(self._Y_pos, -1)
        self._X_pos[-1] = XX
        self._Y_pos[-1] = YY

        self.__Position.setData(x=XX, y=YY)
        # self.__Position.setSize([i for i in range(5,25,2)])
        self.pattern.setData(x=self._X_pos, y=self._Y_pos)

        if self._sector:
            visible = self._visible(XX, YY)
            if not visible :
                color = 'w'
        self.__Position.setBrush(color)

    def setLabelData(self, XX, YY, label):
        if label == 0 :
            self._Y_lpos = np.zeros(1)
            self._X_lpos = np.zeros(1)
            self._z_lpos = np.zeros(1)
        elif label == 1:
            self._X_lpos = np.insert(self._X_lpos, -1, XX)
            self._Y_lpos = np.insert(self._Y_lpos, -1, YY)

        color = 'g'
        # self._X_pos = np.roll(self._X_pos, -1)
        # self._Y_pos = np.roll(self._Y_pos, -1)
        self._X_lpos[-1] = XX
        self._Y_lpos[-1] = YY

        self.__Position.setData(x=XX, y=YY)
        # self.__Position.setSize([i for i in range(5,25,2)])
        self.pattern.setData(x=self._X_lpos, y=self._Y_lpos)

        if self._sector:
            visible = self._visible(XX, YY)
            if not visible :
                color = 'w'
        self.__Position.setBrush(color)

class TrakingWidget(QtWidgets.QWidget):
    def __init__(self, title='Traking Test'):
        super(TrakingWidget, self).__init__()
        self._title = title
        self._stepUI()
        self._lastTime = None
        pass

    def enableWidget(self, FPS=False):
        if FPS:
            self._lb_fps = QtWidgets.QLabel('{:.2f} fps.'.format(0))
            self._layout.addWidget(self._lb_fps, 0,0)

    def _stepUI(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 10, 0, 10)
        grid_widget = QtWidgets.QWidget()
        layout.addWidget(grid_widget)

        self._layout = QtWidgets.QGridLayout(grid_widget)
        self._layout.setContentsMargins(6, 0, 6, 0)
        self.Tracking_2D = DrawingPosition(self._title)
        self._layout.addWidget(self.Tracking_2D,2,0)


    def setData(self, x, y):
        self.Tracking_2D.setData(x,y)
        self._updatedFPS()

    def _updatedFPS(self):
        if not hasattr(self, '_lb_fps'):
            return
        if self._lastTime == None:
            self._lastTime = time.time()
        else:
            now = time.time()
            dt = now - self._lastTime
            self._lastTime = now
            self._lb_fps.setText(" {:.2f} fps.".format(1.0 / dt))



##=============================  Unit Testing  ========================================
if __name__ == '__main__':
    import sys
    # y=np.zeros(1)
    # x=np.zeros(1)
    y=0
    x=0
    x_inc = 0.2
    y_inc = 0.2

    def data_update():
        global Tracking, y, x, y_inc, x_inc
        # y = np.random.randint(low=-10, high=10, size=(2, 1))
        if x >= 10:
            x_inc = -0.2
        if x <= -10:
            x_inc =0.2

        if y >= 20:
            y_inc = -0.2
        if y <= 0:
            y_inc = 0.2

        y = y + y_inc
        x = x + x_inc
        print(x,y)
        Tracking.setData(x, y)

    app = QtWidgets.QApplication([])

    Tracking = TrakingWidget('Traking Test')
    Tracking.enableWidget(True)

    Tracking.show()

    qtimer = QtCore.QTimer()
    qtimer.timeout.connect(data_update)
    qtimer.start(50)

    app.exec_()
    qtimer.stop()