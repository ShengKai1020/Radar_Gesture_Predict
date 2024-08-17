class ADCRDIMapUpdater(Updater):
    def __init__(self):
        super(ADCRDIMapUpdater, self).__init__()
        self.s = time.time_ns()
        self.chirp = 32
        self._RDI_cfg = cfg()
        from KKT_Module.KKTUtility.PreseceDetect import PresenceDetect
        self.presence_detect = PresenceDetect()
        self.max_distance = 64
        self.chirp = 32

        pass

    def setup(self, win: ModeWindow):
        self.win = win
        self.addWidgetToCanvas()
        self.addWidgetToSubLayout()

    def addWidgetToCanvas(self):
        from KKT_Module.KKTGraph.ShowADCRaw import FFTWidget, FFTPlots
        from KKT_Module.KKTGraph.ShowFeatureMap import FeatureMapWidget2
        # self.FFT = FFTWidget()
        self.FFT = FFTPlots()
        # self.FFT.enableWidgets(True, True)
        self.mean1 = self.FFT.getSettingWidget()
        self.FeatureMap = FeatureMapWidget2(['RDI CH1', 'RDI CH2'])
        # self.FeatureMap.enableWidget(adjust=True)

        self.lb = QtWidgets.QLabel('fps :')
        # self.win.canvas_layout.setStretch(1, 3)
        # self.win.canvas_layout.setStretch(2, 2)
        self.win.canvas_layout.addWidget(self.lb)
        self.win.canvas_layout.addWidget(self.FFT,6)
        self.win.canvas_layout.addWidget(self.FeatureMap, 6)

        self.Widgets.append(self.lb)
        self.Widgets.append(self.FFT)
        self.Widgets.append(self.FeatureMap)

    def addWidgetToSubLayout(self):
        from KKT_Module.KKTUtility.qt_obj import CollapsibleSection,DoubleSpinBoxListWidget
        RDI_configs = {
            # 'FT_downSample': {'Enable': True,
            #         'Label': 'Fast Down Sample Ratio',
            #         'Check': True,
            #         'Range': [1, 2],
            #         'Value': 2,
            #         },
            # 'ST_downSample': {'Enable': True,
            #         'Label': 'Slow Down Sample Ratio',
            #         'Check': True,
            #         'Range': [1, 2],
            #         'Value': 2,
            #         },
            'FT_startPoint': {'Enable': True,
                    'Label': 'RDI Map Start Range (cm)',
                    'Check': True,
                    'Range': [0, 34, 34/64],
                    'Value': 0,
                    },
                       }
        self._cb_RDI_configs = DoubleSpinBoxListWidget(items=RDI_configs)
        self._cb_RDI_configs.change_Signal.connect(lambda :self._changeRDI_configs())
        # self.map_section = CollapsibleSection('Map Configs :')
        # self.map_section.grid.addWidget(self._cb_RDI_configs, 0, 0, 1, 2)
        # self.map_section.grid.addWidget(self.FeatureMap.MapLevelBar, 1,0,1,2)

        self.plot_option = CollapsibleSection("Plot Options")
        group1 = QtWidgets.QGroupBox('FFT')
        ly1 = QtWidgets.QVBoxLayout()
        group1.setLayout(ly1)
        ly1.addWidget(self.mean1)
        self.plot_option.grid.addWidget(group1, 0, 0, 1, 2)
        self.plot_option.grid.addWidget(self._cb_RDI_configs, 1, 0, 1, 2)
        self.plot_option.grid.addWidget(self.FeatureMap.MapLevelBar, 2, 0, 1, 2)


        self.Widgets.append(self.plot_option)


        self.win.main_sublayout.addWidget(self.plot_option, 5, 0 ,1 ,1)
        pass

    def enableSublayoutWidget(self, enable):
        # self._cb_RDI_configs.setEnabled(enable)
        # self.FeatureMap.MapLevelBar.setEnabled(enable)
        pass

    def _changeRDI_configs(self):
        items_dict = self._cb_RDI_configs.getItemsStatus()
        # self._RDI_cfg.RDI1.Fast_downsample_ratio = items_dict['FT_downSample']['Value']
        # self._RDI_cfg.RDI1.Slow_time_downsample_ratio = items_dict['ST_downSample']['Value']
        self._RDI_cfg.RDI1.Fast_time_start_point = int(items_dict['FT_startPoint']['Value']*128/self.max_distance)
        #
        # self._RDI_cfg.RDI2.Fast_downsample_ratio = items_dict['FT_downSample']['Value']
        # self._RDI_cfg.RDI2.Slow_time_downsample_ratio = items_dict['ST_downSample']['Value']
        self._RDI_cfg.RDI2.Fast_time_start_point = int(items_dict['FT_startPoint']['Value']*128/self.max_distance)
        self.FeatureMap.setAxis(x_len=0.3, x_start=-0.15, y_start=0 + items_dict['FT_startPoint']['Value'], y_len=self.max_distance/2)#, x_ratio=items_dict['ST_downSample']['Value'], y_ratio=items_dict['FT_downSample']['Value'])
        pass

    def deleteWidgets(self):
        super(ADCRDIMapUpdater, self).deleteWidgets()


    def update(self, res):
        RDI = np.zeros((2, 32, 32))
        RDI[0] = np.real(RDI_gen2(np.reshape(res[0], (128, self.chirp), 'F'), self._RDI_cfg.RDI1)[0])[:,:,0]/2**15
        RDI[1] = np.real(RDI_gen2(np.reshape(res[1], (128, self.chirp), 'F'), self._RDI_cfg.RDI2)[0])[:,:,0]/2**15
        self.FeatureMap.setData(RDI[0], RDI[1])

        res = np.reshape(res,(2, self.chirp, 128))
        res = res[:, :, :64]
        FFT = np.zeros((2,self.chirp,32))
        FFT[0] = np.real(getFFT(res[0], 32))
        FFT[1] = np.real(getFFT(res[1], 32))
        self.FFT.setData(FFT)
        self.lb.setText('fps : {:.2f}'.format((10 ** 9) / ((time.time_ns() - self.s) + np.finfo(np.float32).eps)))
        self.s = time.time_ns()
        pass

    def setChirp(self, chirp):
        self.chirp = chirp
        self._RDI_cfg.RDI1.Slow_time_symbols = self.chirp
        self._RDI_cfg.RDI2.Slow_time_symbols = self.chirp
        self.FFT.setChirp(chirp)

    def setConfigs(self,**kwargs):
        self.max_distance = kwargs.get('max_distance')
        self.chirp = kwargs.get('chirp')
        self._changeRDI_configs()
        if self.max_distance is not None:
            self.FFT.setParameters(XRange=[0,self.max_distance],xrange_label = np.linspace(0, self.max_distance, 32))
            self.FFT.initPlots()
            self._cb_RDI_configs.setRange('FT_startPoint',range=[0,self.max_distance/2,self.max_distance/128])
            self._cb_RDI_configs.setDefault()

