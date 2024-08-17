import sys
import numpy as np

class Debounce():
    def __init__(self, lock_margin=0.6, sample_rate=50e-3, bg_id=0, enable=False):
        self._bg_id = int(bg_id)
        self.sample_rate = sample_rate
        self.temporal_gap = int(lock_margin * (1.0 / sample_rate))
        self._buffer_init()
        self.lock = False
        self.out = False
        self.holding_gesture = None
        self._enable = enable

    def debounce(self, preds, target_id=2, lock_id=[3]):
        """
        Argument:
        preds:
        target_id:
        lock_id:
        """
        if not self._enable:
            return preds
        out = int(preds)
        get_gesture = int(preds)

        if not self.lock and get_gesture in lock_id:
            self.holding_gesture = get_gesture
            self.lock = True

        if self.lock:
            out = self._bg_id
            self._buffer_update(get_gesture)
            if self.buffer[0] in lock_id or target_id in self.buffer:
                if target_id in self.buffer[1:]:
                    out = target_id
                    sys.stdout.write("\r[" + ', '.join([str(x) for x in self.buffer]) + ']')
                else:
                    out = self.holding_gesture
                self._buffer_init()
                self.holding_gesture = None
                self.lock = False

        return str(out)

    def _buffer_update(self, get_gesture):
        self.buffer = np.roll(self.buffer, shift=-1, axis=0)
        self.buffer[-1] = get_gesture

    def _buffer_init(self):
        self.buffer = np.zeros([self.temporal_gap])