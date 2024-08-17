import os
import re
from datetime import datetime

class ProcessListSymbol:
    RegSymbol = "Register"
    CommentSymbol = "Remark"
    RFFileSymbol = "RFFile"
    AIWeightPathSymbol = "AIWeightPath"
    AIWeightFilesSymbol = "AIWeightFiles"

    @classmethod
    def getSymbolString(cls, symbol):
        return {
            cls.RegSymbol: 'reg_write',
            cls.CommentSymbol: '//',
            # cls.WeightFileSymbol: '// WeightFile',
            cls.RFFileSymbol: '// RFFile',
            cls.AIWeightPathSymbol: '// AIWeightPath',
            cls.AIWeightFilesSymbol: '// AIWeightFiles',
        }.get(symbol, None)
pls = ProcessListSymbol()

class ProcessListGenerator:
    pls = ProcessListSymbol()
    _ProcList = []
    def __init__(self, ProcList=[]):
        self._ProcList = ProcList
        pass

    def genProcessList(self, sheetParam):
        global mux_flag
        self._ProcList.clear()

        self._ProcList.append([pls.CommentSymbol, ""])
        self._ProcList.append([pls.CommentSymbol, "Created Date : " + datetime.now().strftime(r'%Y/%m/%d %H:%M:%S')])
        self._ProcList.append([pls.CommentSymbol, "Config File : " + os.path.basename(sheetParam['file_name'])])
        self._ProcList.append([pls.CommentSymbol, ""])

        self._ProcList.append([pls.CommentSymbol, "Clear_AI_Enable"])
        self._ProcList.append([pls.RegSymbol, 0x400608F8, 0x00000000])

        self._ProcList.append([pls.CommentSymbol, "SIC_Disable"])
        self._ProcList.append([pls.RegSymbol, 0x40060900, 0x00000000])
        self._ProcList.append([pls.RegSymbol, 0x400601AC, 0x00000000])

        self._ProcList.append([pls.RegSymbol, 0x400B0084, 0x00000402])
        self._ProcList.append([pls.RegSymbol, 0x400B00A4, 0x00000402])
        self._ProcList.append([pls.RegSymbol, 0x40090084, 0x00000402])

        self._ProcList.append([pls.CommentSymbol, "Dynamic_AIC_Operation"])
        self._ProcList.append([pls.RegSymbol, 0x400B00E4, 0x00000030])
        self._ProcList.append([pls.RegSymbol, 0x400900E4, 0x00000030])
        self._ProcList.append([pls.RegSymbol, 0x4005C0E4, 0x00000004])

        self._ProcList.append([pls.CommentSymbol, "AI_FFT_Tracking_Reset"])
        dsp_unit_num = 0
        self._getReg_DSPRx625k_AICctrl_ctrl0([0, 1, 0, 0, 0, 0, 0, 0, 0], dsp_unit_num)
        self._getReg_DSPRx625k_AICctrl_ctrl1([0, 1, 0, 0, 0, 0, 0, 0, 0], dsp_unit_num)
        dsp_unit_num = 1
        self._getReg_DSPRx625k_AICctrl_ctrl0([0, 1, 0, 0, 0, 0, 0, 0, 0], dsp_unit_num)
        self._getReg_DSPRx625k_AICctrl_ctrl1([0, 1, 0, 0, 0, 0, 0, 0, 0], dsp_unit_num)

        self._getRegSysReset([1, 1, 0, 0, 1, 0, 0, 0])

        self._ProcList.append([pls.CommentSymbol, "Clear AI_FFT_Tracking_Reset"])
        self._getRegSysReset([0, 0, 0, 0, 0, 0, 0, 0])

        self._getRegRFIC_SPI_Master_Init()

        self._ProcList.append([pls.CommentSymbol, "Pre-RFIC-Script Setting"])
        rfscriptfile = os.path.join(sheetParam['workbook']['$RFIC_S2P']['FilePath'],
                                    sheetParam['workbook']['$RFIC_S2P']['FileName'])
        self._ProcList.append([pls.RFFileSymbol, rfscriptfile])
        self._ProcList.append([pls.CommentSymbol, "RFIC_Script Write from Excel Param."])

        self._ProcList.append([pls.CommentSymbol, "Pre-AI_WeightData Setting"])
        self._getRegSysReset([1, 1, 0, 0, 1, 0, 0, 0])
        self._getRegAISYSCTL([1, 1, 1, 1, 1, 1, 1, 1, 0, 0])

        self._ProcList.append([pls.CommentSymbol, "AI-WeightData-Script"])
        aiweightdatafolder = sheetParam['workbook']['$AI_WeightData']['FilePath']
        aiweightdatafiles = sheetParam['workbook']['$AI_WeightData']['FileName']
        self._ProcList.append([pls.AIWeightPathSymbol, aiweightdatafolder])
        self._ProcList.append([pls.AIWeightFilesSymbol, aiweightdatafiles])

        self._ProcList.append([pls.CommentSymbol, "select AI_WeightData Excel Param."])

        self._ProcList.append([pls.CommentSymbol, "Post-AI_WeightData Setting"])
        self._getRegSysReset([0, 0, 0, 0, 0, 0, 0, 0])
        self._getRegAISYSCTL([1, 1, 1, 1, 1, 1, 1, 1, 0, 0])

        self._ProcList.append([pls.CommentSymbol, "Init AI/FFT/SPI_GES/Track_3D Clock"])
        self._getRegAISYSCTL([1, 1, 1, 1, 1, 1, 1, 1, 0, 0])

        self._ProcList.append([pls.CommentSymbol, "RFIC S2P Set Process"])
        for reg in sheetParam['workbook']['$RFIC_S2P']['Registers']:
            self._ProcList.append([pls.RegSymbol, reg[1], reg[2]])

        self._ProcList.append([pls.CommentSymbol, "Adc_Mux Parameters"])
        for reg in sheetParam['workbook']['$Adc_MUX']['Registers']:
            self._ProcList.append([pls.RegSymbol, reg[1], reg[2]])

        self._ProcList.append([pls.CommentSymbol, "Tracking Parameters"])
        for reg in sheetParam['workbook']['$Tracking']['Registers']:
            self._ProcList.append([pls.RegSymbol, reg[1], reg[2]])

        self._ProcList.append([pls.CommentSymbol, "AIACC_MEM Parameters"])
        for reg in sheetParam['workbook']['$AIACC_MEM']['Registers']:
            self._ProcList.append([pls.RegSymbol, reg[1], reg[2]])

        self._ProcList.append([pls.CommentSymbol, "AIACC_Layer Parameters"])
        for reg in sheetParam['workbook']['$AIACC_Layer']['Registers']:
            self._ProcList.append([pls.RegSymbol, reg[1], reg[2]])

        self._ProcList.append([pls.CommentSymbol, "AIACC_PARAM Parameters"])
        for reg in sheetParam['workbook']['$AIACC_PARAM']['Registers']:
            self._ProcList.append([pls.RegSymbol, reg[1], reg[2]])

        self._ProcList.append([pls.CommentSymbol, "AIACC_Siamese Parameters"])
        for reg in sheetParam['workbook']['$AIACC_Siamese']['Registers']:
            self._ProcList.append([pls.RegSymbol, reg[1], reg[2]])

        # DPS UNIT 0
        self._ProcList.append([pls.CommentSymbol, "DSPRx20M_Unit_0 Parameters"])
        for reg in sheetParam['workbook']['$DSPRx20M_Unit_0']['Registers']:
            self._ProcList.append([pls.RegSymbol, reg[1], reg[2]])

        self._ProcList.append([pls.CommentSymbol, "DSPRx625K_Unit_0 Parameters"])
        for reg in sheetParam['workbook']['$DSPRx625K_Unit_0']['Registers']:
            self._ProcList.append([pls.RegSymbol, reg[1], reg[2]])

        self._ProcList.append([pls.CommentSymbol, "DSP Control and Sync: DSP_UNIT_0"])
        dsp_unit_num = 0
        self._getReg_DSPRx625k_RFCctrl_ctrl2([1, 1, 0], dsp_unit_num)
        self._getReg_DSPRx20M_RDIGen0_ctrl0([1, 0, 0, 0], dsp_unit_num)  # ch0 start RDI trig
        self._getReg_DSPRx20M_RDIGen1_ctrl0([1, 0, 0, 0], dsp_unit_num)  # ch1 start RDI trig
        self._getReg_DSPRx20M_RDIGen0_ctrl0([0, 0, 1, 0], dsp_unit_num)  # ch0 DIPowerSaveModeTrigger
        self._getReg_DSPRx20M_RDIGen1_ctrl0([0, 0, 1, 0], dsp_unit_num)  # ch1 DIPowerSaveModeTrigger
        self._getReg_DSPRx625k_AICctrl_ctrl0([0, 0, 1, 0, 0, 0, 1, 0, 0], dsp_unit_num)  # ch0 AICPowerSaveModTrigger
        self._getReg_DSPRx625k_AICctrl_ctrl1([0, 0, 1, 0, 0, 0, 1, 0, 0], dsp_unit_num)  # ch1 AICPowerSaveModTrigger
        self._getReg_DSPRx20M_FX3InfCtrl_ctrl0([1, 1], dsp_unit_num)  # RDICh0En + RDICh1En
        self._getReg_DSPRx20M_AIInfCtrl_ctrl0([1, 1], dsp_unit_num)  # RDICh0En + RDICh1En
        TestNumOfFrm = 0
        self._getReg_DSPRx625K_RFCtrl_ctrl3([TestNumOfFrm], dsp_unit_num)  # TestNumOfFrm
        self._getReg_DSPRx625K_RFCtrl_ctrl4([0x2000, 0], dsp_unit_num)  # init RF Ctrl
        self._getReg_DSPRx625K_RFCtrl_ctrl0([0, 1, 0, 0], dsp_unit_num)  # startExtRFTrig

        self._getReg_DSPRx625k_AICctrl_ctrl0([0, 0, 0, 0, 0, 0, 0, 0, 1], dsp_unit_num)  # ch0 waitRegSettingDoneTrigger
        self._getReg_DSPRx625k_AICctrl_ctrl1([0, 0, 0, 0, 0, 0, 0, 0, 1], dsp_unit_num)  # ch1 waitRegSettingDoneTrigger
        self._getReg_DSPRx20M_WinFuncCtrl0_ctrl0([1], dsp_unit_num)  # ch0 waitRegSettingDoneTrigger
        self._getReg_DSPRx20M_WinFuncCtrl1_ctrl0([1], dsp_unit_num)  # ch1 waitRegSettingDoneTrigger
        self._getReg_DSPRx625K_RFCtrl_ctrl0([0, 0, 0, 1], dsp_unit_num)  # regSettingTrig
        self._getReg_DSPRx625k_AICctrl_ctrl0([1, 0, 0, 0, 0, 0, 0, 0, 0], dsp_unit_num)  # ch0 waitRegSettingDoneTrigger
        self._getReg_DSPRx625k_AICctrl_ctrl1([1, 0, 0, 0, 0, 0, 0, 0, 0], dsp_unit_num)  # ch1 waitRegSettingDoneTrigger

        # DPS UNIT 1
        self._ProcList.append([pls.CommentSymbol, "DSPRx20M_Unit_1 Parameters"])
        for reg in sheetParam['workbook']['$DSPRx20M_Unit_1']['Registers']:
            self._ProcList.append([pls.RegSymbol, reg[1], reg[2]])

        self._ProcList.append([pls.CommentSymbol, "DSPRx625K_Unit_1 Parameters"])
        for reg in sheetParam['workbook']['$DSPRx625K_Unit_1']['Registers']:
            self._ProcList.append([pls.RegSymbol, reg[1], reg[2]])

        self._ProcList.append([pls.CommentSymbol, "DSP Control and Sync: DSP_UNIT_1"])
        dsp_unit_num = 1
        self._getReg_DSPRx625k_RFCctrl_ctrl2([1, 1, 0], dsp_unit_num)
        self._getReg_DSPRx20M_RDIGen0_ctrl0([1, 0, 0, 0], dsp_unit_num)  # ch0 start RDI trig
        self._getReg_DSPRx20M_RDIGen1_ctrl0([1, 0, 0, 0], dsp_unit_num)  # ch1 start RDI trig
        self._getReg_DSPRx20M_RDIGen0_ctrl0([0, 0, 1, 0], dsp_unit_num)  # ch0 DIPowerSaveModeTrigger
        self._getReg_DSPRx20M_RDIGen1_ctrl0([0, 0, 1, 0], dsp_unit_num)  # ch1 DIPowerSaveModeTrigger
        self._getReg_DSPRx625k_AICctrl_ctrl0([0, 0, 1, 0, 0, 0, 1, 0, 0], dsp_unit_num)  # ch0 AICPowerSaveModTrigger
        self._getReg_DSPRx625k_AICctrl_ctrl1([0, 0, 1, 0, 0, 0, 1, 0, 0], dsp_unit_num)  # ch1 AICPowerSaveModTrigger
        self._getReg_DSPRx20M_FX3InfCtrl_ctrl0([1, 1], dsp_unit_num)  # RDICh0En + RDICh1En
        self._getReg_DSPRx20M_AIInfCtrl_ctrl0([1, 1], dsp_unit_num)  # RDICh0En + RDICh1En
        TestNumOfFrm = 0
        self._getReg_DSPRx625K_RFCtrl_ctrl3([TestNumOfFrm], dsp_unit_num)  # TestNumOfFrm
        self._getReg_DSPRx625K_RFCtrl_ctrl4([0x2000, 0], dsp_unit_num)  # init RF Ctrl
        self._getReg_DSPRx625K_RFCtrl_ctrl0([0, 1, 0, 0], dsp_unit_num)  # startExtRFTrig

        self._getReg_DSPRx625k_AICctrl_ctrl0([0, 0, 0, 0, 0, 0, 0, 0, 1], dsp_unit_num)  # ch0 waitRegSettingDoneTrigger
        self._getReg_DSPRx625k_AICctrl_ctrl1([0, 0, 0, 0, 0, 0, 0, 0, 1], dsp_unit_num)  # ch1 waitRegSettingDoneTrigger
        self._getReg_DSPRx20M_WinFuncCtrl0_ctrl0([1], dsp_unit_num)  # ch0 waitRegSettingDoneTrigger
        self._getReg_DSPRx20M_WinFuncCtrl1_ctrl0([1], dsp_unit_num)  # ch1 waitRegSettingDoneTrigger
        self._getReg_DSPRx625K_RFCtrl_ctrl0([0, 0, 0, 1], dsp_unit_num)  # regSettingTrig
        self._getReg_DSPRx625k_AICctrl_ctrl0([1, 0, 0, 0, 0, 0, 0, 0, 0], dsp_unit_num)  # ch0 waitRegSettingDoneTrigger
        self._getReg_DSPRx625k_AICctrl_ctrl1([1, 0, 0, 0, 0, 0, 0, 0, 0], dsp_unit_num)  # ch1 waitRegSettingDoneTrigger

        # DSP_Motion
        self._ProcList.append([pls.CommentSymbol, "DSP_Motion Parameters"])
        for reg in sheetParam['workbook']['$DSP_Motion']['Registers']:
            self._ProcList.append([pls.RegSymbol, reg[1], reg[2]])
        self._ProcList.append([pls.CommentSymbol, "DSP_Motion Control"])
        self._getReg_DSP_Motion_ctrl0([0x100])  #
        self._getReg_DSP_Motion_ctrl1([4])  #
        self._getReg_DSP_Motion_ctrl0([1])  #

        return self._ProcList

    @classmethod
    def saveProcListToFile(cls, filepath, proclist=None):
        if proclist is None:
            assert cls._ProcList != [], 'Empty Process list !'
            proclist = cls._ProcList

        with open(filepath, 'w') as out_file:
            for plist in proclist:
                pstr = None
                if plist[0] == pls.RegSymbol:
                    pstr = pls.getSymbolString(pls.RegSymbol) + " ( 0x{:08X}, 0x{:08X});".format(plist[1], plist[2])
                elif plist[0] == pls.CommentSymbol:
                    pstr = pls.getSymbolString(pls.CommentSymbol) + ' ' + plist[1]
                # elif plist[0] == pls.WeightFileSymbol:
                #     pstr = pls.getSymbolString(pls.WeightFileSymbol) + ' : ' + plist[1]
                elif plist[0] == pls.RFFileSymbol:
                    pstr = pls.getSymbolString(pls.RFFileSymbol) + ' : ' + plist[1]
                elif plist[0] == pls.AIWeightPathSymbol:
                    pstr = pls.getSymbolString(pls.AIWeightPathSymbol) + ' : ' + plist[1]
                elif plist[0] == pls.AIWeightFilesSymbol:
                    pstr = pls.getSymbolString(pls.AIWeightFilesSymbol)+ ' : '  + ' '.join(str(x) for x in plist[1])
                    # pstr = pls.getSymbolString(pls.AIWeightFilesSymbol) + ' ' + ' '.join(plist[1])
                if pstr != None:
                    # out_file.write(pstr + os.linesep)
                    out_file.write(pstr + '\n')

    @classmethod
    def readProcListFromFile(cls, filename):
        read_procList =[]
        regex = re.compile(r'0x[0-9A-Fa-f]+')
        with open(filename) as in_file:
            for line in in_file:
                if line.find(pls.getSymbolString(pls.RegSymbol)) >= 0:
                    val = regex.findall(line)
                    if len(val) >= 2:
                        read_procList.append([pls.RegSymbol, int(val[0], 16), int(val[1], 16)])
                elif line.find(pls.getSymbolString(pls.CommentSymbol)) >= 0:
                    if line.find(pls.getSymbolString(pls.RFFileSymbol)) >= 0:
                        val = line.split(':')
                        read_procList.append([pls.RFFileSymbol, val[1].strip()])
                    elif line.find(pls.getSymbolString(pls.AIWeightPathSymbol)) >= 0:
                        val = line.split(':')
                        read_procList.append([pls.AIWeightPathSymbol, val[1].strip()])
                    elif line.find(pls.getSymbolString(pls.AIWeightFilesSymbol)) >= 0:
                        val = line.split(':')
                        files = val[1].strip().split(' ')
                        read_procList.append([pls.AIWeightFilesSymbol, files])
                    else:
                        val = line.replace(pls.getSymbolString(pls.CommentSymbol), "")
                        read_procList.append([pls.CommentSymbol, val.strip()])
        cls._ProcList = read_procList
        return read_procList

    @classmethod
    def setProcListVal(cls, add: int, val: int, procList=None, symbol=pls.RegSymbol):
        '''

        Args:
            procList: process list of address and value
            symbol: register symbol
            add: register address(hex)
            val: register value(hex)

        Returns: None

        '''
        if procList is None:
            assert cls._ProcList != [], 'Empty process list!'

        for plist in procList:
            if symbol == pls.RegSymbol and plist[0] == pls.RegSymbol:
                if plist[1] == add:
                    plist[2] = val
            elif symbol == pls.CommentSymbol and plist[0] == pls.CommentSymbol:
                pass
            elif symbol == pls.RFFileSymbol and plist[0] == pls.RFFileSymbol:
                pass
            elif symbol == pls.AIWeightPathSymbol and plist[0] == pls.AIWeightPathSymbol:
                pass
            elif symbol == pls.AIWeightFilesSymbol and plist[0] == pls.AIWeightFilesSymbol:
                pass

    @classmethod
    def getProcListVal(cls, add: int = None, field: list = None, procList=None, symbol=pls.RegSymbol):
        '''

        Args:
            procList: process list of address and value
            symbol: register symbol
            add: register address(hex)
            field: address's bit size (list)

        Returns: values(list) or files path(str)

        '''
        if procList is None:
            assert cls._ProcList != [], 'Empty process list!'

        for plist in procList:
            if symbol == pls.RegSymbol and plist[0] == pls.RegSymbol:
                if plist[1] == add:
                    reg = plist[2]
                    val = []
                    for f in field:
                        mask = 2 ** f - 1
                        val.append(reg & mask)
                        reg = reg >> f
                    return val

            elif symbol == pls.CommentSymbol and plist[0] == pls.CommentSymbol:
                pass
            elif symbol == pls.RFFileSymbol and plist[0] == pls.RFFileSymbol:
                return plist[1]
            elif symbol == pls.AIWeightPathSymbol and plist[0] == pls.AIWeightPathSymbol:
                return plist[1]
            elif symbol == pls.AIWeightFilesSymbol and plist[0] == pls.AIWeightFilesSymbol:
                return plist[1]

    def _getRegSysReset(self, val):
        bitsMap = [
            #  size, pos
            [1, 18],  # FFT_Rst
            [1, 19],  # TRACK_Rst
            [1, 21],  # SPIGES_Rst
            [1, 22],  # MOTION_Rst
            [1, 27],  # AIACC_Rst
            [1, 28],  # SPI_FLASH_Rst
            [1, 29],  # SPI_RFIC_Rst
            [1, 30],  # ANA_Rst
        ]
        if len(val) != len(bitsMap):
            raise Exception("[ERROR] getSysReset: array range error")

        addr = getRegAddr('IPRSTC2_SetReset', None)

        reg_adr = addr[0] + addr[1]

        self._ProcList.append([pls.RegSymbol, reg_adr, bit2Val(bitsMap, val)])

    def _getReg_DSPRx20M_RDIGen0_ctrl0(self, val, dsp_unit):
        bitsMap = [
            #  size, pos
            [0, 0],  # startRDI_trig
            [0, 1],  # stopRDI_trig
            [0, 2],  # startPowerSave_trig
            [0, 3],  # stopPowerSave_trig
        ]
        if len(val) != len(bitsMap):
            raise Exception("[ERROR] getReg_DSPRx20M_RDIGen0_ctrl0: array range error")

        addr = 0
        if dsp_unit > 0:
            addr = getRegAddr('DSPRx20M_RDIGen0_ctrl0', 'DSPRx20M_Unit_1')
        else:
            addr = getRegAddr('DSPRx20M_RDIGen0_ctrl0', 'DSPRx20M_Unit_0')

        reg_adr = addr[0] + addr[1]

        self._ProcList.append([pls.RegSymbol, reg_adr, bit2Val(bitsMap, val)])

    def _getReg_DSPRx20M_RDIGen1_ctrl0(self, val, dsp_unit):
        bitsMap = [
            #  size, pos
            [0, 0],  # startRDI_trig
            [0, 1],  # stopRDI_trig
            [0, 2],  # startPowerSave_trig
            [0, 3],  # stopPowerSave_trig
        ]
        if len(val) != len(bitsMap):
            raise Exception("[ERROR] getReg_DSPRx20M_RDIGen1_ctrl0: array range error")
        addr = 0
        if dsp_unit > 0:
            addr = getRegAddr('DSPRx20M_RDIGen1_ctrl0', 'DSPRx20M_Unit_1')
        else:
            addr = getRegAddr('DSPRx20M_RDIGen1_ctrl0', 'DSPRx20M_Unit_0')
        reg_adr = addr[0] + addr[1]
        self._ProcList.append([pls.RegSymbol, reg_adr, bit2Val(bitsMap, val)])

    def _getReg_DSPRx625k_AICctrl_ctrl0(self, val, dsp_unit):
        bitsMap = [
            #  size, pos
            [1, 0],  # opTrigger
            [1, 1],  # stopTrigger
            [1, 2],  # startPowerSave_trig
            [1, 3],  # stopPowerSave_trig
            [1, 4],  # resetWeightTrigger
            [1, 5],  # clearBufferTrigger
            [1, 6],  # enableWnCntUpTrig
            [1, 7],  # disableWnCntUpTrig
            [1, 8],  # waitRegSettingDone
        ]
        if len(val) != len(bitsMap):
            raise Exception("[ERROR] getReg_DSPRx625k_AICctrl_ctrl0: array range error")
        addr = 0
        if dsp_unit > 0:
            addr = getRegAddr('DSPRx625k_AICctrl_ctrl0', 'DSPRx625K_Unit_1')
        else:
            addr = getRegAddr('DSPRx625k_AICctrl_ctrl0', 'DSPRx625K_Unit_0')
        reg_adr = addr[0] + addr[1]
        self._ProcList.append([pls.RegSymbol, reg_adr, bit2Val(bitsMap, val)])

    def _getReg_DSPRx625k_AICctrl_ctrl1(self, val, dsp_unit):
        bitsMap = [
            #  size, pos
            [1, 0],  # opTrigger
            [1, 1],  # stopTrigger
            [1, 2],  # startPowerSave_trig
            [1, 3],  # stopPowerSave_trig
            [1, 4],  # resetWeightTrigger
            [1, 5],  # clearBufferTrigger
            [1, 6],  # enableWnCntUpTrig
            [1, 7],  # disableWnCntUpTrig
            [1, 8],  # waitRegSettingDone
        ]
        if len(val) != len(bitsMap):
            raise Exception("[ERROR] getReg_DSPRx625k_AICctrl_ctrl0: array range error")
        addr = 0
        if dsp_unit > 0:
            addr = getRegAddr('DSPRx625k_AICctrl_ctrl1', 'DSPRx625K_Unit_1')
        else:
            addr = getRegAddr('DSPRx625k_AICctrl_ctrl1', 'DSPRx625K_Unit_0')
        reg_adr = addr[0] + addr[1]
        self._ProcList.append([pls.RegSymbol, reg_adr, bit2Val(bitsMap, val)])

    def _getReg_DSPRx20M_FX3InfCtrl_ctrl0(self, val, dsp_unit):
        bitsMap = [
            #  size, pos
            [0, 0],  # RDICh0En
            [0, 1],  # RDICh1En
        ]
        if len(val) != len(bitsMap):
            raise Exception("[ERROR] getReg_DSPRx20M_FX3InfCtrl_ctrl0: array range error")
        addr = 0
        if dsp_unit > 0:
            addr = getRegAddr('DSPRx20M_RDIGen_ctrl0', 'DSPRx20M_Unit_1')
        else:
            addr = getRegAddr('DSPRx20M_RDIGen_ctrl0', 'DSPRx20M_Unit_0')
        reg_adr = addr[0] + addr[1]
        self._ProcList.append([pls.RegSymbol, reg_adr, bit2Val(bitsMap, val)])

    def _getReg_DSPRx20M_AIInfCtrl_ctrl0(self, val, dsp_unit):
        bitsMap = [
            #  size, pos
            [0, 0],  # RDICh0En
            [0, 1],  # RDICh1En
        ]
        if len(val) != len(bitsMap):
            raise Exception("[ERROR] getReg_DSPRx20M_AIInfCtrl_ctrl0: array range error")
        addr = 0
        if dsp_unit > 0:
            addr = getRegAddr('DSPRx20M_AIInfCtrl_ctrl0', 'DSPRx20M_Unit_1')
        else:
            addr = getRegAddr('DSPRx20M_AIInfCtrl_ctrl0', 'DSPRx20M_Unit_0')
        reg_adr = addr[0] + addr[1]
        self._ProcList.append([pls.RegSymbol, reg_adr, bit2Val(bitsMap, val)])

    def _getReg_DSPRx625K_RFCtrl_ctrl0(self, val, dsp_unit):
        bitsMap = [
            #  size, pos
            [0, 0],  # oneFrmTrig
            [0, 1],  # extRFStartTrig
            [0, 2],  # extRFStopTrig
            [0, 3],  # regSettingTrig
        ]
        if len(val) != len(bitsMap):
            raise Exception("[ERROR] getReg_DSPRx625K_RFCtrl_ctrl0: array range error")
        addr = 0
        if dsp_unit > 0:
            addr = getRegAddr('DSPRx625k_RFCtrl_ctrl0', 'DSPRx625K_Unit_1')
        else:
            addr = getRegAddr('DSPRx625k_RFCtrl_ctrl0', 'DSPRx625K_Unit_0')
        reg_adr = addr[0] + addr[1]
        self._ProcList.append([pls.RegSymbol, reg_adr, bit2Val(bitsMap, val)])

    def _getReg_DSPRx625k_RFCctrl_ctrl2(self, val, dsp_unit):
        bitsMap = [
            #  size, pos
            [0, 0],  # ch0En
            [0, 1],  # ch1En
            [0, 2],  # extRFSel
        ]
        if len(val) != len(bitsMap):
            raise Exception("[ERROR] getReg_DSPRx625k_RFCctrl_ctrl2: array range error")
        addr = 0
        if dsp_unit > 0:
            addr = getRegAddr('DSPRx625k_RFCtrl_ctrl2', 'DSPRx625K_Unit_1')
        else:
            addr = getRegAddr('DSPRx625k_RFCtrl_ctrl2', 'DSPRx625K_Unit_0')
        reg_adr = addr[0] + addr[1]
        self._ProcList.append([pls.RegSymbol, reg_adr, bit2Val(bitsMap, val)])

    def _getReg_DSPRx625K_RFCtrl_ctrl3(self, val, dsp_unit):
        bitsMap = [
            #  size, pos
            [0, 0],  # numOfFrm
        ]
        if len(val) != len(bitsMap):
            raise Exception("[ERROR] getReg_DSPRx625K_RFCtrl_ctrl3: array range error")
        addr = 0
        if dsp_unit > 0:
            addr = getRegAddr('DSPRx625k_RFCtrl_ctrl3', 'DSPRx625K_Unit_1')
        else:
            addr = getRegAddr('DSPRx625k_RFCtrl_ctrl3', 'DSPRx625K_Unit_0')
        reg_adr = addr[0] + addr[1]
        self._ProcList.append([pls.RegSymbol, reg_adr, bit2Val(bitsMap, val)])

    def _getReg_DSPRx625K_RFCtrl_ctrl4(self, val, dsp_unit):
        bitsMap = [
            #  size, pos
            [0, 0],  # frmStartPeriod
            [0, 20],  # frmSampleOffset
        ]
        if len(val) != len(bitsMap):
            raise Exception("[ERROR] getReg_DSPRx625K_RFCtrl_ctrl4: array range error")
        addr = 0
        if dsp_unit > 0:
            addr = getRegAddr('DSPRx625k_RFCtrl_ctrl4', 'DSPRx625K_Unit_1')
        else:
            addr = getRegAddr('DSPRx625k_RFCtrl_ctrl4', 'DSPRx625K_Unit_0')
        reg_adr = addr[0] + addr[1]
        self._ProcList.append([pls.RegSymbol, reg_adr, bit2Val(bitsMap, val)])

    def _getReg_DSPRx20M_WinFuncCtrl0_ctrl0(self, val, dsp_unit):
        bitsMap = [
            #  size, pos
            [0, 0],  # waitRegSettingDone
        ]
        if len(val) != len(bitsMap):
            raise Exception("[ERROR] getReg_DSPRx20M_WinFuncCtrl0_ctrl0: array range error")
        addr = 0
        if dsp_unit > 0:
            addr = getRegAddr('DSPRx625k_WinFuncCtrl0_ctrl0', 'DSPRx625K_Unit_1')
        else:
            addr = getRegAddr('DSPRx625k_WinFuncCtrl0_ctrl0', 'DSPRx625K_Unit_0')
        reg_adr = addr[0] + addr[1]
        self._ProcList.append([pls.RegSymbol, reg_adr, bit2Val(bitsMap, val)])

    def _getReg_DSPRx20M_WinFuncCtrl1_ctrl0(self, val, dsp_unit):
        bitsMap = [
            #  size, pos
            [0, 0],  # waitRegSettingDone
        ]
        if len(val) != len(bitsMap):
            raise Exception("[ERROR] getReg_DSPRx20M_WinFuncCtrl1_ctrl0: array range error")
        addr = 0
        if dsp_unit > 0:
            addr = getRegAddr('DSPRx625k_WinFuncCtrl1_ctrl0', 'DSPRx625K_Unit_1')
        else:
            addr = getRegAddr('DSPRx625k_WinFuncCtrl1_ctrl0', 'DSPRx625K_Unit_0')
        reg_adr = addr[0] + addr[1]
        self._ProcList.append([pls.RegSymbol, reg_adr, bit2Val(bitsMap, val)])

    def _getReg_DSP_Motion_ctrl0(self, val):
        bitsMap = [
            #  size, pos
            [0, 0],  #
        ]
        if len(val) != len(bitsMap):
            raise Exception("[ERROR] getReg_DSP_Motion_ctrl0: array range error")
        addr = getRegAddr('DSP_Motion_ctrl0', None)
        reg_adr = addr[0] + addr[1]
        self._ProcList.append([pls.RegSymbol, reg_adr, bit2Val(bitsMap, val)])

    def _getReg_DSP_Motion_ctrl1(self, val):
        bitsMap = [
            #  size, pos
            [0, 0],  #
        ]
        if len(val) != len(bitsMap):
            raise Exception("[ERROR] getReg_DSP_Motion_ctrl1: array range error")
        addr = getRegAddr('DSP_Motion_ctrl1', None)
        reg_adr = addr[0] + addr[1]
        self._ProcList.append([pls.RegSymbol, reg_adr, bit2Val(bitsMap, val)])

    def _getRegRFIC_SPI_Master_Init(self):
        regList = []
        bitsMap = [
            #  size, pos
            [0, 0],  # DIVIDER
            [0, 16],  # DIVIDER 2
        ]
        addr = getRegAddr('RFIC_SPI_Regs_Div', None)
        reg_adr = addr[0] + addr[1]
        val = bit2Val(bitsMap, [79, 0])
        self._ProcList.append([pls.RegSymbol, reg_adr, val])

        bitsMap = [
            #  size, pos
            [0, 0],  # SSR
            [0, 2],  # SS_LVL
            [0, 3],  # ASS
            [0, 4],  # SS_LTRIG
            [0, 5],  # LTRIG_FLAG
        ]
        addr = getRegAddr('RFIC_SPI_Regs_SSR', None)
        reg_adr = addr[0] + addr[1]
        val = bit2Val(bitsMap, [1, 0, 1, 0, 0])
        self._ProcList.append([pls.RegSymbol, reg_adr, val])

        bitsMap = [
            #  size, pos
            [0, 0],  # GO_BUSY
            [0, 1],  # RX_NEG
            [0, 2],  # TX_NEG
            [0, 3],  # TX_BIT_LEN
            [0, 8],  # TX_NUM
            [0, 10],  # LSB
            [0, 11],  # CLKP
            [0, 12],  # SLEEP
            [0, 16],  # IF
            [0, 17],  # IE
            [0, 18],  # SLAVE
            [0, 19],  # BYTE_SLEEP
            [0, 20],  # BYTE_ENDIAN
            [0, 21],  # FIFO
            [0, 22],  # TWOB
            [0, 23],  # VARCLK_EN
            [0, 24],  # RX_EMPTY
            [0, 25],  # RX_FULL
            [0, 26],  # TX_EMPTY
            [0, 27],  # TX_FULL
            [0, 28],  # %DMA_ASS_BURST
        ]
        bsize = 0  # 0 -> 32bit for 15bit address
        # bsize = 24;     #for 7bit address
        addr = getRegAddr('RFIC_SPI_Regs_CNTRL', None)
        reg_adr = addr[0] + addr[1]
        val = bit2Val(bitsMap, [0, 1, 1, bsize, 0, 0, 0, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        self._ProcList.append([pls.RegSymbol, reg_adr, val])

    def _getRegAISYSCTL(self, val):
        if len(val) != 10:
            raise Exception("[ERROR] getRegAISYSCTL: array range error")

        bitsMap = [
            #  size, pos
            [0, 9],  # TRACK_EN
            [0, 17],  # AIACC_EN
            [0, 18],  # FFT_EN
            [0, 19],  # SPIGES_EN
            [0, 22],  # MOTION_EN
            [0, 28],  # SPI_FLASH_EN
            [0, 29],  # SPI_RFIC_EN
            [0, 30],  # ANA_EN
        ]
        addr = getRegAddr('APBCLK', None)
        reg_adr = addr[0] + addr[1]
        reg_val = bit2Val(bitsMap, val[:-2])
        reg_val = 0xffffffff & reg_val
        reg_val = 0xffffffff
        self._ProcList.append([pls.RegSymbol, reg_adr, reg_val])

        bitsMap = [
            #  size, pos
            [0, 0],  # AISRAM_REQ
            [0, 31],  # Force SRAM 625K
        ]
        # SysCtlPin(9)     0;     % AISRAM_REQ
        # SysCtlPin(10)     31];	% Force SRAM 625K
        addr = getRegAddr('AIMTXEN', None)
        reg_adr = addr[0] + addr[1]
        self._ProcList.append([pls.RegSymbol, reg_adr, bit2Val(bitsMap, val[-2:])])

def getBaseAddr(addr):
    return{
        'TRK_BA'            :0x50000500,
        'DSPRx20M_Unit_0'   :0x400D0000,
        'DSPRx625K_Unit_0'  :0x400B0000,
        'DSPRx20M_Unit_1'   :0x400F0000,
        'DSPRx625K_Unit_1'  :0x40090000,
        'DSP_Motion'        :0x4005C000,
        'AIACC'             :0x40060000,
        'GCR_BA'            :0x50000000,
        'CLK_BA'            :0x50000200,
        'SPI_RFIC_BA'       :0x400A0000,
        'AI_WEIGHT_BA'      :0x20020000,
    }.get(addr,None)

def getRegAddr(reg, dsp_unit):
    return{
        'IPRSTC2_SetReset'              :[getBaseAddr('GCR_BA'), 0x0C],
        'RFIC_SPI_Regs_CNTRL'           :[getBaseAddr('SPI_RFIC_BA'), 0x00],  #RFIC_SPI_Regs_CNTRL
        'RFIC_SPI_Regs_Div'             :[getBaseAddr('SPI_RFIC_BA'), 0x04],  #RFIC_SPI_Regs_DIVIDER
        'RFIC_SPI_Regs_SSR'             :[getBaseAddr('SPI_RFIC_BA'), 0x08],  #RFIC_SPI_Regs_DIVIDER
        'APBCLK'                        :[getBaseAddr('CLK_BA'), 0x08],  #APBCLK
        'AIMTXEN'                       :[getBaseAddr('TRK_BA'), 0x00],  #AIMTXEN

        'DSPRx625k_WinFuncCtrl0_ctrl0'  :[getBaseAddr(dsp_unit), 0xC4],
        'DSPRx625k_WinFuncCtrl1_ctrl0'  :[getBaseAddr(dsp_unit), 0xD4],
        'DSPRx625k_AICctrl_ctrl0'       :[getBaseAddr(dsp_unit), 0x84],
        'DSPRx625k_AICctrl_ctrl1'       :[getBaseAddr(dsp_unit), 0xA4],
        'DSPRx625k_RFCtrl_ctrl0'        :[getBaseAddr(dsp_unit), 0x40],
        'DSPRx625k_RFCtrl_ctrl1'        :[getBaseAddr(dsp_unit), 0x44],
        'DSPRx625k_RFCtrl_ctrl2'        :[getBaseAddr(dsp_unit), 0x48],
        'DSPRx625k_RFCtrl_ctrl3'        :[getBaseAddr(dsp_unit), 0x4C],
        'DSPRx625k_RFCtrl_ctrl4'        :[getBaseAddr(dsp_unit), 0x50],

        'DSPRx20M_RDIGen0_ctrl0'        :[getBaseAddr(dsp_unit), 0x2000],
        'DSPRx20M_RDIGen1_ctrl0'        :[getBaseAddr(dsp_unit), 0x6000],
        'DSPRx20M_AIInfCtrl_ctrl0'      :[getBaseAddr(dsp_unit), 0x8008],
        'DSPRx20M_RDIGen_ctrl0'         :[getBaseAddr(dsp_unit), 0x8010],

        'DSP_Motion_ctrl0'              :[getBaseAddr('DSP_Motion'), 0x84],
        'DSP_Motion_ctrl1'              :[getBaseAddr('DSP_Motion'), 0x40],
    }.get(reg, None)

def bit2Val(bitsMap, val):
    if len(val) != len(bitsMap):
        raise Exception("[ERROR] bit2Val: array range error")
    new_val = 0
    for i in range(len(val)):
        if bitsMap[i][0] == 0:
            mask = 0xffffffff
        else:
            mask = 2 ** bitsMap[i][0] - 1
        v = val[i] & mask
        v <<= bitsMap[i][1]
        new_val |= v
    return new_val

def bitFieldToVal(fieldVal, field):
    if len(fieldVal) != len(field):
        raise Exception("[ERROR] bitFieldToVal: array range error")
    new_val = 0
    shift = 0
    for i, f in enumerate(field):
        mask = 2 ** f - 1
        v = fieldVal[i] & mask
        v <<= shift
        new_val |= v
        shift = shift + f
    return new_val


if __name__ == '__main__':
    pls = ProcessListSymbol()
    print(pls.getSymbolString(pls.RegSymbol))