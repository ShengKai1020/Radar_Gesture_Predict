# Library
***
此模組為 C# library API 的 python 介面，架構主要分為兩層。 

<code> LibWrapper.py </code> 為與 .dll 的實作：

* 只實現 C# library 的 API ，負責專換 Python data type to C# input type 和 C# output data type to python format.
* Catch error number and raise exceptions.

<code> KsocLib.py </code> 為與 Python 上層溝通的介面：

* 擴充 API 或增加判斷式及城市邏輯 for python.
* 整合舊版 python code (2022/10/18 後的版本有整理模組，以及修改function名稱，不符合命名規則的方法，使用此層去做整合。)
* Libaray log.


***
## 關於與 C# Lib 之間版本對應的問題

目前 C# .dll 放置的路徑為與執行的程式同目錄下命名為 **KSOC_USB_Tools/(相容舊版)** 或 **KSOC_Libs/** 的資料夾下，之前有 .dll
版本與 python library 版本之間不好控管的問題，所以現在會以此模組裡 **./KSOC_Libs/KSOC_Lib.dll** 的版本為主測試後一起推至GitLab。


***
## 命名規則

資料夾名稱 : 單字開頭大寫並以底線分割，縮寫皆大寫，ex.<code>KSOC_Libs/</code>

Module名稱 : 單字開頭大寫不以底線分割，ex.<code>LibWrapper.py </code>

class名稱 : 單字開頭大寫不以底線分割，ex.<code>class KSOCIntegration()</code>

function名稱 : 以動詞+名詞的形式如果有備註以底線分割，動詞開頭小寫其餘大寫，ex.<code>def receiveAllData_list()</code>

global變數 : 單字皆大寫並以底線分割，ex.<code>GLOBAL_VAR</code>

class屬性 : 單字小寫並以底線分割，ex.<code>self.class_var</code>

***
## KKTLib.py

此模組中的類別<code>"Lib"</code>為**單例模式**的實作，只要進入程式後第一次實例化類別<code>"Lib"</code>就可以在有 import 此類別的模組中
在其靜態屬性<code>"ksoclib"</code>中使用 Libaray 的函數。

此模組一部分是為了 PyQT/PySide 設計( 如果有使用 QT 的 UI 需在 QApplication 的 loop 中實例化，不然在使用QFileDialog類別的時候會有檔案選單打不開的bug)，
一部分是為了分離KKT_Module模組間的相依性。

***

## 環境與模組安裝

編譯環境請使用 **Python 3.7** 以上和 **Python 3.9** 以下版本，或查看  **requirements.txt** 
模組版本。

###pip指令
安裝套件： 可以將 package 換成任何想安裝的 Python 套件

    pip install [package]
更新套件：

    pip install -U [package]
移除安裝過的套件：

    pip uninstall [package]
安裝並且指定套件版本：

    pip install -v [package]==1.0 
查看目前安裝過的清單：

    pip list
匯出套件版本指令:

    pip freeze > requirements.txt
用 pip 安裝 requirement.txt: [推薦使用]

    pip install -r requirements.txt
***
##  Create environment and install modules in Conda

使用 anaconda 的指令安裝環境，目前環境請使用 **Python 3.8** 並根據根據 **environments.yaml** 安裝環境所需的模組。

###Conda指令

1.創建環境： 在 Conda 中創建一個新的環境

    conda create -n [environment_name] [python=(version, ex. 3.8)] (版本)
2.啟動環境：

    conda activate [environment_name]
3.退出環境：

    deactivate
4.列舉環境：

    conda env list
5.匯出環境：

    conda env export > environment.yml 
6.匯入環境：

    conda env create -f environment.yml
7.刪除環境 (需退出要刪除的環境):

    conda env remove -n environment_name




