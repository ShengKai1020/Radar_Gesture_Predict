# -*- coding: utf-8 -*-
"""
Created on Wed Dec 23 16:02:16 2020

@author: sam.cheng
"""

import time
import numpy as np
from KKT_Module.ksoc_global import  kgl
from KKT_Module.Configs import SettingConfigs
class SICFunction:
    bufB_startIdx = 125
    delayOfStart = -21 - 3
    syncOffset = 0
    chirp_log_num = 5  # 2^n
    chirp_period = 1  # 0:64  1:128
    changePolarity = 0

    # for feedback gain DAC gain is 32x and  feedback loop atten -16->-12dB
    W_starting = 32
    W_end = 32

    # -----------------MISC-------------------------
    symbolPerFrm = 1  # 0:16   1:32   2:64  3: user
    symbolPerFrmuser = 33
    cycelsPerFrm = 31250
    noUpdateBufB = 0

    auto_cyclesPerFrm = 1
    SICInfo_sel = 1  # 0=AIC_start, 1=cyclesPerFrm
    outputShiftNum = 0
    @classmethod
    def _setSICParameters(cls, name, addr, param, bitH ,bitL, RBcheck, debug):
        read_param = kgl.ksoclib.readReg(addr, bitH, bitL)
        if not (param - read_param == 0):
            print("Overwrite {} in reg={} bit=[{}:{}] from '{}' to '{}'".format(name, hex(addr), bitH, bitL,read_param, param))
        kResult = kgl.ksoclib.writeReg(param, addr, bitH, bitL, RBcheck)
        if debug:
            print("[{}] write addr: {}, value: {}, result: {}".format(name, addr, param, kResult))
    @classmethod
    def setSICInfo_sel(clr, param, RBCheck=True, debug=False):
        print("--> [Func] setSICInfo_sel")
        addrs = [0x400B0098,0x40090098,0x400B00B8,0x400900B8,]
        for addr in addrs:
            clr._setSICParameters('setSICInfo_sel', addr, param, 28, 28, RBCheck, debug)
    @classmethod
    def setauto_cyclesPerFrm(clr, param, RBCheck=True, debug=False):
        print("--> [Func] setauto_cyclesPerFrm")
        addrs = [0x400B0098, 0x40090098, 0x400B00B8, 0x400900B8, ]
        for addr in addrs:
            clr._setSICParameters('setauto_cyclesPerFrm', addr, param, 27, 27, RBCheck, debug)
    @classmethod
    def setchangePolarity(clr, param, RBCheck=True, debug=False):
        print("--> [Func] setchangePolarity")
        addrs = [0x400B0098, 0x40090098, 0x400B00B8, 0x400900B8,]
        for addr in addrs:
            clr._setSICParameters('setchangePolarity', addr, param, 26, 26, RBCheck, debug)
    @classmethod
    def setnoUpdateBufB(clr, param, RBCheck=True, debug=False):
        print("--> [Func] setnoUpdateBufB")
        addrs = [0x400B0098, 0x40090098, 0x400B00B8, 0x400900B8, ]
        for addr in addrs:
            clr._setSICParameters('setnoUpdateBufB', addr, param, 25, 25, RBCheck, debug)
    @classmethod
    def setcyclePerFrm(clr, param, RBCheck=True, debug=False):
        print("--> [Func] setcyclePerFrm")
        addrs = [0x400B0098, 0x40090098, 0x400B00B8, 0x400900B8, ]
        for addr in addrs:
            clr._setSICParameters('setcyclePerFrm', addr, param, 24, 7, RBCheck, debug)
    @classmethod
    def setbufB_startIdx(clr, param, RBCheck=True, debug=False):
        print("--> [Func] setbufB_startIdx")
        addrs = [0x400B0098, 0x40090098, 0x400B00B8, 0x400900B8, ]
        for addr in addrs:
            clr._setSICParameters('setbufB_startIdx', addr, param, 6, 0, RBCheck, debug)
    @classmethod
    def setsymbolPerFrm(clr, param, RBCheck=True, debug=False):
        print("--> [Func] setsymbolPerFrm")
        addrs = [0x400B0088, 0x40090088, 0x400B00A8, 0x400900A8, ]
        for addr in addrs:
            clr._setSICParameters('setsymbolPerFrm', addr, param, 17, 16, RBCheck, debug)
    @classmethod
    def setsymbolPerFrmuser(clr, param, RBCheck=True, debug=False):
        print("--> [Func] setsymbolPerFrmuser")
        addrs = [0x400B0088, 0x40090088, 0x400B00A8, 0x400900A8, ]
        for addr in addrs:
            clr._setSICParameters('setsymbolPerFrmuser', addr, param, 25, 18, RBCheck, debug)
    @classmethod
    def setoutputShiftNum(clr, param, RBCheck=True, debug=False):
        print("--> [Func] setoutputShiftNum")
        addrs = [0x400B0088, 0x40090088, 0x400B00A8, 0x400900A8, ]
        for addr in addrs:
            clr._setSICParameters('setoutputShiftNum', addr, param, 15, 12, RBCheck, debug)
    @classmethod
    def setchirp_period(clr, param, RBCheck=True, debug=False):
        print("--> [Func] setchirp_period")
        addrs = [0x400B0088, 0x40090088, 0x400B00A8, 0x400900A8, ]
        for addr in addrs:
            clr._setSICParameters('setchirp_period', addr, param, 11, 11, RBCheck, debug)
    @classmethod
    def setchirp_log_num(clr, param, RBCheck=True, debug=False):
        print("--> [Func] setchirp_log_num")
        addrs = [0x400B0088, 0x40090088, 0x400B00A8, 0x400900A8, ]
        for addr in addrs:
            clr._setSICParameters('setchirp_log_num', addr, param, 10, 8, RBCheck, debug)
    @classmethod
    def setsyncOffset(clr, param, RBCheck=True, debug=False):
        print("--> [Func] setsyncOffset")
        addrs = [0x400B0088, 0x40090088, 0x400B00A8, 0x400900A8, ]
        for addr in addrs:
            clr._setSICParameters('setsyncOffset', addr, param, 7, 0, RBCheck, debug)
    @classmethod
    def setdelayOfStart(clr, param, RBCheck=True, debug=False):
        print("--> [Func] setdelayOfStart")
        addrs = [0x400B009C, 0x4009009C, 0x400B00BC, 0x400900BC, ]
        for addr in addrs:
            clr._setSICParameters('setdelayOfStart', addr, param, 8, 0, RBCheck, debug)
    @classmethod
    def setW_starting(clr, param, RBCheck=True, debug=False):
        print("--> [Func] setW_starting")
        addrs = [0x400B008C, 0x4009008C, 0x400B00AC, 0x400900AC, ]
        for addr in addrs:
            clr._setSICParameters('setW_starting', addr, param, 7, 0, RBCheck, debug)
    @classmethod
    def setW_end(clr, param, RBCheck=True, debug=False):
        print("--> [Func] setW_end")
        addrs = [0x400B008C, 0x4009008C, 0x400B00AC, 0x400900AC, ]
        for addr in addrs:
            clr._setSICParameters('setW_end', addr, param, 15, 8, RBCheck, debug)

        # read_W_end0=kgl.ksoclib.readReg(0x400B008C, 15, 8)
        # if not (read_W_end0-W_end==0):
        #     print ("Overwrite W_end in reg 0x400B008C bit 15:8=", W_end)
    # @classmethod
    # def SICCtrlReg(cls, RF_trigger):
    #     print("---> SICCtrlReg()")
    #     outputshift0, outputshift1, outputshift2, outputshift3 = readoutputShiftNum()
    #     print("outputshift0,outputshift1, outputshift2, outputshift3=", outputshift0, outputshift1, outputshift2,
    #           outputshift3)
    #     # reg400B0088=read400B0088()
    #     # print("reg400B0088=", reg400B0088)
    #     # breakpoint()
    #     zdx = UpdateMUXValue()
    #     u0c0, u0c1, u1c0, u1c1 = UpdateMUXValue()
    #     idx1 = find(zdx, 1)
    #     if len(idx1) != 0:
    #         feedback1 = idx1[0]
    #     else:
    #         feedback1 = 2
    #
    #     idx2 = find(zdx, 2)
    #     if len(idx2) != 0:
    #         feedback2 = idx2[0][0]
    #     else:
    #         feedback2 = 2
    #
    #     idx3 = find(zdx, 3)
    #     if len(idx3) != 0:
    #         feedback3 = idx3[0][0]
    #     else:
    #         feedback3 = 2
    #     muxcfg(u0c0, u0c1, u1c0, u1c1, feedback1, feedback2, feedback3)
    #     print("Overwrite SIC MUX: u0c0:", str(u0c0), " u0c1:", str(u0c1), " u1c0:", str(u1c0), " u1c1:", str(u1c1),
    #           " feedback1:", str(feedback1), " feedback2:", str(feedback2), " feedback3:", str(feedback3))
    #     # print("!!Overwrite SIC MUX: u0c0:",str(u0c0), " u0c1:",str(u0c1))
    #
    #     if hasattr(cls, 'setting_config'):
    #         ParamDict = cls.setting_config.ParamDict
    #         if cls.setting_config.SIC.SIC_from_DSP_dict:
    #             print('SIC set from script.')
    #             cls.bufB_startIdx = ParamDict['DSPRx625K_Unit_0']['0x400B0098'][3]['bufB_startIdx']
    #             cls.delayOfStart = ParamDict['DSPRx625K_Unit_0']['0x400B009C'][3]['delayOfStart']
    #             cls.syncOffset = ParamDict['DSPRx625K_Unit_0']['0x400B0088'][3]['syncOffset']
    #             cls.chirp_log_num = ParamDict['DSPRx625K_Unit_0']['0x400B0088'][3]['chirp_log_num']  # 2^n
    #             cls.chirp_period = ParamDict['DSPRx625K_Unit_0']['0x400B0088'][3]['chirp_period']  # 0:64  1:128
    #             cls.changePolarity = ParamDict['DSPRx625K_Unit_0']['0x400B0098'][3]['changePolarity']
    #
    #             # for feedback gain DAC gain is 32x and  feedback loop atten -16->-12dB
    #             cls.W_starting = ParamDict['DSPRx625K_Unit_0']['0x400B008C'][3]['W_starting']
    #             cls.W_end = ParamDict['DSPRx625K_Unit_0']['0x400B008C'][3]['W_end']
    #
    #             # -----------------MISC-------------------------
    #             cls.symbolPerFrm = ParamDict['DSPRx625K_Unit_0']['0x400B0088'][3]['symbolPerFrm']  # 0:16   1:32   2:64  3: user
    #             cls.symbolPerFrmuser = ParamDict['DSPRx625K_Unit_0']['0x400B0088'][3]['symbolPerFrm_user']
    #             cls.cycelsPerFrm = ParamDict['DSPRx625K_Unit_0']['0x400B0098'][3]['cyclesPerFrm']
    #             cls.noUpdateBufB = ParamDict['DSPRx625K_Unit_0']['0x400B0098'][3]['noUpdateBufB']
    #
    #             cls.auto_cyclesPerFrm = ParamDict['DSPRx625K_Unit_0']['0x400B0098'][3]['auto_cyclesPerFrm']
    #             cls.SICInfo_sel = ParamDict['DSPRx625K_Unit_0']['0x400B0098'][3]['SICInfo_sel']  # 0=AIC_start, 1=cyclesPerFrm
    #             cls.outputShiftNum = ParamDict['DSPRx625K_Unit_0']['0x400B0088'][3]['outputShiftNum']
    #
    #     cls.setSICInfo_sel(cls.SICInfo_sel)
    #     print("!!Overwrite SICInfo_sel=", cls.SICInfo_sel)
    #     cls.setauto_cyclesPerFrm(cls.auto_cyclesPerFrm)
    #     print("!!Overwrite auto_cyclesPerFrm=", cls.auto_cyclesPerFrm)
    #     cls.setchangePolarity(cls.changePolarity)
    #     print("!!Overwrite changePolarity=", cls.changePolarity)
    #     cls.setnoUpdateBufB(cls.noUpdateBufB)
    #     print("!!Overwrite noUpdateBufB=", cls.noUpdateBufB)
    #     cls.setcyclePerFrm(cls.cycelsPerFrm)
    #     print("!!Overwrite cycelsPerFrm=", cls.cycelsPerFrm)
    #     cls.setbufB_startIdx(cls.bufB_startIdx)
    #     print("!!Overwrite bufB_startIdx=", cls.bufB_startIdx)
    #     cls.setsymbolPerFrm(cls.symbolPerFrm)
    #     print("!!Overwrite symbolPerFrm=", cls.symbolPerFrm)
    #     cls.setsymbolPerFrmuser(cls.symbolPerFrmuser)
    #     print("!!Overwrite symbolPerFrmuser=", cls.symbolPerFrmuser)
    #     # clr.setoutputShiftNum(clr.outputShiftNum)
    #     cls.setchirp_period(cls.chirp_period)
    #     print("!!Overwrite chirp_period=", cls.chirp_period)
    #     cls.setchirp_log_num(cls.chirp_log_num)
    #     print("!!Overwrite  chirp_log_num=", cls.chirp_log_num)
    #     cls.setsyncOffset(cls.syncOffset)
    #     print("!!Overwrite syncOffset=", cls.syncOffset)
    #     cls.setdelayOfStart(cls.delayOfStart)
    #     print("!!Overwrite delayOfStart=", cls.delayOfStart)
    #     cls.setW_starting(cls.W_starting)
    #     print("!!Overwrite W_starting=", cls.W_starting)
    #     cls.setW_end(cls.W_end)
    #     print("!!Overwrite W_end=", cls.W_end)
    #     # trigger setting done
    #     time.sleep(0.1)
    #     triggerRegSettingDoneAll()
    #     time.sleep(0.1)
    #     if RF_trigger:
    #         triggerSIC()
    #         print('SIC triggered')
    #     else:
    #         triggerAIC()
    #         print('AIC triggered')
    #     outputshift0, outputshift1, outputshift2, outputshift3 = readoutputShiftNum()
    #     print("outputshift0,outputshift1, outputshift2, outputshift3=", outputshift0, outputshift1, outputshift2,
    #           outputshift3)

