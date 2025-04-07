import numpy as np

def create_thermal_colormap():
    # Create a colormap with the right shape from the beginning
    colormap = np.zeros((256, 1, 3), dtype=np.uint8)

    ranges = [
        (0, 44, (0, 0, 128), (0, 0, 255)),     # Black to Blue
        (44, 86, (0, 0, 255), (0, 255, 255)),  # Blue to Cyan
        (86, 129, (0, 255, 255), (0, 255, 0)), # Cyan to Green
        (129, 171, (0, 255, 0), (255, 255, 0)), # Green to Yellow
        (171, 214, (255, 255, 0), (255, 0, 0)), # Yellow to Red
        (214, 256, (255, 0, 0), (255, 255, 255)) # Red to White

        # (0, 44, (255, 0, 0), (255, 255, 255)),  # Black to Blue
        # (44, 86, (255, 255, 0), (255, 0, 0)),  # Blue to Cyan
        # (86, 129, (0, 255, 0), (255, 255, 0)),  # Cyan to Green
        # (129, 171, (0, 255, 255), (0, 255, 0)),  # Green to Yellow
        # (171, 214, (0, 0, 255), (0, 255, 255)),  # Yellow to Red
        # (214, 256, (0, 0, 128), (0, 0, 255))  # Red to White
    ]

    for start, end, color_start, color_end in ranges:
        for i in range(start, end):
            # Calculate the interpolated color
            ratio = (i - start) / (end - start)
            for channel in range(3):
                value = int(color_start[channel] * (1 - ratio) + color_end[channel] * ratio)
                colormap[i, 0, channel] = value

    # Verify the shape and properties
    assert colormap.flags['C_CONTIGUOUS'], "Colormap must be C_CONTIGUOUS"
    assert colormap.shape == (256, 1, 3), f"Expected shape (256, 1, 3), got {colormap.shape}"
    assert colormap.dtype == np.uint8, f"Expected dtype np.uint8, got {colormap.dtype}"

    return colormap