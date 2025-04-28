from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

class Message(BaseModel):
    """聊天消息模型"""
    role: str = Field(..., description="消息角色: user, assistant, system")
    content: str = Field(..., description="消息内容")


class ChatRequest(BaseModel):
    """聊天请求模型"""
    messages: List[Message] = Field(..., description="消息列表")
    model: Optional[str] = Field(None, description="使用的模型名称")
    temperature: Optional[float] = Field(None, description="温度参数，控制随机性")
    max_tokens: Optional[int] = Field(None, description="最大生成token数")
    stream: Optional[bool] = Field(False, description="是否使用流式响应")


class TokenUsage(BaseModel):
    """Token使用情况"""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ChatResponse(BaseModel):
    """聊天响应模型"""
    response: str = Field(..., description="AI响应内容")
    usage: Optional[TokenUsage] = Field(None, description="Token使用情况")


class ModelsResponse(BaseModel):
    """模型列表响应"""
    models: List[str] = Field(..., description="可用模型列表") 