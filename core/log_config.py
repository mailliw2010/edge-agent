# core/log_config.py
import sys
import os
import json
import logging
from loguru import logger

def setup_logging():
    """
    配置 Loguru 日志系统。

    该函数负责设置整个应用的日志行为。它遵循“十二要素应用”的日志原则，
    将日志作为事件流输出到标准输出（stdout），并根据环境决定输出格式。

    - 在生产环境 (LOG_FORMAT="json")，日志将以 JSON 格式输出，便于机器解析和收集。
    - 在开发环境 (默认)，日志将以带颜色的、人类可读的文本格式输出。
    """
    # 1. 移除 Loguru 默认的处理器，以便完全自定义
    logger.remove()

    # 2. 从环境变量读取日志级别和格式，提供默认值
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    log_format = os.getenv("LOG_FORMAT", "text").lower()

    # 3. 定义 JSON 格式化器
    def json_formatter(record):
        """
        一个自定义的序列化器，用于将 Loguru 的记录对象转换为 JSON 字符串。
        """
        # 对于被拦截的日志，file.path 可能不存在，需要安全访问
        file_path = record["file"].path if record.get("file") else "unknown"
        
        log_object = {
            "timestamp": record["time"].isoformat(),
            "level": record["level"].name,
            "message": record["message"],
            "source": {
                "name": record["name"],
                "file": file_path,
                "line": record["line"],
            },
            **record["extra"],
        }
        return json.dumps(log_object, ensure_ascii=False) + "\\n"

    # 4. 根据配置选择格式化器和输出目标
    if log_format == "json":
        # 生产环境：使用 JSON 格式
        logger.add(
            sys.stdout,
            level=log_level,
            format=json_formatter,
            serialize=True,
        )
    else:
        # 开发环境：使用一个对所有日志记录都安全的标准格式
        log_format_string = (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
        )
        logger.add(sys.stdout, level=log_level, colorize=True, format=log_format_string)

    # 5. 关键一步：接管标准 `logging` 模块
    class InterceptHandler(logging.Handler):
        def emit(self, record):
            try:
                level = logger.level(record.levelname).name
            except ValueError:
                level = record.levelno

            frame, depth = logging.currentframe(), 2
            while frame and frame.f_code.co_filename == logging.__file__:
                frame = frame.f_back
                depth += 1

            logger.opt(depth=depth, exception=record.exc_info).log(
                level, record.getMessage()
            )

    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    logger.info(f"日志系统初始化完成。日志级别: {log_level}, 日志格式: {log_format}")
