from pi5_fan_control.control import FanController
import os

def test_find_hwmon_path() -> None:
    controller = FanController()
    hwmon_path = controller._find_hwmon_path()
    assert hwmon_path.startswith('/sys/class/hwmon/hwmon')
    assert os.path.exists(os.path.join(hwmon_path, 'fan1_input'))

def test_find_thermal_zone_path() -> None:
    controller = FanController()
    thermal_zone_path = controller._find_thermal_zone_path()
    assert thermal_zone_path.startswith('/sys/class/thermal/thermal_zone')
    assert os.path.exists(os.path.join(thermal_zone_path, 'temp'))

def test_get_available_policies() -> None:
    controller = FanController()
    policies = controller.get_available_policies()
    assert isinstance(policies, list)
    assert "step_wise" in policies

def test_get_current_policy() -> None:
    controller = FanController()
    current_policy = controller.get_current_policy()
    assert isinstance(current_policy, str)
    assert current_policy in controller.get_available_policies() or current_policy == "Unknown"

def test_get_fan_speed() -> None:
    controller = FanController()
    fan_speed = controller.get_fan_speed()
    assert isinstance(fan_speed, int)
    assert fan_speed >= 0

def test_get_current_temperature() -> None:
    controller = FanController()
    temperature = controller.get_current_temperature()
    assert isinstance(temperature, float)
    assert temperature > 0.0

def test_get_current_fan_curve() -> None:
    controller = FanController()
    curr_curve = controller.get_current_fan_curve()
    print(f"Current fan curve: {curr_curve}")
    assert isinstance(curr_curve, list)
    assert all(isinstance(point, dict) and len(point) == 2 for point in curr_curve)

def test_update_current_fan_curve() -> None:
    controller = FanController()
    try:
        # get the current values to restore later
        old_fan_curve = controller.get_current_fan_curve()[1:]  # skip the first point (critical shutdown temp)

        new_fan_curve = [{"temp": 30, "hyst": 0}, {"temp": 50, "hyst": 5}, {"temp": 70, "hyst": 3}, {"temp": 90, "hyst": 15}]
        controller.update_current_fan_curve(new_fan_curve)
        # check that the fan curve was updated
        updated_curve = controller.get_current_fan_curve()
        assert updated_curve[1:] == new_fan_curve  # skip the first point (critical shutdown temp)

        # restore the old fan curve
        controller.update_current_fan_curve(old_fan_curve)
    except Exception as e:
        assert False, f"update_fan_curve raised an exception: {e}"