from KKT_Module.ksoc_global import kgl
import os
import platform
import sys
import glob
import numpy as np
import re
import configparser

class INIConfigs:
    '''
    For parsing ini file.
    '''
    BOOLEAN_STATES = {'1': True, 'yes': True, 'true': True, 'on': True, 'y': True,
                      '0': False, 'no': False, 'false': False, 'off': False, 'n': False,}
    class MyConfigParser(configparser.ConfigParser):
        def optionxform(self, optionstr: str) -> str:
            return optionstr
    def __init__(self, filename):
        self.config = self.MyConfigParser()
        self.config.read(filename, encoding="utf-8")
        self.section = self.config.sections()
        pass
    def setConfigs(self):
        for k,v in self.config['CONFIGS'].items():
                self.__setattr__(k.lower(), v)

class SettingConfigs:
    '''
    Configs generated or need for init in Script setting process .

    '''
    # LogMode = {'Isprint':False, 'DebugView':False, 'OutputToFile':False}
    Processes = [
        'Reset Device',
        'Gen Process Script',
        'Gen Param Dict', 'Get Gesture Dict',
        'Set Script',
        'Phase Calibration',
        'Run SIC',
        'Modulation On'
    ]
    ScriptDir = {'Script_path' : None,
                 'Hardware_excel' : None,
                 'Hardware_text' : None,
                 'RF_setting' : None,
                 'AIweight_h5': None,
                 'AIweight_coe': None,
                 'AIweight_bin': None,
                 }
    SheetParam = None
    ProcList = []
    ParamDict = {}
    CoreGestures = {}
    SiameseGestures = {}
    # Debounce = False
    Firmware = ''
    Tool = ''
    PhaseKConfigs={}

    class SIC:
        isDebug = False
        SIC_from_DSP_dict = True
        SIC_open = False

    class AIWeight:
        Enable = True

    class Connect:...

    class PhaseK:
        # Phase calibrate
        OpenRX = 'RX123'
        OpenRXByScript = True
        OpenRX1 = True
        OpenRX2 = True
        OpenRX3 = True

    class HardwareSetting:
        Ai_MUX= None
        Tracking_MUX = None
        Ch_valid = None

    class RFSetting:
        Enable = True
        Enable_RX1 = False
        Enable_RX2 = False
        Enable_RX3 = False

    class ModulationOn:
        Enable = True
        Status = False

    class GenScript:
        SaveTextScript = True

    def __init__(self, **kwargs):
        self.SIC = self.SIC()
        self.AIWeight = self.AIWeight()
        self.Connect = self.Connect()
        self.PhaseK = self.PhaseK()
        self.HardwareSetting = self.HardwareSetting()
        self.RFSetting = self.RFSetting()
        self.ModulationOn =self.ModulationOn()
        self.GenScript = self.GenScript()

    @classmethod
    def setDefaultParamDict(cls):
        txt_file_name = os.path.join(kgl.KKTConfig, 'Default_Param.txt')
        if not os.path.isfile(txt_file_name):
            print("No Default param")
            return
        from KKT_Module.SettingProcess.ProcessList import ProcessListGenerator
        from KKT_Module.SettingProcess.ExeclParsing import ParamDictGenerator

        PLG = ProcessListGenerator()
        PDG = ParamDictGenerator(kgl.KKTConfig + r'/HW_setting.json')
        ProcList = PLG.readProcListFromFile(txt_file_name)
        cls.ParamDict = PDG.writeRegVal(ProcList)
        pass

    @classmethod
    def setScriptDir(cls, script_name):
        '''
        Get all file's path in Hardware setting folder.

        :param script_path: Hardware setting folder name.
        '''
        for k in cls.ScriptDir.keys():
            cls.ScriptDir[k] = None
        script_path = os.path.join(kgl.KKTTempParam, script_name)
        print('Script Path : {}'.format(script_path))
        assert os.path.isdir(script_path),'Script folder not found !'
        cls.ScriptDir['Script_path'] = script_path

        HW_excel_path = os.path.join(script_path)
        HW_excel = glob.glob(os.path.join(HW_excel_path , '*.xlsx'))
        if len(HW_excel) != 0:
            cls.ScriptDir['Hardware_excel'] = HW_excel[0]

        HW_text_path = os.path.join(script_path, 'param')
        HW_text = glob.glob(HW_text_path + '/*.txt')
        if len(HW_text) != 0:
            cls.ScriptDir['Hardware_text'] = HW_text[0]

        weight_h5_path = os.path.join(script_path, 'ai_acc_weight', 'sram_h5')
        weight_h5 = glob.glob(weight_h5_path + '/*.h5')
        if len(weight_h5) != 0:
            cls.ScriptDir['AIweight_h5'] = weight_h5[0]

        weight_coe_path = os.path.join(script_path, 'ai_acc_weight', 'sram_coe')
        weight_coe = glob.glob(weight_coe_path + '/*.coe')
        if len(weight_coe) != 0:
            cls.ScriptDir['AIweight_coe'] = weight_coe

        RF_text_path = os.path.join(script_path, 'Integration_Test_script', 'SOCA')
        RF_text = glob.glob(RF_text_path + '/*.txt')
        if len(RF_text) != 0:
            cls.ScriptDir['RF_setting'] = RF_text[0]

        RF_bin_path = os.path.join(script_path, 'Integration_Test_script', 'SOCA')
        RF_bin = glob.glob(RF_bin_path + '/*.bin')
        if len(RF_bin) != 0:
            cls.ScriptDir['RF_setting'] = RF_bin[0]
        # import pprint
        # pprint.pprint(cls.ScriptDir,)
        pass


    def genDSPConfigs(self):
        assert self.ParamDict is not None, "DSP config hasn't been set !"
        d625k_u0_reg_AICctrl0_param0 = self.ParamDict['DSPRx625K_Unit_0']['0x400B0088']
        d625k_u0_reg_AICctrl1_param0 = self.ParamDict['DSPRx625K_Unit_0']['0x400B00A8']
        d625k_u1_reg_AICctrl0_param0 = self.ParamDict['DSPRx625K_Unit_1']['0x40090088']
        d625k_u1_reg_AICctrl1_param0 = self.ParamDict['DSPRx625K_Unit_1']['0x400900A8']

        # AIC_outputShiftNum
        DSPRx625K_Uint_0_REG_AICctrl0_param0_outputShiftNum = d625k_u0_reg_AICctrl0_param0[3]['outputShiftNum']
        DSPRx625K_Uint_0_REG_AICctrl1_param0_outputShiftNum = d625k_u0_reg_AICctrl1_param0[3]["outputShiftNum"]
        DSPRx625K_Uint_1_REG_AICctrl0_param0_outputShiftNum = d625k_u1_reg_AICctrl0_param0[3]["outputShiftNum"]
        DSPRx625K_Uint_1_REG_AICctrl1_param0_outputShiftNum = d625k_u1_reg_AICctrl1_param0[3]["outputShiftNum"]
        arr = np.array(
            [DSPRx625K_Uint_0_REG_AICctrl0_param0_outputShiftNum, DSPRx625K_Uint_0_REG_AICctrl1_param0_outputShiftNum,
             DSPRx625K_Uint_1_REG_AICctrl0_param0_outputShiftNum, DSPRx625K_Uint_1_REG_AICctrl1_param0_outputShiftNum])
        result = np.all(arr == arr[0])
        assert result,"Warning: Uint{0,1} REG_AICctrl0_param0_outputShiftNum ~= REG_AICctrl1_param0_outputShiftNum"
        AIC_outputShiftNum = DSPRx625K_Uint_0_REG_AICctrl0_param0_outputShiftNum

        # chirp num
        DSPRx625K_Uint_0_REG_symbolPerFrm = d625k_u0_reg_AICctrl0_param0[3]["symbolPerFrm"]
        DSPRx625K_Uint_1_REG_symbolPerFrm = d625k_u1_reg_AICctrl0_param0[3]["symbolPerFrm"]
        DSPRx625K_Uint_0_REG_symbolPerFrm_user = d625k_u0_reg_AICctrl0_param0[3]["symbolPerFrm_user"]
        DSPRx625K_Uint_1_REG_symbolPerFrm_user = d625k_u1_reg_AICctrl0_param0[3]["symbolPerFrm_user"]
        assert DSPRx625K_Uint_0_REG_symbolPerFrm == DSPRx625K_Uint_1_REG_symbolPerFrm,\
            "Warning: Uint{0,1} REG_symbolPerFrm ~= REG_symbolPerFrm"
        assert DSPRx625K_Uint_0_REG_symbolPerFrm_user == DSPRx625K_Uint_1_REG_symbolPerFrm_user,\
            "Warning: Uint{0,1} REG_symbolPerFrm_user ~= REG_symbolPerFrm_user"
        chirp_num = 0
        if DSPRx625K_Uint_0_REG_symbolPerFrm == 0:
            chirp_num = 16
        elif DSPRx625K_Uint_0_REG_symbolPerFrm == 1:
            chirp_num = 32
        elif DSPRx625K_Uint_0_REG_symbolPerFrm == 2:
            chirp_num = 64
        elif DSPRx625K_Uint_0_REG_symbolPerFrm >= 3:
            chirp_num = DSPRx625K_Uint_0_REG_symbolPerFrm_user

        d20m_u0_REG_RDIGen0_param0 = self.ParamDict['DSPRx20M_Unit_0']['0x400D2008']
        d20m_u0_REG_RDIGen1_param0 = self.ParamDict['DSPRx20M_Unit_0']['0x400D6008']
        d20m_u1_REG_RDIGen0_param0 = self.ParamDict['DSPRx20M_Unit_1']['0x400F2008']
        d20m_u1_REG_RDIGen1_param0 = self.ParamDict['DSPRx20M_Unit_1']['0x400F6008']

        # Fast_time_sample
        DSPRx20M_Uint_0_REG_RDIGen0_param0_FT_sample = d20m_u0_REG_RDIGen0_param0[3]["FT_sample"]
        DSPRx20M_Uint_0_REG_RDIGen1_param0_FT_sample = d20m_u0_REG_RDIGen1_param0[3]["FT_sample"]
        DSPRx20M_Uint_1_REG_RDIGen0_param0_FT_sample = d20m_u1_REG_RDIGen0_param0[3]["FT_sample"]
        DSPRx20M_Uint_1_REG_RDIGen1_param0_FT_sample = d20m_u1_REG_RDIGen1_param0[3]["FT_sample"]
        arr = np.array([DSPRx20M_Uint_0_REG_RDIGen0_param0_FT_sample, DSPRx20M_Uint_0_REG_RDIGen1_param0_FT_sample,
                        DSPRx20M_Uint_1_REG_RDIGen0_param0_FT_sample, DSPRx20M_Uint_1_REG_RDIGen1_param0_FT_sample])
        result = np.all(arr == arr[0])
        assert result, "Warning: Uint{0,1} REG_RDIGen0_param0_FT_sample ~= REG_RDIGen1_param0_FT_sample"
        Fast_time_sample = None
        if DSPRx20M_Uint_0_REG_RDIGen0_param0_FT_sample == 0:
            Fast_time_sample = 64
        elif DSPRx20M_Uint_0_REG_RDIGen0_param0_FT_sample == 1:
            Fast_time_sample = 128

        # up_down_combining
        DSPRx20M_Uint_0_REG_RDIGen0_param0_upDownComb = d20m_u0_REG_RDIGen0_param0[3]["upDownComb"]
        DSPRx20M_Uint_0_REG_RDIGen1_param0_upDownComb = d20m_u0_REG_RDIGen1_param0[3]["upDownComb"]
        DSPRx20M_Uint_1_REG_RDIGen0_param0_upDownComb = d20m_u1_REG_RDIGen0_param0[3]["upDownComb"]
        DSPRx20M_Uint_1_REG_RDIGen1_param0_upDownComb = d20m_u1_REG_RDIGen1_param0[3]["upDownComb"]
        arr = np.array([DSPRx20M_Uint_0_REG_RDIGen0_param0_upDownComb, DSPRx20M_Uint_0_REG_RDIGen1_param0_upDownComb,
                        DSPRx20M_Uint_1_REG_RDIGen0_param0_upDownComb, DSPRx20M_Uint_1_REG_RDIGen1_param0_upDownComb])
        result = np.all(arr == arr[0])
        assert result, "Warning: Uint{0,1} REG_RDIGen0_param0_upDownComb ~= REG_RDIGen1_param0_upDownComb"
        upDownComb = DSPRx20M_Uint_0_REG_RDIGen0_param0_upDownComb

        # Slow_time_symbols
        DSPRx20M_Uint_0_REG_RDIGen0_param0_ST_SymbolCnt = d20m_u0_REG_RDIGen0_param0[3]["ST_SymbolCnt"]
        DSPRx20M_Uint_0_REG_RDIGen1_param0_ST_SymbolCnt = d20m_u0_REG_RDIGen1_param0[3]["ST_SymbolCnt"]
        DSPRx20M_Uint_1_REG_RDIGen0_param0_ST_SymbolCnt = d20m_u1_REG_RDIGen0_param0[3]["ST_SymbolCnt"]
        DSPRx20M_Uint_1_REG_RDIGen1_param0_ST_SymbolCnt = d20m_u1_REG_RDIGen1_param0[3]["ST_SymbolCnt"]
        arr = np.array(
            [DSPRx20M_Uint_0_REG_RDIGen0_param0_ST_SymbolCnt, DSPRx20M_Uint_0_REG_RDIGen1_param0_ST_SymbolCnt,
             DSPRx20M_Uint_1_REG_RDIGen0_param0_ST_SymbolCnt, DSPRx20M_Uint_1_REG_RDIGen1_param0_ST_SymbolCnt])
        result = np.all(arr == arr[0])
        assert result, "Warning: Uint{0,1} REG_RDIGen0_param0_ST_SymbolCnt ~= REG_RDIGen1_param0_ST_SymbolCnt"
        Slow_time_symbols = None
        if DSPRx20M_Uint_0_REG_RDIGen0_param0_ST_SymbolCnt == 0:
            Slow_time_symbols = 16
        elif DSPRx20M_Uint_0_REG_RDIGen0_param0_ST_SymbolCnt == 1:
            Slow_time_symbols = 32
        elif DSPRx20M_Uint_0_REG_RDIGen0_param0_ST_SymbolCnt == 2:
            Slow_time_symbols = 64

        # Slow_time_conv2polar_GainShift
        DSPRx20M_Uint_0_REG_RDIGen0_param0_con2PolarGainShift = d20m_u0_REG_RDIGen0_param0[3]["con2PolarGainShift"]
        DSPRx20M_Uint_0_REG_RDIGen1_param0_con2PolarGainShift = d20m_u0_REG_RDIGen1_param0[3]["con2PolarGainShift"]
        DSPRx20M_Uint_1_REG_RDIGen0_param0_con2PolarGainShift = d20m_u1_REG_RDIGen0_param0[3]["con2PolarGainShift"]
        DSPRx20M_Uint_1_REG_RDIGen1_param0_con2PolarGainShift = d20m_u1_REG_RDIGen1_param0[3]["con2PolarGainShift"]
        arr = np.array([DSPRx20M_Uint_0_REG_RDIGen0_param0_con2PolarGainShift,
                        DSPRx20M_Uint_0_REG_RDIGen1_param0_con2PolarGainShift,
                        DSPRx20M_Uint_1_REG_RDIGen0_param0_con2PolarGainShift,
                        DSPRx20M_Uint_1_REG_RDIGen1_param0_con2PolarGainShift])
        result = np.all(arr == arr[0])
        assert result, "Warning: Uint{0,1} REG_RDIGen0_param0_con2PolarGainShift ~= REG_RDIGen1_param0_con2PolarGainShift"
        con2PolarGainShift = DSPRx20M_Uint_0_REG_RDIGen0_param0_con2PolarGainShift

        d20m_u0_REG_phaseMap_ctrl0 = self.ParamDict['DSPRx20M_Unit_0']['0x400D8018']
        d20m_u1_REG_phaseMap_ctrl0 = self.ParamDict['DSPRx20M_Unit_1']['0x400F8018']
        # PHD
        # phasemap_ctrl_enable
        DSPRx20M_Uint_0_REG_phaseMap_ctrl0 = d20m_u0_REG_phaseMap_ctrl0[3]["Enable"]
        DSPRx20M_Uint_1_REG_phaseMap_ctrl0 = d20m_u1_REG_phaseMap_ctrl0[3]["Enable"]
        arr = np.array([DSPRx20M_Uint_0_REG_phaseMap_ctrl0, DSPRx20M_Uint_1_REG_phaseMap_ctrl0])
        result = np.all(arr == arr[0])
        assert result,"Warning: Uint{0,1} REG_phaseMap_ctrl0 ~= REG_phaseMap_ctrl0"
        phaseMap_enable = DSPRx20M_Uint_0_REG_phaseMap_ctrl0

        d20m_u0_REG_phaseMap_param0 = self.ParamDict['DSPRx20M_Unit_0']['0x400D801C']
        d20m_u1_REG_phaseMap_param0 = self.ParamDict['DSPRx20M_Unit_1']['0x400F801C']
        # conv2polar_gain_RDI
        DSPRx20M_Uint_0_REG_gainRDI = d20m_u0_REG_phaseMap_param0[3]["gainRDI"]
        DSPRx20M_Uint_1_REG_gainRDI = d20m_u1_REG_phaseMap_param0[3]["gainRDI"]
        arr = np.array([DSPRx20M_Uint_0_REG_gainRDI, DSPRx20M_Uint_1_REG_gainRDI])
        result = np.all(arr == arr[0])
        # assert result, "Warning: Uint{0,1} REG_gainRDI ~= REG_gainRDI"
        conv2polar_gain_RDI = DSPRx20M_Uint_0_REG_gainRDI

        # conv2polar_gain_PhaseFFT
        DSPRx20M_Uint_0_REG_gainPhaseFFT = d20m_u0_REG_phaseMap_param0[3]["gainPhaseFFT"]
        DSPRx20M_Uint_1_REG_gainPhaseFFT = d20m_u1_REG_phaseMap_param0[3]["gainPhaseFFT"]
        arr = np.array([DSPRx20M_Uint_0_REG_gainPhaseFFT, DSPRx20M_Uint_1_REG_gainPhaseFFT])
        result = np.all(arr == arr[0])
        # assert result,"Warning: Uint{0,1} REG_gainPhaseFFT ~= REG_gainPhaseFFT"
        conv2polar_gain_PhaseFFT = DSPRx20M_Uint_0_REG_gainPhaseFFT

        # n_c
        if phaseMap_enable == 0:
            RDI_nc = 15 - AIC_outputShiftNum - np.log2(Fast_time_sample / 2 ** upDownComb) - (
                        np.log2(Slow_time_symbols) + 1) - 1 + con2PolarGainShift
            kProcMap1_nc = RDI_nc
            kProcMap2_nc = RDI_nc
        elif phaseMap_enable == 1:
            RDI_nc = 15 - AIC_outputShiftNum - np.log2(Fast_time_sample / 2 ** upDownComb) - (
                        np.log2(Slow_time_symbols) + 1) - 1 + conv2polar_gain_RDI
            PHD_nc = 15 - AIC_outputShiftNum - np.log2(Fast_time_sample / 2 ** upDownComb) - (
                        np.log2(Slow_time_symbols) + 1) - np.log2(2) - 1 + conv2polar_gain_PhaseFFT
            kProcMap1_nc = RDI_nc
            kProcMap2_nc = PHD_nc

        # print('DSP Config = ', kProcMap1_nc, kProcMap2_nc, chirp_num)
        return kProcMap1_nc, kProcMap2_nc, chirp_num


    def getBackgroundID(self):
        for k, v in self.CoreGestures.items():
            if v == 'Background':
                return k
        return '-1'

    @classmethod
    def getScriptInfo(cls):
        ScriptDir = cls.ScriptDir.get('Script_path')
        assert ScriptDir is not None, 'Empty Script path !'
        ScriptDir = os.path.basename(ScriptDir)
        IC = 'K60168'
        ReleaseStatus= None
        CustomerID= 'xxxxx'
        SubCustomerID= 'xxx'
        ProductVer= 'vx.x.x'
        Date= None

        ScriptDir_list = str(ScriptDir).split('-')
        if ScriptDir_list[0] != IC:
            return IC, ReleaseStatus, CustomerID, SubCustomerID, ProductVer, Date

        CustomerID_re = re.compile('-(\d{5})-')
        if CustomerID_re.search(ScriptDir) is not None:
            CustomerID = CustomerID_re.search(ScriptDir).group(1)

        ProductVer_re = re.compile('v\d+\.\d+\.\d+')
        if ProductVer_re.search(ScriptDir) is not None:
            ProductVer = ProductVer_re.search(ScriptDir).group()

        SubCustomerID_re = re.compile('-(\d{3})-')
        if SubCustomerID_re.search(ScriptDir) is not None:
            SubCustomerID = SubCustomerID_re.search(ScriptDir).group(1)

        Date_re = re.compile('-(\d{7}\d$)')
        if Date_re.search(ScriptDir) is not None:
            Date = Date_re.search(ScriptDir).group(1)

        IC = ScriptDir_list[0]
        ReleaseStatus = ScriptDir_list[1]

        return IC, ReleaseStatus, CustomerID, SubCustomerID, ProductVer, Date

