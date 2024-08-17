
# https://stackoverflow.com/questions/50533812/what-is-the-best-way-to-define-constant-variables-python-
# http://note.drx.tw/2015/01/google-python-style-callname-rules-main.html
import os
import inspect
import pathlib

import clr  #clr是公共執行時環境，該模組是與c#互動的核心
import sys

# 匯入clr時這個模組最好也一起匯入，這樣可用使用AddReference()方法
clr.AddReference("System")
# clr.FindAssembly("System")

import System
from System import Array,UInt32, Int32, UInt16, Int16, String, UInt32, Int32
# from System import *
import numpy as np
from .LibLog import lib_logger as log



DLL_DIRS = ("KSOC_USB_Tools", 'KSOC_Libs')
MAIN_PATH = pathlib.Path(__file__).parent.parent
if not pathlib.Path.is_dir(MAIN_PATH):
    MAIN_PATH = pathlib.Path.cwd()
DLL_NAME = "KSOC_Lib"

for dir in DLL_DIRS:
    abs_path = os.path.normpath(os.path.join(MAIN_PATH, dir))
    log.info(abs_path)
    sys.path.append(abs_path)

def printEnvironment():
    '''print .net runtime version and current environment'''
    # ======== print .net runtime version =============
    print(System.Environment.Version)
    # print("my num is 0x{0:02x}{1:02x}".format(res[0],res[1]))
    # print('Hello, {:s}. You have {:d} messages.'.format('Rex', 999))

    # ========= print current environment =============
    print('---------------------')
    for p in sys.path:
        print(p)
    print('---------------------')

def printCLRInfo():
    '''列印程式集，如果動態庫載入成功，程式集裡就會含有動態庫的程式集'''
    lt = clr.ListAssemblies(False)
    for i in range(lt.Length):
        print('%d = %s' % (i,lt[i]))

def addReferenceLib(dll_name):
    ksoc_lib = clr.AddReference(dll_name)
    log.info("clr.AddReference = {}".format(ksoc_lib))
    ksoc_lib = clr.FindAssembly(dll_name)
    log.info("clr.FindAssembly = {}".format(ksoc_lib))
    log.info(ksoc_lib)
    return ksoc_lib

KSOC_Lib = addReferenceLib(DLL_NAME)

from KSOC_Lib import KSOC_Integration, Kit_Communication_Type, KKT_USB_Device_Index, MassDataProc_Type


class KKTLibException(Exception):
    def __init__(self, function_name, kres, *args, **kwargs):
        msg = "[ {} ] Failure, kres = {}".format(function_name, kres)
        super(KKTLibException, self).__init__(msg, *args, **kwargs)
    pass


