from KKT_Module.GuiUpdater.GuiUpdater import Updater
from PySide2 import QtGui,QtCore,QtWidgets
import numpy as np

class RawDataTracking2DUpdater(Updater):
    def __init__(self):
        super(RawDataTracking2DUpdater, self).__init__()
        from Tracking.Tracking_init import Motion, config_struct
        self._Motion = Motion()
        self._T_struct = config_struct()
        self.setting_config = None
        pass

    def setup(self, win):
        self.win = win
        self.addWidgetToCanvas()
        pass

    def addWidgetToCanvas(self):
        from KKT_Module.KKTGraph.ShowTracking import DrawingPosition
        self.T_XY = DrawingPosition('XY Tracking')
        # self.lb = QtWidgets.QLabel('fps :')

        self.Widgets.append(self.T_XY)
        # self.Widgets.append(self.lb)

        # self.win.canvas_layout.addWidget(self.lb)
        self.win.canvas_layout.addWidget(self.T_XY)

    def enableSublayoutWidget(self, enable):
        pass

    def update(self, res):
        self._Motion.AIC_processing(res[0])
        X, Y ,energy_detect= self._T_struct.tracking_run(res[0], res[1])
        print('[Axis]X={:.3f}, Y={:.3f}'.format(X, Y))
        x = np.asarray([X])
        y = np.asarray([Y])
        self.T_XY.setData(x, y)
        self.win.lb_FPS.setText('fps : {:.2f}'.format(self.FPS_counter.updateFPS()))

        pass

