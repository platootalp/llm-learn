"""
自动模型检测机制
自动识别并适配系统中可用的各类LLM模型
"""

import os
import requests
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from .base_llm import ModelConfig, ModelType

@dataclass
class DetectedModel:
    """检测到的模型信息"""
    model_name: str
    model_type: ModelType
    provider: str
    available: bool
    config: ModelConfig
    description: str = ""


class ModelDetector:
    """模型检测器"""

    def __init__(self):
        self.detected_models: List[DetectedModel] = []
        self._detect_all()

    def _detect_all(self):
        """检测所有可用的模型"""
        self.detected_models = []
        
        self._detect_openai()
        self._detect_anthropic()
        self._detect_qwen()
        self._detect_ollama()
        self._detect_huggingface()

    def _detect_openai(self) -> Optional[DetectedModel]:
        """检测OpenAI模型"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return None
        
        base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        
        try:
            response = requests.get(
                f"{base_url}/models",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=5
            )
            if response.status_code == 200:
                models = response.json().get("data", [])
                available_models = [m["id"] for m in models if m["id"].startswith("gpt")]
                
                if available_models:
                    config = ModelConfig(
                        model_name=available_models[0],
                        model_type=ModelType.OPENAI,
                        api_key=api_key,
                        base_url=base_url
                    )
                    detected = DetectedModel(
                        model_name=available_models[0],
                        model_type=ModelType.OPENAI,
                        provider="OpenAI",
                        available=True,
                        config=config,
                        description=f"OpenAI API，可用模型: {', '.join(available_models[:5])}"
                    )
                    self.detected_models.append(detected)
                    return detected
        except Exception:
            pass
        
        return None

    def _detect_anthropic(self) -> Optional[DetectedModel]:
        """检测Anthropic模型"""
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            return None
        
        try:
            from anthropic import Anthropic
            client = Anthropic(api_key=api_key)
            models = client.models.list()
            
            available_models = [m.id for m in models.data]
            
            if available_models:
                config = ModelConfig(
                    model_name=available_models[0],
                    model_type=ModelType.ANTHROPIC,
                    api_key=api_key
                )
                detected = DetectedModel(
                    model_name=available_models[0],
                    model_type=ModelType.ANTHROPIC,
                    provider="Anthropic",
                    available=True,
                    config=config,
                    description=f"Anthropic API，可用模型: {', '.join(available_models[:5])}"
                )
                self.detected_models.append(detected)
                return detected
        except Exception:
            pass
        
        return None

    def _detect_qwen(self) -> Optional[DetectedModel]:
        """检测通义千问模型"""
        api_key = os.getenv("DASHSCOPE_API_KEY")
        if not api_key:
            return None
        
        base_url = os.getenv("DASHSCOPE_API_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
        
        try:
            headers = {"Authorization": f"Bearer {api_key}"}
            response = requests.get(
                f"{base_url}/models",
                headers=headers,
                timeout=5
            )
            if response.status_code == 200:
                models = response.json().get("data", [])
                
                text_models = []
                for m in models:
                    model_id = m["id"].lower()
                    if "qwen" in model_id and "image" not in model_id and "vision" not in model_id and "vl" not in model_id and "tts" not in model_id and "asr" not in model_id and "mt" not in model_id and "character" not in model_id and "omni" not in model_id and "livetranslate" not in model_id and "s2s" not in model_id:
                        text_models.append(m["id"])
                
                if text_models:
                    preferred_models = ["qwen3-coder-flash","qwen3-coder-plus","qwen-plus-latest", "qwen-plus", "qwen-turbo-latest", "qwen-turbo", "qwen-max-latest", "qwen-max"]
                    selected_model = None
                    
                    for preferred in preferred_models:
                        if preferred in text_models:
                            selected_model = preferred
                            break
                    
                    if not selected_model:
                        selected_model = text_models[0]
                    
                    config = ModelConfig(
                        model_name=selected_model,
                        model_type=ModelType.QWEN,
                        api_key=api_key,
                        base_url=base_url
                    )
                    detected = DetectedModel(
                        model_name=selected_model,
                        model_type=ModelType.QWEN,
                        provider="通义千问",
                        available=True,
                        config=config,
                        description=f"通义千问API，可用模型: {', '.join(text_models[:5])}"
                    )
                    self.detected_models.append(detected)
                    return detected
        except Exception:
            pass
        
        return None

    def _detect_ollama(self) -> Optional[DetectedModel]:
        """检测Ollama本地模型"""
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        
        try:
            response = requests.get(f"{base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                result = response.json()
                models = result.get("models", [])
                
                if models:
                    model_name = models[0]["name"]
                    config = ModelConfig(
                        model_name=model_name,
                        model_type=ModelType.OLLAMA,
                        base_url=base_url
                    )
                    detected = DetectedModel(
                        model_name=model_name,
                        model_type=ModelType.OLLAMA,
                        provider="Ollama",
                        available=True,
                        config=config,
                        description=f"Ollama本地模型，可用模型: {', '.join([m['name'] for m in models[:5]])}"
                    )
                    self.detected_models.append(detected)
                    return detected
        except Exception:
            pass
        
        return None

    def _detect_huggingface(self) -> Optional[DetectedModel]:
        """检测Hugging Face本地模型"""
        try:
            from transformers import AutoTokenizer
            import torch
        except ImportError:
            return None
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        
        common_models = [
            "Qwen/Qwen2.5-7B-Instruct",
            "THUDM/chatglm3-6b",
            "microsoft/DialoGPT-medium",
            "gpt2",
            "facebook/opt-1.3b"
        ]
        
        for model_name in common_models:
            try:
                tokenizer = AutoTokenizer.from_pretrained(
                    model_name,
                    trust_remote_code=True,
                    local_files_only=True
                )
                
                config = ModelConfig(
                    model_name=model_name,
                    model_type=ModelType.HUGGINGFACE
                )
                detected = DetectedModel(
                    model_name=model_name,
                    model_type=ModelType.HUGGINGFACE,
                    provider="Hugging Face",
                    available=True,
                    config=config,
                    description=f"Hugging Face本地模型，设备: {device}"
                )
                self.detected_models.append(detected)
                return detected
            except Exception:
                continue
        
        return None

    def get_available_models(self) -> List[DetectedModel]:
        """获取所有检测到的可用模型"""
        return [m for m in self.detected_models if m.available]

    def get_models_by_type(self, model_type: ModelType) -> List[DetectedModel]:
        """根据类型获取模型"""
        return [m for m in self.detected_models if m.model_type == model_type and m.available]

    def get_best_model(self, preference: Optional[str] = None) -> Optional[DetectedModel]:
        """
        获取最佳模型
        :param preference: 优先选择的模型类型 (openai, anthropic, qwen, ollama, huggingface)
        :return: 最佳模型
        """
        available = self.get_available_models()
        if not available:
            return None
        
        if preference:
            pref_type = ModelType(preference.lower())
            for model in available:
                if model.model_type == pref_type:
                    return model
        
        priority_order = [
            ModelType.OPENAI,
            ModelType.ANTHROPIC,
            ModelType.QWEN,
            ModelType.OLLAMA,
            ModelType.HUGGINGFACE
        ]
        
        for model_type in priority_order:
            for model in available:
                if model.model_type == model_type:
                    return model
        
        return available[0]

    def print_detected_models(self):
        """打印检测到的模型信息"""
        print("\n" + "=" * 70)
        print("检测到的LLM模型")
        print("=" * 70)
        
        available = self.get_available_models()
        
        if not available:
            print("未检测到可用的LLM模型")
            print("\n提示：")
            print("- 配置API密钥：设置 OPENAI_API_KEY, ANTHROPIC_API_KEY, DASHSCOPE_API_KEY")
            print("- 启动Ollama：运行 'ollama serve'")
            print("- 下载Hugging Face模型：使用 transformers 库下载")
            return
        
        for i, model in enumerate(available, 1):
            print(f"\n{i}. {model.provider} - {model.model_name}")
            print(f"   类型: {model.model_type.value}")
            print(f"   描述: {model.description}")
        
        best = self.get_best_model()
        if best:
            print(f"\n推荐使用: {best.provider} - {best.model_name}")
        
        print("=" * 70 + "\n")


def auto_detect_models() -> List[DetectedModel]:
    """
    自动检测所有可用的LLM模型
    :return: 检测到的模型列表
    """
    detector = ModelDetector()
    return detector.get_available_models()


def get_best_available_model(preference: Optional[str] = None) -> Optional[DetectedModel]:
    """
    获取最佳可用模型
    :param preference: 优先选择的模型类型
    :return: 最佳模型
    """
    detector = ModelDetector()
    return detector.get_best_model(preference)
