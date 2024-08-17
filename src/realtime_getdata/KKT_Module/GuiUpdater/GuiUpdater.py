import time
import os

import h5py
import numpy as np
from PySide2 import QtWidgets,QtCore, QtGui
from collections import deque
from KKT_Module.ksoc_global import kgl
from KKT_Module.Configs import SettingConfigs, RecordingConfigs
from KKT_Module.KKTUtility.qt_obj import CMessageBox, OKMessageBox, TimeMessageBox
from KKT_Module.KKTUtility.GestureObserver import GestureObserver
from KKT_Module.QtObject.ModeWindow import ModeWindow, KKTMainWindow
from KKT_Module.KKTUtility.PostProcess import PostProcess
from KKT_Module.KKTUtility.Debounce import Debounce

from abc import ABCMeta, abstractmethod
# from DSP_Module.RDI_gen2_module import RDI_gen2,RDI_gen3,phase_detect,find_peak, gen_RDI, cfg1, cfg2, cfg3

class Updater(metaclass=ABCMeta):
    def __init__(self):
        self.Widgets = []
        self.win = None
        self.FPS_counter = FPSCounter()
        pass
    def __del__(self):
        self.deleteWidgets()

    @abstractmethod
    def setup(self, win:KKTMainWindow):
        pass

    @abstractmethod
    def update(self,res):
        pass

    def deleteWidgets(self):
        for widget in self.Widgets:
            try:
                widget.deleteLater()
            except Exception as error:
                print(error)
        pass

    def setChirp(self,chirp):
        pass

    def addWidgetToCanvas(self):
        pass

    def addWidgetToSublayout(self):
        pass

    def enableSublayoutWidget(self, enable):
        pass

    def setConfigs(self,**kwargs):
        for k,v in kwargs.items():
            if not hasattr(self, k):
                print( 'Attribute "{}" not in updater.'.format(k))
                continue
            # assert hasattr(self, k), 'Attribute "{}" not in receiver.'.format(k)
            self.__setattr__(k,v)
            print('Attribute "{}", set "{}"'.format(k, v))
        pass

    def updateBufferData(self, res):
        return res

    def updateLoadData(self, load_data):
        return load_data

class RawDataUpdater(Updater):
    '''
    Present CH1 CH2 Raw data with stem plot.
    '''
    def __init__(self):
        super(RawDataUpdater, self).__init__()
        pass
    def setup(self, win):
        self.win = win
        self.addWidgetToCanvas()

    def update(self, res):
            self.RawData.setData(res[0], res[1])
            for chirp in range(32):
                i = chirp +1
                start = i*128-64
                res[0][start:start+64] = np.zeros(64)
                res[1][start:start+64] = np.zeros(64)
            self.UpChirpRawData.setData(res[0], res[1])
            self.lb.setText('fps : {:.2f}'.format(self.FPS_counter.updateFPS()))
            pass

    def addWidgetToCanvas(self):
        from KKT_Module.KKTGraph.ShowRawData import RawDataGraph
        self.RawData = RawDataGraph()
        self.UpChirpRawData = RawDataGraph()

        if hasattr(self.win,'lb_FPS'):
            self.lb = self.win.lb_FPS
        else:
            self.lb = QtWidgets.QLabel('fps : ')
            self.Widgets.append(self.lb)
            self.win.canvas_layout.addWidget(self.lb)

        self.Widgets.append(self.RawData)
        self.Widgets.append(self.UpChirpRawData)

        self.win.canvas_layout.addWidget(self.RawData)
        self.win.canvas_layout.addWidget(self.UpChirpRawData)

