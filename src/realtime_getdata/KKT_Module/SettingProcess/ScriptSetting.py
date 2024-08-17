import os
import time
from KKT_Module.ksoc_global import kgl

class ProcessListSymbol:
    RegSymbol = "Register"
    CommentSymbol = "Remark"
    RFFileSymbol = "RFFile"
    AIWeightPathSymbol = "AIWeightPath"
    AIWeightFilesSymbol = "AIWeightFiles"

    @classmethod
    def getSymbolString(cls, symbol):
        return {
            cls.RegSymbol: 'reg_write',
            cls.CommentSymbol: '//',
            # cls.WeightFileSymbol: '// WeightFile',
            cls.RFFileSymbol: '// RFFile',
            cls.AIWeightPathSymbol: '// AIWeightPath',
            cls.AIWeightFilesSymbol: '// AIWeightFiles',
        }.get(symbol, None)
pls = ProcessListSymbol()

class ScriptSetter:
    def __init__(self):
        self.process =[0,100]
        pass

    def configByDevice(self, script_path, procList:list, weightDir=None, write_AI=True, write_RF=True):
        aiweightpath = None
        proclist_len = len(procList)
        cnt = 0
        self.process[1] = proclist_len
        for plist in procList:
            cnt = cnt + 1
            self.process[0] = cnt
            # print('Process List: {}/{}'.format(cnt, proclist_len))
            if plist[0] == pls.RegSymbol:
                pstr = pls.getSymbolString(pls.RegSymbol) + " ( 0x{:08X}, 0x{:08X});".format(plist[1], plist[2])
                kgl.ksoclib.regWrite(plist[1], [plist[2]])
                result = kgl.ksoclib.regRead(plist[1], 1)
                if result[0] != plist[2]:
                    print("{:08X}".format(plist[1]))
            elif plist[0] == pls.CommentSymbol:
                print("// {}".format(plist[1]))
            elif plist[0] == pls.RFFileSymbol and write_RF:
                pstr = pls.getSymbolString(pls.RFFileSymbol) + ' : ' + plist[1]
                rficfolder = script_path + r'\Integration_Test_script\SOCA'
                rficfiles = os.listdir(rficfolder)
                rficfile = os.path.join(rficfolder,rficfiles[0])
                # assert script_dir.get('RF_setting') is not None, "Empty RF setting !"
                # rficfile = script_dir.get('RF_setting')
                print(rficfile)
                # printMessage(rficfile)
                kgl.ksoclib.setScriptRfic(rficfile, True, [0x005D, 0x0071,  0x0085, 0x010D, 0x010E, 0x020C])
            elif plist[0] == pls.AIWeightPathSymbol and write_AI:
                pstr = pls.getSymbolString(pls.AIWeightPathSymbol) + ' : ' + plist[1]
                aiweightpath = plist[1]
                aiweightpath = script_path + r'\ai_acc_weight\sram_coe'
                # printMessage(aiweightpath)
            elif plist[0] == pls.AIWeightFilesSymbol and write_AI:
                pstr = pls.getSymbolString(pls.AIWeightFilesSymbol)+ ' : '  + ' '.join(str(x) for x in plist[1])
                for f in plist[1]:
                    if weightDir == None:
                        # aiwf =  os.path.normpath(os.path.join(kgl.ScriptDir, '.' + aiweightpath, f))
                        aiwf = os.path.normpath(os.path.join(aiweightpath, f))
                    else:
                        aiwf =  os.path.normpath(os.path.join(weightDir, f))
                    print(aiwf)
                    kgl.ksoclib.setScriptAIWeight(aiwf, True)
            elif plist[0] == 'test':
                time.sleep(0.01)
                print('test process list set: {} ,{}'.format(cnt, plist[1]))


if __name__ == '__main__':
    from threading import Thread
    import random
    def setScript(sc):
        scriptpath = '123'
        proclist = []
        for i in range(1000):
            proclist.append(['test', random.randint(0, 100)])
        print('start')
        args = (scriptpath, proclist)
        T = Thread(target=sc.configByDevice, args=args)
        T.start()
        # sc.configByDevice(scriptpath, proclist)
        print('end')

    def main():
        from PySide2 import QtWidgets, QtCore
        app = QtWidgets.QApplication([])
        win = QtWidgets.QMainWindow()
        win.resize(300, 50)
        wg = QtWidgets.QWidget()
        ly = QtWidgets.QVBoxLayout(wg)
        win.setCentralWidget(wg)
        lb = QtWidgets.QLabel('process:')
        pgb = QtWidgets.QProgressBar()
        pgb.setRange(0, 100)
        pgb.setFormat('%p%')
        pgb.setValue(0)
        pgb.setFormat('%v%')
        pgb.setTextVisible(True)
        pb = QtWidgets.QPushButton('start')
        qtimer = QtCore.QTimer()
        ly.addWidget(lb)
        ly.addWidget(pgb)
        ly.addWidget(pb)
        win.show()
        sc = ScriptSetter()

        def start():
            qtimer.start(1)
            setScript(sc)

        def update():
            p = sc.process
            lb.setText('process: {}/{}'.format(p[0], p[1]))
            v = int(p[0] / p[1] * 100)
            pgb.setValue(v)
            app.processEvents()
            pass

        pb.clicked.connect(lambda: start())
        qtimer.timeout.connect(lambda: update())

        app.exec_()
    main()