class KSOCIntegration(KSOC_Integration):
    def __init__(self):
        super(KSOCIntegration, self).__init__()

    def getLibVersion(self)->str:
        '''
        Get C# Lib version.

        :return: [Customer ID (00000 ~ 65535)]-[model ID (001 ~ 255)]-v[major version].[patches]
        '''
        return self.GetLibVersionInfor()

    def getDeviceInfo(self, comport_type=2)->str:
        '''
        Get ComPort informations.

        0: 'Unknow' ,
        1: 'Cypress' ,
        2: 'VComPort' ,
        3: 'I2C'

        :param comport_type: Comport type number.
        :return: ComPort informations
        '''
        return self.GetDeviceInfor(comport_type)

    def getSN(self):
        '''
        Get series number.
        '''
        kres, SN = self.GetSN(None)
        if kres != 0:
            raise KKTLibException(function_name=inspect.stack()[0][3], kres=kres)
        return SN

    def outputDebugview(self, msg="", isWriteLog=False):
        '''
        Output message to debug view.

        :param msg: Message to ouput on debug view.
        :param isWriteLog: Save to log file.
        :return:
        '''
        self.OutputMsgToDebugView(msg, isWriteLog)

    def switchLogMode(self, Isprint=False, DebugView=False, OutputToFile=False):
        self.SwitchLogMode(Isprint, DebugView, OutputToFile)

    def _connectDevice(self, device):
        kres = self.ConnectUsbDevice(device, KKT_USB_Device_Index.KKT_USB_Device_0)
        if kres != 0:
            raise KKTLibException(inspect.stack()[0][3], kres)

    def closeDevice(self):
        kres = self.CloseUsbDevice()

    def _readHWRegister(self, addr, num_of_reg=1):
        kres, val = self.Device_Read_Reg(addr, num_of_reg, None)
        if kres != 0:
            raise KKTLibException(inspect.stack()[0][3], kres)
        return np.asarray(list(val), dtype='uint32')

    def _writeHWRegister(self, addr, val_ary):
        new_val_ary = Array[UInt32](val_ary)
        kres = self.Device_Write_Reg(addr, new_val_ary)
        if kres != 0:
            raise KKTLibException(inspect.stack()[0][3], kres)

    def _switchSPIChannel(self, mode):
        assert mode in [0, 1]
        kres = self.SwitchSPIChannel(mode)
        if kres != 0:
            raise KKTLibException(inspect.stack()[0][3], kres)
        return kres

    def _readRFICRegister(self, addr):
        kres, val = self.RFIC_Cmd_Read(UInt16(addr), UInt16(0))
        if kres != 0:
            raise KKTLibException(inspect.stack()[0][3], kres)
        return val

    def _writeRFICRegister(self, addr, val):
        kres = self.RFIC_Cmd_Write(UInt16(addr), UInt16(val))
        if kres != 0:
            raise KKTLibException(inspect.stack()[0][3], kres)

    def getAllResults(self):
        kres, ges, axes_ary, softmax_ary, sia_ges, sia_softmax_ary, motion_rssi, motion_rssi_ary = self.RegGet_AllResult(
            UInt32(0), None, None, UInt32(0), None, UInt32(0), None)
        if kres == 0:
            return ges, axes_ary, softmax_ary, sia_ges, sia_softmax_ary, motion_rssi, motion_rssi_ary

    def getAutoPowerStateMachine(self):
        kres, PowerSateOrAck = self.GetAutoPowerStateMachine(Int32(0))
        if kres != 0:
            raise KKTLibException(inspect.stack()[0][3], kres)
        return PowerSateOrAck

    def setAutoPowerStateMachine(self, PowerState: int):
        kres = self.SetAutoPowerStateMachine(PowerState)
        if kres != 0:
            raise KKTLibException(inspect.stack()[0][3], kres)
        return kres

    def receiveAllData_list(self):
        '''
        Get HW results using FW cmd "0xA0".

        :return:
        '''
        kres, data = self.ReceiveAllDataAsList(None)
        if kres != 0:
            return None
        data = list(data)
        if data[0] == -1:
            return None
        if data[2] is not None:
            data[2] = np.asarray(list(data[2])).astype('int16')
        if data[3] is not None:
            data[3] = np.asarray(list(data[3])).astype('uint16')
        return data

    def getGestureResult(self):
        '''
        Read registers after softmax interrupt to get HW results and clear softmax interrupt.

        :return: ( gesture number, axis(x, y, z), probability )
        '''
        kres, ges, axes_ary, softmax_ary = self.RegGet_GESTURE(UInt32(0), None, None)
        if kres == 0:
            return ges, np.asarray(list(axes_ary), dtype='int16'), np.asarray(list(softmax_ary), dtype='uint16')

    def setRFICScript(self, filename, compare=False, ignoreAddrList=None):
        kres = self.SetScript_Rfic(filename, compare, ignoreAddrList)
        if kres != 0:
            raise KKTLibException(inspect.stack()[0][3], kres)

    def setAIWeightScript(self,filename, compare=True):
        kres = self.SetScript_AIWeight(filename, compare)
        if kres != 0:
            raise KKTLibException(inspect.stack()[0][3], kres)

    def startMassDataBuf_RAW(self, buf_size, delay_ms, chirps=32):
        if chirps == 16:
            mass_proc_type = MassDataProc_Type.MDP_Normal_16
        elif chirps == 32:
            mass_proc_type = MassDataProc_Type.MDP_Normal_32
        elif chirps == 64:
            mass_proc_type = MassDataProc_Type.MDP_Normal_64
        kres = self.MassDataBuffer_Start_Setting(mass_proc_type, UInt32(buf_size), UInt32(delay_ms))
        if kres != 0:
            raise KKTLibException(inspect.stack()[0][3], kres)

    def startMassDataBuf_RDI(self, buf_size, delay_ms):
        kres = self.MassDataBuffer_Start_Setting(MassDataProc_Type.MDP_Normal_RDI, UInt32(buf_size),
                                                      UInt32(delay_ms))
        if kres != 0:
            raise KKTLibException(inspect.stack()[0][3], kres)

    def stopMassDataBuf(self):
        kres = self.MassDataBuffer_Stop()
        if kres != 0:
            raise KKTLibException(inspect.stack()[0][3], kres)

    def getMassDataBuf(self):
        kres, ch1_frameCount, ch1, ch2_frameCount, ch2 = self.MassDataBuffer_Get(UInt16(0), None, UInt16(0), None)
        if kres == 0:
            return ch2_frameCount, np.asarray(list(ch1), dtype='int16'), \
                   ch1_frameCount, np.asarray(list(ch2), dtype='int16')

    def getMassDataBuf_RDI(self):
        kres, ch1_frameCount, ch2_frameCount, rdi_raw = self.MassDataBuffer_GetRDIRaw(UInt16(0), UInt16(0), None)
        if kres == 0:
            return (ch1_frameCount, ch2_frameCount, np.asarray(list(rdi_raw), dtype='uint16'))

    def readEFuseCmd(self, addr):
        kres, outreg_val = self.EFuse_Cmd_Read(addr, None)
        if kres != 0:
            raise KKTLibException(inspect.stack()[0][3], kres)
        return outreg_val[0]

    def getFWVersion(self):
        kres, version = self.GetFWVersion(None)
        if kres != 0:
            raise KKTLibException(inspect.stack()[0][3], kres)
        return version

    def resetDevice(self):
        '''
        Reset device.

        :return: kres
        '''
        kres = self.Reset_Device()
        if kres != 0:
            raise KKTLibException(inspect.stack()[0][3], kres)

    def writeRawDataToSRAM(self, channel, rawdata:bytearray):
        '''
        Write raw data to SRAM.

        :param channel: address of RX.
        :param rawdata: array of rawdata in dtype='int16'.
        :return: kres
        '''
        kres = self.Write_Raw_to_SRAM(channel, rawdata)
        if kres != 0:
            raise KKTLibException(inspect.stack()[0][3], kres)

    def readRangeRegisters(self, first_addr: int, last_addr: int):
        '''
        Give range of registers and get array of values.

        :param first_addr: start address
        :param last_addr: end address
        :return: Array of values or None
        '''
        kres, val_arry = self.Read_Register_Range(first_addr, last_addr, None)
        if kres == 0:
            return np.asarray(list(val_arry)).astype('int32')

    def switchSoftmaxInterrupt(self, enable, read_interrupt, clear_interrupt, size, ch_of_RBank, reg_addrs):
        '''
        Enable/Disable to get address's values when interrupt go high.

        :param enable: Start or stop getting data.
        :param read_interrupt: Interrupt that waiting for.
        :param clear_interrupt: Interrupt to clean.
        :param ch_of_RBank: Bit to enable the channel of reference bank .
        :param reg_addrs: Array of address.
        :return: kres
        '''
        kres = self.SwitchSoftMaxInterruptAsserted(enable, read_interrupt, clear_interrupt, size, ch_of_RBank, reg_addrs)
        if kres != 0:
            raise KKTLibException(inspect.stack()[0][3], kres)

    def switchDiagnosisInterrupt_payload(self, payload: bytearray):
        '''
        Enable/Disable to get address's values when interrupt go high.

        :param enable: Start or stop getting data.
        :param read_interrupt: Interrupt that waiting for.
        :param clear_interrupt: Interrupt 20to clean.
        :param num_of_reg: Number of register.
        :param reg_addrs: Array of address.
        :return: kres
        '''
        kres = self.SwitchDiagnosisInterruptAsserted(payload)
        if kres != 0:
            raise Exception("[{}] Failure, kres = {}".format(inspect.stack()[0][3], kres))

    def switchDiagnosisInterrupt(self, enable, gemmini_res, data_size, reg_addrs):
        '''
        Enable/Disable to get address's values when interrupt go high.

        :param enable: Start or stop getting data.
        :param read_interrupt: Interrupt that waiting for.
        :param clear_interrupt: Interrupt 20to clean.
        :param num_of_reg: Number of register.
        :param reg_addrs: Array of address.
        :return: kres
        '''
        kres = self.SwitchDiagnosisInterruptAsserted(enable, gemmini_res, data_size, reg_addrs)
        if kres != 0:
            raise KKTLibException(inspect.stack()[0][3], kres)

    def getSoftmaxInterruptAsserted(self):
        '''
        Get array of register's values when interrupt go high.

        :return: None or array of register's values.
        '''
        kres, reg_vals = self.GetSoftMaxInterruptAssertedRegValues(None)
        if kres != 0:
            return None
        return list(reg_vals)

    def getDiagnosisInterruptAsserted(self):
        '''
        Get array of register's values when interrupt go high.

        :return: None or array of register's values.
        '''
        kres, raw, diagnosis, AGC, Motion = self.GetDiagnosisInterruptAssertedRegValues(None, None, None, None)
        if kres != 0:
            return None
        if raw is not None:
            raw = np.asarray(list(raw), dtype='int16')

        if diagnosis is not None:
            diagnosis = list(diagnosis)

        if AGC is not None:
            AGC = bytearray(AGC)
            AGC = np.asarray(AGC, dtype='int8')

        if Motion is not None:
            Motion = np.asarray(list(Motion), dtype='int16')

        return raw, diagnosis, AGC, Motion

    def updateRFICSetting(self, path):
        kres = self.UpdateRFICSetting(path)
        if kres != 0:
            raise KKTLibException(inspect.stack()[0][3], kres)

    def runRFICInit(self):
        kres = self.RunRFICInit()
        if kres != 0:
            raise KKTLibException(inspect.stack()[0][3], kres)

    def switchAutoPowerStateMachine(self, IsStop: bool):
        kres = self.SwitchAutoPowerStateMachine(IsStop)
        if kres != 0:
            raise KKTLibException(inspect.stack()[0][3], kres)

    def getChipID(self):
        kres, chip_id = self.GetChipID(None)
        if kres != 0:
            raise KKTLibException(inspect.stack()[0][3], kres)
        return chip_id

    def getOldFWVersion(self):
        kres, old_ver = self.GetOldVersion(None)
        if kres != 0:
            raise KKTLibException(inspect.stack()[0][3], kres)
        return old_ver

    def setAIWeight_bin(self, filepath):
        kres = self.Set_AIWeight_Bin(filepath)
        if kres != 0:
            raise KKTLibException(inspect.stack()[0][3], kres)

    def setUserTable_bin(self, filepath):
        kres = self.Set_UserTable_Bin(filepath)
        if kres != 0:
            raise KKTLibException(inspect.stack()[0][3], kres)

    def controlGemmini(self, mode):
        kres = self.Control_Gemmini(mode)
        if kres != 0:
            raise KKTLibException(inspect.stack()[0][3], kres)

    def initRFIC(self):
        kres = self.InitRFIC()
        if kres != 0:
            raise KKTLibException(inspect.stack()[0][3], kres)
        return kres

if __name__ == '__main__':
    printEnvironment()
    printCLRInfo()
    k = KSOCIntegration()
    print(k.getLibVersionInfo())
    print(k.getDeviceInfo())
    print(k._connectDevice(2))
    # print(k.getSN())
    print("Done")




