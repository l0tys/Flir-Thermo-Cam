# Library imports
from collections import deque
import numpy as np

# Raw data buffer
class RawDataBuffer:
    def __init__(self, max_size: int = 10):
        self.buffer = deque(maxlen=max_size)

    def add(self, data: np.ndarray):
        self.buffer.append(data)

    def export(self) -> list:
        return list(self.buffer)

raw_data_buffer = RawDataBuffer()

def get_raw_buffered_data() -> list:
    return raw_data_buffer.export()