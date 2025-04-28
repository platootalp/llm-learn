# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.core.config import settings
from app.api.routes import router as api_router

# 创建FastAPI应用
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    debug=settings.DEBUG
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含API路由
app.include_router(api_router, prefix=settings.API_V1_PREFIX)

# 健康检查路由
@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/")
async def root():
    """
    API根路径，返回服务信息
    """
    return {
        "service": settings.PROJECT_NAME,
        "version": "1.0.0",
        "documentation": f"/docs",
        "api_prefix": settings.API_V1_PREFIX
    }


if __name__ == "__main__":
    # 设置日志
    logger.info(f"启动 {settings.PROJECT_NAME}")
    
    # 获取端口号
    port = int(os.getenv("API_PORT", 8000))
    
    # 启动服务
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=settings.DEBUG)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
