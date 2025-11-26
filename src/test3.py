import numpy as np
from pathlib import Path
from datetime import datetime
import struct

def read_thermal_recording(filename, export_txt=True):
    frames = []

    with open(filename, 'rb') as f:
        # Read and verify header
        magic = f.read(4)
        if magic != b'THRM':
            raise ValueError("Invalid file format - missing THRM magic number")

        version = struct.unpack('i', f.read(4))[0]
        print(f"File version: {version}")

        # Read frames
        while True:
            # Try to read frame marker
            marker = f.read(4)
            if not marker or len(marker) < 4:
                break  # End of file

            if marker != b'FRAM':
                print(f"Warning: Expected FRAM marker, got {marker}")
                break

            # Read frame metadata
            num_dims = struct.unpack('i', f.read(4))[0]
            shape = []
            for _ in range(num_dims):
                shape.append(struct.unpack('i', f.read(4))[0])

            # Read timestamp
            timestamp = struct.unpack('d', f.read(8))[0]

            # Read frame number
            frame_num = struct.unpack('i', f.read(4))[0]

            # Read matrix data
            matrix_data = np.fromfile(f, dtype=np.float64, count=np.prod(shape)).reshape(shape)

            frames.append((timestamp, frame_num, matrix_data))

    # Export to text files if requested
    if export_txt:
        base_path = Path(filename)
        txt_dir = base_path.parent / f"{base_path.stem}_txt"
        txt_dir.mkdir(parents=True, exist_ok=True)

        print(f"\nExporting {len(frames)} frames to text files in: {txt_dir}")

        # Create a metadata file
        metadata_file = txt_dir / "metadata.txt"
        with open(metadata_file, 'w') as meta:
            meta.write(f"Binary File: {filename}\n")
            meta.write(f"Total Frames: {len(frames)}\n")
            meta.write(f"Version: {version}\n")
            meta.write("=" * 70 + "\n\n")

            for timestamp, frame_num, matrix in frames:
                # Export individual frame
                frame_file = txt_dir / f"frame_{frame_num:04d}.txt"
                np.savetxt(frame_file, matrix, fmt='%.4f')

                # Add to metadata
                dt = datetime.fromtimestamp(timestamp)
                meta.write(f"Frame {frame_num}:\n")
                meta.write(f"  File: frame_{frame_num:04d}.txt\n")
                meta.write(f"  Timestamp: {timestamp} ({dt.strftime('%Y-%m-%d %H:%M:%S')})\n")
                meta.write(f"  Shape: {matrix.shape}\n")
                meta.write(f"  Min: {np.nanmin(matrix):.4f}\n")
                meta.write(f"  Max: {np.nanmax(matrix):.4f}\n")
                meta.write(f"  Mean: {np.nanmean(matrix):.4f}\n\n")
        print(f"Text export complete. Metadata saved to: {metadata_file}")
    return frames

def convert_binary_to_txt(binary_filename):
    frames = read_thermal_recording(binary_filename, export_txt=True)
    print(f"\nConversion complete. {len(frames)} frames exported.")
    return frames