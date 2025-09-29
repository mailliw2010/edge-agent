#!/usr/bin/env python3
"""
Policy Engine usage example
"""

import asyncio
import os
import sys
from datetime import datetime

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from edge_agent.agents.edge_agent import DeviceManager
from edge_agent.devices.models import AirConditionerDevice, ACMode, DeviceStatus, PolicyRule
from edge_agent.utils.policy_engine import PolicyEngine, create_energy_saving_rule, create_night_mode_rule


async def main():
    """Policy engine demonstration"""
    print("⚙️  Policy Engine Example")
    print("=" * 40)
    
    # Create device manager
    device_manager = DeviceManager()
    
    # Create sample devices
    devices = [
        AirConditionerDevice(
            device_id="ac_bedroom",
            name="Bedroom AC",
            location="Bedroom",
            current_temperature=26.0,
            target_temperature=20.0,  # Very low temperature
            mode=ACMode.COOL,
            fan_speed=5,
            power_on=True,
            energy_consumption=4.2  # High consumption
        ),
        AirConditionerDevice(
            device_id="ac_living_room",
            name="Living Room AC",
            location="Living Room",
            current_temperature=24.0,
            target_temperature=23.0,
            mode=ACMode.AUTO,
            fan_speed=2,
            power_on=True,
            energy_consumption=1.8
        )
    ]
    
    # Add devices
    for device in devices:
        device.status = DeviceStatus.ONLINE
        device.last_seen = datetime.now()
        device_manager.add_device(device, interface_type="http")
    
    print(f"✅ Created {len(devices)} devices")
    
    # Create policy engine
    policy_engine = PolicyEngine(device_manager)
    
    # Add energy saving rules
    for device in devices:
        energy_rule = create_energy_saving_rule(device.device_id)
        night_rule = create_night_mode_rule(device.device_id)
        policy_engine.add_rule(energy_rule)
        policy_engine.add_rule(night_rule)
    
    # Create custom rule for temperature optimization
    temp_optimization_rule = PolicyRule(
        rule_id="temp_optimization",
        name="Temperature Optimization",
        description="Optimize temperature settings for efficiency",
        conditions=[
            {
                "type": "temperature",
                "device_id": "ac_bedroom",
                "operator": "<=",
                "value": 21.0  # Target too low
            }
        ],
        actions=[
            {
                "type": "set_temperature",
                "device_id": "ac_bedroom",
                "temperature": 24.0
            },
            {
                "type": "notification",
                "message": "Optimized bedroom AC temperature for efficiency"
            }
        ],
        priority=3
    )
    
    policy_engine.add_rule(temp_optimization_rule)
    
    print(f"✅ Created {len(policy_engine.rules)} policy rules")
    
    # List all rules
    print("\n📜 Policy Rules:")
    for rule in policy_engine.list_rules():
        print(f"• {rule.name}: {rule.description}")
    
    # Evaluate rules once
    print("\n🔍 Evaluating policy rules...")
    await policy_engine.evaluate_rules()
    
    # Show device states after policy evaluation
    print("\n📊 Device states after policy evaluation:")
    for device in device_manager.devices.values():
        if isinstance(device, AirConditionerDevice):
            print(f"• {device.name}:")
            print(f"  Temperature: {device.current_temperature}°C → {device.target_temperature}°C")
            print(f"  Mode: {device.mode.value}")
            print(f"  Power: {'ON' if device.power_on else 'OFF'}")
            print(f"  Energy: {device.energy_consumption} kWh")
    
    print("\n✅ Policy example completed!")


if __name__ == "__main__":
    asyncio.run(main())