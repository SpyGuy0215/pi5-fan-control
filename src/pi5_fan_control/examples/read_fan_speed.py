from pi5_fan_control.control import FanController

controller = FanController()
rpm = controller.get_rpm()

print(f"Current Fan Speed: {rpm} RPM")