class SICControl(SICFunction):
    def __init__(self, setting_config: SettingConfigs = None):
        self.setting_config = setting_config

    def SICCtrlReg(self, RF_trigger):
        print("---> SICCtrlReg()")
        outputshift0, outputshift1, outputshift2, outputshift3 = readoutputShiftNum()
        print("outputshift0,outputshift1, outputshift2, outputshift3=", outputshift0, outputshift1, outputshift2,
              outputshift3)
        # reg400B0088=read400B0088()
        # print("reg400B0088=", reg400B0088)
        # breakpoint()
        zdx = UpdateMUXValue()
        u0c0, u0c1, u1c0, u1c1 = UpdateMUXValue()
        idx1 = find(zdx, 1)
        if len(idx1) != 0:
            feedback1 = idx1[0][0]
        else:
            feedback1 = 2

        idx2 = find(zdx, 2)
        if len(idx2) != 0:
            feedback2 = idx2[0][0]
        else:
            feedback2 = 2

        idx3 = find(zdx, 3)
        if len(idx3) != 0:
            feedback3 = idx3[0][0]
        else:
            feedback3 = 2
        muxcfg(u0c0, u0c1, u1c0, u1c1, feedback1, feedback2, feedback3)
        print("Overwrite SIC MUX: u0c0:", str(u0c0), " u0c1:", str(u0c1), " u1c0:", str(u1c0), " u1c1:", str(u1c1),
              " feedback1:", str(feedback1), " feedback2:", str(feedback2), " feedback3:", str(feedback3))
        # print("!!Overwrite SIC MUX: u0c0:",str(u0c0), " u0c1:",str(u0c1))

        if hasattr(self, 'setting_config'):
            ParamDict = self.setting_config.ParamDict
            if self.setting_config.SIC.SIC_from_DSP_dict:
                print('SIC set from script.')
                self.bufB_startIdx = ParamDict['DSPRx625K_Unit_0']['0x400B0098'][3]['bufB_startIdx']
                self.delayOfStart = ParamDict['DSPRx625K_Unit_0']['0x400B009C'][3]['delayOfStart']
                self.syncOffset = ParamDict['DSPRx625K_Unit_0']['0x400B0088'][3]['syncOffset']
                self.chirp_log_num = ParamDict['DSPRx625K_Unit_0']['0x400B0088'][3]['chirp_log_num']  # 2^n
                self.chirp_period = ParamDict['DSPRx625K_Unit_0']['0x400B0088'][3]['chirp_period']  # 0:64  1:128
                self.changePolarity = ParamDict['DSPRx625K_Unit_0']['0x400B0098'][3]['changePolarity']

                # for feedback gain DAC gain is 32x and  feedback loop atten -16->-12dB
                self.W_starting = ParamDict['DSPRx625K_Unit_0']['0x400B008C'][3]['W_starting']
                self.W_end = ParamDict['DSPRx625K_Unit_0']['0x400B008C'][3]['W_end']

                # -----------------MISC-------------------------
                self.symbolPerFrm = ParamDict['DSPRx625K_Unit_0']['0x400B0088'][3][
                    'symbolPerFrm']  # 0:16   1:32   2:64  3: user
                self.symbolPerFrmuser = ParamDict['DSPRx625K_Unit_0']['0x400B0088'][3]['symbolPerFrm_user']
                self.cycelsPerFrm = ParamDict['DSPRx625K_Unit_0']['0x400B0098'][3]['cyclesPerFrm']
                self.noUpdateBufB = ParamDict['DSPRx625K_Unit_0']['0x400B0098'][3]['noUpdateBufB']

                self.auto_cyclesPerFrm = ParamDict['DSPRx625K_Unit_0']['0x400B0098'][3]['auto_cyclesPerFrm']
                self.SICInfo_sel = ParamDict['DSPRx625K_Unit_0']['0x400B0098'][3][
                    'SICInfo_sel']  # 0=AIC_start, 1=cyclesPerFrm
                self.outputShiftNum = ParamDict['DSPRx625K_Unit_0']['0x400B0088'][3]['outputShiftNum']

        self.setSICInfo_sel(self.SICInfo_sel)
        print("!!Overwrite SICInfo_sel=", self.SICInfo_sel)
        self.setauto_cyclesPerFrm(self.auto_cyclesPerFrm)
        print("!!Overwrite auto_cyclesPerFrm=", self.auto_cyclesPerFrm)
        self.setchangePolarity(self.changePolarity)
        print("!!Overwrite changePolarity=", self.changePolarity)
        self.setnoUpdateBufB(self.noUpdateBufB)
        print("!!Overwrite noUpdateBufB=", self.noUpdateBufB)
        self.setcyclePerFrm(self.cycelsPerFrm)
        print("!!Overwrite cycelsPerFrm=", self.cycelsPerFrm)
        self.setbufB_startIdx(self.bufB_startIdx)
        print("!!Overwrite bufB_startIdx=", self.bufB_startIdx)
        self.setsymbolPerFrm(self.symbolPerFrm)
        print("!!Overwrite symbolPerFrm=", self.symbolPerFrm)
        self.setsymbolPerFrmuser(self.symbolPerFrmuser)
        print("!!Overwrite symbolPerFrmuser=", self.symbolPerFrmuser)
        # clr.setoutputShiftNum(clr.outputShiftNum)
        self.setchirp_period(self.chirp_period)
        print("!!Overwrite chirp_period=", self.chirp_period)
        self.setchirp_log_num(self.chirp_log_num)
        print("!!Overwrite  chirp_log_num=", self.chirp_log_num)
        self.setsyncOffset(self.syncOffset)
        print("!!Overwrite syncOffset=", self.syncOffset)
        self.setdelayOfStart(self.delayOfStart)
        print("!!Overwrite delayOfStart=", self.delayOfStart)
        self.setW_starting(self.W_starting)
        print("!!Overwrite W_starting=", self.W_starting)
        self.setW_end(self.W_end)
        print("!!Overwrite W_end=", self.W_end)
        # trigger setting done
        time.sleep(0.1)
        triggerRegSettingDoneAll()
        time.sleep(0.1)
        if RF_trigger:
            triggerSIC()
            print('SIC triggered')
        else:
            triggerAIC()
            print('AIC triggered')
        outputshift0, outputshift1, outputshift2, outputshift3 = readoutputShiftNum()
        print("outputshift0,outputshift1, outputshift2, outputshift3=", outputshift0, outputshift1, outputshift2,
              outputshift3)

