import os
import h5py
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d

# 資料夾路徑
DATA_DIR = 'data/newdata'  # 原始數據所在的資料夾
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, 'processed_data')  # 處理後數據儲存的資料夾
PROCESSED_DATA_FILE = os.path.join(PROCESSED_DATA_DIR, 'processed_data_new.npz')  # 儲存處理後數據的檔案名稱和路徑
WINDOW_SIZE = 30  # 設定frame數量的窗口大小

# 定義新的手勢類型
gesture_types = ['background', 'forward', 'right']

def load_h5_file(file_path):
    """
    載入 .h5 檔案並提取 DS1 和 LABEL 數據
    Args:
        file_path (str): h5檔案路徑
    Returns:
        tuple: DS1 數據和 LABEL 數據
    """
    with h5py.File(file_path, 'r') as f:
        ds1 = np.array(f['DS1'], dtype=np.float32)  # 轉換為 float32 以避免溢出
        label = np.array(f['LABEL'])  # 修改這裡的名稱為 'LABEL'
    return ds1, label

# 標準化的部分被註解掉了
# def standardize_feature_map(feature_map):
#     """
#     標準化 feature map 的數據，使其均值為0，標準差為1
#     Args:
#         feature_map (np.array): 原始 feature map 數據
#     Returns:
#         np.array: 標準化後的 feature map 數據
#     """
#     mean = np.mean(feature_map, axis=(1, 2), keepdims=True)  # 計算每個frame的均值
#     std = np.std(feature_map, axis=(1, 2), keepdims=True)    # 計算每個frame的標準差
#     standardized_map = (feature_map - mean) / (std + 1e-6)   # 避免除以0的情況
#     return standardized_map

def generate_ground_truth(label, gesture_type, total_classes):
    """
    生成 ground_truth, 基於label從 0 變成 1 的區域
    Args:
        label (np.array): 標籤數據
        gesture_type (int): 當前手勢的類型索引
        total_classes (int): 手勢類型的總數
    Returns:
        np.array: 生成的 ground_truth
    """
    ground_truth = np.zeros((len(label), total_classes))

    # 找到手勢開始和結束的位置
    gesture_indices = np.where(label == 1)[0]
    
    if len(gesture_indices) == 0:
        # 如果没有手势（即全为背景），直接将 Class 0 设为1，其他为0
        ground_truth[:, 0] = 1
        return ground_truth
    
    start_idx = gesture_indices[0]
    end_idx = gesture_indices[-1]

    # 生成對稱的高斯分佈，從 0 上升到 1 再下降到 0
    length = end_idx - start_idx + 1
    center = length // 2
    x = np.arange(0, length) - center
    sigma = length / 6
    gaussian_curve = np.exp(-0.5 * (x / sigma) ** 2)

    # 正規化高斯曲線，使其最大值為 1
    gaussian_curve /= gaussian_curve.max()

    ground_truth[start_idx:end_idx+1, gesture_type] = gaussian_curve

    # 背景分數是 1 減去手勢分數
    ground_truth[:, 0] = 1 - ground_truth[:, gesture_type]
    
    return ground_truth


def process_data():
    """
    處理所有資料夾內的 .h5 檔案，生成包含ground_truth的處理後數據
    """
    # 確保儲存處理後數據的資料夾存在
    if not os.path.exists(PROCESSED_DATA_DIR):
        os.makedirs(PROCESSED_DATA_DIR)

    all_features = []
    all_labels = []
    all_ground_truths = []

    for gesture_idx, gesture_type in enumerate(gesture_types):
        gesture_dir = os.path.join(DATA_DIR, gesture_type)
        for file_name in os.listdir(gesture_dir):
            if file_name.endswith('.h5'):
                file_path = os.path.join(gesture_dir, file_name)
                
                # 載入 .h5 檔案
                ds1, label = load_h5_file(file_path)

                # # 標準化處理被註解掉了
                # ds1[0] = standardize_feature_map(ds1[0])  # 標準化 RDI map
                # ds1[1] = standardize_feature_map(ds1[1])  # 標準化 PHD map

                # 生成 ground truth
                ground_truth = generate_ground_truth(label, gesture_idx, len(gesture_types))

                # 儲存處理後的數據
                all_features.append(ds1)
                all_labels.append(label)
                all_ground_truths.append(ground_truth)

    # 將所有處理後的數據儲存成一個檔案
    np.savez(PROCESSED_DATA_FILE, features=np.array(all_features), labels=np.array(all_labels), ground_truths=np.array(all_ground_truths))
    print(f'成功儲存處理後的數據到 {PROCESSED_DATA_FILE}')

if __name__ == '__main__':
    process_data()
