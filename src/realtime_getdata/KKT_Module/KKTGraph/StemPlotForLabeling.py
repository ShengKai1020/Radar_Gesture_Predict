
import numpy as np
import pyqtgraph as pg
from PySide2 import QtGui, QtCore, QtWidgets


class StemPlotForLabeling(pg.PlotWidget):
    def __init__(self, title="Stem Plot Example"):
        pg.setConfigOption('foreground', 'k')   # Default foreground color for text, lines, axes, etc.
        pg.setConfigOption('background', (0,0,0,0))  # Default background for GraphicsView.
        pg.setConfigOptions(antialias=True)     # Draw lines with smooth edges at the cost of reduced performance.
        super(StemPlotForLabeling, self).__init__(enableMenu=False, title=title)
        # pg.PlotWidget.__init__(self, enableMenu=False, title=ptitle)
        self.__curveFixed = []
        self.__curve = None
        self.__curveXRange = [0, 0]
        self.__curveYLevel = 1
        self.__curveXCount = 0
        self.__curve_add = None
        self.__curveYLevel_add = 1
        self.x = np.zeros(0)
        self.y = np.zeros(0)
        self.x1 = np.zeros(0)
        self.y1 = np.zeros(0)
        self.scale(200,100)

        self.__colors = (
            (255, 255, 0), # yellow # (255, 204, 0),
            (255, 0, 0), # red
            (0, 255, 0), # lime , green
            (255, 0, 255), # Fuchsia
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
        self.__font = QtGui.QFont()
        self.__font.setPixelSize(15)
        # print('geometry', self.geometry())
        # print('geometry', self.width())

    def addFixedStemGroup(self, xrange, ylevel, c=None, label_string=None):
        x = np.arange(xrange[0],xrange[1])
        y = np.linspace(ylevel, ylevel, xrange[1] - xrange[0])
        cstem = None
        cpoint = None
        text = None
        if c == None:
            cor = 'r'
            cor1 = (20, 20, 200)
        else:
            if c >= len(self.__colors):
                c = c % len(self.__colors)
            c1 = c + 1
            if c1 >= len(self.__colors):
                c1 = c1 % len(self.__colors)
            cor = self.__colors[c]
            cor1 = self.__colors[c1]

        cstem = self.plot(np.repeat(x, 2), np.dstack((np.zeros(y.shape[0], dtype=int), y)).flatten(), pen=pg.mkPen(cor, width=0.5), connect='pairs', name='Stems')
        cpoint = self.plot(x, y, pen=None, symbol='o', symbolPen=cor, symbolBrush=cor1, symbolSize=8, name='Points')
        if label_string != None:
            text = pg.TextItem(label_string, border='w', fill=(0, 0, 255, 150))
            text.setPos(x[-1] + 1, y[-1])
            text.setFont(self.__font)
            self.addItem(text)

        self.__curveFixed.append([cstem, cpoint, text])
        # strpen = pg.mkPen(color='b')
        # self.plot([30], [0.7], name='plotname', pen=strpen, symbol='+', symbolSize=20, symbolBrush=QtGui.QBrush(QtGui.QColor(200, 20, 25)))
        # text = pg.TextItem(html='<div style="text-align: center"><span style="color: #FFF;">This is the</span><br><span style="color: #FF0; font-size: 16pt;">PEAK</span></div>', anchor=(0.7, 0.7), border='w', fill=(0, 0, 255, 100))

    def addFixedStemGroup_org(self, xrange, ylevel, stemColor='r'):
        x = np.arange(xrange[0],xrange[1])
        y = np.linspace(ylevel, ylevel, xrange[1] - xrange[0])
        cstem = None
        cpoint = None
        if stemColor == 'r':
            cstem = self.plot(np.repeat(x, 2), np.dstack((np.zeros(y.shape[0], dtype=int), y)).flatten(), pen=pg.mkPen('r', width=0.5), connect='pairs', name='Stems')
            cpoint = self.plot(x, y, pen=None, symbol='o', symbolPen='b', symbolBrush=QtGui.QBrush(QtGui.QColor(200, 20, 25)), symbolSize=8, name='Points')
            # text = pg.TextItem('234', anchor=(1.7, 1.7), border='w', fill=(0, 0, 255, 150))
            # text.setFont(self.__font)
            # self.addItem(text)
        else:
            cstem = self.plot(np.repeat(x, 2), np.dstack((np.zeros(y.shape[0], dtype=int), y)).flatten(), pen=pg.mkPen('k', width=0.5), connect='pairs', name='Stems')
            cpoint = self.plot(x, y, pen=None, symbol='o', symbolPen='b', symbolBrush=QtGui.QBrush(QtGui.QColor(20, 20, 25)), symbolSize=8, name='Points')
        self.__curveFixed.append([cstem, cpoint])
        # strpen = pg.mkPen(color='b')
        # self.plot([30], [0.7], name='plotname', pen=strpen, symbol='+', symbolSize=20, symbolBrush=QtGui.QBrush(QtGui.QColor(200, 20, 25)))
        # text = pg.TextItem(html='<div style="text-align: center"><span style="color: #FFF;">This is the</span><br><span style="color: #FF0; font-size: 16pt;">PEAK</span></div>', anchor=(0.7, 0.7), border='w', fill=(0, 0, 255, 100))

    def removeLastFixedStemGroup(self):
        if len(self.__curveFixed) == 0:
            return
        remove = self.__curveFixed[-1]
        self.__removeCurve(remove[0])
        self.__removeCurve(remove[1])
        self.__removeCurve(remove[2])
        del self.__curveFixed[-1]

    def removeFirstFixedStemGroup(self):
        if len(self.__curveFixed) == 0:
            return
        remove = self.__curveFixed[0]
        self.__removeCurve(remove[0])
        self.__removeCurve(remove[1])
        self.__removeCurve(remove[2])
        del self.__curveFixed[0]

    def removeAllFixedStemGroup(self):
        for obj in self.__curveFixed:
            self.__removeCurve(obj[0])
            self.__removeCurve(obj[1])
            self.__removeCurve(obj[2])
        self.__curveFixed.clear()

    def setDynamicStem(self, xrange, ylevel):
        '''
         Setup the recording timing graph axis.

        :param xrange: list(start frames:0, number of record frames)
        :param ylevel: list()
        '''
        self.__curveXRange = xrange
        self.__curveYLevel = ylevel[0]
        self.__curveYLevel_add = ylevel[1]
        self.__curveXCount = 0
        self.x = np.zeros(0)
        self.y = np.zeros(0)
        self.x1 = np.zeros(0)
        self.y1 = np.zeros(0)
        self.clearDynamicStem()

    def clearDynamicStem(self):
        if self.__curve != None:
            self.__removeCurve(self.__curve[0])
            self.__removeCurve(self.__curve[1])
            del self.__curve
            self.__curve = None
            self.__curveXCount = 0

        if self.__curve_add != None:
            self.__removeCurve(self.__curve_add[0])
            self.__removeCurve(self.__curve_add[1])
            del self.__curve_add
            self.__curve_add = None

    def incDynamicStem(self, c=0, region_flag=1):
        if self.__curveXCount > self.__curveXRange[1] - self.__curveXRange[0]:
            return
        self.__curveXCount += 1
        self.__setStemData(self.__curveXRange, self.__curveYLevel, self.__curveXCount, c, self.__curveYLevel_add, region=region_flag)

    def decDynamicStem(self):
        if self.__curveXCount <= 0:
            return
        self.__curveXCount -= 1
        self.__setStemData(self.__curveXRange, self.__curveYLevel, self.__curveXCount)

    def setAxisRange(self, xaxisrange, yaxisrange):
        '''
        Set plot axis range

        :param xaxisrange: plot X axis range
        :param yaxisrange: plot Y axis range
        :return:
        '''
        self.setXRange(xaxisrange[0], xaxisrange[1], padding=.01)
        self.setYRange(yaxisrange[0], yaxisrange[1], padding=.01)

    def __creatCurve(self):
        x = np.arange(0,1)
        y = np.linspace(1, 1, 1)
        cstem = self.plot(np.repeat(x, 2), np.dstack((np.zeros(y.shape[0], dtype=int), y)).flatten(), pen=pg.mkPen('b', width=0.5), connect='pairs', name='Stems')
        cpoint = self.plot(x, y, pen=None, symbol='o', symbolPen='b', symbolBrush=QtGui.QBrush(QtGui.QColor(20, 20, 200)), symbolSize=8, name='Points')

    def __removeCurve(self, curve):
        if curve != None:
            self.removeItem(curve)

    def __setStemData(self, xrange, ylevel, count, c=0, ylevel_add=1, region=1):
        # x = np.arange(xrange[0], xrange[0] + count)
        # y = np.linspace(ylevel, ylevel, count)
        if region == 0:
            ylevel = 0.4
        self.x = np.insert(self.x, count-1, np.arange(count-1, count))
        self.y = np.insert(self.y, count-1, ylevel)
        # print(self.x, self.y)
        stemx = np.insert(self.x.reshape(-1, 1), 1, self.x, axis=1).flatten()
        stemy = np.insert(self.y.reshape(-1, 1), 0, 0, axis=1).flatten()

        if self.__curve == None:
            cstem = self.plot(np.repeat(self.x, 2), np.dstack((np.zeros(self.y.shape[0], dtype=int), self.y)).flatten(), pen=pg.mkPen('b', width=0.5), connect='pairs', name='Stems')
            cpoint = self.plot(self.x, self.y, pen=None, symbol='o', symbolPen='b', symbolBrush=QtGui.QBrush(QtGui.QColor(20, 20, 200)), symbolSize=8, name='Points')
            self.__curve = [cstem, cpoint]
        else:
            self.__curve[0].setData(stemx, stemy)
            self.__curve[1].setData(self.x, self.y)

        if c != 0:
            if c >= len(self.__colors):
                c = c % len(self.__colors)
            c1 = c + 1
            if c1 >= len(self.__colors):
                c1 = c1 % len(self.__colors)
            cor = self.__colors[c]
            cor1 = self.__colors[c1]


            self.x1 = np.append(self.x1, [self.x[-1]])
            self.y1 = np.append(self.y1, ylevel_add)
            stemx1 = np.insert(self.x1.reshape(-1, 1), 1, self.x1, axis=1).flatten()
            stemy1 = np.insert(self.y1.reshape(-1, 1), 0, 0, axis=1).flatten()

            if self.__curve_add == None:
                cstem1 = self.plot(stemx1, stemy1,
                                   pen=pg.mkPen(cor, width=0.5), connect='pairs', name='Stems')
                cpoint1 = self.plot(self.x1, self.y1, pen=None, symbol='o', symbolPen=cor, symbolBrush=cor1,
                                    symbolSize=8,
                                    name='Points')
                self.__curve_add = [cstem1, cpoint1]
            else:
                # self.__curve_add.append([cstem1, cpoint1])
                self.__curve_add[0].setData(stemx1, stemy1)
                self.__curve_add[1].setData(self.x1, self.y1)





def __data_update():
    global stempw
    global count

    # y = np.random.randint(100, size=(16))
    # # print(y)
    count += 1
    print(count)
    # if count % 2 == 0:
    #     stempw.clearData()
    # else:
    #     stempw.setYData(y)

    # if count == 1:
    #     stempw.addFixedStemGroup([4,15], 0.8)
    # elif count == 2:
    #     stempw.addFixedStemGroup([20,35], 0.7, 'k')
    # elif count == 3:
    #     stempw.addFixedStemGroup([44,48], 1)
    # elif count == 4:
    #     stempw.removeAllFixedStemGroup()
    # elif count == 5:
    #     stempw.removeFirstFixedStemGroup()
    # elif count == 6:
    #     stempw.addFixedStemGroup([4,15], 0.8)
    # elif count == 7:
    #     stempw.setDynamicStem([2, 20], 1)
    # elif count > 0:
    #     stempw.incDynamicStem()

    if count == 1:
        stempw.addFixedStemGroup([4,15], 0.8, 1, label_string='2')
        stempw.addFixedStemGroup([20,35], 0.7, 2, label_string='3')
        stempw.addFixedStemGroup([40,55], 0.6, 3, label_string='5')
        stempw.addFixedStemGroup([60,75], 0.5, 4, label_string='f')
    elif count == 2:
        # pass
        stempw.setDynamicStem([0, 5], [0.4,0.9])
    elif count == 3:
        stempw.incDynamicStem()
        stempw.incDynamicStem()
        stempw.incDynamicStem()
        stempw.incDynamicStem()
    # elif count == 4:
    #     stempw.decDynamicStem()
    # elif count == 5:
    #     stempw.clearDynamicStem()
    # elif count == 6:
    #     stempw.incDynamicStem()
    #     stempw.incDynamicStem()
    #     stempw.incDynamicStem()


## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys

    count = 0

    app = QtWidgets.QApplication([])
    app.setAttribute(QtCore.Qt.AA_Use96Dpi)


    ## Create window with ImageView widget
    win = QtWidgets.QMainWindow()
    win.resize(600,400)

    w1 = pg.LayoutWidget()
    win.setCentralWidget(w1)
    win.show()
    win.setWindowTitle('pyqtgraph : ImageView')

    stempw = StemPlotForLabeling()

    w1.addWidget(stempw, row=0, col=0)




    qtimer = QtCore.QTimer()
    qtimer.timeout.connect(__data_update)
    qtimer.start(500)

    # stempw.setYData





    # display_plot_image_with_minimal_setup()
    if sys.flags.interactive != 1 or not hasattr(QtCore, 'PYQT_VERSION'):
        QtWidgets.QApplication.instance().exec_()