def muxcfg(u0c0_frmstartSel, u0c1_frmstartSel, u1c0_frmstartSel, u1c1_frmstartSel, rf1_sic_in_sel, rf2_sic_in_sel, rf3_sic_in_sel):   
    print("--> [Func] muxcfg") 
    RBCheck=True   
    
    #%-------------------Basic:SIC input mux----------------
    kResult=kgl.ksoclib.writeReg(u0c0_frmstartSel , 0x400B0200 , 1, 0, RBCheck)
    kResult=kgl.ksoclib.writeReg(u0c1_frmstartSel , 0x400B0200 , 3, 2, RBCheck)
    kResult=kgl.ksoclib.writeReg(u1c0_frmstartSel , 0x400B0200 , 5, 4, RBCheck)
    kResult=kgl.ksoclib.writeReg(u1c1_frmstartSel , 0x400B0200 , 7, 6, RBCheck)
    
    kResult=kgl.ksoclib.writeReg(u0c0_frmstartSel , 0x40090200 , 1, 0, RBCheck)
    kResult=kgl.ksoclib.writeReg(u0c1_frmstartSel , 0x40090200 , 3, 2, RBCheck)
    kResult=kgl.ksoclib.writeReg(u1c0_frmstartSel , 0x40090200 , 5, 4, RBCheck)
    kResult=kgl.ksoclib.writeReg(u1c1_frmstartSel , 0x40090200 , 7, 6, RBCheck)
    
    kResult=kgl.ksoclib.writeReg(rf1_sic_in_sel , 0x400B0200 , 10, 8 , RBCheck)
    kResult=kgl.ksoclib.writeReg(rf2_sic_in_sel , 0x400B0200 , 13, 11 ,RBCheck)
    kResult=kgl.ksoclib.writeReg(rf3_sic_in_sel , 0x400B0200 , 16, 14,RBCheck)

    kResult=kgl.ksoclib.writeReg(rf1_sic_in_sel , 0x40090200 , 10, 8, RBCheck)
    kResult=kgl.ksoclib.writeReg(rf2_sic_in_sel , 0x40090200 , 13, 11, RBCheck)
    kResult=kgl.ksoclib.writeReg(rf3_sic_in_sel , 0x40090200 , 16, 14, RBCheck)
    #%-----------------------------------------------------------

