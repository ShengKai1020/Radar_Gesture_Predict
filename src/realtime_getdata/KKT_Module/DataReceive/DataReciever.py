import os
import time
from datetime import datetime
import numpy as np
from KKT_Module.DataReceive.Parsing import ResultParsing
from abc import ABCMeta, abstractmethod
from KKT_Module.ksoc_global import kgl
from KKT_Module.KKTUtility.DigiControl import Digi168BController
from KKT_Module.Configs import INIConfigs


class Receiver(metaclass=ABCMeta):
    '''
    Data receiver.
    '''
    def __init__(self):
        self.trigger_arg = []
        self._trigger = False
        pass

    @abstractmethod
    def trigger(self, **kwargs):
        '''
        Before start to get the data which receivedH5 from the receiver,
        you have to init some configs and trigger it.
        '''
        print('triggered receiver : {}'.format(self.__class__.__name__))
        if not self._trigger:
            return

    @abstractmethod
    def getResults(self):
        '''
        Get the data which received from the receiver.
        '''
        if not self._trigger:
            return


    @abstractmethod
    def stop(self):
        '''
        Shut down the receiver.
        '''
        return

    def setConfig(self, **kwargs):
        for k,v in kwargs.items():
            if not hasattr(self, k):
                print( 'Attribute "{}" not in receiver.'.format(k))
                continue
            # assert hasattr(self, k), 'Attribute "{}" not in receiver.'.format(k)
            self.__setattr__(k,v)
            print('Attribute "{}", set "{}"'.format(k, v))

class ReceiverConfigs(INIConfigs):
    def __init__(self, filename):
        super(ReceiverConfigs, self).__init__(filename=filename)
        self.setINIConfigs()

    def setINIConfigs(self):
        for section in self.section:
            self.__setattr__(section, dict(self.config[section].items()))

    def getConfig(self, section):
        if not hasattr(self, section):
            return {}
        return self.__getattribute__(section)
# ============================

class ReadBBufferReceiver(Receiver):
    '''
    Rename from "ReadBBfferRecevier"
    '''
    def __init__(self):
        super(ReadBBufferReceiver, self).__init__()
        from read3CH128REG import ksoc_read_b_buffer
        self.ch1_buf, self.ch2_buf,self.ch3_buf = ksoc_read_b_buffer()
        self.saveData()
        pass

    def trigger(self):
        pass

    def getResults(self):
        time.sleep(0.05)
        return self.ch1_buf, self.ch2_buf,self.ch3_buf

    def stop(self):
        pass

    def saveData(self):
        date = datetime.now().strftime(r'%Y_%m_%d_%H_%M_%S')
        b_buffer_dir = os.path.join(os.getcwd(), 'Read_B_Buffer')
        if not os.path.isdir(b_buffer_dir):
            os.makedirs(b_buffer_dir, exist_ok=True)
        with open(os.path.join(b_buffer_dir, 'ch1_' + str(date) + '.txt'), mode='w') as f:
            for i in range(len(self.ch1_buf)):
                f.write(str(self.ch1_buf[i])+'\n')
        with open(os.path.join(b_buffer_dir, 'ch2_' + str(date) + '.txt'), mode='w') as f:
            for i in range(len(self.ch2_buf)):
                f.write(str(self.ch2_buf[i])+'\n')
        with open(os.path.join(b_buffer_dir, 'ch3_' + str(date) + '.txt'), mode='w') as f:
            for i in range(len(self.ch3_buf)):
                f.write(str(self.ch3_buf[i])+'\n')

