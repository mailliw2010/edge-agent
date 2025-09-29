# config/settings.py
import os
from dotenv import load_dotenv

# --- 核心功能：加载环境变量 ---
# 这段代码的目的是从项目根目录下的 .env 文件中加载环境变量。
# .env 文件是一个纯文本文件，用于存储敏感信息，如 API 密钥，
# 从而避免将这些信息硬编码在代码中或提交到版本控制系统（如 Git）。
# load_dotenv() 函数会自动查找 .env 文件并将其中的键值对加载到操作系统的环境中。
print("正在加载 .env 文件中的环境变量...")
load_dotenv()
print("环境变量加载完成。")

# --- 配置项：通义千问 API 密钥 ---
# 从环境变量中获取阿里通义千问的 API 密钥。
# 这个 API 密钥是 Agent 与通义千问大语言模型（LLM）进行通信的凭证。
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")

# --- 验证与提示 ---
# 这是一个关键的启动检查。如果未能获取到 API 密钥，
# 程序将打印一条明确的错误消息并退出。
if not DASHSCOPE_API_KEY:
    print("错误：DASHSCOPE_API_KEY 环境变量未设置。")
    print("请在项目根目录下创建 .env 文件，并添加如下内容：")
    print("DASHSCOPE_API_KEY='your_api_key_here'")
    exit() # 强制退出程序

print("通义千问 API 密钥已成功加载。")
