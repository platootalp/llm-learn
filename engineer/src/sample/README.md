# LLM集成示例

本目录包含LLM集成模块的使用示例。

## 文件说明

- `llm_integration_example.py` - LLM集成功能完整使用示例

## 示例内容

该示例文件包含10个不同的使用场景：

1. **快速聊天接口** - 使用`quick_chat()`函数快速发送消息
2. **创建特定类型的模型** - 创建OpenAI、通义千问等特定模型
3. **使用消息列表进行多轮对话** - 通过消息列表实现多轮对话
4. **流式聊天** - 使用流式接口实时获取响应
5. **模型检测** - 自动检测系统中可用的模型
6. **自动创建最佳可用模型** - 自动选择并创建最佳模型
7. **查看模型性能指标** - 获取延迟、速度、成功率等指标
8. **使用自定义配置创建模型** - 自定义温度、最大tokens等参数
9. **使用本地模型** - 使用Hugging Face和Ollama本地模型
10. **模型管理** - 列出、切换、删除已加载的模型

## 运行方式

### 运行所有示例

```bash
cd /Users/lijunyi/road/llm-learn/engineer
python src/sample/llm_integration_example.py
```

### 运行特定示例

在Python中导入并调用特定示例函数：

```python
from src.sample.llm_integration_example import example_1_quick_chat

example_1_quick_chat()
```

## 环境要求

- Python 3.8+
- 需要配置相应的API密钥（如OPENAI_API_KEY、DASHSCOPE_API_KEY等）
- 本地模型需要安装相应的依赖（如transformers、ollama等）

## 注意事项

- 某些示例需要配置API密钥才能正常运行
- 本地模型示例需要提前安装并启动相应的服务
- 如果没有配置API密钥，相关示例会显示错误信息
