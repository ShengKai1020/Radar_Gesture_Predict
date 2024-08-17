import array
import time

import numpy
import numpy as np


class ResultParsing():
    '''
        Import a list for the hardware results want to be parsed.

    '''
    def __init__(self, result_list:list):
        self._result_list = result_list
        self._parsed_result_dict = {}
        pass

    def parsing(self, result_dict:dict):
        parsed_result_dict = {}
        for result in self._result_list:
            arry = result_dict.get(result)
            if arry is None:
                continue
            if result in ['CFAR']:
                arry = self.__parseCFAR(arry)
            elif result in ['SoftmaxExponential']:
                arry = self.__parseSoftMaxExponential(arry)
            elif result in ['SiameseExponential']:
                arry = self.__parseSiameseExponential(arry)
            elif result in ['Axis']:
                arry = self.__parseAxis(arry)
            elif result in ['Gestures']:
                arry = self.__parseGesture(arry, 0, 4)
            elif result in ['SiameseGestures']:
                arry = self.__parseGesture(arry, 16, 20)
            elif result in ['IMax']:
                arry = self.__parseIMax(arry)
            elif result in ['AI Sram']:
                arry = self.__parseAISram (arry)
            else:
                pass
            parsed_result_dict[result] = arry
        self._parsed_result_dict = parsed_result_dict

    def getParsedResults(self):
        return self._parsed_result_dict

    def __parseAISram(self, arry):
        ai_sram = []
        binvals=''
        for i in range(len(arry)):
            binval = bin(arry[i]).split('0b')[1].zfill(32)
            binvals = binval+binvals

        ai_sram_list = [binvals[i: i + 12] for i in range(0, len(binvals), 12)]

        for i in range(len(ai_sram_list)):
            ai_sram.insert(0,  unsign2sign(int(ai_sram_list[i],2),12))


        return ai_sram

    def __parseCFAR(self, arry):
        CFAR = []
        for i in range(len(arry)):
            binval = bin(arry[i]).split('0b')[1].zfill(32)
            CFAR_amp_odd = int(binval[0:16], 2)
            CFAR.append(CFAR_amp_odd)
            CFAR_amp_even = int(binval[16:32], 2)
            CFAR.append(CFAR_amp_even)
        return np.asarray(CFAR).astype('int16')

    def __parseIMax(self, arry):
        IMax = []
        binval = bin(arry[0]).split('0b')[1].zfill(32)
        imax = int(binval[0:16], 2)
        IMax.append(imax)
        return np.asarray(IMax).astype('int16')

    def __parseSoftMaxExponential(self, arry):
        val_line = ''
        for v in arry:
            hex_val = hex(v).split('0x')[1].zfill(8)
            val_line = hex_val + val_line
        exponential = []
        for i in range(len(val_line), 0, -3):
            dec_val = int(val_line[i - 3:i], 16)
            dec_val = unsign2sign(dec_val, 12)
            exponential.append(dec_val)
        return np.asarray(exponential).astype('int16')

    def __parseSiameseExponential(self, arry):
        val_line = ''
        for v in arry:
            hex_val = hex(v).split('0x')[1].zfill(8)
            val_line = hex_val + val_line
        exponential = []
        for i in range(len(val_line), 0, -3):
            dec_val = int(val_line[i - 3:i], 16)
            exponential.append(dec_val)
        return np.asarray(exponential).astype('int16')

    def __parseGesture(self, arry, start_bit=0, end_bit=4):
        gesture = []
        bin_val = bin(arry[0]).split('0b')[1].zfill(32)
        bin_val_rev = bin_val[::-1]
        val_rev = bin_val_rev[start_bit:end_bit + 1]
        val = val_rev[::-1]
        if val[-5] == '0':
            gesture.append(int(val[-4:], 2))
        elif val[-5] == '1':
            gesture.append(int(val[-4:], 2) - 16)
        else:
            print('gesture not save')
            return
        return np.asarray(gesture).astype('int16')

    def __parseAxis(self, arry):
        # tracking_axis = []
        hex_val_0 = hex(arry[0]).split('0x')[1].zfill(8)
        hex_val_1 = hex(arry[1]).split('0x')[1].zfill(8)
        tracking_axis = [int(hex_val_0[4:8], 16),
                         int(hex_val_0[0:4], 16),
                         int(hex_val_1[4:8], 16)]
        return np.asarray(tracking_axis).astype('int16')

    def parseRawData(self, res, start, end):
        FrameCount1 = res[start]
        FrameCount2 = res[start+1]

        data = res[start + 2:end]
        ch1 = data[::2]
        ch2 = data[1::2]
        data = np.vstack((ch1, ch2))

        # print('FrameCount 1={}, FrameCount 2={}'.format((FrameCount & 0xFFFF), (FrameCount >> 16) & 0xFFFF))
        return data

    def parseRDI(self, res, start, end):

        FrameCount = res[start]
        data = res[start + 1:start+end]
        # print('FrameCount 1={}, FrameCount 2={}'.format((FrameCount & 0xFFFF), (FrameCount >> 16) & 0xFFFF))
        raw_RDI = convertBitArray(data,16,12)
        return raw_RDI
        # return np.frombuffer(data.tobytes(), dtype='int16')

    def parseRawData2(self, res, start, size, switch_mode):
        '''
        For 0xAF command raw data
        Args:
            res:
            start:
            size:

        Returns:

        '''
        if res is None:
            return
        FrameCount1 = res[start]
        FrameCount2 = res[start+1]
        data = np.zeros(size, dtype='int16')


        if switch_mode == 1:
            data = np.reshape(data, (32, 128))
            res = np.reshape(res[start + 2:], (2, 16, 128))
            data[0::2] = res[0]
            data[1::2] = res[1]
            data = np.reshape(data, size)
        else:
            data = res[start + 2:start + 2 + size]

        # print('FrameCount 1={}, FrameCount 2={}'.format((FrameCount1 & 0xFFFF), (FrameCount2) & 0xFF))
        return data




