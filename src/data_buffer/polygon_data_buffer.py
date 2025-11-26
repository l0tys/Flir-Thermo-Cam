# * Library imports
from collections import deque
import numpy as np

class PolygonDataBuffer:
    def __init__(self, max_size: int = 10):
        self.buffer = deque(maxlen=max_size)

    def add(self, data: np.ndarray):
        self.buffer.append(data)

    def export(self) -> list:
        return list(self.buffer)

polygon_data_buffer = PolygonDataBuffer()

def get_polygon_buffered_data() -> list:
    return polygon_data_buffer.export()