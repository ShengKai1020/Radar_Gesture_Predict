import time

from PySide2 import QtGui, QtCore, QtWidgets
import numpy as np
import pyqtgraph as pg
from collections import deque


class StemPlotForLabeling(pg.PlotWidget):
    sig_increase_frame = QtCore.Signal(object)
    Colors = (
        (255, 255, 0),  # yellow # (255, 204, 0),
        (255, 0, 0),  # red
        (0, 255, 0),  # lime , green
        (255, 0, 255),  # Fuchsia
        (204, 255, 51),
        (255, 102, 0),
        (51, 204, 51),
        (204, 51, 255),
        (255, 153, 0),
        (255, 80, 80),
        (0, 204, 102),
        (204, 0, 153),
        (153, 51, 51),
        (0, 204, 153),
        (102, 0, 255),
    )
    def __init__(self,title='StemPlotForLabeling', x_range=(0,100), show_frames=100, frame_level=0.4, label_level=0.9):
        pg.setConfigOption('foreground', 'k')   # Default foreground color for text, lines, axes, etc.
        pg.setConfigOption('background', (0,0,0,0))  # Default background for GraphicsView.
        pg.setConfigOptions(antialias=True)     # Draw lines with smooth edges at the cost of reduced performance.
        super(StemPlotForLabeling, self).__init__(enableMenu=False)
        self.title = title
        self.__XRange = x_range
        self.__show_frames = show_frames
        self.__showXRange = (x_range[0],self.__show_frames)
        self.__frame_level = frame_level
        self.__label_level = label_level
        self.fixed_curves = deque()
        self.setup()
        self.sig_increase_frame.connect(lambda x:self.incDynamicStem(x))

    def setConfigs(self, **kwargs):
        for k,v in kwargs.items():
            if not hasattr(self, k):
                print( 'Attribute "{}" not in the class.'.format(k))
                continue
            self.__setattr__(k,v)
            print('Attribute "{}", set "{}"'.format(k, v))

    def setup(self):
        self.setupFrameStems()
        self.setupLabelStems(c=1)
        self.PI = self.getPlotItem()
        self.PI.setTitle(self.title)
        self.VB = self.PI.getViewBox()
        # self.VB.setRange(xRange=(0,100), yRange=(0,1))
        self.setPlotXRange()
        self.axis_bottom = self.PI.getAxis('bottom')
        self.axis_bottom.setLabel('Frames')
        self.axis_left = self.PI.getAxis('left')
        self.axis_left.hide()
        pass

    def setPlotXRange(self):
        arg = {'xMin':self.__showXRange[0]-int(self.__show_frames*0.05),
               'xMax':self.__showXRange[1]+int(self.__show_frames*0.05),
               'yMin':0,
               'yMax':1.2,
               'minXRange':self.__show_frames+int(self.__show_frames*0.05)*2,
                'maxXRange':self.__show_frames+int(self.__show_frames*0.05)*2,
              'minYRange':1,
              'maxYRange':1}
        self.VB.setLimits(**arg)
        self.VB.setRange(xRange=self.__showXRange, yRange=(0, 1))

    def _removeCurve(self, curve):
        if curve is not None:
            self.removeItem(curve)

    def addFixedStemGroup(self, xrange, ylevel, c=None, label_string=None):
        x = np.arange(xrange[0],xrange[1])
        y = np.linspace(ylevel, ylevel, xrange[1] - xrange[0])
        text = None
        cor, cor1 = self._selectColor(c)
        cstem = self.plot(np.repeat(x, 2), np.dstack((np.zeros(y.shape[0], dtype=int), y)).flatten(), pen=pg.mkPen(cor, width=3), connect='pairs', name='Stems')
        cpoint = self.plot(x, y, pen=None, symbol='o', symbolPen=cor, symbolBrush=cor1, symbolSize=8, name='Points')

        font = QtGui.QFont()
        font.setPixelSize(15)
        if label_string is not None:
            text = pg.TextItem(label_string, border='w', fill=(0, 0, 255, 150))
            text.setPos(x[0], y[-1])
            text.setFont(font)
            self.addItem(text)
        self.fixed_curves.append([cstem, cpoint, text])

    def removeLastFixedStemGroup(self):
        if len(self.fixed_curves) == 0:
            return
        remove = self.fixed_curves[-1]
        for item in remove:
            if item is not None:
                self._removeCurve(item)
        self.fixed_curves.remove(remove)

    def removeFirstFixedStemGroup(self):
        if len(self.fixed_curves) == 0:
            return
        remove = self.fixed_curves[0]
        for item in remove:
            if item is not None:
                self._removeCurve(item)
        self.fixed_curves.remove(remove)

    def removeAllFixedStemGroup(self):
        for curve in self.fixed_curves:
            for item in curve:
                if item is not None:
                    self._removeCurve(item)
        self.fixed_curves.clear()

    def setDynamicStem(self, x_range, ylevel, show_frames=None):
        '''
         Setup the recording timing graph axis.

        :param xrange: list(start frames:0, number of record frames)
        :param ylevel: list()
        '''
        self.__XRange = x_range
        self.__frame_level = ylevel[0]
        self.__label_level = ylevel[1]
        if show_frames is not None:
            self.__show_frames = show_frames
        self.__showXRange = (x_range[0],self.__show_frames)
        self.clearDynamicStem()
        self.setPlotXRange()
        self.__curveXCount = 0

    def clearDynamicStem(self):
        self.x_frame = np.zeros(0, dtype='uint32')
        self.y_frame = np.zeros(0)
        self.x_label = np.zeros(0, dtype='uint32')
        self.y_label = np.zeros(0)
        self.stem_x_frame = np.zeros(0, dtype='uint32')
        self.stem_y_frame = np.zeros(0)
        self.stem_x_label = np.zeros(0, dtype='uint32')
        self.stem_y_label = np.zeros(0)
        self.__setStemData(0, label_level=1)


    def incDynamicStem(self, labeled=0):
        s = time.time_ns()
        if self.__curveXCount >= self.__showXRange[1]:
            self.__showXRange = (self.__showXRange[0]+self.__show_frames, self.__showXRange[1]+self.__show_frames)
            self.setPlotXRange()
            self.clearDynamicStem()
        self.__curveXCount += 1
        self.__setStemData(count=self.__curveXCount, label_level=labeled)
        # print('Update label plot time = {} ms'.format((time.time_ns() - s)/1000000))

    def decDynamicStem(self):
        if self.__curveXCount <= 0:
            return
        self.__curveXCount -= 1
        self.__setStemData(self.__curveXRange, self.__curveYLevel, self.__curveXCount)

    def __setStemData(self, count, frame_level=0.8, label_level=1):
        length= len(self.x_frame)
        if count !=0 :
            # self.x_frame = np.insert(self.x_frame, length ,count-1)
            # self.y_frame = np.insert(self.y_frame, length ,frame_level)
        # stemx = np.insert(np.reshape(self.x_frame,(-1, 1)), 1, self.x_frame, axis=1).flatten()
        # stemy = np.insert(np.reshape(self.y_frame,(-1, 1)), 0, 0, axis=1).flatten()
            self.stem_x_frame = np.append(self.stem_x_frame, [count-1, count-1])
            self.stem_y_frame = np.append(self.stem_y_frame , [0, frame_level])
        #
        self.frame_stem.setData(self.stem_x_frame, self.stem_y_frame)
        # self.frame_point.setData(self.x_frame, self.y_frame)
        if not label_level:
            return
        length= len(self.y_label)
        if count != 0:
            # self.x_label = np.append(self.x_label, count-1)
            # self.y_label = np.append(self.y_label,label_level)
        # stemx1 = np.repeat(self.x_label, 2)
        # stemx1 = np.insert(np.reshape(self.x_label,(-1, 1)), 1, self.x_label, axis=1).flatten()
        # stemy1 = np.insert(np.reshape(self.y_label, (-1, 1)), 0, 0, axis=1).flatten()
            self.stem_x_label = np.append(self.stem_x_label, [count - 1, count - 1])
            self.stem_y_label = np.append(self.stem_y_label, [0, label_level])

        self.label_stem.setData(self.stem_x_label, self.stem_y_label)
        # self.label_point.setData(self.x_label, self.y_label)


    def setupFrameStems(self):
        self.frame_stem = pg.PlotDataItem(pen=pg.mkPen('b', width=1), connect='pairs', name='Stems')
        self.frame_point = pg.PlotDataItem(pen=None, symbol='o', symbolPen='b',
                                           symbolBrush=QtGui.QBrush(QtGui.QColor(20, 20, 200)), symbolSize=8, name='Points')
        self.addItem(self.frame_stem)
        self.addItem(self.frame_point)

    def setupLabelStems(self, c):
        cor, cor1 = self._selectColor(c)
        self.label_stem = pg.PlotDataItem(pen=pg.mkPen(cor, width=1), connect='pairs', name='Stems')
        self.label_point = pg.PlotDataItem(pen=None, symbol='o', symbolPen=cor, symbolBrush=cor1, symbolSize=8,
                                           name='Points')
        self.addItem(self.label_stem)
        self.addItem(self.label_point)

    def _selectColor(self, c):
        if c is None:
            cor = 'r'
            cor1 = (20, 20, 200)
        else:
            if c >= len(self.Colors):
                c = c % len(self.Colors)
            c1 = c + 1
            if c1 >= len(self.Colors):
                c1 = c1 % len(self.Colors)
            cor = self.Colors[c]
            cor1 = self.Colors[c1]
        return cor, cor1

    def contextMenuEvent(self, event: QtWidgets.QGraphicsSceneContextMenuEvent) -> None:
        menu = QtWidgets.QMenu()
        range = menu.addAction('Set Range')
        selected_action = menu.exec_(QtGui.QCursor.pos())
        if selected_action == range:
            num , ok = QtWidgets.QInputDialog.getInt(None, 'X axis range', 'Input X axis range:', self.__show_frames, minValue=10)
            if ok:
                self.__show_frames = num
                self.__showXRange = (self.__showXRange[0], self.__showXRange[0]+self.__show_frames)
                self.setPlotXRange()
            print("You have selected the first option")
        return super().eventFilter(selected_action, event)

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
                self.addFixedStemGroup(
                    [label_info[0], label_info[1]],
                    label_info[2],
                    c=count,
                    label_string=str(label_string_list[count - 1]))
            else:
                self.addFixedStemGroup(
                    [label_info[0], label_info[1]],
                    label_info[2],
                    c=count)
            count += 1




