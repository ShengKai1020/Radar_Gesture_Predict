import os
import matplotlib.pyplot as plt
import numpy as np

# 設定曲線保存目錄
CURVE_SAVE_PATH = "output/curves"
NUM_CLASSES = 4
EPOCHS = 20

def plot_train_history(history, model_name):
    """
    繪製訓練和驗證損失的圖表。
    """
    if not os.path.exists(CURVE_SAVE_PATH):
        os.makedirs(CURVE_SAVE_PATH)

    plt.plot(history['loss'], label='Train Loss')
    plt.plot(history['val_loss'], label='Validation Loss')
    plt.legend()
    plt.title('Train and Validation Loss', fontweight='bold')

    savefig_name = os.path.join(
        CURVE_SAVE_PATH,
        f'{model_name}_{NUM_CLASSES}_Gesture_{EPOCHS}_epoch.png',
    )
    plt.savefig(savefig_name)
    print(f'成功儲存損失圖表於 {savefig_name}')
    plt.show()

def main():
    # 加載保存的訓練歷史數據（假設你保存了訓練歷史）
    history_file = "path_to_saved_history.npy"  # 修改為保存歷史的真實路徑
    history = np.load(history_file, allow_pickle=True).item()

    # 使用保存的模型名稱
    model_name = "3d_cnn_model_{timestamp}"  # 你應該確保這個名稱與保存的名稱一致

    plot_train_history(history, model_name)

if __name__ == "__main__":
    main()
