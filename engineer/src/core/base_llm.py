"""
LLM基础抽象类和统一接口
定义所有LLM提供商和本地LLM必须实现的标准接口
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import time


class ModelType(Enum):
    """LLM类型枚举"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    QWEN = "qwen"
    HUGGINGFACE = "huggingface"
    OLLAMA = "ollama"


@dataclass
class ModelConfig:
    """LLM配置类
    
    用于配置LLM的各种参数，包括LLM名称、类型、API密钥、生成参数等
    
    Attributes:
        model_name: LLM名称
        model_type: LLM类型
        api_key: API密钥（可选）
        base_url: API基础URL（可选）
        temperature: 温度参数，控制输出的随机性，范围0-2，默认0.7
        max_tokens: 最大生成token数，默认2000
        top_p: 核采样参数，范围0-1，默认0.9
        top_k: 采样参数，默认None
        frequency_penalty: 频率惩罚，默认0.0
        presence_penalty: 存在惩罚，默认0.0
        timeout: 请求超时时间（秒），默认60
        max_retries: 最大重试次数，默认3
        additional_params: 额外参数字典
    """
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


class BaseMessage:
    """基础消息类
    
    所有消息类型的基类，包含消息内容和角色信息
    
    Attributes:
        content: 消息内容
        role: 消息角色（system、user、assistant等）
    """
    def __init__(self, content: str, role: str):
        self.content = content
        self.role = role
    
    def to_dict(self) -> Dict[str, str]:
        """转换为字典格式
        
        Returns:
            包含role和content的字典
        """
        return {"role": self.role, "content": self.content}


class SystemMessage(BaseMessage):
    """系统消息类
    
    用于设置系统级别的指令或行为
    
    Attributes:
        content: 系统消息内容
    """
    def __init__(self, content: str):
        super().__init__(content, "system")


class HumanMessage(BaseMessage):
    """人类消息类
    
    表示用户发送的消息
    
    Attributes:
        content: 用户消息内容
    """
    def __init__(self, content: str):
        super().__init__(content, "user")


class AIMessage(BaseMessage):
    """AI消息类
    
    表示AI助手的回复
    
    Attributes:
        content: AI回复内容
    """
    def __init__(self, content: str):
        super().__init__(content, "assistant")


@dataclass
class Message:
    """消息格式（向后兼容）
    
    简单的消息数据类，用于向后兼容
    
    Attributes:
        role: 消息角色
        content: 消息内容
    """
    role: str
    content: str
    
    def to_dict(self) -> Dict[str, str]:
        """转换为字典格式
        
        Returns:
            包含role和content的字典
        """
        return {"role": self.role, "content": self.content}


@dataclass
class ModelResponse:
    """LLM响应类
    
    封装LLM的响应信息
    
    Attributes:
        content: 响应内容
        model: 使用的LLM名称
        usage: token使用情况字典，包含prompt_tokens、completion_tokens、total_tokens
        finish_reason: 结束原因（如stop、length等）
        latency: 响应延迟（秒）
        metadata: 额外的元数据字典
    """
    content: str
    model: str
    usage: Dict[str, int] = field(default_factory=dict)
    finish_reason: Optional[str] = None
    latency: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_aimessage(self) -> AIMessage:
        """转换为AIMessage对象
        
        Returns:
            包含响应内容的AIMessage对象
        """
        return AIMessage(content=self.content)


@dataclass
class ModelMetrics:
    """LLM性能指标类
    
    记录LLM的性能统计数据
    
    Attributes:
        model_name: LLM名称
        avg_latency: 平均延迟（秒）
        avg_tokens_per_second: 平均生成速度（tokens/秒）
        success_rate: 成功率（0-1）
        total_calls: 总调用次数
        error_count: 错误次数
        last_updated: 最后更新时间戳
    """
    model_name: str
    avg_latency: float
    avg_tokens_per_second: float
    success_rate: float
    total_calls: int
    error_count: int
    last_updated: float


class BaseLLM(ABC):
    """LLM基础抽象类
    
    所有LLM提供商必须继承此类并实现抽象方法。
    提供统一的接口用于LLM调用、性能指标管理等功能。
    
    Attributes:
        config: LLM配置对象
        metrics: LLM性能指标
    """
    
    def __init__(self, config: ModelConfig):
        """初始化LLM实例
        
        Args:
            config: LLM配置对象
        """
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
    def chat(self, messages: List[Union[Message, BaseMessage]], **kwargs) -> ModelResponse:
        """聊天接口（抽象方法）
        
        子类必须实现此方法以支持多轮对话
        
        Args:
            messages: 消息列表，支持Message或BaseMessage类型
            **kwargs: 额外参数，如temperature、max_tokens等
        
        Returns:
            ModelResponse对象，包含响应内容和使用信息
        
        Raises:
            NotImplementedError: 子类未实现此方法
        """
        pass

    def invoke(self, messages: List[Union[Message, BaseMessage]], **kwargs) -> AIMessage:
        """调用LLM（LangChain风格接口）
        
        提供与LangChain兼容的接口，返回AIMessage对象
        
        Args:
            messages: 消息列表，支持SystemMessage、HumanMessage、AIMessage
            **kwargs: 额外参数
        
        Returns:
            AIMessage对象，包含AI回复内容
        """
        response = self.chat(messages, **kwargs)
        return response.to_aimessage()

    @abstractmethod
    def complete(self, prompt: str, **kwargs) -> ModelResponse:
        """文本补全接口（抽象方法）
        
        子类必须实现此方法以支持单轮文本补全
        
        Args:
            prompt: 提示文本
            **kwargs: 额外参数
        
        Returns:
            ModelResponse对象，包含响应内容和使用信息
        
        Raises:
            NotImplementedError: 子类未实现此方法
        """
        pass

    @abstractmethod
    def stream_chat(self, messages: List[Message], **kwargs):
        """流式聊天接口（抽象方法）
        
        子类必须实现此方法以支持流式响应
        
        Args:
            messages: 消息列表
            **kwargs: 额外参数
        
        Yields:
            str: 流式响应的文本片段
        
        Raises:
            NotImplementedError: 子类未实现此方法
        """
        pass

    def update_metrics(self, latency: float, tokens: int, success: bool):
        """更新性能指标
        
        根据最新的调用结果更新LLM的性能统计数据
        
        Args:
            latency: 本次调用的延迟（秒）
            tokens: 本次调用的token数
            success: 本次调用是否成功
        """
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
        """获取性能指标
        
        Returns:
            ModelMetrics对象，包含当前的性能统计数据
        """
        return self.metrics

    def reset_metrics(self):
        """重置性能指标
        
        将所有性能统计重置为初始值
        """
        self.metrics = ModelMetrics(
            model_name=self.config.model_name,
            avg_latency=0.0,
            avg_tokens_per_second=0.0,
            success_rate=1.0,
            total_calls=0,
            error_count=0,
            last_updated=time.time()
        )