class HardwareInferenceUpdater(Updater):
    def __init__(self):
        super(HardwareInferenceUpdater, self).__init__()
        self.bg_id = '0'
        self.enable_debounce = False
        self.ges_dict = {}
        self.PostProcess = PostProcess(self.bg_id)
        self.debounce = Debounce(bg_id=self.bg_id,enable=self.enable_debounce)
        self._CoreOb = GestureObserver()
        self.setting_config = None
        # self.s = time.time_ns()
        pass
    def setConfigs(self,**kwargs):
        super(HardwareInferenceUpdater, self).setConfigs(**kwargs)
        setting_config = kwargs.get('setting_config')
        if setting_config is not None:
            self.setting_config = setting_config
            self.bg_id = setting_config.getBackgroundID()
            self.ges_dict = setting_config.CoreGestures
        bg_id = kwargs.get('bg_id')
        if bg_id is not None:
            self.bg_id = str(bg_id)
        enable_debounce = kwargs.get('enable_debounce')
        if enable_debounce is not None:
            self.enable_debounce = enable_debounce
        ges_dict = kwargs.get('ges_dict')
        if ges_dict is not None:
            self.ges_dict = ges_dict
        self.PostProcess = PostProcess(self.bg_id)
        self.debounce = Debounce(bg_id=self.bg_id,enable=self.enable_debounce)
        self._CoreOb.ges_dict = self.ges_dict

    def setup(self, win: ModeWindow):
        self.win = win
        self.addWidgetToCanvas()
        self.addWidgetToSublayout()
        pass

    def addWidgetToCanvas(self):
        from KKT_Module.KKTGraph.ShowResults import DrawingResult_GS

        self.ExponentialPlot = DrawingResult_GS(title='Exponential Value ( Hardware Inference )')
        # self.ExponentialPlot.enableWidget(Threshold=True)
        self.ExponentialPlot.setAxisRange([-1, 16] , [0, 1])
        # self.lb = QtWidgets.QLabel('fps : ')
        # self.win.canvas_layout.addWidget(self.lb)
        self.win.canvas_layout.addWidget(self.ExponentialPlot)

        # self.Widgets.append(self.lb)
        self.Widgets.append(self.ExponentialPlot)

    def addWidgetToSublayout(self):
        from KKT_Module.KKTUtility.qt_obj import CollapsibleSection
        self.post_process_section = CollapsibleSection('Post Processing')
        self.post_process_section.grid.addWidget(self.ExponentialPlot.threshold, 0,0,1,2)

        self.win.main_sublayout.addWidget(self.post_process_section,4,0 )
        self.Widgets.append(self.post_process_section)

    def update(self, res):
        gesture_num = len(self.setting_config.CoreGestures)
        if gesture_num > 0:
            exponential = (res[2]/res[2].sum())[:gesture_num]
        else:
            exponential = (res[2] / res[2].sum())
        self.ExponentialPlot.setData(exponential)
        th = self.ExponentialPlot.getThresholdList()
        ges_id = str(self.PostProcess.postprocess(exponential, th[0], th[1]))
        ges_id = self.debounce.debounce(ges_id)
        if ges_id != self.setting_config.getBackgroundID():
            ges = self._CoreOb.setGesture(ges_id)
            self.ExponentialPlot.setGestureLabel(ges)
            print(self.setting_config.CoreGestures.get(str(ges_id)), th[0], th[1])
        self.win.lb_FPS.setText('fps : {:.2f}'.format(self.FPS_counter.updateFPS()))
        pass

class TrackingUpdater(Updater):
    def __init__(self):
        super(TrackingUpdater, self).__init__()
        pass

    def setup(self, win:ModeWindow):
        self.win = win
        from KKT_Module.KKTGraph.ShowTracking import DrawingPosition
        self.wg = QtWidgets.QWidget()
        ly = QtWidgets.QGridLayout()
        self.wg.setLayout(ly)
        self.T_YZ = DrawingPosition('YZ Tracking')
        self.T_XZ = DrawingPosition('XZ Tracking')
        ly.addWidget(self.T_XZ, 0, 0 ,1 ,1)
        ly.addWidget(self.T_YZ, 0, 1 ,1 ,1)
        self.lb = QtWidgets.QLabel('fps :')
        self.win.canvas_layout.addWidget(self.lb)
        self.win.canvas_layout.addWidget(self.wg)
        self.Widgets.append(self.wg)
        self.Widgets.append(self.lb)
        pass

    def update(self, res):
        print('[Axis]X={:.3f}, Y={:.3f}, Z={:.3f}'.format(res[2][0], res[2][1], res[2][2]))
        data = res[2] / 64
        x = np.asarray([data[0]])
        y = np.asarray([data[1]])
        z = np.asarray([data[2]])
        self.T_XZ.setData(x, z)
        self.T_YZ.setData(y, z)
        self.lb.setText('fps : {:.2f}'.format(self.FPS_counter.updateFPS()))
        pass

class FeatureMapUpdater(Updater):
    def __init__(self):
        super(FeatureMapUpdater, self).__init__()
        pass

    def setup(self, win):
        from KKT_Module.KKTGraph.ShowFeatureMap import FeatureMapWidget
        self.win = win
        self.FeatureMap = FeatureMapWidget()
        self.lb = QtWidgets.QLabel('fps : ')
        self.Widgets.append(self.FeatureMap)
        self.Widgets.append(self.lb)
        self.win.canvas_layout.addWidget(self.lb)
        self.win.canvas_layout.addWidget(self.FeatureMap)
        pass

    def update(self, res):
        self.FeatureMap.setData(res[0], res[1])
        self.lb.setText('fps : {:.2f}'.format(self.FPS_counter.updateFPS()))
        pass

