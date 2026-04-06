from pi5_fan_control.control import FanController

# This example demonstrates how to read the current fan curve configuration
# This information is also stored in the config.txt file (/boot/firmware/config.txt)

controller = FanController()
config = controller.get_config_fan_curve()

print("Current Fan Curve Configuration:")
print(config)
