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
TOTAL_FRAMES = 2000  # 需要收集的總 frame 數量
collected_frames = 0  # 已收集的 frame 數量
data_storage = np.zeros((2, 32, 32, TOTAL_FRAMES), dtype=np.float32)  # 用於存儲的數組

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
    global collected_frames, data_storage, buffer  # 使用全局變量 buffer 和 data_storage

    # 記錄開始時間
    start_time = time.time()

    # 創建接收器來獲取 RDI 和 PHD 圖
    R = FeatureMapReceiver(chirps=32)  # 創建接收器來接收 RDI 和 PHD 圖
    R.trigger(chirps=32)  # 在接收數據前觸發接收器
    time.sleep(0.5)
    print('# ======== 開始接收手勢數據 ===========')
    
    while collected_frames < TOTAL_FRAMES:  # 當收集的幀數少於總幀數時繼續運行
        res = R.getResults()  # 從接收器獲取數據
        if res is None:
            continue

        res = list(res)  # 將 tuple 轉換為 list 以進行修改

        # # 先对矩阵进行转置操作
        # res[0] = np.transpose(res[0])  # 对第一个矩阵执行 X 轴和 Y 轴的转置
        # res[1] = np.transpose(res[1])  # 对第二个矩阵执行 X 轴和 Y 轴的转置
        
        # 保存數據到 data_storage
        data_storage[..., collected_frames] = res  # 保存當前幀到數據存儲

        collected_frames += 1  # 更新收集的幀數

        # 停止條件
        if collected_frames >= TOTAL_FRAMES:
            print("已收集 2000 個幀，停止接收數據。")
            break

    # 記錄結束時間並計算總時間
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"收集 2000 個幀共花費時間: {elapsed_time:.2f} 秒")

    # 保存數據到文件
    save_data()

def save_data():
    """
    保存收集的數據到文件
    """
    np.save('collected_data.npy', data_storage)
    print("數據已保存到 collected_data.npy")

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
