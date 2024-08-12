import h5py

# # 替換為你的 .h5 文件路徑
# file_path = "./data/stone/ThirdGesture_0001_2024_07_28_18_12_17.h5"

# with h5py.File(file_path, 'r') as f:
#     # 列出所有的 keys (頂層資料集名稱)
#     print("Keys in the file:", list(f.keys()))
    
#     # 如果 'DS1' 和 'label' 存在，顯示它們的形狀和數據類型
#     if 'DS1' in f:
#         print("DS1 shape:", f['DS1'].shape)
#         print("DS1 dtype:", f['DS1'].dty
# 
# 
# pe)
    
#     if 'label' in f:
#         print("label shape:", f['label'].shape)
#         print("label dtype:", f['label'].dtype)



# import numpy as np

# def read_npz_file(npz_file_path):
#     """
#     讀取並顯示 .npz 文件中的數據集資訊
#     Args:
#         npz_file_path (str): .npz 文件的路徑
#     """
#     data = np.load(npz_file_path)
    
#     # 列出所有儲存的數據集名稱
#     print("Data keys in the .npz file:", data.files)
    
#     # 遍歷每個數據集，顯示它們的形狀和數據類型
#     for key in data.files:
#         print(f"Dataset '{key}': shape = {data[key].shape}, dtype = {data[key].dtype}")
    
#     # 如果需要檢查某個特定數據集的數值內容，可以這樣做
#     # print("Example data from 'features':", data['features'][0])

# if __name__ == "__main__":
#     # 替換成你的 .npz 文件路徑
#     npz_file_path = 'processed_data.npz'
#     read_npz_file(npz_file_path)


import numpy as np
import matplotlib.pyplot as plt

# 載入處理後的數據
npz_file_path = 'processed_data.npz'
data = np.load(npz_file_path)

# 取得數據集
features = data['features']
labels = data['labels']
ground_truths = data['ground_truths']

def plot_data(index):
    """
    畫出指定索引的 labels 和 ground_truths 圖片
    Args:
        index (int): 資料索引
    """
    fig, axs = plt.subplots(2, 1, figsize=(10, 8))  # 產生兩個子圖，垂直排列

    # 第一張圖：labels
    axs[0].plot(labels[index], label='Label')
    axs[0].set_title(f'Labels for Index {index}')
    axs[0].set_xlabel('Frames')
    axs[0].set_ylabel('Label')
    axs[0].set_ylim(-0.1, 1.1)  # 設定縱軸範圍為 0-1
    axs[0].legend()

    # 第二張圖：ground_truths
    for i in range(ground_truths.shape[2]):  # ground_truths.shape[2] 表示四種類型
        axs[1].plot(ground_truths[index][:, i], label=f'Class {i}')
    axs[1].set_title(f'Ground Truths for Index {index}')
    axs[1].set_xlabel('Frames')
    axs[1].set_ylabel('Probability')
    axs[1].set_ylim(-0.1, 1.1)  # 設定縱軸範圍為 0-1
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
            if 0 <= index < len(labels):
                plot_data(index)
            else:
                print(f"Index out of range. Please enter a number between 0 and 799.")
        except ValueError:
            print("Invalid input. Please enter a valid number or 's' to stop.")

if __name__ == "__main__":
    main()






