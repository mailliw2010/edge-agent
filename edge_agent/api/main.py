"""FastAPI application for Edge Agent"""

from typing import Dict, Any, List, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from ..agents.edge_agent import EdgeAgent, DeviceManager
from ..devices.models import AirConditionerDevice, DeviceStatus, ACMode
from ..core.config import config
from ..core.logger import logger


# API Models
class ChatMessage(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    response: str
    timestamp: datetime


class DeviceInfo(BaseModel):
    device_id: str
    name: str
    device_type: str
    location: str
    status: str


class SystemHealth(BaseModel):
    system_status: str
    total_devices: int
    online_devices: int
    uptime_percentage: float
    alerts: List[str]


# Global instances
device_manager = DeviceManager()
edge_agent = EdgeAgent(device_manager)
app = FastAPI(
    title="Edge Agent API",
    description="Intelligent AI Agent for edge device management",
    version="0.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize the application"""
    logger.info("Starting Edge Agent API...")
    
    # Add sample devices for demonstration
    ac1 = AirConditionerDevice(
        device_id="ac_001",
        name="Living Room AC",
        location="Living Room",
        current_temperature=25.0,
        target_temperature=22.0,
        mode=ACMode.COOL,
        fan_speed=3,
        power_on=True
    )
    
    ac2 = AirConditionerDevice(
        device_id="ac_002",
        name="Bedroom AC",
        location="Bedroom",
        current_temperature=24.0,
        target_temperature=23.0,
        mode=ACMode.AUTO,
        fan_speed=2,
        power_on=False
    )
    
    device_manager.add_device(ac1, interface_type="http", base_url="http://localhost:8081")
    device_manager.add_device(ac2, interface_type="http", base_url="http://localhost:8082")
    
    # Set devices as online for demo
    ac1.status = DeviceStatus.ONLINE
    ac2.status = DeviceStatus.ONLINE
    ac1.last_seen = datetime.now()
    ac2.last_seen = datetime.now()
    
    logger.info("Edge Agent API started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Edge Agent API...")
    await device_manager.disconnect_all_devices()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Edge Agent API",
        "version": "0.1.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return await edge_agent.get_system_health()


@app.get("/devices", response_model=List[DeviceInfo])
async def list_devices():
    """List all devices"""
    devices = device_manager.list_devices()
    return [
        DeviceInfo(
            device_id=device.device_id,
            name=device.name,
            device_type=device.device_type,
            location=device.location,
            status=device.status.value
        )
        for device in devices
    ]


@app.get("/devices/{device_id}")
async def get_device_status(device_id: str):
    """Get specific device status"""
    device = device_manager.get_device(device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    controller = device_manager.get_controller(device_id)
    if controller and hasattr(controller, 'get_status_summary'):
        return controller.get_status_summary()
    else:
        return {
            "device_id": device.device_id,
            "name": device.name,
            "type": device.device_type,
            "location": device.location,
            "status": device.status.value,
            "last_seen": device.last_seen.isoformat() if device.last_seen else None
        }


@app.post("/chat", response_model=ChatResponse)
async def chat_with_agent(message: ChatMessage):
    """Chat with the Edge Agent"""
    try:
        response = await edge_agent.process_message(message.message, message.context)
        return ChatResponse(
            response=response,
            timestamp=datetime.now()
        )
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze")
async def analyze_environment():
    """Analyze the current environment"""
    return await edge_agent.analyze_environment()


@app.post("/optimize")
async def optimize_system():
    """Optimize air conditioning system"""
    return await edge_agent.optimize_air_conditioning()


@app.post("/emergency-shutdown")
async def emergency_shutdown(reason: str = "Emergency"):
    """Emergency shutdown of all devices"""
    return await edge_agent.handle_emergency_shutdown(reason)


@app.get("/conversation-history")
async def get_conversation_history():
    """Get conversation history with the agent"""
    return edge_agent.get_conversation_history()


@app.delete("/conversation-history")
async def clear_conversation_history():
    """Clear conversation history"""
    edge_agent.clear_memory()
    return {"message": "Conversation history cleared"}


if __name__ == "__main__":
    uvicorn.run(
        "edge_agent.api.main:app",
        host=config.api_host,
        port=config.api_port,
        reload=True
    )