class RawFeatureMapUpdater(Updater):
    def __init__(self):
        super(RawFeatureMapUpdater, self).__init__()
        self.s = time.time_ns()
        pass

    def setup(self, win: QtWidgets.QMainWindow):
        from KKT_Module.KKTGraph.ShowFeatureMap import FeatureMapWidget
        setup_config(SettingConfigs.ParamDict)

        wg = pg.LayoutWidget()
        win.resize(700, 500)
        win.setWindowTitle('Raw data to Feature Map')
        self.FeatureMap = FeatureMapWidget()
        self.lb = QtWidgets.QLabel('fps : ')
        wg.addWidget(self.lb, 0, 0)
        wg.addWidget(self.FeatureMap, 1, 0)
        win.setCentralWidget(wg)
        win.show()
        pass

    def update(self, res):
        rawdata = np.hstack([res[0], res[1]])
        feature_map = np.real(preprocessing_fx_HW(rawdata)[1])
        self.FeatureMap.setData(feature_map[:,:,0], feature_map[:,:,1])
        self.lb.setText('fps : {:.2f}'.format((10 ** 9) / ((time.time_ns() - self.s) + np.finfo(np.float32).eps)))
        self.s = time.time_ns()
        pass

class RawFeatVectorUpdater(Updater):
    def __init__(self):
        self.s = time.time_ns()
        pass

    def setup(self, win: QtWidgets.QMainWindow):
        from KKT_Module.KKTGraph.ShowRawData import FeatVectorGraph
        setup_config(SettingConfigs.ParamDict)
        wg = pg.LayoutWidget()
        win.resize(700, 500)
        win.setWindowTitle('Raw data to Feat Vector')
        win.setWindowTitle('Feat vector')
        self.FeatVector = FeatVectorGraph()
        self.FeatVector.setCh1AxisRange([0, 35], [-50, 100])
        self.FeatVector.setCh2AxisRange([0, 35], [-10, 10])
        self.lb = QtWidgets.QLabel('fps : ')
        wg.addWidget(self.lb, 0, 0)
        wg.addWidget(self.FeatVector, 1, 0)
        win.setCentralWidget(wg)
        win.show()
        pass

    def update(self, res):
        rawdata = np.hstack([res[0], res[1]])
        feature_map = preprocessing_fx_HW(rawdata)[6]
        self.FeatVector.setData(feature_map[:32,:], feature_map[32:,:])
        self.lb.setText('fps : {:.2f}'.format((10 ** 9) / ((time.time_ns() - self.s) + np.finfo(np.float32).eps)))
        self.s = time.time_ns()
        pass
