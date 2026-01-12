"""
LLM提供商实现
支持多供应商模型集成（OpenAI、Anthropic、通义千问）和本地模型部署（Hugging Face、Ollama）
"""

import time
import requests
import json
from typing import List, Dict, Any, Optional, Generator
import warnings

warnings.filterwarnings("ignore", category=UserWarning)

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    from anthropic import Anthropic
except ImportError:
    Anthropic = None

try:
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM, AutoModelForSeq2SeqLM

    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

from .base_llm import (
    BaseLLM, ModelConfig, Message, ModelResponse, ModelType
)


class OpenAILLM(BaseLLM):
    """OpenAI LLM提供商"""

    def __init__(self, config: ModelConfig):
        if OpenAI is None:
            raise RuntimeError("请安装openai库: pip install openai")

        super().__init__(config)
        self.client = OpenAI(
            api_key=config.api_key,
            base_url=config.base_url,
            timeout=config.timeout,
            max_retries=config.max_retries
        )

    def chat(self, messages: List[Message], **kwargs) -> ModelResponse:
        start_time = time.time()
        try:
            response = self.client.chat.completions.create(
                model=self.config.model_name,
                messages=[{"role": m.role, "content": m.content} for m in messages],
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
        messages = [Message(role="user", content=prompt)]
        return self.chat(messages, **kwargs)

    def stream_chat(self, messages: List[Message], **kwargs) -> Generator[str, None, None]:
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
            raise RuntimeError(f"OpenAI流式调用失败: {str(e)}")


class AnthropicLLM(BaseLLM):
    """Anthropic Claude LLM提供商"""

    def __init__(self, config: ModelConfig):
        if Anthropic is None:
            raise RuntimeError("请安装anthropic库: pip install anthropic")

        super().__init__(config)
        self.client = Anthropic(
            api_key=config.api_key,
            timeout=config.timeout,
            max_retries=config.max_retries
        )

    def chat(self, messages: List[Message], **kwargs) -> ModelResponse:
        start_time = time.time()
        try:
            response = self.client.messages.create(
                model=self.config.model_name,
                messages=[{"role": m.role, "content": m.content} for m in messages],
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
        messages = [Message(role="user", content=prompt)]
        return self.chat(messages, **kwargs)

    def stream_chat(self, messages: List[Message], **kwargs) -> Generator[str, None, None]:
        try:
            with self.client.messages.stream(
                    model=self.config.model_name,
                    messages=[{"role": m.role, "content": m.content} for m in messages],
                    temperature=kwargs.get("temperature", self.config.temperature),
                    max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
                    **self.config.additional_params,
                    **kwargs
            ) as stream:
                for text in stream.text_stream:
                    yield text
        except Exception as e:
            raise RuntimeError(f"Anthropic流式调用失败: {str(e)}")


class QwenLLM(BaseLLM):
    """通义千问 LLM提供商"""

    def __init__(self, config: ModelConfig):
        if OpenAI is None:
            raise RuntimeError("请安装openai库: pip install openai")
        
        super().__init__(config)
        self.client = OpenAI(
            api_key=config.api_key,
            base_url=config.base_url or "https://dashscope.aliyuncs.com/compatible-mode/v1",
            timeout=config.timeout,
            max_retries=config.max_retries
        )

    def chat(self, messages: List[Message], **kwargs) -> ModelResponse:
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
            raise RuntimeError(f"通义千问API调用失败: {str(e)}")

    def complete(self, prompt: str, **kwargs) -> ModelResponse:
        messages = [Message(role="user", content=prompt)]
        return self.chat(messages, **kwargs)

    def stream_chat(self, messages: List[Message], **kwargs) -> Generator[str, None, None]:
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
            raise RuntimeError(f"通义千问流式调用失败: {str(e)}")


class HuggingFaceLLM(BaseLLM):
    """Hugging Face本地模型"""

    def __init__(self, config: ModelConfig):
        if not TRANSFORMERS_AVAILABLE:
            raise RuntimeError("请安装transformers和torch库: pip install transformers torch")

        super().__init__(config)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"[HuggingFace] 使用设备: {self.device}")

        print(f"[HuggingFace] 正在加载模型: {config.model_name}")
        self.tokenizer = AutoTokenizer.from_pretrained(
            config.model_name,
            trust_remote_code=True
        )

        try:
            self.model = AutoModelForCausalLM.from_pretrained(
                config.model_name,
                torch_dtype=torch.float16 if self.device.type == "cuda" else torch.float32,
                device_map="auto" if self.device.type == "cuda" else None,
                trust_remote_code=True,
                low_cpu_mem_usage=True
            )
        except:
            self.model = AutoModelForSeq2SeqLM.from_pretrained(
                config.model_name,
                torch_dtype=torch.float16 if self.device.type == "cuda" else torch.float32,
                device_map="auto" if self.device.type == "cuda" else None,
                trust_remote_code=True,
                low_cpu_mem_usage=True
            )

        if self.device.type == "cpu":
            self.model = self.model.to(self.device)

        print(f"[HuggingFace] 模型加载完成")

    def chat(self, messages: List[Message], **kwargs) -> ModelResponse:
        start_time = time.time()
        try:
            prompt = self._format_messages(messages)

            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                truncation=True,
                max_length=kwargs.get("max_input_length", 4096)
            ).to(self.device)

            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=kwargs.get("max_tokens", self.config.max_tokens),
                    temperature=kwargs.get("temperature", self.config.temperature),
                    top_p=kwargs.get("top_p", self.config.top_p),
                    top_k=kwargs.get("top_k", self.config.top_k) or 50,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    **self.config.additional_params,
                    **kwargs
                )

            response_text = self.tokenizer.decode(
                outputs[0][inputs['input_ids'].shape[1]:],
                skip_special_tokens=True
            )

            latency = time.time() - start_time
            tokens = outputs.shape[1]

            self.update_metrics(latency, tokens, True)

            return ModelResponse(
                content=response_text.strip(),
                model=self.config.model_name,
                usage={
                    "prompt_tokens": inputs['input_ids'].shape[1],
                    "completion_tokens": outputs.shape[1] - inputs['input_ids'].shape[1],
                    "total_tokens": tokens
                },
                finish_reason="length",
                latency=latency
            )
        except Exception as e:
            latency = time.time() - start_time
            self.update_metrics(latency, 0, False)
            raise RuntimeError(f"Hugging Face模型调用失败: {str(e)}")

    def complete(self, prompt: str, **kwargs) -> ModelResponse:
        messages = [Message(role="user", content=prompt)]
        return self.chat(messages, **kwargs)

    def stream_chat(self, messages: List[Message], **kwargs) -> Generator[str, None, None]:
        prompt = self._format_messages(messages)

        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=kwargs.get("max_input_length", 4096)
        ).to(self.device)

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=kwargs.get("max_tokens", self.config.max_tokens),
                temperature=kwargs.get("temperature", self.config.temperature),
                top_p=kwargs.get("top_p", self.config.top_p),
                top_k=kwargs.get("top_k", self.config.top_k) or 50,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
                **self.config.additional_params,
                **kwargs
            )

        full_text = self.tokenizer.decode(
            outputs[0][inputs['input_ids'].shape[1]:],
            skip_special_tokens=True
        )

        for char in full_text:
            yield char

    def _format_messages(self, messages: List[Message]) -> str:
        """格式化消息为提示词"""
        if hasattr(self.tokenizer, 'chat_template') and self.tokenizer.chat_template:
            return self.tokenizer.apply_chat_template(
                [{"role": m.role, "content": m.content} for m in messages],
                tokenize=False,
                add_generation_prompt=True
            )
        else:
            formatted = []
            for msg in messages:
                if msg.role == "system":
                    formatted.append(f"System: {msg.content}")
                elif msg.role == "user":
                    formatted.append(f"User: {msg.content}")
                elif msg.role == "assistant":
                    formatted.append(f"Assistant: {msg.content}")
            formatted.append("Assistant:")
            return "\n".join(formatted)


class OllamaLLM(BaseLLM):
    """Ollama本地模型"""

    def __init__(self, config: ModelConfig):
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
        messages = [Message(role="user", content=prompt)]
        return self.chat(messages, **kwargs)

    def stream_chat(self, messages: List[Message], **kwargs) -> Generator[str, None, None]:
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
        """列出所有可用的Ollama模型"""
        try:
            response = requests.get(f"{self.client.base_url.replace('/v1', '')}/api/tags", timeout=10)
            response.raise_for_status()
            result = response.json()
            return [model['name'] for model in result.get('models', [])]
        except Exception as e:
            raise RuntimeError(f"获取Ollama模型列表失败: {str(e)}")


def create_llm(config: ModelConfig) -> BaseLLM:
    """
    根据配置创建对应的LLM实例
    :param config: 模型配置
    :return: LLM实例
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
        raise ValueError(f"不支持的模型类型: {config.model_type}")

    return provider_class(config)
