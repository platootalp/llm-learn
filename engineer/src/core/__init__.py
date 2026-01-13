"""
LLM集成模块
提供统一的LLM调用接口，支持多供应商LLM集成和本地LLM部署
"""

from .base_llm import (
    BaseLLM,
    ModelConfig,
    Message,
    ModelResponse,
    ModelMetrics,
    ModelType
)

from .providers import (
    OpenAILLM,
    AnthropicLLM,
    QwenLLM,
    HuggingFaceLLM,
    OllamaLLM
)

from .llm_factory import (
    create_llm,
    infer_model_type,
    create_model,
    quick_chat,
    quick_chat_stream
)

from .model_info import (
    ModelInfoProvider,
    ModelInfo,
    list_models,
    print_models
)

__all__ = [
    "BaseLLM",
    "ModelConfig",
    "Message",
    "ModelResponse",
    "ModelMetrics",
    "ModelType",
    "OpenAILLM",
    "AnthropicLLM",
    "QwenLLM",
    "HuggingFaceLLM",
    "OllamaLLM",
    "create_llm",
    "infer_model_type",
    "create_model",
    "quick_chat",
    "quick_chat_stream",
    "ModelInfoProvider",
    "ModelInfo",
    "list_models",
    "print_models"
]

__version__ = "1.0.0"
