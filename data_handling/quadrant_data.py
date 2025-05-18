import numpy as np

def f(x):
    return 0.0466667 * x - 49

def load_and_transform_data(file_path):
    data = np.loadtxt(file_path)
    transformed_data = f(data)
    return transformed_data

def divide_into_quadrants(data):
    rows, cols = data.shape

    # Calculate midpoints to divide into quadrants
    mid_row = rows // 2
    mid_col = cols // 2

    # Define the quadrants
    quadrant1 = data[:mid_row, :mid_col]  # Top-left
    quadrant2 = data[:mid_row, mid_col:]  # Top-right
    quadrant3 = data[mid_row:, :mid_col]  # Bottom-left
    quadrant4 = data[mid_row:, mid_col:]  # Bottom-right

    return quadrant1, quadrant2, quadrant3, quadrant4, mid_row, mid_col


def get_quadrant_statistics(quadrant1, quadrant2, quadrant3, quadrant4):
    stats = {
        "quadrant1": {
            "min": np.min(quadrant1),
            "max": np.max(quadrant1),
            "mean": np.mean(quadrant1)
        },
        "quadrant2": {
            "min": np.min(quadrant2),
            "max": np.max(quadrant2),
            "mean": np.mean(quadrant2)
        },
        "quadrant3": {
            "min": np.min(quadrant3),
            "max": np.max(quadrant3),
            "mean": np.mean(quadrant3)
        },
        "quadrant4": {
            "min": np.min(quadrant4),
            "max": np.max(quadrant4),
            "mean": np.mean(quadrant4)
        }
    }
    return stats


def create_quadrant_mean_matrix(quadrant1, quadrant2, quadrant3, quadrant4):
    return np.array([
        [np.mean(quadrant1), np.mean(quadrant2)],
        [np.mean(quadrant3), np.mean(quadrant4)]
    ])