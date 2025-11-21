# Technical Architecture: FLIR Thermal Acquisition System

## System Overview

This system implements a concurrent data pipeline for thermal radiometry using the FLIR Spinnaker SDK. The architecture follows a producer-consumer pattern with shared ring buffers, enabling decoupled operation of acquisition, processing, and visualization subsystems.

## Concurrency Model

The application employs Python's `asyncio` cooperative multitasking to run four concurrent coroutines:

```
┌─────────────────────────────────────────────────────────────────────┐
│                         asyncio Event Loop                          │
├─────────────────────────────────────────────────────────────────────┤
│  capture_task    process_task    image_task    export_task          │
│       │               │               │              │              │
│       ▼               ▼               ▼              ▼              │
│  ┌─────────┐    ┌──────────┐    ┌──────────┐   ┌──────────┐        │
│  │ Camera  │───▶│ Raw      │───▶│ Process  │──▶│ Processed│        │
│  │ Driver  │    │ Buffer   │    │ Data     │   │ Buffer   │        │
│  └─────────┘    └──────────┘    └──────────┘   └──────────┘        │
│                      │                              │               │
│                      ▼                              ▼               │
│                 ┌──────────┐                  ┌──────────┐          │
│                 │ Heatmap  │                  │ Binary   │          │
│                 │ Render   │                  │ Export   │          │
│                 └──────────┘                  └──────────┘          │
└─────────────────────────────────────────────────────────────────────┘
```

Each task yields control via `await asyncio.sleep(0)`, allowing round-robin execution without blocking. This design achieves near-real-time performance without threading complexity.

## Data Buffer Implementation

### Ring Buffer Architecture

Both `RawDataBuffer` and `ProcessedDataBuffer` utilize `collections.deque` with bounded capacity:

```python
class RawDataBuffer:
    def __init__(self, max_size: int = 10):
        self.buffer = deque(maxlen=max_size)
```

The bounded deque provides O(1) append/pop operations and automatic eviction of stale frames when capacity is exceeded. This prevents unbounded memory growth during sustained operation while maintaining a sliding window of recent data.

### Buffer Access Pattern

Consumers read the most recent frame via `buffer[-1]`, implementing a "latest-value" semantics rather than queue consumption. This ensures visualization always displays current data even if processing throughput varies.

## Camera Interface Layer

### Spinnaker SDK Integration

The `DataCapture` class interfaces with PySpin's streaming API:

```python
self.camera.Init()
self.camera.BeginAcquisition()

while True:
    image = self.camera.GetNextImage()  # Blocking call to driver
    np_image = np.frombuffer(image.GetData(), dtype=np.uint16)
    self.data_buffer.add(np_image.reshape(height, width))
    image.Release()  # Return buffer to driver pool
```

Key considerations:
- `GetNextImage()` blocks until a frame is available from the driver's internal buffer
- `image.Release()` is critical—failure to release causes driver buffer exhaustion
- The first row is discarded (`np_image[1:]`) as it contains embedded metadata on FLIR cameras

### GenICam Node Configuration

Calibration parameters are applied via the GenICam nodemap interface:

```python
nodemap = cam.GetNodeMap()
node = PySpin.CIntegerPtr(nodemap.GetNode("Width"))
node.SetValue(640)
```

Parameters support Integer, Float, String, and Boolean types, parsed from `cal_params.txt` and applied through type-specific pointer classes (`CIntegerPtr`, `CFloatPtr`, etc.).

## Radiometric Conversion

### Linear Calibration Model

Raw 16-bit pixel values from the thermal sensor undergo linear transformation to temperature:

```
T(°C) = m × DN + b
```

Where:
- `DN` = Digital Number (raw 16-bit value, 0-65535)
- `m` = 0.0130303 (gain coefficient)
- `b` = -62.4242 (offset)

This linear approximation is valid within the calibrated temperature range (typically 35°C-150°C for the default configuration). Outside this range, non-linear corrections may be necessary.

### Calibration Derivation

The coefficients derive from a two-point calibration:
1. Observe raw values at two known blackbody temperatures
2. Solve the linear system for slope and intercept

The current coefficients suggest a dynamic range mapping approximately:
- 4,790 DN → 0°C
- 12,468 DN → 100°C

## Visualization Pipeline

### Heatmap Generation

The thermal image rendering process:

```python
# 1. Apply radiometric conversion
matrix = 0.0130303 * raw_data - 62.4242

# 2. Normalize to 8-bit range for colormap
matrix_norm = cv2.normalize(matrix, None, 0, 255, cv2.NORM_MINMAX)
matrix_norm = np.uint8(matrix_norm)

# 3. Apply JET colormap (blue=cold, red=hot)
heatmap = cv2.applyColorMap(matrix_norm, cv2.COLORMAP_JET)
```

