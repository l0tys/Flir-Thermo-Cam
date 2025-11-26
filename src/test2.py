from test3 import read_thermal_recording, convert_binary_to_txt

# Read and automatically convert to text
frames = read_thermal_recording("test_exports/thermal_recording_20251127_005342.bin")

# Or just convert without reading into memory
convert_binary_to_txt("test_exports/thermal_recording_20251127_005342.bin")