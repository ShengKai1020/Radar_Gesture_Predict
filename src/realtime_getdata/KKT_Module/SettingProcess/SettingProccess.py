import atexit
import time
from threading import Thread
from abc import ABCMeta, abstractmethod
from KKT_Module.ksoc_global import kgl
from KKT_Module.Configs import SettingConfigs
from KKT_Module.SettingProcess.PhaseCalibration import PhaseCalibration
from KKT_Module.SettingProcess.sic_func import runSIC
from KKT_Module.SettingProcess.ExeclParsing import KsocExcelParser, ParamDictGenerator
from KKT_Module.SettingProcess.ProcessList import ProcessListGenerator
from KKT_Module.SettingProcess.ScriptSetting import ScriptSetter
from KKT_Module.KKTUtility.H5Tool import KKTH5Tool
import os
import pyqtgraph

class ProcessComponent(metaclass=ABCMeta):
    def __init__(self):
        self.config = None
        pass

    @abstractmethod
    def startUp(self, config:SettingConfigs):
        '''
        Start process.
        :param config: import setting config from KKTLibInterface.py
        '''
        self.config = config
        print("\n# ======= Run {} process =======".format(self.__class__.__name__))
        kgl.ksoclib.outputDebugview("// ======= Run {} process =======".format(self.__class__.__name__),
                                    True)
        pass

    @abstractmethod
    def showInfo(self):...

class ProcessComposite(ProcessComponent):
    def __init__(self):
        super(ProcessComposite, self).__init__()
        self.process_list = []
        self.processes_dict = {}
        self.process = ''

    def addProcess(self,process_name,  process:ProcessComponent):
        self.processes[process_name] = process

    def removeProcess(self, process_name):
        self.processes.pop(process_name)

    def startUp(self, config:SettingConfigs):
        '''
        Start setting order to Process List.

        :param config: import setting config from KKTLibInterface.py
        '''
        super(ProcessComposite, self).startUp(config)
        print('process :{}'.format(self.process_list))
        # try:
        for process in self.process_list:
            self.process = process
            self.processes_dict.get(process).startUp(config)
        # except Exception as error:
        #     print(error)
        #     return

    def setConfig(self, config):
        self.config = config

# Setting process class

class SettingProc(ProcessComposite):
    def __init__(self):
        super(SettingProc, self).__init__()
        atexit.register(self.__cleanupFunction)
        self.current_percent = 0
        self.current_process = ''
        self.processes_dict={'Connect Device' : ConnectDevice(),
                             'Reset Device' : ResetDevice(),
                             'Phase Calibration' : CalibratePhase(),
                             'Script Setting' : SetScript(),
                             'Gen Process Script': GenProcessScript(),
                             'Gen Param Dict' : GetParamDict(),
                             'Set Script' : SetScript(),
                             'Run SIC' : RunSIC(),
                             'Modulation On' : ModulationOn(),
                             'Get Gesture Dict' : GenGestureDict(),
                             }

        self.percentage_dict = {
            'Reset Device' : [0,1],
            'Gen Process Script': [1,2],
            'Gen Param Dict' : [2,3],
            'Get Gesture Dict' : [3,4],
            'Set Script' : [4,97],
            'Phase Calibration' : [97,98],
            'Run SIC' : [98,99],
            'Modulation On' :[99,100]
            }
        self.process_list = list(self.processes_dict.keys())

    def startUp(self, config):
        assert config.ScriptDir.get('Script_path') is not None, 'Please set the script path'
        self.process_list = config.Processes
        self.current_percent = 0
        # self.total_percentage = 0
        # for process in self.process_list:
        #     self.total_percentage = self.total_percentage + self.percentage_dict[process]
        super(SettingProc, self).startUp(config)

    def getProgress(self):
        process = self.process
        progress = self.processes_dict.get(self.process)
        if progress is None:
            return None
        progress = progress.progress
        if progress is None:
            return None
        s = self.percentage_dict.get(self.process)[0]
        e = self.percentage_dict.get(self.process)[1]
        percentage = s + int((e - s) * progress[0] / progress[1])
        return process, progress, percentage

    def __cleanupFunction(self):
        print('KsocSettingProc cleanupFunction')
        self.__closeDevice()

    def __closeDevice(self):
        if kgl.ksoclib != None:
            kgl.ksoclib.closeCyDevice()
            # kgl.ksoclib = None
            print("Stop ksoc lib...")

    def startSetting(self,config):
        '''Start setting process in a subthread.'''
        arg = (config ,)
        T = Thread(target=self.startUp, args=arg)
        T.start()

    def showInfo(self):...

# Process Class
class ConnectDevice(ProcessComponent):
    '''
    Connect to the Device.
    '''
    def __init__(self):
        super(ConnectDevice, self).__init__()
        self._device = ''
        self.progress = None

    def startUp(self, config=None):
        super(ConnectDevice, self).startUp(config)
        self.progress = [0,1]
        self._device= kgl.ksoclib.connectDevice()
        print('# -Device was connected')
        try:
            FW_ver = kgl.ksoclib.getFWVersion()
        except:
            FW_ver = None

        try:
            IC_info = kgl.ksoclib.getChipID().strip().split(' ')
        except:
            IC_info = None
        self.progress[0] = 1
        return self._device, FW_ver, IC_info

    def showInfo(self):
        print('Connect to {}'.format(self._device))

