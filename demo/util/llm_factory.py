import os
import logging
from typing import Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_core.language_models.chat_models import BaseChatModel

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables once (optional)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    logger.warning("python-dotenv module not found, skipping .env file loading")
except Exception as e:
    logger.warning(f"Failed to load .env file: {e}")


class LLMFactory:
    """
    大语言模型工厂类，用于创建和管理不同类型的LLM实例
    实现单例模式，确保每个模型只创建一次
    """
    
    # 模型配置映射 - 增强支持更多模型和配置选项
    MODEL_CONFIGS = {
        "qwen": {
            "model_name": "qwen-turbo",
            "api_base_env": "DASHSCOPE_API_URL",
            "api_key_env": "DASHSCOPE_API_KEY",
            "default_api_base": "https://dashscope.aliyuncs.com/compatible-mode/v1",
            "model_class": ChatOpenAI,
            "default_params": {
                "temperature": 0.7,
                "max_tokens": 2048,
                "response_format": {"type": "text"}
            }
        },
        "mimo": {
            "model_name": "mimo-v2-flash",
            "api_base_env": "MIMO_API_URL",
            "api_key_env": "MIMO_API_KEY",
            "default_api_base": "https://api.mimo.ai/v1",
            "model_class": ChatOpenAI,
            "default_params": {
                "temperature": 0.6,
                "max_tokens": 4096,
                "response_format": {"type": "text"}
            }
        },
        "qwen-long": {
            "model_name": "qwen-max-longcontext",
            "api_base_env": "DASHSCOPE_API_URL",
            "api_key_env": "DASHSCOPE_API_KEY",
            "default_api_base": "https://dashscope.aliyuncs.com/compatible-mode/v1",
            "model_class": ChatOpenAI,
            "default_params": {
                "temperature": 0.5,
                "max_tokens": 8192,
                "response_format": {"type": "text"}
            }
        }
    }
    
    def __init__(self):
        self._model_instances: Dict[str, BaseChatModel] = {}
    
    def get_model(self, model_name: str, **kwargs) -> BaseChatModel:
        """
        获取指定名称的模型实例
        
        Args:
            model_name: 模型名称
            **kwargs: 额外的模型配置参数
            
        Returns:
            BaseChatModel: 模型实例
            
        Raises:
            ValueError: 当模型名称不支持或参数无效时
            KeyError: 当缺少必要的环境变量时
            RuntimeError: 当模型实例创建失败时
        """
        if not model_name:
            raise ValueError("模型名称不能为空")
        
        # 检查模型是否已存在（单例模式）
        if model_name in self._model_instances:
            logger.info(f"Returning cached model instance for: {model_name}")
            return self._model_instances[model_name]
        
        # 检查模型是否支持
        if model_name not in self.MODEL_CONFIGS:
            raise ValueError(f"不支持的模型名称: {model_name}。支持的模型: {list(self.MODEL_CONFIGS.keys())}")
        
        logger.info(f"Creating new model instance for: {model_name}")
        config = self.MODEL_CONFIGS[model_name]
        
        # 获取环境变量
        try:
            api_base = os.environ.get(config["api_base_env"]) or config["default_api_base"]
            if not api_base:
                raise ValueError(f"API base URL is empty for model {model_name}")
            
            api_key = os.environ[config["api_key_env"]]
            if not api_key:
                raise ValueError(f"API key is empty for model {model_name}")
        except KeyError as e:
            raise KeyError(f"缺少必要的环境变量: {e}")
        except ValueError as e:
            raise ValueError(f"无效的环境变量配置: {e}")
        
        # 构建模型参数 - 使用模型特定的默认参数
        model_kwargs = {
            "model_name": config["model_name"],
            "openai_api_base": api_base,
            "openai_api_key": api_key,
        }
        
        # 添加模型特定的默认参数
        if "default_params" in config:
            model_kwargs.update(config["default_params"])
        
        # 添加通用默认参数（如果模型配置中没有指定）
        model_kwargs.setdefault("temperature", 0.7)
        model_kwargs.setdefault("max_tokens", 2048)
        
        # 合并额外的参数，覆盖默认值
        model_kwargs.update(kwargs)
        
        logger.debug(f"Model instantiation parameters for {model_name}: " + 
                    f"{{'model_name': '{model_kwargs['model_name']}', " +
                    f"'openai_api_base': '{api_base.split('://')[0] + '://' + '***' + api_base.split('://')[1][-10:] if '://' in api_base else '***'}', " +
                    f"'temperature': {model_kwargs['temperature']}, " +
                    f"'max_tokens': {model_kwargs['max_tokens']}}}")
        
        # 创建具体模型
        try:
            # 支持自定义模型类
            model_class = config.get("model_class", ChatOpenAI)
            model = model_class(**model_kwargs)
            
            # 缓存模型实例
            self._model_instances[model_name] = model
            logger.info(f"Successfully created model instance for: {model_name}")
            return model
        except TypeError as e:
            logger.error(f"Invalid parameters for model {model_name}: {e}")
            raise ValueError(f"无效的模型参数配置: {e}") from e
        except Exception as e:
            logger.error(f"Failed to create model instance for {model_name}: {e}", exc_info=True)
            raise RuntimeError(f"模型实例创建失败: {str(e)}") from e
    
    def list_supported_models(self) -> list[str]:
        """
        获取支持的模型列表
        
        Returns:
            list[str]: 支持的模型名称列表
        """
        return list(self.MODEL_CONFIGS.keys())
    
    def clear_cache(self) -> None:
        """
        清除所有缓存的模型实例
        """
        logger.info("Clearing all cached model instances")
        self._model_instances.clear()
    
    def get_qwen_model(self, **kwargs) -> ChatOpenAI:
        """
        便捷方法：获取 Qwen 模型实例
        
        Args:
            **kwargs: 额外的模型配置参数
            
        Returns:
            ChatOpenAI: Qwen 模型实例
        """
        return self.get_model("qwen", **kwargs)
    
    def get_mimo_model(self, **kwargs) -> ChatOpenAI:
        """
        便捷方法：获取 MIMO 模型实例
        
        Args:
            **kwargs: 额外的模型配置参数
            
        Returns:
            ChatOpenAI: MIMO 模型实例
        """
        return self.get_model("mimo", **kwargs)
    
    def update_model_config(self, model_name: str, **config_updates) -> None:
        """
        更新指定模型的配置
        
        Args:
            model_name: 模型名称
            **config_updates: 要更新的配置参数
            
        Raises:
            ValueError: 当模型名称不支持时
        """
        if model_name not in self.MODEL_CONFIGS:
            raise ValueError(f"不支持的模型名称: {model_name}。支持的模型: {list(self.MODEL_CONFIGS.keys())}")
        
        self.MODEL_CONFIGS[model_name].update(config_updates)
        logger.info(f"Updated configuration for model {model_name}: {config_updates}")
        
        # 如果模型实例已存在，清除缓存以应用新配置
        if model_name in self._model_instances:
            logger.info(f"Clearing cached instance for model {model_name} to apply new configuration")
            del self._model_instances[model_name]
    
    def validate_environment(self) -> Dict[str, bool]:
        """
        验证所有支持模型的环境变量是否配置正确
        
        Returns:
            Dict[str, bool]: 每个模型的环境变量验证结果
        """
        validation_results = {}
        
        for model_name, config in self.MODEL_CONFIGS.items():
            try:
                # 检查API密钥是否存在
                api_key = os.environ[config["api_key_env"]]
                if not api_key:
                    raise ValueError(f"API key for {model_name} is empty")
                
                # API base是可选的，因为有默认值
                validation_results[model_name] = True
            except (KeyError, ValueError) as e:
                logger.warning(f"Environment validation failed for {model_name}: {e}")
                validation_results[model_name] = False
        
        return validation_results


