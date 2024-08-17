class kgl:
    ksoclib = None
    KKTLibDll = ''
    KKTModule = ''
    KKTConfig = ''
    KKTImage = ''
    KKTSound = ''
    KKTTempParam = ''
    KKTRecord= ''
    @classmethod
    def setLib(cls):
        from Library import Lib
        kgl.ksoclib = Lib().ksoclib
        return kgl.ksoclib




if __name__ == '__main__':
    input('any:')