if __name__ == '__main__':
    def __data_update():
        global stempw
        global count
        print(count)
        if count == 0:
            stempw.addFixedStemGroup([4,15], 0.8, 1, label_string='2')
            stempw.addFixedStemGroup([20,35], 0.7, 2, label_string='3')
            stempw.addFixedStemGroup([40,55], 0.6, 3, label_string='5')
            stempw.addFixedStemGroup([60,75], 0.5, 4, label_string='f')
            count += 1
        elif count == 1:
            # pass
            stempw.setDynamicStem([0, 1000], [0.4, 0.9])
            stempw.removeFirstFixedStemGroup()
            # stempw.removeLastFixedStemGroup()
            count += 1
        elif count >= 2:
            label = 0
            # stempw.removeAllFixedStemGroup()
            if count >= 20 and count < 60:
                label = 1
            stempw.incDynamicStem(labeled=label)
            count += 1
            if count==1200:
                count=1

    count = 0

    app = QtWidgets.QApplication([])
    app.setAttribute(QtCore.Qt.AA_Use96Dpi)


    ## Create window with ImageView widget
    win = QtWidgets.QMainWindow()
    win.resize(600,400)

    stempw = StemPlotForLabeling()
    win.setCentralWidget(stempw)
    win.show()
    qtimer = QtCore.QTimer()
    qtimer.timeout.connect(__data_update)
    qtimer.start(10)
    app.exec_()
