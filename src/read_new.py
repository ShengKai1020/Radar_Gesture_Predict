import numpy as np
import matplotlib.pyplot as plt

# 載入處理後的數據
npz_file_path = 'data/processed_data/processed_data_new.npz'
data = np.load(npz_file_path)

# 打印數據集的資料型態和意思
print("Data loaded from 'processed_data.npz':")
print(f"features: {data['features'].shape}, dtype: {data['features'].dtype} - 原始數據的特徵數據")
print(f"labels: {data['labels'].shape}, dtype: {data['labels'].dtype} - 對應的標籤數據")
print(f"ground_truths: {data['ground_truths'].shape}, dtype: {data['ground_truths'].dtype} - 生成的Ground Truth數據（可能是高斯分佈）")
print()

# 取得數據集
features = data['features']
labels = data['labels']
ground_truths = data['ground_truths']

def get_max_label_interval(label):
    """
    找出 label 中連續為 1 的最大區間長度
    Args:
        label (np.array): 單個資料索引的標籤數據
    Returns:
        int: 最大區間長度
    """
    max_interval = 0
    current_interval = 0
    
    for value in label:
        if value == 1:
            current_interval += 1
        else:
            if current_interval > max_interval:
                max_interval = current_interval
            current_interval = 0
    
    return max(max_interval, current_interval)  # 如果最后一段是最长的，直接返回

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
    for i in range(ground_truths.shape[2]):  # ground_truths.shape[2] 表示類別數量
        axs[1].plot(ground_truths[index][:, i], label=f'Class {i}')
    axs[1].set_title(f'Ground Truths for Index {index}')
    axs[1].set_xlabel('Frames')
    axs[1].set_ylabel('Probability')
    axs[1].set_ylim(-0.1, 1.1)  # 設定縱軸範圍為 0-1
    axs[1].legend()

    plt.tight_layout()  # 自動調整子圖間距
    plt.show()

def analyze_label_intervals():
    """
    分析所有 labels 中的最大區間，並統計每個區間範圍內的 label 長度數量
    """
    interval_counts = {
        "0": 0,
        "10-15": 0,
        "16-20": 0,
        "21-25": 0,
        "26-30": 0,
        "31-35": 0,
        "36-40": 0
    }

    for label in labels:
        max_interval = get_max_label_interval(label)
        
        if max_interval == 0:
            interval_counts["0"] += 1
        elif 10 <= max_interval <= 15:
            interval_counts["10-15"] += 1
        elif 16 <= max_interval <= 20:
            interval_counts["16-20"] += 1
        elif 21 <= max_interval <= 25:
            interval_counts["21-25"] += 1
        elif 26 <= max_interval <= 30:
            interval_counts["26-30"] += 1
        elif 31 <= max_interval <= 35:
            interval_counts["31-35"] += 1
        elif 36 <= max_interval <= 40:
            interval_counts["36-40"] += 1

    print("Label interval counts:")
    for interval, count in interval_counts.items():
        print(f"{interval}: {count}")

def main():
    analyze_label_intervals()  # 分析並打印 label 最大區間統計

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
