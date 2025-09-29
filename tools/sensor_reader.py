# tools/sensor_reader.py
import os
import json
import time
from typing import Dict, Any, List

class SensorReaderTool:
    """
    传感器读取工具。

    这个工具封装了与硬件或模拟传感器交互的底层细节。
    Agent 通过调用这个工具来“感知”环境，而无需关心数据是如何具体获取的。
    这种设计使得更换传感器硬件或修改数据源时，只需修改这个工具，而 Agent 的逻辑保持不变。
    """
    name = "sensor_reader"
    description = "读取指定传感器或所有设备的实时数据。"

    # 模拟的设备文件系统路径
    _SIMULATED_SYS_PATH = "/tmp/edge_agent_sim/sys/"

    def __init__(self, simulate: bool = True):
        """
        初始化工具。

        Args:
            simulate (bool): 是否启用模拟模式。在生产环境中应设为 False。
        """
        self.simulate = simulate
        if self.simulate:
            self._setup_simulation()

    def _setup_simulation(self):
        """
        创建模拟的设备文件，用于开发和测试。
        这个函数模拟了真实硬件在文件系统中的表现。
        """
        # 确保模拟目录存在
        os.makedirs(os.path.join(self._SIMULATED_SYS_PATH, "temp_sensor_01"), exist_ok=True)
        os.makedirs(os.path.join(self._SIMULATED_SYS_PATH, "light_01"), exist_ok=True)
        os.makedirs(os.path.join(self._SIMULATED_SYS_PATH, "ac_01"), exist_ok=True)

        # 模拟温度传感器数据
        with open(os.path.join(self._SIMULATED_SYS_PATH, "temp_sensor_01", "data"), "w") as f:
            json.dump({"value": 25.5, "unit": "C"}, f)

        # 模拟灯光状态
        with open(os.path.join(self._SIMULATED_SYS_PATH, "light_01", "status"), "w") as f:
            f.write("off")

        # 模拟空调状态
        with open(os.path.join(self._SIMULATED_SYS_PATH, "ac_01", "status"), "w") as f:
            f.write("off")
        with open(os.path.join(self._SIMULATED_SYS_PATH, "ac_01", "config"), "w") as f:
            json.dump({"mode": "cool", "temperature": 26}, f)


    def execute(self, device_id: str = "all") -> List[Dict[str, Any]]:
        """
        执行读取操作。

        Args:
            device_id (str): 要读取的设备 ID。如果为 "all"，则返回所有设备的状态。

        Returns:
            List[Dict[str, Any]]: 一个包含设备状态的列表。
        """
        if self.simulate:
            path = self._SIMULATED_SYS_PATH
        else:
            # 在生产环境中，这里应指向真实的 /sys 路径
            path = "/sys/i800/" # 假设的真实路径

        if not os.path.exists(path):
            return [{"error": f"设备路径 {path} 不存在。"}]

        devices_to_scan = [device_id] if device_id != "all" else os.listdir(path)
        results = []

        for dev_id in devices_to_scan:
            dev_path = os.path.join(path, dev_id)
            if not os.path.isdir(dev_path):
                continue

            # 读取设备数据
            data = {"device_id": dev_id, "timestamp": time.time()}
            # ... 在这里添加更复杂的读取逻辑 ...
            # 例如，根据设备类型读取不同的文件
            if os.path.exists(os.path.join(dev_path, "data")):
                with open(os.path.join(dev_path, "data"), "r") as f:
                    data.update(json.load(f))
            if os.path.exists(os.path.join(dev_path, "status")):
                 with open(os.path.join(dev_path, "status"), "r") as f:
                    data["status"] = f.read().strip()

            results.append(data)

        return results
