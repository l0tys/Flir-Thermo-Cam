# Library imports
from collections import deque


class DataBuffer:
    def __init__(self, max_size=10):
        self.buffer = deque(maxlen=max_size)

    def add(self, data):
        self.buffer.append(data)

    def export(self):
        return list(self.buffer)


data_buffer = DataBuffer()


def get_buffered_data():
    return data_buffer.export()
