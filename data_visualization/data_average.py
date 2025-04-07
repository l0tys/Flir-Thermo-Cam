# * Library imports
import sys
import datetime
import asyncio
import numpy as np
import matplotlib

if sys.platform == 'darwin':
    matplotlib.use('MacOSX')
else:
    matplotlib.use('TkAgg')

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# * File imports
from data_buffer import get_processed_buffered_temp_data

class DataAverage:
    def __init__(self):
        self.is_running = True

        plt.rcParams['figure.figsize'] = (20, 10)
        self.fig, self.ax = plt.subplots()
        self.fig.canvas.mpl_connect('close_event', self.on_close)
        self.fig.canvas.mpl_connect('key_press_event', self.press)
        # plt.ion()

    def press(self, event):
        print('press', event.key)
        if event.key == 'escape':
            self.is_running = False

    def on_close(self, event):
        self.is_running = False

    async def data_chart(self):
        time_list = []

        while self.is_running:
            try:
                data_buffer = get_processed_buffered_temp_data()

                if not data_buffer:
                    await asyncio.sleep(0.1)
                    continue

                self.ax.clear()

                current_time = datetime.datetime.now()
                time_list.append(current_time)

                np_points = np.array(data_buffer)
                np_seconds = np.array(time_list)

                np_seconds = mdates.date2num(np_seconds)

                self.ax.plot(np_points, color='black', linestyle='-', linewidth=3, label='Temperature °C')
                self.ax.set_xlabel("Time (s)")
                self.ax.set_ylabel("Temperature (T)")
                self.ax.grid(True, linestyle='--', alpha=1)
                self.ax.set_ylim(np.min(np_points) - 1, np.max(np_points) + 1)
                self.ax.legend()
                self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
                self.fig.autofmt_xdate()
                plt.title('Average Temperature')
                plt.draw()
                plt.pause(0.01)

                await asyncio.sleep(0)

            except asyncio.CancelledError:
                print("Chart generation was cancelled.")
                break
            except Exception as e:
                print(f"Error: {e}")

        plt.close(self.fig)