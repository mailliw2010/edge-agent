# tools/ac_control.py
from langchain_core.tools import tool
import os
import json

from core.reliability import (
    OperationTimeoutError,
    ResilienceError,
    run_with_resilience,
)

# 模拟的设备文件系统路径
_SIMULATED_SYS_PATH = "/tmp/edge_agent_sim/sys/"

TOOL_TIMEOUT_SECONDS = float(os.getenv("TOOL_TIMEOUT_SECONDS", "5"))
TOOL_MAX_ATTEMPTS = int(os.getenv("TOOL_MAX_ATTEMPTS", "3"))

@tool
def ac_control(device_id: str, action: str, temperature: float = None) -> str:
    """
    控制空调设备。可以开启、关闭空调，或设置温度。
    - device_id: 要控制的空调设备ID。
    - action: 要执行的操作，必须是 'turn_on', 'turn_off', 或 'set_temperature' 之一。
    - temperature: 当 action 为 'set_temperature' 时，需要设置的目标温度。
    """
    # --- 输入验证 ---
    # 这是工具的“保护层”。在执行任何操作之前，首先检查输入参数的有效性。
    # 这样做可以防止无效的指令对物理设备造成潜在的损害或导致系统进入未知状态。
    # 例如，防止向一个不存在的设备发送指令，或执行一个不支持的操作。
    allowed_actions = ['turn_on', 'turn_off', 'set_temperature']
    if action not in allowed_actions:
        return f"错误：无效的操作 '{action}'。允许的操作包括: {allowed_actions}"
    
    if action == 'set_temperature' and temperature is None:
        return "错误：设置温度时必须提供 'temperature' 参数。"

    # --- 定位设备 ---
    # 根据 device_id 构建设备在（模拟）文件系统中的路径。
    # 这是将逻辑设备ID映射到物理或模拟设备接口的关键步骤。
    ac_path = os.path.join(_SIMULATED_SYS_PATH, device_id)
    if not os.path.exists(ac_path):
        return f"错误：找不到设备 '{device_id}'。"

    # --- 执行操作 ---
    # 这是工具的核心逻辑，负责与“硬件”进行交互。
    # 通过读写文件来模拟对设备状态和配置的更改。
    status_file = os.path.join(ac_path, "status")
    config_file = os.path.join(ac_path, "config")

    def _operate() -> str:
        if action == 'turn_on':
            with open(status_file, "w") as f:
                f.write("on")
            return f"成功：空调 '{device_id}' 已开启。"

        if action == 'turn_off':
            with open(status_file, "w") as f:
                f.write("off")
            return f"成功：空调 '{device_id}' 已关闭。"

        # action == 'set_temperature'
        with open(config_file, "r+") as f:
            config_data = json.load(f)
            config_data['temperature'] = temperature
            f.seek(0)  # 回到文件开头
            json.dump(config_data, f)
            f.truncate()  # 清除可能存在的旧文件内容
        return f"成功：空调 '{device_id}' 温度已设置为 {temperature}°C。"

    try:
        return run_with_resilience(
            "ac_control",
            _operate,
            timeout_seconds=TOOL_TIMEOUT_SECONDS,
            max_attempts=TOOL_MAX_ATTEMPTS,
            retry_exceptions=(OSError, IOError, json.JSONDecodeError, OperationTimeoutError),
        )
    except ResilienceError as exc:
        return f"错误：控制空调 '{device_id}' 时发生异常: {exc}"
