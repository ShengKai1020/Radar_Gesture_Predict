import numpy as np
import h5py
import matplotlib.pyplot as plt

# 檔案路徑
h5_file_path = 'data/test/Background_0001_2024_08_18_13_54_35.h5'
npy_file_path = 'data/test/collected_data.npy'

def load_h5_data(file_path):
    """
    從 .h5 檔案中讀取 DS1 的數據
    Args:
        file_path (str): h5 檔案的路徑
    Returns:
        np.array: DS1 的數據
    """
    with h5py.File(file_path, 'r') as f:
        ds1_data = np.array(f['DS1'])
    return ds1_data

def load_npy_data(file_path):
    """
    從 .npy 檔案中讀取數據
    Args:
        file_path (str): npy 檔案的路徑
    Returns:
        np.array: 讀取的數據
    """
    data = np.load(file_path)
    return data

def plot_data(ds1_data, npy_data):
    """
    從第一個frame開始畫圖，一直到第2000個frame
    Args:
        ds1_data (np.array): 來自 h5 的數據
        npy_data (np.array): 來自 npy 的數據
    """
    fig, axs = plt.subplots(2, 2, figsize=(12, 8))

    # 计算两个数据集中最小值和最大值
    min_val = min(np.min(ds1_data), np.min(npy_data))
    max_val = max(np.max(ds1_data), np.max(npy_data))

    min_val = 0
    max_val = 50
    for frame_idx in range(2000):
        # 清除前一帧的图像
        axs[0, 0].cla()
        axs[1, 0].cla()
        axs[0, 1].cla()
        axs[1, 1].cla()

        # 确保数据类型为 float32
        ds1_rdi = ds1_data[0, :, :, frame_idx].astype(np.float32)
        ds1_phd = ds1_data[1, :, :, frame_idx].astype(np.float32)
        npy_rdi = npy_data[0, :, :, frame_idx].astype(np.float32)
        npy_phd = npy_data[1, :, :, frame_idx].astype(np.float32)

        # RDI from h5
        axs[0, 0].imshow(ds1_rdi, cmap='jet', vmin=min_val, vmax=max_val)
        axs[0, 0].set_title('RDI from h5')

        # PHD from h5
        axs[1, 0].imshow(ds1_phd, cmap='jet', vmin=min_val, vmax=max_val)
        axs[1, 0].set_title('PHD from h5')

        # RDI from npy
        axs[0, 1].imshow(npy_rdi, cmap='jet', vmin=min_val, vmax=max_val)
        axs[0, 1].set_title('RDI from npy')

        # PHD from npy
        axs[1, 1].imshow(npy_phd, cmap='jet', vmin=min_val, vmax=max_val)
        axs[1, 1].set_title('PHD from npy')

        # 更新图像
        plt.pause(0.001)  # 控制每帧之间的间隔时间
        fig.canvas.draw()

    plt.show()

def main():
    # 讀取 h5 檔案和 npy 檔案中的數據
    ds1_data = load_h5_data(h5_file_path)
    npy_data = load_npy_data(npy_file_path)

    # 開始連續顯示圖像
    plot_data(ds1_data, npy_data)

if __name__ == "__main__":
    main()
