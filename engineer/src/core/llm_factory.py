"""
LLM提供商工厂函数和便捷接口
提供统一的LLM实例创建接口，支持自动推断LLM类型
"""

import os
from typing import Optional, Generator

from .base_llm import (
    BaseLLM, ModelConfig, ModelType, Message, ModelResponse
)
from .providers import (
    OpenAILLM, AnthropicLLM, QwenLLM,
    HuggingFaceLLM, OllamaLLM
)


def create_llm(config: ModelConfig) -> BaseLLM:
    """根据配置创建对应的LLM实例
    
    根据LLM类型选择合适的提供商类并创建实例
    这是工厂模式的实现，用于统一创建不同类型的LLM实例
    
    Args:
        config: LLM配置对象，包含LLM类型和其他配置信息
    
    Returns:
        BaseLLM: 对应的LLM实例（OpenAILLM、AnthropicLLM等）
    
    Raises:
        ValueError: 不支持的LLM类型
    """
    provider_map = {
        ModelType.OPENAI: OpenAILLM,
        ModelType.ANTHROPIC: AnthropicLLM,
        ModelType.QWEN: QwenLLM,
        ModelType.HUGGINGFACE: HuggingFaceLLM,
        ModelType.OLLAMA: OllamaLLM,
    }

    provider_class = provider_map.get(config.model_type)
    if not provider_class:
        raise ValueError(f"不支持的LLM类型: {config.model_type}")

    return provider_class(config)


def infer_model_type(model_name: str) -> ModelType:
    """根据LLM名称推断LLM类型
    
    基于LLM名称的模式匹配自动推断LLM类型
    支持的推断规则：
    - gpt前缀 -> OPENAI
    - claude前缀 -> ANTHROPIC
    - 包含qwen -> QWEN
    - 包含/（路径分隔符） -> HUGGINGFACE
    - 其他 -> OLLAMA
    
    Args:
        model_name: LLM名称字符串
    
    Returns:
        ModelType: 推断出的LLM类型枚举值
    """
    model_name_lower = model_name.lower()
    
    if model_name_lower.startswith("gpt"):
        return ModelType.OPENAI
    elif model_name_lower.startswith("claude"):
        return ModelType.ANTHROPIC
    elif "qwen" in model_name_lower:
        return ModelType.QWEN
    elif "/" in model_name_lower:
        return ModelType.HUGGINGFACE
    else:
        return ModelType.OLLAMA


def create_model(
    model_name: str,
    model_type: Optional[ModelType] = None,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    **kwargs
) -> BaseLLM:
    """创建LLM实例（必须显式指定LLM名称）
    
    提供便捷的LLM创建接口，支持自动推断LLM类型
    自动从环境变量读取API密钥和基础URL（如果未显式提供）
    
    Args:
        model_name: LLM名称（必需参数）
        model_type: LLM类型（可选，未指定时自动推断）
        api_key: API密钥（可选，未指定时从环境变量读取）
        base_url: API基础URL（可选，未指定时使用默认值或从环境变量读取）
        **kwargs: 其他配置参数，如temperature、max_tokens等
    
    Returns:
        BaseLLM: 创建的LLM实例
    
    Raises:
        ValueError: LLM名称为空或不支持的LLM类型
    
    Examples:
        >>> model = create_model("gpt-4")
        >>> model = create_model("claude-3-opus", api_key="sk-...")
        >>> model = create_model("qwen-turbo", temperature=0.7)
    """
    if not model_name:
        raise ValueError("LLM名称是必需参数")
    
    if model_type is None:
        model_type = infer_model_type(model_name)
    
    if model_type == ModelType.OPENAI:
        config = ModelConfig(
            model_name=model_name,
            model_type=ModelType.OPENAI,
            api_key=api_key or os.getenv("OPENAI_API_KEY"),
            base_url=base_url or os.getenv("OPENAI_BASE_URL"),
            **kwargs
        )
    elif model_type == ModelType.ANTHROPIC:
        config = ModelConfig(
            model_name=model_name,
            model_type=ModelType.ANTHROPIC,
            api_key=api_key or os.getenv("ANTHROPIC_API_KEY"),
            **kwargs
        )
    elif model_type == ModelType.QWEN:
        config = ModelConfig(
            model_name=model_name,
            model_type=ModelType.QWEN,
            api_key=api_key or os.getenv("DASHSCOPE_API_KEY"),
            base_url=base_url or os.getenv("DASHSCOPE_API_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"),
            **kwargs
        )
    elif model_type == ModelType.HUGGINGFACE:
        config = ModelConfig(
            model_name=model_name,
            model_type=ModelType.HUGGINGFACE,
            **kwargs
        )
    elif model_type == ModelType.OLLAMA:
        config = ModelConfig(
            model_name=model_name,
            model_type=ModelType.OLLAMA,
            base_url=base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            **kwargs
        )
    else:
        raise ValueError(f"不支持的LLM类型: {model_type}")
    
    return create_llm(config)


def quick_chat(
    prompt: str,
    model_name: str,
    model_type: Optional[ModelType] = None,
    **kwargs
) -> ModelResponse:
    """快速聊天接口
    
    提供简化的单次对话接口，自动创建LLM并调用
    适合快速测试和简单场景使用
    
    Args:
        prompt: 提示文本
        model_name: LLM名称（必需参数）
        model_type: LLM类型（可选，未指定时自动推断）
        **kwargs: 额外参数，如temperature、max_tokens等
    
    Returns:
        ModelResponse: LLM响应对象
    
    Raises:
        ValueError: LLM名称为空
    
    Examples:
        >>> response = quick_chat("你好", "gpt-4")
        >>> print(response.content)
    """
    if not model_name:
        raise ValueError("LLM名称是必需参数")
    
    model = create_model(model_name=model_name, model_type=model_type, **kwargs)
    return model.complete(prompt, **kwargs)


def quick_chat_stream(
    prompt: str,
    model_name: str,
    model_type: Optional[ModelType] = None,
    **kwargs
) -> Generator[str, None, None]:
    """快速流式聊天接口
    
    提供简化的流式对话接口，自动创建LLM并调用
    适合需要实时显示响应的场景
    
    Args:
        prompt: 提示文本
        model_name: LLM名称（必需参数）
        model_type: LLM类型（可选，未指定时自动推断）
        **kwargs: 额外参数，如temperature、max_tokens等
    
    Yields:
        str: 流式响应的文本片段
    
    Raises:
        ValueError: LLM名称为空
    
    Examples:
        >>> for chunk in quick_chat_stream("讲个笑话", "gpt-4"):
        ...     print(chunk, end='', flush=True)
    """
    if not model_name:
        raise ValueError("LLM名称是必需参数")
    
    model = create_model(model_name=model_name, model_type=model_type, **kwargs)
    return model.stream_chat([Message(role="user", content=prompt)], **kwargs)
