class PresenceUpdater(Updater):
    def __init__(self):
        super(PresenceUpdater, self).__init__()
        self.s = time.time_ns()
        from KKT_Module.KKTUtility.PreseceDetect import PresenceDetect
        self.presence_detect = PresenceDetect()
        self.time_counter = 0
        self.time_timer = QtCore.QTimer()
        self.time_timer.timeout.connect(lambda :self.countDetectTime())
        self.detected = False
        self.output = "Undetect"
        self.proportion = None
        self.chirp = 32
        pass

    def setup(self, win: ModeWindow):
        self.win = win

        self.addWidgetToCanvas()
        self.addSublayoutWidgets()
        # if hasattr(self.win, 'start_process_Signal'):
        #     self.win.start_process_Signal.connect(lambda :self.CurrentDistance.initPeak())
        if hasattr(self.win, 'stop_process_Signal'):
            print('stop')
            self.win.stop_process_Signal.connect(lambda :self.stopProcess())

    def stopProcess(self):
        self.time_timer.stop()
        self.time_counter = 0
        if hasattr(self, 'lb_detect_time'):
            self.lb_detect_time.setText('Stay Time (s) = {}'.format("Undetect"))
        if hasattr(self, 'lb_distance'):
            self.lb_distance.setText('Distance (cm) = {}'.format("Undetect"))
        self.LED.turn_on(False)
        self.detected = False
        self.win.stop_process_Signal.disconnect()

    def update(self, res):

        res = np.asarray(res)
        res = np.reshape(res,(2, self.chirp, 128))

        res = res[:, :, :64]
        FFT = np.zeros((2, self.chirp, 32))
        FFT[0] = getFFT(res[0], 32)
        FFT[1] = getFFT(res[1], 32)
        self.FFT.setData(FFT)

        res = res[:,:,:64]
        self.output, detected , thres_arry, rdi_mean = self.presence_detect.detect(res)

        if not self.time_timer.isActive():
            self.win.stop_process_Signal.connect(lambda :self.stopProcess())
            self.CurrentDistance.initPeak()
            self.time_timer.start(1000 / self.SB.getItemsStatus().get('times')['Value'])
        if detected != self.detected:
            if detected:
                self.LED.turn_on(True)
                self.time_counter = 0
                self.lb_detect_time.setText('Detected Duration (s) = {}'.format(self.time_counter))
                self.lb_distance.setText('Detected Distance (cm) = {}'.format(self.output))
            else:
                self.LED.turn_on(False)
                self.lb_detect_time.setText('Detected Duration (s) = {}'.format("Undetect"))
                self.lb_distance.setText('Detected Distance (cm) = {}'.format("Undetect"))
            self.detected = detected
        self.lb.setText('fps : {:.2f}'.format((10 ** 9) / ((time.time_ns() - self.s) + np.finfo(np.float32).eps)))
        self.s = time.time_ns()
        pass

    def countDetectTime(self):
        if not self.detected:
            self.CurrentDistance.setYData(0)
            self.lb_detect_time.setText('Detected Duration (s) = {}'.format("Undetect"))
            self.lb_distance.setText('Detected Distance (cm) = {}'.format("Undetect"))
            return
        self.time_counter = self.time_counter + 1
        second = self.time_counter//self.SB.getItemsStatus().get('times')['Value']
        mod = self.time_counter%self.SB.getItemsStatus().get('times')['Value']
        if mod == 0 :
            self.lb_detect_time.setText('Detected Duration (s) = {}'.format(second))
        self.lb_distance.setText('Detected Distance (cm) = {}'.format(int(self.proportion[self.output])))
        self.CurrentDistance.setYData(self.output)

    def setTimePerSecond(self):
        self.CurrentDistance.setTimes(self.SB.getItemsStatus().get('times')['Value'])

    def addSublayoutWidgets(self):
        from KKT_Module.KKTUtility.qt_obj import SpinBoxListWidget
        spin_list = {'times':{'Label':'Update Times Per Second',
                              'Range':[1,10],
                              'Value':5}}
        self.SB = SpinBoxListWidget(items=spin_list)
        self.presence_section = CollapsibleSection("Presence Setting")
        self.presence_section.grid.addWidget(self.SB,0,0,1,2)
        self.Widgets.append(self.presence_section)

        self.plot_option_section = CollapsibleSection("Plot Options")

        self.plot_option_section.grid.addWidget(self.FFT.mean_wg,0,0,1,2)
        self.Widgets.append(self.plot_option_section)

        self.win.main_sublayout.addWidget(self.presence_section,5,0)
        self.win.main_sublayout.addWidget(self.plot_option_section, 6, 0)

    def addWidgetToCanvas(self):
        from KKT_Module.KKTGraph.ShowADCRaw import FFTPlots
        from KKT_Module.KKTGraph.ShowCurrentPlot import CurrentDistance
        from KKT_Module.KKTGraph.LED import Led


        self.FFT = FFTPlots()
        self.CurrentDistance = CurrentDistance()

        self.showWidget = QtWidgets.QWidget()
        ly = QtWidgets.QGridLayout()
        self.showWidget.setLayout(ly)
        self.LED = Led(self, shape=Led.circle)
        self.LED.setFixedSize(200, 200)
        self.LED.setText('Presence')
        ly.addWidget(self.LED, 0,0,4,1, alignment=QtCore.Qt.AlignCenter)
        self.lb_distance = QtWidgets.QLabel('Detected Distance (cm) = Undetect')
        self.lb_distance.setFont(QtGui.QFont('Yu Gothic UI', 20))
        self.lb_detect_time = QtWidgets.QLabel('Detected Duration (s) = Undetect')
        self.lb_detect_time.setFont(QtGui.QFont('Yu Gothic UI', 20))
        ly.addWidget(self.lb_distance, 1,1,1,1)
        ly.addWidget(self.lb_detect_time, 2,1,1,1)

        self.lb = QtWidgets.QLabel('fps : ')


        self.win.canvas_layout.addWidget(self.lb)
        self.win.canvas_layout.addWidget(self.showWidget,2)
        self.win.canvas_layout.addWidget(self.CurrentDistance,2)
        self.win.canvas_layout.addWidget(self.FFT, 2)

        self.Widgets.append(self.lb)
        self.Widgets.append(self.showWidget)
        self.Widgets.append(self.CurrentDistance)
        self.Widgets.append(self.FFT)

    def setChirp(self, chirp):
        self.chirp = chirp
        pass

    def enableSublayoutWidget(self, enable):
        self.presence_section.setEnabled(not enable)
        pass

    def deleteWidgets(self):
        super(PresenceUpdater, self).deleteWidgets()
        self.time_timer.stop()

    def setConfigs(self,**kwargs):
        max_distance = kwargs.get('max_distance')
        chirp = kwargs.get('chirp')
        self.FFT.setParameters(XRange=[0,max_distance],xrange_label = np.linspace(0, max_distance, 32))
        self.FFT.initPlots()