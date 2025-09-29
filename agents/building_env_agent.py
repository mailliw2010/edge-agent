# agents/building_env_agent.py
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from typing import List, Any, Dict

# --- Agent 核心组件初始化 ---

# 1. 定义系统提示 (System Prompt)
# 这是 Agent 的“性格”和“指令手册”。它告诉 LLM 它的角色、目标、可用工具以及如何响应。
# 这个提示的设计至关重要，直接影响 Agent 的行为和性能。
# 我们明确指示它要主动感知环境，并根据感知结果和用户请求来做决策。
prompt_template = """
你是一个名为 "BuildingEnvAgent" 的智能建筑环境管家。
你的目标是：根据用户的指令和环境的实时状态，自主地维护一个舒适和节能的建筑环境。

可用工具：
- 你可以使用 `sensor_reader` 工具来感知环境，比如读取温度、灯光状态等。
- 你可以使用 `ac_control` 和 `light_control` 工具来控制设备。

决策流程：
1.  **感知**：在做任何决策之前，首先使用 `sensor_reader` 工具获取当前的环境状态。
2.  **思考**：结合你的感知结果和用户的最新请求，分析是否需要采取行动。
3.  **行动**：如果需要，选择最合适的工具并调用它来完成任务。

当前环境状态：
{environment_status}

用户最新请求：
{input}

{agent_scratchpad}
"""

# 2. 创建聊天提示模板
# ChatPromptTemplate 是 LangChain 中用于构建与聊天模型交互的标准化结构。
prompt = ChatPromptTemplate.from_template(prompt_template)

# 3. 初始化大语言模型 (LLM)
# 我们选择使用 OpenAI 的 gpt-4-turbo 模型，因为它在工具调用方面表现出色。
# temperature=0 表示我们希望模型做出确定性的、可重复的决策，而不是创造性的回答。
llm = ChatOpenAI(model="gpt-4-turbo", temperature=0)


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
