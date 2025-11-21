# * Library imports
import numpy as np

def divide_into_quadrants(matrix):
    rows, cols = matrix.shape
    mid_row = rows // 2
    mid_col = cols // 2

    quadrant1 = matrix[mid_row//2:mid_row, mid_col//2:mid_col]  # Top-left
    quadrant2 = matrix[mid_row//2:mid_row, mid_col:mid_col+mid_col//2]  # Top-right
    quadrant3 = matrix[mid_row:mid_row+mid_row//2, mid_col//2:mid_col]  # Bottom-left
    quadrant4 = matrix[mid_row:mid_row+mid_row//2, mid_col:mid_col+mid_col//2]  # Bottom-right

    return quadrant1, quadrant2, quadrant3, quadrant4, mid_row, mid_col

def get_quadrant_statistics(q1, q2, q3, q4):
    stats_array = np.array([
        [q1.mean(), q2.mean()],
        [q3.mean(),q4.mean()]
    ])

    print(f"\n{'=' * 50}\n{stats_array}")

    return stats_array
