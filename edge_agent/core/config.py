"""Configuration management for Edge Agent"""

import os
from typing import Optional
from pydantic import BaseSettings, Field


class EdgeAgentConfig(BaseSettings):
    """Configuration settings for Edge Agent"""
    
    # OpenAI Configuration
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    
    # Agent Configuration
    agent_name: str = Field("EdgeAgent", env="AGENT_NAME")
    agent_description: str = Field(
        "Intelligent AI Agent for edge device management", 
        env="AGENT_DESCRIPTION"
    )
    
    # MQTT Configuration
    mqtt_broker_host: str = Field("localhost", env="MQTT_BROKER_HOST")
    mqtt_broker_port: int = Field(1883, env="MQTT_BROKER_PORT")
    mqtt_username: Optional[str] = Field(None, env="MQTT_USERNAME")
    mqtt_password: Optional[str] = Field(None, env="MQTT_PASSWORD")
    
    # Redis Configuration
    redis_host: str = Field("localhost", env="REDIS_HOST")
    redis_port: int = Field(6379, env="REDIS_PORT")
    redis_password: Optional[str] = Field(None, env="REDIS_PASSWORD")
    
    # Database Configuration
    database_url: str = Field("sqlite:///./edge_agent.db", env="DATABASE_URL")
    
    # API Configuration
    api_host: str = Field("0.0.0.0", env="API_HOST")
    api_port: int = Field(8000, env="API_PORT")
    
    # Logging Configuration
    log_level: str = Field("INFO", env="LOG_LEVEL")
    log_file: str = Field("logs/edge_agent.log", env="LOG_FILE")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global configuration instance
config = EdgeAgentConfig()