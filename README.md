# Edge-Agent 项目说明

## 项目简介
本项目基于 LangChain 技术栈，旨在实现一个智能 AI Agent，用于边缘设备和末端设备的自动感知、状态查询与策略控制，特别针对空调等设备的智能管理。

## 主要功能
1. 通过自然语言对话获取和查询边缘设备的数量和在线状态。
2. 自动感知边缘设备下的末端设备状态。
3. 自动感知边缘设备下的空调设备运行情况，并可根据策略进行启停操作。

## 代码结构
```
edge-agent/
│
├── agent/                  # AI Agent 相关核心逻辑
│   ├── base_agent.py       # Agent基类，定义通用接口
│   ├── device_agent.py     # 设备感知与控制Agent
│   └── ac_agent.py         # 空调设备专用Agent
│
├── chains/                 # LangChain链路定义
│   ├── device_status_chain.py   # 查询设备状态的链
│   ├── ac_status_chain.py       # 查询/控制空调的链
│   └── policy_chain.py          # 策略决策链
│
├── data/                   # 存放设备、策略等数据
│   ├── devices.json
│   └── policies.json
│
├── services/               # 设备/空调/策略等服务层
│   ├── device_service.py   # 设备数据获取与管理
│   ├── ac_service.py       # 空调设备管理
│   └── policy_service.py   # 策略管理与执行
│
├── api/                    # 对外API接口（如FastAPI等）
│   └── main.py
│
├── utils/                  # 工具类
│   └── logger.py
│
├── config.py               # 配置文件
├── requirements.txt        # 依赖包
└── README.md
```

## 依赖安装
```bash
pip install -r requirements.txt
```

## 运行方式
```bash
uvicorn api.main:app --reload
```

## 典型用例
- 查询所有边缘设备的在线状态
- 查询指定设备的详细状态
- 查询/控制空调设备

## 设备状态上报说明
边缘设备通过 `/sys/i800/DEVID/event/register` 路径上报状态，Agent 通过读取该路径下的内容来感知设备的在线状态。

---

# 示例：查询所有边缘设备在线状态

见 `services/device_service.py` 和 `agent/device_agent.py` 示例代码。
