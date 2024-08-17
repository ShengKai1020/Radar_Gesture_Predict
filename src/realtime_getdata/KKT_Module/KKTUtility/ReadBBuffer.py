import time

from KKT_Module.ksoc_global import kgl
import numpy as np

def ksoc_read_b_buffer(buf_list):
    print('ksoc_read_b_buffer')
    ksoc_freeze_b_buffer()
    ksoc_stop_digi_sic()

    channel = [1 ,2, 3]
    addrs = range(128)

    # ch1_buffer = np.zeros(128)
    # ch2_buffer = np.zeros(128)
    # ch3_buffer = np.zeros(128)
    ch1_buffer = buf_list[0]
    ch2_buffer = buf_list[1]
    ch3_buffer = buf_list[2]
    Compare = False

    for ch in channel:
        for addr in addrs:
            print('ch[{}], addr={}'.format(ch, addr))
            if ch == 1:
                kgl.ksoclib.writeReg(addr, 0x400B009C, 16, 9)
                kgl.ksoclib.writeReg(1, 0x400B0084, 8, 8 ,Compare=Compare)
                while True:
                    if kgl.ksoclib.readReg(0x400B0084, 8, 8) == 0:
                        break

                kgl.ksoclib.writeReg(1, 0x400B0084, 12, 12,Compare=Compare)
                while True:
                    if kgl.ksoclib.readReg(0x400B0084, 12, 12) == 0:
                        break

                kgl.ksoclib.writeReg(1, 0x400B0084, 8, 8,Compare=Compare)
                while True:
                    if kgl.ksoclib.readReg(0x400B0084, 8, 8) == 0:
                        break
                # ch1_buffer[addr] = unsign2sign(kgl.ksoclib.readReg(0x400B0094, 31, 16), 16)
                ch1_buffer[addr] = kgl.ksoclib.readReg(0x400B0094, 31, 16)

            elif ch == 2:
                kgl.ksoclib.writeReg(addr, 0x400B00BC, 16, 9)

                kgl.ksoclib.writeReg(1, 0x400B00A4, 8, 8,Compare=Compare)
                while True:
                    if kgl.ksoclib.readReg(0x400B00A4, 8, 8) == 0:
                        break

                kgl.ksoclib.writeReg(1, 0x400B00A4, 12, 12,Compare=Compare)
                while True:
                    if kgl.ksoclib.readReg(0x400B00A4, 12, 12) == 0:
                        break

                kgl.ksoclib.writeReg(1, 0x400B00A4, 8, 8,Compare=Compare)
                while True:
                    if kgl.ksoclib.readReg(0x400B00A4, 8, 8) == 0:
                        break
                # ch2_buffer[addr] = unsign2sign(kgl.ksoclib.readReg(0x400B00B4, 31, 16), 16)
                ch2_buffer[addr] = kgl.ksoclib.readReg(0x400B00B4, 31, 16)

            elif ch == 3:
                kgl.ksoclib.writeReg(addr, 0x4009009C, 16, 9)

                kgl.ksoclib.writeReg(1, 0x40090084, 8, 8,Compare=Compare)
                while True:
                    if kgl.ksoclib.readReg(0x40090084, 8, 8) == 0:
                        break

                kgl.ksoclib.writeReg(1, 0x40090084, 12, 12,Compare=Compare)
                while True:
                    if kgl.ksoclib.readReg(0x40090084, 12, 12) == 0:
                        break

                kgl.ksoclib.writeReg(1, 0x40090084, 8, 8,Compare=Compare)
                while True:
                    if kgl.ksoclib.readReg(0x40090084, 8, 8) == 0:
                        break
                # ch3_buffer[addr] = unsign2sign(kgl.ksoclib.readReg(0x40090094, 31, 16), 16)
                ch3_buffer[addr] = kgl.ksoclib.readReg(0x40090094, 31, 16)


    ksoc_trigger_digi_sic()
    ksoc_unfreeze_b_buffer()

    return ch1_buffer, ch2_buffer, ch3_buffer

