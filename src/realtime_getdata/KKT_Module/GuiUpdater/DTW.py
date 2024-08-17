from KKT_Module.GuiUpdater.GuiUpdater import Updater
try :
    from fastdtw._fastdtw import fastdtw
except Exception as err:
    print(err)

class DTWUpdater(Updater):
    def __init__(self):
        super(DTWUpdater, self).__init__()
        self.s = time.time_ns()
        self.flag = 0
        self.dist_thres = 0
        self.ges_lock = 0
        pass
    # def __del__(self):
    #     self.T3D


    def setup(self, win: ModeWindow):
        self.win = win
        self.addWidgetToCanvas()
        self.addWidgetToSubLayout()
        self.TimeTracking.initPlot()
        pass
    def addWidgetToSubLayout(self):
        self.plot_option = CollapsibleSection('Plot Options :')
        self.pb_setDefault = QtWidgets.QPushButton('Set Default')

        self.pb_setDefault.clicked.connect(lambda: self.setDefault())
        self.plot_option.grid.addWidget(self.pb_setDefault, 0, 0, 1, 2)


        self.win.main_sublayout.addWidget(self.plot_option, 4, 0, 1, 1)

        self.Widgets.append(self.plot_option)

    def addWidgetToCanvas(self):
        from DTW import TimeTracking,InferenceTracking
        from KKT_Module.KKTGraph.LED import Led

        self.Led = Led(None,shape=Led.circle, autoOff=1)
        self.Led.setText('Inference')
        self.Led.setFixedSize(100,100)


        l = QtWidgets.QVBoxLayout()

        wg = QtWidgets.QWidget()
        wg.setLayout(l)
        # self.T3D = Tracking3DPLot()
        self.TimeTracking = TimeTracking()
        # l.addWidget(self.T3D, 1)
        l.addWidget(self.TimeTracking, 1)
        self.lb = QtWidgets.QLabel('fps :')
        # self.Widgets.append(self.T3D)
        self.Widgets.append(self.TimeTracking)

        self.Widgets.append(self.lb)
        self.tabW = QtWidgets.QTabWidget()
        self.tabW.addTab(wg, 'Data Collection')
        # self.tabW.setStyleSheet("QWidget {background-color: light-gray; }")

        l2 = QtWidgets.QVBoxLayout()

        wg2 = QtWidgets.QWidget()
        wg2.setLayout(l2)
        self.distance_threshold_lb = QtWidgets.QLabel('Distance Threshold =')
        self.distance_threshold_lb.setFixedHeight(20)
        self.distance_threshold = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.distance_threshold.setTickPosition(QtWidgets.QSlider.TickPosition.TicksBelow)
        self.distance_threshold.valueChanged.connect(lambda: self.changeDistanceThreshold())
        self.distance_threshold.setRange(0, 100)
        self.distance_threshold.setValue(50)

        lb_easy = QtWidgets.QLabel('Easy To Do')
        lb_easy.setFixedHeight(20)
        lb_hard = QtWidgets.QLabel('Hard To Do')
        lb_hard.setFixedHeight(20)
        w = QtWidgets.QWidget()
        l = QtWidgets.QHBoxLayout(w)
        w.setLayout(l)
        l.addWidget(lb_hard,1)
        l.addWidget(self.distance_threshold,8)
        l.addWidget(lb_easy,1)

        self.InferenceTracking = InferenceTracking()
        l2.addWidget(self.Led, 0, alignment=QtGui.Qt.AlignCenter)
        l2.addWidget(self.InferenceTracking, 2)
        l2.addWidget(w, 1)
        l2.setStretch(0,7)
        l2.setStretch(1,10)
        l2.setStretch(2,1)


        self.tabW.addTab(wg2, 'Inference')
        self.tabW.setTabPosition(QtWidgets.QTabWidget.TabPosition.South)

        self.Widgets.append(self.tabW)
        self.win.canvas_layout.setContentsMargins(7, 7, 7, 7)
        self.win.canvas_layout.addWidget(self.lb)
        self.win.canvas_layout.addWidget(self.tabW)

    def setDefault(self):
        # self.T3D.initPlot()
        self.TimeTracking.initPlot()
        pass

    def changeDistanceThreshold(self):
        distance_threshold = self.distance_threshold.value()
        self.distance_threshold_lb.setText('Distance Threshold = {}'.format(distance_threshold))

    def enableSublayoutWidget(self, enable):

        pass

    def update(self, res):
        print('[Axis]X={:.3f}, Y={:.3f}, Z={:.3f}'.format(res[1][0], res[1][1], res[1][2]))
        if self.tabW.currentIndex() == 0:
            self.DataCollection(res[1])
            self.inf_init = 1
        elif self.tabW.currentIndex() == 1:
            if self.inf_init == 1:
                self.anchor = self.TimeTracking.pts[:, self.TimeTracking.s:self.TimeTracking.e][:, ::-1]
                self.anchor = self.anchor[1] + 1j * self.anchor[0]
                self.aug_anchors = self.augementation_xy(self.anchor, [0.8, 1.2], [0.8, 1.25], [0.8, 1.25], 2) * 2 ** 6
                self.aug_anchors = np.array([np.real(self.aug_anchors[:]), np.imag(self.aug_anchors[:])]).transpose(1,
                                                                                                                    2,
                                                                                                                    0)
                print("Number of Anchors: ", self.aug_anchors.shape[0])
                self.inf_array = np.zeros([self.anchor.shape[0] + 5, 2],
                                          dtype=np.float32)  # the dimension of self.inf_array will follow the dimension of the training anchor

                self.inf_init = 0

            self.Inference(res[1])
            if self.ges_lock:
                self.Led.turn_on()

        self.lb.setText('fps : {:.2f}'.format((10 ** 9) / ((time.time_ns() - self.s)+np.finfo(np.float32).eps)))
        self.s = time.time_ns()

        pass

    def DataCollection(self, res):
        data = res / 64
        self.TimeTracking.updateData(data[:2])
        # self.T3D.setData(data[:2])

        pass

    def Inference(self,res):
        data = res / 64
        self.InferenceTracking.updateData(pos_record=self.TimeTracking.pts[:,self.TimeTracking.s:self.TimeTracking.e],pos_current=data[:2])
        pass

        data = res / 64
        self.InferenceTracking.updateData(pos_record=self.TimeTracking.pts[:, self.TimeTracking.s:self.TimeTracking.e],
                                          pos_current=data[:2])
        self.inference_array(res)
        dist_array = np.zeros([self.aug_anchors.shape[0]])

        for i in range(dist_array.shape[0]):
            dist_array[i], _ = fastdtw(self.aug_anchors[i], self.inf_array)
        print('Min Distant: ', np.min(dist_array).astype(int))
        min_dist = np.min(dist_array).astype(int)

        thres = 400 * 25 * self.dist_thres * 0.0175

        # if any(dist_array < 400*25*self.dist_thres*0.0175) and self.flag == 0:
        if (min_dist < thres) and self.flag == 0:
            self.flag = 1
            print("GESTURE")
        elif (min_dist > thres) and self.flag == 1:
            self.flag = 0

        if (self.flag == 1) and (self.ges_lock == 0):
            self.ges_lock = 1
        elif (self.flag == 0) and (self.ges_lock == 1):
            self.ges_lock = 0

    def changeDistanceThreshold(self):
        self.dist_thres = distance_threshold = self.distance_threshold.value()
        self.distance_threshold_lb.setText('Distance Threshold = {}'.format(distance_threshold))

        pass

    def inference_array(self, pos):
        x = np.asarray(pos[0])
        y = np.asarray(pos[1])
        # s = y + 1j*x

        self.inf_array = np.roll(self.inf_array, -1, axis=0)
        self.inf_array[-1, 0], self.inf_array[-1, 1] = y, x

    def augementation_xy(self, input, zoom_scale, x_scale, y_scale, shift_res):
        ratio = 0.2
        x_scale_arg = np.full((len(np.arange(x_scale[0], x_scale[1] + 0.0001, ratio)), 1), 1) + 1j * (
            np.arange(x_scale[0], x_scale[1] + 0.0001, ratio)[..., None])
        y_scale_arg = np.arange(y_scale[0], y_scale[1] + 0.0001, ratio)[..., None] + 1j * (
            np.full((len(np.arange(y_scale[0], y_scale[1] + 0.0001, ratio)), 1), 1))
        zoom_scale_arg = np.arange(zoom_scale[0], zoom_scale[1] + 0.0001, ratio)[..., None] + 1j * (
            np.arange(zoom_scale[0], zoom_scale[1] + 0.0001, ratio)[..., None])

        x_scale_arg = self.complex_mul(x_scale_arg, input)
        y_scale_arg = self.complex_mul(y_scale_arg, input)
        zoom_scale_arg = self.complex_mul(zoom_scale_arg, input)

        scale_cat = np.concatenate((x_scale_arg, y_scale_arg, zoom_scale_arg), axis=0)

        output = self.xy_input_shift(scale_cat, [-3, 3], [0, 4], shift_res)

        return output

    def xy_input_shift(self, input, x_regin, y_regin, bin_res):
        output = []

        if len(np.arange(x_regin[0], y_regin[1] + 1, bin_res)) > 1:
            for i in range(len(np.arange(x_regin[0], x_regin[1] + 0.0001, bin_res))):
                for j in range(len(np.arange(y_regin[0], y_regin[1] + 0.0001, bin_res))):
                    data = input + (y_regin[0] + j * bin_res) + 1j * (x_regin[0] + i * bin_res)
                    output.append(data)
            return np.vstack(output)
        else:
            return input

    def complex_mul(self, a, b):
        c = np.real(a) * np.real(b)
        d = np.imag(a) * np.imag(b)

        return c + 1j * d

    def setConfigs(self,**kwargs):
        super(DTWUpdater, self).setConfigs()
        frame = int(self.TimeTracking.region.getRegion()[1]) - int(self.TimeTracking.region.getRegion()[0]) + 50
        self.InferenceTracking.frame = frame
        # self.TimeTracking.initPlot()
        self.InferenceTracking.initPlot()

        pass