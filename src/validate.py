import os
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
from tensorflow.keras.models import load_model
import h5py

# 模型和數據路徑
MODEL_PATH = 'output/models/3d_cnn_model_20240813_131109.h5'
TEST_DATA_DIR = 'data/Stone'  # 測試資料夾，可以換成其他手勢資料夾

WINDOW_SIZE = 40  # 與訓練時一致的滑動窗口大小
STEP_SIZE = 1  # 與訓練時一致的滑動窗口步長

def load_h5_file(file_path):
    """
    載入 .h5 檔案並提取 DS1 數據
    Args:
        file_path (str): h5檔案路徑
    Returns:
        np.array: DS1 數據
    """
    with h5py.File(file_path, 'r') as f:
        ds1 = np.array(f['DS1'])
    return ds1

def preprocess_data(ds1):
    """
    預處理數據，應用滑動窗口
    Args:
        ds1 (np.array): 載入的數據
    Returns:
        np.array: 處理後的數據
    """
    X = []
    for start in range(0, ds1.shape[-1] - WINDOW_SIZE + 1, STEP_SIZE):
        end = start + WINDOW_SIZE
        X.append(ds1[:, :, :, start:end])
    X = np.array(X)
    X = X.astype('float32') / 255.0  # 標準化
    return X

def visualize_prediction(predictions, file_name):
    """
    視覺化預測結果
    Args:
        predictions (np.array): 預測結果
        file_name (str): 測試檔案名稱
    """
    plt.figure(figsize=(10, 6))
    for i in range(predictions.shape[1]):
        plt.plot(predictions[:, i], label=f'Class {i}')
    plt.title(f'Predictions for {file_name}')
    plt.xlabel('Frame')
    plt.ylabel('Probability')
    plt.legend()
    plt.show()

def validate_model():
    """
    加載模型並對測試數據進行驗證
    """
    # 加載模型
    model = load_model(MODEL_PATH)
    print(f"模型已加載：{MODEL_PATH}")

    # 處理測試資料夾內的所有 .h5 檔案
    for file_name in os.listdir(TEST_DATA_DIR):
        if file_name.endswith('.h5'):
            file_path = os.path.join(TEST_DATA_DIR, file_name)
            
            # 加載數據
            ds1 = load_h5_file(file_path)

            # 預處理數據
            X_test = preprocess_data(ds1)

            # 預測
            predictions = model.predict(X_test)

            # 可視化結果
            visualize_prediction(predictions, file_name)

if __name__ == '__main__':
    validate_model()
