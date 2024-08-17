import pyqtgraph as pg
import numpy as np
from PySide2 import QtWidgets,QtCore,QtGui
from KKT_Module.KKTUtility.qt_obj import OKMessageBox
import time

class PlotData2(pg.PlotWidget):
    pg.setConfigOption('foreground', 'k')  # Default foreground color for text, lines, axes, etc.
    pg.setConfigOption('background', None)  # Default background for GraphicsView.
    pg.setConfigOptions(antialias=True)  # Draw lines with smooth edges at the cost of reduced performance.
    def __init__(self,title='test plot'):
        super(PlotData2, self).__init__()
        self.XRange = [0, 100]
        self.YRange = [-2**8+10, 2**8-10]
        self.xrange_label = np.asarray([i for i in range(1000)])
        self._title = title
        self.axis_label = {'bottom': "X", 'left': 'Y'}

        pass

    def setupGUI(self):
        self.PI = self.getPlotItem()
        self.PI.setTitle(self._title)
        self.scale(2,3)


    def initPlots(self):
        self.getAxis('bottom').setLabel(text=self.axis_label['bottom'])
        self.getAxis('left').setLabel(text=self.axis_label['left'])
        self.setAxisLabel(self.axis_label['bottom'], self.axis_label['left'])
        self.setAxisRange(self.XRange, self.YRange)
        pg.setConfigOption('foreground', 'k')  # Default foreground color for text, lines, axes, etc.
        pg.setConfigOption('background', None)  # Default background for GraphicsView.
        pg.setConfigOptions(antialias=True)  # Draw lines with smooth edges at the cost of reduced performance.
        pass

    def setAxisLabel(self, bottom, left):
        self.getAxis('bottom').setLabel(text=bottom)
        self.getAxis('left').setLabel(text=left)

    def setAxisRange(self, XRange:list, YRange:list):
        self.setXRange(min =XRange[0], max=XRange[1])
        self.setYRange(min =YRange[0], max=YRange[1])

    def setParameters(self,**kwargs):
        for k, v in kwargs.items():
            # assert hasattr(self, k), 'No attribute : {}'.format(k)
            if not hasattr(self, k):
                continue
            setattr(self, k, v)
        pass

class ADCRawData(PlotData2):
    def __init__(self, title='test plot'):
        super(ADCRawData, self).__init__(title)
        # parameters
        self._overlap_num = 32
        self.xrange_label = np.linspace(0, 127, 128)
        self._start = 1
        self._end = 5
        self.plot_list = []
        self.mean = False
        self.setupGUI()
        self.initPlots()
        pass

    def setupGUI(self):
        super(ADCRawData, self).setupGUI()
        self.mean_plot = self.plot(pen=6)

        for i in range(self._overlap_num):
            PI = self.plot(pen=(i, 3))
            self.plot_list.append(PI)

    def initPlots(self):
        super(ADCRawData, self).initPlots()
        if self.mean:
            self.setMeanItems()
        else:
            self.setOverlapItems(self._start,self._end)

    def setMeanItems(self):
        self.clear()
        self.addItem(self.mean_plot)

    def setOverlapItems(self, start, end):
        self.clear()
        for i in range(start-1, end):
            self.addItem(self.plot_list[i])
            pass
        self.setOverlapRange(start,end)

    def setAxisRange(self, XRange, YRange):
        self.setLimits(xMin=XRange[0]-5, xMax=XRange[1]+5, minYRange=100, maxXRange=XRange[1]+10)
        super(ADCRawData, self).setAxisRange(XRange, YRange)



    def setData(self, res):
        if self.mean:
            res = np.mean(res, axis=0)
            self.mean_plot.setData(res)
        else:
            for i in range(self._start -1 ,self._end):
                self.plot_list[i].setData(res[i])

    def enableMean(self, enable):
        self.mean = enable
        self.initPlots()

    def enableOverlap(self):
        self.mean = False
        self.initPlots()

    def setOverlapRange(self, start, end):
        self._start = int(start)
        self._end = int(end)

