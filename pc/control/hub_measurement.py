from dataclasses import dataclass
from datetime import datetime


@dataclass
class HubMeasurement:
    pitch: float
    roll: float
    acceleration_x: float
    acceleration_y: float
    acceleration_z: float
    angular_velocity_x: float
    angular_velocity_y: float
    angular_velocity_z: float
    distance: float
    time: datetime

    jerk_x: float = 0
    jerk_y: float = 0
    jerk_z: float = 0

    @staticmethod
    def fieldnames():
        return ['pitch', 'roll', 'acceleration_x', 'acceleration_y', 'acceleration_z', 'angular_velocity_x',
                'angular_velocity_y', 'angular_velocity_z', 'distance', 'time', 'jerk_x', 'jerk_y', 'jerk_z']

    @staticmethod
    def from_string(data: str, previous_measurement: 'HubMeasurement' = None) -> 'HubMeasurement':
        values = [float(x) for x in data.split('|')]
        measurement = HubMeasurement(*values, datetime.now())

        if previous_measurement is None:
            return measurement

        dt = (measurement.time - previous_measurement.time).total_seconds()

        # Check to ensure we have a non-zero time difference to avoid division by zero
        if dt != 0:
            # Calculate jerk as the rate of change of acceleration
            measurement.jerk_x = (measurement.acceleration_x - previous_measurement.acceleration_x) / dt
            measurement.jerk_y = (measurement.acceleration_y - previous_measurement.acceleration_y) / dt
            measurement.jerk_z = (measurement.acceleration_z - previous_measurement.acceleration_z) / dt
        else:
            measurement.jerk_x = 0
            measurement.jerk_y = 0
            measurement.jerk_z = 0

        return measurement
