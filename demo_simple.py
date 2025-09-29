#!/usr/bin/env python3
"""
Simple demo of Edge Agent functionality without external dependencies
"""

import json
from datetime import datetime
from typing import Dict, Any, List
from enum import Enum


# Simplified models without pydantic for demo
class DeviceStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    ERROR = "error"


class ACMode(str, Enum):
    COOL = "cool"
    HEAT = "heat"
    AUTO = "auto"
    FAN = "fan"
    OFF = "off"


class SimpleAirConditioner:
    """Simplified air conditioner for demo"""
    
    def __init__(self, device_id: str, name: str, location: str):
        self.device_id = device_id
        self.name = name
        self.location = location
        self.status = DeviceStatus.ONLINE
        self.power_on = True
        self.mode = ACMode.COOL
        self.current_temperature = 26.0
        self.target_temperature = 24.0
        self.fan_speed = 3
        self.energy_consumption = 2.5
        self.last_seen = datetime.now()
    
    def set_temperature(self, temperature: float) -> Dict[str, Any]:
        if 16 <= temperature <= 30:
            self.target_temperature = temperature
            return {"status": "success", "message": f"Temperature set to {temperature}°C"}
        else:
            return {"status": "error", "message": "Temperature must be between 16°C and 30°C"}
    
    def set_mode(self, mode: ACMode) -> Dict[str, Any]:
        self.mode = mode
        if mode == ACMode.OFF:
            self.power_on = False
        else:
            self.power_on = True
        return {"status": "success", "message": f"Mode set to {mode.value}"}
    
    def power_off(self) -> Dict[str, Any]:
        self.power_on = False
        self.mode = ACMode.OFF
        return {"status": "success", "message": "Device powered off"}
    
    def power_on(self) -> Dict[str, Any]:
        self.power_on = True
        if self.mode == ACMode.OFF:
            self.mode = ACMode.AUTO
        return {"status": "success", "message": "Device powered on"}
    
    def get_status(self) -> Dict[str, Any]:
        return {
            "device_id": self.device_id,
            "name": self.name,
            "location": self.location,
            "status": self.status.value,
            "power_on": self.power_on,
            "mode": self.mode.value,
            "current_temperature": self.current_temperature,
            "target_temperature": self.target_temperature,
            "fan_speed": self.fan_speed,
            "energy_consumption": self.energy_consumption,
            "last_seen": self.last_seen.isoformat()
        }


class SimpleDeviceManager:
    """Simplified device manager for demo"""
    
    def __init__(self):
        self.devices: Dict[str, SimpleAirConditioner] = {}
    
    def add_device(self, device: SimpleAirConditioner):
        self.devices[device.device_id] = device
        print(f"✅ Added device: {device.name} ({device.device_id})")
    
    def get_device(self, device_id: str) -> SimpleAirConditioner:
        return self.devices.get(device_id)
    
    def list_devices(self) -> List[SimpleAirConditioner]:
        return list(self.devices.values())
    
    def control_device(self, device_id: str, action: str, **params) -> Dict[str, Any]:
        device = self.get_device(device_id)
        if not device:
            return {"status": "error", "message": f"Device {device_id} not found"}
        
        if action == "set_temperature":
            return device.set_temperature(params.get("temperature", 24.0))
        elif action == "set_mode":
            return device.set_mode(ACMode(params.get("mode", "auto")))
        elif action == "power_on":
            return device.power_on()
        elif action == "power_off":
            return device.power_off()
        else:
            return {"status": "error", "message": f"Unknown action: {action}"}