class FFTData(PlotData2):
    def __init__(self, title='test plot'):
        super(FFTData, self).__init__(title)
        # parameters
        self._overlap_num = 32
        self.xrange_label = np.linspace(0, 68, 32)
        self._start = 1
        self._end = 5
        self.plot_list = []
        self.mean = False
        self.setupGUI()
        self.initPlots()
        pass

    def setupGUI(self):
        super(FFTData, self).setupGUI()
        self.mean_plot = self.plot(pen=6)

        for i in range(self._overlap_num):
            PI = self.plot(pen=(i, 3))
            self.plot_list.append(PI)

    def initPlots(self):
        super(FFTData, self).initPlots()
        self.setPlotItems()
        self.xrange_label = np.linspace(0, self.XRange[1], 32)

    def setPlotItems(self):
        if self.mean:
            self.setMeanItems()
        else:
            self.setOverlapItems(self._start, self._end)

    def setMeanItems(self):
        self.clear()
        self.addItem(self.mean_plot)

    def setOverlapItems(self, start, end):
        self.clear()
        for i in range(start-1, end):
            self.addItem(self.plot_list[i])
            pass
        self.setOverlapRange(start, end)

    def setAxisRange(self, XRange, YRange):
        self.setLimits(yMin=0, xMin=XRange[0]-5, xMax=XRange[1]+5, minYRange=100, maxXRange=XRange[1]+10)
        super(FFTData, self).setAxisRange(XRange, YRange)


    def setData(self, res):
        if self.mean:
            res = np.mean(res, axis=0)
            self.mean_plot.setData(self.xrange_label, res)
        else:
            for i in range(self._start -1 ,self._end):
                self.plot_list[i].setData(self.xrange_label, res[i])

    def enableMean(self, enable=True):
        self.mean = enable
        self.setPlotItems()

    def enableOverlap(self):
        self.mean = False
        self.initPlots()

    def setOverlapRange(self, start, end):
        self._start = int(start)
        self._end = int(end)

from KKT_Module.KKTUtility.qt_obj import SubWidgetQFrame
class DataPlotWidget(SubWidgetQFrame):
    sig_Press_Default = QtCore.Signal()
    sig_Clicked_Mean = QtCore.Signal(bool)
    sig_Changed_Spin = QtCore.Signal(object)
    def __init__(self):
        super(DataPlotWidget, self).__init__()
        self._Mean = False
        self.start = 1
        self.end = 5
        self.setupGUI()

    def setupGUI(self):
        self.check_mean = QtWidgets.QCheckBox('Mean')
        self.check_mean.clicked.connect(lambda: self._clickMeanCheck())
        self.check_mean.setChecked(self._Mean)

        pb_default_axis = QtWidgets.QPushButton('Default Axis')
        pb_default_axis.clicked.connect(lambda: self._setDefaultAxis())


        from KKT_Module.KKTUtility.qt_obj import SpinBoxListWidget

        self.spin_chirps = SpinBoxListWidget(items={'Start Chirp Number': {'Value': self.start,
                                                                    'Range': [1, 32]},
                                                    'End Chirp Number': {'Value': self.end,
                                                                  'Range': [1, 32]},
                                                    }, cols=1)
        self.spin_chirps.change_Signal.connect(lambda: self._changeSpinBox())
        self.grid.addWidget(pb_default_axis, 0,0,1,1)
        self.grid.addWidget(self.check_mean, 0,1,1,1)
        self.grid.addWidget(self.spin_chirps,1,0,1,2)

    def _clickMeanCheck(self):
        self.sig_Clicked_Mean.emit(self.check_mean.isChecked())
        self.spin_chirps.setEnabled(True)
        if self.check_mean.isChecked():
            self.spin_chirps.setEnabled(False)
        pass

    def _setDefaultAxis(self):
        self.sig_Press_Default.emit()
        pass

    def _changeSpinBox(self):
        status = self.spin_chirps.getItemsStatus()
        start = status.get('Start Chirp Number')['Spin'].value()
        end = status.get('End Chirp Number')['Spin'].value()
        if start > end:
            self.spin_chirps.setValue('Start Chirp Number',self.start)
            self.spin_chirps.setValue('End Chirp Number',self.end)
            OKMessageBox(QtWidgets.QMessageBox.Warning, 'End Chirp Number must be greater than Start Chirp Number !')
        else:
            self.start = start
            self.end = end
            self.sig_Changed_Spin.emit(status)


#==================== old ================================

