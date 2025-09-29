# main.py
import config.settings # 导入以确保环境变量被最先加载
import time
import json
import os
from agents.building_env_agent import BuildingEnvAgent
from tools.sensor_reader import sensor_reader # 导入新的 sensor_reader 函数
from tools.ac_control import ac_control
from tools.light_control import light_control

def main_loop():
    """
    项目主循环，演示 Agent 如何与环境交互。

    这个新版本的主循环更加清晰地分离了“感知”和“决策”两个阶段。
    它不再关心 Agent 内部的“思考-行动”循环，因为这已经完全由 LangChain 的
    `AgentExecutor` 接管。主循环的职责简化为：
    1.  **感知环境**: 定期调用 `SensorReaderTool` 来获取最新的环境快照。
    2.  **模拟用户输入**: 提供一个自然语言指令来驱动 Agent。
    3.  **调用 Agent**: 将环境快照和用户指令交给 Agent 处理。
    4.  **展示结果**: 打印 Agent 的最终输出。
    """
    # 1. 初始化工具集
    # 现在所有工具都是统一的 @tool 函数格式。
    tools = [
        sensor_reader,
        ac_control,
        light_control
    ]

    # 2. 实例化 Agent
    # 创建 Agent 实例，并将所有可用的工具传递给它。
    agent = BuildingEnvAgent(tools=tools)
    print("🚀 LangChain Agent 'BuildingEnvAgent' 已启动，准备接收指令...")

    # 3. 定义一个简单的任务场景
    # 我们可以轮流测试不同的用户指令来观察 Agent 的行为。
    task_scenarios = [
        "天气好像有点热，帮我处理一下。",
        "办公室没人了，确保所有设备都已关闭。",
        "现在是什么情况？",
    ]
    scenario_index = 0

    # 4. 启动主循环
    try:
        while True:
            print("\n" + "="*20 + f" 新一轮任务开始 (任务 {scenario_index + 1}) " + "="*20 + "\n")

            # --- 感知阶段 ---
            # Agent 在做决策前，需要先了解当前的环境状态。
            print("🤖 [感知] 正在获取当前环境状态...")
            # 直接调用 sensor_reader 函数
            environment_status = sensor_reader({"device_id": "all"})
            print(f"🤖 [感知] 环境状态获取完成: \n{json.dumps(environment_status, indent=2, ensure_ascii=False)}")

            # --- 决策与执行阶段 ---
            # 获取当前场景的用户指令
            user_input = task_scenarios[scenario_index]
            print(f"👤 [用户指令] {user_input}")
            
            # 调用 Agent，将用户指令和环境状态作为输入
            print("🧠 [Agent 决策中]...")
            result = agent.run(user_input, environment_status)
            
            # 打印 Agent 的最终输出
            print(f"\n✅ [Agent 最终结果] {result['output']}")

            # 切换到下一个场景
            scenario_index = (scenario_index + 1) % len(task_scenarios)

            # 等待一段时间，模拟真实世界的时间流逝
            print("\n" + "="*60 + "\n")
            time.sleep(15)

    except KeyboardInterrupt:
        print("\n🛑 Agent 运行被手动终止。")
    except Exception as e:
        print(f"\n💥 Agent 运行时发生严重错误: {e}")


if __name__ == "__main__":
    # 启动主循环
    main_loop()
