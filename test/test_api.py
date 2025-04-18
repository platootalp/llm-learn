import unittest
import httpx
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 测试配置
BASE_URL = "http://localhost:8000"
API_KEY = os.getenv("API_KEY")
HEADERS = {"api_key": API_KEY} if API_KEY else {}


class TestAPI(unittest.IsolatedAsyncioTestCase):
    """API测试类"""
    
    async def test_health_check(self):
        """测试健康检查接口"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/health")
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["status"], "healthy")
    
    async def test_root(self):
        """测试根路径接口"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/")
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn("service", data)
            self.assertIn("version", data)
    
    async def test_models_endpoint(self):
        """测试获取模型列表接口"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/api/models", headers=HEADERS)
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn("models", data)
            self.assertTrue(isinstance(data["models"], list))
    
    async def test_chat_endpoint(self):
        """测试聊天接口"""
        # 准备测试请求
        request_data = {
            "messages": [
                {"role": "user", "content": "你好，请介绍一下你自己"}
            ],
            # "model": "qwen-turbo",
            "temperature": 0.7,
            "max_tokens": 100
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/api/chat",
                headers=HEADERS,
                json=request_data
            )
            
            # 如果API密钥未设置或阿里云百炼API密钥未设置，预期会失败
            if not os.getenv("QWEN_API_KEY"):
                self.assertNotEqual(response.status_code, 200)
                return
                
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn("response", data)
            self.assertTrue(isinstance(data["response"], str))
            # 可能有usage字段，但不一定存在


if __name__ == "__main__":
    unittest.main() 