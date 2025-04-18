import getpass
import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

if not os.environ.get("QWEN_API_KEY"):
    os.environ["QWEN_API_KEY"] = getpass.getpass("Enter API key for Qwen: ")

# 替换 OpenAI API 地址为阿里云百炼的 OpenAI 兼容接口
model = ChatOpenAI(
    model_name="qwen-turbo",  # 选择阿里云百炼模型
    openai_api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",  # 阿里云 DashScope API 地址
    openai_api_key="sk-f755ab0f995c43ffa206424bb2c43de2"
)

# 进行测试
if __name__ == '__main__':
    response = model.predict("什么是rag")
    print(response)

