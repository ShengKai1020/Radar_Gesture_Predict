import numpy as np

from Library.KKTLib import Lib

def test_SoftMaxInterrupt():
    print(Lib.ksoclib.connectDevice())
    print(hex(Lib.ksoclib.regRead(0x50000544, 1)[0]))
    Lib.ksoclib.switchSoftMaxInterrupt(0b111, 0, 0, 4097*4, 7, [0x50000544])
    i = 0
    while i < 100:
        res = Lib.ksoclib.getSoftmaxInterruptAsserted()
        if res is None:
            continue
        print(np.asarray(list(res[0])))
        print(np.asarray(list(res[1])))
        print(np.asarray(list(res[2])))
        print(i)
        i += 1
    Lib.ksoclib.switchSoftMaxInterrupt(0)
    Lib.ksoclib.closeDevice()

def test_EFuse_Read():
    print(Lib.ksoclib.connectDevice())
    print(hex(Lib.ksoclib.regRead(0x50000544, 1)[0]))

    for i in range(16):
        res = Lib.ksoclib.readEFuseCmd(i)
        print(str(i) + ':' + str(res))



if __name__ == '__main__':
    Lib = Lib()
    # lib.ksoclib.switchLogMode(True)
    print('')
    test_EFuse_Read()
