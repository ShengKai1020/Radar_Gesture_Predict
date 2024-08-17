class ResultsPalmRotateUpdater(Updater):
    def __init__(self):
        super(ResultsPalmRotateUpdater, self).__init__()
        self.s = time.time_ns()
        from KKT_Module.KKTUtility.PostProcess import PostProcess
        self.post_process = PostProcess()
        self.cw_x_Cache = np.zeros([1, 10])
        self.cw_y_Cache = np.zeros([1, 10])
        self.forward_flag = 1 * np.ones(20)
        self.backward_flag = 0 * np.ones(20)
        self.cw_Cache = -1 * np.ones(20)
        self.clockwise_state = 'off'
        self.cnt = 0
        pass

    def setup(self, win: ModeWindow):
        self.win = win
        self.addWidgetToCanvas()
        pass

    def addWidgetToCanvas(self):
        from KKT_Module.KKTGraph.ShowTracking import DrawingPosition
        from KKT_Module.KKTGraph.ShowResults import DrawingResult_GS
        self.T_XY = DrawingPosition('XY Tracking')
        self.T_XY.setRange(xRange=[-20,20], yRange=[0,30])
        self.ExponentialPlot = DrawingResult_GS(title='Exponential Value ( Hardware Inference )')
        self.ExponentialPlot.enableWidget(Threshold=True)
        self.ExponentialPlot.setAxisRange([-1, 16], [0, 1])
        self.ExponentialPlot.setThreshold([0.1, 0.4])
        self.lb = QtWidgets.QLabel('fps :')
        self.lb_clockwise = QtWidgets.QLabel('Tracking Mode = ')
        self.lb_clockwise.setFont(QtGui.QFont("Yu Gothic UI", 12))

        self.Widgets.append(self.T_XY)
        self.Widgets.append(self.ExponentialPlot)
        self.Widgets.append(self.lb)
        self.Widgets.append(self.lb_clockwise)

        self.win.canvas_layout.addWidget(self.lb)
        self.win.canvas_layout.addWidget(self.ExponentialPlot, 2)
        self.win.canvas_layout.addWidget(self.lb_clockwise)
        self.win.canvas_layout.addWidget(self.T_XY, 2, alignment=QtGui.Qt.AlignLeft)

    def enableSublayoutWidget(self, enable):
        pass

    def setChirp(self, chirp):
        pass

    def update(self, res):
        softmax_ary = res[2]
        ydata = softmax_ary/sum(softmax_ary)
        self.ExponentialPlot.setData(ydata)
        th = self.ExponentialPlot.getThresholdList()
        output = self.post_process.postprocess(ydata, th[0], th[1])

        # res = np.asarray(list(axes_ary), dtype='int16')
        print(res[1])
        x_axis = np.asarray([res[1][0] / 64]) # Fetch x corordinate axis
        y_axis = np.asarray([res[1][1] / 64])  # Fetch y corordinate axis

        self.cw_x_Cache = np.roll(self.cw_x_Cache, -1)
        self.cw_y_Cache = np.roll(self.cw_y_Cache, -1)
        self.cw_x_Cache[0, -1] = x_axis
        self.cw_y_Cache[0, -1] = y_axis
        cw_ans = self.ispolycw_revise(self.cw_x_Cache, self.cw_y_Cache)  # Use these two array to determine clockwise or not
        # print(cw_ans)
        self.cw_Cache = np.roll(self.cw_Cache, -1)
        self.cw_Cache[-1] = cw_ans
        # print(output, self.clockwise_state)
        # if (output != 0) & (self.clockwise_state == 'off'):
        if (output != 0):
            print('{}: Gesture = {}, tracking={}'.format(self.cnt, output, np.asarray(list(res[1]), dtype='int16')))
            self.ExponentialPlot.setGestureLabel('{}'.format(output))
            # print(output)

        if self.clockwise_state == 'off':
            if (np.array_equal(self.cw_Cache, self.forward_flag)) | (np.array_equal(self.cw_Cache, self.backward_flag)):
                self.clockwise_state = 'on'
                print('Start Rotate')
                # self.ExponentialPlot.setGestureLabel('Start Rotate')
                self.lb_clockwise.setText('Tracking Mode = {}'.format(''))
                if self.cw_Cache[0] == 1:
                    print('Action of Forward')
                    # self.ExponentialPlot.setGestureLabel('Action of Forward')
                    self.lb_clockwise.setText('Tracking Mode = {}'.format('Action of Forward'))
                elif self.cw_Cache[0] == 0:
                    print('Action of Backward')
                    # self.ExponentialPlot.setGestureLabel('Action of Backward')
                    self.lb_clockwise.setText('Tracking Mode = {}'.format('Action of Backward'))
                self.cw_Cache = -2 * np.ones(10)
        elif self.clockwise_state == 'on':
            if np.array_equal(self.cw_Cache, self.forward_flag[10:]):
                print('Action of Forward')
                # self.ExponentialPlot.setGestureLabel('Action of Forward')
                self.lb_clockwise.setText('Tracking Mode = {}'.format('Action of Forward'))
                self.cw_Cache = -2 * np.ones(10)
            elif np.array_equal(self.cw_Cache, self.backward_flag[10:]):
                print('Action of Backward')
                # self.ExponentialPlot.setGestureLabel('Action of Backward')
                self.lb_clockwise.setText('Tracking Mode = {}'.format('Action of Backward'))
                self.cw_Cache = -2 * np.ones(10)
            elif np.array_equal(self.cw_Cache[5:], -1 * np.ones(5)):
                print('Back to normal')
                # self.ExponentialPlot.setGestureLabel('Back to normal')
                self.lb_clockwise.setText('Tracking Mode = {}'.format(''))
                self.clockwise_state = 'off'
                self.cw_Cache = -2 * np.ones(20)
        self.T_XY.setData(x_axis, y_axis)
        self.lb.setText('fps : {:.2f}'.format((10 ** 9) / ((time.time_ns() - self.s) + np.finfo(np.float32).eps)))
        self.s = time.time_ns()
        pass

    def ispolycw_revise(self, x, y):
        if ((x.max() - x.min()) > 4) | ((y.max() - y.min()) > 5):
            tf = self.isContourClockwise(x, y)
        else:
            tf = -1
        return tf

    def isContourClockwise(self, x, y):
        result = self.removeDuplicates(x, y)
        xx = result[0]
        yy = result[1]
        if xx.shape[0] > 5:
            tf = self.signedArea(xx, yy) <= 0
        else:
            tf = True

        if tf:
            output = 1
        else:
            output = 0
        return output

    def removeDuplicates(self, x, y):
        is_closed = (x[0, 0] == x[0, -1]) & (y[0, 0] == y[0, -1])
        if is_closed:
            x = np.delete(x, -1)
            y = np.delete(y, -1)
        m = (np.diff(x) == 0)
        n = (np.diff(y) == 0)
        p = m & n
        dups = np.insert(p, 0, False, axis=1)
        idx = np.logical_not(dups.flatten('F'))
        x_out = x[0, idx]
        y_out = y[0, idx]
        return x_out, y_out

    def signedArea(self, x, y):

        x = x - np.mean(x)
        n = x.shape[0]
        if n <= 2:
            a = 0
        else:
            i = np.roll(np.arange(n), -1)
            j = np.roll(np.arange(n), -2)
            k = np.arange(n)
            a = np.dot(x[i], (y[j] - y[k]))

        return a

    def update_stem(self, h_stem, x=None, y=None, bottom=None):
        if x is None:
            x = h_stem[0].get_xdata()
        else:
            h_stem[0].set_xdata(x)
            h_stem[2].set_xdata([np.min(x), np.max(x)])

        if y is None:
            y = h_stem[0].get_ydata()
        else:
            h_stem[0].set_ydata(y)

        if bottom is None:
            bottom = h_stem[2].get_ydata()[0]
        else:
            h_stem[2].set_ydata([bottom, bottom])

        h_stem[1].set_paths([np.array([[xx, bottom], [xx, yy]]) for (xx, yy) in zip(x, y)])

    def deleteWidgets(self):
        super(ResultsPalmRotateUpdater, self).deleteWidgets()
        # self.T_XY.deleteLater()
        # self.ExponentialPlot.deleteLater()
        # self.lb.deleteLater()