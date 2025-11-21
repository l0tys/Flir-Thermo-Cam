# FLIR Thermal Camera Acquisition System

A real-time thermal imaging data acquisition, processing, and visualization system built on the FLIR Spinnaker SDK (PySpin). Captures thermal data from FLIR cameras, converts raw sensor values to temperature readings, and provides multiple visualization outputs including live heatmaps and statistical analysis.

## Features

- Real-time thermal image capture from FLIR cameras via GigE Vision
- Raw-to-temperature conversion with calibrated coefficients
- Live thermal heatmap visualization with quadrant statistics
- Timestamped binary data export for post-processing
- Async pipeline architecture for concurrent capture, processing, and display
- Configurable camera calibration via parameter files
- Optional 3D temperature surface visualization
- Historical temperature averaging charts

## Requirements

### Hardware
- FLIR thermal camera (tested with A6752/Xsc Series)
- GigE Vision interface or compatible connection

### Software
- Python 3.8+
- FLIR Spinnaker SDK with PySpin bindings
- Dependencies:
  ```
  numpy
  opencv-python
  matplotlib
  scipy
  ```

## Installation

1. Install the FLIR Spinnaker SDK from [FLIR's website](https://www.flir.com/products/spinnaker-sdk/)

2. Install Python dependencies:
   ```bash
   pip install numpy opencv-python matplotlib scipy
   ```

3. Clone this repository:
   ```bash
   git clone <repository-url>
   cd spinnaker
   ```

## Usage

### Basic Operation

```bash
python main.py
```

The application will:
1. Detect connected FLIR cameras
2. Apply calibration parameters
3. Begin continuous acquisition
4. Display a live thermal heatmap window
5. Export data to `./data_exports/`

### Controls

- **ESC**: Exit the application
- Close the OpenCV window to stop acquisition

### Configuration

Camera parameters are configured via `src/calibration/params/cal_params.txt`. Default settings:
- Resolution: 640x513 pixels
- Pixel Format: Mono16
- Frame Rate: ~125 Hz (camera-dependent)

## Project Structure

```
spinnaker/
├── main.py                          # Application entry point
├── src/
│   ├── calibration/
│   │   ├── set_calibration.py       # Camera parameter configuration
│   │   ├── get_all_nodes.py         # Node enumeration utility
│   │   └── params/
│   │       └── cal_params.txt       # Calibration parameters
│   ├── data_acquisition/
│   │   ├── data_capture.py          # Frame acquisition from camera
│   │   └── data_record.py           # Recording utilities
│   ├── data_buffer/
│   │   ├── raw_data_buffer.py       # Ring buffer for raw frames
│   │   └── processed_data_buffer.py # Buffer for temperature data
│   ├── data_handling/
│   │   ├── proccess_data.py         # Raw to temperature conversion
│   │   ├── data_export.py           # Binary file export
│   │   ├── quadrant_data.py         # Quadrant statistics
│   │   └── data_cumulated.py        # Cumulative heat calculation
│   ├── data_visualization/
│   │   ├── data_to_image.py         # Thermal heatmap rendering
│   │   ├── data_average.py          # Temperature time-series chart
│   │   └── color_map.py             # Colormap utilities
│   └── util_functions/
│       └── util_functions.py        # Helper functions
└── data_exports/                    # Output directory for binary data
```

## Data Export Format

Binary export files (`sensor_data_YYYYMMDD_HHMMSS.bin`) contain:

| Field | Type | Description |
|-------|------|-------------|
| num_dimensions | int32 | Number of array dimensions |
| dim_sizes | int32[] | Size of each dimension |
| timestamp | float64 | Unix timestamp |
| data | float64[] | Temperature matrix (row-major) |

Records repeat (timestamp + data) until export stops.

## Temperature Conversion

Raw 16-bit sensor values are converted to Celsius using a linear calibration:

```
Temperature (°C) = 0.0130303 × raw_value - 62.4242
```

This calibration is specific to the camera/lens configuration and should be verified for your setup.

## Visualization

### Thermal Heatmap
- JET colormap applied to normalized temperature data
- Quadrant division with mean temperature statistics
- Real-time display at acquisition frame rate

### Quadrant Statistics
The image is divided into four quadrants (Q1-Q4) with live mean temperature displayed for each region.

## API Reference

### Camera Class
Main application controller managing camera lifecycle and async task coordination.

```python
camera = Camera()
asyncio.run(camera.main())
```

### DataCapture
Continuous frame acquisition from the camera.

```python
capture = DataCapture(camera=pyspin_camera)
await capture.data_capture()
```

### ProcessData
Temperature conversion pipeline.

```python
processor = ProcessData()
await processor.process_data()
```

### DataExport
Binary data serialization with timestamps.

```python
exporter = DataExport(output_dir="./exports", file_prefix="thermal")
await exporter.data_export(duration=60)  # Export for 60 seconds
```

## Troubleshooting

### No cameras detected
- Verify Spinnaker SDK installation
- Check network/USB connection
- Ensure camera is powered and configured for GigE

### SpinnakerException errors
- Camera may be in use by another application
- Check firewall settings for GigE cameras
- Verify IP configuration matches camera subnet

### Low frame rate
- Reduce image resolution in calibration parameters
- Check network bandwidth (GigE requires dedicated NIC)
- Disable unnecessary processing tasks

## License

[Specify your license]

## Contributing

[Contribution guidelines]
