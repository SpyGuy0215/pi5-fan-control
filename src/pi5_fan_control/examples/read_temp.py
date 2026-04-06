from pi5_fan_control.control import FanController

# This example demonstrates how to read the current CPU temperature

controller = FanController()
temperature = controller.get_temperature()

print(f"Current CPU Temperature: {temperature:.2f} °C")