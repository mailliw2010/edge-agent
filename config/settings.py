# config/settings.py
import os
from dotenv import load_dotenv
from typing import Literal
from loguru import logger

# --- 核心功能：加载环境变量 ---
logger.info("正在加载 .env 文件中的环境变量...")
load_dotenv()
logger.info("环境变量加载完成。")

# --- LLM 提供商配置 ---
LLMProvider = Literal["dashscope", "vllm"]

LLM_PROVIDER: LLMProvider = os.getenv("LLM_PROVIDER", "dashscope").lower() # type: ignore
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "qwen-max")

logger.info(f"LLM 提供商已配置为: {LLM_PROVIDER}")
logger.info(f"LLM 模型名称已配置为: {LLM_MODEL_NAME}")

# --- Dashscope (通义千问) 配置 ---
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")

# --- vLLM (本地 OpenAI 兼容接口) 配置 ---
VLLM_API_BASE = os.getenv("VLLM_API_BASE")
VLLM_API_KEY = os.getenv("VLLM_API_KEY")


# --- 通用 LLM 配置 ---
# 将字符串 "False" 或 "True" 转换为布尔值
LLM_STREAMING = os.getenv("LLM_STREAMING", "False").lower() == "true"
logger.info(f"LLM 流式响应已配置为: {LLM_STREAMING}")

# --- 启动时验证 ---
# 根据选择的 LLM 提供商，验证必要的环境变量是否已设置。
if LLM_PROVIDER == "dashscope":
    if not DASHSCOPE_API_KEY:
        logger.error("错误：当 LLM_PROVIDER='dashscope' 时，必须设置 DASHSCOPE_API_KEY。")
        logger.error("请在 .env 文件中添加：DASHSCOPE_API_KEY='your_api_key_here'")
        exit()
    logger.info("✅ Dashscope 配置验证通过。")

elif LLM_PROVIDER == "vllm":
    if not VLLM_API_BASE:
        logger.error("错误：当 LLM_PROVIDER='vllm' 时，必须设置 VLLM_API_BASE。")
        logger.error("请在 .env 文件中添加：VLLM_API_BASE='http://your_vllm_server/v1'")
        exit()
    logger.info("✅ vLLM 配置验证通过。")

else:
    logger.error(f"错误：不支持的 LLM_PROVIDER: '{LLM_PROVIDER}'。")
    logger.error("请在 .env 文件中将 LLM_PROVIDER 设置为 'dashscope' 或 'vllm'。")
    exit()

