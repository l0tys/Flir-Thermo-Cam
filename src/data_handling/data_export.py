# * Library imports
import asyncio
import numpy as np
from pathlib import Path
from datetime import datetime

# * File imports
from ..data_buffer import get_polygon_buffered_data


class DataExport:
    def __init__(self, output_dir="./data/exports", file_prefix="polygon_data"):
        """
        Initialize PolygonDataExport with output directory and file naming options.

        Args:
            output_dir: Directory where text files will be saved
            file_prefix: Prefix for generated filenames
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.file_prefix = file_prefix
        self.current_file = None
        self.is_exporting = False

    def _generate_filename(self):
        """Generate a unique filename with timestamp."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return self.output_dir / f"{self.file_prefix}_{timestamp}.txt"

    async def start_export(self, update_interval=1.0):
        """
        Start continuous polygon data export process.

        Args:
            update_interval: Time in seconds between data buffer reads
        """
        if self.is_exporting:
            print("Export already in progress")
            return

        self.is_exporting = True
        self.current_file = self._generate_filename()

        print(f"Started polygon data export to: {self.current_file}")

        try:
            while self.is_exporting:
                # Get current data from polygon buffer
                buffered_data = get_polygon_buffered_data()

                if buffered_data and len(buffered_data) > 0:
                    # Get the last frame (matrix)
                    matrix_data = buffered_data[-1]

                    # Write matrix to file
                    await asyncio.get_event_loop().run_in_executor(
                        None,
                        lambda: np.savetxt(self.current_file, matrix_data, fmt='%.4f')
                    )

                    print(f"Exported matrix with shape {matrix_data.shape}")

                await asyncio.sleep(update_interval)

        except Exception as e:
            print(f"Error during export: {e}")
            import traceback
            traceback.print_exc()
        finally:
            print(f"Export stopped. Data saved to: {self.current_file}")

    def stop_export(self):
        """Stop the continuous export process."""
        self.is_exporting = False

    async def export_once(self):
        """
        Export polygon buffer data once to a new file.
        """
        buffered_data = get_polygon_buffered_data()

        if not buffered_data or len(buffered_data) == 0:
            print("No polygon data in buffer to export")
            return None

        filename = self._generate_filename()

        # Get the last frame (matrix)
        matrix_data = buffered_data[-1]

        # Save matrix to file
        await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: np.savetxt(filename, matrix_data, fmt='%.4f')
        )

        print(f"Exported matrix with shape {matrix_data.shape} to {filename}")
        return str(filename)

    async def polygon_data_export(self, duration=None, update_interval=1.0):
        """
        Export polygon data for a specific duration or indefinitely.

        Args:
            duration: Export duration in seconds (None for indefinite)
            update_interval: Time between buffer reads in seconds
        """
        export_task = asyncio.create_task(self.start_export(update_interval))

        if duration:
            await asyncio.sleep(duration)
            self.stop_export()

        await export_task


# Convenience function for one-time export
async def export_polygon_data_once():
    """Quick function to export polygon buffer once"""
    exporter = DataExport()
    return await exporter.export_once()