class TuneVolumeUpdater(Updater):
    def __init__(self):
        super(TuneVolumeUpdater, self).__init__()
        self.s = time.time_ns()
        self.pos_dict = {1:[-4,8], 2:[4,8], 3:[0,11], 4:[5,14]}
        self.pos_cnt = 0
        self.PosBufferSize = 1
        self.PosBuffer = np.zeros(self.PosBufferSize)
        pass

    def setup(self, win: QtWidgets.QMainWindow):
        wg = pg.LayoutWidget()
        self.Vol_Bar = QtWidgets.QSlider()
        self.lb = QtWidgets.QLabel('fps :')
        self.Vol_Bar.setRange(0,100)
        self.Vol_Bar.setValue(50)
        wg.addWidget(self.lb, 0, 0)
        wg.addWidget(self.Vol_Bar, 1, 0)
        win.setCentralWidget(wg)
        win.show()
        pass

    def update(self, res):
        # data = res[2] / 64
        # print('[Axis]X={:.2f}, Y={:.2f}, Z={:.2f}'.format(res[0], res[1], res[2]))
        print('[Axis]X={:.3f}, Y={:.3f}, Z={:.3f}'.format(res[2][0], res[2][1], res[2][2]))

        self.PosBuffer = np.roll(self.PosBuffer, 1)
        self.PosBuffer[-1] = res[1][0]
        self.pos_cnt = self.pos_cnt + 1
        if self.pos_cnt == self.PosBufferSize:
            self.pos_cnt = 0
            Pos = self.PosBuffer.mean()
            # print( Pos)
            self.adjustVolume(Pos)

        self.lb.setText('fps : {:.2f}'.format(self.FPS_counter.updateFPS()))
        pass

    def adjustVolume(self, Pos):
        if Pos <= -10:
            if self.volume < 100:
                self.volume = self.volume + 7
                self.Vol_Bar.setValue(self.volume)
        elif Pos >= 10:
            if self.volume > 0:
                self.volume = self.volume - 7
                self.Vol_Bar.setValue(self.volume)

class FPSCounter:
    def __init__(self):
        self.s = None

    def reset(self):
        self.s = None
        pass

    def updateFPS(self):
        if self.s is None:
            self.s = time.time_ns()
        fps = (10 ** 9) / ((time.time_ns() - self.s) + np.finfo(np.float32).eps)
        self.s = time.time_ns()
        return fps

