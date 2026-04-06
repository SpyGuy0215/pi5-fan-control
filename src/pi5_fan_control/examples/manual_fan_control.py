from pi5_fan_control.control import FanController
from time import sleep

# This example demonstrates how to manually control the fan speed.
# You can either turn the fan off, set it to max speed, or give the
# control back to the firmware. 
# Note: This relies on direct control of the PWM pins, so it may not
# work on all hardware revisions or configurations.

controller = FanController()

# set speed to 0
controller.fan_off()
sleep(1)
print("Fan turned off. Current speed:", controller.get_fan_speed())
sleep(0.5)

# set speed to max
controller.fan_max()
sleep(1)
print("Fan set to max. Current speed:", controller.get_fan_speed())
sleep(0.5)

# give back control to firmware
controller.fan_auto()
sleep(1)
print("Fan control returned to firmware. Current speed:", controller.get_fan_speed())
