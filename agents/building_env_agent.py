# agents/building_env_agent.py
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_models import ChatTongyi # 导入通义千问模型
from langchain.agents import AgentExecutor, create_openai_tools_agent
from typing import List, Any, Dict

# --- Agent 核心组件初始化 ---

# 1. 定义系统提示 (System Prompt) - 已优化为中文
# 这是 Agent 的“性格”和“指令手册”。它告诉 LLM 它的角色、目标、可用工具以及如何响应。
# 针对中文环境和 Qwen 模型进行了优化。
prompt_template = """
你是一个名为“智能楼宇管家”的AI Agent。
你的核心任务是：根据用户的指令和环境的实时状态，自主地维护一个舒适、节能的建筑环境。

# 可用工具
你掌握以下工具，并清楚它们的用途：
- `sensor_reader`: 用于感知环境，可以读取温度、灯光状态等所有设备的实时数据。
- `ac_control`: 用于控制空调，可以开启、关闭或设定温度。
- `light_control`: 用于控制灯光，可以开启或关闭。

# 决策流程
你必须严格遵循以下思考和行动的流程：
1.  **感知环境**: 在做任何决策之前，必须先调用 `sensor_reader` 工具来全面了解当前的环境状态。
2.  **分析思考**: 结合你刚刚感知到的环境状态和用户的最新指令，分析并判断是否需要采取行动。
3.  **执行动作**: 如果需要行动，选择最合适的工具并调用它来完成任务。如果不需要，就明确地说明情况。

# 当前环境状态
{environment_status}

# 用户最新指令
{input}

# 思考与行动历史
{agent_scratchpad}
"""

# 2. 创建聊天提示模板
prompt = ChatPromptTemplate.from_template(prompt_template)

# 3. 初始化大语言模型 (LLM) - 更换为通义千问
# 我们选择使用阿里的通义千问 qwen-max 模型，它在中文处理和工具调用方面表现优异。
# temperature=0 表示我们希望模型做出确定性的、可重复的决策。
# 注意：用户提到的 qwen3-max 在API中通常标识为 qwen-max
llm = ChatTongyi(model="qwen-max", temperature=0)


class BuildingEnvAgent:
    """
    基于 LangChain 的建筑环境管理 Agent。

    这个类封装了 LangChain Agent 的创建和执行逻辑。它不再需要自己实现
    `think` 或 `act` 方法，因为这些复杂的流程已经由 `AgentExecutor` 完美处理。
    它的主要职责是：
    - 整合工具 (Tools)
    - 整合提示 (Prompt)
    - 整合大语言模型 (LLM)
    - 创建可执行的 Agent 实例
    - 提供一个简单的接口 (`run`) 来与 Agent 交互
    """
    def __init__(self, tools: List[Any]):
        """
        初始化 Agent。

        Args:
            tools (List[Any]): 一个包含所有可用工具的列表。这些工具必须是
                               使用 LangChain 的 `@tool` 装饰器创建的。
        """
        # --- 创建 LangChain Agent ---
        # `create_openai_tools_agent` 是一个高级辅助函数，它将 LLM 和 Prompt 绑定在一起，
        # 并专门针对 OpenAI 的函数调用（工具调用）功能进行了优化。
        # 这个函数返回一个 `Runnable` 对象，它是 LangChain 表达式语言 (LCEL) 的一部分，
        # 代表了一个可以被调用的、定义好的计算步骤。
        agent = create_openai_tools_agent(llm, tools, prompt)

        # --- 创建 Agent 执行器 ---
        # `AgentExecutor` 是驱动 Agent 运行的核心。它接收用户的输入，
        # 调用 `agent` (Runnable) 来决定下一步行动，如果需要调用工具，它会执行工具，
        # 然后将工具的输出返回给 `agent` 进行下一步思考，如此循环直到任务完成。
        # `verbose=True` 会在控制台打印出 Agent 的完整思考链，非常便于调试。
        self.executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    def run(self, user_input: str, environment_status: Dict) -> Dict:
        """
        运行 Agent 并获取结果。

        Args:
            user_input (str): 来自用户的自然语言指令。
            environment_status (Dict): 当前的环境状态，由感知模块提供。

        Returns:
            Dict: Agent 执行后返回的结果。
        """
        # --- 调用 Agent 执行器 ---
        # `.invoke()` 是 LangChain `Runnable` 对象的标准执行方法。
        # 我们将用户输入和格式化后的环境状态一起传递给 Agent。
        # AgentExecutor 会处理所有中间步骤，并最终返回一个包含最终答案的字典。
        return self.executor.invoke({
            "input": user_input,
            "environment_status": str(environment_status) # 转换为字符串以适应提示模板
        })
