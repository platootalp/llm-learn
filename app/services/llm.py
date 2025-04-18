from typing import Dict, List, Optional, Any
from loguru import logger

from langchain.chat_models import ChatOpenAI
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)

from app.core.config import settings
from app.models.schemas import Message, TokenUsage


class LLMService:
    """LLM服务类"""
    
    def __init__(self):
        # 环境变量检查
        if not settings.QWEN_API_KEY:
            logger.warning("QWEN_API_KEY 环境变量未设置。服务将无法正常工作。")
    
    def _convert_to_langchain_messages(self, messages: List[Message]) -> List[Any]:
        """将API消息转换为LangChain消息格式
        
        Args:
            messages: API消息列表
            
        Returns:
            LangChain消息列表
        """
        langchain_messages = []
        
        for message in messages:
            if message.role == "user":
                langchain_messages.append(HumanMessage(content=message.content))
            elif message.role == "assistant":
                langchain_messages.append(AIMessage(content=message.content))
            elif message.role == "system":
                langchain_messages.append(SystemMessage(content=message.content))
            else:
                logger.warning(f"未知消息角色: {message.role}，将作为用户消息处理")
                langchain_messages.append(HumanMessage(content=message.content))
                
        return langchain_messages
    
    async def generate_response(
        self,
        messages: List[Message],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """生成LLM响应
        
        Args:
            messages: 消息列表
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大生成token数
            
        Returns:
            包含响应和token使用情况的字典
        """
        model = model or settings.DEFAULT_MODEL
        temperature = temperature or settings.DEFAULT_TEMPERATURE
        max_tokens = max_tokens or settings.DEFAULT_MAX_TOKENS
        
        logger.info(f"使用模型 {model} 生成响应")
        
        try:
            langchain_messages = self._convert_to_langchain_messages(messages)

            llm = ChatOpenAI(
                model_name=settings.DEFAULT_MODEL,  # 例如 "qwen-turbo"
                openai_api_base=settings.QWEN_API_URL,
                openai_api_key=settings.QWEN_API_KEY,  # 阿里云 API Key
                temperature=temperature,
                max_tokens=max_tokens
            )
            response = await llm.agenerate(messages=[langchain_messages])
            
            # 提取结果
            first_generation = response.generations[0]
            message = first_generation[0].message
            
            # 提取token使用情况
            token_usage = None
            if response.llm_output and isinstance(response.llm_output, dict) and "token_usage" in response.llm_output:
                usage_data = response.llm_output["token_usage"]
                token_usage = TokenUsage(
                    prompt_tokens=usage_data.get("prompt_tokens", 0),
                    completion_tokens=usage_data.get("completion_tokens", 0),
                    total_tokens=usage_data.get("total_tokens", 0)
                )
            
            return {
                "response": message.content,
                "usage": token_usage
            }
            
        except Exception as e:
            logger.error(f"生成响应时出错: {str(e)}")
            raise
    
    def get_available_models(self) -> List[str]:
        """获取可用模型列表
        
        Returns:
            可用模型列表
        """
        return settings.AVAILABLE_MODELS


# 创建服务实例
llm_service = LLMService() 