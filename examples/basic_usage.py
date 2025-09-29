#!/usr/bin/env python3
"""
Basic usage example for Edge Agent
"""

import asyncio
import os
import sys

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from edge_agent.agents.edge_agent import EdgeAgent, DeviceManager
from edge_agent.devices.models import AirConditionerDevice, ACMode, DeviceStatus
from edge_agent.devices.air_conditioner import AirConditionerController
from edge_agent.devices.base import HTTPDeviceInterface


async def main():
    """Basic usage demonstration"""
    print("🤖 Edge Agent Basic Usage Example")
    print("=" * 40)
    
    # Create device manager
    device_manager = DeviceManager()
    
    # Create an air conditioner device
    ac_device = AirConditionerDevice(
        device_id="demo_ac_001",
        name="Demo Living Room AC",
        location="Living Room",
        current_temperature=25.5,
        target_temperature=22.0,
        mode=ACMode.COOL,
        fan_speed=3,
        power_on=True,
        energy_consumption=2.5
    )
    ac_device.status = DeviceStatus.ONLINE
    
    # Add device to manager
    device_manager.add_device(ac_device, interface_type="http", base_url="http://localhost:8080")
    
    # Create Edge Agent
    agent = EdgeAgent(device_manager)
    
    print(f"✅ Created agent with {len(device_manager.devices)} device(s)")
    print()
    
    # Example interactions
    interactions = [
        "What devices are available?",
        "What's the status of the living room AC?",
        "Set the living room AC temperature to 24 degrees",
        "Turn off the living room AC",
        "Analyze the current environment",
        "What are some energy saving recommendations?"
    ]
    
    for interaction in interactions:
        print(f"👤 User: {interaction}")
        response = await agent.process_message(interaction)
        print(f"🤖 Agent: {response}")
        print("-" * 40)
        await asyncio.sleep(1)  # Small delay for demo
    
    # Show system analysis
    print("\n📊 System Analysis:")
    analysis = await agent.analyze_environment()
    print(f"Total devices: {analysis['total_devices']}")
    print(f"Online devices: {analysis['online_devices']}")
    print(f"Active ACs: {analysis['active_air_conditioners']}")
    print(f"Total energy consumption: {analysis['total_energy_consumption']} kWh")
    
    if analysis['recommendations']:
        print("\nRecommendations:")
        for rec in analysis['recommendations']:
            print(f"• {rec}")
    
    print("\n✅ Demo completed!")


if __name__ == "__main__":
    asyncio.run(main())