class MultiResult4168BReceiver(Receiver):
    '''
    Rename from AIResultReceiver.

    Instance with interrupts and get hardware results when "read_interrupt"
    was detected ,clear the results when "clear_interrupt was detected."'''
    _res_addrs_dict = {
        'SoftmaxExponential': [addr for addr in range(0x50000508, 0x5000051C + 1, 4)],
        'Axis': [addr for addr in range(0x50000578, 0x5000057C + 1, 4)],
        'Gestures': [addr for addr in range(0x50000580, 0x50000580 + 1, 4)],
        'SiameseGestures': [addr for addr in range(0x50000580, 0x50000580 + 1, 4)],
        'SiameseExponential': [addr for addr in range(0x50000604, 0x50000618 + 1, 4)],
        'IMax': [addr for addr in range(0x500005A4, 0x500005A4 + 1, 4)],
        'CFAR': [addr for addr in range(0x500005A8, 0x500005E4 + 1, 4)],
        'RSSI': [addr for addr in range(0x4005C10C, 0x4005C10C + 1, 4)],
        'Motion': [addr for addr in range(0x4005C140, 0x4005C15C + 1, 4)],
        'Motion EABS': [addr for addr in range(0x4005C190, 0x4005C1AC + 1, 4)],
        'AGC_Ch1': [addr for addr in range(0x400D8060, 0x400D8060 + 1, 4)],
        'AGC_Ch2': [addr for addr in range(0x400D80A0, 0x400D80A0 + 1, 4)],
        'AGC_Ch3': [addr for addr in range(0x400F8060, 0x400F8060 + 1, 4)],

        'AI Sram': [0x20020C04, 0x20022404, 0x20023C04, 0x20025404, 0x20026C04, 0x20028404,
                    0x20029C04,
                    0x2002B404, 0x2002CC04, 0x2002E404, 0x2002FC04, 0x20031404, 0x20020C08,
                    0x20022408,
                    0x20023C08, 0x20025408, 0x20026C08, 0x20028408, 0x20029C08, 0x2002B408,
                    0x2002CC08,
                    0x2002E408, 0x2002FC08, 0x20031408],
                            }

    def __init__(self, actions=0b101, read_interrupt:int=0, clear_interrupt:int=0, rbank_ch_enable=0b111):
        super(MultiResult4168BReceiver, self).__init__()
        self._result_list = []
        self._result_dict = {'SoftmaxExponential': [],
                            'Axis': [],
                            'Gestures': [],
                            'SiameseGestures': [],
                            'SiameseExponential': [],
                            'IMax': [],
                            'CFAR': [],
                            'RSSI': [],
                            'Motion': [],
                            'Motion EABS': [],
                            'AGC Ch1': [],
                            'AGC Ch2': [],
                            'AGC Ch3': [],
                            'AI Sram':[],
                             }

        self._trigger = False
        self.read_interrupt = read_interrupt
        self.clear_interrupt = clear_interrupt
        self.rbank_ch_enable = rbank_ch_enable
        self.actions = actions
        self.RDI_enable = True
    def trigger(self,**kwargs):
        '''
        :param kwargs:

        read_interrupt = read interrupt\n
        clear_interrupt = clear interrupt\n
            interrupt types are 0: softmax, 1: cfar, 2: amplitude, 3: md, 4: tracking, 5: raw_data, 6: c1_done

        enable:
            2 - Enable to read registgers and RAW/RDI\n
            1 - Enable to read registgers\n
            0 - Disable\n

        RDI_enable: Switch RDI/Raw.

        :return:
        '''
        self.setConfig(**kwargs)
        total_res = []
        actions = int(self.actions)
        read_interrupt = int(self.read_interrupt)
        clear_interrupt = int(self.clear_interrupt)
        rbank_ch_enable = int(self.rbank_ch_enable)
        self._result_list=[]
        if (actions & 0b100):
            if read_interrupt == 0:
                self._result_list = list(self._res_addrs_dict.keys())
                # self._result_list = ['Axis']
            elif read_interrupt == 3:
                self._result_list = ['RSSI', 'Motion', 'Motion EABS']
            elif read_interrupt == 2:
                self._result_list = ['CFAR', 'RSSI', 'Motion', 'Motion EABS']
            elif read_interrupt == 1:
                self._result_list = ['CFAR', 'IMax', 'RSSI', 'Motion', 'Motion EABS']
            elif read_interrupt == 4:
                self._result_list = ['AXIS', 'CFAR', 'IMax', 'RSSI', 'Motion', 'Motion EABS']
            # instance paring machine
            for res_name in self._result_list:
                total_res = total_res + self._res_addrs_dict[res_name]

        self._ResultParser = ResultParsing(self._result_list)
        reg_addrs = np.asarray(total_res).astype('uint32')
        self.size = 1
        if (actions & 0b1):
            self.RDI_enable = kgl.ksoclib.readReg(0x50000504, 5, 5)
            if self.RDI_enable:
                self.size = 1620 + self.size
            else:
                chirp = Digi168BController.getChirpNumber()+1
                self.size = chirp*128 + self.size
        kgl.ksoclib.switchSoftMaxInterrupt(actions, read_interrupt, clear_interrupt, self.size*4, rbank_ch_enable, reg_addrs)
        self._trigger = True
        print('SwitchSoftMaxInterrupt success')
        time.sleep(0.5)
        super(MultiResult4168BReceiver, self).trigger()

    def getResults(self):
        '''

        Returns: result dictionary or None

        '''
        res = kgl.ksoclib.getSoftMaxInterruptRegValues()

        if res is None:
            return None

        self._result_dict = {}
        if (int(self.actions) & 0b1):
            data = res.pop(0)
            if self.RDI_enable:
                rdi_raw = self._ResultParser.parseRDI(data, 0, self.size*2)
                RDI_PHD = convertFeatureMap(rdi_raw)
                self._result_dict.setdefault('FeatureMap', RDI_PHD)
            else:
                raw_data = self._ResultParser.parseRawData(data, 0, self.size*2)
                # raw_data = np.split(raw_data, (2))
                self._result_dict.setdefault('RawData', raw_data)

        if (int(self.actions) & 0b10):
            data = res.pop(0)
            retention = np.zeros((3,128), dtype='int16')
            data = np.reshape(data,(int(len(data)/128), 128))
            for i in range(data.shape[0]):
                retention[i,:] = data[i,:]
            self._result_dict.setdefault('Retention', retention)

        if (int(self.actions) & 0b100):
            data = res.pop(0)
            start = 0
            result_dict ={}
            for res_name in self._result_list:
                result_dict.setdefault(res_name, data[start:start + len(self._res_addrs_dict[res_name])])
                start = start + len(self._res_addrs_dict[res_name])
            self._ResultParser.parsing(result_dict)
            self._result_dict.update(self._ResultParser.getParsedResults())
        return self._result_dict

    def stop(self):
        if self._trigger:
            kres = kgl.ksoclib.switchSoftMaxInterrupt(enable=0)
            self._trigger = False
            print('SwitchSoftMaxInterrupt stop')

