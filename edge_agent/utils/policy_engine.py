"""Policy Engine for automated device control"""

from typing import Dict, Any, List, Optional
import asyncio
from datetime import datetime, time
from enum import Enum

from ..devices.models import PolicyRule, Device, AirConditionerDevice, ACMode
from ..core.logger import logger


class PolicyEngine:
    """Policy engine for automated device control"""
    
    def __init__(self, device_manager):
        self.device_manager = device_manager
        self.rules: Dict[str, PolicyRule] = {}
        self.is_running = False
        
    def add_rule(self, rule: PolicyRule):
        """Add a policy rule"""
        self.rules[rule.rule_id] = rule
        logger.info(f"Added policy rule: {rule.name}")
    
    def remove_rule(self, rule_id: str):
        """Remove a policy rule"""
        if rule_id in self.rules:
            del self.rules[rule_id]
            logger.info(f"Removed policy rule: {rule_id}")
    
    def get_rule(self, rule_id: str) -> Optional[PolicyRule]:
        """Get a specific rule"""
        return self.rules.get(rule_id)
    
    def list_rules(self) -> List[PolicyRule]:
        """List all rules"""
        return list(self.rules.values())
    
    async def evaluate_rules(self):
        """Evaluate all active rules"""
        for rule in self.rules.values():
            if not rule.enabled:
                continue
                
            try:
                if await self._evaluate_conditions(rule.conditions):
                    await self._execute_actions(rule.actions)
                    logger.info(f"Executed rule: {rule.name}")
                    
            except Exception as e:
                logger.error(f"Error evaluating rule {rule.name}: {e}")
    
    async def _evaluate_conditions(self, conditions: List[Dict[str, Any]]) -> bool:
        """Evaluate rule conditions"""
        for condition in conditions:
            condition_type = condition.get("type")
            
            if condition_type == "time_range":
                if not self._check_time_range(condition):
                    return False
                    
            elif condition_type == "temperature":
                if not await self._check_temperature_condition(condition):
                    return False
                    
            elif condition_type == "device_status":
                if not self._check_device_status(condition):
                    return False
                    
            elif condition_type == "energy_consumption":
                if not await self._check_energy_condition(condition):
                    return False
        
        return True
    
    def _check_time_range(self, condition: Dict[str, Any]) -> bool:
        """Check if current time is within specified range"""
        start_time = time.fromisoformat(condition["start_time"])
        end_time = time.fromisoformat(condition["end_time"])
        current_time = datetime.now().time()
        
        if start_time <= end_time:
            return start_time <= current_time <= end_time
        else:  # Crosses midnight
            return current_time >= start_time or current_time <= end_time
    
    async def _check_temperature_condition(self, condition: Dict[str, Any]) -> bool:
        """Check temperature condition"""
        device_id = condition.get("device_id")
        operator = condition.get("operator", ">=")
        threshold = condition.get("value")
        
        if not device_id or threshold is None:
            return False
        
        device = self.device_manager.get_device(device_id)
        if not isinstance(device, AirConditionerDevice):
            return False
        
        current_temp = device.current_temperature
        if current_temp is None:
            return False
        
        if operator == ">=":
            return current_temp >= threshold
        elif operator == "<=":
            return current_temp <= threshold
        elif operator == ">":
            return current_temp > threshold
        elif operator == "<":
            return current_temp < threshold
        elif operator == "==":
            return abs(current_temp - threshold) < 0.5
        
        return False
    
    def _check_device_status(self, condition: Dict[str, Any]) -> bool:
        """Check device status condition"""
        device_id = condition.get("device_id")
        expected_status = condition.get("status")
        
        if not device_id or not expected_status:
            return False
        
        device = self.device_manager.get_device(device_id)
        if not device:
            return False
        
        return device.status.value == expected_status
    
    async def _check_energy_condition(self, condition: Dict[str, Any]) -> bool:
        """Check energy consumption condition"""
        device_id = condition.get("device_id")
        operator = condition.get("operator", ">=")
        threshold = condition.get("value")
        
        if not device_id or threshold is None:
            return False
        
        device = self.device_manager.get_device(device_id)
        if not isinstance(device, AirConditionerDevice):
            return False
        
        energy = device.energy_consumption
        if energy is None:
            return False
        
        if operator == ">=":
            return energy >= threshold
        elif operator == "<=":
            return energy <= threshold
        elif operator == ">":
            return energy > threshold
        elif operator == "<":
            return energy < threshold
        
        return False
    
    async def _execute_actions(self, actions: List[Dict[str, Any]]):
        """Execute rule actions"""
        for action in actions:
            action_type = action.get("type")
            
            if action_type == "set_temperature":
                await self._set_temperature_action(action)
            elif action_type == "set_mode":
                await self._set_mode_action(action)
            elif action_type == "power_control":
                await self._power_control_action(action)
            elif action_type == "notification":
                await self._notification_action(action)
    
    async def _set_temperature_action(self, action: Dict[str, Any]):
        """Execute set temperature action"""
        device_id = action.get("device_id")
        temperature = action.get("temperature")
        
        if device_id and temperature:
            controller = self.device_manager.get_controller(device_id)
            if controller and hasattr(controller, 'set_temperature'):
                await controller.set_temperature(temperature)
                logger.info(f"Policy action: Set temperature to {temperature}°C for {device_id}")
    
    async def _set_mode_action(self, action: Dict[str, Any]):
        """Execute set mode action"""
        device_id = action.get("device_id")
        mode = action.get("mode")
        
        if device_id and mode:
            controller = self.device_manager.get_controller(device_id)
            if controller and hasattr(controller, 'set_mode'):
                ac_mode = ACMode(mode)
                await controller.set_mode(ac_mode)
                logger.info(f"Policy action: Set mode to {mode} for {device_id}")
    
    async def _power_control_action(self, action: Dict[str, Any]):
        """Execute power control action"""
        device_id = action.get("device_id")
        power_state = action.get("power_on")
        
        if device_id and power_state is not None:
            controller = self.device_manager.get_controller(device_id)
            if controller:
                if power_state:
                    await controller.power_on()
                    logger.info(f"Policy action: Powered on {device_id}")
                else:
                    await controller.power_off()
                    logger.info(f"Policy action: Powered off {device_id}")
    
    async def _notification_action(self, action: Dict[str, Any]):
        """Execute notification action"""
        message = action.get("message", "Policy rule triggered")
        logger.info(f"Policy notification: {message}")
    
    async def start_monitoring(self, interval: int = 60):
        """Start policy monitoring loop"""
        self.is_running = True
        logger.info(f"Started policy monitoring with {interval}s interval")
        
        while self.is_running:
            try:
                await self.evaluate_rules()
                await asyncio.sleep(interval)
            except Exception as e:
                logger.error(f"Error in policy monitoring loop: {e}")
                await asyncio.sleep(interval)
    
    def stop_monitoring(self):
        """Stop policy monitoring"""
        self.is_running = False
        logger.info("Stopped policy monitoring")


