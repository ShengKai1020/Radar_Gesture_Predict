import numpy as np
class PostProcess:
    def __init__(self, bg_id=0):
        self._bg_id = int(bg_id)
        self._current_ges = self._bg_id
        self._rising_ges = self._bg_id
        self._gesture_flag = False

    def postprocess(self, preds:np.ndarray, lower_thd=0.5, upper_thd=0.6):
        """
        :param preds: A numpy array of model prediction with shape [classes, ]
        :param bg_id: Specific background ID
        :param lower_thd:
        :param upper_thd:
        :return: A tensor that has the same size as preds
        """
        if preds[self._bg_id] != preds.sum():
            preds[self._bg_id] = 0

        if self._gesture_flag and preds[self._current_ges] < lower_thd:
            # print('in 1')
            # print('current:{}'.format(self._current_ges))
            self._current_ges = self._bg_id
            self._gesture_flag = False

        if not (self._gesture_flag) and (preds.max() >= upper_thd) and (preds.argmax() != self._bg_id):
            # print('in 2')
            self._rising_ges = preds.argmax()
            self._current_ges = self._rising_ges
            self._gesture_flag = True
            # print('current:{}'.format(self._current_ges))

        # Record without background
        output = self._bg_id if self._rising_ges == self._bg_id else self._current_ges
        self._rising_ges = self._bg_id
        # print(output)

        return output

class PostProcess_Siamese:
    def __init__(self, bg_id=0):
        self._bg_id = int(bg_id)
        self._current_ges = self._bg_id
        self._rising_ges = self._bg_id
        self._gesture_flag = False

    def postprocess(self, preds:np.ndarray, lower_thd=0.5, upper_thd=0.6):
        """
        :param preds: A numpy array of model prediction with shape [classes, ]
        :param bg_id: Specific background ID
        :param lower_thd:
        :param upper_thd:
        :return: A tensor that has the same size as preds
        """
        if preds[self._bg_id] != preds.sum():
            preds[self._bg_id] = 0

        if self._gesture_flag and preds[self._current_ges] < lower_thd:
            # print('in 1')
            # print('current:{}'.format(self._current_ges))
            self._current_ges = self._bg_id
            self._gesture_flag = False

        if not (self._gesture_flag) and (preds.max() >= upper_thd) and (preds.argmax() != self._bg_id):
            # print('in 2')
            self._rising_ges = preds.argmax()
            self._current_ges = self._rising_ges
            self._gesture_flag = True
            # print('current:{}'.format(self._current_ges))

        # Record without background
        output = self._bg_id if self._rising_ges == self._bg_id else self._current_ges
        self._rising_ges = self._bg_id
        # print(output)

        return output