class PlotData(QtWidgets.QWidget):
    pg.setConfigOption('foreground', 'k')  # Default foreground color for text, lines, axes, etc.
    pg.setConfigOption('background', None)  # Default background for GraphicsView.
    pg.setConfigOptions(antialias=True)  # Draw lines with smooth edges at the cost of reduced performance.
    def __init__(self,title='test plot'):
        super(PlotData, self).__init__()
        self.XRange = [0, 1000]
        self.YRange = [2**15+10, -2**15-10]
        self.xrange_label = np.asarray([i for i in range(1000)])
        self._title = title
        self.setupGUI()
        pass

    def setupGUI(self):
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)
        self.PW = pg.PlotWidget()
        self.PW.scale(2,3)
        self.PW.getAxis('bottom').setLabel(text='X')
        self.PW.getAxis('left').setLabel(text='Y')
        lb = QtWidgets.QLabel(self._title)
        lb.setAlignment(QtGui.Qt.AlignCenter)
        self.setAxisToDefault()
        layout.addWidget(lb)
        layout.addWidget(self.PW)

    def setDefaultAxis(self, xMin=None, xMax=None, yMin=None, yMax=None):
        if xMin is not None:
            self.XRange[0] = xMin
        if xMax is not None:
            self.XRange[1] = xMax
        if yMin is not None:
            self.YRange[0] = yMin
        if yMax is not None:
            self.YRange[1] = yMax
        self.setAxisToDefault()

    def setAxisToDefault(self):
        self.setRange(self.XRange, self.YRange)

    def setAxisLabel(self, bottom, left):
        self.PW.getAxis('bottom').setLabel(text=bottom)
        self.PW.getAxis('left').setLabel(text=left)

    def setRange(self, XRange, YRange):
        x_gap = (XRange[1]-XRange[0])/20
        y_gap = (YRange[1]-YRange[0])/20
        self.PW.setXRange(min =XRange[0]-x_gap, max=XRange[1])
        self.PW.setYRange(min =YRange[0]-y_gap, max=YRange[1])

    def setXrangeLabel(self, start, stop, num):
        self.xrange_label = np.linspace(start, stop, num)
        x_gap = (self.xrange_label[-1]-self.xrange_label[0])/20
        self.PW.setLimits(xMin=self.xrange_label[0]-x_gap, xMax=self.xrange_label[-1])
        self.setDefaultAxis(xMin=self.xrange_label[0], xMax=self.xrange_label[-1])

class PlotOverlapData2(PlotData):
    def __init__(self, title='test plot'):
        super(PlotOverlapData2, self).__init__(title)
        # parameters
        self._overlap_num = 32
        self._start = 1
        self._end = 5

        self.plot_list = []

        self.initPlots()
        pass

    def initPlots(self):
        self.PW.clear()
        self.plot_list = []
        for i in range(self._end - self._start+1):
            PI = self.PW.plot(pen=(i,3))
            self.plot_list.append(PI)

    def setData(self, res):
        for i in range(self._end - self._start + 1 ):
            self.plot_list[i].setData(self.xrange_label, res[self._start+i-1])

    def setOverlapRange(self, start, end):
        self._start = int(start)
        self._end = int(end)
        self.initPlots()

class MeanDataPlot2(PlotData):
    def __init__(self, title='test plot'):
        super(MeanDataPlot2, self).__init__(title)
        self.initPLots()
        pass

    def initPLots(self):
        self.PI = self.PW.plot(pen=6)

    def setData(self, res):
        res = np.mean(res, axis=0)
        self.PI.setData(self.xrange_label,res)

