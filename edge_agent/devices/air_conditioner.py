"""Air conditioner device implementation"""

from typing import Dict, Any, Optional
from datetime import datetime

from .models import AirConditionerDevice, DeviceCommand, ACMode, DeviceStatus
from .base import DeviceInterface
from ..core.logger import logger


class AirConditionerController:
    """Air conditioner device controller with intelligent operations"""
    
    def __init__(self, device: AirConditionerDevice, interface: DeviceInterface):
        self.device = device
        self.interface = interface
        
    async def power_on(self) -> Dict[str, Any]:
        """Turn on the air conditioner"""
        command = DeviceCommand(
            device_id=self.device.device_id,
            command="power_on",
            parameters={}
        )
        
        result = await self.interface.send_command(command)
        if result.get("status") == "success":
            self.device.power_on = True
            self.device.status = DeviceStatus.ONLINE
            logger.info(f"Air conditioner {self.device.device_id} powered on")
        
        return result
    
    async def power_off(self) -> Dict[str, Any]:
        """Turn off the air conditioner"""
        command = DeviceCommand(
            device_id=self.device.device_id,
            command="power_off",
            parameters={}
        )
        
        result = await self.interface.send_command(command)
        if result.get("status") == "success":
            self.device.power_on = False
            self.device.mode = ACMode.OFF
            logger.info(f"Air conditioner {self.device.device_id} powered off")
        
        return result
    
    async def set_temperature(self, temperature: float) -> Dict[str, Any]:
        """Set target temperature"""
        if not (16 <= temperature <= 30):
            raise ValueError("Temperature must be between 16°C and 30°C")
        
        command = DeviceCommand(
            device_id=self.device.device_id,
            command="set_temperature",
            parameters={"temperature": temperature}
        )
        
        result = await self.interface.send_command(command)
        if result.get("status") == "success":
            self.device.target_temperature = temperature
            logger.info(f"Set temperature to {temperature}°C for AC {self.device.device_id}")
        
        return result
    
    async def set_mode(self, mode: ACMode) -> Dict[str, Any]:
        """Set operating mode"""
        command = DeviceCommand(
            device_id=self.device.device_id,
            command="set_mode",
            parameters={"mode": mode.value}
        )
        
        result = await self.interface.send_command(command)
        if result.get("status") == "success":
            self.device.mode = mode
            if mode == ACMode.OFF:
                self.device.power_on = False
            else:
                self.device.power_on = True
            logger.info(f"Set mode to {mode.value} for AC {self.device.device_id}")
        
        return result
    
    async def set_fan_speed(self, speed: int) -> Dict[str, Any]:
        """Set fan speed (0-5)"""
        if not (0 <= speed <= 5):
            raise ValueError("Fan speed must be between 0 and 5")
        
        command = DeviceCommand(
            device_id=self.device.device_id,
            command="set_fan_speed",
            parameters={"speed": speed}
        )
        
        result = await self.interface.send_command(command)
        if result.get("status") == "success":
            self.device.fan_speed = speed
            logger.info(f"Set fan speed to {speed} for AC {self.device.device_id}")
        
        return result
    
    async def get_current_temperature(self) -> Optional[float]:
        """Get current temperature reading"""
        try:
            state = await self.interface.get_status()
            current_temp = state.state_data.get("current_temperature")
            if current_temp is not None:
                self.device.current_temperature = float(current_temp)
            return self.device.current_temperature
        except Exception as e:
            logger.error(f"Failed to get current temperature for AC {self.device.device_id}: {e}")
            return None
    
    async def get_energy_consumption(self) -> Optional[float]:
        """Get current energy consumption"""
        try:
            state = await self.interface.get_status()
            energy = state.state_data.get("energy_consumption")
            if energy is not None:
                self.device.energy_consumption = float(energy)
            return self.device.energy_consumption
        except Exception as e:
            logger.error(f"Failed to get energy consumption for AC {self.device.device_id}: {e}")
            return None
    
    async def intelligent_cooling(self, target_temp: float, room_temp: float) -> Dict[str, Any]:
        """Intelligent cooling algorithm based on temperature difference"""
        temp_diff = room_temp - target_temp
        
        if temp_diff <= 0:
            # Target reached or room is cooler
            return await self.set_mode(ACMode.OFF)
        
        # Determine optimal settings based on temperature difference
        if temp_diff > 5:
            # Significant cooling needed
            await self.set_mode(ACMode.COOL)
            await self.set_fan_speed(5)  # Maximum fan speed
        elif temp_diff > 2:
            # Moderate cooling needed
            await self.set_mode(ACMode.COOL)
            await self.set_fan_speed(3)  # Medium fan speed
        else:
            # Minor cooling needed
            await self.set_mode(ACMode.COOL)
            await self.set_fan_speed(1)  # Low fan speed
        
        # Set target temperature
        result = await self.set_temperature(target_temp)
        
        logger.info(f"Applied intelligent cooling for AC {self.device.device_id}: "
                   f"room={room_temp}°C, target={target_temp}°C, diff={temp_diff}°C")
        
        return result
    
    async def energy_efficient_mode(self) -> Dict[str, Any]:
        """Enable energy-efficient operation"""
        # Set moderate temperature and fan speed for efficiency
        await self.set_temperature(24.0)  # Balanced temperature
        await self.set_fan_speed(2)       # Medium-low fan speed
        result = await self.set_mode(ACMode.AUTO)  # Auto mode for optimization
        
        logger.info(f"Enabled energy-efficient mode for AC {self.device.device_id}")
        return result
    
    async def schedule_operation(self, start_time: datetime, end_time: datetime, 
                               temperature: float, mode: ACMode) -> Dict[str, Any]:
        """Schedule AC operation (simplified implementation)"""
        # In a real implementation, this would integrate with a scheduler
        schedule_data = {
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "temperature": temperature,
            "mode": mode.value
        }
        
        command = DeviceCommand(
            device_id=self.device.device_id,
            command="schedule_operation",
            parameters=schedule_data
        )
        
        result = await self.interface.send_command(command)
        logger.info(f"Scheduled operation for AC {self.device.device_id}: {schedule_data}")
        
        return result
    
    def get_status_summary(self) -> Dict[str, Any]:
        """Get comprehensive status summary"""
        return {
            "device_id": self.device.device_id,
            "name": self.device.name,
            "location": self.device.location,
            "status": self.device.status.value,
            "power_on": self.device.power_on,
            "mode": self.device.mode.value,
            "current_temperature": self.device.current_temperature,
            "target_temperature": self.device.target_temperature,
            "fan_speed": self.device.fan_speed,
            "energy_consumption": self.device.energy_consumption,
            "last_seen": self.device.last_seen.isoformat() if self.device.last_seen else None
        }