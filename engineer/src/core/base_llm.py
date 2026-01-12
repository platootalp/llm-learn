"""
LLM基础抽象类和统一接口
定义所有LLM提供商和本地模型必须实现的标准接口
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import time


class ModelType(Enum):
    """模型类型枚举"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    QWEN = "qwen"
    HUGGINGFACE = "huggingface"
    OLLAMA = "ollama"


@dataclass
class ModelConfig:
    """模型配置"""
    model_name: str
    model_type: ModelType
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 2000
    top_p: float = 0.9
    top_k: Optional[int] = None
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    timeout: int = 60
    max_retries: int = 3
    additional_params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Message:
    """消息格式"""
    role: str
    content: str


@dataclass
class ModelResponse:
    """模型响应"""
    content: str
    model: str
    usage: Dict[str, int] = field(default_factory=dict)
    finish_reason: Optional[str] = None
    latency: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ModelMetrics:
    """模型性能指标"""
    model_name: str
    avg_latency: float
    avg_tokens_per_second: float
    success_rate: float
    total_calls: int
    error_count: int
    last_updated: float


class BaseLLM(ABC):
    """LLM基础抽象类，所有LLM提供商必须继承此类"""

    def __init__(self, config: ModelConfig):
        self.config = config
        self.metrics = ModelMetrics(
            model_name=config.model_name,
            avg_latency=0.0,
            avg_tokens_per_second=0.0,
            success_rate=1.0,
            total_calls=0,
            error_count=0,
            last_updated=time.time()
        )

    @abstractmethod
    def chat(self, messages: List[Message], **kwargs) -> ModelResponse:
        """
        聊天接口
        :param messages: 消息列表
        :param kwargs: 额外参数
        :return: 模型响应
        """
        pass

    @abstractmethod
    def complete(self, prompt: str, **kwargs) -> ModelResponse:
        """
        文本补全接口
        :param prompt: 提示文本
        :param kwargs: 额外参数
        :return: 模型响应
        """
        pass

    @abstractmethod
    def stream_chat(self, messages: List[Message], **kwargs):
        """
        流式聊天接口
        :param messages: 消息列表
        :param kwargs: 额外参数
        :return: 流式响应生成器
        """
        pass

    def update_metrics(self, latency: float, tokens: int, success: bool):
        """更新性能指标"""
        self.metrics.total_calls += 1
        if not success:
            self.metrics.error_count += 1
        
        total_calls = self.metrics.total_calls
        self.metrics.avg_latency = (
            (self.metrics.avg_latency * (total_calls - 1) + latency) / total_calls
        )
        
        if tokens > 0 and latency > 0:
            tps = tokens / latency
            self.metrics.avg_tokens_per_second = (
                (self.metrics.avg_tokens_per_second * (total_calls - 1) + tps) / total_calls
            )
        
        self.metrics.success_rate = (total_calls - self.metrics.error_count) / total_calls
        self.metrics.last_updated = time.time()

    def get_metrics(self) -> ModelMetrics:
        """获取性能指标"""
        return self.metrics

    def reset_metrics(self):
        """重置性能指标"""
        self.metrics = ModelMetrics(
            model_name=self.config.model_name,
            avg_latency=0.0,
            avg_tokens_per_second=0.0,
            success_rate=1.0,
            total_calls=0,
            error_count=0,
            last_updated=time.time()
        )
