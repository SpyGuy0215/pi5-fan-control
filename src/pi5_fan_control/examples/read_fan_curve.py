from pi5_fan_control.control import FanController

controller = FanController()
config = controller.get_current_config()

print("Current Fan Curve Configuration:")
for point, temp in config.items():
    print(f"{point}: {temp:.2f} °C")