class MultiResult4169CReceiver(Receiver):
    def __init__(self):
        '''
        Receive some hardware results
        (Gesture, Axis and Exponential).
        '''
        super(MultiResult4169CReceiver, self).__init__()
        self._result_list = []
        self.interrupt_list = []
        self.dec = None
        self.switch_mode = 2
        self.data_size = 4096
        from KKT_Module.KKTUtility.RFControl import RFController
        self.RFController = RFController()
        pass

    def setDec(self, dec):
        self.dec = dec

    def trigger(self, **kwargs):
        super(MultiResult4169CReceiver, self).trigger()
        # self.RFController.turnOnModulation(True)
        self._ResultParser = ResultParsing(self._result_list)
        enable = kwargs.get('enable')
        if enable is None:
            enable = 7
        dec = kwargs.get('BinaryArray')
        # bytes_array = 0
        # if dec is not None:
        #     bytes_array = dec.to_bytes(4, 'big')
        if dec is None:
            dec = 0
        chirps = kwargs.get('chirps')
        samples = kwargs.get('samples')
        if chirps is None:
            chirps = int(kgl.ksoclib.readReg(0x60000530, 7, 0)) + 1
        if samples is None:
            samples = int(kgl.ksoclib.readReg(0x60000530, 25, 16))
        self.data_size = chirps * samples
        # size = kwargs.get('raw_size')
        # if size is not None:
        #     self.data_size = size
        switch_mode = kwargs.get('switch_mode')
        if switch_mode is not None:
            self.switch_mode = switch_mode

        self.interrupt_list = self.__genFPGAAnswerDict(dec)
        kgl.ksoclib.switchDiagnosisInterrupt(enable, gemmini_res=dec, reg_addrs=[], data_size=self.data_size * 2)
        pass

    def getResults(self):
        '''

        :return: Gesture, Axis and Exponential.
        '''
        res = kgl.ksoclib.getDiagnosisInterruptRegValues()
        start = 0
        if res is None:
            return None
        raw = res[0]
        diagnosis = res[1]
        AGC = res[2]
        Motion = res[3]
        raw_data = self._ResultParser.parseRawData2(raw, start, self.data_size, self.switch_mode)
        diagnosis_dict = {}
        for i in range(len(diagnosis)):
            if self.interrupt_list[i] == 'SF_SOFTMAX':
                # combine 4 byte to float32, <f：little endian; >f：big endian
                assert len(bytearray(diagnosis[i])) % 4 == 0, 'The length of SF_SOFTMAX is wrong !'
                d = np.frombuffer(bytearray(diagnosis[i]), dtype='float32')
            elif self.interrupt_list[i] == 'TRACKING':
                # combine 2 byte to int16
                assert len(bytearray(diagnosis[i])) % 2 == 0, 'The length of TRACKING is wrong !'
                d = np.frombuffer(bytearray(diagnosis[i]), dtype='int16')
            else:
                d = np.asarray(bytearray(diagnosis[i]), dtype='int8')

            diagnosis_dict.setdefault(self.interrupt_list[i], d)
            print(d)
        return diagnosis_dict, raw_data, AGC, Motion

    def stop(self):
        kgl.ksoclib.switchDiagnosisInterrupt(0)
        pass

    def __genFPGAAnswerDict(self, binary: str):
        binarys = list(bin(binary)[2:].zfill(32))
        binarys.reverse()
        interrupt_list = []
        diagnosis = [
            'SCID_ITS_DIAG_MIN',  # 0
            'SCID_ITS_DIAG_ROWDATA_LOOPBACK',
            'SCID_ITS_DIAG_DFT_FAST_REAL',
            'SCID_ITS_DIAG_DFT_FAST_IMAG',
            'SCID_ITS_DIAG_DFT_CORDIC',
            'SCID_ITS_DIAG_DFT_SLOW_RESULT_REAL',  # 5
            'SCID_ITS_DIAG_DFT_SLOW_RESULT_IMAG',
            'SCID_ITS_DIAG_CONVD_1',
            'SCID_ITS_DIAG_CONVP_1',
            'SCID_ITS_DIAG_CONVD_2',
            'SCID_ITS_DIAG_CONVP_2',  # 10
            'SCID_ITS_DIAG_GLOBAL_AVERAGE',
            'SCID_ITS_DIAG_BATCH_NORMALIZATION',
            'SCID_ITS_DIAG_CONV_REV1',
            'SCID_ITS_DIAG_CONV_REV2',
            'SCID_ITS_DIAG_MGU_CONCAT_STATE',  # 15
            'SCID_ITS_DIAG_MGU_TILED_MATMUL_G',
            'SCID_ITS_DIAG_MGU_SIGMOID',
            'SCID_ITS_DIAG_MGU_SUB',
            'SCID_ITS_DIAG_MGU_MUL1',
            'SCID_ITS_DIAG_MGU_CONCAT_MUL1',  # 20
            'SCID_ITS_DIAG_MGU_TILED_MATMUL_C',
            'SCID_ITS_DIAG_MGU_TANH',
            'SCID_ITS_DIAG_MGU_MUL3',
            'SCID_ITS_DIAG_MGU_ADD',
            'SCID_ITS_DIAG_MGU_REV1',  # 25
            'SCID_ITS_DIAG_MGU_REV2',
            'SCID_ITS_DIAG_NEXT_MGU_STATE',
            'SCID_ITS_DIAG_SF_FC_LAST',
            'SCID_ITS_DIAG_SF_SOFTMAX',
            'SCID_ITS_DIAG_TRACKING'  # 30
        ]
        for i in range(len(binarys)):
            if binarys[i] == '1':
                interrupt_list.append(diagnosis[i].replace('SCID_ITS_DIAG_', ''))
        return interrupt_list

    def initDataBuffer(self, enable, interrupt_list):
        pass

