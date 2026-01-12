"""
LLM集成模块
提供统一的LLM调用接口，支持多供应商模型集成和本地模型部署
"""

from .base_llm import (
    BaseLLM,
    ModelConfig,
    Message,
    ModelResponse,
    ModelMetrics,
    ModelType
)

from .llm_providers import (
    OpenAILLM,
    AnthropicLLM,
    QwenLLM,
    HuggingFaceLLM,
    OllamaLLM,
    create_llm
)

from .model_detector import (
    ModelDetector,
    DetectedModel,
    auto_detect_models,
    get_best_available_model
)

from .llm_manager import (
    LLMManager,
    create_llm_manager,
    quick_chat,
    quick_chat_stream
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
    "ModelDetector",
    "DetectedModel",
    "auto_detect_models",
    "get_best_available_model",
    "LLMManager",
    "create_llm_manager",
    "quick_chat",
    "quick_chat_stream"
]

__version__ = "1.0.0"
