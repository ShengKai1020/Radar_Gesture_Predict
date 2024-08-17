import sys
import traceback
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

def traceException(error):
    error_class = error.__class__.__name__  # 取得錯誤類型
    detail = error.args[0]  # 取得詳細內容
    cl, exc, tb = sys.exc_info()  # 取得Call Stack
    lastCallStack = traceback.extract_tb(tb)[-1]  # 取得Call Stack的最後一筆資料
    fileName = lastCallStack[0]  # 取得發生的檔案名稱
    lineNum = lastCallStack[1]  # 取得發生的行號
    funcName = lastCallStack[2]  # 取得發生的函數名稱
    errMsg = "{} \n line {} in {}: \n[{}] {}".format(fileName, lineNum, funcName, error_class, detail)
    return errMsg

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