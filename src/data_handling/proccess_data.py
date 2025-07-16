# * Library imports
import asyncio
import numpy as np
import datetime

# * File imports
from data_buffer import get_raw_buffered_data, processed_data_buffer

class ProcessData:
    def __init__(self, raw_buffer=None, processed_buffer=None):
        self.raw_buffer = raw_buffer or get_raw_buffered_data()
        self.processed_buffer = processed_buffer or processed_data_buffer
        self.time_list = []

    async def process_data(self):
        try:
            while True:
                self.raw_buffer = get_raw_buffered_data()
                if not self.raw_buffer:
                    print("Warning: No buffered data available.")
                    await asyncio.sleep(1)
                    continue

                data = self.raw_buffer[-1]

                # data_matrix = 0.0107143 * data - 44.2857
                # Bik precizak
                data_matrix = 0.0130303 * data - 62.4242

                current_time = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")
                self.time_list.append(current_time)
                np_time_list = np.array(self.time_list)

                self.processed_buffer.add(temp_data=data_matrix, time_data=np_time_list)

                await asyncio.sleep(0)
        except asyncio.CancelledError:
            pass