class ResetDevice(ProcessComponent):
    '''
    Reset hardware register.
    '''
    def __init__(self):
        super(ResetDevice, self).__init__()
        self.progress = None

    def startUp(self,config=None):
        super(ResetDevice, self).startUp(config)
        self.progress = [0, 1]
        if kgl.ksoclib.rficRegRead(0x0029) == 0x40FE:
            kgl.ksoclib.switchModulationOn(False)
            print('Modulation off')
        kgl.ksoclib.resetDevice()
        kgl.ksoclib.connectDevice()
        # kgl.ksoclib.regWrite(0x50000030, [0x80010000])
        self.progress[0] = 1
        print('# -Device was reseted')

    def showInfo(self):
        print('Device Reseted')

class CalibratePhase(ProcessComponent):
    '''
    Do the phase calibration.


    '''
    def __init__(self):
        super(CalibratePhase, self).__init__()
        self.progress = None

    def startUp(self, config=None):
        super(CalibratePhase, self).startUp(config)
        s = time.time()
        from KKT_Module.KKTUtility.RFControl import RFController
        from KKT_Module.SettingProcess.PhaseCalibration import PhaseCalibration, RXControl
        RFController = RFController()
        self.progress = [0, 1]
        PhaseK = PhaseCalibration(config)
        if config.PhaseK.OpenRXByScript:
            RX_enable = RFController.getOpenedRX()
            open_RX = RXControl.enableRFRX(open_RX1=RX_enable['RX1'],
                                           open_RX2=RX_enable['RX2'],
                                           open_RX3=RX_enable['RX3']
                                           )
        else:
            open_RX = RXControl.enableRFRX(open_RX1=config.PhaseK.OpenRX1,
                                           open_RX2=config.PhaseK.OpenRX2,
                                           open_RX3=config.PhaseK.OpenRX3,
                                           )
        RXControl.rewriteMuxConfig(open_RX)
        PhaseK.calibrate()
        PhaseK.updateRFConfig(config.PhaseKConfigs)
        self.progress[0] = 1
        print('phase calibration {}s'.format(time.time() - s))

    def showInfo(self):...

class ModulationOn(ProcessComponent):
    '''
    Modulation on.
    '''
    def __init__(self):
        super(ModulationOn, self).__init__()
        self._name = 'Modulatio On'
        self.progress = None

    def startUp(self, config=None):
        super(ModulationOn, self).startUp(config)
        self.progress = [0, 1]
        if config.ModulationOn.Enable:
            config.ModulationOn.Status = False
            kgl.ksoclib.rficRegWrite(addr=0x0029, val=0x40FE)
            time.sleep(0.3)
            result = kgl.ksoclib.rficRegRead(0x0029)
            config.ModulationOn.Status = False
            assert result == 0x40FE, 'Modulation on failed !'
            config.ModulationOn.Status = True
        self.progress[0] = 1
        print('# -Modulation on : {}'.format(config.ModulationOn.Status))

    def showInfo(self):
        print('Modulation on = {}'.format(self.config.ModulationOn.Status))

class SetScript(ProcessComponent):
    '''
    Set RF, AI and hardware setting by setting script.
    '''
    def __init__(self):
        super(SetScript, self).__init__()
        self.progress = None
        from KKT_Module.KKTUtility.RFControl import RFController
        self.RFController = RFController()


    def startUp(self, config=None):
        super(SetScript, self).startUp(config)
        s = time.time()
        SS = ScriptSetter()
        self.progress = SS.process
        if config.RFSetting.Enable:
            self.RFController.enableRX('RX1', True)
            self.RFController.enableRX('RX2', True)
            self.RFController.enableRX('RX3', True)
        SS.configByDevice(script_path=config.ScriptDir.get('Script_path'),
                          procList=config.ProcList,
                          write_AI=config.AIWeight.Enable,
                          write_RF=config.RFSetting.Enable)

        print('set config {}s'.format(time.time() - s))

    def showInfo(self):...

