"""
Hugging Face本地LLM提供商实现
支持在本地部署和运行Hugging Face Transformers库中的开源LLM
支持自动检测设备（CPU/GPU）并优化LLM加载
支持因果语言LLM（CausalLM）和序列到序列LLM（Seq2SeqLM）
"""

import time
from typing import List, Union, Generator

try:
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM, AutoModelForSeq2SeqLM

    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

from ..base_llm import (
    BaseLLM, ModelConfig, Message, ModelResponse,
    BaseMessage
)


class HuggingFaceLLM(BaseLLM):
    """Hugging Face本地LLM提供商
    
    支持在本地部署和运行Hugging Face Transformers库中的开源LLM
    支持自动检测设备（CPU/GPU）并优化LLM加载
    支持因果语言LLM（CausalLM）和序列到序列LLM（Seq2SeqLM）
    
    Attributes:
        model: 加载的PyTorch LLM实例
        tokenizer: LLM对应的分词器
        device: 运行设备（cuda或cpu）
        config: LLM配置对象
    """

    def __init__(self, config: ModelConfig):
        """初始化Hugging Face LLM实例
        
        自动检测可用设备（优先使用GPU），加载LLM和分词器
        支持自动选择LLM类型（CausalLM或Seq2SeqLM）
        
        Args:
            config: LLM配置对象，model_name为Hugging Face LLM标识符
        
        Raises:
            RuntimeError: 未安装transformers和torch库
        """
        if not TRANSFORMERS_AVAILABLE:
            raise RuntimeError("请安装transformers和torch库: pip install transformers torch")

        super().__init__(config)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"[HuggingFace] 使用设备: {self.device}")

        print(f"[HuggingFace] 正在加载LLM: {config.model_name}")
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

        print(f"[HuggingFace] LLM加载完成")

    def chat(self, messages: List[Union[Message, BaseMessage]], **kwargs) -> ModelResponse:
        """调用Hugging Face LLM进行对话
        
        将消息格式化为提示词，使用LLM生成响应
        支持温度、top_p、top_k等生成参数
        
        Args:
            messages: 消息列表
            **kwargs: 额外参数，如max_tokens、temperature、top_p、top_k等
        
        Returns:
            ModelResponse对象，包含响应内容和使用信息
        
        Raises:
            RuntimeError: LLM调用失败
        """
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
            raise RuntimeError(f"Hugging Face LLM调用失败: {str(e)}")

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
        
        生成完整响应后逐字符返回（模拟流式输出）
        
        Args:
            messages: 消息列表
            **kwargs: 额外参数
        
        Yields:
            str: 流式响应的文本片段（逐字符）
        """
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

    def _format_messages(self, messages: List[Union[Message, BaseMessage]]) -> str:
        """格式化消息为提示词
        
        优先使用分词器的chat_template（如果可用）
        否则使用简单的格式化规则
        
        Args:
            messages: 消息列表
        
        Returns:
            str: 格式化后的提示词字符串
        """
        if hasattr(self.tokenizer, 'chat_template') and self.tokenizer.chat_template:
            return self.tokenizer.apply_chat_template(
                self._convert_messages_to_dict(messages),
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

    def _convert_messages_to_dict(self, messages: List[Union[Message, BaseMessage]]) -> List[dict]:
        """将消息列表转换为字典格式
        
        Args:
            messages: 消息列表，支持Message或BaseMessage类型
        
        Returns:
            包含role和content的字典列表
        """
        return [m.to_dict() if hasattr(m, 'to_dict') else {"role": m.role, "content": m.content} for m in messages]
