from KKT_Module.ksoc_global import kgl
from KKT_Module.Configs import SettingConfigs
from KKT_Module.KKTUtility.RFControl import RFController
from KKT_Module.KKTUtility.DigiControl import DigiController


class PhaseCalibration:
    '''
    class for K60168 phase calibration process.
    '''
    _block_select_table = dict(enumerate(
        ((0b001, 0b010),
         (0b010, 0b100),
         (0b100, 0b001),
         (0b001, 0b001),
         (0b010, 0b001),
         (0b100, 0b010),
         (0b001, 0b100),
         (0b010, 0b010),
         (0b100, 0b100),)
    ))

    def __init__(self, config:SettingConfigs=None):
        self._phaseK_configs={
            'RX1_real_compansate': 'None',
            'RX1_image_compansate':'None',
            'RX2_real_compansate':'None',
            'RX2_image_compansate':'None',
            'Package':None,
            'ECC_burned':None,
                              }
        self._config = config
        pass

    def calibrate(self):
        print('# =========== Start Phase Calibration ===============')
        ECC_burned = self._checkEFuseBurned()
        self._phaseK_configs['ECC_burned'] = str(ECC_burned)
        if not ECC_burned:
            print('Dongle_type : pop')
            self._phaseK_configs['Package'] = 'POP'
            return self._phaseK_configs

        # if ECC_burned
        ICodesITanks = self._getICodeITank()
        self.setICodeITank(ICodesITanks)

        self._phase_offset_RX2, self._phase_offset_RX1, self._site_location, self._package_type = self._getPhaseKParam()
        self._lut = self._getLut()
        self._Cmd_list = self._getCmdList(ICodesITanks)

        self.setPacketType(self._package_type)
        self.setRXCompensate(self._lut, self._phase_offset_RX1, self._phase_offset_RX2)
        self._writeCompensate(self._phaseK_configs['RX1_real_compansate'],
                              self._phaseK_configs['RX1_image_compansate'],
                              self._phaseK_configs['RX2_real_compansate'],
                              self._phaseK_configs['RX2_image_compansate'])
        self._writeEFuseVal(self._Cmd_list)
        print('# -Phase calibrated')

        return self._phaseK_configs

    def updateRFConfig(self, RFConfig:dict):
        RFConfig.update(self._phaseK_configs)

    def getRXCompensate(self, lut, offset):
        phase_offset = offset - 0
        phase_offset = sign2unsign(phase_offset, 8)
        real_compensate = int(lut[0][phase_offset])
        image_compensate = int(lut[1][phase_offset])
        return real_compensate, image_compensate

    def setICodeITank(self, ICodesITanks):
        self._phaseK_configs['RX3_ICode'] = ICodesITanks[5]
        self._phaseK_configs['RX2_ICode'] = ICodesITanks[4]
        self._phaseK_configs['RX1_ICode'] = ICodesITanks[3]
        self._phaseK_configs['RX3_ITank'] = ICodesITanks[2]
        self._phaseK_configs['RX2_ITank'] = ICodesITanks[1]
        self._phaseK_configs['RX1_ITank'] = ICodesITanks[0]

    def setPacketType(self, package_type):
        if package_type == 0:  # POP
            self._phaseK_configs['Package'] = 'POP'
            print('Package_type : pop ')
        elif package_type == 1:  # possum
            self._phaseK_configs['Package'] = 'Possum'
            print('Package_type : Possum ')
        else:
            print('Unknow package type')

    def setRXCompensate(self, lut , RX1_offset=None, RX2_offset=None):
        if RX1_offset is not None:
            real_compensate, image_compensate = self.getRXCompensate(lut, RX1_offset)
            self._phaseK_configs['RX1_real_compansate'] = real_compensate
            self._phaseK_configs['RX1_image_compansate'] = image_compensate
        if RX2_offset is not None:
            real_compensate, image_compensate = self.getRXCompensate(lut, RX2_offset)
            self._phaseK_configs['RX2_real_compansate'] = real_compensate
            self._phaseK_configs['RX2_image_compansate'] = image_compensate
        return self._phaseK_configs

    def _writeCompensate(self, RX1_real_compensate, RX1_image_compensate, RX2_real_compensate, RX2_image_compensate):
        ADC_MuxParam = DigiController.getMuxParam()
        AI_mux = ADC_MuxParam[0]
        tracking_mux = ADC_MuxParam[1]

        unit0_upper_real_compensate = 1024
        unit0_upper_image_compensate = 0
        unit0_lower_real_compensate = 1024
        unit0_lower_image_compensate = 0
        unit1_upper_real_compensate = 1024
        unit1_upper_image_compensate = 0


        AI_block_select = self._block_select_table.get(int(AI_mux))
        tracking_block_select = self._block_select_table.get(int(tracking_mux))

        if AI_block_select[0] & 0b1:
            unit0_upper_real_compensate = RX1_real_compensate
            unit0_upper_image_compensate = RX1_image_compensate
        elif AI_block_select[0] & 0b10:
            unit0_upper_real_compensate = RX2_real_compensate
            unit0_upper_image_compensate = RX2_image_compensate

        kgl.ksoclib.writeReg(unit0_upper_real_compensate, 0x400D200C, 11, 0)
        kgl.ksoclib.writeReg(unit0_upper_image_compensate, 0x400D200C, 23, 12)

        if AI_block_select[1] & 0b1:
            unit0_lower_real_compensate = RX1_real_compensate
            unit0_lower_image_compensate = RX1_image_compensate
        elif AI_block_select[1] & 0b10:
            unit0_lower_real_compensate = RX2_real_compensate
            unit0_lower_image_compensate = RX2_image_compensate

        kgl.ksoclib.writeReg(unit0_lower_real_compensate, 0x400D600C, 11, 0)
        kgl.ksoclib.writeReg(unit0_lower_image_compensate, 0x400D600C, 23, 12)

        if tracking_block_select[0] & 0b1:
            unit1_upper_real_compensate = RX1_real_compensate
            unit1_upper_image_compensate = RX1_image_compensate
        elif tracking_block_select[0] & 0b10:
            unit1_upper_real_compensate = RX2_real_compensate
            unit1_upper_image_compensate = RX2_image_compensate

        kgl.ksoclib.writeReg(unit1_upper_real_compensate, 0x400F200C, 11, 0)
        kgl.ksoclib.writeReg(unit1_upper_image_compensate, 0x400F200C, 23, 12)


        # write compensate to setting configs
        if self._config is not None:
            DSPRx20M_Unit_0 = self._config.ParamDict['DSPRx20M_Unit_0']
            DSPRx20M_Unit_1 = self._config.ParamDict['DSPRx20M_Unit_1']

            DSPRx20M_Unit_0['0x400D200C'][3]['FT_rot_vec_re'] = unit0_upper_real_compensate
            DSPRx20M_Unit_0['0x400D200C'][3]['FT_rot_vec_im'] = unit0_upper_image_compensate
            DSPRx20M_Unit_0['0x400D600C'][3]['FT_rot_vec_re'] = unit0_lower_real_compensate
            DSPRx20M_Unit_0['0x400D600C'][3]['FT_rot_vec_im'] = unit0_lower_image_compensate
            DSPRx20M_Unit_1['0x400F200C'][3]['FT_rot_vec_re'] = unit1_upper_real_compensate
            DSPRx20M_Unit_1['0x400F200C'][3]['FT_rot_vec_im'] = unit1_upper_image_compensate

        compensates=(unit0_upper_real_compensate,
                     unit0_upper_image_compensate,
                     unit0_lower_real_compensate,
                     unit0_lower_image_compensate,
                     unit1_upper_real_compensate,
                     unit1_upper_image_compensate,)

        return compensates

    def _writeEFuseVal(self, Cmd_list):
        for cmd in Cmd_list:
            addr = int(cmd[:4], 16)
            val = int(cmd[4:], 16)
            kgl.ksoclib.rficRegWrite(addr=addr, val=val, Print=False)

    def _checkEFuseBurned(self)->bool:
        val = kgl.ksoclib.readEFuseCmd(addr=1)
        mod_val = val % (2 ** 27)
        bitmap = [[4, 0],
                  [4, 4],
                  [4, 8],
                  [4, 12],
                  [4, 16],
                  [4, 20],
                  [1, 24],
                  [1, 25]]
        signlist = ['$UNSG32', '$UNSG32', '$UNSG32', '$UNSG32', '$UNSG32', '$UNSG32', '$UNSG32', '$UNSG32']
        val_list = val2vallist(bitmap, mod_val, signlist)
        ECC_burned = False
        # print('addr25={}, addr26={}'.format(val_list[6], val_list[6]))
        if val_list[6]==0 and val_list[7]==1:
            ECC_burned = True
        print('ECC Burned :', ECC_burned)
        return ECC_burned

    def _getICodeITank(self):
        '''
        Return : RX1_ITank, RX2_ITank, RX3_ITank, RX1_ICode, RX2_ICode, RX3_ICode
        '''
        val = kgl.ksoclib.readEFuseCmd(addr=1)
        mod_val = val % (2 ** 25)
        bitmap = [[4, 0],
                  [4, 4],
                  [4, 8],
                  [4, 12],
                  [4, 16],
                  [4, 20]]
        signlist = ['$UNSG32', '$UNSG32', '$UNSG32', '$UNSG32', '$UNSG32', '$UNSG32']
        addr1vallist = val2vallist(bitmap, mod_val, signlist)
        return tuple(addr1vallist)

    def _getPhaseKParam(self):
        efuse_addr_list = [10, 9, 8, 2]
        val2 = None
        for i in range(len(efuse_addr_list)):
            val2 = kgl.ksoclib.readEFuseCmd(addr=efuse_addr_list[i])
            if val2 != 0:
                break
        mod_val2 = val2 % (2 ** 25)
        bitmap2 = [[8, 0],
                   [8, 8],
                   [4, 16],
                   [4, 20]]
        signlist2 = ['$UNSG32', '$UNSG32', '$UNSG32', '$UNSG32']
        val_list = val2vallist(bitmap2, mod_val2, signlist2)
        phase_offset_RX2 = val_list[0]
        phase_offset_RX1 = val_list[1]
        site_location = val_list[2]
        package_type = val_list[3]

        return phase_offset_RX2, phase_offset_RX1, site_location, package_type

    def _getLut(self):
        s1 = "0	25	50	75	100	125	150	175	200	224	249	273	297	321	345	369	392	415	438	460	483	505	526	548	569	590	610	630	650	669	688	706	724	742	759	775	792	807	822	837	851	865	878	891	903	915	926	936	946	955	964	972	980	987	993	999	1004	1009	1013	1016	1019	1021	1023	1024	1024	1024	1023	1021	1019	1016	1013	1009	1004	999	993	987	980	972	964	955	946	936	926	915	903	891	878	865	851	837	822	807	792	775	759	742	724	706	688	669	650	630	610	590	569	548	526	505	483	460	438	415	392	369	345	321	297	273	249	224	200	175	150	125	100	75	50	25	0	-25	-50	-75	-100	-125	-150	-175	-200	-224	-249	-273	-297	-321	-345	-369	-392	-415	-438	-460	-483	-505	-526	-548	-569	-590	-610	-630	-650	-669	-688	-706	-724	-742	-759	-775	-792	-807	-822	-837	-851	-865	-878	-891	-903	-915	-926	-936	-946	-955	-964	-972	-980	-987	-993	-999	-1004	-1009	-1013	-1016	-1019	-1021	-1023	-1024	-1024	-1024	-1023	-1021	-1019	-1016	-1013	-1009	-1004	-999	-993	-987	-980	-972	-964	-955	-946	-936	-926	-915	-903	-891	-878	-865	-851	-837	-822	-807	-792	-775	-759	-742	-724	-706	-688	-669	-650	-630	-610	-590	-569	-548	-526	-505	-483	-460	-438	-415	-392	-369	-345	-321	-297	-273	-249	-224	-200	-175	-150	-125	-100	-75	-50	-25"
        s2 = "1024	1024	1023	1021	1019	1016	1013	1009	1004	999	993	987	980	972	964	955	946	936	926	915	903	891	878	865	851	837	822	807	792	775	759	742	724	706	688	669	650	630	610	590	569	548	526	505	483	460	438	415	392	369	345	321	297	273	249	224	200	175	150	125	100	75	50	25	0	-25	-50	-75	-100	-125	-150	-175	-200	-224	-249	-273	-297	-321	-345	-369	-392	-415	-438	-460	-483	-505	-526	-548	-569	-590	-610	-630	-650	-669	-688	-706	-724	-742	-759	-775	-792	-807	-822	-837	-851	-865	-878	-891	-903	-915	-926	-936	-946	-955	-964	-972	-980	-987	-993	-999	-1004	-1009	-1013	-1016	-1019	-1021	-1023	-1024	-1024	-1024	-1023	-1021	-1019	-1016	-1013	-1009	-1004	-999	-993	-987	-980	-972	-964	-955	-946	-936	-926	-915	-903	-891	-878	-865	-851	-837	-822	-807	-792	-775	-759	-742	-724	-706	-688	-669	-650	-630	-610	-590	-569	-548	-526	-505	-483	-460	-438	-415	-392	-369	-345	-321	-297	-273	-249	-224	-200	-175	-150	-125	-100	-75	-50	-25	0	25	50	75	100	125	150	175	200	224	249	273	297	321	345	369	392	415	438	460	483	505	526	548	569	590	610	630	650	669	688	706	724	742	759	775	792	807	822	837	851	865	878	891	903	915	926	936	946	955	964	972	980	987	993	999	1004	1009	1013	1016	1019	1021	1023	1024"
        imag_lut = s1.split(' ')[0].split('\t')
        real_lut = s2.split(' ')[0].split('\t')
        lut = [real_lut, imag_lut]
        return lut

    def _getCmdList(self, ICodes_ITanks):
        tank_to_REG ={ 0: '0011',
                       1: '0031',
                       2: '0051',
                       3: '0071',
                       4: '0091',
                       5: '00B1',
                       6: '00D1',
                       7: '00F1',
                       8: '0111',
                       9: '0131',
                      10: '0151',
                      11: '0171',
                      12: '0191',
                      13: '01B1',
                      14: '01D1',
                      15: '01F1'  }
        ITank_RX1 = ('0055' + tank_to_REG[ICodes_ITanks[0]])
        ITank_RX2 = ('0069' + tank_to_REG[ICodes_ITanks[1]])
        ITank_RX3 = ('007D' + tank_to_REG[ICodes_ITanks[2]])
        Enable_RX1 = '00580110'
        Enable_RX2 = '006C0110'
        Enable_RX3 = '00800110'

        ICode_RX1 = ('0059005' + str(ICodes_ITanks[3]))
        ICode_RX2 = ('006D005' + str(ICodes_ITanks[4]))
        ICode_RX3 = ('0081005' + str(ICodes_ITanks[5]))

        Cmd_list = [ITank_RX1, Enable_RX1, ITank_RX2, Enable_RX2, ITank_RX3, Enable_RX3, ICode_RX1, ICode_RX2, ICode_RX3]
        return Cmd_list

