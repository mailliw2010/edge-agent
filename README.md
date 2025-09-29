# Edge Agent - 智能边缘设备管理系统

基于 LangChain 技术栈的智能 AI Agent，专为边缘设备和末端设备的自动感知、状态查询与策略控制而设计，特别针对空调等设备的智能管理。

## 🌟 核心特性

- **🤖 智能 AI Agent**: 基于 LangChain 和 OpenAI GPT 的对话式设备管理
- **🏠 设备管理**: 支持空调、传感器等多种边缘设备
- **📊 实时监控**: 设备状态感知、温度监控、能耗分析
- **⚡ 智能控制**: 自动化策略控制、节能优化、故障处理
- **🔄 多协议支持**: MQTT、HTTP 等通信协议
- **📋 策略引擎**: 基于规则的自动化控制系统
- **🌐 Web API**: RESTful API 接口，支持远程管理
- **📈 能效分析**: 能耗监控和优化建议

## 🏗️ 系统架构

```
edge-agent/
├── edge_agent/
│   ├── core/           # 核心组件
│   │   ├── config.py   # 配置管理
│   │   └── logger.py   # 日志系统
│   ├── devices/        # 设备管理
│   │   ├── models.py   # 设备模型
│   │   ├── base.py     # 基础接口
│   │   └── air_conditioner.py  # 空调控制器
│   ├── agents/         # AI Agent
│   │   ├── base.py     # 基础 Agent
│   │   ├── tools.py    # LangChain 工具
│   │   └── edge_agent.py  # 主 Agent
│   ├── api/            # Web API
│   │   └── main.py     # FastAPI 应用
│   └── utils/          # 工具模块
│       └── policy_engine.py  # 策略引擎
├── examples/           # 示例代码
├── tests/             # 测试文件
└── config/            # 配置文件
```

## 🚀 快速开始

### 1. 安装依赖

```bash
# 克隆仓库
git clone https://github.com/mailliw2010/edge-agent.git
cd edge-agent

# 安装依赖
pip install -r requirements.txt
# 或使用 pip install -e .
```

### 2. 配置环境

```bash
# 复制环境配置文件
cp .env.example .env

# 编辑配置文件，添加 OpenAI API Key
nano .env
```

必需配置：
```env
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. 运行方式

#### 命令行界面 (CLI)
```bash
# 运行 CLI 演示
python -m edge_agent.main cli
```

#### Web API 服务器
```bash
# 启动 API 服务器
python -m edge_agent.main api

# 访问 API 文档
open http://localhost:8000/docs
```

#### 示例脚本
```bash
# 基础使用示例
python examples/basic_usage.py

# 策略引擎示例
python examples/policy_example.py
```

## 💡 使用示例

### 1. 基础设备控制

```python
from edge_agent.agents.edge_agent import EdgeAgent, DeviceManager
from edge_agent.devices.models import AirConditionerDevice, ACMode

# 创建设备管理器
device_manager = DeviceManager()

# 添加空调设备
ac = AirConditionerDevice(
    device_id="living_room_ac",
    name="客厅空调",
    location="客厅",
    current_temperature=26.0,
    target_temperature=24.0,
    mode=ACMode.COOL
)
device_manager.add_device(ac)

# 创建 AI Agent
agent = EdgeAgent(device_manager)

# 与 Agent 对话
response = await agent.process_message("把客厅空调温度调到 22 度")
print(response)
```

### 2. 策略自动化

```python
from edge_agent.utils.policy_engine import PolicyEngine, PolicyRule

# 创建策略引擎
policy_engine = PolicyEngine(device_manager)

# 添加节能规则
energy_rule = PolicyRule(
    rule_id="energy_saving",
    name="节能模式",
    conditions=[
        {"type": "time_range", "start_time": "14:00", "end_time": "18:00"},
        {"type": "energy_consumption", "device_id": "ac_001", "operator": ">=", "value": 3.0}
    ],
    actions=[
        {"type": "set_temperature", "device_id": "ac_001", "temperature": 26.0}
    ]
)
policy_engine.add_rule(energy_rule)