The normalization step maps the current frame's temperature range to [0,255], providing maximum contrast but losing absolute temperature reference in the display. Quadrant statistics overlay provides quantitative temperature values.

### Quadrant Analysis

The frame is divided into four regions centered on the image:

```
┌──────────┬──────────┐
│    Q1    │    Q2    │
│ (0,mid)  │(mid,mid) │
├──────────┼──────────┤
│    Q3    │    Q4    │
│(0,end)   │(mid,end) │
└──────────┴──────────┘
```

Each quadrant's mean temperature is computed and displayed, enabling region-of-interest monitoring without full statistical computation.

## Binary Export Format

### File Structure

```
┌────────────────────────────────────────┐
│ Header (written once)                  │
├────────────────────────────────────────┤
│ num_dimensions: int32                  │
│ dim_0: int32                           │
│ dim_1: int32                           │
│ ...                                    │
├────────────────────────────────────────┤
│ Record 0                               │
├────────────────────────────────────────┤
│ timestamp: float64 (Unix epoch)        │
│ data: float64[dim_0 × dim_1 × ...]     │
├────────────────────────────────────────┤
│ Record 1                               │
├────────────────────────────────────────┤
│ timestamp: float64                     │
│ data: float64[...]                     │
├────────────────────────────────────────┤
│ ...                                    │
└────────────────────────────────────────┘
```

Records are appended sequentially with `flush()` after each write to minimize data loss on abnormal termination.

### Reading Exported Data

```python
import struct
import numpy as np

with open('sensor_data.bin', 'rb') as f:
    # Read header
    ndims = struct.unpack('i', f.read(4))[0]
    shape = [struct.unpack('i', f.read(4))[0] for _ in range(ndims)]

    # Read records
    records = []
    while True:
        ts_bytes = f.read(8)
        if not ts_bytes:
            break
        timestamp = struct.unpack('d', ts_bytes)[0]
        data = np.frombuffer(f.read(np.prod(shape) * 8), dtype=np.float64)
        records.append((timestamp, data.reshape(shape)))
```

## Cumulative Heat Integration

The `DataCumulated` class implements numerical integration of temperature over time using Simpson's rule:

```python
from scipy.integrate import simpson

cumulative_heat = simpson(heat_history, time_history)  # °C·s
```

This metric represents the integral of (T - T_base) over time, useful for applications requiring thermal dose quantification or energy accumulation monitoring.

## Performance Characteristics

### Throughput

- Frame acquisition: Up to ~125 Hz (camera-limited)
- Processing: Negligible latency (vectorized NumPy operations)
- Visualization: ~30-60 FPS (OpenCV imshow + waitKey timing)
- Export: 1 Hz default (configurable)

### Memory Footprint

- Raw buffer: 10 frames × 640×513 × 2 bytes ≈ 6.5 MB
- Processed buffer: 10 frames × 640×513 × 8 bytes ≈ 26 MB
- Total working set: ~50 MB typical

### Latency

End-to-end latency from photon capture to display is dominated by:
1. Camera integration time (~0.4 ms typical)
2. GigE transfer (~1-2 ms for full frame)
3. asyncio scheduling jitter (~0-10 ms)

Total latency: 5-15 ms typical under normal operation.

## Error Handling

### Camera Exceptions

SpinnakerException handling covers:
- Connection loss during streaming
- Buffer underrun/overrun
- Invalid parameter configuration

Cleanup ensures proper resource release:
```python
finally:
    camera.EndAcquisition()
    camera.DeInit()
    camera_list.Clear()
    system.ReleaseInstance()
```

### Graceful Degradation

Missing buffer data triggers warning messages and retry loops rather than exceptions, allowing temporary dropouts without system failure:

```python
if not processed_buffer:
    print("Warning: No buffered data available.")
    await asyncio.sleep(1)
    continue
```

## Extension Points

### Adding New Visualization Modes

1. Create class in `src/data_visualization/`
2. Subscribe to appropriate buffer (`raw_data_buffer` or `processed_data_buffer`)
3. Implement async coroutine for render loop
4. Register task in `Camera.main()`

### Custom Calibration

1. Modify coefficients in `ProcessData.process_data()` and `DataToImage.data_to_image()`
2. For non-linear calibration, replace linear formula with lookup table or polynomial
3. Per-pixel calibration requires additional NUC (Non-Uniformity Correction) data

### Alternative Export Formats

The `DataExport` class can be extended to support:
- HDF5 for hierarchical storage with metadata
- NetCDF for climate/geophysical compatibility
- TIFF sequences for image-based workflows
