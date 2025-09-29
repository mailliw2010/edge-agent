# api/server.py
import sys
import os
from fastapi import FastAPI
from api.models import AgentRequest, AgentResponse

# 将项目根目录添加到 sys.path，以确保可以正确导入 agent 和 tools
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config.settings # 确保环境变量被加载
from agents.building_env_agent import BuildingEnvAgent
from tools.sensor_reader import sensor_reader
from tools.ac_control import ac_control
from tools.light_control import light_control

# --- 全局 Agent 实例 ---
# 在生产环境中，我们希望 Agent 是一个单例，在服务启动时初始化一次即可。
# 这样可以避免每次 API 调用都重新加载模型和工具，从而提高响应速度。

def get_agent_instance():
    """
    初始化并返回一个 Agent 单例。
    """
    tools = [sensor_reader, ac_control, light_control]
    agent = BuildingEnvAgent(tools=tools)
    print("🚀 LangChain Agent 'BuildingEnvAgent' 已在 API 服务中初始化。")
    return agent

# --- FastAPI 应用 ---

app = FastAPI(
    title="Edge AI Agent API",
    description="用于与边缘计算环境交互的 AI Agent 服务。",
    version="1.0.0",
)

# 在应用启动时加载 Agent
@app.on_event("startup")
def startup_event():
    app.state.agent = get_agent_instance()
    print("✅ API 服务已启动，Agent 准备就绪。")

@app.post("/api/v1/agent/invoke", response_model=AgentResponse)
async def invoke_agent(request: AgentRequest):
    """
    调用 AI Agent 来处理用户指令。

    - **接收**: 一个包含 `query` (用户指令) 和可选 `session_id` 的 JSON 对象。
    - **处理**:
        1. 获取当前环境状态。
        2. 调用 Agent 的 `run` 方法，传入用户指令和环境状态。
    - **返回**: 一个包含 `output` (Agent 的最终答复) 的 JSON 对象。
    """
    print(f"📥 [API] 收到请求: {request.query}")

    # 1. 感知环境
    # 在调用 Agent 之前，先获取最新的环境快照。
    environment_status = sensor_reader({"device_id": "all"})

    # 2. 调用 Agent
    # 从 app.state 中获取已初始化的 Agent 实例
    agent = app.state.agent
    result = agent.run(request.query, environment_status)

    print(f"📤 [API] 发送响应: {result['output']}")

    # 3. 构造并返回响应
    return AgentResponse(
        output=result["output"],
        intermediate_steps=result.get("intermediate_steps")
    )

@app.get("/")
def read_root():
    return {"message": "欢迎使用 Edge AI Agent API。请访问 /docs 查看 API 文档。"}

# --- 如何运行 ---
#
# 1. 安装依赖:
#    pip install fastapi "uvicorn[standard]"
#
# 2. 启动服务 (用于本地开发):
#    uvicorn api.server:app --reload --port 8001
#
# 3. 启动服务 (用于生产环境，允许外部访问):
#    uvicorn api.server:app --host 0.0.0.0 --port 8001
#
# 4. 访问 API 文档:
#    在浏览器中打开 http://127.0.0.1:8001/docs (本地) 或 http://<your_server_ip>:8001/docs (生产)
#
