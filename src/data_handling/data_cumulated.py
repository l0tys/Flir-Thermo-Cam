# * Library imports
import asyncio
import numpy as np
from scipy.integrate import simpson
from typing import Optional

# * File imports
from src.data_buffer import get_processed_buffered_temp_data


class DataCumulated:
    def __init__(self, base_temp: float = 0.0, timestep_seconds: float = 10.0):
        self.base_temp = base_temp
        self.timestep_seconds = timestep_seconds
        self.heat_history = []
        self.time_history = []

    async def process_temp_matrix(self, temp_matrix: np.ndarray) -> float:
        effective_heat = np.maximum(temp_matrix - self.base_temp, 0)
        timestep_avg = np.mean(effective_heat)

        self.heat_history.append(timestep_avg)
        self.time_history.append(len(self.heat_history) * self.timestep_seconds)

        return timestep_avg

    def compute_cumulative_heat(self) -> float:
        if len(self.heat_history) < 2:
            return 0.0
        return simpson(self.heat_history, self.time_history)

    async def data_cumulated(self, new_matrix: Optional[np.ndarray] = None):
        while True:
            if new_matrix is None:
                new_matrix = get_processed_buffered_temp_data()

            if not isinstance(new_matrix, np.ndarray):
                new_matrix = np.array(new_matrix)

            cumulative = self.compute_cumulative_heat()

            print(f"Timestep {len(self.heat_history)}:")
            print(f"  Cumulative heat: {cumulative:.2f} °C·s")

            await asyncio.sleep(self.timestep_seconds)
