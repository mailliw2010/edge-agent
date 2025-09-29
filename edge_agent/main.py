"""Main entry point for Edge Agent"""

import asyncio
import sys
from typing import Optional
import uvicorn

from .api.main import app
from .agents.edge_agent import EdgeAgent, DeviceManager
from .devices.models import AirConditionerDevice, ACMode, DeviceStatus
from .utils.policy_engine import PolicyEngine, create_energy_saving_rule, create_night_mode_rule
from .core.config import config
from .core.logger import logger


async def setup_demo_environment():
    """Set up a demo environment with sample devices and policies"""
    
    device_manager = DeviceManager()
    
    # Create sample air conditioners
    devices = [
        AirConditionerDevice(
            device_id="ac_living_room",
            name="Living Room AC",
            location="Living Room",
            current_temperature=26.5,
            target_temperature=24.0,
            mode=ACMode.COOL,
            fan_speed=3,
            power_on=True,
            energy_consumption=2.8
        ),
        AirConditionerDevice(
            device_id="ac_bedroom",
            name="Bedroom AC", 
            location="Bedroom",
            current_temperature=25.0,
            target_temperature=23.0,
            mode=ACMode.AUTO,
            fan_speed=2,
            power_on=True,
            energy_consumption=2.1
        ),
        AirConditionerDevice(
            device_id="ac_office",
            name="Office AC",
            location="Office",
            current_temperature=27.0,
            target_temperature=22.0,
            mode=ACMode.COOL,
            fan_speed=4,
            power_on=False,
            energy_consumption=0.0
        )
    ]
    
    # Add devices to manager
    for device in devices:
        device.status = DeviceStatus.ONLINE
        device_manager.add_device(device, interface_type="http", 
                                base_url=f"http://localhost:808{len(device_manager.devices)}")
    
    # Create Edge Agent
    edge_agent = EdgeAgent(device_manager)
    
    # Set up policy engine with sample rules
    policy_engine = PolicyEngine(device_manager)
    
    # Add energy saving rules
    for device in devices:
        energy_rule = create_energy_saving_rule(device.device_id)
        night_rule = create_night_mode_rule(device.device_id)
        policy_engine.add_rule(energy_rule)
        policy_engine.add_rule(night_rule)
    
    logger.info("Demo environment set up successfully")
    return device_manager, edge_agent, policy_engine


async def run_cli_demo():
    """Run a CLI demo of the Edge Agent"""
    print("🤖 Edge Agent CLI Demo")
    print("=" * 50)
    
    # Set up demo environment
    device_manager, edge_agent, policy_engine = await setup_demo_environment()
    
    print(f"✅ Initialized with {len(device_manager.devices)} devices")
    
    # Start policy monitoring in background
    asyncio.create_task(policy_engine.start_monitoring(interval=30))
    
    while True:
        try:
            print("\n" + "=" * 50)
            print("Available commands:")
            print("1. chat - Chat with the agent")
            print("2. status - Show system status")
            print("3. analyze - Analyze environment")
            print("4. optimize - Optimize AC systems")
            print("5. health - Show system health")
            print("6. quit - Exit")
            print("=" * 50)
            
            choice = input("\nEnter command: ").strip().lower()
            
            if choice in ['quit', 'exit', 'q']:
                break
            elif choice == 'chat' or choice == '1':
                message = input("💬 Enter your message: ")
                print("🤖 Agent response:")
                response = await edge_agent.process_message(message)
                print(response)
                
            elif choice == 'status' or choice == '2':
                print("📊 System Status:")
                devices = device_manager.list_devices()
                for device in devices:
                    if isinstance(device, AirConditionerDevice):
                        print(f"• {device.name} ({device.device_id})")
                        print(f"  Status: {device.status.value}")
                        print(f"  Power: {'ON' if device.power_on else 'OFF'}")
                        print(f"  Mode: {device.mode.value}")
                        print(f"  Current: {device.current_temperature}°C")
                        print(f"  Target: {device.target_temperature}°C")
                        print(f"  Energy: {device.energy_consumption} kWh")
                        print()
                        
            elif choice == 'analyze' or choice == '3':
                print("🔍 Environment Analysis:")
                analysis = await edge_agent.analyze_environment()
                print(f"Total Devices: {analysis['total_devices']}")
                print(f"Online: {analysis['online_devices']}")
                print(f"Active ACs: {analysis['active_air_conditioners']}")
                print(f"Energy Consumption: {analysis['total_energy_consumption']} kWh")
                if analysis['recommendations']:
                    print("Recommendations:")
                    for rec in analysis['recommendations']:
                        print(f"• {rec}")
                        
            elif choice == 'optimize' or choice == '4':
                print("⚡ Optimizing AC Systems...")
                optimization = await edge_agent.optimize_air_conditioning()
                print(f"Optimized Devices: {len(optimization['optimized_devices'])}")
                print(f"Estimated Savings: {optimization['energy_savings_estimate']} kWh")
                if optimization['actions_taken']:
                    print("Actions Taken:")
                    for action in optimization['actions_taken']:
                        print(f"• {action}")
                        
            elif choice == 'health' or choice == '5':
                print("🏥 System Health:")
                health = await edge_agent.get_system_health()
                print(f"System Status: {health['system_status'].upper()}")
                print(f"Uptime: {health['uptime_stats']['uptime_percentage']:.1f}%")
                if health['alerts']:
                    print("Alerts:")
                    for alert in health['alerts']:
                        print(f"⚠️  {alert}")
            else:
                print("❌ Invalid command")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Cleanup
    policy_engine.stop_monitoring()
    await device_manager.disconnect_all_devices()


def run_api_server():
    """Run the FastAPI server"""
    print("🚀 Starting Edge Agent API Server...")
    print(f"Server will be available at http://{config.api_host}:{config.api_port}")
    print("API Documentation at http://localhost:8000/docs")
    
    uvicorn.run(
        "edge_agent.api.main:app",
        host=config.api_host,
        port=config.api_port,
        reload=True,
        log_level=config.log_level.lower()
    )


async def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        if mode == "api":
            run_api_server()
        elif mode == "cli":
            await run_cli_demo()
        else:
            print("Usage: python -m edge_agent.main [api|cli]")
            sys.exit(1)
    else:
        # Default to CLI demo
        await run_cli_demo()


if __name__ == "__main__":
    asyncio.run(main())