class ADCRawWidget(QtWidgets.QWidget):
    pg.setConfigOption('foreground', 'k')  # Default foreground color for text, lines, axes, etc.
    pg.setConfigOption('background', None)  # Default background for GraphicsView.
    pg.setConfigOptions(antialias=True)  # Draw lines with smooth edges at the cost of reduced performance.
    def __init__(self):
        super(ADCRawWidget, self).__init__()
        self._chirp = 32
        self._sample = 128
        self._Mean = False
        self.setupGUI()
        self.plotMean(self._Mean)

    def setChirp(self, chirp):
        self._chirp = chirp
        spin_boxes = self.spin_chirps.getItemsStatus()
        for k,v in spin_boxes.items():
            v.get('Spin').setRange(1, chirp)

    def enableWidgets(self, check_mean=False, SpinBox=False):
        if check_mean:
            self.layout.addWidget(self.check_mean, 2, 1, 1, 1, alignment=QtGui.Qt.AlignRight)
        if SpinBox:
            self.layout.addWidget(self.spin_chirps, 3, 0, 1, 2)

    def setupGUI(self):
        self.layout = QtWidgets.QGridLayout()
        self.setLayout(self.layout)
        self.layout.setColumnStretch(0, 1)
        self.layout.setColumnStretch(1, 1)
        self.layout.setColumnStretch(2, 1)
        self.layout.setColumnStretch(3, 1)
        self.check_mean = QtWidgets.QCheckBox('Mean')
        self.check_mean.clicked.connect(lambda: self._clickMeanCheck())
        self.check_mean.setChecked(self._Mean)

        pb_default_axis = QtWidgets.QPushButton('Default Axis')
        pb_default_axis.clicked.connect(lambda :self._setDefaultAxis())
        self.layout.addWidget(pb_default_axis, 2, 0, 1, 1)

        from KKT_Module.KKTUtility.qt_obj import SpinBoxListWidget

        self.spin_chirps = SpinBoxListWidget(items={'Start Chirp Number':{'Value':1,
                                                            'Range':[1,32]},
                                                   'End Chirp  Number': {'Value': 5,
                                                             'Range': [1, 32]},
                                                   }, cols=1)
        self.spin_chirps.change_Signal.connect(lambda :self._changeSpinBox())



        self.ch1 = PlotOverlapData2(title='CH1 ADC raw data')
        self.ch1.setAxisLabel(bottom='Sample numbers', left='Amplitude')
        self.ch1.PW.setLimits(xMax=70, xMin=-5)
        self.ch1.setDefaultAxis(0, int(self._sample/2))
        self.ch1.xrange_label = np.linspace(0, int(self._sample/2), int(self._sample/2))

        self.ch2 = PlotOverlapData2(title='CH2 ADC raw data')
        self.ch2.setAxisLabel(bottom='Sample numbers', left='Amplitude')
        self.ch2.PW.setLimits(xMax=70, xMin=-5)
        self.ch2.setDefaultAxis(0, int(self._sample / 2))
        self.ch2.xrange_label = np.linspace(1, int(self._sample / 2), int(self._sample / 2))

        self.ch1_mean = MeanDataPlot2(title='CH1 ADC raw data')
        self.ch1_mean.setAxisLabel(bottom='Sample numbers', left='Amplitude')
        self.ch1_mean.PW.setLimits(xMax=70, xMin=-5)
        self.ch1_mean.setDefaultAxis(0, int(self._sample / 2))
        self.ch1_mean.xrange_label = np.linspace(1, int(self._sample / 2), int(self._sample / 2))

        self.ch2_mean = MeanDataPlot2(title='CH2 ADC raw data')
        self.ch2_mean.setAxisLabel(bottom='Sample numbers', left='Amplitude')
        self.ch2_mean.PW.setLimits(xMax=70, xMin=-5)
        self.ch2_mean.setDefaultAxis(0, int(self._sample / 2))
        self.ch2_mean.xrange_label = np.linspace(1, int(self._sample / 2), int(self._sample / 2))

        self.layout.addWidget(self.ch1, 0, 0, 1, 2)
        self.layout.addWidget(self.ch2, 0, 2, 1, 2)
        self.layout.addWidget(self.ch1_mean, 0, 0, 1, 2)
        self.layout.addWidget(self.ch2_mean, 0, 2, 1, 2)

    def _setDefaultAxis(self):
        self.ch1.setDefaultAxis()
        self.ch1_mean.setDefaultAxis()
        self.ch2.setDefaultAxis()
        self.ch2_mean.setDefaultAxis()
        pass

    def _changeSpinBox(self):
        items = self.spin_chirps.getItemsStatus()
        start = items['Start chirp']['Value']
        end = items['End chirp']['Value']
        self.ch1.setOverlapRange(start,end)
        self.ch2.setOverlapRange(start, end)
        pass

    def _clickMeanCheck(self):
        mean = self.check_mean.isChecked()
        self.plotMean(mean)
        self.spin_chirps.setEnabled(not mean)

    def setData(self, res):
        up_chirp = int(self._sample / 2)
        if self._Mean:
            self.ch1_mean.setData(res[0][:,:up_chirp])
            self.ch2_mean.setData(res[1][:,:up_chirp])
            return
        self.ch1.setData(res[0][:,:up_chirp])
        self.ch2.setData(res[1][:,:up_chirp])


    def plotMean(self, mean:bool):
        self._Mean = mean
        self.ch1_mean.setVisible(mean)
        self.ch2_mean.setVisible(mean)
        self.ch1.setVisible(not mean)
        self.ch2.setVisible(not mean)

