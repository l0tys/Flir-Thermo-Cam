# * Library imports
import time
import asyncio
import numpy as np
from scipy.integrate import simpson
from typing import Optional
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.cm as cm
from matplotlib.colors import Normalize

# * File imports
from ..data_buffer import get_processed_buffered_temp_data


class DataCumulated:
    def __init__(self, base_temp: float = 0.0, timestep_seconds: float = 10.0):
        self.base_temp = base_temp
        self.timestep_seconds = timestep_seconds
        self.heat_history = []
        self.time_history = []
        self.temp_matrices = []
        self.is_running = True

        # Visualization setup
        plt.rcParams['figure.figsize'] = (14, 10)
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111, projection='3d')

        # Connect event handlers
        self.fig.canvas.mpl_connect('close_event', self.on_close)
        self.fig.canvas.mpl_connect('key_press_event', self.press)

        # Initial plot setup
        self.ax.set_xlabel('X Position', fontsize=10)
        self.ax.set_ylabel('Y Position', fontsize=10)
        self.ax.set_zlabel('Temperature (°C)', fontsize=10)
        self.ax.set_title('Real-time 3D Temperature Heatmap', fontsize=12)

        # Store bar plot references
        self.bar_collection = None
        self.colorbar = None

        plt.show(block=False)
        self.fig.canvas.draw()
        plt.ion()

        self.start_time = time.time()
        self.last_update_time = 0
        self.update_interval = 0.1  # Update visualization every 100ms

    def press(self, event):
        """Handle key press events"""
        print('press', event.key)
        if event.key == 'escape':
            self.is_running = False

    def on_close(self, event):
        """Handle window close event"""
        self.is_running = False

    async def process_temp_matrix(self, temp_matrix: np.ndarray) -> float:
        """Process temperature matrix and calculate effective heat"""
        effective_heat = np.maximum(temp_matrix - self.base_temp, 0)
        timestep_avg = np.mean(effective_heat)

        self.heat_history.append(timestep_avg)
        self.time_history.append(len(self.heat_history) * self.timestep_seconds)
        self.temp_matrices.append(temp_matrix.copy())

        # Limit history to prevent memory issues
        max_history = 1000
        if len(self.temp_matrices) > max_history:
            self.temp_matrices = self.temp_matrices[-max_history:]
            self.heat_history = self.heat_history[-max_history:]
            self.time_history = self.time_history[-max_history:]

        return timestep_avg

    def compute_cumulative_heat(self) -> float:
        """Compute cumulative heat using Simpson's rule"""
        if len(self.heat_history) < 2:
            return 0.0
        return simpson(self.heat_history, self.time_history)

    def update_plot(self):
        """Update the 3D bar plot with current data"""
        if not self.temp_matrices:
            return

        current_time = time.time()
        if current_time - self.last_update_time < self.update_interval:
            return

        self.last_update_time = current_time

        try:
            # Clear previous plot
            self.ax.clear()

            # Get the latest temperature matrix
            temp_matrix = self.temp_matrices[-1]

            # Handle multi-dimensional arrays
            if temp_matrix.ndim > 2:
                if temp_matrix.shape[-1] == 1:
                    temp_matrix = temp_matrix.squeeze()
                else:
                    temp_matrix = np.mean(temp_matrix, axis=tuple(range(2, temp_matrix.ndim)))

            if temp_matrix.ndim != 2:
                print(f"Warning: Unexpected matrix shape {temp_matrix.shape}, skipping visualization")
                return

            rows, cols = temp_matrix.shape

            # Create meshgrid for bar positions
            x_pos = np.arange(cols)
            y_pos = np.arange(rows)
            x_pos, y_pos = np.meshgrid(x_pos, y_pos)
            x_pos = x_pos.flatten()
            y_pos = y_pos.flatten()
            z_pos = np.zeros_like(x_pos)

            # Bar dimensions
            dx = dy = 0.75
            dz = temp_matrix.flatten()

            # Create colormap based on temperature values
            vmin = max(0, dz.min())
            vmax = dz.max()
            if vmax <= vmin:
                vmax = vmin + 1

            norm = Normalize(vmin=vmin, vmax=vmax)
            colors = cm.hot(norm(dz))

            # Plot 3D bars
            self.ax.bar3d(x_pos, y_pos, z_pos, dx, dy, dz,
                          color=colors, shade=True, alpha=0.85, edgecolor='black', linewidth=0.5)

            # Set labels and title with cumulative info
            self.ax.set_xlabel('X Position', fontsize=10)
            self.ax.set_ylabel('Y Position', fontsize=10)
            self.ax.set_zlabel('Temperature (°C)', fontsize=10)

            cumulative = self.compute_cumulative_heat()
            elapsed_time = time.time() - self.start_time

            self.ax.set_title(
                f'Temperature Heatmap - Timestep {len(self.heat_history)}\n'
                f'Cumulative Heat: {cumulative:.2f} °C·s | Elapsed: {elapsed_time:.1f}s\n'
                f'Current Avg: {np.mean(temp_matrix):.2f}°C | Max: {vmax:.2f}°C',
                fontsize=11
            )

            # Set limits
            self.ax.set_xlim(-0.5, cols - 0.5)
            self.ax.set_ylim(-0.5, rows - 0.5)
            self.ax.set_zlim(0, vmax * 1.1)

            # Add colorbar
            if self.colorbar is not None:
                self.colorbar.remove()

            mappable = cm.ScalarMappable(norm=norm, cmap='hot')
            mappable.set_array(dz)
            self.colorbar = self.fig.colorbar(mappable, ax=self.ax, pad=0.1, shrink=0.7, aspect=20)
            self.colorbar.set_label('Temperature (°C)', fontsize=9)

            # Draw the canvas
            self.fig.canvas.draw_idle()
            self.fig.canvas.flush_events()

        except Exception as e:
            print(f"Error updating plot: {e}")
            import traceback
            traceback.print_exc()

    async def data_cumulated(self):
        """Main loop for data collection and visualization"""
        print("Starting 3D temperature visualization...")
        update_counter = 0

        plt.figure(self.fig.number)

        while self.is_running:
            try:
                # Get fresh data from buffer
                temp_matrix = get_processed_buffered_temp_data()

                if temp_matrix is None:
                    await asyncio.sleep(0.1)
                    continue

                if not isinstance(temp_matrix, np.ndarray):
                    temp_matrix = np.array(temp_matrix)

                update_counter += 1

                # Process the temperature matrix
                await self.process_temp_matrix(temp_matrix)

                cumulative = self.compute_cumulative_heat()

                # Print status every 10 updates
                if update_counter % 10 == 0:
                    print(f"Timestep {len(self.heat_history)}:")
                    print(f"  Cumulative heat: {cumulative:.2f} °C·s")
                    print(f"  Matrix shape: {temp_matrix.shape}")
                    print(f"  Avg temp: {np.mean(temp_matrix):.2f}°C")

                # Update visualization
                self.update_plot()

                # Check if window still exists
                if not plt.fignum_exists(self.fig.number):
                    self.is_running = False
                    break

                await asyncio.sleep(0.01)

            except asyncio.CancelledError:
                print("3D visualization was cancelled.")
                break
            except Exception as e:
                print(f"Error in data_cumulated: {e}")
                import traceback
                traceback.print_exc()
                await asyncio.sleep(0.1)

        print("3D visualization loop ended")
        self.close_plot()

    def close_plot(self):
        """Close the plot window"""
        try:
            if self.fig and plt.fignum_exists(self.fig.number):
                plt.close(self.fig)
        except Exception as e:
            print(f"Error closing plot: {e}")


# Example usage
async def main():
    """Example usage of the DataCumulated class with visualization"""
    data_processor = DataCumulated(base_temp=25.0, timestep_seconds=1.0)

    try:
        await data_processor.data_cumulated()
    except KeyboardInterrupt:
        print("\nStopping visualization...")
        data_processor.close_plot()


if __name__ == "__main__":
    asyncio.run(main())