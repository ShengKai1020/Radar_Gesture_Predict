import numpy as np
def getFFT(data, output_len):
    input_len = len(data[0])
    assert input_len>5 and input_len > output_len

    FT = np.fft.fft(data, axis=1)
    powerFT = np.abs(FT)[:,:output_len]
    # powerFT = powerFFT(FT,input_len)[:,:output_len]

    return np.real(powerFT)

def powerFFT(data, input_len):
    data = data / input_len
    data = np.square(data)
    last = data[:, 1]
    for i in range(1,int(input_len/2)):
        data[:,i] = np.sqrt(data[:,2*i]+data[:,2*i+1])
    revers = data[:,::-1]
    data[:,input_len:]= revers[:,input_len:]
    data[:,int(input_len/2)] = last
    return data

def powerFFT2(data, input_len):
    data = data / input_len
    data = np.abs(data)
    last = data[:, 1]
    revers = data[:,::-1]
    data[:,int(input_len):]= revers[:,int(input_len):]
    data[:,int(input_len/2)] = last
    return data

if __name__ == '__main__':
    data = np.loadtxt(r'C:\Users\eric.li\Downloads\FFTdemo\FFTdemo\sin0.25Hz_fs4Hz.txt')
    res = np.asarray(getFFT(data, 128), dtype='float16')
    pass