from pi5_fan_control.control import FanController

# This example demonstrates how to read the current fan speed (RPM)

controller = FanController()
rpm = controller.get_fan_speed()

print(f"Current Fan Speed: {rpm} RPM")