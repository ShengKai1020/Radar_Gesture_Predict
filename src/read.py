import h5py

# 替換為你的 .h5 文件路徑
file_path = "./data/stone/ThirdGesture_0001_2024_07_28_18_12_17.h5"

with h5py.File(file_path, 'r') as f:
    # 列出所有的 keys (頂層資料集名稱)
    print("Keys in the file:", list(f.keys()))
    
    # 如果 'DS1' 和 'label' 存在，顯示它們的形狀和數據類型
    if 'DS1' in f:
        print("DS1 shape:", f['DS1'].shape)
        print("DS1 dtype:", f['DS1'].dtype)
    
    if 'label' in f:
        print("label shape:", f['label'].shape)
        print("label dtype:", f['label'].dtype)