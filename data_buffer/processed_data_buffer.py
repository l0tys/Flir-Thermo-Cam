# Library imports
from collections import deque
import numpy as np

# Processed Data buffer
class ProcessedDataBuffer:
    def __init__(self, max_size: int = 10):
        self.temp_buffer = deque(maxlen=max_size)
        self.time_buffer = deque(maxlen=max_size)

    def add(self, temp_data: np.ndarray, time_data: np.ndarray):
        self.temp_buffer.append(temp_data)
        self.time_buffer.append(time_data)

    def export_temp(self) -> list:
        return list(self.temp_buffer)


    def export_time(self) -> list:
        return list(self.time_buffer)

processed_data_buffer = ProcessedDataBuffer()

def get_processed_buffered_temp_data() -> list:
    return processed_data_buffer.export_temp()

def get_processed_buffered_time_data() -> list:
    return processed_data_buffer.export_time()