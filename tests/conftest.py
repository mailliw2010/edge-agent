import os
import shutil
from pathlib import Path

import pytest

# --- 默认测试环境变量设置 ---
os.environ.setdefault("SIMULATION_MODE", "True")
os.environ.setdefault("LLM_PROVIDER", "vllm")
os.environ.setdefault("LLM_MODEL_NAME", "test-model")
os.environ.setdefault("VLLM_API_BASE", "http://localhost:8000/v1")
os.environ.setdefault("VLLM_API_KEY", "test-key")
os.environ.setdefault("TOOL_TIMEOUT_SECONDS", "2")
os.environ.setdefault("TOOL_MAX_ATTEMPTS", "2")

def _simulation_root() -> Path:
    from tools.sensor_reader import _SIMULATED_SYS_PATH  # 延迟导入，避免循环

    return Path(_SIMULATED_SYS_PATH)


@pytest.fixture(autouse=True)
def clean_simulation_environment():
    """在每个测试前后清理模拟设备目录，确保环境隔离。"""
    root = _simulation_root()
    if root.exists():
        shutil.rmtree(root)
    yield
    if root.exists():
        shutil.rmtree(root)
