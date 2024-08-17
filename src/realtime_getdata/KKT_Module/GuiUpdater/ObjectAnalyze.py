class ObjectAnalyzeUpdater(Updater):
    def __init__(self):
        super(ObjectAnalyzeUpdater, self).__init__()
        self.s = time.time_ns()
        self.chirp = 32
        self._RDI_cfg = cfg()
        from KKT_Module.KKTUtility.PreseceDetect import PresenceDetect
        self.presence_detect = PresenceDetect()
        self.object_num = 2

        self.RDI_gen1 = gen_RDI(cfg1)
        self.RDI_gen2 = gen_RDI(cfg2)
        self.find_peak = find_peak(cfg3)


        pass

    def setup(self, win: ModeWindow):
        self.win = win
        self.addWidgetToCanvas()
        self.addWidgetToSubLayout()

    def addWidgetToCanvas(self):
        from KKT_Module.KKTGraph.ShowADCRaw import FFT
        from KKT_Module.KKTGraph.ShowFeatureMap import DrawMap2
        from RDIAnalyze import RDIAnalyze, PolarPlot
        wg = QtWidgets.QWidget()
        gl = QtWidgets.QGridLayout()


        wg.setLayout(gl)

        self.polar = PolarPlot()


        self.RDIAnalyze = RDIAnalyze()
        self.RDIAnalyze.setMaximumVelocity(2)

        self.FFT = FFT()
        self.mean = self.FFT.getSettingWidget()

        self.FeatureMap = DrawMap2('RDI',whole_map=True)
        self.FeatureMap.setAxis(x_len=30, y_len=64, x_start=-15, y_start=0)
        self.FeatureMap.setLevel(max=800)

        gl.addWidget(self.FeatureMap    , 8, 0, 4, 1)
        gl.addWidget(self.polar         , 0, 0, 8, 1)
        gl.addWidget(self.RDIAnalyze    , 8, 1, 4, 1)
        gl.addWidget(self.FFT           , 0, 1, 8, 1)

        self.lb = QtWidgets.QLabel('fps :')
        self.win.canvas_layout.addWidget(self.lb)
        self.win.canvas_layout.addWidget(wg,6)
        self.Widgets.append(self.lb)
        self.Widgets.append(wg)

    def addWidgetToSubLayout(self):
        from KKT_Module.KKTUtility.qt_obj import CollapsibleSection,SpinBoxListWidget
        from KKT_Module.KKTUtility.qt_obj import MapLevelBar, LevelBar
        self.plot_option = CollapsibleSection('Plot Options :')
        self._level_slider = MapLevelBar()
        self._level_slider.LevelChanged.connect(lambda: self._setLevel())
        self.threshold_level = LevelBar('Magnitude Threshold', [0,10,5,1])
        self.threshold_level.LevelChanged.connect(lambda: self._setThreshold())
        self.low_idx_filter = LevelBar('Filter Range(cm)', [0,31,10,1])
        self.low_idx_filter.setSlider(64/64)
        self.low_idx_filter.LevelChanged.connect(lambda: self._setFilterIndx())
        self.object_spin = SpinBoxListWidget(items={'Object Number': {'Value': 2,
                                                                    'Range': [1, 2]},

                                                    }, cols=1)
        self.object_spin.change_Signal.connect(lambda :self.setObjectNumber())
        self.plot_option.grid.addWidget(self.mean, 0, 0, 1, 2)
        self.plot_option.grid.addWidget(self._level_slider, 1, 0, 1, 2)

        self.plot_option.grid.addWidget(self.threshold_level, 2, 0, 1, 2)
        self.plot_option.grid.addWidget(self.low_idx_filter, 3, 0, 1, 2)
        self.plot_option.grid.addWidget(self.object_spin, 4, 0, 1, 2)

        self.win.main_sublayout.addWidget(self.plot_option, 4, 0 ,1 ,1)


        self.Widgets.append(self.plot_option)
        pass

    def setObjectNumber(self):
        status = self.object_spin.getItemsStatus()
        self.object_num = status.get('Object Number')['Value']
        self.setConfigs(object_num=self.object_num)
        pass

    def _setFilterIndx(self):
        idx = self.low_idx_filter.getLevel()
        self.setConfigs(filter_index=idx)

    def _setLevel(self):
        self.FeatureMap.setLevel(self._level_slider.getLevel())
        self.RDIAnalyze.setMaximumAmplitude(self._level_slider.getLevel())

    def _setThreshold(self):
        thr = self.threshold_level.getLevel()
        self.setConfigs(threshold_level = thr)

    def enableSublayoutWidget(self, enable):
        # self._cb_RDI_configs.setEnabled(enable)
        # self.FeatureMap.MapLevelBar.setEnabled(enable)
        pass

    def _changeRDI_configs(self):
        items_dict = self._cb_RDI_configs.getItemsStatus()
        self._RDI_cfg.RDI1.Fast_downsample_ratio = items_dict['FT_downSample']['Value']
        self._RDI_cfg.RDI1.Slow_time_downsample_ratio = items_dict['ST_downSample']['Value']
        self._RDI_cfg.RDI1.Fast_time_start_point = items_dict['FT_startPoint']['Value']

        self._RDI_cfg.RDI2.Fast_downsample_ratio = items_dict['FT_downSample']['Value']
        self._RDI_cfg.RDI2.Slow_time_downsample_ratio = items_dict['ST_downSample']['Value']
        self._RDI_cfg.RDI2.Fast_time_start_point = items_dict['FT_startPoint']['Value']
        self.FeatureMap.setAxis(x_len=30, x_start=-15, y_start=0+items_dict['FT_startPoint']['Value'], x_ratio=items_dict['ST_downSample']['Value'], y_ratio=items_dict['FT_downSample']['Value'])
        pass

    def deleteWidgets(self):
        super(ObjectAnalyzeUpdater, self).deleteWidgets()


    def setRDIConfigs(self, FastTimeDownSampleRatio, SlowTimeDownSampleRatio, FastTimeStartPoint):
        self._RDI_cfg.RDI1.Fast_downsample_ratio = FastTimeDownSampleRatio
        self._RDI_cfg.RDI1.Slow_time_downsample_ratio = SlowTimeDownSampleRatio
        self._RDI_cfg.RDI1.Fast_time_start_point = FastTimeStartPoint

        self._RDI_cfg.RDI2.Fast_downsample_ratio = FastTimeDownSampleRatio
        self._RDI_cfg.RDI2.Slow_time_downsample_ratio = SlowTimeDownSampleRatio
        self._RDI_cfg.RDI2.Fast_time_start_point = FastTimeStartPoint
        pass

    def update(self, res):

        RDI1, cRDI1 = self.RDI_gen1.run(res[0])
        RDI2, cRDI2 = self.RDI_gen2.run(res[1])
        range_idx, velocity_idx, peak_val = self.find_peak.run(RDI1, RDI2)
        phase = phase_detect(cRDI1, cRDI2, range_idx, velocity_idx)

        # RDI, FFT  = RDI_gen3(res[0], self._RDI_cfg.RDI1)
        Map = np.real(RDI2) / 2 ** 11
        # Map = np.real(RDI2)
        self.FeatureMap.setData(Map)

        velocity = np.linspace(-0.13*100,0.13*100,32).take(velocity_idx+16)
        distance = np.linspace(0, self.max_distance, 64).take(range_idx)


        velocity = self.padParam(velocity)
        distance = self.padParam(distance)
        phase = self.padParam(phase)
        peak_val = self.padParam(peak_val)/2**11


        self.RDIAnalyze.setData(velocity=velocity,distance=distance,amplitude=peak_val)
        res = np.asarray(res)
        res = np.reshape(res, (2, self.chirp, 128))
        res = res[:, :, :64]
        FFT = np.zeros((2, self.chirp, 32))
        FFT[0] = getFFT(res[0], 32)
        FFT[1] = getFFT(res[1], 32)

        self.FFT.setData(FFT)
        self.polar.setData(x=distance*np.sin(phase), y=distance*np.cos(phase), velocity=velocity, peak_val=peak_val)
        print('velocity={}, distance={}, amplitude={}, phase={}'.format(velocity, distance, peak_val, phase))

        self.lb.setText('fps : {:.2f}'.format((10 ** 9) / (time.time_ns() - self.s+np.finfo(np.float32).eps)))
        self.s = time.time_ns()

        pass

    def padParam(self,param):
        if len(param) < self.object_num:
            param = np.pad(param,(0,self.object_num-len(param)),constant_values=(0,0))
        else:
            param = param[:self.object_num]
        return param

    def setChirp(self, chirp):
        self.chirp = chirp
        self._RDI_cfg.RDI1.Slow_time_symbols = self.chirp
        self._RDI_cfg.RDI2.Slow_time_symbols = self.chirp
        self.FFT.setChirp(chirp)


    def setConfigs(self,**kwargs):
        if kwargs.get('chirp') is not None:
            self.chirp = kwargs.get('chirp')
            cfg1.Slow_time_symbols = self.chirp
            cfg2.Slow_time_symbols = self.chirp
            self.RDI_gen1.setConfigs(cfg1)
            self.RDI_gen2.setConfigs(cfg2)
            self.find_peak.setConfigs(cfg3)

        if kwargs.get('max_distance') is not None:
            self.max_distance = kwargs.get('max_distance')
            self.polar.setParameters(max_distance=self.max_distance)
            self.polar.initPlots()
            self.FeatureMap.setAxis(x_len=30, x_start=-15, y_len=self.max_distance,)
            self.FeatureMap.initPlots()
            self.RDIAnalyze.setParameters(max_distance= self.max_distance, max_velocity=20, max_amplitude=1500)
            self.RDIAnalyze.initPLots()
            self.FFT.setParameters(XRange=[0, self.max_distance])
            self.FFT.p.initPlots()

            self.low_idx_filter.setSlider(self.max_distance / 64)
        if kwargs.get('threshold_level') is not None:
            cfg3.mag_th = kwargs.get('threshold_level')*1000
            self.find_peak.setConfigs(cfg3)

        if kwargs.get('object_num') is not None:
            object_num = kwargs.get('object_num')
            cfg3.max_tar_num = object_num
            self.find_peak.setConfigs(cfg3)

            self.RDIAnalyze.setParameters(object_num=self.object_num)
            self.RDIAnalyze.initPLots()

            self.polar.setParameters(object_num=self.object_num)
            self.polar.initPlots()



        if kwargs.get('filter_index') is not None:
            filter_index = kwargs.get('filter_index')
            cfg3.start_idx = filter_index
            self.find_peak.setConfigs(cfg3)

        self.RDIAnalyze.setMaximumAmplitude(self._level_slider.getLevel())