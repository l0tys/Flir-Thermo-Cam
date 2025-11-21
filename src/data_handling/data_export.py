# * Library imports
import asyncio
import numpy as np
from pathlib import Path
from datetime import datetime
import struct

# * File imports
from ..data_buffer import get_processed_buffered_temp_data


class DataExport:
    def __init__(self, output_dir="./data_exports", file_prefix="data_export"):
        """
        Initialize DataExport with output directory and file naming options.

        Args:
            output_dir: Directory where binary files will be saved
            file_prefix: Prefix for generated filenames
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.file_prefix = file_prefix
        self.current_file = None
        self.file_handle = None
        self.is_exporting = False

    def _generate_filename(self):
        """Generate a unique filename with timestamp."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return self.output_dir / f"{self.file_prefix}_{timestamp}.bin"

    def _write_metadata(self, data_shape):
        """
        Write metadata header to the file.
        Format: [num_dimensions (int32), dim1 (int32), dim2 (int32), ...]
        """
        if self.file_handle:
            # Write number of dimensions
            self.file_handle.write(struct.pack('i', len(data_shape)))
            # Write each dimension size
            for dim in data_shape:
                self.file_handle.write(struct.pack('i', dim))

    async def start_export(self, update_interval=1.0):
        """
        Start continuous data export process.

        Args:
            update_interval: Time in seconds between data buffer reads
        """
        if self.is_exporting:
            print("Export already in progress")
            return

        self.is_exporting = True
        self.current_file = self._generate_filename()
        self.file_handle = open(self.current_file, 'wb')

        print(f"Started data export to: {self.current_file}")

        first_write = True

        try:
            while self.is_exporting:
                # Get current data from buffer
                data = get_processed_buffered_temp_data()

                if data is not None:
                    # Convert to numpy array if not already
                    if not isinstance(data, np.ndarray):
                        data = np.asarray(data)

                    # Write metadata on first write
                    if first_write:
                        self._write_metadata(data.shape)
                        first_write = False

                    # Write timestamp
                    timestamp = datetime.now().timestamp()
                    self.file_handle.write(struct.pack('d', timestamp))

                    # Write data as binary (assumes float64/double)
                    data.astype(np.float64).tofile(self.file_handle)
                    self.file_handle.flush()  # Ensure data is written

                await asyncio.sleep(update_interval)

        except Exception as e:
            print(f"Error during export: {e}")
        finally:
            if self.file_handle:
                self.file_handle.close()
                print(f"Export stopped. Data saved to: {self.current_file}")

    def stop_export(self):
        """Stop the continuous export process."""
        self.is_exporting = False

    async def data_export(self, duration=None, update_interval=1.0):
        """
        Export data for a specific duration or indefinitely.

        Args:
            duration: Export duration in seconds (None for indefinite)
            update_interval: Time between buffer reads in seconds
        """
        export_task = asyncio.create_task(self.start_export(update_interval))

        if duration:
            await asyncio.sleep(duration)
            self.stop_export()

        await export_task