import json

from tools.sensor_reader import sensor_reader
from tools.ac_control import ac_control
from tools.light_control import light_control


def test_sensor_reader_returns_devices_in_simulation_mode():
    readings = sensor_reader.invoke({"device_id": "all", "simulate": True})
    assert readings, "传感器读取结果不应为空"
    assert all("device_id" in item for item in readings)


def test_sensor_reader_missing_path_returns_error():
    result = sensor_reader.invoke({"device_id": "unknown", "simulate": False})
    assert result
    assert "error" in result[0]


def test_ac_control_operations():
    # 先使用 sensor_reader 创建模拟环境
    sensor_reader.invoke({"device_id": "all", "simulate": True})

    assert "成功" in ac_control.invoke({"device_id": "ac_01", "action": "turn_on"})
    assert "成功" in ac_control.invoke({"device_id": "ac_01", "action": "set_temperature", "temperature": 23})
    assert "成功" in ac_control.invoke({"device_id": "ac_01", "action": "turn_off"})


def test_light_control_operations():
    sensor_reader.invoke({"device_id": "all", "simulate": True})

    assert "成功" in light_control.invoke({"device_id": "light_01", "action": "turn_on"})
    assert "成功" in light_control.invoke({"device_id": "light_01", "action": "turn_off"})
