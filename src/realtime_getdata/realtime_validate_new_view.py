import sys
import os
import numpy as np
import time
import pyqtgraph as pg
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QVBoxLayout, QPushButton, QLabel, QTextEdit, QWidget
from PyQt5.QtCore import QThread, pyqtSignal
from KKT_Module.ksoc_global import kgl
from KKT_Module.Configs import SettingConfigs
from KKT_Module.SettingProcess.SettingProccess import SettingProc, ConnectDevice, ResetDevice
from KKT_Module.DataReceive.DataReciever import FeatureMapReceiver
from tensorflow.keras.models import load_model

# 定義全局變量
WINDOW_SIZE = 30  # Sliding window 的大小
BUFFER_SIZE = WINDOW_SIZE  # Buffer 的大小，應與 WINDOW_SIZE 一致
buffer = np.zeros((2, 32, 32, BUFFER_SIZE), dtype=np.float32)  # 初始化 buffer

# 載入訓練好的模型
model_path = 'output/models/3d_cnn_model_20240817_213956.h5'  # 修改為你的模型路徑
model = load_model(model_path)

# 模擬接收數據的線程
class DataReceiver(QThread):
    data_received = pyqtSignal(list)  # 自訂義信號，用來傳遞接收到的數據
    prediction_result = pyqtSignal(str)  # 自訂義信號，用來傳遞預測結果

    def __init__(self):
        super().__init__()
        self.running = True  # 設定線程是否繼續運行的標誌

    def run(self):
        connect()  # 連接裝置
        startSetting()  # 設定硬體 AI 和 RF 參數

        R = FeatureMapReceiver(chirps=32)  # 創建接收器來接收 RDI 和 PHD 圖
        R.trigger(chirps=32)  # 在接收數據前觸發接收器
        time.sleep(0.5)
        print('# ======== 開始接收手勢數據 ===========')

        global buffer  # 使用全局變量 buffer

        while self.running:
            res = R.getResults()  # 從接收器獲取數據
            if res is None:
                continue

            res = list(res)  # 將 tuple 轉換為 list 以進行修改

            # 對於每個矩陣，進行順時針 90 度旋轉
            # res[0] = np.rot90(res[0], k=-1)  # 順時針旋轉90度
            # res[1] = np.rot90(res[1], k=-1)  # 順時針旋轉90度

            # 將矩陣左右相反
            # res[0] = np.fliplr(res[0])  # 將第一個矩陣左右翻轉
            # res[1] = np.fliplr(res[1])  # 將第二個矩陣左右翻轉

            # 將矩陣上下相反
            # res[0] = np.flipud(res[0])  # 將第一個矩陣上下翻轉
            # res[1] = np.flipud(res[1])  # 將第二個矩陣上下翻轉

            # 先对矩阵进行转置操作
            res[0] = np.transpose(res[0])  # 对第一个矩阵执行 X 轴和 Y 轴的转置
            res[1] = np.transpose(res[1])  # 对第二个矩阵执行 X 轴和 Y 轴的转置



            # 插入新數據到 buffer
            buffer = np.roll(buffer, shift=-1, axis=-1)  # 將 buffer 左移，丟棄最舊的幀
            buffer[..., -1] = res[0]  # 將新幀放入 buffer 的最後位置

            # 當 buffer 填滿時進行預測
            if buffer.shape[-1] == WINDOW_SIZE:
                window_feature = np.expand_dims(buffer, axis=0)  # 增加 batch 維度
                window_feature = window_feature.astype('float32') / 255.0  # 進行數據縮放，與訓練時一致
                predictions = model.predict(window_feature)[0]  # 獲取預測結果

                background_prob = predictions[0]
                forward_prob = predictions[1]
                right_prob = predictions[2]

                if forward_prob > 0.5:
                    output = f"預測結果為forward: background: {background_prob:.2f}, forward: {forward_prob:.2f}, right: {right_prob:.2f}"
                elif right_prob > 0.5:
                    output = f"預測結果為right: background: {background_prob:.2f}, forward: {forward_prob:.2f}, right: {right_prob:.2f}"
                else:
                    output = f"預測結果為background: background: {background_prob:.2f}, forward: {forward_prob:.2f}, right: {right_prob:.2f}"

                self.data_received.emit(res)  # 發送接收到的數據到主窗口
                self.prediction_result.emit(output)  # 發送預測結果到主窗口

            self.msleep(100)  # 模擬每100毫秒接收一次數據

    def stop(self):
        self.running = False  # 停止線程運行

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()  # 初始化介面佈局
        self.data_receiver = DataReceiver()  # 創建數據接收線程
        self.data_receiver.data_received.connect(self.update_plots)  # 連接接收數據信號到更新圖像函數
        self.data_receiver.prediction_result.connect(self.update_console)  # 連接預測結果到更新console函數
        self.data_receiver.start()  # 啟動數據接收線程

    def init_ui(self):
        layout = QVBoxLayout()  # 創建垂直佈局

        # 創建兩個圖像顯示區域，分別用於顯示RDI和PHD map
        self.plot_rdi = pg.ImageView()
        self.plot_phd = pg.ImageView()

        # 創建控制台顯示區域，用來顯示print的內容
        self.console_output = QTextEdit()
        self.console_output.setReadOnly(True)  # 設置為只讀模式

        # 創建停止按鈕
        self.stop_button = QPushButton('Stop')
        self.stop_button.clicked.connect(self.stop_data_receiver)  # 連接停止按鈕到停止函數

        # 添加部件到佈局
        layout.addWidget(QLabel("RDI Map"))
        layout.addWidget(self.plot_rdi)
        layout.addWidget(QLabel("PHD Map"))
        layout.addWidget(self.plot_phd)
        layout.addWidget(QLabel("Console Output"))
        layout.addWidget(self.console_output)
        layout.addWidget(self.stop_button)

        self.setLayout(layout)  # 設定窗口的佈局
        self.setWindowTitle('RDI and PHD Map Viewer')  # 設定窗口標題

    def update_plots(self, res):
        # 更新RDI和PHD圖像
        if isinstance(res, list):
            self.plot_rdi.setImage(res[0])
            self.plot_phd.setImage(res[1])

            # 設置顏色映射，將0對應藍色，255對應紅色，中間值漸變為綠色
            colormap = pg.ColorMap([0, 127, 255], [(0, 0, 255), (0, 255, 0), (255, 0, 0)])
            self.plot_rdi.getImageItem().setLookupTable(colormap.getLookupTable(0, 255, 256))
            self.plot_phd.getImageItem().setLookupTable(colormap.getLookupTable(0, 255, 256))

    def update_console(self, text):
        # 更新控制台輸出
        if isinstance(text, str):
            self.console_output.append(text)

    def stop_data_receiver(self):
        # 停止接收數據
        self.data_receiver.stop()

def connect():
    """
    連接裝置並重置硬體設定
    """
    connect = ConnectDevice()
    connect.startUp()  # 連接裝置
    reset = ResetDevice()
    reset.startUp()  # 重置硬體設定

def startSetting():
    """
    設定硬體 AI 和 RF 參數
    """
    SettingConfigs.setScriptDir("K60168-Test-00256-008-v0.0.8-20230717_120cm")  # 設定腳本目錄
    ksp = SettingProc()  # 創建設定過程的物件
    ksp.startUp(SettingConfigs)  # 啟動設定過程

def main():
    """
    主函數，負責啟動主窗口
    """
    kgl.setLib()  # 初始化 KKT 模組

    app = QtWidgets.QApplication(sys.argv)  # 創建PyQt應用
    main_window = MainWindow()  # 創建主窗口
    main_window.show()  # 顯示主窗口
    sys.exit(app.exec_())  # 運行PyQt應用

if __name__ == '__main__':
    main()
