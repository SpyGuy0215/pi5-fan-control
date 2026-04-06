from pi5_fan_control.control import FanController

# This example demonstrates how to update the fan curve configuration
# Temperature: The CPU temperature at which the fan speed should change
# Speed: The fan speed percentage (0-100) corresponding to the temperature
# Hysteresis: The temperature difference to prevent rapid fan speed changes
#             i.e. a 5 degree hysteresis means that the fan will only drop
#             to a lower speed if the temp drops 5 degrees below the threshold
# Each point in the curve should be a dictionary with 'temp', 'speed', and 'hyst'
# keys, and each curve should have exactly 4 points with ascending temperatures

controller = FanController()
curve = [
    {"temp": 40, "speed": 20, "hyst": 5},
    {"temp": 50, "speed": 40, "hyst": 10},
    {"temp": 60, "speed": 70, "hyst": 15},
    {"temp": 70, "speed": 100, "hyst": 20}
]       # this curve will blast pretty fast even at lower temps!

controller.update_fan_curve(curve)
print("Fan curve updated successfully!")

# Now check that it updated...
current_curve = controller.get_config_fan_curve()
print("Current Fan Curve Configuration:")
print(current_curve)
is_updated = current_curve == curve
print(f"Fan curve update verification: {'Success' if is_updated else 'Failure'}")

# And now, clear the curve after the test to restore defaults
controller.clear_config_fan_curve()
print("Fan curve configuration cleared to defaults.")