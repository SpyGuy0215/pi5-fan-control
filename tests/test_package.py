from pi5_fan_control import hello


def test_hello_returns_expected_message() -> None:
    assert hello() == "Hello from pi5-fan-control!"
