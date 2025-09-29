# api/models.py
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class AgentRequest(BaseModel):
    """
    API 请求体模型
    """
    query: str
    session_id: Optional[str] = None # 可选的会话ID，用于支持多轮对话

class AgentResponse(BaseModel):
    """
    API 响应体模型
    """
    output: str
    intermediate_steps: Optional[List[Dict[str, Any]]] = None