class SimpleEdgeAgent:
    """Simplified Edge Agent for demo"""
    
    def __init__(self, device_manager: SimpleDeviceManager):
        self.device_manager = device_manager
        self.conversation_history = []
    
    def process_message(self, message: str) -> str:
        """Process user message and return response"""
        message_lower = message.lower()
        
        # Simple rule-based responses
        if "list" in message_lower and "device" in message_lower:
            devices = self.device_manager.list_devices()
            device_list = []
            for device in devices:
                device_list.append(f"{device.name} ({device.device_id}) in {device.location}")
            return f"Available devices:\n" + "\n".join([f"• {d}" for d in device_list])
        
        elif "status" in message_lower:
            devices = self.device_manager.list_devices()
            status_info = []
            for device in devices:
                status = device.get_status()
                status_info.append(
                    f"{device.name}: {status['current_temperature']}°C → {status['target_temperature']}°C, "
                    f"Mode: {status['mode']}, Power: {'ON' if status['power_on'] else 'OFF'}"
                )
            return "Device Status:\n" + "\n".join([f"• {s}" for s in status_info])
        
        elif "temperature" in message_lower and "set" in message_lower:
            # Extract temperature and device
            import re
            temp_match = re.search(r'(\d+(?:\.\d+)?)', message)
            if temp_match:
                temperature = float(temp_match.group(1))
                devices = self.device_manager.list_devices()
                if devices:
                    device = devices[0]  # Use first device for demo
                    result = device.set_temperature(temperature)
                    return f"Set {device.name} temperature to {temperature}°C. {result['message']}"
            return "Please specify a temperature (e.g., 'set temperature to 24 degrees')"
        
        elif "turn off" in message_lower or "power off" in message_lower:
            devices = self.device_manager.list_devices()
            results = []
            for device in devices:
                result = device.power_off()
                results.append(f"{device.name}: {result['message']}")
            return "Turned off devices:\n" + "\n".join([f"• {r}" for r in results])
        
        elif "turn on" in message_lower or "power on" in message_lower:
            devices = self.device_manager.list_devices()
            results = []
            for device in devices:
                result = device.power_on()
                results.append(f"{device.name}: {result['message']}")
            return "Turned on devices:\n" + "\n".join([f"• {r}" for r in results])
        
        elif "cool" in message_lower or "cooling" in message_lower:
            devices = self.device_manager.list_devices()
            results = []
            for device in devices:
                result = device.set_mode(ACMode.COOL)
                results.append(f"{device.name}: {result['message']}")
            return "Set devices to cooling mode:\n" + "\n".join([f"• {r}" for r in results])
        
        elif "energy" in message_lower or "consumption" in message_lower:
            devices = self.device_manager.list_devices()
            total_energy = sum(device.energy_consumption for device in devices)
            energy_info = []
            for device in devices:
                energy_info.append(f"{device.name}: {device.energy_consumption} kWh")
            
            response = f"Energy Consumption:\n" + "\n".join([f"• {e}" for e in energy_info])
            response += f"\nTotal: {total_energy} kWh"
            
            if total_energy > 5.0:
                response += "\n\n💡 Recommendation: Consider raising temperature by 1-2°C to save energy"
            
            return response
        
        elif "optimize" in message_lower:
            devices = self.device_manager.list_devices()
            optimizations = []
            for device in devices:
                if device.target_temperature < 22:
                    device.set_temperature(24.0)
                    optimizations.append(f"{device.name}: Raised temperature to 24°C for efficiency")
                if device.fan_speed > 3:
                    device.fan_speed = 3
                    optimizations.append(f"{device.name}: Reduced fan speed to level 3")
            
            if optimizations:
                return "Optimization applied:\n" + "\n".join([f"• {o}" for o in optimizations])
            else:
                return "All devices are already optimized for energy efficiency."
        
        else:
            return (
                f"I understand you said: '{message}'\n\n"
                "I can help you with:\n"
                "• List devices\n"
                "• Check device status\n"
                "• Set temperature (e.g., 'set temperature to 24')\n"
                "• Turn devices on/off\n"
                "• Set cooling mode\n"
                "• Check energy consumption\n"
                "• Optimize system\n"
                "\nTry asking something like 'show device status' or 'set temperature to 22 degrees'"
            )


def main():
    """Run the simple demo"""
    print("🤖 Edge Agent Simple Demo")
    print("=" * 50)
    print("This demo shows the core functionality without external dependencies")
    print()
    
    # Create device manager
    device_manager = SimpleDeviceManager()
    
    # Create sample devices
    devices = [
        SimpleAirConditioner("ac_living_room", "Living Room AC", "Living Room"),
        SimpleAirConditioner("ac_bedroom", "Bedroom AC", "Bedroom"),
        SimpleAirConditioner("ac_office", "Office AC", "Office")
    ]
    
    # Add devices
    for device in devices:
        device_manager.add_device(device)
    
    # Create agent
    agent = SimpleEdgeAgent(device_manager)
    
    print(f"\n✅ Initialized with {len(devices)} devices")
    print()
    
    # Demo interactions
    demo_messages = [
        "List all devices",
        "Show device status", 
        "Set temperature to 22 degrees",
        "Check energy consumption",
        "Optimize the system",
        "Turn off all devices"
    ]
    
    print("🎬 Demo Interactions:")
    print("=" * 30)
    
    for i, message in enumerate(demo_messages, 1):
        print(f"\n{i}. 👤 User: {message}")
        response = agent.process_message(message)
        print(f"🤖 Agent: {response}")
        print("-" * 30)
    
    print("\n✅ Demo completed!")
    print("\nTo use the full system with LangChain and OpenAI:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Set OPENAI_API_KEY in .env file")
    print("3. Run: python -m edge_agent.main cli")


if __name__ == "__main__":
    main()