class FeatureMapReceiver(Receiver):
    def __init__(self, chirps:int=32):
        '''
        Receive RDI PHD map from hardware.

        :param chirps: chirps number.
        '''
        super(FeatureMapReceiver, self).__init__()
        self._trigger = False
        self.__LastFrameCount = 0
        self.trigger_arg = ['chirps']
        self.chirps = chirps
        pass

    def trigger(self,**kwargs):
        super(FeatureMapReceiver, self).trigger(**kwargs)
        kgl.ksoclib.writeReg(1, 0x50000504, 5, 5, 0)
        time.sleep(0.3)
        if self.chirps <= 35:
            kgl.ksoclib.massdatabufStart_RDI(0, 0x0C)
        elif self.chirps <= 64:
            kgl.ksoclib.massdatabufStart_RDI(0, 0x10)
        else:
            kgl.ksoclib.massdatabufStart_RDI(0, 0x08)

        self._trigger = True
        print('switch RDI ')
        pass

    def getResults(self):
        '''
        :return: RDI, PHD shape 32*32 array.
        '''
        result = kgl.ksoclib.massdatabufGet_RDI()

        if result is None:
            return None

        framecount1 = result[0]
        framecount2 = result[1]
        raw_RDI = result[2]

        # print("(framecount1/framecount2) = (", framecount1, "/", framecount2, ")")
        if framecount1 != framecount2:
            print("framecount1 != framecount2 (", framecount1, "/", framecount2, ")")
        elif framecount1 == 0 and framecount2 ==0:
            pass
            # print("framcount1 = 0")
        elif framecount1 - 1 != self.__LastFrameCount and framecount1 != -1:
            print("shift ", framecount1 - self.__LastFrameCount - 1)
        self.__LastFrameCount = framecount1

        # # use it if received the raw RDI data
        # from KKT_Module.DataReceive.Parsing import convertBitArray
        # raw_RDI = convertBitArray(raw_RDI,32,12)

        return convertFeatureMap(raw_RDI)

    def stop(self):
        if self._trigger:
            kgl.ksoclib.massdatabufStop()
            print('Mass data buffer stopped')
            self._trigger = False
        pass

