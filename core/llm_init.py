from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel

from config import get_settings


def get_llm() -> BaseChatModel:
    """
    根据运行时配置初始化并返回 LLM 实例。

    优先从环境变量 / .env 中读取：
      - LLM_API_KEY
      - LLM_BASE_URL
      - LLM_MODEL
      - LLM_TEMPERATURE
    """
    settings = get_settings()

    if not settings.api_key.get_secret_value():
        raise ValueError("未配置 LLM_API_KEY，请在 .env 或环境变量中设置。")

    model = init_chat_model(
        settings.model or "deepseek-chat",
        api_key=settings.api_key.get_secret_value(),
        base_url=settings.base_url or None,
        temperature=settings.temperature,
        timeout=settings.request_timeout,
    )
    return model
