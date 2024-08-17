import os.path
import pathlib

from KKT_Module.KKTUtility.EncryptTool import EncryptTool
from KKT_Module.ksoc_global import kgl
import io
import ast
import h5py
import zlib
import time
import numpy as np

class KKTH5Tool:
    _current_file = ''
    File = None
    def __init__(self):
        # self._current_file = ''
        # self._f = None
        pass

    @classmethod
    def getGestureDict(cls, filename:str):
        '''
        :param weights_path: AI Weight H5 file
        :return: gesture mapping dict , background id
        '''
        f = cls.openH5(filename)
        gesture_dicts = {}
        gesture_map_list = ['Mapping_dict', 'Mapping_dict_core', 'Mapping_dict_siamese']
        for gesDict in gesture_map_list:
            # note that you read a bytes data from h5, but it is string in python3 actually, str=b'123'
            if f.get(gesDict) is None:
                continue
            mapping_dict = str(np.array(f.get(gesDict)))[2:-1]
            gesture_dicts[gesDict] = ast.literal_eval(mapping_dict)
        return gesture_dicts

    @classmethod
    def readData(cls, filename):
        print('# =============== Read H5 Dataset ================')
        # open h5 file
        f = cls.openH5(filename)
        # extract RDI/PhD from h5 data and transform as numpy
        data = f.get('DS1')
        if data is not None:
            data = data[:].astype(np.float32)
            # data = data[0, :, :, 0]
            print(data.shape)

        # extract label from h5 data and transform as numpy
        label = f.get('LABEL')
        if label is not None:
            label = label[:].astype(np.int16)
            print(label.shape)

        # extract axis from h5 data and transform as numpy
        axis = f.get('AXIS')
        if axis is not None:
            axis = axis[:].astype(np.int32)
            print(axis.shape)
        # remember to close file
        return data, label, axis


    # -------- parsing H5 file--------------
    @classmethod
    def parsingRecordH5(cls, filename):
        # open h5 file
        print('======== Parse h5 file info ==========')
        f = cls.openH5(filename)
        # print('file path : {}'.format(filename))
        for key in f.keys():
            if type(f[key]) == h5py.Group:
                print(r'\{}'.format(key))
                cls._visitGroup(f[key])

            if type(f[key]) == h5py.Dataset:
                print('[{}]'.format(key))
                cls._showDataset(f[key])
        # remember to close file
        # f.close()
        return f

    @classmethod
    def _visitGroup(cls, group:h5py.Group, tab=1):
        for attr in group.attrs:
            print('\t' * tab, '{} : {}'.format(attr, group.attrs[attr]))
        for key in group.keys():
            if type(group[key]) == h5py.Group:
                print('\t' * tab, r'\{}'.format(key))
                cls._visitGroup(group[key], tab=tab+1)

            if type(group[key]) == h5py.Dataset:
                print('\t' * tab, '[{}]'.format(key))
                cls._showDataset(group[key], tab=tab+1)

    @classmethod
    def _showDataset(cls, data_set:h5py.Dataset , tab=1):
        print('\t'*tab,'Size : {}'.format(data_set.shape))
        print('\t'*tab,'Datatype : {}'.format(data_set.dtype))
    #-----------------------------------------

    @classmethod
    def getH5Attribute(cls, filename, group_name, attribute=None) -> dict:
        print('# ======== get h5 attrs ==========')
        attr_dict = {}
        key = group_name
        print('File path : {}'.format(filename))
        print('Group name : {}'.format(group_name))
        print('Attribute : {}'.format(attribute))
        f = cls.openH5(filename)
        if attribute != None:
            if attribute in f[key].attrs:
                attr_dict[attribute] = f[key].attrs[attribute]
            else:
                print('attribute "{}" not in group "{}"'.format(attribute, key))
        else:
            for attr in f[key].attrs:
                attr_dict[attr] = f[key].attrs[attr]
        return attr_dict

    @classmethod
    def save_data(cls, filename, data, label=None, xy_axis=None, bit_true_axis=None, attrs=None):
        # open h5 file
        h5_file = h5py.File(filename + '.h5', 'w')

        # save data under key [DS1]
        h5_file.create_dataset('DS1', data=data)

        # save label under key [label]
        if label != None:
            h5_file.create_dataset('LABEL', data=label)

        # save xy_axis under key [xy_axis]
        if xy_axis != None:
            h5_file.create_dataset('AXIS', data=xy_axis)

        # save xy_axis under key [track_Axis]
        if bit_true_axis != None:
            h5_file.create_dataset('bit_true_axis', data=bit_true_axis)

        if attrs != None:
            for item in attrs:
                h5_file.attrs[item] = attrs[item]

        # remember to close file
        h5_file.close()

    @classmethod
    def openH5(cls, h5_path):
        assert os.path.exists(h5_path), 'File "{}" not found.'.format(h5_path)
        if hasattr(cls, '_current_file'):
            if h5_path == cls._current_file:
                return cls.File
            if type(cls.File) == h5py.File:
                cls.File.close()
            cls._current_file = h5_path
        print('File path: {}'.format(h5_path))

        if pathlib.Path(h5_path).suffix in ['.kkt','.KKT']:
            print('weight is kkt')
            print('Decompressing...')
            encryptTool = EncryptTool()
            with open(h5_path, 'rb') as F:
                Ouput_IOFile = io.BytesIO(F.read())
            private_key = encryptTool.Get_private_key()
            Decrypted_file, decrpyted_string = encryptTool.Decode_BytesIOObject(Ouput_IOFile, private_key)
            btime = time.time()
            decom_con = zlib.decompress(Decrypted_file.read())
            BytesIOObject = io.BytesIO(decom_con)
            print("Decompress time: {}".format(time.time() - btime))
            file = h5py.File(BytesIOObject, 'a')

        elif pathlib.Path(h5_path).suffix in ['.h5','.H5']:
            print('weight is h5')
            file = h5py.File(h5_path, 'a')

        if hasattr(cls, 'File'):
            cls.File = file
        return file

    def close(self):
        if type(self.File) == h5py.File:
            self.File.close()

    def flush(self):
        if type(self.File) == h5py.File:
            self.File.flush()




if __name__ == '__main__':
    weight_path = r'C:\Users\eric.li\Desktop\Python\0_Sniff_Collection_Tool\Record\RawData\KKT\_2022_10_31_19_26_02.h5'
    KKTH5Tool.parsingRecordH5(weight_path)
    # KKTH5Tool.getGestureDict(weight_path)

