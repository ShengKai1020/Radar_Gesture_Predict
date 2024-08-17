import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv3D, MaxPooling3D, Flatten, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import time

# 確保使用 GPU
gpus = tf.config.list_physical_devices('GPU')
if gpus:
    try:
        tf.config.experimental.set_memory_growth(gpus[0], True)
        tf.config.set_visible_devices(gpus[0], 'GPU')
        print(f"使用 GPU: {gpus[0]}")
    except RuntimeError as e:
        print(e)
else:
    print("未檢測到 GPU，將使用 CPU 進行運算。")

# 設定數據和參數
DATA_DIR = 'data/processed_data/processed_data_new.npz'  # 已處理數據的路徑
WINDOW_SIZE = 30  # 滑動窗口大小
STEP_SIZE = 1  # 滑動窗口的步長
BATCH_SIZE = 32  # 批次大小
EPOCHS = 20  # 訓練的回合數
NUM_CLASSES = 3  # 手勢類別數量

# 設定模型保存和輸出目錄
MODEL_SAVE_PATH = "output/models"
CURVE_SAVE_PATH = "output/curves"
LOG_DIR = 'logs/training_logs'
timestamp = time.strftime('%Y%m%d_%H%M%S', time.localtime(time.time()))

# 定義手勢類型
gesture_types = ['background', 'forward', 'right']

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
            mid = start + WINDOW_SIZE // 2  # 取中間位置的 frame

            X.append(feature[:, :, :, start:end])
            y.append(ground_truth[mid])  # 使用滑動窗口中間的frame的ground_truth作為標籤

    X = np.array(X)
    y = np.array(y)

    # 標準化處理
    X = X.astype('float32') / 255.0

    return X, y

def build_3d_cnn_model(input_shape, num_classes, learning_rate=1e-4):
    """
    構建 3D CNN 模型。

    參數:
        input_shape (tuple): 輸入數據的形狀
        num_classes (int): 分類的數量
        learning_rate (float): 優化器的學習率

    返回:
        keras.Model: 編譯後的模型
    """
    model = Sequential([
        Conv3D(32, kernel_size=(2, 3, 3), activation='relu', input_shape=input_shape),
        MaxPooling3D(pool_size=(1, 2, 2)),
        Conv3D(64, kernel_size=(1, 3, 3), activation='relu'),
        MaxPooling3D(pool_size=(1, 2, 2)),
        Conv3D(128, kernel_size=(1, 3, 3), activation='relu'),
        MaxPooling3D(pool_size=(1, 2, 2)),
        Flatten(),
        Dense(128, activation='relu'),
        Dropout(0.5),
        Dense(num_classes, activation='softmax')
    ])

    # 使用較低的學習率
    optimizer = Adam(learning_rate=learning_rate)
    model.compile(optimizer=optimizer, loss='mean_squared_error', metrics=['accuracy'])
    return model

def train_model(X, y):
    """
    訓練模型並保存。
    """
    # 切分數據集
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

    # 獲取輸入形狀和類別數量
    input_shape = X_train.shape[1:]  # (2, 32, 32, 30)
    num_classes = y_train.shape[-1]  # 類別數量

    # 構建和編譯模型
    model = build_3d_cnn_model(input_shape, num_classes)

    # 設置模型保存路徑
    model_name = f"3d_cnn_model_{timestamp}.h5"
    model_save_path = os.path.join(MODEL_SAVE_PATH, model_name)

    # 確保保存模型和圖表的目錄存在
    if not os.path.exists(MODEL_SAVE_PATH):
        os.makedirs(MODEL_SAVE_PATH)
    if not os.path.exists(CURVE_SAVE_PATH):
        os.makedirs(CURVE_SAVE_PATH)
    
    # 訓練模型
    history = model.fit(X_train, y_train, batch_size=BATCH_SIZE, epochs=EPOCHS, validation_data=(X_val, y_val))

    # 保存模型
    model.save(model_save_path)
    print(f"模型訓練完成並保存為 {model_save_path}")

    return model, history

def plot_train_history(history, model_name):
    """
    繪製訓練和驗證損失的圖表。
    """
    # Plot the loss history
    plt.plot(history.history['loss'], label='Train Loss')
    plt.plot(history.history['val_loss'], label='Validation Loss')
    plt.legend()
    plt.title('Train and Validation Loss', fontweight='bold')

    # Save the plot of loss history
    savefig_name = os.path.join(
        CURVE_SAVE_PATH,
        f'{model_name}_{NUM_CLASSES}_Gesture_{EPOCHS}_epoch.png',
    )
    plt.savefig(savefig_name)
    print(f'成功儲存損失圖表於 {savefig_name}')
    plt.show()

def main():
    """
    主函數，用於加載數據和訓練模型。
    """
    # 加載數據
    X, y = load_data()

    # 訓練模型
    model, history = train_model(X, y)

    # 繪製訓練歷史
    plot_train_history(history, model_name=f"3d_cnn_model_{timestamp}")

if __name__ == "__main__":
    main()
