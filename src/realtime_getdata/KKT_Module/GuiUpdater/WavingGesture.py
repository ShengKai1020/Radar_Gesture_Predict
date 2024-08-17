class RawDataWavingGestureUpdater(Updater):
    def __init__(self):
        super(RawDataWavingGestureUpdater, self).__init__()
        self.s = time.time_ns()
        from Tracking.Tracking_init import Motion, config_struct
        self._Motion = Motion()
        self._T_struct = config_struct()
        self.x_cache = np.zeros(15)  # Cache of 15 frames, could be programmable
        self.y_cache = np.zeros(15)  # Cache of 15 frames, could be programmable
        pass

    def setup(self, win: ModeWindow):
        self.win = win
        self.addWidgetToCanvas()
        pass

    def addWidgetToCanvas(self):
        from KKT_Module.KKTGraph.ShowTracking import DrawingPosition
        self.T_XY = DrawingPosition('XY Tracking')
        self.lb = QtWidgets.QLabel('fps :')

        self.Widgets.append(self.T_XY)
        self.Widgets.append(self.lb)

        self.win.canvas_layout.addWidget(self.lb)
        self.win.canvas_layout.addWidget(self.T_XY)

    def enableSublayoutWidget(self, enable):
        pass

    def update(self, res):
        self._Motion.AIC_processing(res[0])
        X, Y = self._T_struct.tracking_run(res[0], res[1])
        # print('[Axis]X={:.3f}, Y={:.3f}'.format(X, Y))
        self.waveGesture(X, Y)
        x = -1*np.asarray([X])
        y = np.asarray([Y])
        self.T_XY.setData(x, y)
        self.lb.setText('fps : {:.2f}'.format((10 ** 9) / ((time.time_ns() - self.s) + np.finfo(np.float32).eps)))
        self.s = time.time_ns()
        pass

    def waveGesture(self, x, y):
        self.x_cache = np.roll(self.x_cache, -1)
        self.y_cache = np.roll(self.y_cache, -1)

        # Update latest Tracking result into cache
        self.x_cache[-1] = 1 * x

        self.y_cache[-1] = 1 * y

        # Calculate element-wise diffence value
        x_diff = np.diff(self.x_cache)
        y_diff = np.diff(self.y_cache)

        if np.abs(np.max(self.x_cache) - np.min(self.x_cache)) > 8:  # Check x cache value distance over 20, 20 could be programmable
            # Check x direction and avoild some unexpected behavior
            print(self.x_cache)
            if (np.sum(x_diff) > 0) and (np.any(self.x_cache[0:8] < -1)) and (np.any(self.x_cache[8:] > 1)):
                print('Left')
                post_out = 1
                # Reset x cache
                self.x_cache = np.zeros(15)
                # Reset tracking
                kgl.ksoclib.writeReg(1, 0x5000000C, 19, 19, 0)
                time.sleep(0.01)  # I am not sure that fw needs it or not
                # Restart tracking
                kgl.ksoclib.writeReg(0, 0x5000000C, 19, 19, 0)

            elif np.sum(x_diff) < 0 and (np.any(self.x_cache[0:8] > 1)) and (np.any(self.x_cache[8:] < -1)):

                print('Right')
                post_out = 2
                # Reset x cache
                self.x_cache = np.zeros(15)
                # Reset tracking
                kgl.ksoclib.writeReg(1, 0x5000000C, 19, 19, 0)
                time.sleep(0.01)  # I am not sure that fw needs it or not
                # Restart tracking
                kgl.ksoclib.writeReg(0, 0x5000000C, 19, 19, 0)
        elif np.abs(np.max(self.y_cache) - np.min(self.y_cache)) > 5:  # Check y cache value distance over 20, 20 could be programmable
                                                                # Check y direction and avoild some unexpected behavior
            print(self.y_cache)
            if np.sum(y_diff) > 0 and (np.any(self.y_cache[0:8] < -1)) and (np.any(self.y_cache[8:] > 1)):
                print('Up')
                post_out = 3
                # Reset y cache
                self.y_cache = np.zeros(15)
                # Reset tracking
                kgl.ksoclib.writeReg(1, 0x5000000C, 19, 19, 0)
                time.sleep(0.01)  # I am not sure that fw needs it or not
                # Restart tracking
                kgl.ksoclib.writeReg(0, 0x5000000C, 19, 19, 0)
            elif np.sum(y_diff) < 0 and (np.any(self.y_cache[0:8] > 1)) and (np.any(self.y_cache[8:] < -1)):
                print('Down')
                post_out = 4
                # Reset y cache
                self.y_cache = np.zeros(15)
                # Reset tracking
                kgl.ksoclib.writeReg(1, 0x5000000C, 19, 19, 0)
                time.sleep(0.01)  # I am not sure that fw needs it or not
                # Restart tracking
                kgl.ksoclib.writeReg(0, 0x5000000C, 19, 19, 0)
        else:
            print(self.y_cache)

        # If there is no object, tracking hw will be reset
        if (np.all(self.x_cache == self.x_cache[0])) and (self.x_cache[0] != 0):
            # Reset tracking
            kgl.ksoclib.writeReg(1, 0x5000000C, 19, 19, 0)
            time.sleep(0.01)  # I am not sure that fw needs it or not
            # Restart tracking
            kgl.ksoclib.writeReg(0, 0x5000000C, 19, 19, 0)

    def deleteWidgets(self):
        super(RawDataWavingGestureUpdater, self).deleteWidgets()
        # self.T_XY.deleteLater()
        # self.lb.deleteLater()