# 启动策略监控
await policy_engine.start_monitoring()
```

### 3. Web API 使用

```python
import requests

# 获取设备列表
response = requests.get("http://localhost:8000/devices")
devices = response.json()

# 与 Agent 对话
chat_data = {"message": "分析当前环境状况"}
response = requests.post("http://localhost:8000/chat", json=chat_data)
print(response.json()["response"])

# 系统优化
response = requests.post("http://localhost:8000/optimize")
optimization = response.json()
```

## 🛠️ 主要功能

### 设备管理
- **多设备支持**: 空调、传感器、执行器等
- **实时监控**: 温度、湿度、能耗等参数
- **状态管理**: 设备在线状态、故障检测
- **远程控制**: 电源、温度、模式、风速等

### 智能 Agent
- **自然语言交互**: 支持中文对话式控制
- **智能理解**: 理解用户意图，执行相应操作
- **上下文记忆**: 保持对话历史和设备状态
- **错误处理**: 智能故障诊断和建议

### 策略引擎
- **规则配置**: 基于时间、温度、能耗的自动化规则
- **智能调度**: 自动执行设备控制策略
- **节能优化**: 智能节能算法
- **场景模式**: 预设场景快速切换

### 通信协议
- **MQTT**: 支持 MQTT 协议设备通信
- **HTTP**: RESTful API 设备接口
- **扩展性**: 易于添加新的通信协议

## 📊 监控与分析

### 实时监控
- 设备在线状态
- 温度变化趋势
- 能耗实时数据
- 系统健康状态

### 数据分析
- 能耗统计分析
- 使用模式分析
- 效率优化建议
- 故障预测

### 报告生成
- 日/周/月使用报告
- 节能效果分析
- 设备性能评估
- 维护建议

## 🔧 配置说明

### 环境变量配置

| 变量名 | 描述 | 默认值 |
|--------|------|--------|
| `OPENAI_API_KEY` | OpenAI API 密钥 | 必需 |
| `MQTT_BROKER_HOST` | MQTT 服务器地址 | localhost |
| `MQTT_BROKER_PORT` | MQTT 服务器端口 | 1883 |
| `API_HOST` | API 服务器地址 | 0.0.0.0 |
| `API_PORT` | API 服务器端口 | 8000 |
| `LOG_LEVEL` | 日志级别 | INFO |

### 设备配置
支持通过配置文件或代码动态添加设备：

```yaml
devices:
  - device_id: "ac_001"
    name: "主卧空调"
    type: "air_conditioner"
    location: "主卧"
    interface:
      type: "mqtt"
      topic_prefix: "home/ac_001"
```

## 🧪 测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_devices.py

# 带覆盖率报告
pytest --cov=edge_agent
```

## 📚 API 文档

启动 API 服务器后，访问以下地址获取完整 API 文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 主要 API 端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/devices` | GET | 获取设备列表 |
| `/devices/{device_id}` | GET | 获取设备状态 |
| `/chat` | POST | 与 Agent 对话 |
| `/analyze` | POST | 环境分析 |
| `/optimize` | POST | 系统优化 |
| `/health` | GET | 系统健康检查 |

## 🤝 贡献指南

欢迎贡献代码、报告问题或提出改进建议！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 🆘 支持与帮助

- 📧 邮箱: support@edge-agent.com
- 💬 讨论: [GitHub Discussions](https://github.com/mailliw2010/edge-agent/discussions)
- 🐛 问题: [GitHub Issues](https://github.com/mailliw2010/edge-agent/issues)

## 🔮 未来规划

- [ ] 支持更多设备类型（照明、安防等）
- [ ] 机器学习预测算法
- [ ] 移动端应用
- [ ] 云端集成
- [ ] 多语言支持
- [ ] 图形化配置界面

---

**注意**: 本项目需要 OpenAI API 密钥才能正常运行 AI Agent 功能。请确保已正确配置 `OPENAI_API_KEY` 环境变量。