import os.path
import random
from KKT_Module.ksoc_global import kgl
from PySide2 import QtWidgets,QtCore, QtGui
import time

##=====================================================================================
class ShowGesInference_label(QtWidgets.QLabel):
    def __init__(self, gesture, product_ver):
        super(ShowGesInference_label, self).__init__()
        self.product_ver = product_ver
        self.gesture= gesture
        self.setupUI()

    def setupUI(self):
        pic_path = os.path.join(kgl.KKTImage, self.product_ver, (self.gesture + '_D' + '.jpg'))
        pic_D = QtGui.QPixmap(pic_path).scaled(220, 220, aspectMode=QtCore.Qt.KeepAspectRatio)
        pic_D.detach()
        self.setPixmap(pic_D)

    def setPic_D(self):
        pic_path = os.path.join(kgl.KKTImage, self.product_ver, (self.gesture + '_D' + '.jpg'))
        pic_D = QtGui.QPixmap(pic_path).scaled(220, 220, aspectMode=QtCore.Qt.KeepAspectRatio)
        pic_D.detach()
        self.setPixmap(pic_D)

    def setPic_L(self):
        pic_path = os.path.join(kgl.KKTImage, self.product_ver, (self.gesture + '.jpg'))
        pic_L = QtGui.QPixmap(pic_path).scaled(220, 220, aspectMode=QtCore.Qt.KeepAspectRatio)
        pic_L.detach()
        self.setPixmap(pic_L)

class ShowGesInferenceBtn(QtWidgets.QPushButton):
    def __init__(self, gesture, product_ver):
        super(ShowGesInferenceBtn, self).__init__()
        self.gesture= gesture
        self.product_ver = product_ver
        self.setStyleSheet('background-color: None')
        self.pressed.connect(lambda : self.action())
        self.pushed = False
        self._timer = QtCore.QTimer()
        self._timer.timeout.connect(lambda :self.setPic_D())
        self.setupUI()

    def setupUI(self):
        pic_path = os.path.join(kgl.KKTImage, self.product_ver ,  (self.gesture+'_D'+'.jpg'))
        pic_D = QtGui.QPixmap(pic_path)#.scaled(220, 220, aspectMode=QtCore.Qt.KeepAspectRatio)
        self.setIcon(QtGui.QIcon(pic_D))
        self.setIconSize(QtCore.QSize(200,200))

    def action(self):
        if not self.pushed:
            self.setStyleSheet('background-color: lime')
            self.pushed = True
        else:
            self.setStyleSheet('background-color: None')
            self.pushed = False

    def setPic_D(self):
        pic_path = os.path.join(kgl.KKTImage, self.product_ver, (self.gesture + '_D' + '.jpg'))
        pic_D = QtGui.QPixmap(pic_path).scaled(220, 220, aspectMode=QtCore.Qt.KeepAspectRatio)
        self.setIcon(QtGui.QIcon(pic_D))
        self._timer.stop()

    def setPic_L(self):
        if not self.pushed:
            return False
        pic_path = os.path.join(kgl.KKTImage, self.product_ver, (self.gesture + '.jpg'))
        pic_L = QtGui.QPixmap(pic_path).scaled(220, 220,aspectMode=QtCore.Qt.KeepAspectRatio)
        self.setIcon(QtGui.QIcon(pic_L))
        self._timer.start(500)
        return  True

class ShowGesLogo(QtWidgets.QLabel):
    def __init__(self, logo='KaiKuTeK_LOGO_Italic.png'):
        super(ShowGesLogo, self).__init__()
        self.logo= logo
        self.setupUI()
        self.setAlignment(QtCore.Qt.AlignRight)

    def setupUI(self):
        pic_path = os.path.join(kgl.KKTImage, self.logo)
        logo = QtGui.QPixmap(pic_path).scaled(180, 180, aspectMode=QtCore.Qt.KeepAspectRatio)
        logo.detach()
        self.setPixmap(logo)

class ShowFPS(QtWidgets.QLabel):
    def __init__(self):
        super(ShowFPS, self).__init__()
        self.setText('fps')
        self.clearFPS()
        self.resize(20,20)
        self.setAlignment(QtCore.Qt.AlignLeft)

    def updatedFPS(self):
        if self._lastTime == None:
            self._lastTime = time.time()
            self.g_fps = None
        else:
            now = time.time()
            dt = now - self._lastTime
            self._lastTime = now
            self.setText(" {:.2f} fps.".format(1.0/dt))

    def clearFPS(self):
        self._lastTime = None
        self.g_fps = None
        self.setText('fps')

class PicturesInference(QtWidgets.QWidget):
    def __init__(self, ges_dict , CustomerID):
        super(PicturesInference, self).__init__()
        self._CustomerID = CustomerID
        self._gestures = self._genGestureDict(ges_dict)
        self.setup()

    def enableWidget(self, Threshold=False):
        if Threshold:
            self.grid.addWidget(self._threshold, self._row + 1, 0, 1 ,2)


    def setup(self):
        from KKT_Module.KKTUtility.qt_obj import InputThreshold
        self._layout = QtWidgets.QVBoxLayout(self)
        self._layout.setContentsMargins(0, 10, 0, 10)
        self.grid_widget = QtWidgets.QWidget()
        self._layout.addWidget(self.grid_widget)
        self.grid = QtWidgets.QGridLayout(self.grid_widget)
        self.grid.setContentsMargins(6, 0, 6, 0)

        self._row = 1
        col = 0
        for ges in self._gestures.values():
            self.grid.addWidget(ges[1], self._row, col ,1 , 1)
            self.grid.setColumnStretch(col, 1)
            self.grid.setRowStretch(self._row, 1)
            col = col + 1
            if col == 3:
                col = 0
                self._row= self._row+1

        self.threshold = InputThreshold()

    def getThresholdList(self):
        return self.threshold.getThreshold()



    def _genGestureDict(self, ges_dict:dict):
        gestures = {}
        for k, v in ges_dict.items():
            if v == 'Background':
                continue
            gestures[k] = [v , ShowGesInferenceBtn(v, self._CustomerID)]
        return gestures

    def triggerGesture(self, ges_id):
        return  self._gestures[ges_id][1].setPic_L()




##=============================  Unit Testing  ========================================
if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication([])
    app.setAttribute(QtCore.Qt.AA_Use96Dpi)

    win = QtWidgets.QMainWindow()
    win.setWindowTitle('test')
    win.resize(600, 400)

    img1 = PicturesInference({'0': 'Background', '2': 'PatPat', '3': 'FrontFront', '4': 'BackBack', '5': 'LeftLeft', '6': 'RightRight'}, '60000')
    img1.enableWidget(True)

    win.setCentralWidget(img1)
    win.show()
    win.setWindowTitle('Unit test')
    win.show()

    def data_update():
        global img1
        id = random.randint(2,6)
        img1.triggerGesture(str(id))

    qtimer = QtCore.QTimer()
    qtimer.timeout.connect(data_update)
    qtimer.start(2000)


    app.exec_()
    # qtimer.stop()