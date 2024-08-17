from PySide2 import QtWidgets, QtCore, QtGui
import numpy as np

class ShowResultMainWin(QtWidgets.QWidget):
    closed = QtCore.Signal()
    def __init__(self):
        super(ShowResultMainWin,self).__init__()
        self.stepPlot()
        return

    def stepPlot(self):
            #ges

            ly = QtWidgets.QGridLayout()
            ly.setRowStretch(0,1)
            ly.setRowStretch(1, 1)
            ly.setRowStretch(2, 1)
            self.setLayout(ly)
            wg_exp = QtWidgets.QWidget()
            layout_exp = QtWidgets.QHBoxLayout()
            wg_exp.setLayout(layout_exp)
            wg_Tracking = QtWidgets.QWidget()
            layout_Tracking = QtWidgets.QHBoxLayout()
            wg_Tracking.setLayout(layout_Tracking)
            wg_CFAR = QtWidgets.QWidget()
            layout_CFAR = QtWidgets.QHBoxLayout()
            wg_CFAR.setLayout(layout_CFAR)

            from KKT_Module.KKTGraph.ShowTracking import DrawingPosition
            self.YZ_Tracking_graphic = DrawingPosition('YZ', xRange=[-14, 14], yRange=[0,30])
            self.XZ_Tracking_graphic = DrawingPosition('XZ', xRange=[-14, 14], yRange=[0,30])
            self.XY_Tracking_graphic = DrawingPosition('XY', xRange=[-14, 14], yRange=[0,30])

            layout_Tracking.addWidget(self.XZ_Tracking_graphic)
            layout_Tracking.addWidget(self.YZ_Tracking_graphic)
            layout_Tracking.addWidget(self.XY_Tracking_graphic)

            from KKT_Module.KKTGraph.ShowResults import DrawingResult_GS
            self.Exp_graphic = DrawingResult_GS("Exponential Value")
            self.Sia_Exp_graphic = DrawingResult_GS("Siamese Exponential Value")

            layout_exp.addWidget(self.Exp_graphic)
            layout_exp.addWidget(self.Sia_Exp_graphic)



            self.CFAR_graphic = DrawingResult_GS("CFAR")
            layout_CFAR.addWidget(self.CFAR_graphic)


            self.Exp_graphic.setAxisRange([-1, 17], [0, 1])
            self.Sia_Exp_graphic.setAxisRange([-1, 17], [0, 1])
            self.CFAR_graphic.setAxisRange([-1, 33], [0, 250])

            ly.addWidget(wg_Tracking,0,0,1,2)
            ly.addWidget(wg_exp, 1, 0, 1, 2)
            ly.addWidget(wg_CFAR, 2, 0, 1, 1)


    def setGesture(self, ges):
        self.Exp_graphic.setGestureLabel(ges)

    def setSiaGesture(self, sia_ges):
        self.Sia_Exp_graphic.setGestureLabel(sia_ges)

    def setPosition(self, X=0, Y=0, Z=0):
        X = np.asarray([X])
        Y = np.asarray([Y])
        Z = np.asarray([Z])
        self.XY_Tracking_graphic.setData(X, Y)
        self.XZ_Tracking_graphic.setData(X, Z)
        self.YZ_Tracking_graphic.setData(Y, Z)
        pass

    def setExponential(self, data):
        self.Exp_graphic.setData(data)
        pass

    def setSiaExponential(self, data):
        self.Sia_Exp_graphic.setData(data)
        pass

    def setCFAR(self, data):
        self.CFAR_graphic.setData(data)

        pass
    def setImax(self, IMax):
        self.CFAR_graphic.setGestureLabel(IMax)



if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    app.setAttribute(QtCore.Qt.AA_Use96Dpi)
    win = QtWidgets.QMainWindow()
    win.resize(1000,1000)
    wg = ShowResultMainWin()
    win.setCentralWidget(wg)
    win.show()

    app.exec_()