def getCh(u):
    o1 = 0
    o2 = 0
    
    if u == 0:
        o1 = 1
        o2 = 2
    elif u == 1:
        o1 = 2
        o2 = 3    
    elif u == 2:
        o1 = 3
        o2 = 1
    elif u == 3:
        o1 = 1
        o2 = 1
    elif u == 4:
        o1 = 2
        o2 = 1
    elif u == 5:
        o1 = 3
        o2 = 2
    elif u == 6:
        o1 = 1
        o2 = 3
    elif u == 7:
        o1 = 2
        o2 = 2
    elif u == 8:
        o1 = 3
        o2 = 3
    return o1,o2

def find(source, target):
    zdx=np.array(source)
    return np.argwhere(zdx==target)

## Nick begin
def UpdateMUXValue():
    global MUXValue
    data = kgl.ksoclib.regRead(0x50000544, 1)
    MUXValue = data[0]

    u0 = MUXValue & 0xF
    # u0 = 5
    print('u0: {}'.format(MUXValue & 0xF))
    u0c0, u0c1 = getCh(u0)
    u1 = (MUXValue >> 4) & 0xF
    # u1 = 5
    print('u1: {}'.format((MUXValue >> 4) & 0xF))
    u1c0, u1c1 = getCh(u1)
    return u0c0, u0c1, u1c0, u1c1

