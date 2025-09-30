# core/log_config.py
import sys
import os
import logging
from loguru import logger

def setup_logging():
    """
    配置 Loguru 日志系统。

    该函数负责设置整个应用的日志行为。它遵循“十二要素应用”的日志原则，
    将日志作为事件流输出到标准输出（stdout），并根据环境决定输出格式。

    - 在生产环境 (LOG_FORMAT="json")，日志将以 JSON 格式输出，便于机器解析和收集。
    - 在开发环境 (默认)，日志将以带颜色的、人类可读的文本格式输出。
    - 支持通过 LOG_FILE 环境变量将日志同时输出到文件。
    """
    # 1. 移除 Loguru 默认的处理器，以便完全自定义
    logger.remove()

    # 2. 从环境变量读取日志级别和格式，提供默认值
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    log_format = os.getenv("LOG_FORMAT", "text").lower()
    log_file = os.getenv("LOG_FILE", "")

    # 3. 根据配置选择格式化器和输出目标
    if log_format == "json":
        # 生产环境：使用 Loguru 内置的 JSON 序列化，这是最稳定可靠的方式。
        # `serialize=True` 会自动将日志记录转换为 JSON 格式，包含所有核心信息。
        logger.add(
            sys.stdout,
            level=log_level,
            serialize=True,
        )
    else:
        # 开发环境：使用对所有日志记录都安全的标准格式
        log_format_string = (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
        )
        logger.add(sys.stdout, level=log_level, colorize=True, format=log_format_string)

    # 4. 如果配置了日志文件路径，则添加文件处理器
    if log_file:
        logger.info(f"日志也将被写入到文件: {log_file}")
        try:
            logger.add(
                log_file,
                level=log_level,
                rotation="10 MB",       # 每 10 MB 切割
                retention="7 days",     # 保留 7 天
                compression="zip",      # 压缩旧文件
                serialize=(log_format == "json"), # 如果是json格式，文件也用json
                # 如果是文本格式，文件也用同样的文本格式
                format=log_format_string if log_format != "json" else None,
                # 确保文件写入是线程安全的
                enqueue=True,
                # 在程序退出时等待日志写完
                catch=True,
            )
        except Exception as e:
            logger.error(f"无法配置日志文件处理器: {e}")


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
