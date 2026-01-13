"""
Anthropic Claude LLM提供商实现
支持Anthropic Claude系列LLM的调用，包括Claude-3、Claude-2等
支持标准API调用和流式响应
"""

import time
from typing import List, Union, Generator

try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None

from ..base_llm import (
    BaseLLM, ModelConfig, Message, ModelResponse,
    BaseMessage
)


class AnthropicLLM(BaseLLM):
    """Anthropic Claude LLM提供商
    
    支持Anthropic Claude系列LLM的调用，包括Claude-3、Claude-2等
    支持标准API调用和流式响应
    
    Attributes:
        client: Anthropic客户端实例
        config: LLM配置对象
    """

    def __init__(self, config: ModelConfig):
        """初始化Anthropic LLM实例
        
        Args:
            config: LLM配置对象，必须包含api_key
        
        Raises:
            RuntimeError: 未安装anthropic库
        """
        if Anthropic is None:
            raise RuntimeError("请安装anthropic库: pip install anthropic")

        super().__init__(config)
        self.client = Anthropic(
            api_key=config.api_key,
            timeout=config.timeout,
            max_retries=config.max_retries
        )

    def chat(self, messages: List[Union[Message, BaseMessage]], **kwargs) -> ModelResponse:
        """调用Anthropic聊天接口
        
        Args:
            messages: 消息列表
            **kwargs: 额外参数，如temperature、max_tokens等
        
        Returns:
            ModelResponse对象，包含响应内容和使用信息
        
        Raises:
            RuntimeError: API调用失败
        """
        start_time = time.time()
        try:
            response = self.client.messages.create(
                model=self.config.model_name,
                messages=self._convert_messages_to_dict(messages),
                temperature=kwargs.get("temperature", self.config.temperature),
                max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
                top_p=kwargs.get("top_p", self.config.top_p),
                **self.config.additional_params,
                **kwargs
            )

            latency = time.time() - start_time
            tokens = response.usage.input_tokens + response.usage.output_tokens

            self.update_metrics(latency, tokens, True)

            return ModelResponse(
                content=response.content[0].text,
                model=response.model,
                usage={
                    "prompt_tokens": response.usage.input_tokens,
                    "completion_tokens": response.usage.output_tokens,
                    "total_tokens": tokens
                },
                finish_reason=response.stop_reason,
                latency=latency
            )
        except Exception as e:
            latency = time.time() - start_time
            self.update_metrics(latency, 0, False)
            raise RuntimeError(f"Anthropic API调用失败: {str(e)}")

    def complete(self, prompt: str, **kwargs) -> ModelResponse:
        """文本补全接口
        
        Args:
            prompt: 提示文本
            **kwargs: 额外参数
        
        Returns:
            ModelResponse对象，包含响应内容和使用信息
        """
        messages = [Message(role="user", content=prompt)]
        return self.chat(messages, **kwargs)

    def stream_chat(self, messages: List[Union[Message, BaseMessage]], **kwargs) -> Generator[str, None, None]:
        """流式聊天接口
        
        Args:
            messages: 消息列表
            **kwargs: 额外参数
        
        Yields:
            str: 流式响应的文本片段
        
        Raises:
            RuntimeError: 流式调用失败
        """
        try:
            with self.client.messages.stream(
                    model=self.config.model_name,
                    messages=self._convert_messages_to_dict(messages),
                    temperature=kwargs.get("temperature", self.config.temperature),
                    max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
                    **self.config.additional_params,
                    **kwargs
            ) as stream:
                for text in stream.text_stream:
                    yield text
        except Exception as e:
            raise RuntimeError(f"Anthropic流式调用失败: {str(e)}")

    def _convert_messages_to_dict(self, messages: List[Union[Message, BaseMessage]]) -> List[dict]:
        """将消息列表转换为字典格式
        
        Args:
            messages: 消息列表，支持Message或BaseMessage类型
        
        Returns:
            包含role和content的字典列表
        """
        return [m.to_dict() if hasattr(m, 'to_dict') else {"role": m.role, "content": m.content} for m in messages]