## end
def readoutputShiftNum():
    print("--> [Func] readoutputShiftNum")
    outputShiftNum0 = kgl.ksoclib.readReg(0x400B0088, 15, 12)
    value = kgl.ksoclib.readReg(0x400B0088, 15, 12)
    print('0x400B0088[15:12]={0}'.format(value))
    value = kgl.ksoclib.readReg(0x400B0088, 31, 0)
    print('0x400B0088[31:0]={0}'.format(value))
    value = kgl.ksoclib.regRead(0x400B0088, 1)
    print('0x400B0088[31:0]={0}'.format(value))

    outputShiftNum1 = kgl.ksoclib.readReg(0x40090088, 15, 12)
    outputShiftNum2 = kgl.ksoclib.readReg(0x400B00A8, 15, 12)
    outputShiftNum3 = kgl.ksoclib.readReg(0x400900A8, 15, 12)
    return outputShiftNum0, outputShiftNum1, outputShiftNum2, outputShiftNum3

def read400B0088():
    out = kgl.ksoclib.readReg(0x400B0088, 31, 0)
    return out

def triggerRegSettingDoneAll():
    print("--> [Func] triggerRegSettingDoneAll")
    RBCheck = 1

    kResult = kgl.ksoclib.writeReg(1, 0x400B0084, 8, 8, RBCheck)
    kResult = kgl.ksoclib.writeReg(1, 0x400B00A4, 8, 8, RBCheck)
    kResult = kgl.ksoclib.writeReg(1, 0x40090084, 8, 8, RBCheck)
    kResult = kgl.ksoclib.writeReg(1, 0x400900A4, 8, 8, RBCheck)

