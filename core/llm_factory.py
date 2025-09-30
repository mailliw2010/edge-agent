# core/llm_factory.py
from loguru import logger
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_community.chat_models import ChatTongyi
from langchain_openai import ChatOpenAI

from config import settings

def create_llm_client() -> BaseChatModel:
    """
    LLM 客户端工厂函数。

    根据 .env 文件中的配置，创建并返回相应的 LLM 客户端实例。
    这个函数是连接代码逻辑与基础设施配置的桥梁。

    Returns:
        一个实现了 LangChain `BaseChatModel` 接口的 LLM 客户端实例。

    Raises:
        ValueError: 如果配置的 LLM_PROVIDER 不被支持。
    """
    provider = settings.LLM_PROVIDER

    logger.info(f"🏭 Creating LLM client for provider: '{provider}'")

    if provider == "dashscope":
        # 使用通义千问
        llm = ChatTongyi(
            model=settings.LLM_MODEL_NAME,
            dashscope_api_key=settings.DASHSCOPE_API_KEY,
        )
        logger.success(f"✅ ChatTongyi client created successfully (model: {settings.LLM_MODEL_NAME}).")
        return llm

    elif provider == "vllm":
        # 使用 vLLM 提供的 OpenAI 兼容接口
        # LangChain 的 ChatOpenAI 客户端可以连接任何 OpenAI 兼容的 API
        llm = ChatOpenAI(
            model=settings.LLM_MODEL_NAME,
            openai_api_base=settings.VLLM_API_BASE,
            openai_api_key=settings.VLLM_API_KEY,
            streaming=settings.LLM_STREAMING, # 从配置中读取流式设置
            temperature=0.7, # 可以根据需要调整默认参数
        )
        logger.success(
            f"✅ vLLM (ChatOpenAI) client created successfully "
            f"(model: {settings.LLM_MODEL_NAME}, API Base: {settings.VLLM_API_BASE}, Streaming: {settings.LLM_STREAMING})."
        )
        return llm

    else:
        # 这个分支理论上不会被执行，因为 settings.py 已经做了检查
        logger.error(f"Unsupported LLM provider: '{provider}'")
        raise ValueError(f"不支持的 LLM 提供商: '{provider}'")
