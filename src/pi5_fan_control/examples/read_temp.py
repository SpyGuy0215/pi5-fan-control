from pi5_fan_control.control import FanController

controller = FanController()
temperature = controller.get_temperature()

print(f"Current CPU Temperature: {temperature:.2f} °C")