def unsign2sign(x, bit):
    '''
    return sign-extend value.

    Parameters:
            NA.
    Returns:
            (y) : a integer between 0~2^bit
    '''
    if x >= 0 and x < 2 ** (bit-1):
        y = x
    elif x >= 2 ** (bit-1) and x < 2**bit:
        y = x - 2**(bit)
    else:
        raise Exception('Value is out of bit range')
    return y


def convertBitArray(arry, src_bit, dis_bit):
    niddles = int(src_bit/4)
    new_niddle_num = int(dis_bit/4)
    Hex_line = ''
    for i in arry:
        Hex = hex(i).split('0x')[1].zfill(niddles)
        Hex_line =  Hex + Hex_line


    hexs = [int(Hex_line[3*k:3*k+new_niddle_num],16) for k in range(int(len(Hex_line)/new_niddle_num))]

    output = hexs

    output.reverse()

    return np.asarray(output,dtype='uint16')





if __name__ == '__main__':
    # result_dict = {}
    # result_dict['SoftmaxExponential'] = np.random.randint(2 ** 32, size=6, dtype='uint32')
    # result_dict['SiameseExponential'] = np.random.randint(2 ** 32, size=6, dtype='uint32')
    # result_dict['Axis'] = np.random.randint(2 ** 32, size=2, dtype='uint32')
    # result_dict['Gestures'] = np.random.randint(2 ** 32, size=1, dtype='uint32')
    # result_dict['SiameseGestures'] = np.random.randint(2 ** 32, size=1, dtype='uint32')
    # result_dict['IMax'] = np.random.randint(2 ** 32, size=1, dtype='uint32')
    # result_dict['CFAR'] = np.random.randint(2 ** 32, size=16, dtype='uint32')
    # result_list = list(result_dict.keys())
    # s = time.time_ns()
    # result_parser = ResultParsing(result_list)
    # result_parser.parsing(result_dict)
    # results = result_parser.getParsedResults()
    # e = time.time_ns()
    # print(results)
    arry = np.asarray([i for i in range(1620)])
    a =  convertBitArray(arry, 32, 12)
    print(a)