def ksoc_freeze_b_buffer():
    print('# -ksoc_freeze_b_buffer')
    kgl.ksoclib.writeReg(1, 0x400B0098, 25, 25,0)
    kgl.ksoclib.writeReg(1, 0x40090098, 25, 25,0)
    kgl.ksoclib.writeReg(1, 0x400B00B8, 25, 25,0)
    kgl.ksoclib.writeReg(1, 0x400900B8, 25, 25,0)

    kgl.ksoclib.writeReg(1, 0x400B0084, 8, 8,0, Compare=False)
    kgl.ksoclib.writeReg(1, 0x400B00A4, 8, 8,0, Compare=False)
    kgl.ksoclib.writeReg(1, 0x400B0098, 8, 8,0)
    kgl.ksoclib.writeReg(1, 0x40090084, 8, 8,0, Compare=False)

    while True:
        if kgl.ksoclib.readReg(0x400B0084,8,8) != 0:
            continue
        if kgl.ksoclib.readReg(0x400B00A4,8,8) != 0:
            continue
        if kgl.ksoclib.readReg(0x40090084,8,8) != 0:
            continue
        if kgl.ksoclib.readReg(0x400900A4,8,8) != 0:
            continue
        break

def ksoc_unfreeze_b_buffer():
    print('# -ksoc_unfreeze_b_buffer')
    kgl.ksoclib.writeReg(0, 0x400B0098, 25, 25,0)
    kgl.ksoclib.writeReg(0, 0x40090098, 25, 25,0)
    kgl.ksoclib.writeReg(0, 0x400B00B8, 25, 25,0)
    kgl.ksoclib.writeReg(0, 0x400900B8, 25, 25,0)

    kgl.ksoclib.writeReg(1, 0x400B0084, 8, 8,0, Compare=False)
    kgl.ksoclib.writeReg(1, 0x400B00A4, 8, 8,0, Compare=False)
    kgl.ksoclib.writeReg(1, 0x400B0098, 8, 8,0)
    kgl.ksoclib.writeReg(1, 0x40090084, 8, 8,0, Compare=False)

    while True:
        if kgl.ksoclib.readReg(0x400B0084,8,8) != 0:
            continue
        if kgl.ksoclib.readReg(0x400B00A4,8,8) != 0:
            continue
        if kgl.ksoclib.readReg(0x40090084,8,8) != 0:
            continue
        if kgl.ksoclib.readReg(0x400900A4,8,8) != 0:
            continue
        break

def ksoc_stop_digi_sic():
    print('# -ksoc_stop_digi_sic')
    kgl.ksoclib.writeReg(1, 0x400B0084, 10, 10,0, Compare=False)
    kgl.ksoclib.writeReg(1, 0x400B00A4, 10, 10,0, Compare=False)
    kgl.ksoclib.writeReg(1, 0x40090084, 10, 10,0, Compare=False)
    kgl.ksoclib.writeReg(1, 0x400900A4, 10, 10,0)


    while True:
        if kgl.ksoclib.readReg(0x400B0084, 9, 9) != 0:
            continue
        if kgl.ksoclib.readReg(0x400B00A4, 9, 9) != 0:
            continue
        if kgl.ksoclib.readReg(0x40090084, 9, 9) != 0:
            continue
        break

def ksoc_trigger_digi_sic():
    print('# -ksoc_trigger_digi_sic')
    kgl.ksoclib.writeReg(1, 0x400B0084, 9, 9,0, Compare=False)
    kgl.ksoclib.writeReg(1, 0x400B00A4, 9, 9,0, Compare=False)
    kgl.ksoclib.writeReg(1, 0x40090084, 9, 9,0, Compare=False)
    kgl.ksoclib.writeReg(1, 0x400900A4, 9, 9,0)

def ksoc_set_SIC_RF():
    kgl.ksoclib.rficRegWrite(0x0162, 0x5D4F)
    kgl.ksoclib.rficRegWrite(0x0163, 0x0000)
    kgl.ksoclib.rficRegWrite(0x0176, 0x5D4F)
    kgl.ksoclib.rficRegWrite(0x0177, 0x0000)
    kgl.ksoclib.rficRegWrite(0x018A, 0x5D4F)
    kgl.ksoclib.rficRegWrite(0x018B, 0x0000)

