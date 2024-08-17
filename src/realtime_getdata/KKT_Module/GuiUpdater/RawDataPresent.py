

class ADCRawDataUpdater(Updater):
    def __init__(self):
        super(ADCRawDataUpdater, self).__init__()
        self.s = time.time_ns()
        self.chirp = 32
        from KKT_Module.KKTUtility.PreseceDetect import PresenceDetect
        self.presence_detect = PresenceDetect()
        pg.setConfigOption('foreground', 'k')  # Default foreground color for text, lines, axes, etc.
        pg.setConfigOption('background', None)  # Default background for GraphicsView.
        pg.setConfigOptions(antialias=True)  # Draw lines with smooth edges at the cost of reduced performance.
        pass

    def setup(self, win: ModeWindow):
        self.win = win
        self.addWidgetToCanvas()
        self.addSublaputWidget()

    def addWidgetToCanvas(self):
        from KKT_Module.KKTGraph.ShowADCRaw import  FFTPlots, ADCPlots

        self.raw = ADCPlots()
        self.mean1 = self.raw.getSettingWidget()

        self.FFT = FFTPlots()
        self.mean2 = self.FFT.getSettingWidget()
        self.lb = QtWidgets.QLabel('fps :')

        self.win.canvas_layout.addWidget(self.lb)
        self.win.canvas_layout.addWidget(self.raw)
        self.win.canvas_layout.addWidget(self.FFT)

        self.Widgets.append(self.lb)
        self.Widgets.append(self.raw)
        self.Widgets.append(self.FFT)

    def addSublaputWidget(self):
        self.plot_option = CollapsibleSection("Plot Options")
        group1 = QtWidgets.QGroupBox('Raw Data')
        ly1 = QtWidgets.QVBoxLayout()
        group1.setLayout(ly1)
        ly1.addWidget(self.mean1)
        self.plot_option.grid.addWidget(group1,0,0,1,2)

        group2 = QtWidgets.QGroupBox('FFT')
        ly2 = QtWidgets.QVBoxLayout()
        group2.setLayout(ly2)
        ly2.addWidget(self.mean2)
        self.plot_option.grid.addWidget(group2,1,0,1,2)

        self.win.main_sublayout.addWidget(self.plot_option, 5, 0)


        self.Widgets.append(self.plot_option)

    def enableSublayoutWidget(self, enable):

            pass

    def deleteWidgets(self):
        super(ADCRawDataUpdater, self).deleteWidgets()

    def update(self, res):
        # chirp =32
        res = np.asarray(res)
        res = np.reshape(res, (2, self.chirp, 128))
        self.raw.setData(res)
        # res[:,:,64:]=0
        res = res[:,:,:64]
        # self.output, detected, thres_arry = self.presence_detect.detect(res)
        FFT = np.zeros((2,self.chirp,32))
        FFT[0] = getFFT(res[0], 32)
        # FFT[0][0] = thres_arry

        FFT[1] = getFFT(res[1], 32)

        self.FFT.setData(FFT)
        self.lb.setText('fps : {:.2f}'.format((10 ** 9) / ((time.time_ns() - self.s) + np.finfo(np.float32).eps)))
        self.s = time.time_ns()
        pass

    def setChirp(self, chirp):
        self.chirp = chirp
        self.raw.setChirp(chirp)
        self.FFT.setChirp(chirp)

    def setConfigs(self,**kwargs):
        max_distance = kwargs.get('max_distance')
        chirp = kwargs.get('chirp')
        self.FFT.setParameters(XRange=[0,max_distance],xrange_label = np.linspace(0, max_distance, 32))
        self.raw.setParameters(XRange=[0,64],xrange_label = np.linspace(0, 63, 64))
        self.FFT.initPlots()
        self.raw.initPlots()

