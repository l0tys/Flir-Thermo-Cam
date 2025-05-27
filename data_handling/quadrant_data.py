import numpy as np


def divide_into_quadrants(matrix):
    rows, cols = matrix.shape
    mid_row = rows // 2
    mid_col = cols // 2

    quadrant1 = matrix[:mid_row, :mid_col]  # Top-left
    quadrant2 = matrix[:mid_row, mid_col:]  # Top-right
    quadrant3 = matrix[mid_row:, :mid_col]  # Bottom-left
    quadrant4 = matrix[mid_row:, mid_col:]  # Bottom-right

    return quadrant1, quadrant2, quadrant3, quadrant4, mid_row, mid_col

def get_quadrant_statistics(q1, q2, q3, q4):
    print(f"\n{"-" * 50}\n{np.array([
        [np.mean(q1), np.mean(q2)],
        [np.mean(q3), np.mean(q4)]
    ])}")

    return np.array([
        [np.mean(q1), np.mean(q2)],
        [np.mean(q3), np.mean(q4)]])