class FFTWidget(QtWidgets.QWidget):
    pg.setConfigOption('foreground', 'k')  # Default foreground color for text, lines, axes, etc.
    pg.setConfigOption('background', None)  # Default background for GraphicsView.
    pg.setConfigOptions(antialias=True)  # Draw lines with smooth edges at the cost of reduced performance.
    def __init__(self):
        super(FFTWidget, self).__init__()
        self._chirp = 32
        self._sample = 128
        self._Mean = False
        self.setupGUI()
        self.plotMean(self._Mean)

    def setChirp(self, chirp):
        self._chirp = chirp
        spin_boxes = self.spin_chirps.getItemsStatus()
        for k,v in spin_boxes.items():
            v.get('Spin').setRange(1, chirp)

    def enableWidgets(self, check_mean=False, SpinBox=False):
        if check_mean:
            self.layout.addWidget(self.check_mean, 2, 1, 1, 1, alignment=QtGui.Qt.AlignRight)
        if SpinBox:
            self.layout.addWidget(self.spin_chirps, 3, 0, 1, 2)

    def setupGUI(self):
        self.layout = QtWidgets.QGridLayout()
        self.setLayout(self.layout)
        self.layout.setColumnStretch(0, 1)
        self.layout.setColumnStretch(1, 1)
        self.layout.setColumnStretch(2, 1)
        self.layout.setColumnStretch(3, 1)
        self.check_mean = QtWidgets.QCheckBox('Mean')
        self.check_mean.clicked.connect(lambda: self._clickMeanCheck())
        self.check_mean.setChecked(self._Mean)

        pb_default_axis = QtWidgets.QPushButton('Default Axis')
        pb_default_axis.clicked.connect(lambda :self._setDefaultAxis())
        self.layout.addWidget(pb_default_axis, 2, 0, 1, 1)

        from KKT_Module.KKTUtility.qt_obj import SpinBoxListWidget

        self.spin_chirps = SpinBoxListWidget(items={'Start Chirp Number':{'Value':1,
                                                            'Range':[1,32]},
                                                   'End Chirp Number': {'Value': 5,
                                                             'Range': [1, 32]},
                                                   }, cols=1)
        self.spin_chirps.change_Signal.connect(lambda :self._changeSpinBox())



        self.ch1 = PlotOverlapData2(title='CH1 FFT')
        self.ch1.setAxisLabel(bottom='Distance (cm)', left='Amplitude')
        self.ch1.PW.setLimits(yMin=0, xMin=-5)
        self.ch1.setDefaultAxis(xMin=0, xMax=32, yMin=0, yMax=200000)
        self.ch1.xrange_label = np.linspace(1, int(self._sample/2), int(self._sample/2))

        self.ch2 = PlotOverlapData2(title='CH2 FFT')
        self.ch2.setAxisLabel(bottom='Distance (cm)', left='Amplitude')
        self.ch2.PW.setLimits(yMin=0, xMin=-5)
        self.ch2.setDefaultAxis(xMin=0, xMax=32, yMin=0, yMax=200000)
        self.ch2.xrange_label = np.linspace(1, int(self._sample / 2), int(self._sample / 2))

        self.ch1_mean = MeanDataPlot2(title='CH1 FFT')
        self.ch1_mean.setAxisLabel(bottom='Distance (cm)', left='Amplitude')
        self.ch1_mean.PW.setLimits(yMin=0, xMin=-5)
        self.ch1_mean.setDefaultAxis(xMin=0, xMax=32, yMin=0, yMax=200000)
        self.ch1_mean.xrange_label = np.linspace(1, int(self._sample / 2), int(self._sample / 2))

        self.ch2_mean = MeanDataPlot2(title='CH2 FFT')
        self.ch2_mean.setAxisLabel(bottom='Distance (cm)', left='Amplitude')
        self.ch2_mean.PW.setLimits(yMin=0, xMin=-5)
        self.ch2_mean.setDefaultAxis(xMin=0, xMax=32, yMin=0, yMax=200000)
        self.ch2_mean.xrange_label = np.linspace(1, int(self._sample / 2), int(self._sample / 2))

        self.layout.addWidget(self.ch1, 0, 0, 1, 2)
        self.layout.addWidget(self.ch2, 0, 2, 1, 2)
        self.layout.addWidget(self.ch1_mean, 0, 0, 1, 2)
        self.layout.addWidget(self.ch2_mean, 0, 2, 1, 2)

    def _setDefaultAxis(self):
        self.ch1.setDefaultAxis()
        self.ch1_mean.setDefaultAxis()
        self.ch2.setDefaultAxis()
        self.ch2_mean.setDefaultAxis()
        pass

    def _changeSpinBox(self):
        items = self.spin_chirps.getItemsStatus()
        start = items['Start chirp']['Value']
        end = items['End chirp']['Value']
        self.ch1.setOverlapRange(start,end)
        self.ch2.setOverlapRange(start, end)
        pass

    def _clickMeanCheck(self):
        mean = self.check_mean.isChecked()
        self.plotMean(mean)
        self.spin_chirps.setEnabled(not mean)

    def setData(self, res):
        up_chirp = int(self._sample / 2)
        if self._Mean:
            self.ch1_mean.setData(res[0][:,:up_chirp])
            self.ch2_mean.setData(res[1][:,:up_chirp])
            return
        self.ch1.setData(res[0][:,:up_chirp])
        self.ch2.setData(res[1][:,:up_chirp])
        # print(self.ch1.XRange)

    def plotMean(self, mean:bool):
        self._Mean = mean
        self.ch1_mean.setVisible(mean)
        self.ch2_mean.setVisible(mean)
        self.ch1.setVisible(not mean)
        self.ch2.setVisible(not mean)

    def setXrangeLabel(self, start, stop, num):
        self.ch1.setXrangeLabel(start, stop, num)
        self.ch2.setXrangeLabel(start, stop, num)
        self.ch1_mean.setXrangeLabel(start, stop, num)
        self.ch2_mean.setXrangeLabel(start, stop, num)

