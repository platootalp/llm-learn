"""
OpenAI LLM提供商实现
支持OpenAI GPT系列LLM的调用，包括GPT-3.5、GPT-4等
支持标准API调用和流式响应
"""

import time
from typing import List, Union, Generator

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

from ..base_llm import (
    BaseLLM, ModelConfig, Message, ModelResponse,
    BaseMessage
)


class OpenAILLM(BaseLLM):
    """OpenAI LLM提供商
    
    支持OpenAI GPT系列LLM的调用，包括GPT-3.5、GPT-4等
    支持标准API调用和流式响应
    
    Attributes:
        client: OpenAI客户端实例
        config: LLM配置对象
    """

    def __init__(self, config: ModelConfig):
        """初始化OpenAI LLM实例
        
        Args:
            config: LLM配置对象，必须包含api_key
        
        Raises:
            RuntimeError: 未安装openai库
        """
        if OpenAI is None:
            raise RuntimeError("请安装openai库: pip install openai")

        super().__init__(config)
        self.client = OpenAI(
            api_key=config.api_key,
            base_url=config.base_url,
            timeout=config.timeout,
            max_retries=config.max_retries
        )

    def chat(self, messages: List[Union[Message, BaseMessage]], **kwargs) -> ModelResponse:
        """调用OpenAI聊天接口
        
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
            response = self.client.chat.completions.create(
                model=self.config.model_name,
                messages=self._convert_messages_to_dict(messages),
                temperature=kwargs.get("temperature", self.config.temperature),
                max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
                top_p=kwargs.get("top_p", self.config.top_p),
                frequency_penalty=kwargs.get("frequency_penalty", self.config.frequency_penalty),
                presence_penalty=kwargs.get("presence_penalty", self.config.presence_penalty),
                **self.config.additional_params,
                **kwargs
            )

            latency = time.time() - start_time
            tokens = response.usage.total_tokens if response.usage else 0

            self.update_metrics(latency, tokens, True)

            return ModelResponse(
                content=response.choices[0].message.content,
                model=response.model,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                    "total_tokens": tokens
                },
                finish_reason=response.choices[0].finish_reason,
                latency=latency
            )
        except Exception as e:
            latency = time.time() - start_time
            self.update_metrics(latency, 0, False)
            raise RuntimeError(f"OpenAI API调用失败: {str(e)}")

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
            stream = self.client.chat.completions.create(
                model=self.config.model_name,
                messages=self._convert_messages_to_dict(messages),
                temperature=kwargs.get("temperature", self.config.temperature),
                max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
                top_p=kwargs.get("top_p", self.config.top_p),
                stream=True,
                **self.config.additional_params,
                **kwargs
            )

            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            raise RuntimeError(f"OpenAI流式调用失败: {str(e)}")

    def _convert_messages_to_dict(self, messages: List[Union[Message, BaseMessage]]) -> List[dict]:
        """将消息列表转换为字典格式
        
        Args:
            messages: 消息列表，支持Message或BaseMessage类型
        
        Returns:
            包含role和content的字典列表
        """
        return [m.to_dict() if hasattr(m, 'to_dict') else {"role": m.role, "content": m.content} for m in messages]
