"""Base device interface and communication protocols"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import asyncio
import json
from datetime import datetime

from ..core.logger import logger
from .models import Device, DeviceCommand, DeviceState, DeviceStatus


class DeviceInterface(ABC):
    """Abstract base class for device interfaces"""
    
    def __init__(self, device: Device):
        self.device = device
        self._is_connected = False
        
    @abstractmethod
    async def connect(self) -> bool:
        """Connect to the device"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from the device"""
        pass
    
    @abstractmethod
    async def send_command(self, command: DeviceCommand) -> Dict[str, Any]:
        """Send command to device"""
        pass
    
    @abstractmethod
    async def get_status(self) -> DeviceState:
        """Get current device status"""
        pass
    
    @abstractmethod
    async def get_properties(self) -> Dict[str, Any]:
        """Get device properties"""
        pass
    
    @property
    def is_connected(self) -> bool:
        """Check if device is connected"""
        return self._is_connected


class MQTTDeviceInterface(DeviceInterface):
    """MQTT-based device interface"""
    
    def __init__(self, device: Device, mqtt_config: Dict[str, Any]):
        super().__init__(device)
        self.mqtt_config = mqtt_config
        self.mqtt_client = None
        self._command_topic = f"devices/{device.device_id}/commands"
        self._status_topic = f"devices/{device.device_id}/status"
        self._response_topic = f"devices/{device.device_id}/responses"
        
    async def connect(self) -> bool:
        """Connect to MQTT broker and subscribe to device topics"""
        try:
            # Import asyncio_mqtt here to avoid import errors if not installed
            from asyncio_mqtt import Client
            
            self.mqtt_client = Client(
                hostname=self.mqtt_config.get("host", "localhost"),
                port=self.mqtt_config.get("port", 1883),
                username=self.mqtt_config.get("username"),
                password=self.mqtt_config.get("password")
            )
            
            await self.mqtt_client.__aenter__()
            await self.mqtt_client.subscribe(self._status_topic)
            await self.mqtt_client.subscribe(self._response_topic)
            
            self._is_connected = True
            self.device.status = DeviceStatus.ONLINE
            self.device.last_seen = datetime.now()
            
            logger.info(f"Connected to device {self.device.device_id} via MQTT")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to device {self.device.device_id}: {e}")
            self.device.status = DeviceStatus.ERROR
            return False
    
    async def disconnect(self) -> None:
        """Disconnect from MQTT broker"""
        if self.mqtt_client:
            try:
                await self.mqtt_client.__aexit__(None, None, None)
                self._is_connected = False
                self.device.status = DeviceStatus.OFFLINE
                logger.info(f"Disconnected from device {self.device.device_id}")
            except Exception as e:
                logger.error(f"Error disconnecting from device {self.device.device_id}: {e}")
    
    async def send_command(self, command: DeviceCommand) -> Dict[str, Any]:
        """Send command to device via MQTT"""
        if not self._is_connected or not self.mqtt_client:
            raise ConnectionError(f"Device {self.device.device_id} is not connected")
        
        try:
            command_payload = {
                "command": command.command,
                "parameters": command.parameters,
                "timestamp": command.timestamp.isoformat()
            }
            
            await self.mqtt_client.publish(
                self._command_topic,
                json.dumps(command_payload)
            )
            
            logger.info(f"Sent command {command.command} to device {self.device.device_id}")
            
            # Wait for response (with timeout)
            response = await self._wait_for_response(timeout=10.0)
            return response
            
        except Exception as e:
            logger.error(f"Failed to send command to device {self.device.device_id}: {e}")
            raise
    
    async def get_status(self) -> DeviceState:
        """Get current device status"""
        # Request status update
        status_request = DeviceCommand(
            device_id=self.device.device_id,
            command="get_status",
            parameters={}
        )
        
        response = await self.send_command(status_request)
        
        return DeviceState(
            device_id=self.device.device_id,
            state_data=response
        )
    
    async def get_properties(self) -> Dict[str, Any]:
        """Get device properties"""
        # Request properties
        properties_request = DeviceCommand(
            device_id=self.device.device_id,
            command="get_properties",
            parameters={}
        )
        
        response = await self.send_command(properties_request)
        return response
    
    async def _wait_for_response(self, timeout: float = 10.0) -> Dict[str, Any]:
        """Wait for device response"""
        # This is a simplified implementation
        # In a real scenario, you'd listen for messages on the response topic
        await asyncio.sleep(0.1)  # Simulate response time
        return {"status": "success", "message": "Command executed"}


class HTTPDeviceInterface(DeviceInterface):
    """HTTP-based device interface"""
    
    def __init__(self, device: Device, base_url: str):
        super().__init__(device)
        self.base_url = base_url.rstrip('/')
        
    async def connect(self) -> bool:
        """Test connection to HTTP device"""
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/health") as response:
                    if response.status == 200:
                        self._is_connected = True
                        self.device.status = DeviceStatus.ONLINE
                        self.device.last_seen = datetime.now()
                        logger.info(f"Connected to device {self.device.device_id} via HTTP")
                        return True
                    else:
                        raise Exception(f"HTTP {response.status}")
                        
        except Exception as e:
            logger.error(f"Failed to connect to device {self.device.device_id}: {e}")
            self.device.status = DeviceStatus.ERROR
            return False
    
    async def disconnect(self) -> None:
        """Disconnect from HTTP device"""
        self._is_connected = False
        self.device.status = DeviceStatus.OFFLINE
        logger.info(f"Disconnected from device {self.device.device_id}")
    
    async def send_command(self, command: DeviceCommand) -> Dict[str, Any]:
        """Send command to device via HTTP"""
        if not self._is_connected:
            raise ConnectionError(f"Device {self.device.device_id} is not connected")
        
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                payload = {
                    "command": command.command,
                    "parameters": command.parameters
                }
                
                async with session.post(
                    f"{self.base_url}/commands",
                    json=payload
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"Sent command {command.command} to device {self.device.device_id}")
                        return result
                    else:
                        raise Exception(f"HTTP {response.status}")
                        
        except Exception as e:
            logger.error(f"Failed to send command to device {self.device.device_id}: {e}")
            raise
    
    async def get_status(self) -> DeviceState:
        """Get current device status via HTTP"""
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/status") as response:
                    if response.status == 200:
                        status_data = await response.json()
                        return DeviceState(
                            device_id=self.device.device_id,
                            state_data=status_data
                        )
                    else:
                        raise Exception(f"HTTP {response.status}")
                        
        except Exception as e:
            logger.error(f"Failed to get status from device {self.device.device_id}: {e}")
            raise
    
    async def get_properties(self) -> Dict[str, Any]:
        """Get device properties via HTTP"""
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/properties") as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        raise Exception(f"HTTP {response.status}")
                        
        except Exception as e:
            logger.error(f"Failed to get properties from device {self.device.device_id}: {e}")
            raise