class GenProcessScript(ProcessComponent):
    '''
    Generate setting process script.
    '''
    def __init__(self):
        super(GenProcessScript, self).__init__()
        self.progress = None

    def startUp(self, config=None):
        super(GenProcessScript, self).startUp(config)
        s = time.time()
        self.progress = [0, 1]
        exl_file_name = config.ScriptDir.get('Hardware_excel')
        txt_file_name = config.ScriptDir.get('Hardware_text')
        PLG = ProcessListGenerator()
        if exl_file_name is None:
            assert txt_file_name is not None, 'Empty script file !'
            txt_file_name = txt_file_name
            assert os.path.isfile(txt_file_name), 'File not found !'
            config.ProcList = PLG.readProcListFromFile(txt_file_name)
        else:
            exl_file_name = exl_file_name
            assert os.path.isfile(exl_file_name), 'File not found !'
            config.Sheet_param = KsocExcelParser.parsing(exl_file_name)
            config.ProcList = PLG.genProcessList(config.Sheet_param)
            if config.GenScript.SaveTextScript:
                paramname = os.path.basename(exl_file_name)
                paramname = paramname.split(".")
                paramname.pop(-1)
                paramname.insert(0, 'param_')
                paramname.append('.txt')
                paramname = ''.join(paramname)
                paramdir = os.path.join(kgl.KKTTempParam, config.ScriptDir['Script_path'], 'param')
                paramfile = os.path.join(paramdir, paramname)
                if not os.path.isdir(paramdir):
                    os.makedirs(paramdir)
                PLG.saveProcListToFile(filepath=paramfile, proclist=config.ProcList)
        self.progress[0] = 1
        print('Gen Process script {}s'.format(time.time() - s))

    def showInfo(self):...

class GenGestureDict(ProcessComponent):
    '''
    Get gesture mapping dictionary for Ai weight H5 file.
    '''
    def __init__(self):
        super(GenGestureDict, self).__init__()
        self.progress = None

    def startUp(self, config=None):
        super(GenGestureDict, self).startUp(config)
        s = time.time()
        self.progress = [0, 1]
        assert config.ScriptDir.get('AIweight_h5') is not None, 'Empty AIweight H5 file !'
        mapping_dicts = KKTH5Tool.getGestureDict(config.ScriptDir['AIweight_h5'])

        if mapping_dicts.get('Mapping_dict_Core') is None:
            assert mapping_dicts.get('Mapping_dict') is not None,'Empty Core Gestures !'
            config.CoreGestures = mapping_dicts.get('Mapping_dict')
        else:
            config.CoreGestures = mapping_dicts.get('Mapping_dict_core')
        config.SiameseGestures = mapping_dicts.get('Mapping_dict_siamese')
        print('Core Gestures dictionary :', config.CoreGestures)
        print('Siamese Gestures dictionary :', config.SiameseGestures)
        self.progress[0] = 1
        print('Get Gesture dict {}s'.format(time.time() - s))

    def showInfo(self):...

class GetParamDict(ProcessComponent):
    '''
    Generate hardware setting parameter dictionary from excel or text file.
    '''
    def __init__(self):
        super(GetParamDict, self).__init__()
        self.progress = None

    def startUp(self, config=None):
        super(GetParamDict, self).startUp(config)
        s = time.time()
        self.progress = [0, 1]
        PDG = ParamDictGenerator(kgl.KKTConfig + r'/HW_setting.json')
        config.ParamDict = PDG.writeRegVal(config.ProcList)
        self.progress[0] = 1
        print('Gen param dict {}s'.format(time.time() - s))

    def showInfo(self):...

class RunSIC(ProcessComponent):
    '''
    Set SIC setting and trigger.
    '''
    def __init__(self):
        super(RunSIC, self).__init__()
        self.progress = None

    def startUp(self, config=None):
        super(RunSIC, self).startUp(config)
        s = time.time()
        self.progress = [0, 1]
        SIC_trigger = kgl.ksoclib.getRFSICEnableStatus()
        print("RF SIC Open : {}".format(SIC_trigger))
        config.SIC.SIC_open = SIC_trigger
        # SIC_trigger = False
        runSIC(SIC_trigger, config)
        self.progress[0] = 1
        print('SIC trigger {}s'.format(time.time() - s))

    def showInfo(self):...


def main():

    exl_file_name = r"kkt60SOCA1_2D_SIC_RX13_32chirp_Dongle.xlsx"
    sheet_param = KsocExcelParser.parsing(exl_file_name)
    PLG = ProcessListGenerator()
    # ProcList = PLG.genProcessList(sheet_param)
    ProcList = PLG.readProcListFromFile('param_kkt60SOCA1_2D_SIC_RX13_32chirp_Dongle.txt')
    KsocHWsetting = ParamDictGenerator('HW_setting.json')
    param_dict = KsocHWsetting.writeRegVal(ProcList)
    connect = ConnectDevice()
    connect.startUp()
    reset = ResetDevice()
    reset.startUp()

    s = time.time()
    SS = ScriptSetter()
    script_dir = r"\SettingProcess\K60168-Release-60000-001-v1.2.0-20210504"
    SS.configByDevice(script_path=script_dir, procList=ProcList)
    print('set config {}s'.format(time.time()-s))
    s = time.time()
    pc = PhaseCalibration()
    pc.calibrate()
    print('phase calibration {}s'.format(time.time() - s))

    s = time.time()
    runSIC()
    print('run SIC {}s'.format(time.time() - s))

    modulation = ModulationOn()
    modulation.startUp()

if __name__ == '__main__':
    kgl.setLib()
    ksp = SettingProc()
    c = ConnectDevice()
    c.startUp()
    input('[Device Connected] Press any key to continue !')
    setting_config = SettingConfigs()
    setting_config.setScriptDir('K60168-Release-60000-001-v1.3.0-rc0-20210624')
    ksp.startUp(setting_config)











