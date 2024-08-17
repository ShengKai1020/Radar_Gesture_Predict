from KKT_Module.ksoc_global import kgl

class ModeConfigs:
    '''
        Class for mode configs.
        configs:
            updater
            receiver
            user_level
            need_set_script
            description
    '''
    def __init__(self, receiver=None, updater=None, user_level=1, need_set_script=False, **kwargs):
        self.receiver = receiver
        self.updater = updater
        self.user_level = user_level
        self.need_set_script = need_set_script
        self.description = ''
        self.setConfigs(**kwargs)
        pass

    def setConfigs(self, **kwargs):
        for config, value in kwargs.items():
            assert hasattr(self, config)
            self.__setattr__(config, value)

    def getConfigs(self):
        return self.__dict__

    def setDescription(self, description):
        self.description = description

class ModeSelector():
    @classmethod
    def selectUpdater(clr, mode_config:ModeConfigs):
        updater = mode_config.updater
        print('updater={}'.format(updater))
        if updater == 'RawData':
            from KKT_Module.GuiUpdater.GuiUpdater import RawDataUpdater
            updater = RawDataUpdater()
        elif updater == 'HardwareInference':
            from KKT_Module.GuiUpdater.GuiUpdater import HardwareInferenceUpdater
            updater = HardwareInferenceUpdater()
        elif updater == 'Tracking':
            from KKT_Module.GuiUpdater.GuiUpdater import TrackingUpdater
            updater = TrackingUpdater()
        elif updater == 'FeatureMap':
            from KKT_Module.GuiUpdater.GuiUpdater import FeatureMapUpdater
            updater = FeatureMapUpdater()
        return updater

    @classmethod
    def selectReceiver(clr, mode_config:ModeConfigs):
        receiver = mode_config.receiver
        print('receiver={}'.format(receiver))
        if receiver == 'RawData':
            from KKT_Module.DataReceive.DataReciever import RawDataReceiver
            receiver = RawDataReceiver()
        elif receiver == 'FeatureMap':
            from KKT_Module.DataReceive.DataReciever import FeatureMapReceiver
            receiver = FeatureMapReceiver()
        elif receiver == 'HWResult':
            from KKT_Module.DataReceive.DataReciever import HWResultReceiver
            receiver = HWResultReceiver()
        elif receiver == 'MultiResult4168B':
            from KKT_Module.DataReceive.DataReciever import MultiResult4168BReceiver
            receiver = MultiResult4168BReceiver()
        elif receiver == 'MultiResult4169C':
            from KKT_Module.DataReceive.DataReciever import MultiResult4169CReceiver
            receiver = MultiResult4169CReceiver()
        elif receiver == 'HWResultOpenPSM':
            from KKT_Module.DataReceive.DataReciever import HWResultOpenPSMReceiver
            receiver = HWResultOpenPSMReceiver()
        return receiver

if __name__ == '__main__':
    m = ModeConfigs(
        receiver='RawData',
        updater='RawData',
        user_level=1,
        need_set_script=True,
        app = 'app'
    )

    u = ModeSelector.selectUpdater(m)
    r = ModeSelector.selectReceiver(m)

    print('end')




