import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras.models import load_model

# 載入處理後的數據
npz_file_path = 'data/processed_data/processed_data_new.npz'
data = np.load(npz_file_path)

# 只讀取 features 和 ground_truths
features = data['features']
ground_truths = data['ground_truths']

# 對特徵進行標準化處理
features = features.astype('float32') / 255.0

# 載入訓練好的模型
model_path = 'output/models/3d_cnn_model_20240817_185529.h5'  # 修改為你的模型路徑
model = load_model(model_path)

# 打印數據集的資料型態和意思
print("Data loaded from 'processed_data_new.npz':")
print(f"features: {features.shape}, dtype: {features.dtype} - 原始數據的特徵數據")
print(f"ground_truths: {ground_truths.shape}, dtype: {ground_truths.dtype} - 生成的Ground Truth數據（可能是高斯分佈）")
print()

def plot_ground_truth_and_predictions(index):
    """
    畫出指定索引的 ground_truths 和模型預測的結果圖片
    Args:
        index (int): 資料索引
    """
    # 設定 sliding window 的大小
    window_size = 30
    
    # 初始化預測結果的陣列，長度與 ground_truth 一致
    predictions = np.zeros((ground_truths.shape[1], ground_truths.shape[2]))

    # 用 sliding window 進行預測
    for start in range(ground_truths.shape[1] - window_size + 1):
        mid = start + window_size // 2  # 計算滑動窗口中間位置
        window_feature = features[index, :, :, :, start:start + window_size]
        window_feature = np.expand_dims(window_feature, axis=0)  # 增加 batch 維度
        window_prediction = model.predict(window_feature)
        predictions[mid] = window_prediction  # 將結果填入對應的 frames

    # 將前15個frames和最後15個frames設定為背景
    predictions[:15, 0] = 1
    predictions[:15, 1:] = 0
    predictions[-15:, 0] = 1
    predictions[-15:, 1:] = 0

    # 畫出 Ground Truth 和預測結果
    fig, axs = plt.subplots(2, 1, figsize=(10, 8))  # 產生兩個子圖，垂直排列

    # 第一張圖：Ground Truths
    for i in range(ground_truths.shape[2]):
        axs[0].plot(ground_truths[index][:, i], label=f'Class {i}')
    axs[0].set_title(f'Ground Truths for Index {index}')
    axs[0].set_xlabel('Frames')
    axs[0].set_ylabel('Probability')
    axs[0].set_ylim(-0.1, 1.1)
    axs[0].legend()

    # 第二張圖：Predictions
    for i in range(predictions.shape[1]):
        axs[1].plot(predictions[:, i], label=f'Class {i}')
    axs[1].set_title(f'Predictions for Index {index}')
    axs[1].set_xlabel('Frames')
    axs[1].set_ylabel('Probability')
    axs[1].set_ylim(-0.1, 1.1)
    axs[1].legend()

    plt.tight_layout()  # 自動調整子圖間距
    plt.show()

def main():
    while True:
        user_input = input("Enter an index (0-799) to plot or 's' to stop: ").strip()
        if user_input.lower() == 's':
            break

        try:
            index = int(user_input)
            if 0 <= index < ground_truths.shape[0]:
                plot_ground_truth_and_predictions(index)
            else:
                print(f"Index out of range. Please enter a number between 0 and {ground_truths.shape[0] - 1}.")
        except ValueError:
            print("Invalid input. Please enter a valid number or 's' to stop.")

if __name__ == "__main__":
    main()
