import sys
from .LibWrapper import KSOCIntegration
import numpy as np
from .LibLog import lib_logger as log
from pathlib import Path

class KsocLib(KSOCIntegration):
    def __init__(self):
        super().__init__()
        log.info("__init__...")
        self.lib_ver = self.getLibVersion()
        log.info('KKT lib was setuped')

    def __del__(self):
        self.__cleanup()

    def __cleanup(self):
        log.info("Running cleanup...")
        self.closeDevice()
        log.info("CloseUsbDevice...")

    def connectCySpi(self):
        return self.connectCySpi()

    def closeDevice(self):
        super().closeDevice()

    def getRFSICEnableStatus(self):
        mode0_addrs = (0x0189, 0x018A, 0x018B)
        mode0_compare_vals = []
        for addr in mode0_addrs:
            mode0_compare_vals.append(self.readRFICRegister(addr))
        l = list(bin(mode0_compare_vals[1])[2:].zfill(16))
        l.reverse()
        return int(l[6])

    def connectDevice(self, device_num=-1)->str:
        '''
        if device_num is default (-1),
        this function will try to connect all type of device and return connected device name.

        device_num :

        0: 'Unknow'
        1: 'Cypress'
        2: 'VComPort'
        3: 'I2C'

        '''

        device_dict = {0: 'Unknow',
                       1: 'Cypress',
                       2: 'VComPort',
                       3: 'I2C'}

        device = device_dict.get(device_num)
        if device is not None :
            super()._connectDevice(device)
            return device_dict[device]
        for device in tuple(device_dict.keys()):
            try:
                super()._connectDevice(device)
                return device_dict[device]
            except:
                continue
        return device_dict[0]

    def readHWRegister(self, addr, num_of_reg=1):
        log.debug('Read HW register addr=0x{:08X}'.format(addr))
        return super()._readHWRegister(addr, num_of_reg)

    def writeHWRegister(self, addr, val_ary):
        log.debug('Write HW register addr=0x{:08X}, write=0x{:08X}'.format(addr, val_ary[0]))
        return super()._writeHWRegister(addr, val_ary)

    def readRFICRegister(self, addr):
        log.debug("Read RF register addr=0x{:04X}".format(addr))
        return super()._readRFICRegister(addr)

    def writeRFICRegister(self, addr=None, val=None, RB_check=False):
        log.debug('Write RF register addr=0x{:04X}, write=0x{:04X}'.format(addr, val))
        super()._writeRFICRegister(addr, val)
        if RB_check:
            res = self.readRFICRegister(addr)
            log.info('Write RF register(0x{:04X}) read back compare match :{}, write={}, read={}'.format(addr, res == val, val, res))

    def readHWRegister_bit(self, addr, bitH, bitL):
        log.debug("Read HW register addr=0x{:08X} [{}:{}]".format(addr, bitH, bitL))
        assert 31 >= bitH >= bitL >= 0
        bitLen = (bitH - bitL) + 1
        data = self.readHWRegister(addr, 1)
        mask = ((1 << bitLen) - 1) << bitL
        return (data[0] & mask) >> bitL

    def writeHWRegister_bit(self, decvalue, addr, bitH, bitL, RBCheck=False):
        log.debug("Write HW register addr=0x{:08X} [{}:{}] to {}".format(addr, bitH, bitL, decvalue))
        bitLen = bitH - bitL + 1
        if decvalue < 0:
            decvalue = decvalue + 2 ** (bitLen)

        r_data = self.readHWRegister(addr, 1)

        temp = r_data[0] >> (bitH + 1)
        temp = temp << bitLen
        temp = temp | decvalue
        temp = temp << bitL
        temp = temp | (r_data[0] & ~(~(1 << bitL) + 1))
        w_data = [temp]

        log.debug("Write HW register val from 0x{:08X} to 0x{:08X}".format(r_data[0], temp))
        self.writeHWRegister(addr, w_data)

        if RBCheck == True:
            CmpData = self.readHWRegister_bit(addr, bitH, bitL)
            log.info("Write HW register(0x{:08X} [{}:{}]) read back compare match :{} write={}, read={}"
                     .format(addr, bitH, bitL, CmpData == decvalue, decvalue, CmpData))

    def setRFICScript(self, filename:str, compare=False , ignoreAddrList=None):
        suffix =  Path(filename).suffix
        if suffix == '.txt':
            super().setRFICScript(filename, compare , ignoreAddrList)
        elif suffix == '.bin':
            self.updateRFICSetting(filename)
            self.runRFICInit()
        else:
            log.warning('[setScriptRfic] file suffix not exist')

    def setAIWeightScript(self, filename, compare=True):
        super().setAIWeightScript(filename, compare)

    def getLibVersion(self):
        self.lib_ver = super().getLibVersion()
        log.info('lib version : {}'.format(self.lib_ver))
        return self.lib_ver

    def writeRawDataToSRAM(self, channel , rawdata):
        rawdata_arr = np.asarray(rawdata, dtype='int8')
        rawdata_arr2 = bytearray(rawdata_arr)
        super().writeRawDataToSRAM(channel , rawdata_arr2)

    def readRangeRegisters(self, first_addr, last_addr):
        addr_list = []
        for addr in range(first_addr, last_addr+1, 4):
            addr_list.append(addr)
        addr_arry = np.asarray(addr_list)
        val_arry = super().readRangeRegisters()(first_addr, last_addr)
        if len(addr_arry) == len(val_arry):
            # assert len(addr_arry) == len(val_arry), 'Number of address not match with results'
            return val_arry, addr_arry
        return None

    def switchSoftMaxInterrupt(self, enable, read_interupt=0, clear_interupt=0, size=4096, ch_of_RBank=0, reg_addrs=np.zeros(0,dtype='uint32')):
        self.switchSoftmaxInterrupt(enable, read_interupt, clear_interupt, size, ch_of_RBank, reg_addrs)
        log.info('SwitchSoftMaxInterrupt success')

    def getSoftMaxInterruptRegValues(self):
        res = self.getSoftmaxInterruptAsserted()
        if res is not None:
            for i in range(len(res)):
                res[i] = np.asarray(list(res[i]))
        return res

    def switchDiagnosisInterrupt(self, enable, gemmini_res=0, data_size=0, reg_addrs=np.zeros(0,dtype='uint32')):# Old function name
        assert (enable < 128), 'Argument enable is not valid !'
        gemmini_res = 0
        data_size = 0
        reg_addrs = np.asarray([],dtype='uint32')
        gemmini_res = int(gemmini_res).to_bytes(4, 'big')
        super().switchDiagnosisInterrupt(enable, gemmini_res, data_size, reg_addrs)
        print('SwitchSoftMaxInterrupt success')

    def getDiagnosisInterruptRegValues(self):
        res = self.getDiagnosisInterrupt()
        return res

    def getAllResults(self):
        return super().getAllResults()

    def getModulationOnStatus(self):
        result = self.readRFICRegister(0x0029)
        return (result == 0x40FE)

    def switchModulationOn(self, turn_on=True):
        if turn_on:
            value = 0x40FE
        else:
            value = 0x407E
        self.writeRFICRegister(0x0029, value)

    def setAIWeightBinFile(self, filepath):
        self.setAIWeightBinFile(filepath)

    def pullUpRawDataWriteInterrupt(self):
        self.controlGemmini(1)

    def resetMGUState(self):
        self.controlGemmini(2)

