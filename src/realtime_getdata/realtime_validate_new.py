import os
import numpy as np
import time
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

def startLoop():
    """
    開始接收雷達數據並進行即時預測
    """
    global buffer  # 使用全局變量 buffer
    # 創建接收器來獲取 RDI 和 PHD 圖
    R = FeatureMapReceiver(chirps=32)  # 創建接收器來接收 RDI 和 PHD 圖
    R.trigger(chirps=32)  # 在接收數據前觸發接收器
    time.sleep(0.5)
    print('# ======== 開始接收手勢數據 ===========')
    
    while True:  # 循環接收數據
        res = R.getResults()  # 從接收器獲取數據
        if res is None:
            continue

        # print(f"res type: {type(res)}")  # 輸出 res 的型態
        # print(f"res shape: {res.shape}")
        # print(f"res content: {res}")  # 輸出 res 的內容

        res = list(res)  # 將 tuple 轉換為 list 以進行修改

        # res = list(res)  # 將 tuple 轉換為 list 以進行修改

        # 打印 res 的類型和每個元素的形狀
        print(f"res type: {type(res)}")
        for i, arr in enumerate(res):
            if isinstance(arr, np.ndarray):  # 確保元素是 numpy array
                print(f"Shape of res[{i}]: {arr.shape}")
            else:
                print(f"res[{i}] is not a numpy array, it is of type {type(arr)}")
        
        # 將新數據插入 buffer 中，並進行預測
        buffer = np.roll(buffer, shift=-1, axis=-1)  # 將 buffer 左移，丟棄最舊的幀
        buffer[..., -1] = res[0]  # 將新幀放入 buffer 的最後位置
        
        # 當 buffer 填滿時進行預測
        if buffer.shape[-1] == WINDOW_SIZE:
            window_feature = np.expand_dims(buffer, axis=0)  # 增加 batch 維度
            
            # 進行數據縮放，與訓練時一致
            window_feature = window_feature.astype('float32') / 255.0
            
            predictions = model.predict(window_feature)[0]  # 獲取預測結果
            
            # 格式化輸出結果
            background_prob = predictions[0]
            forward_prob = predictions[1]
            right_prob = predictions[2]

            if forward_prob > 0.5:
                output = f"預測結果為forward: background: {background_prob:.2f}, forward: {forward_prob:.2f}, right: {right_prob:.2f}"
                print(output)
            elif right_prob > 0.5:
                output = f"預測結果為right: background: {background_prob:.2f}, forward: {forward_prob:.2f}, right: {right_prob:.2f}"
                print(output)
            else:
                output = f"預測結果為background: background: {background_prob:.2f}, forward: {forward_prob:.2f}, right: {right_prob:.2f}"

            # print(output)  # 輸出結果

def main():
    """
    主函數，負責設定和啟動數據接收與處理
    """
    kgl.setLib()  # 初始化 KKT 模組

    connect()  # 首先連接裝置
    startSetting()  # 設定硬體 AI 和 RF 參數
    startLoop()  # 最後進入數據接收和處理循環

if __name__ == '__main__':
    main()
