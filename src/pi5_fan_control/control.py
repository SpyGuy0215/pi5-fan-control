import os
import shutil
import glob
import re
import tempfile

class FanController:
    def __init__(self):
        self.hwmon_path = self._find_hwmon_path()
        self.thermal_zone_path = self._find_thermal_zone_path()

        # verify that we have sudo permissions for operations
        if os.geteuid() != 0:
            raise PermissionError("This program requires sudo permissions to run.")
        
        self.config_path = '/boot/firmware/config.txt'
    

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
        
        #1. Check if a backup of the current config.txt exists, if not create one
        backup_path = self.config_path + '.bak'
        if not os.path.exists(backup_path):
            shutil.copyfile(self.config_path, backup_path)

        #2. Read the current config file 
        with open(self.config_path, 'r') as f:
            lines = f.readlines()

        #3. Remove any previously managed block so we do not keep appending duplicates.
        start_marker = "# --- Pi5 Fan Control Settings ---"
        end_marker = "# --- End of Pi5 Fan Control Settings ---"
        new_lines = []
        in_managed_block = False
        for line in lines:
            stripped = line.strip()
            if stripped == start_marker:
                in_managed_block = True
                continue
            if in_managed_block and stripped == end_marker:
                in_managed_block = False
                continue
            if not in_managed_block:
                new_lines.append(line)

        #4. Generate a fresh managed block and append it once.
        if new_lines and not new_lines[-1].endswith("\n"):
            new_lines[-1] = new_lines[-1] + "\n"
        new_lines.append(f"\n{start_marker}\n")
        for i, point in enumerate(curve):
            temp_millic = int(point['temp'] * 1000)
            hyst_millic = int(point.get('hyst', 0) * 1000)  # default hysteresis to 0 if not provided
            speed = point['speed']
            new_lines.append(f"dtparam=fan_temp{i}={temp_millic}\n")
            new_lines.append(f"dtparam=fan_speed{i}={speed}\n")
            if hyst_millic > 0:
                new_lines.append(f"dtparam=fan_temp{i}_hyst={hyst_millic}\n")
        new_lines.append(f"{end_marker}\n")

        #5. Perform an atomic write to the config file
        fd, temp_path = tempfile.mkstemp(dir='/boot/firmware')
        try:
            with os.fdopen(fd, 'w') as tmp_file:
                tmp_file.writelines(new_lines)
            os.replace(temp_path, self.config_path)  # atomic operation
            os.chmod(self.config_path, 0o644)  # ensure correct permissions
        except Exception as e:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise e
         
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
    
    def get_config_fan_curve(self) -> list:
        """Get the fan curve defined in the config.txt file."""
        curve = []
        with open(self.config_path, 'r') as f:
            lines = f.readlines()
        
        # Extract lines between the Pi5 Fan Control Settings markers
        in_block = False
        for line in lines:
            if line.strip() == "# --- Pi5 Fan Control Settings ---":
                in_block = True
                continue
            elif line.strip() == "# --- End of Pi5 Fan Control Settings ---":
                break
            
            if in_block:
                temp_match = re.match(r"^dtparam=fan_temp(\d)=(\d+)", line.strip())
                speed_match = re.match(r"^dtparam=fan_speed(\d)=(\d+)", line.strip())
                hyst_match = re.match(r"^dtparam=fan_temp(\d)_hyst=(\d+)", line.strip())
                
                if temp_match:
                    index = int(temp_match.group(1))
                    temp = int(temp_match.group(2)) / 1000.0  # convert from millidegrees to degrees
                    while len(curve) <= index:
                        curve.append({'temp': None, 'speed': None, 'hyst': None})
                    curve[index]['temp'] = temp
                elif speed_match:
                    index = int(speed_match.group(1))
                    speed = int(speed_match.group(2))
                    while len(curve) <= index:
                        curve.append({'temp': None, 'speed': None, 'hyst': None})
                    curve[index]['speed'] = speed
                elif hyst_match:
                    index = int(hyst_match.group(1))
                    hyst = int(hyst_match.group(2)) / 1000.0  # convert from millidegrees to degrees
                    while len(curve) <= index:
                        curve.append({'temp': None, 'speed': None, 'hyst': None})
                    curve[index]['hyst'] = hyst
        return curve

    def clear_config_fan_curve(self) -> None:
        """Remove any managed fan curve settings from the config.txt file."""
        #1. Read the current config file 
        with open(self.config_path, 'r') as f:
            lines = f.readlines()

        #2. Remove any previously managed block so we do not keep appending duplicates.
        start_marker = "# --- Pi5 Fan Control Settings ---"
        end_marker = "# --- End of Pi5 Fan Control Settings ---"
        new_lines = []
        in_managed_block = False
        for line in lines:
            stripped = line.strip()
            if stripped == start_marker:
                in_managed_block = True
                continue
            elif stripped == end_marker:
                in_managed_block = False
                continue

            if not in_managed_block:
                new_lines.append(line)
        #3. Perform an atomic write to the config file
        fd, temp_path = tempfile.mkstemp(dir='/boot/firmware')
        try:
            with os.fdopen(fd, 'w') as tmp_file:
                tmp_file.writelines(new_lines)
            os.replace(temp_path, self.config_path)  # atomic operation
            os.chmod(self.config_path, 0o644)  # ensure correct permissions
        except Exception as e:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise e 

    def fan_off(self) -> None:
        """Immediately turn the fan off with pinctrl"""
        os.system("pinctrl FAN_PWM op dh")
    
    def fan_max(self) -> None:
        """Immediately turn the fan on at max speed with pinctrl"""
        os.system("pinctrl FAN_PWM op dl")
    
    def fan_auto(self):
        """Set the fan back to automatic control with pinctrl"""
        os.system("pinctrl FAN_PWM op a0")