def ksoc_set_b_buffer(bufB_addr_all, bufB_data_wr_all, ch):
    print("-> [Func] setBufferB Channel:{}".format(ch))
    ksoc_stop_digi_sic()
    assert len(bufB_addr_all) == len(bufB_data_wr_all)

    for k in range(len(bufB_addr_all)):

        bufB_addr = bufB_addr_all[k]+1

        bufB_data_wr = bufB_data_wr_all[k]

        ksoc_set_b_buffer_addr(bufB_addr, ch)

        ksoc_set_b_buffer_data_wr(bufB_data_wr, ch)

        triggerRegSettingDoneAll(ch)

        ksoc_trigger_write_b_buffer(ch)

        print('Channel = {}, addr = {}, val = {}'.format(ch, bufB_addr, bufB_data_wr))


def triggerRegSettingDoneAll(ch=None):
    print("--> [Func] triggerRegSettingDoneAll")
    RBCheck = 1
    if ch == 1 or (ch == None):
        kgl.ksoclib.writeReg(1, 0x400B0084, 8, 8, RBCheck)
    elif ch == 2 or (ch == None):
        kgl.ksoclib.writeReg(1, 0x400B00A4, 8, 8, RBCheck)
    elif ch == 3 or (ch == None):
        kgl.ksoclib.writeReg(1, 0x40090084, 8, 8, RBCheck)
    elif ch == 4 or (ch == None):
        kgl.ksoclib.writeReg(1, 0x400900A4, 8, 8, RBCheck)
    if ch == None:
        print('Trigger All Reg Setting Done'.format(ch))
        return
    print('Trigger Reg ({}) Setting Done'.format(ch))

def ksoc_set_b_buffer_addr(bufB_addr, ch):
    RBCheck = 1
    if ch == 1 :
        kgl.ksoclib.writeReg(bufB_addr, 0x400B009C, 15, 9, RBCheck)
    elif ch == 2 :
        kgl.ksoclib.writeReg(bufB_addr, 0x400B00BC, 15, 9, RBCheck)
    elif ch == 3 :
        kgl.ksoclib.writeReg(bufB_addr, 0x4009009C, 15, 9, RBCheck)
    elif ch == 4 :
        kgl.ksoclib.writeReg(bufB_addr, 0x400900BC, 15, 9, RBCheck)
    pass

def ksoc_set_b_buffer_data_wr(bufB_data_wr, ch):
    RBCheck = 1
    if ch == 1:
        kgl.ksoclib.writeReg(bufB_data_wr, 0x400B009C, 31, 16, RBCheck)

    elif ch == 2:
        kgl.ksoclib.writeReg(bufB_data_wr, 0x400B00BC, 31, 16, RBCheck)

    elif ch == 3:
        kgl.ksoclib.writeReg(bufB_data_wr, 0x4009009C, 31, 16, RBCheck)

    elif ch == 4:
        kgl.ksoclib.writeReg(bufB_data_wr, 0x400900BC, 31, 16, RBCheck)
    pass

def ksoc_trigger_write_b_buffer(ch):

    RBCheck = 0
    if ch == 1:
        kgl.ksoclib.writeReg(1, 0x400B0084, 11, 11, RBCheck)

    if ch == 2:
        kgl.ksoclib.writeReg(1, 0x400B00A4, 11, 11, RBCheck)

    if ch == 3:
        kgl.ksoclib.writeReg(1, 0x40090084, 11, 11, RBCheck)

    if ch == 4:
        kgl.ksoclib.writeReg(1, 0x400900A4, 11, 11, RBCheck)


    write_ok = 0
    for k in range(5):
        time.sleep(0.001)
        if ch == 1:
            c = kgl.ksoclib.readReg(0x400B0084, 11, 11);

        elif ch == 2:
            c = kgl.ksoclib.readReg(0x400B00A4, 11, 11);

        elif ch == 3:
            c = kgl.ksoclib.readReg(0x40090084, 11, 11);

        elif ch == 4:
            c = kgl.ksoclib.readReg(0x40090084, 11, 11);

        if c == 0:
            write_ok = 1
            break

        if write_ok:
            print('write BufB fail')
    pass

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
        y = 2**(bit-1) -x
    else:
        raise Exception('Value is out of bit range')
    return y



if __name__ == '__main__':
    kgl.setLib()
    kgl.ksoclib.connectDevice()
    ch1_buffer, ch2_buffer, ch3_buffer = ksoc_read_b_buffer()
    print(ch1_buffer)