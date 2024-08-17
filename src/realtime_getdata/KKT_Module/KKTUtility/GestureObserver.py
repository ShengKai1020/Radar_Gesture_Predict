import os.path
from threading import Thread
from playsound import playsound
from KKT_Module.ksoc_global import kgl
from KKT_Module.Configs import SettingConfigs


class GestureObserver:
    def __init__(self, ges_dict={}, bg_id=-1):
        self._ges_dict = ges_dict
        self._gesture_mode = 'core'
        self._sia_frame = 50
        self._sia_cnt = 0
        self._sia_ges_dict = {}
        self._sound_dir = os.path.join(kgl.KKTSound, 'Temp')

    @property
    def ges_dict(self):
        return self._ges_dict

    @ges_dict.setter
    def ges_dict(self, ges_dict):
        self._ges_dict = ges_dict

    def setSiameseGestureDict(self, sia_ges_dict):
        self._sia_ges_dict = sia_ges_dict

    def setSiameseCountFrame(self, frame):
        self._sia_frame = frame

    def setSiameseGesture(self, ges_id):
        # print(self._gesture_mode)
        if self._gesture_mode != 'siamese':
            return
        self._siameseCounter()
        ges_id = str(ges_id)
        gesture = self._sia_ges_dict.get(ges_id)
        if gesture is None:
            # raise Exception('Gesture id.{} is not in gesture dict'.format(ges_id))
            print('Gesture id.{} is not in gesture dict'.format(ges_id))
            return
        print('Get Siamese gesture "{}" '.format(gesture))
        self._noticeObserver(gesture)

    def setGesture(self, ges_id):
        # print(self._gesture_mode)
        if self._gesture_mode != 'core':
            return
        ges_id = str(ges_id)

        if self._ges_dict.get('ges_id') == 'Switch':
            self._gesture_mode = 'siamese'
            print('Entry Siamese mode')
            return

        gesture = self._ges_dict.get(ges_id)
        if gesture is None:
            # raise Exception('Gesture id.{} is not in gesture dict'.format(ges_id))
            print('Normal gesture id.{} is not in gesture dict'.format(ges_id))
            return str(ges_id)
        print('Get Normal gesture "{}" '.format(gesture))
        self._noticeObserver(gesture)
        return  self._ges_dict[ges_id]

    def _siameseCounter(self):
        if self._sia_cnt == self._sia_frame:
            self._sia_cnt = 0
            self._gesture_mode = 'core'
            print('Entry Normal mode')
            return
        self._sia_cnt = self._sia_cnt + 1

    def _noticeObserver(self, gesture):
        sound_path = str(os.path.join(self._sound_dir, '{}.mp3'.format(gesture)))
        if os.path.isfile(sound_path):
        # sound_path = sound_path.replace(" ", "%20")
            T = Thread(target=playsound, args=(sound_path,))
            T.start()
        return

    def _getSoundPath(self):
        IC, ReleaseStatus, CustomerID, SubCustomerID, ProductVer, Date = SettingConfigs.getScriptInfo()
        sound_dir = os.path.join(kgl.KKTSound, CustomerID)
        self._sound_dir = sound_dir
        return sound_dir
















