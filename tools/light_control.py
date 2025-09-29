# tools/light_control.py
from langchain_core.tools import tool
import os

# 模拟的设备文件系统路径
_SIMULATED_SYS_PATH = "/tmp/edge_agent_sim/sys/"

@tool
def light_control(device_id: str, action: str) -> str:
    """
    控制灯光设备。可以开启或关闭灯光。
    - device_id: 要控制的灯光设备ID。
    - action: 要执行的操作，必须是 'turn_on' 或 'turn_off' 之一。
    """
    # --- 输入验证 ---
    # 确保传入的 action 是有效的，防止对设备进行不支持的操作。
    allowed_actions = ['turn_on', 'turn_off']
    if action not in allowed_actions:
        return f"错误：无效的操作 '{action}'。允许的操作包括: {allowed_actions}"

    # --- 定位设备 ---
    # 将逻辑设备ID映射到模拟的文件系统路径。
    light_path = os.path.join(_SIMULATED_SYS_PATH, device_id)
    if not os.path.exists(light_path):
        return f"错误：找不到设备 '{device_id}'。"

    # --- 执行操作 ---
    # 通过写文件来模拟改变灯光的状态。
    try:
        status_file = os.path.join(light_path, "status")
        
        if action == 'turn_on':
            with open(status_file, "w") as f:
                f.write("on")
            return f"成功：灯光 '{device_id}' 已开启。"
        
        elif action == 'turn_off':
            with open(status_file, "w") as f:
                f.write("off")
            return f"成功：灯光 '{device_id}' 已关闭。"

    except Exception as e:
        # --- 异常处理 ---
        # 捕获并报告在与模拟硬件交互时发生的任何错误。
        return f"错误：控制灯光 '{device_id}' 时发生异常: {e}"
