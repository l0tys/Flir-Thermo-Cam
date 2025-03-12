# Library imports
from collections import deque
import numpy as np

# Processed Data buffer
class ProcessedDataBuffer:
    def __init__(self):
        self.buffer = deque()

    def add(self, data: np.ndarray):
        self.buffer.append(data)

    def export(self) -> list:
        return list(self.buffer)

processed_data_buffer = ProcessedDataBuffer()

def get_processed_buffered_data() -> list:
    return processed_data_buffer.export()