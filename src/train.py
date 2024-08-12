import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv3D, MaxPooling3D, Flatten, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from sklearn.model_selection import train_test_split

# 設定數據和參數
DATA_DIR = 'data/processed_data/processed_data.npz'  # 已處理數據的路徑
WINDOW_SIZE = 40  # 滑動窗口大小
STEP_SIZE = 1  # 滑動窗口的步長
BATCH_SIZE = 32  # 批次大小
EPOCHS = 20  # 訓練的回合數

def load_data():
    """
    從 npz 文件中載入數據，並根據滑動窗口進行數據處理。

    返回:
        tuple: (訓練特徵, ground truths)
    """
    # 載入數據
    data = np.load(DATA_DIR)
    features = data['features']
    labels = data['labels']
    ground_truths = data['ground_truths']

    X = []
    y = []

    # 應用滑動窗口
    for i in range(len(features)):
        feature = features[i]
        ground_truth = ground_truths[i]
        for start in range(0, feature.shape[-1] - WINDOW_SIZE + 1, STEP_SIZE):
            end = start + WINDOW_SIZE
            X.append(feature[:, :, :, start:end])
            y.append(ground_truth[end - 1])  # 使用滑動窗口最後一個frame的ground_truth作為標籤

    X = np.array(X)
    y = np.array(y)

    return X, y

def build_3d_cnn_model(input_shape, num_classes):
    """
    構建 3D CNN 模型。

    參數:
        input_shape (tuple): 輸入數據的形狀
        num_classes (int): 分類的數量

    返回:
        keras.Model: 編譯後的模型
    """
    model = Sequential([
        Conv3D(32, kernel_size=(2, 3, 3), activation='relu', input_shape=input_shape),
        MaxPooling3D(pool_size=(1, 2, 2)),  # 在深度維度上使用 (1, 2, 2) 的內核大小
        Conv3D(64, kernel_size=(1, 3, 3), activation='relu'),  # 調整卷積核大小以避免減少深度維度
        MaxPooling3D(pool_size=(1, 2, 2)),  # 同樣的調整
        Conv3D(128, kernel_size=(1, 3, 3), activation='relu'),  # 調整卷積核大小
        MaxPooling3D(pool_size=(1, 2, 2)),  # 同樣的調整
        Flatten(),
        Dense(128, activation='relu'),
        Dropout(0.5),
        Dense(num_classes, activation='softmax')
    ])

    model.compile(optimizer=Adam(), loss='categorical_crossentropy', metrics=['accuracy'])
    return model

def main():
    """
    主函數，用於訓練模型。
    """
    # 載入數據
    X, y = load_data()

    # 切分數據集
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

    # 獲取輸入形狀和類別數量
    input_shape = X_train.shape[1:]  # (2, 32, 32, 40)
    num_classes = y_train.shape[-1]  # 類別數量

    # 構建和編譯模型
    model = build_3d_cnn_model(input_shape, num_classes)

    # 訓練模型
    model.fit(X_train, y_train, batch_size=BATCH_SIZE, epochs=EPOCHS, validation_data=(X_val, y_val))

    # 保存模型
    model.save('3d_cnn_gesture_model.h5')
    print("模型訓練完成並保存為 3d_cnn_gesture_model.h5")

if __name__ == '__main__':
    main()