def triggerAIC():
    print("--> [Func] triggerAIC")
    RBCheck = 1
    # kResult=kgl.ksoclib.writeReg(513, 0x400B0084, 9, 0, RBCheck)
    # kResult=kgl.ksoclib.writeReg(513, 0x400B00A4, 9, 0, RBCheck)
    # kResult=kgl.ksoclib.writeReg(513, 0x40090084, 9, 0 ,RBCheck)
    # kResult=kgl.ksoclib.writeReg(513, 0x400900A4, 9, 0, RBCheck)

    kResult = kgl.ksoclib.writeReg(1, 0x400B0084, 0, 0, RBCheck)
    kResult = kgl.ksoclib.writeReg(1, 0x400B00A4, 0, 0, RBCheck)
    kResult = kgl.ksoclib.writeReg(1, 0x40090084, 0, 0, RBCheck)
    kResult = kgl.ksoclib.writeReg(1, 0x400900A4, 0, 0, RBCheck)

def triggerSIC():
    print("--> [Func] triggerSIC")
    RBCheck = 1
    # kResult=kgl.ksoclib.writeReg(513, 0x400B0084, 9, 0, RBCheck)
    # kResult=kgl.ksoclib.writeReg(513, 0x400B00A4, 9, 0, RBCheck)
    # kResult=kgl.ksoclib.writeReg(513, 0x40090084, 9, 0 ,RBCheck)
    # kResult=kgl.ksoclib.writeReg(513, 0x400900A4, 9, 0, RBCheck)

    kResult = kgl.ksoclib.writeReg(1, 0x400B0084, 0, 0, RBCheck)
    kResult = kgl.ksoclib.writeReg(1, 0x400B00A4, 0, 0, RBCheck)
    kResult = kgl.ksoclib.writeReg(1, 0x40090084, 0, 0, RBCheck)
    kResult = kgl.ksoclib.writeReg(1, 0x400900A4, 0, 0, RBCheck)
    time.sleep(0.3)
    kResult = kgl.ksoclib.writeReg(1, 0x400B0084, 9, 9, RBCheck)
    kResult = kgl.ksoclib.writeReg(1, 0x400B00A4, 9, 9, RBCheck)
    kResult = kgl.ksoclib.writeReg(1, 0x40090084, 9, 9, RBCheck)
    kResult = kgl.ksoclib.writeReg(1, 0x400900A4, 9, 9, RBCheck)
    
