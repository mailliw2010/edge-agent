"""Device models and data structures"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


class DeviceType(str, Enum):
    """Supported device types"""
    AIR_CONDITIONER = "air_conditioner"
    THERMOSTAT = "thermostat"
    SENSOR = "sensor"
    ACTUATOR = "actuator"


class DeviceStatus(str, Enum):
    """Device status enumeration"""
    ONLINE = "online"
    OFFLINE = "offline"
    ERROR = "error"
    MAINTENANCE = "maintenance"


class ACMode(str, Enum):
    """Air conditioner operating modes"""
    COOL = "cool"
    HEAT = "heat"
    AUTO = "auto"
    FAN = "fan"
    DRY = "dry"
    OFF = "off"


class Device(BaseModel):
    """Base device model"""
    device_id: str = Field(..., description="Unique device identifier")
    device_type: DeviceType = Field(..., description="Type of the device")
    name: str = Field(..., description="Human-readable device name")
    location: str = Field(..., description="Device location")
    status: DeviceStatus = Field(DeviceStatus.OFFLINE, description="Current device status")
    last_seen: Optional[datetime] = Field(None, description="Last communication timestamp")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Device-specific properties")
    
    class Config:
        use_enum_values = True


class AirConditionerDevice(Device):
    """Air conditioner device model"""
    device_type: DeviceType = Field(DeviceType.AIR_CONDITIONER, const=True)
    current_temperature: Optional[float] = Field(None, description="Current temperature reading")
    target_temperature: Optional[float] = Field(None, description="Target temperature setting")
    mode: ACMode = Field(ACMode.OFF, description="Current operating mode")
    fan_speed: Optional[int] = Field(None, ge=0, le=5, description="Fan speed level (0-5)")
    power_on: bool = Field(False, description="Power state")
    energy_consumption: Optional[float] = Field(None, description="Current energy consumption (kWh)")
    
    
class SensorDevice(Device):
    """Sensor device model"""
    device_type: DeviceType = Field(DeviceType.SENSOR, const=True)
    sensor_type: str = Field(..., description="Type of sensor (temperature, humidity, etc.)")
    current_value: Optional[float] = Field(None, description="Current sensor reading")
    unit: str = Field(..., description="Measurement unit")
    min_value: Optional[float] = Field(None, description="Minimum measurable value")
    max_value: Optional[float] = Field(None, description="Maximum measurable value")


class DeviceCommand(BaseModel):
    """Device command model"""
    device_id: str = Field(..., description="Target device ID")
    command: str = Field(..., description="Command to execute")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Command parameters")
    timestamp: datetime = Field(default_factory=datetime.now, description="Command timestamp")


class DeviceState(BaseModel):
    """Device state snapshot"""
    device_id: str = Field(..., description="Device identifier")
    timestamp: datetime = Field(default_factory=datetime.now, description="State timestamp")
    state_data: Dict[str, Any] = Field(..., description="Complete device state")
    
    
class PolicyRule(BaseModel):
    """Policy rule for device automation"""
    rule_id: str = Field(..., description="Unique rule identifier")
    name: str = Field(..., description="Rule name")
    description: str = Field(..., description="Rule description")
    conditions: List[Dict[str, Any]] = Field(..., description="Rule conditions")
    actions: List[Dict[str, Any]] = Field(..., description="Actions to execute")
    enabled: bool = Field(True, description="Whether the rule is active")
    priority: int = Field(0, description="Rule priority (higher number = higher priority)")
    created_at: datetime = Field(default_factory=datetime.now, description="Rule creation time")