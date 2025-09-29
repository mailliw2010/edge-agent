# core/base_agent.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseAgent(ABC):
    """
    Agent 抽象基类 (Abstract Base Class)。

    这个基类定义了所有具体 Agent 必须遵循的接口规范，确保了系统的可扩展性和一致性。
    每个 Agent 都被设计为一个独立的、有特定目标的实体，拥有思考、感知和行动的能力。

    - `think`: 核心决策循环，根据目标和记忆生成计划。
    - `perceive`: 感知环境，从传感器或数据源收集信息。
    - `act`: 执行动作，使用工具与外部世界交互。
    """

    def __init__(self, name: str, tools: List[Any]):
        """
        初始化 Agent。

        Args:
            name (str): Agent 的唯一名称，用于识别和日志记录。
            tools (List[Any]): Agent 可以使用的工具列表。
        """
        self.name = name
        self.tools = {tool.name: tool for tool in tools}
        # 可以在这里初始化记忆模块 (memory)
        # self.memory = Memory()

    @abstractmethod
    def think(self) -> str:
        """
        思考并制定下一步行动计划。
        这是 Agent 的大脑，它会分析当前状态、目标和可用工具，
        然后决定是调用某个工具还是返回最终答案。

        Returns:
            str: 下一步要执行的动作描述或最终结果。
        """
        raise NotImplementedError("子类必须实现 think 方法")

    @abstractmethod
    def perceive(self) -> Dict[str, Any]:
        """
        感知环境状态。
        这个方法负责从外部世界（如传感器、API、数据库）收集信息，
        为 Agent 的决策提供数据支持。

        Returns:
            Dict[str, Any]: 描述当前环境状态的字典。
        """
        raise NotImplementedError("子类必须实现 perceive 方法")

    def act(self, action: str, **kwargs) -> Any:
        """
        根据思考结果执行一个动作。
        它会解析 `think` 方法的输出，找到对应的工具并执行它。

        Args:
            action (str): 要执行的工具名称。
            **kwargs: 传递给工具的参数。

        Returns:
            Any: 工具执行后的返回结果。
        """
        if action not in self.tools:
            return f"错误: 未知的工具 '{action}'"
        tool = self.tools[action]
        # 执行工具，并将结果返回
        return tool.execute(**kwargs)