def PrintAddrValue(addr):
    kres, data = kgl.ksoclib.Device_Read_Reg(addr, 1, None)
    print("DW  {} {}".format(hex(addr), hex(data[0])))

def PrintMatlabGenFile():
    print("")
    print("Check current value")
    print("//MUX, now only for ch2 3")
    PrintAddrValue(0x400B0200)
    PrintAddrValue(0x40090200)
    print("//MISC INFO , polarity reverse, bufb_start")
    PrintAddrValue(0x400B0098)
    PrintAddrValue(0x40090098)
    PrintAddrValue(0x400B00B8)
    PrintAddrValue(0x400900B8)
    print("//MISC INFO , Frame")
    PrintAddrValue(0x400B0088)
    PrintAddrValue(0x40090088)
    PrintAddrValue(0x400B00A8)
    PrintAddrValue(0x400900A8)
    print("//MISC INFO , delay of start")
    PrintAddrValue(0x400B009C)
    PrintAddrValue(0x4009009C)
    PrintAddrValue(0x400B00BC)
    PrintAddrValue(0x400900BC)
    print("//MISC INFO , convergence rate")
    PrintAddrValue(0x400B008C)
    PrintAddrValue(0x400B00AC)
    PrintAddrValue(0x4009008C)
    PrintAddrValue(0x400900AC)
    print("//MISC INFO , sync, please add a little bit of delay after this block")
    PrintAddrValue(0x400B0084)
    PrintAddrValue(0x400B00A4)
    PrintAddrValue(0x40090084)
    PrintAddrValue(0x400900A4)
    print("//SIC  AIC trigger")
    PrintAddrValue(0x400B0084)
    PrintAddrValue(0x400B00A4)
    PrintAddrValue(0x40090084)
    PrintAddrValue(0x400900A4)