def create_energy_saving_rule(device_id: str) -> PolicyRule:
    """Create an energy-saving rule for high consumption periods"""
    return PolicyRule(
        rule_id=f"energy_saving_{device_id}",
        name=f"Energy Saving for {device_id}",
        description="Reduce energy consumption during peak hours",
        conditions=[
            {
                "type": "time_range",
                "start_time": "14:00:00",
                "end_time": "18:00:00"
            },
            {
                "type": "energy_consumption",
                "device_id": device_id,
                "operator": ">=",
                "value": 3.0
            }
        ],
        actions=[
            {
                "type": "set_temperature",
                "device_id": device_id,
                "temperature": 25.0
            },
            {
                "type": "notification",
                "message": f"Applied energy saving mode to {device_id}"
            }
        ],
        priority=1
    )


def create_night_mode_rule(device_id: str) -> PolicyRule:
    """Create a night mode rule for comfortable sleeping"""
    return PolicyRule(
        rule_id=f"night_mode_{device_id}",
        name=f"Night Mode for {device_id}",
        description="Optimize AC for sleeping hours",
        conditions=[
            {
                "type": "time_range",
                "start_time": "22:00:00",
                "end_time": "06:00:00"
            }
        ],
        actions=[
            {
                "type": "set_temperature",
                "device_id": device_id,
                "temperature": 24.0
            },
            {
                "type": "set_mode",
                "device_id": device_id,
                "mode": "auto"
            },
            {
                "type": "notification",
                "message": f"Applied night mode to {device_id}"
            }
        ],
        priority=2
    )