"""
QwenLLM API 客户端封装
使用 OpenAI 风格客户端封装，调用 dashscope API
"""
from typing import List
from openai import OpenAI


class QwenLLM:
    """
    封装百炼大模型 qwen-plus 调用
    使用 OpenAI 风格客户端封装，调用 dashscope API
    """

    def __init__(self, api_key: str, base_url: str, model_name: str = "qwen-plus"):
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,
        )
        self.model_name = model_name

    def think(self, messages: List[dict]) -> str:
        """
        调用 qwen-plus 模型进行推理
        """
        try:
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages
            )
            return completion.choices[0].message.content
        except Exception as e:
            raise Exception(f"API 请求失败：{e}")
