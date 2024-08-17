import sys
import os
import pathlib

kkt_module_path = pathlib.Path(__file__).parent.absolute()
if not os.path.isdir(kkt_module_path):
    main_path = os.getcwd()
    kkt_module_path = os.path.normpath(os.path.join(main_path, '.\KKT_Module'))
print('KKT module path:{}'.format(kkt_module_path))
sys.path.append(str(kkt_module_path))

# kkt_dll_path = os.path.normpath(os.path.join(kkt_module_path, '..\KSOC_USB_Tools'))
# print('Dll path :{}'.format(kkt_dll_path))
# sys.path.append(kkt_dll_path)
kkt_config_path = os.path.normpath(os.path.join(kkt_module_path, '..\Config'))
print('Configs path :{}'.format(kkt_config_path))
sys.path.append(kkt_config_path)
kkt_param_path = os.path.normpath(os.path.join(kkt_module_path, '..\TempParam'))
print('TempParam path :{}'.format(kkt_param_path))
sys.path.append(kkt_param_path)
kkt_image_path = os.path.normpath(os.path.join(kkt_module_path, '..\Image'))
print('Images path :{}'.format(kkt_image_path))
sys.path.append(kkt_param_path)
kkt_sound_path = os.path.normpath(os.path.join(kkt_module_path, '..\Sound'))
print('Sounds path :{}'.format(kkt_sound_path))
sys.path.append(kkt_param_path)
kkt_record_path = os.path.normpath(os.path.join(kkt_module_path, '..\Record'))
print('Record path :{}'.format(kkt_record_path))
sys.path.append(kkt_record_path)

kkt_library_path = os.path.normpath(os.path.join(kkt_module_path, '..\Library'))
print('library path :{}'.format(kkt_library_path))
sys.path.append(kkt_library_path)

kkt_tracking_path = os.path.normpath(os.path.join(kkt_module_path, '..\Tracking'))
print('tracking path :{}'.format(kkt_tracking_path))
sys.path.append(kkt_tracking_path)

kkt_ml_path = os.path.normpath(os.path.join(kkt_module_path, '..\ML'))
print('ML path :{}'.format(kkt_ml_path))
sys.path.append(kkt_ml_path)

kkt_DSP_path = os.path.normpath(os.path.join(kkt_module_path, '..\DSP_Module'))
print('DSP path :{}'.format(kkt_DSP_path))
sys.path.append(kkt_DSP_path)


from KKT_Module.ksoc_global import kgl
# kgl.KKTLibDll = kkt_dll_path
kgl.KKTModule = kkt_module_path
kgl.KKTConfig = kkt_config_path
kgl.KKTTempParam = kkt_param_path
kgl.KKTImage = kkt_image_path
kgl.KKTSound = kkt_sound_path
kgl.KKTRecord = kkt_record_path


# import KKT_Module.KKTGraph
# import KKT_Module.SettingProcess
# import KKT_Module.DataReceive
# import KKT_Module.KKTUtility
# import KKT_Module.GuiUpdater
# if os.path.isdir(kkt_library_path):
#     import Library
# if os.path.isdir(kkt_DSP_path):
#     import DSP_Module
# if os.path.isdir(kkt_ml_path):
#     import ML
# if os.path.isdir(kkt_tracking_path):
#     import Tracking






