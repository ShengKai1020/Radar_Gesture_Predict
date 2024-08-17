import numpy as np
import os
import sys
import json
import traceback


def printArrayInfo(ary, name_str):
    print("AryInfo: name={}, dim={}, shape={}, size={}, dtype={}. normal: len={}, max={}, min={}".format
          (name_str, ary.ndim, ary.shape, ary.size, ary.dtype, len(ary), np.amax(ary), np.amin(ary)))

def sign2unsign(x, bit):
    '''
    return unsign-extend value.

    Parameters:
            NA.
    Returns:
            (y) : a integer between 0~2^bit
    '''
    if x < 0:
        y = x + 2 ** bit
    elif x >= 2 ** bit:
        y = x - 2 ** bit
    else:
        y = x
    return y

def printEnviroment():
    # print .net runtime version
    print('--------------------------------')
    print("System.Environment.Version = {}".format(System.Environment.Version))
    # print current enviroment
    print('---current enviroment-----------')
    for p in sys.path:
        print(p)
    print('--------------------------------')

def printParamAsTree(name, param):
    print(r"//==================================================================================")
    print(name)
    json_format = json.dumps(param, indent=4)
    # print(json_format, file=sys.stderr)
    print(json_format)
    print(r"//==================================================================================")

def strToInt(s):
    try:
        return int(s)
    except :
        return None

def strToFloat(s):

    try:
        return float(s)
    except :
        return None

def getCurrentBaseDir():
    # basedir = os.path.dirname(inspect.stack()[0][1])
    # return basedir
    return os.getcwd()

def getParentDir():
    # pard = Path(getCurrentBaseDir())
    # return str(pard.parent.absolute())
    return os.path.split(os.getcwd())[0]

def remove_repeated_old(arry_str, arry_remove=None):
    res = []
    for i in arry_str:
        if i not in res:
            if arry_remove != None and i in arry_remove:
                continue
            res.append(i)

def remove_repeated(arry_str, arry_remove=None):
    res = []
    previous = arry_str[0]
    res.append(previous)

    for i in arry_str[1:]:
        if previous != i:
            res.append(i)
            previous = i
    if arry_remove != None:
        res = [x for x in res if x not in arry_remove]
    return res

def printMessage(*args):
    text = ''
    for t in args:
        text = text + str(t) + ' '
    print(text)
    try:
        kgl.message.insertPlainText(text+'\n')
        kgl.message.moveCursor(QtGui.QTextCursor.End)
        QtWidgets.QApplication.processEvents()
    except:
        return 0

def traceException(error):
    error_class = error.__class__.__name__  # 取得錯誤類型
    detail = error.args[0]  # 取得詳細內容
    cl, exc, tb = sys.exc_info()  # 取得Call Stack
    lastCallStack = traceback.extract_tb(tb)[-1]  # 取得Call Stack的最後一筆資料
    fileName = lastCallStack[0]  # 取得發生的檔案名稱
    lineNum = lastCallStack[1]  # 取得發生的行號
    funcName = lastCallStack[2]  # 取得發生的函數名稱
    errMsg = "File \"{}\", line {}, in {}: [{}] {}".format(fileName, lineNum, funcName, error_class, detail)
    return errMsg



if __name__ == "__main__":
    try :
        l=[]
        print(l[0])
    except Exception as error:
        erm = traceException(error)
        print(erm)

    # a = ['1', '2', '1', '1', '0', '0', '0', '2', '2', 'b', '1', '0', 'a', '0', ]
    # rr = remove_repeated(a)
    # y = [int(x, 16) for x in rr]
    # print(rr)
    # print(y)
    print(sign2unsign(-912, 12))
    pass