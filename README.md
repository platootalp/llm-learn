# AI服务 - LangChain与FastAPI集成

这是一个基于Python的AI服务，使用LangChain与阿里云百炼大语言模型进行交互，并通过FastAPI对外提供API接口。

## 项目结构

```
.
├── README.md           # 项目说明文档
├── main.py             # FastAPI主应用入口
├── requirements.txt    # 项目依赖文件
├── .env.example        # 环境变量模板
├── app/                # 应用代码
│   ├── __init__.py     
│   ├── api/            # API路由
│   │   ├── __init__.py
│   │   └── routes.py   # API路由定义
│   ├── core/           # 核心配置
│   │   ├── __init__.py
│   │   └── config.py   # 配置管理
│   ├── models/         # 数据模型
│   │   ├── __init__.py
│   │   └── schemas.py  # 请求响应模型
│   └── services/       # 业务服务
│       ├── __init__.py
│       └── llm.py      # LLM服务
└── tests/              # 测试代码
    └── test_api.py     # API测试
```

## 功能特性

1. 支持与阿里云百炼大语言模型(如qwen-turbo, qwen-plus等)进行交互
2. 提供标准化的REST API接口
3. 支持异步请求处理
4. 支持对话历史管理
5. 支持模型参数自定义

## 环境要求

- Python 3.11或更高版本
- 阿里云百炼API密钥

## 安装步骤

1. 克隆仓库
```bash
git clone [repository-url]
cd [repository-directory]
```

2. 创建并激活虚拟环境
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate     # Windows
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 配置环境变量
   - 从`.env.example`复制创建`.env`文件
   ```bash
   cp .env.example .env
   ```
   - 编辑`.env`文件，填入您的API密钥
   ```bash
   # 必须配置
   QWEN_API_KEY=your_qwen_api_key
   
   # 可选配置
   API_PORT=8000  # API服务端口
   API_KEY=your_api_key  # 用于API认证
   OPENAI_API_KEY=your_openai_api_key  # 如需使用OpenAI模型
   ```

## 使用方法

### 启动服务

```bash
# 直接使用Python运行
python main.py

# 或使用uvicorn
uvicorn main:app --reload
```

服务将在 http://localhost:8000 启动，API文档可访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### API接口

1. `/api/chat` - 聊天接口
   - 方法: POST
   - 请求体:
     ```json
     {
       "messages": [
         {"role": "user", "content": "请介绍一下你自己"}
       ],
       "model": "qwen-turbo",  // 可选，默认使用配置中的模型
       "temperature": 0.7,      // 可选，默认0.7
       "max_tokens": 500        // 可选，默认500
     }
     ```
   - 响应:
     ```json
     {
       "response": "我是一个AI助手...",
       "usage": {
         "prompt_tokens": 10,
         "completion_tokens": 50,
         "total_tokens": 60
       }
     }
     ```

2. `/api/models` - 获取可用模型列表
   - 方法: GET
   - 响应:
     ```json
     {
       "models": ["qwen-turbo", "qwen-plus", "qwen-max"]
     }
     ```

### 测试

使用curl测试API:

```bash
# 健康检查
curl http://localhost:8000/health

# 获取可用模型列表
curl http://localhost:8000/api/models

# 发送聊天请求
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "你好，请介绍一下你自己"}]}'
```

## 常见问题

1. **API密钥错误**
   - 确保您已正确设置`.env`文件中的`QWEN_API_KEY`
   - 检查API密钥是否有效且未过期

2. **模型不可用**
   - 默认使用`qwen-turbo`，确保您的阿里云账户有权限访问该模型
   - 如需使用其他模型，请在请求中明确指定`model`参数

3. **服务启动失败**
   - 检查依赖安装是否完整
   - 检查端口8000是否被占用，可通过设置环境变量`API_PORT`修改端口

## 项目维护与改进

- [ ] 支持更多LLM提供商和模型（目前主要支持阿里云百炼）
- [ ] 添加向量数据库集成实现RAG（检索增强生成）
- [ ] 添加更完善的用户认证机制
- [ ] 实现对话历史持久化存储
- [ ] 添加流式响应支持
- [ ] 添加更多模型参数控制能力
- [ ] 优化异常处理和错误提示

## 许可证

MIT 