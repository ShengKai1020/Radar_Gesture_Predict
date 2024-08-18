import numpy as np
import h5py
import matplotlib.pyplot as plt

# 檔案路徑
h5_file_path = 'data/test/FirstGesture_0050_2024_08_17_15_03_23.h5'

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

def plot_continuous_rdi_phd(ds1_data):
    """
    連續顯示 RDI 和 PHD 图像
    Args:
        ds1_data (np.array): 來自 h5 的數據
    """
    fig, axs = plt.subplots(1, 2, figsize=(10, 5))

    # 初始化图像对象
    rdi_im = axs[0].imshow(ds1_data[0, :, :, 0].astype(np.float32), cmap='viridis')
    axs[0].set_title('RDI')

    phd_im = axs[1].imshow(ds1_data[1, :, :, 0].astype(np.float32), cmap='viridis')
    axs[1].set_title('PHD')

    plt.ion()  # 开启交互模式

    for frame_idx in range(ds1_data.shape[3]):  # 遍歷所有帧
        # 确保数据类型为 float32
        ds1_rdi = ds1_data[0, :, :, frame_idx].astype(np.float32)
        ds1_phd = ds1_data[1, :, :, frame_idx].astype(np.float32)

        # 更新 RDI 图像
        rdi_im.set_data(ds1_rdi)
        axs[0].set_title(f'RDI at Frame {frame_idx}')
        
        # 更新 PHD 图像
        phd_im.set_data(ds1_phd)
        axs[1].set_title(f'PHD at Frame {frame_idx}')

        plt.pause(0.02)  # 控制每帧之间的间隔时间

    plt.ioff()  # 关闭交互模式
    plt.show()

def main():
    # 讀取 h5 檔案中的數據
    ds1_data = load_h5_data(h5_file_path)

    # 連續顯示 RDI 和 PHD 圖像
    plot_continuous_rdi_phd(ds1_data)

if __name__ == "__main__":
    main()