class RecordingConfigs:
    '''
    For h5 file data recording.
    '''
    DataConfigs = {'Record_frames': 100,
                    'Datatime': '',
                    'Description': 'Open->Close->Open',
                    'Diversity': 'Random',
                    'Minimum_gap':10,
                    'Duration':[20],
                    'Gesture_name': [],
                    'Hand_type': 'Left hand',
                    'Mode': 'Manual',
                    'Attr_file_name': 'General_model_record_attribute_manual.xlsx',
                    'Owner': 'Eric',
                    'Device': 'K60SOCA1',
                    'Data_format' : 'RawData',
                    }
    RFConfigs = {'RFIC':None,
                 'Chirps':None,
                 'SIC_opened':None,
                 'MUX':None,
                 }
    DSP_Configs={}
    AIC_Configs = {}
    AGC_Configs = {}
    PHD_Configs = {}
    RDI_Configs = {}
    Record_Folder = 'temp'
    DataType = 'RawData'

    def __init__(self,**kwargs):
        '''
        kwargs:
        'Record_frames', 'Datatime', 'Description',
        'Diversity', 'Duration', 'Gesture_name',
        'Hand_type', 'Mode', 'Attr_file_name',
        'Owner', 'Device', 'Data_format'
        '''
        self.setDataConfig(**kwargs)
        pass


    def setDataConfig(self, **kwargs):
        '''
        Update KProcFSM configs.

        :param kwargs: 'Record_frames','Datatime','Description',
                       'Diversity','Duration','Gesture_name',
                       'Hand_type','Mode','Attr_file_name',
                       'Owner','Device','Data_format'
        '''
        for k, v in kwargs.items():
            assert self.DataConfigs.get(k) is not None, 'No attribute "{}" in DataConfigs.'.format(k)
            self.DataConfigs[k] = v


    def initDataConfigs(self, setting_configs):
        visualize_configs = ''
        if setting_configs is not None:
            Hardware_excel = setting_configs.ScriptDir.get('Hardware_excel')
            Hardware_text = setting_configs.ScriptDir.get('Hardware_text')
            if Hardware_excel is None:
                assert Hardware_text is not None,'Empty hardware setting !'
                visualize_configs = os.path.basename(Hardware_text)
            else:
                visualize_configs = os.path.basename(Hardware_excel)

        self.DataConfigs['Visualize_config'] = visualize_configs

        self.DataConfigs['Version'] = 'Python ' + '.'.join([str(x) for x in [sys.version_info.major,
                                                                             sys.version_info.minor,
                                                                             sys.version_info.micro]])
        self.DataConfigs['Platform'] = platform.system() + ' ' + platform.release()
        self.DataConfigs['FW_version'] = kgl.ksoclib.getFWVersion()
        self.DataConfigs['Device'] = kgl.ksoclib.getChipID()
        if self.DataConfigs['Device'].split(' ')[0] != 'K60169A':
            self.DataConfigs['SN'] = kgl.ksoclib.getSN()
        else:
            self.DataConfigs['SN'] = ''


    def initDSPConfigs(self, setting_configs):
        if setting_configs is None:
            return
        Hardware_excel = setting_configs.ScriptDir.get('Hardware_excel')
        Hardware_text = setting_configs.ScriptDir.get('Hardware_text')

        if Hardware_excel is None:
            assert Hardware_text is not None,'Empty hardware setting! '
            visualize_configs = os.path.split(Hardware_text)[1]
            visualize_configs = visualize_configs.split('.')[0].split('param_')[1]
        else:
            visualize_configs = os.path.split(Hardware_excel)[1]
            visualize_configs = visualize_configs.split('.')[0]

        DSP_cfg = setting_configs.genDSPConfigs()
        self.DSP_Configs['Map1_nc'] =DSP_cfg[0]
        self.DSP_Configs['Map2_nc'] =DSP_cfg[1]
        self.DSP_Configs['Gen_Mode'] = 'BT'
        self.DSP_Configs['Hardware_excel'] = visualize_configs


    def initAGCConfigs(self, setting_configs):
        if setting_configs is None:
            return
        DSPRx20M_Unit_0 = setting_configs.ParamDict['DSPRx20M_Unit_0']

        self.AGC_Configs = {
            'alpha':DSPRx20M_Unit_0['0x400D804C'][3]['alpha'],
            'log_P_targ':DSPRx20M_Unit_0['0x400D8048'][3]['log_P_targ'],
            'AGC_bypass':DSPRx20M_Unit_0['0x400D8040'][3]['AGC_ByPass'],
            'AGC_fix_pt':0,
            'samples_per_ACC':DSPRx20M_Unit_0['0x400D8048'][3]['samples_per_acc'],
        }


    def initAICConfigs(self, setting_configs):
        if setting_configs is None:
            return
        chirp_period_dict = {0: 64, 1: 128}
        symbol_per_frame_dict = {0: 16, 1: 32, 2: 64, 3: 'user_define'}
        DSPRx625K_Unit_0 = setting_configs.ParamDict['DSPRx625K_Unit_0']
        DSP_Motion = setting_configs.ParamDict['DSP_Motion']

        AIC_symbol_per_frame = symbol_per_frame_dict[DSPRx625K_Unit_0['0x400B00A8'][3]['symbolPerFrm']]
        if symbol_per_frame_dict[DSPRx625K_Unit_0['0x400B00A8'][3]['symbolPerFrm']] == 'user_define':
            AIC_symbol_per_frame = DSPRx625K_Unit_0['0x400B00A8'][3]['symbolPerFrm_user']

        self.AIC_Configs = {
            'AIC_chirp_periodicity':chirp_period_dict[DSPRx625K_Unit_0['0x400B0088'][3]['chirp_period']],
            'AIC_chirp_log_num':DSPRx625K_Unit_0['0x400B0088'][3]['chirp_log_num'],
            'AIC_sync_delay':DSPRx625K_Unit_0['0x400B0088'][3]['syncOffset'],
            'AIC_Wstart':DSPRx625K_Unit_0['0x400B008C'][3]['W_starting'],
            'AIC_Wend':DSPRx625K_Unit_0['0x400B008C'][3]['W_end'],
            'AIC_symbol_per_frame':AIC_symbol_per_frame,
            'AIC_right_shift_num':DSPRx625K_Unit_0['0x400B0088'][3]['outputShiftNum'],
            'En_first_velocity_est':DSP_Motion['0x4005C08C'][3]['En_first_velocity_est'],
            'Vel_right_shift_num':DSP_Motion['0x4005C08C'][3]['Vel_right_shift_num'],
            'AIC_fix_pt':0
        }


    def initPHDConfigs(self, setting_configs):
        if setting_configs is None:
            return
        DSPRx20M_Unit_0 = setting_configs.ParamDict['DSPRx20M_Unit_0']

        self.PHD_Configs={
            'enable' : DSPRx20M_Unit_0['0x400D8018'][3]['Enable'],
            'Mode' : DSPRx20M_Unit_0['0x400D801C'][3]['mode'],
            'column' : DSPRx20M_Unit_0['0x400D801C'][3]['column'] + 1,
            'twiddle_table' : 0,
            'conv2polar_gain_RDI' : DSPRx20M_Unit_0['0x400D801C'][3]['gainRDI'],
            'conv2polar_gain_phaseFFT' : DSPRx20M_Unit_0['0x400D801C'][3]['gainPhaseFFT'],
            'PHD_fix_pt' : 0
        }


    def initRDIConfigs(self, setting_configs):
        if setting_configs is None:
            return
        Fast_time_sample_dict = {0: 64, 1: 128}
        Fast_downsample_ratio_dict = {0: 1, 1: 2}
        Slow_time_downsample_ratio_dict = {0: 1, 1: 2}
        Slow_time_symbols_dict = {0: 16, 1: 32, 2: 64}
        DSPRx20M_Unit_0 = setting_configs.ParamDict['DSPRx20M_Unit_0']
        self.RDI_Configs = {
            'Fast_time_sample' : Fast_time_sample_dict[DSPRx20M_Unit_0['0x400D2008'][3]['FT_sample']],
            'up_down_combining' : DSPRx20M_Unit_0['0x400D2008'][3]['upDownComb'],
            'Fast_time_start_point' : DSPRx20M_Unit_0['0x400D2008'][3]['FT_startPoint'],
            'Fast_downsample_ratio' : Fast_downsample_ratio_dict[DSPRx20M_Unit_0['0x400D2008'][3]['FT_downSampleRatio']],
            'Fast_time_conv2polar' : DSPRx20M_Unit_0['0x400D2008'][3]['FT_Con2Polar'],
            'Fast_time_post_FFT_comb_enable' : 0,
            'Slow_time_512FFT_ext' : DSPRx20M_Unit_0['0x400D2008'][3]['ST_512FFT_ext'],
            'Slow_time_symbols' : Slow_time_symbols_dict[DSPRx20M_Unit_0['0x400D2008'][3]['ST_SymbolCnt']],
            'Slow_time_downsample_ratio' : Slow_time_downsample_ratio_dict[DSPRx20M_Unit_0['0x400D2008'][3]['ST_downSampleRatio']],
            'Slow_time_conv2polar' : DSPRx20M_Unit_0['0x400D2008'][3]['ST_Con2Polar'],
            'Slow_time_conv2polar_gainshift' : DSPRx20M_Unit_0['0x400D2008'][3]['con2PolarGainShift'],
            'RDI_fix_pt' : 0,
            'Fast_time_rotate_vector_im_ch1': DSPRx20M_Unit_0['0x400D200C'][3]['FT_rot_vec_im'],
            'Fast_time_rotate_vector_re_ch1': DSPRx20M_Unit_0['0x400D200C'][3]['FT_rot_vec_re'],
            'Fast_time_rotate_vector_im_ch2': DSPRx20M_Unit_0['0x400D600C'][3]['FT_rot_vec_im'],
            'Fast_time_rotate_vector_re_ch2': DSPRx20M_Unit_0['0x400D600C'][3]['FT_rot_vec_re'],
        }


    def initRFConfigs(self, setting_configs:SettingConfigs):
        chirps = (kgl.ksoclib.rficRegRead(0x0026) & 0xFF) + 1
        mux = kgl.ksoclib.readReg(0x50000544, 3, 0, )
        if setting_configs is not None:
            RF_setting = setting_configs.ScriptDir.get('RF_setting')
            assert RF_setting is not None, 'Empty RF setting!'
            RF_setting = os.path.basename(RF_setting)
            SIC_opened = setting_configs.SIC.SIC_open
            self.RFConfigs.update(setting_configs.PhaseKConfigs)
        else:
            RF_setting = ''
            SIC_opened = kgl.ksoclib.getRFSICEnableStatus()


        self.RFConfigs['RFIC'] = RF_setting
        self.RFConfigs['Chirps'] = int(chirps)
        self.RFConfigs['SIC_opened'] = SIC_opened
        self.RFConfigs['MUX'] = int(mux)