class FFTPlot(QtWidgets.QWidget):
    pg.setConfigOption('foreground', 'k')  # Default foreground color for text, lines, axes, etc.
    pg.setConfigOption('background', None)  # Default background for GraphicsView.
    pg.setConfigOptions(antialias=True)  # Draw lines with smooth edges at the cost of reduced performance.
    def __init__(self):
        super(FFTPlot, self).__init__()
        self._chirp = 32
        self._sample = 128
        self._Mean = False
        self.setupGUI()
        self.plotMean(self._Mean)

    def setChirp(self, chirp):
        self._chirp = chirp
        spin_boxes = self.spin_chirps.getItemsStatus()
        for k,v in spin_boxes.items():
            v.get('Spin').setRange(1, chirp)

    def enableWidgets(self, check_mean=False, SpinBox=False):
        if check_mean:
            self.layout.addWidget(self.check_mean, 2, 1, 1, 1, alignment=QtGui.Qt.AlignRight)
        if SpinBox:
            self.layout.addWidget(self.spin_chirps, 3, 0, 1, 2)

    def setupGUI(self):
        self.layout = QtWidgets.QGridLayout()
        self.setLayout(self.layout)
        self.layout.setColumnStretch(0, 1)
        self.layout.setColumnStretch(1, 1)
        self.layout.setColumnStretch(2, 1)
        self.layout.setColumnStretch(3, 1)
        self.check_mean = QtWidgets.QCheckBox('Mean')
        self.check_mean.clicked.connect(lambda: self._clickMeanCheck())
        self.check_mean.setChecked(self._Mean)

        pb_default_axis = QtWidgets.QPushButton('Default Axis')
        pb_default_axis.clicked.connect(lambda :self._setDefaultAxis())
        # self.layout.addWidget(pb_default_axis, 2, 0, 1, 1)

        from KKT_Module.KKTUtility.qt_obj import SpinBoxListWidget

        self.spin_chirps = SpinBoxListWidget(items={'Start Chirp Number':{'Value':1,
                                                            'Range':[1,32]},
                                                   'End Chirp Number': {'Value': 5,
                                                             'Range': [1, 32]},
                                                   }, cols=1)
        self.spin_chirps.change_Signal.connect(lambda :self._changeSpinBox())



        self.ch1 = PlotOverlapData2(title='CH1 FFT')
        self.ch1.setAxisLabel(bottom='Distance (cm)', left='Amplitude')
        self.ch1.PW.setLimits(yMin=0, xMin=0)
        self.ch1.setDefaultAxis(xMin=0, xMax=32, yMin=0, yMax=200000)
        self.ch1.xrange_label = np.linspace(1, int(self._sample/2), int(self._sample/2))

        self.ch1_mean = MeanDataPlot2(title='CH1 FFT')
        self.ch1_mean.setAxisLabel(bottom='Distance (cm)', left='Amplitude')
        self.ch1_mean.PW.setLimits(yMin=0, xMin=-5)
        self.ch1_mean.setDefaultAxis(xMin=0, xMax=32, yMin=0, yMax=200000)
        self.ch1_mean.xrange_label = np.linspace(1, int(self._sample / 2), int(self._sample / 2))



        self.layout.addWidget(self.ch1, 0, 0, 1, 4)
        self.layout.addWidget(self.ch1_mean, 0, 0, 1, 4)
        # self.layout.addWidget(self.spin_chirps, 1, 0, 1, 4)
        # self.layout.addWidget(self.check_mean, 3, 0, 1, 4)

    def _setDefaultAxis(self):
        self.ch1.setDefaultAxis()
        self.ch1_mean.setDefaultAxis()

        pass

    def _changeSpinBox(self):
        items = self.spin_chirps.getItemsStatus()
        start = items['Start Chirp Number']['Value']
        end = items['End Chirp Number']['Value']
        self.ch1.setOverlapRange(start,end)

        pass

    def _clickMeanCheck(self):
        mean = self.check_mean.isChecked()
        self.plotMean(mean)
        self.spin_chirps.setEnabled(not mean)

    def setData(self, res):
        up_chirp = int(self._sample / 2)
        if self._Mean:
            self.ch1_mean.setData(res[0][:,:up_chirp])

            return
        self.ch1.setData(res[:,:up_chirp])


    def plotMean(self, mean:bool):
        self._Mean = mean
        self.ch1_mean.setVisible(mean)
        self.ch1.setVisible(not mean)


    def setXrangeLabel(self, start, stop, num):
        self.ch1.setXrangeLabel(start, stop, num)
        self.ch1_mean.setXrangeLabel(start, stop, num)