class RXControl():
    _block_select_table = dict(enumerate(
        (
        (0b001, 0b010),
        (0b010, 0b100),
        (0b100, 0b001),
        (0b001, 0b001),
        (0b010, 0b001),
        (0b100, 0b010),
        (0b001, 0b100),
        (0b010, 0b010),
        (0b100, 0b100),
        )
    ))
    @classmethod
    def rewriteMuxConfig(cls, open_RX:int, **kwargs)->None:
        '''
        param:

            open_RX: 4 bit integer map to S2P channel source selection
            {ch2 enable ,ch1 enable ,ch0 enable}, ex. 0b000: all off.

            AI_mux: 4 bit integer map to select two channel data.

            tracking_mux: 4 bit integer map to select two channel data.

        '''
        # get enable block select number
        block_select =[]
        for k , v in cls._block_select_table.items():
            if open_RX | (v[0] | v[1]) == open_RX:
                block_select.append(k)

        AI_mux = kwargs.get('AI_mux', False)
        tracking_mux = kwargs.get('tracking_mux', False)

        # set default mux
        if open_RX == 0b101:
            if AI_mux is False:
                AI_mux = 6
            if tracking_mux is False:
                tracking_mux = 6
        elif open_RX == 0b110:
            if AI_mux is False:
                AI_mux = 1
            if tracking_mux is False:
                tracking_mux = 1
        elif open_RX == 0b100:
            if AI_mux is False:
                AI_mux = 8
            if tracking_mux is False:
                tracking_mux = 8
        elif open_RX == 0b111:
            if AI_mux is False:
                AI_mux = 0
            if tracking_mux is False:
                tracking_mux = 8
        else:
            raise Exception('Open RX mode is not enable !')

        assert (AI_mux in block_select),'input AI_mux = {} is not available!'.format(AI_mux)
        assert (tracking_mux in block_select),'input tracking_mux = {} is not available!'.format(tracking_mux)

        # set tracking enable = number of open RX
        tracking_enable = kwargs.get('tracking_enable', False)
        if not tracking_enable:
            tracking_enable = (open_RX & 0b1) + ((open_RX>>1) & 0b1) +((open_RX>>2) & 0b1 )

        # set dim select
        dim_sel = kwargs.get('dim_sel', False)
        if not dim_sel:
            dim_sel = tracking_enable - 1

        # if TDD mode must enable all RX and dim_sel = 3
        if  kgl.ksoclib.readReg(0x50000548, 8, 8) and dim_sel==2:
            dim_sel += 1

        # set channel valid
        Ch_valid = kwargs.get('Ch_valid', False)
        if not Ch_valid:
            Ch_valid = open_RX

        DigiController.setMUXParam(AIMux=AI_mux, TrackingMux=tracking_mux, Dim_sel=dim_sel, CH_valid=Ch_valid)
        kgl.ksoclib.writeReg(tracking_enable, 0x50000534, 6, 4)
        DigiController.getMuxParam()

    @classmethod
    def enableRFRX(cls, open_RX1=True, open_RX2=True, open_RX3=True):
        '''
        RFIC RX enable.

        '''
        RFController.enableRX('RX1', open_RX1)
        RFController.enableRX('RX2', open_RX2)
        RFController.enableRX('RX3', open_RX3)

        open_RX = 0b111
        if not open_RX1:
            # Disable RX1
            open_RX = open_RX^0b001

        if not open_RX2:
            # Disable RX2
            open_RX = open_RX^0b010

        if not open_RX3:
            # Disable RX3
            open_RX = open_RX^0b100


        print('open_RX1: {}, open_RX2: {}, open_RX3: {}'.format(open_RX1, open_RX2, open_RX3))
        return open_RX

