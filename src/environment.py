import math
from typing import Tuple


class EnvironmentSimulator:
    def __init__(
        self,
        day_duration_seconds: float = 60.0,
        min_temp: float = 18.0,
        max_temp: float = 28.0,
        initial_soil_moisture: float = 55.0,
        daily_moisture_decay: float = 30.0,
        daily_irrigation_gain: float = 80.0,
    ):
        self.day_duration_seconds = max(1.0, float(day_duration_seconds))
        self.min_temp = min_temp
        self.max_temp = max_temp
        self.soil_moisture = float(initial_soil_moisture)
        self.daily_moisture_decay = float(daily_moisture_decay)
        self.daily_irrigation_gain = float(daily_irrigation_gain)
        self.simulation_time = 0.0

    def update(self, pump_on: bool, elapsed_seconds: float) -> Tuple[int, int]:
        elapsed = max(0.0, float(elapsed_seconds))
        self.simulation_time += elapsed

        day_fraction = elapsed / self.day_duration_seconds
        if pump_on:
            self.soil_moisture += self.daily_irrigation_gain * day_fraction
        else:
            self.soil_moisture -= self.daily_moisture_decay * day_fraction

        self.soil_moisture = max(0.0, min(100.0, self.soil_moisture))

        temperature = self._day_night_temperature()
        return int(round(temperature * 10)), int(round(self.soil_moisture))

    def _day_night_temperature(self) -> float:
        phase = (self.simulation_time % self.day_duration_seconds) / self.day_duration_seconds
        sine = math.sin(2 * math.pi * phase - math.pi / 2)

        amplitude = (self.max_temp - self.min_temp) / 2.0
        average = (self.max_temp + self.min_temp) / 2.0
        return average + amplitude * sine

    def get_simulated_time(self) -> str:
        day_fraction = (self.simulation_time % self.day_duration_seconds) / self.day_duration_seconds
        total_seconds = int(round(day_fraction * 24 * 3600))
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def set_day_duration(self, seconds: float) -> None:
        self.day_duration_seconds = max(1.0, float(seconds))