#=======================New widget========================
class FFTPlots(QtWidgets.QWidget):
    def __init__(self):
        super(FFTPlots, self).__init__()
        self._chirp = 32
        self._sample = 128
        self._Mean = False
        self.setupGUI()


    def setChirp(self, chirp):
        self._chirp = chirp
        spin_boxes = self.mean_wg.spin_chirps.getItemsStatus()
        for k,v in spin_boxes.items():
            v.get('Spin').setRange(1, chirp)

    def enableWidgets(self,mean=False):
        if mean:
            self.ly.addWidget(self.mean_wg, 1, 0, 1, 1)
        else:
            self.ly.removeWidget(self.mean_wg)

    def setupGUI(self):
        self.ly = QtWidgets.QGridLayout()
        self.setLayout(self.ly)
        self.ch1_FFT = FFTData('CH1 FFT')
        self.ch1_FFT.setParameters(XRange=[0, 70], YRange=[0, 200000],axis_label = {'bottom': "Distance (cm)", 'left':'Amplitude'})
        self.ch2_FFT = FFTData('CH2 FFT')
        self.ch2_FFT.setParameters(XRange=[0, 70], YRange=[0, 200000],
                             axis_label={'bottom': "Distance (cm)", 'left': 'Amplitude'})
        self.initPlots()
        self.mean_wg = DataPlotWidget()
        self.mean_wg.sig_Clicked_Mean.connect(self._clickMeanCheck)
        self.mean_wg.sig_Changed_Spin.connect(self._changeSpinBox)
        self.mean_wg.sig_Press_Default.connect(self._setDefaultAxis)

        self.ly.addWidget(self.ch1_FFT,0,0,1,1)
        self.ly.addWidget(self.ch2_FFT, 0, 1, 1, 1)

    def getSettingWidget(self):
        return self.mean_wg

    def _setDefaultAxis(self):
        self.initPlots()
        pass

    def _changeSpinBox(self, item):
        start = item['Start Chirp Number']['Value']
        end = item['End Chirp Number']['Value']
        self.ch1_FFT.setOverlapItems(start, end)
        self.ch2_FFT.setOverlapItems(start, end)
        pass

    def _clickMeanCheck(self, mean):
        self.ch1_FFT.enableMean(enable=mean)
        self.ch2_FFT.enableMean(enable=mean)


    def setData(self, res):
        up_chirp = int(self._sample / 2)
        self.ch1_FFT.setData(res[0][:,: up_chirp])
        self.ch2_FFT.setData(res[1][:, :up_chirp])

    def initPlots(self):
        self.ch1_FFT.initPlots()
        self.ch2_FFT.initPlots()

    def setParameters(self,**kwargs):
        self.ch1_FFT.setParameters(**kwargs)
        self.ch2_FFT.setParameters(**kwargs)
        self.initPlots()
        pass

    def enableOverlap(self):
        self.ch1_FFT.enableOverlap()
        self.ch2_FFT.enableOverlap()

class ADCPlots(QtWidgets.QWidget):
    def __init__(self):
        super(ADCPlots, self).__init__()
        self._chirp = 32
        self._sample = 128
        self._Mean = False
        self.setupGUI()


    def setChirp(self, chirp):
        self._chirp = chirp
        spin_boxes = self.mean_wg.spin_chirps.getItemsStatus()
        for k,v in spin_boxes.items():
            v.get('Spin').setRange(1, chirp)

    def enableWidgets(self, mean=False ):
        if mean:
            self.ly.addWidget(self.mean_wg, 1, 0, 1, 1)
        else:
            self.ly.removeWidget(self.mean_wg)


    def setupGUI(self):
        self.ly = QtWidgets.QGridLayout()
        self.setLayout(self.ly)
        self.ch1_ADC = ADCRawData('CH1 ADC Raw')
        self.ch1_ADC.setParameters(XRange=[0, self._sample/2], YRange=[-2**15, 2**15],axis_label = {'bottom': "Samples", 'left':'Amplitude'})
        self.ch2_ADC = ADCRawData('CH2 ADC Raw')
        self.ch2_ADC.setParameters(XRange=[0, self._sample/2], YRange=[-2**15, 2**15],
                             axis_label={'bottom': "Samples", 'left': 'Amplitude'})
        self.initPlots()
        self.mean_wg = DataPlotWidget()
        self.mean_wg.sig_Clicked_Mean.connect(self._clickMeanCheck)
        self.mean_wg.sig_Changed_Spin.connect(self._changeSpinBox)
        self.mean_wg.sig_Press_Default.connect(self._setDefaultAxis)

        self.ly.addWidget(self.ch1_ADC,0,0,1,1)
        self.ly.addWidget(self.ch2_ADC, 0, 1, 1, 1)
        # ly.addWidget(self.mean_wg, 1, 0, 1, 1)

        self.enableWidgets()

    def _setDefaultAxis(self):
        self.initPlots()
        pass

    def _changeSpinBox(self, item):
        start = item['Start Chirp Number']['Value']
        end = item['End Chirp Number']['Value']
        self.ch1_ADC.setOverlapItems(start, end)
        self.ch2_ADC.setOverlapItems(start, end)
        pass

    def _clickMeanCheck(self, mean):
        self.ch1_ADC.enableMean(enable=mean)
        self.ch2_ADC.enableMean(enable=mean)


    def setData(self, res):
        up_chirp = int(self._sample / 2)
        self.ch1_ADC.setData(res[0][:,: up_chirp])
        self.ch2_ADC.setData(res[1][:, :up_chirp])

    def initPlots(self):
        self.ch1_ADC.initPlots()
        self.ch2_ADC.initPlots()

    def setParameters(self,**kwargs):
        self.ch1_ADC.setParameters(**kwargs)
        self.ch2_ADC.setParameters(**kwargs)
        pass

    def enableOverlap(self):
        self.ch1_ADC.enableOverlap()
        self.ch2_ADC.enableOverlap()

    def getSettingWidget(self):
        return self.mean_wg

