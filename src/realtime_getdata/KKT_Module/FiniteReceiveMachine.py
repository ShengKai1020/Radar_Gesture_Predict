import datetime
import sys
import time
import numpy as np
from KKT_Module.DataReceive.DataReciever import Receiver
from KKT_Module.GuiUpdater.GuiUpdater import DataBuffer
from PySide2 import QtWidgets, QtCore



class FiniteReceiveMachine():
    '''
    Receive hardware data from import receiver and Update plots on input QMainWindow.
    Please input arguments "app" to run any QT objects.
    '''
    def __init__(self, app=None):
        super(FiniteReceiveMachine, self).__init__()
        self._receiver = None
        self._result = None
        self._updater = None
        self.win = None
        self.app = app
        self._pause = False
        self._data_buffer = DataBuffer(100)
        self._load_frame = 0
        self.enable_buffer = False
        self.T_receive = QtCore.QTimer()
        self.T_replay = QtCore.QTimer()
        self.T_replay.timeout.connect(lambda : self._displayBuffedData())

    def __del__(self):
        self.__cleanup()

    def __cleanup(self):
        # self.stop()
        print("Close Finite Receive Machine...")

    def setMainWin(self, win):
        self.win = win

    def setFRM(self, receiver:Receiver, updater=None):
        self._receiver = receiver
        self._updater = updater
        if self._updater is not None:
            assert self.app is not None
            self.setupGUI()

    def setReceiver(self, receiver):
        self._receiver = receiver

    def setUpdater(self, updater):
        self._updater = updater
        self.setupGUI()

    def trigger(self, **trigger_arg):
        if self._receiver is None:
            return
        # assert self._receiver is not None
        self._receiver.trigger(**trigger_arg)

    def setupGUI(self):
        from KKT_Module.QtObject.ModeWindow import ModeWindow
        if self.win is None:
            self.win = ModeWindow(app = self.app)
            self.win.setup()
        self.win.close_Signal.connect(lambda : self.stop())
        self.win.pause_Signal.connect(lambda : self.pause())
        self.win.start_Signal.connect(lambda : self.start())
        self.win.trigger_Signal.connect(lambda: self.trigger())
        self.win.delete_Signal.connect(lambda: self.deleteUpdaterWidgets())
        self.win.setup_Signal.connect(lambda: self.setupWidgets())
        self.setupWidgets()

    def start(self, buffer=False):
        self.enable_buffer = buffer
        self._data_buffer.__del__()
        if self._receiver is None:
            return
        print('start FSM')
        self._loop = True
        if self._pause:
            self._pause = False

        # if self.app is not None:
        #     self.T_receive.timeout.connect(lambda: self.get())
        #     self.T_receive.start(2)
        # else:
        while self._loop:
            if self.app is not None:
                self.app.processEvents()
            self.get()


    def initDataBuffer(self, buffer_len):
        self._data_buffer.initBuffer(buffer_len)

    def updateBuffer(self, res):
        data = self._updater.updateBufferData(res)
        self._data_buffer.updateBuffer(data)

    def getBuffedNumber(self):
        return self._data_buffer.getBufferLength()

    def stop(self):
        self._loop = False
        if hasattr(self, '_receiver') and (self._receiver is not None):
            self._receiver.stop()
            # self._data_buffer.__del__()
            self.T_receive.stop()
        print('stop receiver')

    def pause(self):
        self._pause = True
        self._loop = False
        print('pause')

    def get(self):
        res = self._receiver.getResults()
        if res is None:
            return
        # print(res)
        if self._updater is not None:
            self._updater.update(res)
        if self.enable_buffer:
            self.updateBuffer(res)
            self.win.updateBuffedNum(self._data_buffer.getBufferLength())

    def _dataTimer(self):
        self._result = self._receiver.getResults()

    def deleteUpdaterWidgets(self):
        if self._updater is None:
            return
        self._updater.deleteWidgets()

    def setupWidgets(self):
        if self._updater is None:
            return
        self._updater.setup(self.win)

    def saveBufferData(self, data_name, fmt='%d', header='BUFFER DATA RECORDING' ):
        data = self._data_buffer.getDataBuffer()
        data = np.stack(data)
        np.savetxt(data_name, data, fmt=fmt, header=header, delimiter=',')
        pass

    def loadBufferData(self, file_name, dtype='int16'):
        self._load_data = np.loadtxt(file_name, dtype=dtype, delimiter=',',comments='#')
        header_dict = {}
        with open(file_name) as f:
            headers = f.readlines()
        for header in headers:
            if header[0] in ['#']:
                header = header.split('#')[1].strip().split(' :')
                if len(header) == 2:
                    header_dict[header[0]] = header[1]

        return self._load_data, header_dict

    def replayBuffedData(self, frame_time=50):
        assert self.app is not None
        self.T_replay.start(frame_time-10)
        pass

    def stopReplay(self):
        assert self.app  is not None
        self.T_replay.stop()
        # self.T.timeout.disconnect(lambda: self._displayBuffedData())
        self._load_frame = 0

    def _displayBuffedData(self):
        if self._load_frame == len(self._load_data):
            self.T_replay.stop()
            self._load_frame = 0
            self.win.enableWidgetPressStart(False)
            self.win._pb_start.setEnabled(True)
            self.win.enableRFSettingWidget(True)
            return
        res = self._updater.updateLoadData(self._load_data[self._load_frame])
        self._updater.update(res)
        self._load_frame = self._load_frame+1
        self.win.updateBuffedNum(str(self._load_frame))

    def setWinTitle(self, title):
        self.win.setWindowTitle(title)

    def setConfigs(self, **kwargs):
        for k, v in kwargs.items():
            if not hasattr(self, k):
                print('Attribute "{}" not in receiver.'.format(k))
                continue
            # assert hasattr(self, k), 'Attribute "{}" not in receiver.'.format(k)
            self.__setattr__(k, v)
            print('Attribute "{}", set "{}"'.format(k, v))


if __name__ == '__main__':
    from KKT_Module.ksoc_global import kgl
    from KKT_Module.ModeSelect import ModeSelector, KsocModeConfigs
    kgl.setLib()
    kgl.ksoclib.connectDevice()
    app = QtWidgets.QApplication([])
    m = KsocModeConfigs(
        receiver='HWResult',
        updater='HardwareInference',
        user_level=1,
        need_set_script=True,
        app='app'
    )
    u = ModeSelector.selectUpdater(m)
    r = ModeSelector.selectReceiver(m)
    FSM = FiniteReceiveMachine(app)
    FSM.setFRM(r, u)
    FSM.win.show()
    FSM.trigger(chirps=32)
    FSM.initDataBuffer(100)
    FSM.start(buffer=True)
    app.exec_()



