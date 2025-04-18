from fastapi import APIRouter, Depends, HTTPException, Header
from typing import Optional

from app.core.config import settings
from app.models.schemas import ChatRequest, ChatResponse, ModelsResponse
from app.services.llm import llm_service

router = APIRouter()


async def verify_api_key(api_key: Optional[str] = Header(None)):
    """验证API密钥中间件"""
    if settings.API_KEY and (not api_key or api_key != settings.API_KEY):
        raise HTTPException(status_code=401, detail="无效的API密钥")
    return api_key


@router.post("/chat", response_model=ChatResponse, dependencies=[Depends(verify_api_key)])
async def chat(request: ChatRequest):
    """聊天接口
    
    处理聊天请求，调用LLM服务生成响应
    """
    try:
        result = await llm_service.generate_response(
            messages=request.messages,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        return ChatResponse(
            response=result["response"],
            usage=result.get("usage")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理请求时出错: {str(e)}")


@router.get("/models", response_model=ModelsResponse, dependencies=[Depends(verify_api_key)])
async def get_models():
    """获取可用模型列表"""
    try:
        models = llm_service.get_available_models()
        return ModelsResponse(models=models)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取模型列表时出错: {str(e)}") 