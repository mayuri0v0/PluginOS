from functools import lru_cache

from langchain_openai import ChatOpenAI

from config.settings import get_settings


@lru_cache(maxsize=1)
def get_llm() -> ChatOpenAI:
    """初始化并缓存 LLM 客户端。"""

    settings = get_settings()
    return ChatOpenAI(
        model=settings.model,
        api_key=settings.api_key,
        base_url=settings.base_url or None,
        temperature=settings.temperature,
        timeout=settings.request_timeout,
    )


