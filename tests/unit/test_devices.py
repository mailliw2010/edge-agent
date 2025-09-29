"""Unit tests for device models and controllers"""

import pytest
from datetime import datetime

from edge_agent.devices.models import (
    AirConditionerDevice, ACMode, DeviceStatus, DeviceCommand
)
from edge_agent.devices.air_conditioner import AirConditionerController
from edge_agent.devices.base import HTTPDeviceInterface


class TestAirConditionerDevice:
    """Test air conditioner device model"""
    
    def test_create_device(self):
        """Test creating an air conditioner device"""
        device = AirConditionerDevice(
            device_id="test_ac",
            name="Test AC",
            location="Test Room",
            current_temperature=25.0,
            target_temperature=22.0,
            mode=ACMode.COOL,
            fan_speed=3,
            power_on=True
        )
        
        assert device.device_id == "test_ac"
        assert device.name == "Test AC"
        assert device.current_temperature == 25.0
        assert device.target_temperature == 22.0
        assert device.mode == ACMode.COOL
        assert device.fan_speed == 3
        assert device.power_on is True
        assert device.status == DeviceStatus.OFFLINE  # Default status
    
    def test_device_validation(self):
        """Test device validation"""
        with pytest.raises(ValueError):
            # Invalid fan speed
            AirConditionerDevice(
                device_id="test",
                name="Test",
                location="Test",
                fan_speed=10  # Invalid: should be 0-5
            )


class TestDeviceCommand:
    """Test device command model"""
    
    def test_create_command(self):
        """Test creating a device command"""
        command = DeviceCommand(
            device_id="test_device",
            command="set_temperature",
            parameters={"temperature": 24.0}
        )
        
        assert command.device_id == "test_device"
        assert command.command == "set_temperature"
        assert command.parameters["temperature"] == 24.0
        assert isinstance(command.timestamp, datetime)


class MockDeviceInterface:
    """Mock device interface for testing"""
    
    def __init__(self, device):
        self.device = device
        self._is_connected = True
    
    async def connect(self):
        return True
    
    async def disconnect(self):
        pass
    
    async def send_command(self, command):
        return {"status": "success", "message": "Command executed"}
    
    async def get_status(self):
        from edge_agent.devices.models import DeviceState
        return DeviceState(
            device_id=self.device.device_id,
            state_data={"temperature": 24.0}
        )
    
    @property
    def is_connected(self):
        return self._is_connected


class TestAirConditionerController:
    """Test air conditioner controller"""
    
    @pytest.fixture
    def ac_device(self):
        """Create a test AC device"""
        return AirConditionerDevice(
            device_id="test_ac",
            name="Test AC",
            location="Test Room",
            current_temperature=25.0,
            target_temperature=22.0,
            mode=ACMode.COOL,
            fan_speed=3,
            power_on=True
        )
    
    @pytest.fixture
    def controller(self, ac_device):
        """Create a test controller"""
        interface = MockDeviceInterface(ac_device)
        return AirConditionerController(ac_device, interface)
    
    @pytest.mark.asyncio
    async def test_power_on(self, controller):
        """Test power on command"""
        result = await controller.power_on()
        assert result["status"] == "success"
        assert controller.device.power_on is True
    
    @pytest.mark.asyncio
    async def test_power_off(self, controller):
        """Test power off command"""
        result = await controller.power_off()
        assert result["status"] == "success"
        assert controller.device.power_on is False
        assert controller.device.mode == ACMode.OFF
    
    @pytest.mark.asyncio
    async def test_set_temperature(self, controller):
        """Test set temperature command"""
        result = await controller.set_temperature(24.0)
        assert result["status"] == "success"
        assert controller.device.target_temperature == 24.0
    
    @pytest.mark.asyncio
    async def test_set_temperature_validation(self, controller):
        """Test temperature validation"""
        with pytest.raises(ValueError):
            await controller.set_temperature(10.0)  # Too low
        
        with pytest.raises(ValueError):
            await controller.set_temperature(35.0)  # Too high
    
    @pytest.mark.asyncio
    async def test_set_mode(self, controller):
        """Test set mode command"""
        result = await controller.set_mode(ACMode.AUTO)
        assert result["status"] == "success"
        assert controller.device.mode == ACMode.AUTO
    
    @pytest.mark.asyncio
    async def test_intelligent_cooling(self, controller):
        """Test intelligent cooling algorithm"""
        # Test large temperature difference
        result = await controller.intelligent_cooling(22.0, 28.0)  # 6°C difference
        assert result["status"] == "success"
        assert controller.device.target_temperature == 22.0
        
        # Test small temperature difference
        result = await controller.intelligent_cooling(24.0, 25.0)  # 1°C difference
        assert result["status"] == "success"
    
    def test_get_status_summary(self, controller):
        """Test status summary"""
        summary = controller.get_status_summary()
        assert summary["device_id"] == "test_ac"
        assert summary["name"] == "Test AC"
        assert "power_on" in summary
        assert "mode" in summary
        assert "current_temperature" in summary