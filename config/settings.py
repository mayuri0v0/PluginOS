from functools import lru_cache
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """运行时配置：提供 LLM 连接信息。"""

    api_key: str = Field(default="", description="LLM API Key")
    base_url: str = Field(default="", description="LLM Base URL, 例如 https://api.openai.com/v1")
    model: str = Field(default="gpt-4o-mini", description="模型名称")
    temperature: float = Field(default=0.0, ge=0.0, le=2.0, description="采样温度")
    request_timeout: Optional[float] = Field(default=60.0, description="请求超时时间（秒）")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="LLM_",
        extra="ignore",
    )

    @field_validator("base_url")
    @classmethod
    def _strip_url(cls, v: str) -> str:
        return v.strip().rstrip("/") if v else v


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """懒加载配置，避免重复解析环境变量。"""

    return Settings()


