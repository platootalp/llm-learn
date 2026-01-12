"""
LLM集成统一接口
整合所有LLM集成功能，提供统一的调用接口
"""

from typing import List, Optional, Dict, Any, Generator
import os

from dotenv import load_dotenv

from .base_llm import (
    BaseLLM, ModelConfig, Message, ModelResponse, ModelType, ModelMetrics
)
from .llm_providers import (
    OpenAILLM, AnthropicLLM, QwenLLM, HuggingFaceLLM, OllamaLLM, create_llm
)
from .model_detector import ModelDetector, DetectedModel, auto_detect_models, get_best_available_model
load_dotenv()

class LLMManager:
    """LLM管理器，统一管理所有LLM实例"""

    def __init__(self):
        self.models: Dict[str, BaseLLM] = {}
        self.detector = ModelDetector()
        self.current_model: Optional[BaseLLM] = None

    def detect_models(self) -> List[DetectedModel]:
        """检测所有可用的模型"""
        return self.detector.get_available_models()

    def print_detected_models(self):
        """打印检测到的模型信息"""
        self.detector.print_detected_models()

    def create_model(
        self,
        model_name: Optional[str] = None,
        model_type: Optional[ModelType] = None,
        config: Optional[ModelConfig] = None,
        auto_detect: bool = True
    ) -> BaseLLM:
        """
        创建LLM实例
        :param model_name: 模型名称
        :param model_type: 模型类型
        :param config: 模型配置
        :param auto_detect: 是否自动检测
        :return: LLM实例
        """
        if config:
            return self._create_model_from_config(config)
        
        if auto_detect:
            detected = self.detector.get_best_model(model_type.value if model_type else None)
            if detected:
                return self._create_model_from_config(detected.config)
        
        if model_type is None:
            model_type = ModelType.QWEN
        
        if model_type == ModelType.OPENAI:
            config = ModelConfig(
                model_name=model_name or "gpt-3.5-turbo",
                model_type=ModelType.OPENAI,
                api_key=os.getenv("OPENAI_API_KEY")
            )
        elif model_type == ModelType.ANTHROPIC:
            config = ModelConfig(
                model_name=model_name or "claude-3-sonnet-20240229",
                model_type=ModelType.ANTHROPIC,
                api_key=os.getenv("ANTHROPIC_API_KEY")
            )
        elif model_type == ModelType.QWEN:
            config = ModelConfig(
                model_name=model_name or "qwen-plus",
                model_type=ModelType.QWEN,
                api_key=os.getenv("DASHSCOPE_API_KEY")
            )
        elif model_type == ModelType.HUGGINGFACE:
            config = ModelConfig(
                model_name=model_name or "gpt2",
                model_type=ModelType.HUGGINGFACE
            )
        elif model_type == ModelType.OLLAMA:
            config = ModelConfig(
                model_name=model_name or "llama2",
                model_type=ModelType.OLLAMA
            )
        else:
            raise ValueError(f"不支持的模型类型: {model_type}")
        
        return self._create_model_from_config(config)

    def _create_model_from_config(self, config: ModelConfig) -> BaseLLM:
        """根据配置创建模型"""
        model_key = f"{config.model_type.value}:{config.model_name}"
        
        if model_key in self.models:
            return self.models[model_key]
        
        model = create_llm(config)
        self.models[model_key] = model
        return model

    def set_current_model(self, model: BaseLLM):
        """设置当前使用的模型"""
        self.current_model = model

    def get_current_model(self) -> BaseLLM:
        """获取当前模型"""
        if not self.current_model:
            self.current_model = self.create_model(auto_detect=True)
        return self.current_model

    def chat(
        self,
        messages: List[Message],
        model: Optional[BaseLLM] = None,
        **kwargs
    ) -> ModelResponse:
        """
        聊天接口
        :param messages: 消息列表
        :param model: 指定模型，不指定则使用当前模型
        :param kwargs: 额外参数
        :return: 模型响应
        """
        llm = model or self.get_current_model()
        return llm.chat(messages, **kwargs)

    def complete(
        self,
        prompt: str,
        model: Optional[BaseLLM] = None,
        **kwargs
    ) -> ModelResponse:
        """
        文本补全接口
        :param prompt: 提示文本
        :param model: 指定模型，不指定则使用当前模型
        :param kwargs: 额外参数
        :return: 模型响应
        """
        llm = model or self.get_current_model()
        return llm.complete(prompt, **kwargs)

    def stream_chat(
        self,
        messages: List[Message],
        model: Optional[BaseLLM] = None,
        **kwargs
    ) -> Generator[str, None, None]:
        """
        流式聊天接口
        :param messages: 消息列表
        :param model: 指定模型，不指定则使用当前模型
        :param kwargs: 额外参数
        :return: 流式响应生成器
        """
        llm = model or self.get_current_model()
        return llm.stream_chat(messages, **kwargs)

    def get_model_metrics(self, model: Optional[BaseLLM] = None) -> ModelMetrics:
        """获取模型性能指标"""
        llm = model or self.get_current_model()
        return llm.metrics

    def list_models(self) -> List[str]:
        """列出所有已加载的模型"""
        return list(self.models.keys())

    def remove_model(self, model_key: str):
        """移除模型"""
        if model_key in self.models:
            del self.models[model_key]

    def clear_models(self):
        """清除所有模型"""
        self.models.clear()
        self.current_model = None


def create_llm_manager() -> LLMManager:
    """
    创建LLM管理器
    :return: LLM管理器实例
    """
    return LLMManager()


def quick_chat(
    prompt: str,
    model_type: Optional[ModelType] = None,
    model_name: Optional[str] = None,
    **kwargs
) -> ModelResponse:
    """
    快速聊天接口
    :param prompt: 提示文本
    :param model_type: 模型类型
    :param model_name: 模型名称
    :param kwargs: 额外参数
    :return: 模型响应
    """
    manager = create_llm_manager()
    model = manager.create_model(model_name=model_name, model_type=model_type, auto_detect=True)
    return manager.complete(prompt, model=model, **kwargs)


def quick_chat_stream(
    prompt: str,
    model_type: Optional[ModelType] = None,
    model_name: Optional[str] = None,
    **kwargs
) -> Generator[str, None, None]:
    """
    快速流式聊天接口
    :param prompt: 提示文本
    :param model_type: 模型类型
    :param model_name: 模型名称
    :param kwargs: 额外参数
    :return: 流式响应生成器
    """
    manager = create_llm_manager()
    model = manager.create_model(model_name=model_name, model_type=model_type, auto_detect=True)
    return manager.stream_chat([Message(role="user", content=prompt)], model=model, **kwargs)
