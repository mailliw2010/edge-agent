# tools/sensor_reader.py
from langchain_core.tools import tool
import os
import json
import time
from typing import Dict, Any, List, Optional

from config import settings

from core.reliability import (
    OperationTimeoutError,
    ResilienceError,
    run_with_resilience,
)

# 模拟的设备文件系统路径
_SIMULATED_SYS_PATH = "/tmp/edge_agent_sim/sys/"

TOOL_TIMEOUT_SECONDS = float(os.getenv("TOOL_TIMEOUT_SECONDS", "5"))
TOOL_MAX_ATTEMPTS = int(os.getenv("TOOL_MAX_ATTEMPTS", "3"))

def _setup_simulation():
    """
    一个辅助函数，用于创建模拟的设备文件，仅用于开发和测试。
    这个函数模拟了真实硬件在文件系统中的表现。
    """
    # 确保模拟目录存在
    os.makedirs(os.path.join(_SIMULATED_SYS_PATH, "temp_sensor_01"), exist_ok=True)
    os.makedirs(os.path.join(_SIMULATED_SYS_PATH, "light_01"), exist_ok=True)
    os.makedirs(os.path.join(_SIMULATED_SYS_PATH, "ac_01"), exist_ok=True)

    # 模拟温度传感器数据
    with open(os.path.join(_SIMULATED_SYS_PATH, "temp_sensor_01", "data"), "w") as f:
        json.dump({"value": 25.5, "unit": "C"}, f)

    # 模拟灯光状态
    with open(os.path.join(_SIMULATED_SYS_PATH, "light_01", "status"), "w") as f:
        f.write("off")

    # 模拟空调状态
    with open(os.path.join(_SIMULATED_SYS_PATH, "ac_01", "status"), "w") as f:
        f.write("off")
    with open(os.path.join(_SIMULATED_SYS_PATH, "ac_01", "config"), "w") as f:
        json.dump({"mode": "cool", "temperature": 26}, f)

@tool
def sensor_reader(device_id: str = "all", simulate: Optional[bool] = None) -> List[Dict[str, Any]]:
    """
    读取指定传感器或所有设备的实时数据。
    - device_id: 要读取的设备ID。如果为 "all"，则返回所有设备的状态。
    - simulate: 是否启用模拟模式。在生产环境中应设为 False。
    """
    if simulate is None:
        simulate = settings.SIMULATION_MODE

    if simulate:
        _setup_simulation()
        path = _SIMULATED_SYS_PATH
    else:
        # 在生产环境中，这里应指向真实的 /sys 路径
        path = "/sys/i800/" # 假设的真实路径

    if not os.path.exists(path):
        return [{"error": f"设备路径 {path} 不存在。"}]

    def _read_devices() -> List[Dict[str, Any]]:
        devices_to_scan = [device_id] if device_id != "all" else os.listdir(path)
        results: List[Dict[str, Any]] = []

        for dev_id in devices_to_scan:
            dev_path = os.path.join(path, dev_id)
            if not os.path.isdir(dev_path):
                continue

            # 读取设备数据
            data: Dict[str, Any] = {"device_id": dev_id, "timestamp": time.time()}
            if os.path.exists(os.path.join(dev_path, "data")):
                with open(os.path.join(dev_path, "data"), "r") as f:
                    data.update(json.load(f))
            if os.path.exists(os.path.join(dev_path, "status")):
                with open(os.path.join(dev_path, "status"), "r") as f:
                    data["status"] = f.read().strip()

            results.append(data)

        return results

    try:
        return run_with_resilience(
            "sensor_reader",
            _read_devices,
            timeout_seconds=TOOL_TIMEOUT_SECONDS,
            max_attempts=TOOL_MAX_ATTEMPTS,
            retry_exceptions=(OSError, IOError, json.JSONDecodeError, OperationTimeoutError),
        )
    except ResilienceError as exc:
        return [{"error": f"读取设备状态失败：{exc}"}]
