"""
Ollama本地LLM提供商实现
支持通过Ollama在本地部署和运行开源大语言LLM
使用OpenAI兼容API接口与Ollama服务通信
支持列出和管理本地安装的Ollama LLM
"""

import time
import requests
from typing import List, Generator

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

from ..base_llm import (
    BaseLLM, ModelConfig, Message, ModelResponse
)


class OllamaLLM(BaseLLM):
    """Ollama本地LLM提供商
    
    支持通过Ollama在本地部署和运行开源大语言LLM
    使用OpenAI兼容API接口与Ollama服务通信
    支持列出和管理本地安装的Ollama LLM
    
    Attributes:
        client: OpenAI客户端实例（用于调用Ollama API）
        config: LLM配置对象
    """

    def __init__(self, config: ModelConfig):
        """初始化Ollama LLM实例
        
        连接到本地Ollama服务（默认为http://localhost:11434）
        
        Args:
            config: LLM配置对象，model_name为Ollama LLM名称
        
        Raises:
            RuntimeError: 未安装openai库
        """
        if OpenAI is None:
            raise RuntimeError("请安装openai库: pip install openai")
        
        super().__init__(config)
        self.client = OpenAI(
            api_key="ollama",
            base_url=config.base_url or "http://localhost:11434/v1",
            timeout=config.timeout,
            max_retries=config.max_retries
        )

    def chat(self, messages: List[Message], **kwargs) -> ModelResponse:
        """调用Ollama LLM进行对话
        
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
                messages=[{"role": m.role, "content": m.content} for m in messages],
                temperature=kwargs.get("temperature", self.config.temperature),
                max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
                top_p=kwargs.get("top_p", self.config.top_p),
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
            raise RuntimeError(f"Ollama API调用失败: {str(e)}")

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

    def stream_chat(self, messages: List[Message], **kwargs) -> Generator[str, None, None]:
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
                messages=[{"role": m.role, "content": m.content} for m in messages],
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
            raise RuntimeError(f"Ollama流式调用失败: {str(e)}")

    def list_models(self) -> List[str]:
        """列出所有可用的Ollama LLM
        
        通过Ollama API获取本地已安装的LLM列表
        
        Returns:
            List[str]: LLM名称列表
        
        Raises:
            RuntimeError: 获取LLM列表失败
        """
        try:
            response = requests.get(f"{self.client.base_url.replace('/v1', '')}/api/tags", timeout=10)
            response.raise_for_status()
            result = response.json()
            return [model['name'] for model in result.get('models', [])]
        except Exception as e:
            raise RuntimeError(f"获取Ollama LLM列表失败: {str(e)}")