# ========== old version ===================
class KsocLib(KsocLib): # for old function name
    def closeCyDevice(self):
        self.closeDevice()

    def regRead(self, addr, num_of_reg=1):
        '''
            # For old version
        '''
        return self.readHWRegister(addr, num_of_reg)

    def regWrite(self, addr, val_ary):
        self.writeHWRegister(addr, val_ary)

    def SwitchSPIChannel(self, mode=None):
        return self.switchSPIChannel(mode)

    def rficRegRead(self, addr):  # Old function name
        '''
        # For old version
        '''
        return self.readRFICRegister(addr)

    def rficRegWrite(self, addr=None, val=None, Print=True, Compare=False):
        '''
        # For old version
        '''
        self.writeRFICRegister(addr, val, Compare)

    def readReg(self, addr, bitH, bitL):
        '''
        # For old version
        '''
        return self.readHWRegister_bit(addr, bitH, bitL)

    def writeReg(self, decvalue, addr, bitH, bitL, RBCheck=True, IsPrint=False, Compare=True):
        '''
        # For old version
        '''
        self.writeHWRegister_bit(decvalue, addr, bitH, bitL, RBCheck)

    def setScriptRfic(self, filename: str, compare=False, ignoreAddrList=None):
        self.setRFICScript(filename, compare, ignoreAddrList)

    def setScriptAIWeight(self, filename, compare=True):
        self.setAIWeightScript(filename, compare)

    def massdatabufStart_RAW(self, buf_size, delay_ms, chirps):  # Old function name
        self.startMassDataBuf_RAW(buf_size, delay_ms, chirps)

    def massdatabufStart_RDI(self, buf_size, delay_ms):  # Old function name
        self.startMassDataBuf_RDI(buf_size, delay_ms)

    def massdatabufStop(self):  # Old function name
        self.stopMassDataBuf()

    def massdatabufGet(self):  # Old function name
        return self.getMassDataBuf()

    def massdatabufGet_RDI(self):  # Old function name
        return self.getMassDataBuf_RDI()

    def writeRawDatatoSRAM(self, channel, rawdata):
        self.writeRawDataToSRAM(channel, rawdata)

    def getAllResultsAsList(self):
        return self.receiveAllData_list()

if __name__ == '__main__':
    print("ksoc lib...start")
    Lib = KsocLib()
    print(Lib.connectDevice())
    Lib.resetDevice()
    # print(hex(Lib.regRead(0x50000580)[0]))
    # Lib.switchSoftMaxInterrupt(1, 0, 0, 4096, 1, [0x50000580])
    # Lib.switchSoftMaxInterrupt(0)
    Lib.closeDevice()
    print("ksoc lib...")
    sys.exit()

    