def val2vallist(bitsMap, val, signlist):
    val_list = []
    bin_val = bin(val).split('0b')[1].zfill(32)
    rev_bin_val = bin_val[::-1]
    for i in range(len(bitsMap)):
        bit_len = bitsMap[i][0]
        rev_v = rev_bin_val[bitsMap[i][1]:bitsMap[i][1] + bitsMap[i][0]]
        v = int(rev_v[::-1], 2)
        if signlist[i] in ['$UNSG32', '$UNSG33']:
            val_list.append(v)

        elif signlist[i] == '$SIGN32':
            if v >= 0 and v < 2 ** (bit_len - 1):
                val_list.append(v)
            else:
                val_list.append(v - 2 ** bit_len)
    return val_list

def sign2unsign(x, bit):
    '''
    return unsign-extend value.

    Parameters:
            NA.
    Returns:
            (y) : a integer between 0~2^bit
    '''
    if x < 0:
        y = x + 2 ** bit
    elif x >= 2 ** bit:
        y = x - 2 ** bit
    else:
        y = x
    return y

if __name__ == '__main__':
    kgl.setLib()
    kgl.ksoclib.connectDevice()
    for AI_mux in range(9):
        for tracking_mux in range(9):
            for openRX1 in (True, False):
                for openRX2 in (True, False):
                    for openRX3 in (True, False):
                        print( '# ========= test =====================================' )
                        kgl.ksoclib.resetDevice()
                        try:
                            open_RX = RXControl.enableRFRX(openRX1,openRX2,openRX3)
                            RXControl.rewriteMuxConfig(open_RX, AI_mux=AI_mux, tracking_mux=tracking_mux)
                            p = PhaseCalibration()
                            p.calibrate()
                        except Exception as error:
                            print(error)
    print('end')
    pass