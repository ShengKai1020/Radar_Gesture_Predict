import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
import matplotlib.pyplot as plt

# 設定模型和數據的路徑
MODEL_PATH = 'output/models/3d_cnn_model_20240816_101253.h5'  # 替換為你實際的模型路徑
DATA_PATH = 'data/processed_data/processed_data.npz'  # 已處理數據的路徑

def load_data():
    """
    從已處理的 npz 文件中載入數據。
    """
    data = np.load(DATA_PATH)
    features = data['features']
    labels = data['labels']
    ground_truths = data['ground_truths']
    return features, labels, ground_truths

def predict_and_compare():
    """
    載入模型，進行預測並與 ground truth 進行比較。
    """
    # 載入已處理數據
    features, labels, ground_truths = load_data()

    # 載入模型
    model = load_model(MODEL_PATH)

    # 使用模型進行預測
    predictions = model.predict(features)

    # 比較預測結果與 ground truth
    for i in range(len(predictions)):
        print(f"Sample {i+1}:")
        print(f"Predicted: {predictions[i]}")
        print(f"Ground Truth: {ground_truths[i]}")
        print("=" * 30)

        # 如果需要，這裡可以加入更多的比較邏輯或可視化部分
        plt.plot(predictions[i], label='Prediction')
        plt.plot(ground_truths[i], label='Ground Truth')
        plt.legend()
        plt.show()

if __name__ == "__main__":
    predict_and_compare()