def testSetting_configs():
    print('[Entry testSetting_configs]')
    print('[print main class]',SettingConfigs.SIC.SIC_open)
    SC1 = SettingConfigs()
    print('[print sub class SC1]',SC1.SIC.SIC_open)
    SC1.SIC.SIC_open = True
    print('[print main class]',SettingConfigs.SIC.SIC_open)
    print('[print sub class SC1]',SC1.SIC.SIC_open)
    SC2 = SettingConfigs()
    print('[print sub class SC2]',SC2.SIC.SIC_open)
    SC1 = SettingConfigs()
    print('[print sub class SC1]',SC1.SIC.SIC_open)
    SettingConfigs.SIC.SIC_open = True
    SC3 = SettingConfigs()
    print('[print sub class SC3]',SC3.SIC.SIC_open)
    # SC3.SIC.SIC_open = False
    print('[print main class]', SettingConfigs.SIC.SIC_open)
    print('[print sub class SC1]', SC1.SIC.SIC_open)
    print('[print sub class SC2]', SC2.SIC.SIC_open)
    print('[print sub class SC3]', SC3.SIC.SIC_open)

def testSetting_configs2():
    print('[Entry testSetting_configs]')
    print('[print main class]',SettingConfigs.Debounce)
    SC1 = SettingConfigs()
    print('[print sub class SC1]',SC1.Debounce)
    SC1.Debounce = True
    print('[print main class]',SettingConfigs.Debounce)
    print('[print sub class SC1]',SC1.Debounce)
    SC2 = SettingConfigs()
    print('[print sub class SC2]',SC2.Debounce)
    print('[print sub class SC1]', SC1.Debounce)
    SC1 = SettingConfigs()
    print('[print sub class SC1]',SC1.Debounce)
    SettingConfigs.Debounce = True
    SC3 = SettingConfigs()
    print('[print sub class SC3]',SC3.Debounce)
    # SC3.Debounce = False
    print('[print main class]', SettingConfigs.Debounce)
    print('[print sub class SC1]', SC1.Debounce)
    print('[print sub class SC2]', SC2.Debounce)
    print('[print sub class SC3]', SC3.Debounce)

if __name__ == '__main__':
    testSetting_configs()
    testSetting_configs2()