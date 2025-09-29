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

# --- 配置项：OpenAI API 密钥 ---
# 从环境变量中获取 OpenAI 的 API 密钥。
# os.getenv() 是一个安全的方法，如果环境变量不存在，它会返回 None，
# 而不是抛出异常，这使得代码更具鲁棒性。
# 这个 API 密钥是 Agent 与 OpenAI 的大语言模型（LLM）进行通信的凭证。
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# --- 验证与提示 ---
# 这是一个关键的启动检查。如果未能获取到 API 密钥，
# 程序将打印一条明确的错误消息并退出。
# 这样做可以防止在缺少关键配置的情况下运行程序，从而避免后续出现难以排查的运行时错误。
if not OPENAI_API_KEY:
    print("错误：OPENAI_API_KEY 环境变量未设置。")
    print("请在项目根目录下创建 .env 文件，并添加如下内容：")
    print("OPENAI_API_KEY='your_api_key_here'")
    exit() # 强制退出程序

print("OpenAI API 密钥已成功加载。")
