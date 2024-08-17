import numpy as np

class PresenceDetect:
    def __init__(self):
        self.val_buff = 0
        self.current_peak = 0
        self.output = 0

        self.green_fps = 30  # 30 fps
        self.check_cnt = 0  # counter for check time
        self.present_hit = 0  # conunter for how many number of succesfully hit within 1sec
        self.time_counter = 0  # time counter
        self.hit_ratio = 0  # [0-1], hit ration of green fps, higher means harder to detect
        self.detected = False
        self.timebuffer = np.zeros(40)
        pass

    def FFT(self, res):
        # Get RX3 data and transform into floating point
        norm_ch1 = res[0] / (2 ** 15)
        # Reshape data into [128*32]
        norm_ch1 = norm_ch1.reshape((128, -1), order='F')
        # Average 32 chirps
        rawdata = np.average(norm_ch1, axis=1)
        # Set 65-128 point data as 0
        rawdata[64:] = 0
        # 128 Point FFT
        fast_rdi = np.fft.fft(rawdata, 128 * 1, axis=0)
        # Get abs value
        fast_rdi_abs = np.abs(fast_rdi[0:64])

        return fast_rdi_abs

    def FFT2(self, res):

        FT = np.fft.fft(res, axis=2)
        FT = abs(FT[:, :, 0:32])
        FT = np.mean(FT, axis=0)
        powerFT = np.mean(FT, axis=0)


        return powerFT

    def detect(self, res):
        #1. FFT each index "average"
        fast_rdi_abs = self.FFT2(res)
        #2. average FFT -> get FFT mean -> set threshold = 2 * mean
        threshold = np.mean(fast_rdi_abs)*2
        #3. FFT array > 2*mean --> get occupied feature (array)
        #  a. find nearest index
        fast_rdi_abs[0:4] = 0
        occupied_feat = np.where(fast_rdi_abs>threshold, 1, 0)
        #  b. if [sum(occupied feature)] > 0 & [nearest index > 0] -> presence feature = 1 ; else presence feature = 0
        if np.sum(occupied_feat) > 0 and np.min(np.where(occupied_feat==1)) > 0:
            pres_feat = 1
            self.val_buff = np.min(np.where(occupied_feat==1))
        else:
            pres_feat = 0
        #4. set time buffer (ex. 2 second) and put presence feature into timte buffer
        self.timebuffer[0] = pres_feat
        self.timebuffer = np.roll(self.timebuffer, 1)
        #5. sum (time buffer) & set time_threshold = length_time_buffer * N % (ex. N=15)
        N = 0.15
        time_threshold = len(self.timebuffer) * N
        #6. if sum (time buffer) >  time_threshold  presence_display = 1 & distance = nearest index * resolution
        if np.sum(self.timebuffer) > time_threshold:
            self.detected = 1
            self.current_peak = self.val_buff
        else:
            self.detected = 0
            self.current_peak = 0
        # print(self.timebuffer)
        thres_arr = []

        return self.current_peak, self.detected, thres_arr, fast_rdi_abs

    def detect_peaks(self, x, num_train=8, num_guard=10, rate_fa=0.01):
        """
        Detect peaks with CFAR algorithm.

        num_train: Number of training cells.
        num_guard: Number of guard cells.
        rate_fa: False alarm rate.
        """
        num_cells = x.size
        num_train_half = round(num_train / 2)
        num_guard_half = round(num_guard / 2)
        num_side = num_train_half + num_guard_half

        alpha = num_train * (rate_fa ** (-1 / num_train) - 1)  # threshold factor

        peak_idx = []
        threshold_arry = np.zeros(32)

        # for i in range(num_side, num_cells - num_side):
        for i in range(num_side, num_cells-2):
            if i != i - num_side + np.argmax(x[i - num_side:i + num_side + 1]):
                continue
            sum1 = np.sum(x[i - num_side:i + 1])
            sum2 = np.sum(x[i - num_guard_half:i + 1])
            p_noise = 2 * (sum1 - sum2) / num_train
            threshold = alpha * p_noise
            threshold_arry[i] = threshold

            if x[i] > threshold:
                peak_idx.append(i)
        peak_idx = np.array(peak_idx, dtype=int)
        # print(threshold_arry)
        # print(x)


        return peak_idx , threshold_arry