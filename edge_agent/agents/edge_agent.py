"""Main Edge Agent implementation"""

from typing import Dict, Any, List, Optional
import asyncio
from datetime import datetime

from langchain.tools import BaseTool

from .base import BaseEdgeAgent
from .tools import (
    DeviceStatusTool, DeviceControlTool, ListDevicesTool, 
    EnergyAnalysisTool, ScheduleTool
)
from ..devices.models import Device, AirConditionerDevice, DeviceStatus
from ..devices.air_conditioner import AirConditionerController
from ..devices.base import MQTTDeviceInterface, HTTPDeviceInterface
from ..core.config import config
from ..core.logger import logger


class DeviceManager:
    """Manages all devices and their controllers"""
    
    def __init__(self):
        self.devices: Dict[str, Device] = {}
        self.controllers: Dict[str, Any] = {}
        self.interfaces: Dict[str, Any] = {}
    
    def add_device(self, device: Device, interface_type: str = "mqtt", **interface_kwargs):
        """Add a device to the manager"""
        self.devices[device.device_id] = device
        
        # Create interface
        if interface_type == "mqtt":
            mqtt_config = {
                "host": config.mqtt_broker_host,
                "port": config.mqtt_broker_port,
                "username": config.mqtt_username,
                "password": config.mqtt_password
            }
            mqtt_config.update(interface_kwargs)
            interface = MQTTDeviceInterface(device, mqtt_config)
        elif interface_type == "http":
            base_url = interface_kwargs.get("base_url", f"http://localhost:8080")
            interface = HTTPDeviceInterface(device, base_url)
        else:
            raise ValueError(f"Unsupported interface type: {interface_type}")
        
        self.interfaces[device.device_id] = interface
        
        # Create controller based on device type
        if isinstance(device, AirConditionerDevice):
            controller = AirConditionerController(device, interface)
            self.controllers[device.device_id] = controller
        
        logger.info(f"Added device {device.device_id} ({device.device_type}) to manager")
    
    def get_device(self, device_id: str) -> Optional[Device]:
        """Get device by ID"""
        return self.devices.get(device_id)
    
    def get_controller(self, device_id: str) -> Optional[Any]:
        """Get controller by device ID"""
        return self.controllers.get(device_id)
    
    def get_interface(self, device_id: str) -> Optional[Any]:
        """Get interface by device ID"""
        return self.interfaces.get(device_id)
    
    def list_devices(self) -> List[Device]:
        """List all devices"""
        return list(self.devices.values())
    
    async def connect_all_devices(self):
        """Connect to all devices"""
        for device_id, interface in self.interfaces.items():
            try:
                await interface.connect()
                logger.info(f"Connected to device {device_id}")
            except Exception as e:
                logger.error(f"Failed to connect to device {device_id}: {e}")
    
    async def disconnect_all_devices(self):
        """Disconnect from all devices"""
        for device_id, interface in self.interfaces.items():
            try:
                await interface.disconnect()
                logger.info(f"Disconnected from device {device_id}")
            except Exception as e:
                logger.error(f"Failed to disconnect from device {device_id}: {e}")


