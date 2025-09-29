# api/main.py
# FastAPI接口示例
from fastapi import FastAPI
from agent.device_agent import DeviceAgent
from agent.ac_agent import ACAgent

app = FastAPI()
device_agent = DeviceAgent()
ac_agent = ACAgent()

@app.get("/devices")
def get_devices():
    """获取所有边缘设备及状态"""
    return device_agent.perceive()

@app.get("/acs")
def get_acs():
    """获取所有空调设备及状态"""
    return ac_agent.perceive()

@app.post("/acs/{ac_id}/control")
def control_ac(ac_id: str, action: str):
    """控制空调启停"""
    return ac_agent.control_ac(ac_id, action)
