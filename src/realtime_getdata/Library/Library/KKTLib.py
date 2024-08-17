from .LibLog import lib_logger as log

class Lib(object):
    '''
    Singleton for KSOC lib.
    '''
    _instance = None
    ksoclib = None
    def __new__(cls):
        if not cls._instance:
            # print('# ======== Set KKT Lib ===========')
            log.info('# ======== Set KKT Lib ===========')
            from .KsocLib import KsocLib
            Lib._instance = super(Lib, cls).__new__(cls)
            Lib.ksoclib = KsocLib()
        return cls._instance



if __name__ == '__main__':
    lib = Lib()
    print('')
    input('any:')
    print(lib.ksoclib.connectDevice())
    print(lib.ksoclib.regRead(0x50000544, 1))