class ResultsWavingGestureUpdater(Updater):
    def __init__(self):
        super(ResultsWavingGestureUpdater, self).__init__()
        self.s = time.time_ns()
        self.x_cache = np.zeros(15)  # Cache of 15 frames, could be programmable
        self.y_cache = np.zeros(15)  # Cache of 15 frames, could be programmable
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(lambda : self.countGes())
        pass

    def setup(self, win: ModeWindow):
        self.win = win
        self.addWidgetToCanvas()
        pass

    def addWidgetToCanvas(self):
        from KKT_Module.KKTGraph.ShowTracking import DrawingPosition
        self.T_XY = DrawingPosition('XY Tracking')
        self.T_XY.setRange(xRange=[-20,20], yRange=[-20,20])
        self.lb_ges = QtWidgets.QLabel('Gesture = ')
        self.lb_ges.setFont(QtGui.QFont('Yu Gothic UI', 15))
        self.lb = QtWidgets.QLabel('fps :')

        self.Widgets.append(self.T_XY)
        self.Widgets.append(self.lb_ges)
        self.Widgets.append(self.lb)


        self.win.canvas_layout.setContentsMargins(7,7,7,7)
        self.win.canvas_layout.addWidget(self.lb)
        self.win.canvas_layout.addWidget(self.T_XY)
        self.win.canvas_layout.addWidget(self.lb_ges)

    def enableSublayoutWidget(self, enable):
        pass

    def setChirp(self, chirp):
        pass

    def countGes(self):
        self.timer.stop()
        self.lb_ges.setText('Gesture = ')

    def update(self, res):
        # print(res[1])
        X = res[1][0]/64
        Y = res[1][1]/64
        self.waveGesture(X , Y)
        x = np.asarray([X])
        y = np.asarray([Y])
        self.T_XY.setData(x, y)
        self.lb.setText('fps : {:.2f}'.format((10 ** 9) / ((time.time_ns() - self.s) + np.finfo(np.float32).eps)))
        self.s = time.time_ns()
        pass

    def waveGesture(self, x, y):
        self.x_cache = np.roll(self.x_cache, -1)
        self.y_cache = np.roll(self.y_cache, -1)

        # Update latest Tracking result into cache
        self.x_cache[-1] = 1 * x

        self.y_cache[-1] = 1 * y

        # Calculate element-wise diffence value
        x_diff = np.diff(self.x_cache)
        y_diff = np.diff(self.y_cache)

        if np.abs(np.max(self.x_cache) - np.min(self.x_cache)) > 20:  # Check x cache value distance over 20, 20 could be programmable
            # Check x direction and avoild some unexpected behavior
            # print(self.x_cache)
            if (np.sum(x_diff) > 0) and (np.any(self.x_cache[0:8] < -1)) and (np.any(self.x_cache[8:] > 1)):
                print('Right')
                self.timer.start(1500)
                self.lb_ges.setText('Gesture = {}'.format('Right'))
                post_out = 1
                # Reset x cache
                self.x_cache = np.zeros(15)
                # Reset tracking
                kgl.ksoclib.writeReg(1, 0x5000000C, 19, 19, 0)
                time.sleep(0.01)  # I am not sure that fw needs it or not
                # Restart tracking
                kgl.ksoclib.writeReg(0, 0x5000000C, 19, 19, 0)

            elif np.sum(x_diff) < 0 and (np.any(self.x_cache[0:8] > 1)) and (np.any(self.x_cache[8:] < -1)):

                print('Left')
                self.timer.start(1500)
                self.lb_ges.setText('Gesture = {}'.format('Left'))
                post_out = 2
                # Reset x cache
                self.x_cache = np.zeros(15)
                # Reset tracking
                kgl.ksoclib.writeReg(1, 0x5000000C, 19, 19, 0)
                time.sleep(0.01)  # I am not sure that fw needs it or not
                # Restart tracking
                kgl.ksoclib.writeReg(0, 0x5000000C, 19, 19, 0)
        elif np.abs(np.max(self.y_cache) - np.min(self.y_cache)) > 20:  # Check y cache value distance over 20, 20 could be programmable
                                                                # Check y direction and avoild some unexpected behavior
            # print(self.y_cache)
            # print(np.sum(y_diff))
            if np.sum(y_diff) > 0 and (np.any(self.y_cache[0:8] < -1)) and (np.any(self.y_cache[8:] > 1)):
                print('Up')
                self.timer.start(1500)
                self.lb_ges.setText('Gesture = {}'.format('Up'))
                post_out = 3
                # Reset y cache
                self.y_cache = np.zeros(15)
                # Reset tracking
                kgl.ksoclib.writeReg(1, 0x5000000C, 19, 19, 0)
                time.sleep(0.01)  # I am not sure that fw needs it or not
                # Restart tracking
                kgl.ksoclib.writeReg(0, 0x5000000C, 19, 19, 0)
            elif np.sum(y_diff) < 0 and (np.any(self.y_cache[0:8] > 1)) and (np.any(self.y_cache[8:] < -1)):
                print('Down')
                self.timer.start(1500)
                self.lb_ges.setText('Gesture = {}'.format('Down'))
                post_out = 4
                # Reset y cache
                self.y_cache = np.zeros(15)


                # Reset tracking
                kgl.ksoclib.writeReg(1, 0x5000000C, 19, 19, 0)
                time.sleep(0.01)  # I am not sure that fw needs it or not
                # Restart tracking
                kgl.ksoclib.writeReg(0, 0x5000000C, 19, 19, 0)


        # If there is no object, tracking hw will be reset
        if (np.all(self.x_cache == self.x_cache[0])) and (self.x_cache[0] != 0):
            # Reset tracking
            kgl.ksoclib.writeReg(1, 0x5000000C, 19, 19, 0)
            time.sleep(0.01)  # I am not sure that fw needs it or not
            # Restart tracking
            kgl.ksoclib.writeReg(0, 0x5000000C, 19, 19, 0)

    def deleteWidgets(self):
        super(ResultsWavingGestureUpdater, self).deleteWidgets()
        # self.T_XY.deleteLater()
        # self.lb_ges.deleteLater()
        # self.lb.deleteLater()