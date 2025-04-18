import os
from typing import Dict, List, Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class Settings(BaseSettings):
    """应用配置类"""
    # API配置
    API_V1_PREFIX: str = "/api"
    PROJECT_NAME: str = "AI服务 - LangChain与FastAPI集成"
    DEBUG: bool = True

    # 安全配置
    API_KEY_NAME: str = "api_key"
    API_KEY: Optional[str] = os.getenv("API_KEY")

    # LLM配置（切换到阿里云百炼）
    QWEN_API_KEY: str = os.getenv("QWEN_API_KEY", "")
    QWEN_API_URL: str = os.getenv("QWEN_API_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")

    # 默认模型配置（使用百炼的模型）
    DEFAULT_MODEL: str = "qwen-turbo"  # 可改为 "qwen-plus" 等
    DEFAULT_TEMPERATURE: float = 0.7
    DEFAULT_MAX_TOKENS: int = 500
    AVAILABLE_MODELS: List[str] = [
        "qwen-turbo",
        "qwen-plus",
        "qwen-max"
    ]

    class Config:
        case_sensitive = True


# 创建配置实例
settings = Settings()