class EdgeAgent(BaseEdgeAgent):
    """Main Edge Agent for device management"""
    
    def __init__(self, device_manager: DeviceManager):
        self.device_manager = device_manager
        super().__init__(
            name="EdgeAgent",
            description="Intelligent AI Agent for edge device management, specializing in air conditioning systems and smart device control"
        )
    
    def _initialize_tools(self) -> List[BaseTool]:
        """Initialize agent tools"""
        return [
            DeviceStatusTool(self.device_manager),
            DeviceControlTool(self.device_manager),
            ListDevicesTool(self.device_manager),
            EnergyAnalysisTool(self.device_manager),
            ScheduleTool(self.device_manager)
        ]
    
    async def analyze_environment(self) -> Dict[str, Any]:
        """Analyze the current environment and device states"""
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "total_devices": len(self.device_manager.devices),
            "online_devices": 0,
            "offline_devices": 0,
            "devices_by_type": {},
            "active_air_conditioners": 0,
            "total_energy_consumption": 0.0,
            "recommendations": []
        }
        
        for device in self.device_manager.devices.values():
            # Count by status
            if device.status == DeviceStatus.ONLINE:
                analysis["online_devices"] += 1
            else:
                analysis["offline_devices"] += 1
            
            # Count by type
            device_type = device.device_type
            if device_type not in analysis["devices_by_type"]:
                analysis["devices_by_type"][device_type] = 0
            analysis["devices_by_type"][device_type] += 1
            
            # Air conditioner specific analysis
            if isinstance(device, AirConditionerDevice):
                if device.power_on:
                    analysis["active_air_conditioners"] += 1
                if device.energy_consumption:
                    analysis["total_energy_consumption"] += device.energy_consumption
        
        # Generate recommendations
        if analysis["offline_devices"] > 0:
            analysis["recommendations"].append(
                f"Check connectivity for {analysis['offline_devices']} offline devices"
            )
        
        if analysis["active_air_conditioners"] > 3:
            analysis["recommendations"].append(
                "Consider optimizing AC usage - multiple units running simultaneously"
            )
        
        if analysis["total_energy_consumption"] > 20.0:
            analysis["recommendations"].append(
                "High energy consumption detected - review temperature settings"
            )
        
        logger.info(f"Environment analysis completed: {analysis['total_devices']} devices analyzed")
        return analysis
    
    async def optimize_air_conditioning(self, target_temp_range: tuple = (22, 26)) -> Dict[str, Any]:
        """Optimize air conditioning across all AC units"""
        optimization_results = {
            "timestamp": datetime.now().isoformat(),
            "target_temperature_range": target_temp_range,
            "optimized_devices": [],
            "energy_savings_estimate": 0.0,
            "actions_taken": []
        }
        
        for device_id, device in self.device_manager.devices.items():
            if isinstance(device, AirConditionerDevice) and device.power_on:
                controller = self.device_manager.get_controller(device_id)
                if controller:
                    try:
                        # Get current temperature
                        current_temp = await controller.get_current_temperature()
                        
                        if current_temp and device.target_temperature:
                            # Optimize based on current conditions
                            if device.target_temperature < target_temp_range[0]:
                                # Temperature set too low
                                new_temp = target_temp_range[0]
                                await controller.set_temperature(new_temp)
                                optimization_results["actions_taken"].append(
                                    f"Raised temperature from {device.target_temperature}°C to {new_temp}°C for {device.name}"
                                )
                                optimization_results["energy_savings_estimate"] += 2.5
                            
                            elif device.target_temperature > target_temp_range[1]:
                                # Temperature set too high for cooling
                                new_temp = target_temp_range[1]
                                await controller.set_temperature(new_temp)
                                optimization_results["actions_taken"].append(
                                    f"Lowered temperature from {device.target_temperature}°C to {new_temp}°C for {device.name}"
                                )
                            
                            # Optimize fan speed based on temperature difference
                            if current_temp and abs(current_temp - device.target_temperature) < 1:
                                await controller.set_fan_speed(1)  # Low fan when close to target
                                optimization_results["actions_taken"].append(
                                    f"Reduced fan speed for {device.name} (close to target temperature)"
                                )
                                optimization_results["energy_savings_estimate"] += 1.0
                        
                        optimization_results["optimized_devices"].append(device_id)
                        
                    except Exception as e:
                        logger.error(f"Error optimizing AC {device_id}: {e}")
        
        logger.info(f"AC optimization completed for {len(optimization_results['optimized_devices'])} devices")
        return optimization_results
    
    async def handle_emergency_shutdown(self, reason: str = "Emergency") -> Dict[str, Any]:
        """Emergency shutdown of all devices"""
        shutdown_results = {
            "timestamp": datetime.now().isoformat(),
            "reason": reason,
            "devices_shutdown": [],
            "errors": []
        }
        
        for device_id, device in self.device_manager.devices.items():
            try:
                controller = self.device_manager.get_controller(device_id)
                if controller and hasattr(controller, 'power_off'):
                    await controller.power_off()
                    shutdown_results["devices_shutdown"].append(device_id)
                    logger.warning(f"Emergency shutdown: {device.name} ({device_id})")
                    
            except Exception as e:
                error_msg = f"Failed to shutdown {device_id}: {str(e)}"
                shutdown_results["errors"].append(error_msg)
                logger.error(error_msg)
        
        logger.warning(f"Emergency shutdown completed: {len(shutdown_results['devices_shutdown'])} devices")
        return shutdown_results
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health status"""
        health = {
            "timestamp": datetime.now().isoformat(),
            "system_status": "healthy",
            "devices": {},
            "alerts": [],
            "uptime_stats": {},
            "performance_metrics": {}
        }
        
        total_devices = len(self.device_manager.devices)
        online_count = 0
        
        for device_id, device in self.device_manager.devices.items():
            device_health = {
                "status": device.status.value,
                "last_seen": device.last_seen.isoformat() if device.last_seen else None,
                "health_score": 100  # Simplified health score
            }
            
            if device.status == DeviceStatus.ONLINE:
                online_count += 1
            elif device.status == DeviceStatus.ERROR:
                device_health["health_score"] = 0
                health["alerts"].append(f"Device {device.name} is in error state")
            elif device.status == DeviceStatus.OFFLINE:
                device_health["health_score"] = 30
                health["alerts"].append(f"Device {device.name} is offline")
            
            health["devices"][device_id] = device_health
        
        # Calculate system health
        if online_count == 0:
            health["system_status"] = "critical"
        elif online_count < total_devices * 0.5:
            health["system_status"] = "degraded"
        elif online_count < total_devices * 0.8:
            health["system_status"] = "warning"
        
        health["uptime_stats"] = {
            "total_devices": total_devices,
            "online_devices": online_count,
            "uptime_percentage": (online_count / total_devices * 100) if total_devices > 0 else 0
        }
        
        logger.info(f"System health check: {health['system_status']} - {online_count}/{total_devices} devices online")
        return health