def read_SIC_status(debug_displace=1):
    AIC_enable_status1=kgl.ksoclib.readReg( 0x400B0090, 0, 0)
    sic_info1=kgl.ksoclib.readReg( 0x400B0090, 18, 1)
    sic_frm_cnt1=kgl.ksoclib.readReg( 0x400B0090, 26, 19)
    sic_opstatus1=kgl.ksoclib.readReg( 0x400B0090, 29, 27)

    AIC_enable_status2=kgl.ksoclib.readReg( 0x400B00B0, 0, 0)
    sic_info2=kgl.ksoclib.readReg( 0x400B00B0, 18, 1)
    sic_frm_cnt2=kgl.ksoclib.readReg( 0x400B00B0, 26, 19)
    sic_opstatus2=kgl.ksoclib.readReg( 0x400B00B0, 29, 27)

    AIC_enable_status3=kgl.ksoclib.readReg( 0x40090090, 0, 0)
    sic_info3=kgl.ksoclib.readReg( 0x40090090, 18, 1)
    sic_frm_cnt3=kgl.ksoclib.readReg( 0x40090090, 26, 19)
    sic_opstatus3=kgl.ksoclib.readReg( 0x40090090, 29, 27)

    AIC_enable_status4=kgl.ksoclib.readReg( 0x400900B0, 0, 0)
    sic_info4=kgl.ksoclib.readReg( 0x400900B0, 18, 1)
    sic_frm_cnt4=kgl.ksoclib.readReg( 0x400900B0, 26, 19)
    sic_opstatus4=kgl.ksoclib.readReg( 0x400900B0, 29, 27)
   

    if debug_displace :
        print('-------------------------------SIC debug info--------------------------------')
        print('AIC_enable_status: ', str(AIC_enable_status1), ' ', str(AIC_enable_status2), ' ',  str(AIC_enable_status3), ' ', str(AIC_enable_status4) )
        print('SIC_info: ', str(sic_info1), ' ', str(sic_info2), ' ',  str(sic_info3), ' ', str(sic_info4) )
        print('Frame Cnt: ', str(sic_frm_cnt1), ' ', str(sic_frm_cnt2), ' ',  str(sic_frm_cnt3), ' ', str(sic_frm_cnt4) )
        print('SIC Op Status (0: disable  1:op  2:wait sic frm st ): ', str(sic_opstatus1), ' ', str(sic_opstatus2), ' ',  str(sic_opstatus3), ' ', str(sic_opstatus4) )
        print('-----------------------------------------------------------------------------------')


    triggered = False
    if [str(sic_opstatus1), str(sic_opstatus2), str(sic_opstatus3)] == ['2','2','2'] and \
            [str(AIC_enable_status1),str(AIC_enable_status2),str(AIC_enable_status3),str(AIC_enable_status4)] == ['1','1','1','1']:
        triggered = True

    return sic_frm_cnt1, sic_info1 , triggered

def runSIC(RF_trigger = True, setting_config:SettingConfigs=None):
    SICFunc = SICControl(setting_config)
    SICFunc.SICCtrlReg(RF_trigger)
    time.sleep(1)
    cnt = 0
    if RF_trigger:
        triggered = read_SIC_status()[2]
        while not triggered:
            cnt = cnt + 1
            RBCheck = 0
            # stop AIC
            kgl.ksoclib.writeReg(1, 0x400B0084, 1, 1, RBCheck)
            kgl.ksoclib.writeReg(1, 0x400B00A4, 1, 1, RBCheck)
            kgl.ksoclib.writeReg(1, 0x40090084, 1, 1, RBCheck)
            kgl.ksoclib.writeReg(1, 0x400900A4, 1, 1, RBCheck)
            time.sleep(0.3)
            # stop SIC
            kgl.ksoclib.writeReg(1, 0x400B0084, 10, 10, RBCheck)
            kgl.ksoclib.writeReg(1, 0x400B00A4, 10, 10, RBCheck)
            kgl.ksoclib.writeReg(1, 0x40090084, 10, 10, RBCheck)
            kgl.ksoclib.writeReg(1, 0x400900A4, 10, 10, RBCheck)

            SICFunc.SICCtrlReg(RF_trigger)
            time.sleep(1)
            triggered = read_SIC_status()[2]
            print('SIC opened (trigger times:{})'.format(cnt))





if __name__ == '__main__':
    print("Done")
    

