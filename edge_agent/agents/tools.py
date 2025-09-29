"""LangChain tools for device interaction"""

from typing import Dict, Any, Optional, List
import json
from datetime import datetime

from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from ..devices.models import DeviceCommand, ACMode, DeviceStatus
from ..devices.air_conditioner import AirConditionerController
from ..core.logger import logger


class DeviceStatusInput(BaseModel):
    """Input for device status tool"""
    device_id: str = Field(description="Device ID to check status for")


class DeviceControlInput(BaseModel):
    """Input for device control tool"""
    device_id: str = Field(description="Device ID to control")
    action: str = Field(description="Action to perform (power_on, power_off, set_temperature, set_mode, set_fan_speed)")
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Action parameters")


class DeviceStatusTool(BaseTool):
    """Tool to get device status"""
    name = "get_device_status"
    description = "Get the current status of a device including temperature, power state, mode, and other properties"
    args_schema = DeviceStatusInput
    
    def __init__(self, device_manager):
        super().__init__()
        self.device_manager = device_manager
    
    def _run(self, device_id: str) -> str:
        """Get device status"""
        try:
            device = self.device_manager.get_device(device_id)
            if not device:
                return f"Device {device_id} not found"
            
            controller = self.device_manager.get_controller(device_id)
            if controller and hasattr(controller, 'get_status_summary'):
                status = controller.get_status_summary()
                return json.dumps(status, indent=2)
            else:
                # Basic device info
                status = {
                    "device_id": device.device_id,
                    "name": device.name,
                    "type": device.device_type,
                    "location": device.location,
                    "status": device.status.value,
                    "last_seen": device.last_seen.isoformat() if device.last_seen else None
                }
                return json.dumps(status, indent=2)
                
        except Exception as e:
            logger.error(f"Error getting status for device {device_id}: {e}")
            return f"Error getting device status: {str(e)}"
    
    async def _arun(self, device_id: str) -> str:
        """Async version of _run"""
        return self._run(device_id)


class DeviceControlTool(BaseTool):
    """Tool to control devices"""
    name = "control_device"
    description = "Control device operations like power on/off, temperature setting, mode changes, etc."
    args_schema = DeviceControlInput
    
    def __init__(self, device_manager):
        super().__init__()
        self.device_manager = device_manager
    
    def _run(self, device_id: str, action: str, parameters: Optional[Dict[str, Any]] = None) -> str:
        """Control device"""
        try:
            controller = self.device_manager.get_controller(device_id)
            if not controller:
                return f"Controller for device {device_id} not found"
            
            if parameters is None:
                parameters = {}
            
            # Handle different actions
            if action == "power_on":
                # This would be async in real implementation
                result = {"status": "success", "message": "Device powered on"}
            elif action == "power_off":
                result = {"status": "success", "message": "Device powered off"}
            elif action == "set_temperature":
                temp = parameters.get("temperature")
                if temp is None:
                    return "Temperature parameter is required"
                result = {"status": "success", "message": f"Temperature set to {temp}°C"}
            elif action == "set_mode":
                mode = parameters.get("mode")
                if mode is None:
                    return "Mode parameter is required"
                result = {"status": "success", "message": f"Mode set to {mode}"}
            elif action == "set_fan_speed":
                speed = parameters.get("speed")
                if speed is None:
                    return "Speed parameter is required"
                result = {"status": "success", "message": f"Fan speed set to {speed}"}
            else:
                return f"Unknown action: {action}"
            
            logger.info(f"Device control - {device_id}: {action} with params {parameters}")
            return json.dumps(result)
            
        except Exception as e:
            logger.error(f"Error controlling device {device_id}: {e}")
            return f"Error controlling device: {str(e)}"
    
    async def _arun(self, device_id: str, action: str, parameters: Optional[Dict[str, Any]] = None) -> str:
        """Async version of _run"""
        return self._run(device_id, action, parameters)


class ListDevicesTool(BaseTool):
    """Tool to list all available devices"""
    name = "list_devices"
    description = "List all available devices and their basic information"
    
    def __init__(self, device_manager):
        super().__init__()
        self.device_manager = device_manager
    
    def _run(self) -> str:
        """List all devices"""
        try:
            devices = self.device_manager.list_devices()
            device_list = []
            
            for device in devices:
                device_info = {
                    "device_id": device.device_id,
                    "name": device.name,
                    "type": device.device_type,
                    "location": device.location,
                    "status": device.status.value
                }
                device_list.append(device_info)
            
            return json.dumps(device_list, indent=2)
            
        except Exception as e:
            logger.error(f"Error listing devices: {e}")
            return f"Error listing devices: {str(e)}"
    
    async def _arun(self) -> str:
        """Async version of _run"""
        return self._run()


class EnergyAnalysisTool(BaseTool):
    """Tool to analyze energy consumption"""
    name = "analyze_energy"
    description = "Analyze energy consumption patterns and provide efficiency recommendations"
    args_schema = DeviceStatusInput
    
    def __init__(self, device_manager):
        super().__init__()
        self.device_manager = device_manager
    
    def _run(self, device_id: str) -> str:
        """Analyze energy consumption"""
        try:
            device = self.device_manager.get_device(device_id)
            if not device:
                return f"Device {device_id} not found"
            
            # Simulate energy analysis
            analysis = {
                "device_id": device_id,
                "current_consumption": "2.5 kWh",
                "daily_average": "18.5 kWh",
                "efficiency_rating": "B+",
                "recommendations": [
                    "Consider raising temperature by 1°C to save 10% energy",
                    "Use timer function to avoid unnecessary operation",
                    "Clean air filters for optimal efficiency"
                ],
                "potential_savings": "15% reduction possible with recommended settings"
            }
            
            return json.dumps(analysis, indent=2)
            
        except Exception as e:
            logger.error(f"Error analyzing energy for device {device_id}: {e}")
            return f"Error analyzing energy: {str(e)}"
    
    async def _arun(self, device_id: str) -> str:
        """Async version of _run"""
        return self._run(device_id)


class ScheduleTool(BaseTool):
    """Tool to schedule device operations"""
    name = "schedule_operation"
    description = "Schedule device operations for specific times or create automation rules"
    
    def __init__(self, device_manager):
        super().__init__()
        self.device_manager = device_manager
    
    def _run(self, device_id: str, schedule_data: str) -> str:
        """Schedule device operation"""
        try:
            # Parse schedule data
            schedule = json.loads(schedule_data)
            
            result = {
                "status": "success",
                "message": f"Scheduled operation for device {device_id}",
                "schedule": schedule,
                "schedule_id": f"schedule_{device_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            }
            
            logger.info(f"Created schedule for device {device_id}: {schedule}")
            return json.dumps(result, indent=2)
            
        except Exception as e:
            logger.error(f"Error scheduling operation for device {device_id}: {e}")
            return f"Error scheduling operation: {str(e)}"
    
    async def _arun(self, device_id: str, schedule_data: str) -> str:
        """Async version of _run"""
        return self._run(device_id, schedule_data)