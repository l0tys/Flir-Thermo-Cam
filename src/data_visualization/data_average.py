# * Library imports
import time
import asyncio
import numpy as np
import matplotlib.pyplot as plt

# * File imports
from ..data_buffer import get_processed_buffered_temp_data

class DataAverage:
    def __init__(self):
        self.is_running = True

        plt.rcParams['figure.figsize'] = (20, 10)
        self.fig, self.ax = plt.subplots()

        self.fig.canvas.mpl_connect('close_event', self.on_close)
        self.fig.canvas.mpl_connect('key_press_event', self.press)

        self.time_list = []
        self.point_list = []
        self.line, = self.ax.plot([], [], color='black', linestyle='-', linewidth=3, label='Temperature °C')

        self.line.set_data([0, 1], [0, 0])
        self.ax.set_xlim(0, 10)
        self.ax.set_ylim(-1, 1)

        self.start_time = time.time()

        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Temperature (T)")
        self.ax.grid(True, linestyle='--', alpha=1)
        self.ax.legend()

        self.ax.xaxis.set_major_formatter(plt.FuncFormatter(self._format_time))

        plt.title('Average Temperature')

        plt.show(block=False)
        self.fig.canvas.draw()

        plt.ion()

    def _format_time(self, x, pos):
        seconds = int(x)
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def press(self, event):
        print('press', event.key)
        if event.key == 'escape':
            self.is_running = False

    def on_close(self, event):
        self.is_running = False

    async def data_chart(self):
        print("Starting data chart loop...")
        last_update_time = 0
        update_interval = 0.01
        update_counter = 0

        plt.figure(self.fig.number)

        while self.is_running:
            try:
                processed_buffer = get_processed_buffered_temp_data()

                if processed_buffer is None:
                    await asyncio.sleep(0.1)
                    continue

                current_time = time.time()
                if current_time - last_update_time < update_interval:
                    await asyncio.sleep(0.01)
                    continue

                last_update_time = current_time
                elapsed_time = current_time - self.start_time

                update_counter += 1

                try:
                    if isinstance(processed_buffer, (list, np.ndarray)):
                        if len(processed_buffer) > 0:
                            value = float(np.mean(processed_buffer))
                        else:
                            continue
                    else:
                        value = float(processed_buffer)

                    self.time_list.append(elapsed_time)
                    self.point_list.append(value)

                except (ValueError, TypeError) as e:
                    print(f"Data conversion error: {e}, data={processed_buffer}")
                    continue

                max_points = 2000
                if len(self.time_list) > max_points:
                    self.time_list = self.time_list[-max_points:]
                    self.point_list = self.point_list[-max_points:]

                if len(self.time_list) != len(self.point_list):
                    print(f"Shape mismatch: time_list({len(self.time_list)}) != point_list({len(self.point_list)})")
                    min_len = min(len(self.time_list), len(self.point_list))
                    self.time_list = self.time_list[-min_len:]
                    self.point_list = self.point_list[-min_len:]

                self.line.set_data(self.time_list, self.point_list)

                if len(self.time_list) <= 1:
                    x_min = max(0, self.time_list[0] - 1) if self.time_list else 0
                    x_max = self.time_list[0] + 9 if self.time_list else 10
                else:
                    x_min = min(self.time_list)
                    x_max = max(self.time_list)
                    padding = (x_max - x_min) * 0.05
                    x_min = max(0, x_min - padding)
                    x_max = x_max + padding

                if abs(x_max - x_min) < 0.1:
                    x_max = x_min + 10

                self.ax.set_xlim(x_min, x_max)

                if len(self.point_list) >= 1:
                    y_min = min(self.point_list)
                    y_max = max(self.point_list)

                    padding = (y_max - y_min) * 0.05 if y_max > y_min else 1
                    y_min -= padding
                    y_max += padding

                    self.ax.set_ylim(y_min, y_max)

                try:
                    if update_counter % 5 == 0:
                        self.fig.canvas.draw_idle()
                        self.fig.canvas.flush_events()

                    if update_counter % 100 == 0:
                        plt.figure(self.fig.number)
                        if not plt.fignum_exists(self.fig.number):
                            plt.show(block=False)
                except Exception as e:
                    print(f"Error updating plot: {e}")

                await asyncio.sleep(0)

            except asyncio.CancelledError:
                print("Chart generation was cancelled.")
                break
            except Exception as e:
                print(f"Error in data_chart: {e}, type={type(e)}")
                import traceback
                traceback.print_exc()
                await asyncio.sleep(0.01)

        print("Data chart loop ended")
        plt.close(self.fig)