class FFT(QtWidgets.QWidget):
    def __init__(self):
        super(FFT, self).__init__()
        self.setupGUI()
        pass
    def setupGUI(self):
        ly = QtWidgets.QVBoxLayout()
        self.setLayout(ly)
        self.p = FFTData('FFT')
        # self.p.setAxisLabel(bottom='Distance (cm)', left='Amplitude')
        self.p.setParameters(XRange=[0, 70], YRange=[0, 200000],axis_label = {'bottom': "Distance (cm)", 'left':'Amplitude'})
        self.p.initPlots()
        self.p.enableOverlap()
        self.w = DataPlotWidget()
        self.w.sig_Clicked_Mean.connect(self.p.enableMean)
        self.w.sig_Press_Default.connect(self.p.initPlots)
        self.w.sig_Changed_Spin.connect(self.changeSpin)
        ly.addWidget(self.p)
        ly.addWidget(self.w)
        pass

    def changeSpin(self, status):
        start = status.get('Start chirp')
        end = status.get('End chirp')
        self.p.setOverlapItems(start['Value'], end['Value'])

    def setData(self,res):
        self.p.setData(res[1])

    def setChirp(self,chirp):
        pass

    def setParameters(self, **kwargs):
        # for k, v in kwargs.items():
        #     assert hasattr(self, k), 'No attribute : {}'.format(k)
        #     setattr(self, k, v)
        # pass
        XRange = kwargs.get('XRange')
        self.p.setParameters(XRange=XRange)

    def getSettingWidget(self):
        return self.w







if __name__ == '__main__':
    s = time.time()
    def updateplot():
        global s
        res = np.random.randint(-2 ** 15, 2 ** 15 - 1, (2,32,128), dtype='int16')
        # res = np.random.randint(0, 68.7, (2,32,32), dtype='int16')
        p.setData(res)
        print('fps : {}'.format(1 / (time.time() - s)))
        s = time.time()

    def changeSpin(status):
        start = status.get('Start chirp')
        end = status.get('End chirp')
        p.setOverlapItems(start['Value'], end['Value'])
    app =QtWidgets.QApplication([])
    win = QtWidgets.QMainWindow()
    win.resize(600,600)
    wg = QtWidgets.QWidget()
    ly = QtWidgets.QVBoxLayout()
    wg.setLayout(ly)
    T = QtCore.QTimer()
    # p = ADCRawWidget()
    # p = ADCRawData('ADC Raw')
    # p = FFTData('FFT')
    # p= FFTPlots()
    p = ADCPlots()
    # p.setAxisRange([0,128], [-2 ** 15, 2 ** 15 - 1])
    # p.setParameters(XRange=[0,70], YRange=[0, 128])
    p.enableWidgets(True)
    p.initPlots()
    p.enableOverlap()
    # w = DataPlotWidget()
    # w.sig_Clicked_Mean.connect(p.enableMean)
    # w.sig_Press_Default.connect(p.initPlots)
    # w.sig_Changed_Spin.connect(changeSpin)
    ly.addWidget(p)
    # ly.addWidget(w)


    win.setCentralWidget(wg)
    win.show()
    T.timeout.connect(lambda: updateplot())
    T.start(40)
    app.exec_()
    pass