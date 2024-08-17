import time
from KKT_Module.ksoc_global import kgl

class RFController():
    RX_reg = {
        'RX1': (0x0050, 0x0051, 0x0053),
        'RX2': (0x0064, 0x0065, 0x0067),
        'RX3': (0x0078, 0x0079, 0x007B),
    }
    RX_enable = {
        'enable': (0x0DD3, 0xA1F4, 0x0833),
        'disable': (0x0DD2, 0xA1D4, 0x0823),
    }
    RX_gain_reg = {'RX1':(0x0155, 0x0157),
                   'RX2': (0x0169, 0x016B),
                   'RX3': (0x017D, 0x017F),
                   }
    @classmethod
    def setTXGain(cls, value): # AIoT
        # TX = {'1': [0x003C, 0x08A5],
        #       '2': [0x003C, 0x0CE7],
        #       '3': [0x003C, 0x1129],
        #       '4': [0x003C, 0x19AB],
        #       }
        # gain = TX.get(str(level))
        print('[RF Control] setTXGain')
        kgl.ksoclib.rficRegWrite(0x003C, value)

    @classmethod
    def getTXGain(cls): # AIoT
        val = kgl.ksoclib.rficRegRead(0x003C)
        TX = {
            0x08A5: '1',
            0x0CE7: '2',
            0x1129: '3',
            0x19AB: '4',
        }
        level = TX.get(val)
        return level

    @classmethod
    def setRXGain(cls, level:str, RX:str): # AIoT
        RX_dict = { 'RX1' : {'1': [[0x0155, 0x380B], [0x0157, 0x1C0F]],
                           '2': [[0x0155, 0x380F], [0x0157, 0x1C0F]],
                           '3': [[0x0155, 0x3813], [0x0157, 0x1C0F]],
                           '4': [[0x0155, 0x3817], [0x0157, 0x1C0F]],
                          },
                    'RX2' : {'1': [[0x0169, 0x380B], [0x016B, 0x1C0F]],
                           '2': [[0x0169, 0x380F], [0x016B, 0x1C0F]],
                           '3': [[0x0169, 0x3813], [0x016B, 0x1C0F]],
                           '4': [[0x0169, 0x3817], [0x016B, 0x1C0F]],
                          },
                    'RX3' : {'1': [[0x017D, 0x380B], [0x017F, 0x1C0F]],
                           '2': [[0x017D, 0x380F], [0x017F, 0x1C0F]],
                           '3': [[0x017D, 0x3813], [0x017F, 0x1C0F]],
                           '4': [[0x017D, 0x3817], [0x017F, 0x1C0F]],
                           }
                    }
        print('[RF Control] setTXGain')
        for gain in RX_dict[RX].get(str(level)):
            kgl.ksoclib.rficRegWrite(gain[0], gain[1])

    @classmethod
    def getRXGain(cls, RX:str): # AIoT
        # RX_dict = {
        #     'RX1': 0x0155,
        #     'RX2': 0x0169,
        #     'RX3': 0x017D,
        # }
        # RX_level = {
        #     0x380B :'1',
        #     0x380F :'2',
        #     0x3813 :'3',
        #     0x3817 :'4'
        # }
        val = kgl.ksoclib.rficRegRead(cls.RX_gain_reg[RX])
        # level = RX_level.get(val)
        return val

    @classmethod
    def setChirpNumber(cls, chirp:int, duration:int): # AIoT
        chirp = int(chirp)
        duration = float(duration)
        CN = 0x6200 + ((chirp - 1) & 0xFFFF)
        Gap = int(duration * 5 - chirp) & 0xFFFF
        SX = 0x0001 + (int((duration - 1) * 5 - chirp - 1) << 8) & 0xFFFF
        TX = 0x0001 + (int((duration - 1) * 5 - chirp + 3) << 8) & 0xFFFF
        RX1 = 0x0001 + (int((duration - 1) * 5 - chirp + 0) << 8) & 0xFFFF
        RX2 = 0x0001 + (int((duration - 1) * 5 - chirp + 1) << 8) & 0xFFFF
        RX3 = 0x0001 + (int((duration - 1) * 5 - chirp + 2) << 8) & 0xFFFF
        # number_dict = {'1': [[0x0026, 0x6200],{'35':[[0x0024, 0x00AE],[0x012B, 0xA801],[0x0143, 0xA901],[0x015E, 0xAA01],[0x0172, 0xAB01],[0x0186, 0xAC01]],
        #                                        '50':[[0x0024, 0x00F9],[0x012B, 0xF301],[0x0143, 0xF401],[0x015E, 0xF501],[0x0172, 0xF601],[0x0186,0xF701]],
        #                                        '30': [[0x0024, 0x0095], [0x012B, 0x8F01], [0x0143, 0x9001],[0x015E, 0x9101], [0x0172, 0x9201], [0x0186, 0x9301]],}],
        #                '4': [[0x0026, 0x6203],{'35':[[0x0024, 0x00AB],[0x012B, 0xA501],[0x0143, 0xA601],[0x015E, 0xA701],[0x0172, 0xA801],[0x0186, 0xA901]],
        #                                        '50':[[0x0024, 0x00F6],[0x012B, 0xF001],[0x0143, 0xF101],[0x015E, 0xF201],[0x0172, 0xF301],[0x0186,0xF401]],
        #                                        '30': [ [0x0024,0x0092],[0x012B,0x8C01], [0x0143,0x8D01], [0x015E,0x8E01], [0x0172,0x8F01], [0x0186,0x9001]],}],
        #               '16': [[0x0026, 0x620F],{'35':[[0x0024, 0x009F],[0x012B, 0x9901],[0x0143, 0x9A01],[0x015E, 0x9B01],[0x0172, 0x9C01],[0x0186, 0x9D01]],
        #                                        '50':[[0x0024, 0x00EA],[0x012B, 0xE401],[0x0143, 0xE501],[0x015E, 0xE601],[0x0172, 0xE701],[0x0186,0xE801]],
        #                                        '30': [ [0x0024,0x0086],[0x012B,0x8001], [0x0143,0x8101], [0x015E,0x8201], [0x0172,0x8301], [0x0186,0x8401]],
        #                                        '20': [[0x0024, 0x0054], [0x012B, 0x3F01], [0x0143, 0x4F01],[0x015E, 0x5001], [0x0172, 0x5101], [0x0186, 0x5201]],
        #                                        '25': [[0x0024, 0x006D], [0x012B, 0x6701], [0x012B, 0x6801],[0x015E, 0x6901], [0x0172, 0x6A01], [0x0186, 0x6B01]],}],
        #               '32': [[0x0026, 0x621F],{'35':[[0x0024, 0x008F],[0x012B, 0x8901],[0x0143, 0x8A01],[0x015E, 0x8B01],[0x0172, 0x8C01],[0x0186, 0x8D01]],
        #                                        '50':[[0x0024, 0x00DA],[0x012B, 0xD401],[0x0143, 0xD501],[0x015E, 0xD601],[0x0172, 0xD701],[0x0186,0xD801]],
        #                                        '30': [ [0x0024,0x0076],[0x012B,0x7001], [0x0143,0x7101], [0x015E,0x7201], [0x0172,0x7301], [0x0186,0x7401]],
        #                                        '20': [[0x0024, 0x0044], [0x012B, 0x3E01], [0x0143, 0x3F01],[0x015E, 0x4001], [0x0172, 0x4101], [0x0186, 0x4201]],
        #                                        '25': [[0x0024, 0x0060], [0x012B, 0x5701], [0x0143, 0x5801],[0x015E, 0x5901], [0x0172, 0x5A01], [0x0186, 0x5B01]],}],
        #               }
        print('[RF Control] setChirpNumber')
        arg = (chirp, duration, hex(CN), hex(Gap), hex(SX), hex(TX), hex(RX1), hex(RX2), hex(RX3))
        print('chirp={}, duration= {}ms, CN={}, Gap={}, SX={}, TX={}, RX1={}, RX2={}, RX3={}'.format(*arg))
        # num = number_dict.get(str(chirp))[0]
        kgl.ksoclib.rficRegWrite(0x0026, CN)
        # duration_dict = number_dict.get(str(chirp))[1][duration]
        # gap = duration_dict[0]
        kgl.ksoclib.rficRegWrite(0x0024, Gap)
        # SX = duration_dict[1]
        kgl.ksoclib.rficRegWrite(0x012B, SX)
        # TX = duration_dict[2]
        kgl.ksoclib.rficRegWrite(0x0143, TX)
        # RX1 = duration_dict[3]
        kgl.ksoclib.rficRegWrite(0x015E, RX1)
        # RX2 = duration_dict[4]
        kgl.ksoclib.rficRegWrite(0x0172, RX2)
        # RX3 = duration_dict[5]
        kgl.ksoclib.rficRegWrite(0x0186, RX3)
        cls.setPowerSavingCmd()

    @classmethod
    def getDuration(cls)->int: # AIoT
        # if chirp is None:
        #     return chirp
        # duration_dict = {
        #     '1': {
        #         0x0095: '30',
        #         0x00AE :'35',
        #         0x00F9 :'50',
        #     },
        #     '4': {
        #         0x0092: '30',
        #         0x00AB: '35',
        #         0x00F6: '50',
        #     },
        #     '16': {
        #         0x0086: '30',
        #         0x009F: '35',
        #         0x00EA: '50',
        #         0x0054: '20',
        #         0x006D: '25',
        #     },
        #     '32': {
        #         0x0076: '30',
        #         0x008F: '35',
        #         0x00DA: '50',
        #         0x0044: '20',
        #         0x0060: '25',
        #     }
        # }
        chirp = cls.getChirpNumber()
        val = kgl.ksoclib.rficRegRead(0x0024)
        duration = (val+chirp)/5
        return int(duration)

    @classmethod
    def getChirpNumber(cls)->int: # AIoT
        # chirp_dict = {0x6200: '1' ,
        #               0x6203: '4' ,
        #               0x620F: '16',
        #               0x621F: '32',}
        #
        # duration_dict = {
        #     '1' : {0xA801 :'35',
        #            0xF301 :'50',
        #            0x8F01 :'30',},
        #     '4' : {0xA501 :'35',
        #            0xF001 :'50',
        #            0x8C01 :'30',},
        #     '16': {0x9901 :'35',
        #            0xE401 :'50',
        #            0x8001 :'30',
        #            0x3F01 :'20',
        #            0x6701 :'25',},
        #     '32': {0x8901 :'35',
        #            0xD401 :'50',
        #            0x7001 :'30',
        #            0x3E01 :'20',
        #            0x5701 :'25',}
        # }
        val = kgl.ksoclib.rficRegRead(0x0026)
        chirp = val & 0xFF +1
        # chirp = chirp_dict.get(val)
        # val = kgl.ksoclib.rficRegRead(0x012B)
        # duration = duration_dict[chirp][val]
        return chirp#, duration

    @classmethod
    def setChirpBandWidth(cls, BW_config:tuple):# AIoT
            # band_width_dict = {'7'  :(0x0000, 0x11D0, 0x2300, 0x3000, 0x0802),
            #                    '4'  :(0x0000, 0x1248, 0x1400, 0x4000, 0x0801),
            #                    '2'  :(0x0000, 0x1298, 0x0A00, 0xA000, 0x0800),
            #                    '1.5':(0x0000, 0x12AC, 0x0780, 0x7800, 0x0800),
            #                    '1'  :(0x0000, 0x12C0, 0x0500, 0x5000, 0x0800),
            #                    '0.8':(0x0000, 0x12C8, 0x0400, 0x4000, 0x0800),}
            print('[RF Control] setChirpBandWidth')
            # for bw in band_width_dict.get(BW):
            # F1 Base
            kgl.ksoclib.rficRegWrite(0x0021, BW_config[0])
            kgl.ksoclib.rficRegWrite(0x0022, BW_config[1])
            # F1 to F2 Delta
            kgl.ksoclib.rficRegWrite(0x0025, BW_config[2])
            # DCO CAL
            kgl.ksoclib.rficRegWrite(0x002A, BW_config[3])
            kgl.ksoclib.rficRegWrite(0x002B, BW_config[4])
            cls.calibrateDCO()

    @classmethod
    def getChirpBandWidth(cls):# AIoT
        val = kgl.ksoclib.rficRegRead(0x0022)
        bw = {
        0x11D0 : '0.6857 / 7'  ,
        0x1248 : '1.2 / 4'  ,
        0x1298 : '2.4 / 2'  ,
        0x12AC:  '3.2 / 1.5',
        0x12C0 : '4.8 / 1'  ,
        0x12C8 : '6 / 0.8',
        }
        distance = bw.get(val)
        return distance

    @classmethod
    def enableRX(cls, RX:str, enable):
        reg_list = cls.RX_reg.get(RX)
        if enable:
            val_list = cls.RX_enable.get('enable')
        else:
            val_list = cls.RX_enable.get('disable')
        for i in range(len(reg_list)):
            kgl.ksoclib.rficRegWrite(reg_list[i], val_list[i])

    @classmethod
    def getOpenedRX(cls):
        RX_enable = {}
        for rx in ['RX1', 'RX2', 'RX3']:
            reg= kgl.ksoclib.rficRegRead(cls.RX_reg.get(rx)[0])
            RX_enable[rx] = (reg == cls.RX_enable['enable'][0])
        return RX_enable

    @classmethod
    def switchSIC(cls, switch:bool):
        print('[RF Control] switchSIC')
        if switch:
            cls.enableTIA()
            return
        cls.stopSIC()

    @classmethod
    def stopSIC(cls):
        kgl.ksoclib.rficRegWrite(0x0162, 0x054D)
        kgl.ksoclib.rficRegWrite(0x0163, 0x0000)
        kgl.ksoclib.rficRegWrite(0x0176, 0x054D)
        kgl.ksoclib.rficRegWrite(0x0177, 0x0000)
        kgl.ksoclib.rficRegWrite(0x018A, 0x054D)
        kgl.ksoclib.rficRegWrite(0x018B, 0x0000)

    @classmethod
    def enableTIA(cls):
        print('[RF Control] enable TIA')
        kgl.ksoclib.rficRegWrite(0x0162, 0x4D5E)
        kgl.ksoclib.rficRegWrite(0x0163, 0x0000)
        kgl.ksoclib.rficRegWrite(0x0176, 0x4D5E)
        kgl.ksoclib.rficRegWrite(0x0177, 0x0000)
        kgl.ksoclib.rficRegWrite(0x018A, 0x4D5E)
        kgl.ksoclib.rficRegWrite(0x018B, 0x0000)

    @classmethod
    def enablePGA(self):
        print('[RF Control] enable PGA')
        kgl.ksoclib.rficRegWrite(0x0162, 0x5D4F)
        kgl.ksoclib.rficRegWrite(0x0163, 0x0000)
        kgl.ksoclib.rficRegWrite(0x0176, 0x5D4F)
        kgl.ksoclib.rficRegWrite(0x0177, 0x0000)
        kgl.ksoclib.rficRegWrite(0x018A, 0x5D4F)
        kgl.ksoclib.rficRegWrite(0x018B, 0x0000)

    @classmethod
    def getSICStatus(cls):
        return kgl.ksoclib.getRFSICEnableStatus()

    @classmethod
    def turnOnModulation(cls, turn_on):
        print('[RF Control] turnOnModulation ')
        kgl.ksoclib.switchModulationOn(turn_on)
        time.sleep(0.1)

    @classmethod
    def calibrateDCO(cls):
        print('[RF Control] calibrateDCO ')
        kgl.ksoclib.rficRegWrite(0x0030, 0x0000)
        kgl.ksoclib.rficRegWrite(0x002E, 0x03FF)
        kgl.ksoclib.rficRegWrite(0x0035, 0x0004)
        kgl.ksoclib.rficRegWrite(0x0033, 0x1028)
        kgl.ksoclib.rficRegWrite(0x0033, 0x1029)
        kgl.ksoclib.rficRegWrite(0x0033, 0x1028)
        time.sleep(0.05)
        kgl.ksoclib.rficRegWrite(0x0030, 0x0002)

    @classmethod
    def setPowerSavingGap(cls):
        pass

    @classmethod
    def setPowerSavingCmd(cls):
        kgl.ksoclib.rficRegWrite(0x0129, 0x0085)
        kgl.ksoclib.rficRegWrite(0x012A, 0x0000)
        kgl.ksoclib.rficRegWrite(0x012C, 0x0005)
        kgl.ksoclib.rficRegWrite(0x012D, 0x0013)
        kgl.ksoclib.rficRegWrite(0x0141, 0x2511)
        kgl.ksoclib.rficRegWrite(0x0142, 0x0000)
        kgl.ksoclib.rficRegWrite(0x0144, 0x0001)
        kgl.ksoclib.rficRegWrite(0x0145, 0x0000)
        kgl.ksoclib.rficRegWrite(0x015D, 0x1017)
        kgl.ksoclib.rficRegWrite(0x0160, 0x0002)
        kgl.ksoclib.rficRegWrite(0x0161, 0x3400)
        kgl.ksoclib.rficRegWrite(0x0171, 0x1017)
        kgl.ksoclib.rficRegWrite(0x0174, 0x0003)
        kgl.ksoclib.rficRegWrite(0x0175, 0x3400)
        kgl.ksoclib.rficRegWrite(0x0185, 0x1017)
        kgl.ksoclib.rficRegWrite(0x0188, 0x0004)
        kgl.ksoclib.rficRegWrite(0x0189, 0x3400)
        pass




if __name__ == '__main__':
    RFController.setChirpNumber(32, 10)


