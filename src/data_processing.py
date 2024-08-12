import os
import h5py
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d

# 資料夾路徑
DATA_DIR = 'data/'
PROCESSED_DATA_FILE = 'processed_data.npz'  # 儲存處理後數據的檔案名稱
WINDOW_SIZE = 70  # 設定frame數量的窗口大小

# 定義手勢類型
gesture_types = ['background', 'Stone', 'Swing_Left', 'Swing_Right']

def load_h5_file(file_path):
    """
    載入 .h5 檔案並提取 DS1 和 LABEL 數據
    Args:
        file_path (str): h5檔案路徑
    Returns:
        tuple: DS1 數據和 LABEL 數據
    """
    with h5py.File(file_path, 'r') as f:
        ds1 = np.array(f['DS1'])
        label = np.array(f['LABEL'])  # 修改這裡的名稱為 'LABEL'
    return ds1, label

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
        return ground_truth
    
    start_idx = gesture_indices[0]
    end_idx = gesture_indices[-1]

    # 生成平滑的 ground truth，使用高斯過濾
    ground_truth[start_idx:end_idx+1, gesture_type] = gaussian_filter1d(
        np.ones(end_idx - start_idx + 1), sigma=(end_idx - start_idx) / 6)

    # 背景分數是 1 減去手勢分數
    ground_truth[:, 0] = 1 - ground_truth[:, gesture_type]
    
    return ground_truth

def process_data():
    """
    處理所有資料夾內的 .h5 檔案，生成包含ground_truth的處理後數據
    """
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

                # 生成 ground truth
                ground_truth = generate_ground_truth(label, gesture_idx, len(gesture_types))

                # 儲存處理後的數據
                all_features.append(ds1)
                all_labels.append(label)
                all_ground_truths.append(ground_truth)

                # 驗證生成的 ground truth
                plt.figure(figsize=(10, 2))
                plt.title(f'Ground Truth for {gesture_type} in {file_name}')
                plt.plot(ground_truth[:, gesture_idx], label=gesture_type)
                plt.plot(ground_truth[:, 0], label='background')
                plt.legend()
                plt.show()

    # 將所有處理後的數據儲存成一個檔案
    np.savez(PROCESSED_DATA_FILE, features=np.array(all_features), labels=np.array(all_labels), ground_truths=np.array(all_ground_truths))
    print(f'成功儲存處理後的數據到 {PROCESSED_DATA_FILE}')

if __name__ == '__main__':
    process_data()