class RawDataReceiver(Receiver):
    def __init__(self, chirps:int=32):
        '''
        Receive Raw data and frame count from hardware.

        :param chirps: chirps number.
        '''
        super(RawDataReceiver, self).__init__()
        self._trigger = False
        self.__LastFrameCount = 0
        self.trigger_arg = ['chirps']
        # self._chirps = {'chirps': chirps}
        self.chirps = chirps
        pass

    def trigger(self, **kwargs):
        self.setConfig(**kwargs)
        # chirps = self.chirps
        # if chirps is None:
        #     chirps = 32
        self.__LastFrameCount = 0
        # self.chirps = chirps
        self._ADC_Mux = kgl.ksoclib.readReg(0x50000544, 3, 0)
        rdi_enable = kwargs.get('rdi_enable')
        if rdi_enable is None:
            kgl.ksoclib.writeReg(0, 0x50000504, 5, 5, 0)
        # time.sleep(0.3)
        if self.chirps < 32:
            kgl.ksoclib.massdatabufStart_RAW(0, 0, 16)
        elif self.chirps < 64:
            kgl.ksoclib.massdatabufStart_RAW(0, 0, 32)
        else:
            kgl.ksoclib.massdatabufStart_RAW(0, 0, 64)
        print('switch Raw ')
        self._trigger = True
        super(RawDataReceiver, self).trigger()
        pass

    def getResults(self):
        '''
        :return: CH1 Raw data , CH2 Raw data
        '''
        if not self._trigger:
            return None
        result = kgl.ksoclib.massdatabufGet()
        if result is None:
            return None
        framecount1 = result[0]
        framecount2 = result[2]
        if self._ADC_Mux in [2, 4, 5]:
            result_ch1 = result[3]
            result_ch2 = result[1]
        else:
            result_ch1 = result[1]
            result_ch2 = result[3]

        # print("(framecount1/framecount2) = (", framecount1, "/", framecount2, ")")
        if framecount1 != framecount2:
            print("framecount1 != framecount2 (", framecount1, "/", framecount2, ")")
        elif framecount1 == 0 and framecount2 ==0:
            pass
            # print("framcount1 = 0")
        elif framecount1 - 1 != self.__LastFrameCount and framecount1 != -1:
            print("shift ", framecount1 - self.__LastFrameCount - 1)
        self.__LastFrameCount = framecount1

        return result_ch1, result_ch2

    def stop(self):
        if self._trigger:
            kgl.ksoclib.massdatabufStop()
            print('Mass data buffer stopped')
            self._trigger = False
        pass