# 创建工厂实例（单例使用）
llm_factory = LLMFactory()


if __name__ == '__main__':
    # 测试工厂功能
    try:
        # 列出支持的模型
        print(f"支持的模型: {llm_factory.list_supported_models()}")
        
        # 验证环境配置
        print("\n验证环境配置...")
        env_validation = llm_factory.validate_environment()
        for model_name, is_valid in env_validation.items():
            status = "✅ 有效" if is_valid else "❌ 无效"
            print(f"{model_name}: {status}")
        
        # 选择一个环境有效且支持的模型进行测试
        available_models = [model for model, valid in env_validation.items() if valid]
        
        if not available_models:
            print("\n❌ 没有可用的模型环境配置，请检查环境变量设置")
            exit(1)
        
        test_model = available_models[0]
        print(f"\n选择测试模型: {test_model}")
        
        # 测试获取模型实例
        model = llm_factory.get_model(test_model, temperature=0.5)
        
        # 测试再次获取同一模型（应该返回缓存实例）
        cached_model = llm_factory.get_model(test_model)
        print(f"\n模型缓存测试: {model is cached_model} (同一实例表示缓存生效)")
        
        # 测试模型生成
        print("\n测试模型生成...")
        prompt = "天空是什么颜色的？"
        print(f"提示词: {prompt}")
        print("回答: ", end="", flush=True)
        
        chunks = []
        for chunk in model.stream(prompt):
            chunks.append(chunk)
            print(chunk.content, end="", flush=True)
            
        print("\n\n生成完成！")
        
        # 测试配置更新
        print("\n测试配置更新功能...")
        if test_model in llm_factory.list_supported_models():
            # 更新其他配置参数，而不是model_name
            llm_factory.update_model_config(test_model, temperature=0.8)
            print(f"✅ 成功更新模型 {test_model} 的配置")
        
        # 测试清除缓存
        print("\n测试清除缓存功能...")
        llm_factory.clear_cache()
        print("✅ 成功清除所有模型缓存")
        
        print("\n🎉 所有测试完成！")
        
    except Exception as e:
        logger.error(f"测试失败: {e}", exc_info=True)
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
