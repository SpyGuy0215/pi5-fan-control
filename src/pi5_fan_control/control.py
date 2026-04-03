import os
import glob

class FanController:
    def __init__(self):
        self.hwmon_path = self._find_hwmon_path()
        self.thermal_zone_path = self._find_thermal_zone_path()

        # verify that we have sudo permissions for operations
        if os.geteuid() != 0:
            raise PermissionError("This program requires sudo permissions to run.")
    

    def _find_hwmon_path(self) -> str:
        hwmon_dirs = glob.glob('/sys/class/hwmon/hwmon*')
        for hwmon_dir in hwmon_dirs:
            if os.path.exists(os.path.join(hwmon_dir, 'fan1_input')):
                return hwmon_dir
        raise FileNotFoundError("No hwmon directory with fan1_input found.")
    
    def _find_thermal_zone_path(self) -> str:
        thermal_zone_dirs = glob.glob('/sys/class/thermal/thermal_zone*')
        for thermal_zone_dir in thermal_zone_dirs:
            if os.path.exists(os.path.join(thermal_zone_dir, 'temp')):
                return thermal_zone_dir
        raise FileNotFoundError("No thermal zone directory with temp found.")
    
    def get_available_policies(self) -> list:
        """Get available fan curve policies"""
        policies = []
        policy_path = os.path.join(self.thermal_zone_path, 'available_policies')
        if os.path.exists(policy_path):
            with open(policy_path, 'r') as f:
                policies = f.read().strip().split()
        return policies
    
    def get_current_policy(self) -> str:
        """Get current fan curve policy"""
        policy_path = os.path.join(self.thermal_zone_path, 'policy')
        if os.path.exists(policy_path):
            with open(policy_path, 'r') as f:
                return f.read().strip()
        return "Unknown"

    def get_fan_speed(self) -> int:
        """Read hwmon to get current fan speed"""
        fan_speed_path = os.path.join(self.hwmon_path, 'fan1_input')
        if os.path.exists(fan_speed_path):
            with open(fan_speed_path, 'r') as f:
                return int(f.read().strip())
        raise FileNotFoundError("fan1_input not found in hwmon directory.")
    
    def get_current_temperature(self) -> float:
        """Get current CPU temperature in Celsius from thermalzone0"""
        temp_path = os.path.join(self.thermal_zone_path, 'temp')
        if os.path.exists(temp_path):
            with open(temp_path, 'r') as f:
                return int(f.read().strip()) / 1000.0   # convert from millidegrees to degrees
        raise FileNotFoundError("temp not found in thermal zone directory.")

    def update_fan_curve(self, curve: list) -> None:
        """
        Update both the persistent and the current fan curves
        :param curve: List of dictionaries with 'temp', 'speed', and 'hysteresis' keys, e.g. [{'temp': 50, 'speed': 30, 'hyst': 5}, {'temp': 70, 'speed': 100, 'hyst': 10}]
        """
        # Check if curve is valid (ascending temps)
        if not all(curve[i]['temp'] < curve[i+1]['temp'] for i in range(len(curve)-1)):
            raise ValueError("Fan curve temperatures must be in ascending order.")
        
        update_current_fan_curve(curve)
    
    def get_current_fan_curve(self) -> list:
        """Get the current fan curve by reading thermalzone0 trip points."""
        curve = []
        i = 1       # start from 1 since trip_point_0 is often reserved for critical shutdown temp
        while True:
            temp_path = os.path.join(self.thermal_zone_path, f'trip_point_{i}_temp')
            hysteresis_path = os.path.join(self.thermal_zone_path, f'trip_point_{i}_hyst')
            if os.path.exists(temp_path) and os.path.exists(hysteresis_path):
                with open(temp_path, 'r') as temp_file:
                    temp = int(temp_file.read().strip()) / 1000.0  # convert from millidegrees to degrees
                with open(hysteresis_path, 'r') as hysteresis_file:
                    hyst = int(hysteresis_file.read().strip()) / 1000.0  # convert from millidegrees to degrees
                curve.append({'temp': temp, 'hyst': hyst})
                i += 1
            else:
                break
        return curve

    def update_current_fan_curve(curve: list) -> None:
        """
        Update the current fan curve by writing to thermalzone0 trip points.
        Note: sysfs only supports updating temps and hysterisis during runtime, not speeds.
        :param curve: List of dictionaries with 'temp' and 'hysterisis' keys, e.g. [{'temp': 50, 'hyst': 5}, {'temp': 70, 'hyst': 10}]
                      Speed values can be provided, but they will be ignored.
        """
        
        for i, (t, h) in enumerate(zip(curve['temp'], curve['hyst'])):
            temp_path = os.path.join(self.thermal_zone_path, f'trip_point_{i}_temp')
            hysteresis_path = os.path.join(self.thermal_zone_path, f'trip_point_{i}_hyst')
            if os.path.exists(temp_path) and os.path.exists(hysteresis_path):
                with open(temp_path, 'w') as temp_file:
                    temp_file.write(str(t * 1000))  # convert from degrees to millidegrees
                with open(hysteresis_path, 'w') as hysteresis_file:
                    hysteresis_file.write(str(h * 1000))  # convert from degrees to millidegrees
            else:
                raise FileNotFoundError(f"temp{i} or hysteresis{i} not found in thermal zone directory.")