class HWResultOpenPSMReceiver(Receiver):
    '''
    Rename from AllResultReceiver.

    Get all Hardware results without trigger receiver.
    '''
    def __init__(self):
        super(HWResultOpenPSMReceiver, self).__init__()
        pass

    def trigger(self):
        super(HWResultOpenPSMReceiver, self).trigger()
        pass

    def getResults(self):
        return kgl.ksoclib.getAllResultsAsList()

    def stop(self):
        pass

class HWResultReceiver(Receiver):
    def __init__(self):
        '''
        Rename from GesturesReceiver.

        Read register and receive some hardware results.
        (Gesture, Axis and Exponential).
        '''
        super(HWResultReceiver, self).__init__()
        pass

    def trigger(self,**kwargs):
        super(HWResultReceiver, self).trigger(**kwargs)
        pass

    def getResults(self):
        '''

        :return: Gesture, Axis and Exponential.
        '''
        return kgl.ksoclib.getGestureResult()

    def stop(self):
        pass

def convertFeatureMap(rdi_raw , dual_mode = False):
    # ut.printArrayInfo(rdi_raw, "rdi_raw")

    shape_pack = rdi_raw.reshape([15,18,16])
    spec_pack = np.transpose(shape_pack, (1, 2, 0))
    RDI = np.zeros((33, 33, 2), dtype='uint32')
    spec_pack_up = spec_pack[0:9,:,:]
    spec_pack_down = spec_pack[9:,:,:]

    for i in range(15):
        idx = i
        row_start = 2 * idx
        row_end = row_start + 3
        # print(idx, row_start, row_end)

        RDI[row_start:row_end, 0:16:2, 0] = spec_pack_up[::3, ::2, idx]
        RDI[row_start:row_end, 0:16:2, 1] = spec_pack_up[::3, 1::2, idx]

        RDI[row_start:row_end, 1:17:2, 0] = spec_pack_up[1::3, ::2, idx]
        RDI[row_start:row_end, 1:17:2, 1] = spec_pack_up[1::3, 1::2, idx]

        RDI[row_start:row_end, 2:18:2, 0] = spec_pack_up[2::3, ::2, idx]
        RDI[row_start:row_end, 2:18:2, 1] = spec_pack_up[2::3, 1::2, idx]

        RDI[row_start:row_end, 16:32:2, 0] = spec_pack_down[::3, ::2, idx]
        RDI[row_start:row_end, 16:32:2, 1] = spec_pack_down[::3, 1::2, idx]

        RDI[row_start:row_end, 17:33:2, 0] = spec_pack_down[1::3, ::2, idx]
        RDI[row_start:row_end, 17:33:2, 1] = spec_pack_down[1::3, 1::2, idx]

        RDI[row_start:row_end, 18:34:2, 0] = spec_pack_down[2::3, ::2, idx]
        RDI[row_start:row_end, 18:34:2, 1] = spec_pack_down[2::3, 1::2, idx]

        # RDI_map = RDI[:, :, 0]
        # PHD_map = RDI[:, :, 1]

    return RDI[:32, :32, 0], RDI[:32, :32, 1]

if __name__ == '__main__':
    r_ini = ReceiverConfigs(r'C:\Users\eric.li\Desktop\Python\0_Standard_Ksoc_Tool\Config\Reciver_Configs.ini')
    kgl.setLib()
    kgl.ksoclib.connectDevice()
    receiver = FeatureMapReceiver()
    receiver.trigger(chirps=32)
    i=0
    while i < 100:
        res = receiver.getResults()
        if res is None:
            continue
        print(res)
        print(len(res[0]))
        i = i+1

    receiver.stop()

