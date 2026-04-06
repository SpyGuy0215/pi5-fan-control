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

def test_get_config_fan_curve() -> None:
    controller = FanController()
    config_curve = controller.get_config_fan_curve()
    print(f"Config fan curve: {config_curve}")
    assert isinstance(config_curve, list)
    assert len(config_curve) >= 0
    assert all(isinstance(point, dict) and len(point) == 3 for point in config_curve)

def test_update_fan_curve() -> None:
    controller = FanController()
    old_curve = controller.get_config_fan_curve()
    new_curve = [
        {"temp": 40, "speed": 20, "hyst": 5},
        {"temp": 50, "speed": 40, "hyst": 10},
        {"temp": 65, "speed": 60, "hyst": 15},
        {"temp": 80, "speed": 80, "hyst": 20},
    ]
    controller.update_fan_curve(new_curve)
    # After updating the fan curve, we can check if the current fan curve matches the new curve
    curr_curve = controller.get_config_fan_curve()
    assert curr_curve == new_curve

    # Restore the original curve after the test
    controller.update_fan_curve(old_curve)

def test_clear_config() -> None:
    controller = FanController()
    old_curve = controller.get_config_fan_curve()
    controller.clear_config_fan_curve()
    cleared_curve = controller.get_config_fan_curve()
    assert cleared_curve == []
    # Restore the original curve after the test
    controller.update_fan_curve(old_curve)