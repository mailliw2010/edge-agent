# core/reliability.py
"""统一的重试与超时控制模块。

该模块为工具调用、LLM 调用等长耗时操作提供统一的稳健性保障：

- `run_with_resilience`：在限定时间内执行某个操作，失败时自动重试。
- 自定义异常 `OperationTimeoutError`、`ResilienceError`：
  帮助调用方判断失败原因并输出更友好的错误信息。

实现细节：
- 使用 `ThreadPoolExecutor` 来为同步函数提供超时控制能力。
- 使用 `tenacity` 库实现指数退避 + 最大重试次数的重试策略。
- 默认读取环境变量以允许在生产环境中调优相关参数。
"""

from __future__ import annotations

import atexit
import os
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from typing import Any, Callable, Iterable, Tuple

from loguru import logger
from tenacity import (
    RetryError,
    before_sleep_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

# --- 配置参数（可通过环境变量覆盖） ---
_MAX_WORKERS = int(os.getenv("RELIABILITY_MAX_WORKERS", "8"))
_DEFAULT_TIMEOUT_SECONDS = float(os.getenv("OPERATION_TIMEOUT_SECONDS", "10"))
_DEFAULT_MAX_ATTEMPTS = int(os.getenv("OPERATION_MAX_ATTEMPTS", "3"))
_DEFAULT_BACKOFF_MULTIPLIER = float(os.getenv("RETRY_BACKOFF_BASE", "0.5"))
_DEFAULT_BACKOFF_MAX = float(os.getenv("RETRY_BACKOFF_MAX", "4"))

# --- 线程池：为同步函数提供超时能力 ---
_EXECUTOR = ThreadPoolExecutor(max_workers=_MAX_WORKERS)
atexit.register(_EXECUTOR.shutdown, wait=False)


class OperationTimeoutError(TimeoutError):
    """表示单次执行因超时而失败。"""

    def __init__(self, operation: str, timeout_seconds: float) -> None:
        super().__init__(f"操作 '{operation}' 在 {timeout_seconds}s 内未完成")
        self.operation = operation
        self.timeout_seconds = timeout_seconds


class ResilienceError(RuntimeError):
    """在执行多次重试后仍失败时抛出的统一异常。"""

    def __init__(self, operation: str, attempts: int, last_exception: Exception) -> None:
        message = (
            f"操作 '{operation}' 在 {attempts} 次尝试后仍失败：{last_exception!s}"
        )
        super().__init__(message)
        self.operation = operation
        self.attempts = attempts
        self.last_exception = last_exception


def _execute_with_timeout(func: Callable[[], Any], *, timeout_seconds: float, operation: str) -> Any:
    """在独立线程中执行同步函数，并在超时后抛出 `OperationTimeoutError`。"""
    future = _EXECUTOR.submit(func)
    try:
        return future.result(timeout=timeout_seconds)
    except FuturesTimeoutError as exc:  # pragma: no cover - 依赖于运行时行为
        logger.warning(
            "[{operation}] 执行超时，超过 {timeout}s。", operation=operation, timeout=timeout_seconds
        )
        raise OperationTimeoutError(operation, timeout_seconds) from exc
    finally:
        if not future.done():
            future.cancel()


def run_with_resilience(
    operation_name: str,
    func: Callable[[], Any],
    *,
    timeout_seconds: float | None = None,
    max_attempts: int | None = None,
    retry_exceptions: Iterable[type[BaseException]] | None = None,
    backoff_multiplier: float | None = None,
    backoff_max: float | None = None,
) -> Any:
    """在超时与重试策略下执行给定函数。

    Args:
        operation_name: 操作名称，用于日志与错误信息。
        func: 待执行的无参函数（可通过 `lambda` 捕获上下文）。
        timeout_seconds: 单次执行的超时时间，默认读取环境变量。
        max_attempts: 最大重试次数，默认读取环境变量。
        retry_exceptions: 需要重试的异常类型集合，默认为 `(Exception,)`。
        backoff_multiplier: 指数退避的初始间隔。
        backoff_max: 指数退避的最大间隔。

    Returns:
        func 的执行结果。

    Raises:
        ResilienceError: 在允许的重试次数内仍然失败。
        其他异常: 如果异常类型不在 `retry_exceptions` 中，会直接透传给调用方。
    """

    timeout_seconds = timeout_seconds or _DEFAULT_TIMEOUT_SECONDS
    max_attempts = max_attempts or _DEFAULT_MAX_ATTEMPTS
    backoff_multiplier = backoff_multiplier or _DEFAULT_BACKOFF_MULTIPLIER
    backoff_max = backoff_max or _DEFAULT_BACKOFF_MAX

    retry_exceptions = tuple(retry_exceptions or (Exception,))

    # 确保超时异常始终触发重试逻辑
    retry_exception_types: Tuple[type[BaseException], ...] = tuple(
        set(retry_exceptions + (OperationTimeoutError,))  # type: ignore[arg-type]
    )

    @retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=backoff_multiplier, max=backoff_max),
        reraise=True,
        retry=retry_if_exception_type(retry_exception_types),
        before_sleep=before_sleep_log(
            logger,
            (
                f"[{operation_name}] 第 {{retry_state.attempt_number}} 次执行失败，"
                "将在 {retry_state.next_action.sleep} 秒后重试。"
            ),
        ),
    )
    def _call_with_retry() -> Any:
        return _execute_with_timeout(
            func,
            timeout_seconds=timeout_seconds,
            operation=operation_name,
        )

    try:
        return _call_with_retry()
    except RetryError as retry_exc:
        last_exception = retry_exc.last_attempt.exception()
        # `last_exception` 可能为 None（理应不会发生），做一次保护
        last_exception = last_exception or RuntimeError("未知原因导致的失败")
        logger.error(
            "[{operation}] 在 {attempts} 次尝试后失败：{error}",
            operation=operation_name,
            attempts=max_attempts,
            error=last_exception,
        )
        raise ResilienceError(operation_name, max_attempts, last_exception) from last_exception