import os
import numpy as np
import tensorflow as tf
from sklearn.metrics import confusion_matrix, classification_report
import seaborn as sns
import matplotlib.pyplot as plt

# 设置文件路径
DATA_FILE = 'data/processed_data/processed_data.npz'  # 数据文件路径
MODEL_FILE = 'output/models/3d_cnn_model_20240815_145251.h5'  # 模型文件路径
WINDOW_SIZE = 40  # 滑动窗口大小
STEP_SIZE = 1  # 滑动窗口步长

# 加载模型
model = tf.keras.models.load_model(MODEL_FILE)
print(f'模型已加載：{MODEL_FILE}')

def validate_model():
    """
    通过滑动窗口方法对数据进行预测并生成混淆矩阵。
    """
    # 加载数据
    data = np.load(DATA_FILE)
    X = data['features']
    y = data['labels']

    # 将数据分成滑动窗口
    X_windows = []
    y_true = []

    for i in range(X.shape[0]):
        for start in range(0, X.shape[-1] - WINDOW_SIZE + 1, STEP_SIZE):
            end = start + WINDOW_SIZE
            X_windows.append(X[i, :, :, :, start:end])
            y_true.append(y[i, end - 1])  # 取每个滑动窗口的最后一帧作为真实标签

    X_windows = np.array(X_windows)

    # 验证集滑动窗口
    y_pred = []
    
    for i in range(X_windows.shape[0]):
        window_pred = model.predict(np.expand_dims(X_windows[i], axis=0))
        y_pred.append(np.argmax(window_pred, axis=-1))

    y_pred = np.array(y_pred).flatten()
    y_true = np.array(y_true).flatten()

    # 打印分类报告
    print("Classification Report:")
    print(classification_report(y_true, y_pred, target_names=['Background', 'Stone', 'Swing_Left', 'Swing_Right']))

    # 绘制混淆矩阵
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(10, 7))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Background', 'Stone', 'Swing_Left', 'Swing_Right'], yticklabels=['Background', 'Stone', 'Swing_Left', 'Swing_Right'])
    plt.xlabel('Predicted')
    plt.ylabel('True')
    plt.title('Confusion Matrix')
    plt.show()

if __name__ == '__main__':
    validate_model()