class KKTDataSafer:
    def __init__(self):
        self._H5file_path = None
        self._KKTfile_path = None
        self._save_file_dir = None
        self._save_file_Name = None
        self._save_video_file_dir = None
        self._data_type_dir = {'RDIPHD':'RDI_fx',
                               'RawData':'RawData'}

    def saveH5(self, H5_file_path, recording_config:RecordingConfigs):
        from h5py import File
        print('record h5 file : ', H5_file_path)
        with File(H5_file_path, "w") as f:
            AXIS = np.asarray(recording_config.Axis, dtype='float16')
            DS1 = np.asarray(recording_config.DS1, dtype='float16')
            LABEL = np.asarray(recording_config.Label, dtype='int16')
            f.create_dataset('/AXIS', data=AXIS)
            f.create_dataset('/DS1', data=DS1)
            f.create_dataset('/LABEL', data=LABEL)
            self._addAttributes(f, recording_config)
            return f

    def saveKKT(self, KKT_file_path, recording_config:RecordingConfigs):
        from h5py import File
        from io import BytesIO
        bio = BytesIO()
        with File(bio, 'w') as f:
            AXIS = np.asarray(recording_config.Axis, dtype='float16')
            DS1 = np.asarray(recording_config.DS1, dtype='float16')
            LABEL = np.asarray(recording_config.Label, dtype='int16')
            f.create_dataset('/AXIS', data=AXIS)
            f.create_dataset('/DS1', data=DS1)
            f.create_dataset('/LABEL', data=LABEL)
            self._addAttributes(f, recording_config)
        self._crypt_file_save(bio, KKT_file_path)

    def getSaveInfo(self):
        return self._save_file_dir,self._save_video_file_dir, self._save_file_Name

    def _crypt_file_save(self, BytesIOObject, KKT_file_path):
        from zlib import compress
        from io import BytesIO
        from KKT_Module.KKTUtility.crypt_encode_file import Get_Crypted_Key, Encode_BytesIOObject
        print('crypt file processing ...')
        if True:
            s = time.time()
            com_con = compress(BytesIOObject.getvalue())
            print("compress time: {}".format(time.time()-s))
            BytesIOObject = BytesIO(com_con)

        public_key = Get_Crypted_Key()
        Ouput_IOFile, encrypted_b64 = Encode_BytesIOObject(BytesIOObject, public_key)
        with open(KKT_file_path, 'wb') as f:
            f.write(Ouput_IOFile.getvalue())
            # f.write(com_con)
        BytesIOObject.close()
        print('Save Record File : ', KKT_file_path)

    def _addAttributes(self, f, recording_config:RecordingConfigs):
        Data_config = f.create_group("DATA_CONFIG")
        for attr, config in recording_config.DataConfigs.items():
            Data_config.attrs[attr] = config
        RF_config = f.create_group("RF_CONFIG")
        for attr, config in recording_config.RFConfigs.items():
            RF_config.attrs[attr] = config
        # ===================================================================

        if recording_config.DataConfigs['Data_format'] == 'RDIPHD':
            DSP_config = f.create_group("DSP_CONFIG")
            AIC_config = f.create_group("DSP_CONFIG/AIC_CONFIG")
            AGC_config = f.create_group("DSP_CONFIG/AGC_CONFIG")
            RDI_config = f.create_group("DSP_CONFIG/RDI_CONFIG")
            PHD_config = f.create_group("DSP_CONFIG/PHD_CONFIG")
            for attr, config in recording_config.DSP_Configs.items():
                DSP_config.attrs[attr] = config
            for attr, config in recording_config.AIC_Configs.items():
                AIC_config.attrs[attr] = config
            for attr, config in recording_config.AGC_Configs.items():
                AGC_config.attrs[attr] = config
            for attr, config in recording_config.RDI_Configs.items():
                RDI_config.attrs[attr] = config
            for attr, config in recording_config.PHD_Configs.items():
                PHD_config.attrs[attr] = config

    def genSaveFileName(self, recording_config:RecordingConfigs):
        gesture = ''.join(ges for ges in recording_config.DataConfigs['Gesture_name'])
        gesture = gesture.replace(' ', '_')
        data_time = recording_config.DataConfigs['Datatime']
        # self._save_file_Name = (gesture + '_' + '{:04}'.format(1) + '_' + data_time)
        save_file_Name ='_'.join([gesture, '{:04}'.format(1), data_time])
        return save_file_Name

    def genSaveDir(self, recording_config:RecordingConfigs):
        data_type_dir = self._data_type_dir.get(recording_config.DataConfigs['Data_format'])
        record_dir = recording_config.Record_Folder
        save_file_dir = os.path.join(kgl.KKTRecord, data_type_dir, record_dir)
        if not os.path.isdir(save_file_dir):
            os.makedirs(save_file_dir, exist_ok=True)
            print('Make Data record dir : {}'.format(save_file_dir))
        return save_file_dir

    def genSaveVideoDir(self, recording_config: RecordingConfigs):
        record_dir = recording_config.Record_Folder
        save_video_file_dir = os.path.join(kgl.KKTRecord, 'Video', record_dir)
        if not os.path.isdir(save_video_file_dir):
            os.makedirs(save_video_file_dir, exist_ok=True)
            print('Make Video record dir : {}'.format(save_video_file_dir))
        return save_video_file_dir

    def genSaveFilePath(self, recording_config:RecordingConfigs):
        import os
        self._save_file_Name = self.genSaveFileName(recording_config=recording_config)
        self._save_file_dir = self.genSaveDir(recording_config)
        self._save_video_file_dir = self.genSaveVideoDir(recording_config)
        self._H5file_path = os.path.join(self._save_file_dir,self._save_file_Name+'.h5')
        self._KKTfile_path = os.path.join(self._save_file_dir,self._save_file_Name+'.kkt')

        return self._H5file_path, self._KKTfile_path


class DataBuffer:
    def __init__(self, buffer_len=None):
        '''
        Data buffer for received data, it will save latest frames data.

        :param buffer_len: numbers of frames to save temporary.
        '''
        self._buffer_len = buffer_len
        self._buffer = deque(maxlen=buffer_len)
        self.initBuffer(self._buffer_len)
        pass
    def __del__(self):
        self._buffer.clear()

    def getDataBuffer(self, as_array=False):
        '''
        Get the buffer.

        :return: latest frames data in List.
        '''
        if as_array:
            return np.asarray(self._buffer)
        else:
            return  self._buffer

    def updateBuffer(self, res):
        '''
        To update the buffer per frame.

        :param res: received data.
        '''
        self._buffer.append(res)
        # if self.buffer_number < self._buffer_len:
        #     self.buffer_number = self.buffer_number + 1

    def initBuffer(self, buffer_len=None):
        '''
        Init the buffer size.
        :param buffer_len: buffer size.
        '''
        self._buffer_len = buffer_len
        self._buffer.clear()
        self._buffer = deque(maxlen=buffer_len)

    def setBuffer(self, buffer):
        self._buffer = buffer

    def getBufferLength(self):
        return len(self._buffer)

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    win = ModeWindow()
    updater = HardwareInferenceUpdater()
    updater.setup(win)
    win.show()
    app.exec_()
    pass