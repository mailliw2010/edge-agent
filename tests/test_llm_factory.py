import importlib

from langchain_openai import ChatOpenAI


def test_create_llm_client_vllm(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "vllm")
    monkeypatch.setenv("LLM_MODEL_NAME", "test-model")
    monkeypatch.setenv("VLLM_API_BASE", "http://localhost:8000/v1")
    monkeypatch.setenv("VLLM_API_KEY", "dummy-key")

    import config.settings as settings

    importlib.reload(settings)

    import core.llm_factory as llm_factory

    importlib.reload(llm_factory)

    llm = llm_factory.create_llm_client()

    assert isinstance(llm, ChatOpenAI)
    assert llm_factory.settings.LLM_PROVIDER == "vllm"
