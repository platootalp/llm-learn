"""
LLM集成使用示例
展示如何使用LLM集成模块进行模型调用、检测和管理
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core import (
    ModelConfig, Message, ModelType,
    OpenAILLM, AnthropicLLM, QwenLLM, HuggingFaceLLM, OllamaLLM,
    LLMManager, create_llm_manager, quick_chat, quick_chat_stream,
    ModelDetector, DetectedModel
)


def example_1_quick_chat():
    """示例1: 快速聊天接口"""
    print("=" * 70)
    print("示例1: 快速聊天接口")
    print("=" * 70)
    
    try:
        response = quick_chat("你好，请介绍一下自己")
        print(f"响应: {response.content}")
        print(f"延迟: {response.latency:.2f}秒")
        print(f"Token使用: {response.usage}")
    except Exception as e:
        print(f"错误: {e}")
    
    print()


def example_2_create_specific_model():
    """示例2: 创建特定类型的模型"""
    print("=" * 70)
    print("示例2: 创建特定类型的模型")
    print("=" * 70)
    
    manager = create_llm_manager()
    
    try:
        print("创建OpenAI模型...")
        openai_model = manager.create_model(
            model_type=ModelType.OPENAI,
            model_name="gpt-3.5-turbo"
        )
        print(f"OpenAI模型创建成功: {openai_model.config.model_name}")
    except Exception as e:
        print(f"OpenAI模型创建失败: {e}")
    
    try:
        print("\n创建通义千问模型...")
        qwen_model = manager.create_model(
            model_type=ModelType.QWEN,
            model_name="qwen-plus"
        )
        print(f"通义千问模型创建成功: {qwen_model.config.model_name}")
    except Exception as e:
        print(f"通义千问模型创建失败: {e}")
    
    print()


def example_3_chat_with_messages():
    """示例3: 使用消息列表进行多轮对话"""
    print("=" * 70)
    print("示例3: 使用消息列表进行多轮对话")
    print("=" * 70)
    
    manager = create_llm_manager()
    
    try:
        messages = [
            Message(role="system", content="你是一个有帮助的AI助手"),
            Message(role="user", content="什么是Python？"),
            Message(role="assistant", content="Python是一种高级编程语言"),
            Message(role="user", content="它有哪些特点？")
        ]
        
        response = manager.chat(messages)
        print(f"响应: {response.content}")
        print(f"延迟: {response.latency:.2f}秒")
    except Exception as e:
        print(f"错误: {e}")
    
    print()


def example_4_stream_chat():
    """示例4: 流式聊天"""
    print("=" * 70)
    print("示例4: 流式聊天")
    print("=" * 70)
    
    try:
        print("流式响应: ", end="", flush=True)
        for chunk in quick_chat_stream("请用三句话介绍一下人工智能"):
            print(chunk, end="", flush=True)
        print("\n")
    except Exception as e:
        print(f"错误: {e}")
    
    print()


def example_5_model_detection():
    """示例5: 模型检测"""
    print("=" * 70)
    print("示例5: 模型检测")
    print("=" * 70)
    
    detector = ModelDetector()
    
    print("检测所有可用模型...")
    models = detector.get_available_models()
    
    if models:
        print(f"检测到 {len(models)} 个可用模型:")
        for model in models:
            print(f"  - {model.model_type.value}: {model.model_name}")
            print(f"    可用: {model.available}")
            if model.available:
                print(f"    配置: {model.config}")
    else:
        print("未检测到可用模型")
    
    print()


def example_6_auto_create_model():
    """示例6: 自动创建最佳可用模型"""
    print("=" * 70)
    print("示例6: 自动创建最佳可用模型")
    print("=" * 70)
    
    manager = create_llm_manager()
    
    print("自动检测并创建最佳模型...")
    try:
        model = manager.create_model(auto_detect=True)
        print(f"自动创建的模型: {model.config.model_name}")
        print(f"模型类型: {model.config.model_type.value}")
        
        response = manager.complete("你好")
        print(f"测试响应: {response.content[:50]}...")
    except Exception as e:
        print(f"错误: {e}")
    
    print()


def example_7_model_metrics():
    """示例7: 查看模型性能指标"""
    print("=" * 70)
    print("示例7: 查看模型性能指标")
    print("=" * 70)
    
    manager = create_llm_manager()
    
    try:
        model = manager.create_model(auto_detect=True)
        
        print("进行多次调用以收集指标...")
        for i in range(3):
            manager.complete(f"测试消息 {i+1}")
        
        metrics = manager.get_model_metrics()
        print(f"模型名称: {metrics.model_name}")
        print(f"平均延迟: {metrics.avg_latency:.2f}秒")
        print(f"平均速度: {metrics.avg_tokens_per_second:.2f} tokens/秒")
        print(f"成功率: {metrics.success_rate * 100:.1f}%")
        print(f"总调用次数: {metrics.total_calls}")
        print(f"错误次数: {metrics.error_count}")
    except Exception as e:
        print(f"错误: {e}")
    
    print()


def example_8_custom_config():
    """示例8: 使用自定义配置创建模型"""
    print("=" * 70)
    print("示例8: 使用自定义配置创建模型")
    print("=" * 70)
    
    config = ModelConfig(
        model_name="qwen-plus",
        model_type=ModelType.QWEN,
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        temperature=0.7,
        max_tokens=500,
        top_p=0.9,
        timeout=30
    )
    
    try:
        from core import create_llm
        model = create_llm(config)
        print(f"模型创建成功: {model.config.model_name}")
        print(f"温度: {model.config.temperature}")
        print(f"最大tokens: {model.config.max_tokens}")
        
        response = model.complete("你好")
        print(f"响应: {response.content[:50]}...")
    except Exception as e:
        print(f"错误: {e}")
    
    print()


def example_9_local_models():
    """示例9: 使用本地模型（Hugging Face和Ollama）"""
    print("=" * 70)
    print("示例9: 使用本地模型")
    print("=" * 70)
    
    manager = create_llm_manager()
    
    try:
        print("尝试创建Hugging Face本地模型...")
        hf_model = manager.create_model(
            model_type=ModelType.HUGGINGFACE,
            model_name="gpt2"
        )
        print(f"Hugging Face模型创建成功: {hf_model.config.model_name}")
        
        response = hf_model.complete("Hello, how are you?")
        print(f"响应: {response.content[:100]}...")
    except Exception as e:
        print(f"Hugging Face模型创建失败: {e}")
    
    try:
        print("\n尝试创建Ollama本地模型...")
        ollama_model = manager.create_model(
            model_type=ModelType.OLLAMA,
            model_name="llama2"
        )
        print(f"Ollama模型创建成功: {ollama_model.config.model_name}")
        
        response = ollama_model.complete("Hello")
        print(f"响应: {response.content[:100]}...")
    except Exception as e:
        print(f"Ollama模型创建失败: {e}")
    
    print()


def example_10_model_management():
    """示例10: 模型管理（列出、切换、删除）"""
    print("=" * 70)
    print("示例10: 模型管理")
    print("=" * 70)
    
    manager = create_llm_manager()
    
    try:
        print("创建多个模型...")
        model1 = manager.create_model(
            model_type=ModelType.QWEN,
            model_name="qwen-plus"
        )
        model2 = manager.create_model(
            model_type=ModelType.QWEN,
            model_name="qwen-turbo"
        )
        
        print(f"\n已加载的模型: {manager.list_models()}")
        
        print("\n切换当前模型...")
        manager.set_current_model(model1)
        print(f"当前模型: {manager.get_current_model().config.model_name}")
        
        print("\n删除模型...")
        manager.remove_model("qwen:qwen-turbo")
        print(f"删除后的模型列表: {manager.list_models()}")
        
    except Exception as e:
        print(f"错误: {e}")
    
    print()


def main():
    """运行所有示例"""
    print("\n")
    print("*" * 70)
    print("LLM集成功能使用示例")
    print("*" * 70)
    print("\n")
    
    examples = [
        example_1_quick_chat,
        example_3_chat_with_messages,
        example_4_stream_chat,
        example_5_model_detection,
        example_6_auto_create_model,
        example_7_model_metrics,
        example_8_custom_config,
        # example_2_create_specific_model,
        # example_9_local_models,
        # example_10_model_management,
    ]
    
    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"示例执行失败: {e}")
            print()
    
    print("*" * 70)
    print("所有示例执行完毕")
    print("*" * 70)


if __name__ == "__main__":
    main()
