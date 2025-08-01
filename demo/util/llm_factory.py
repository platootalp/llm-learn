import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from getpass import getpass


def get_qwen_model():
    """
    获取 Qwen 模型实例（单例/懒加载也可扩展）
    """
    load_dotenv()
    # if not os.environ.get("QWEN_API_KEY"):
    #     os.environ["QWEN_API_KEY"] = getpass("Enter API key for Qwen: ")

    return ChatOpenAI(
        model_name="qwen-turbo",
        openai_api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",
        openai_api_key=os.environ["DASHSCOPE_API_KEY"]
    )

if __name__ == '__main__':
    model = get_qwen_model()
    chunks = []
    for chunk in model.stream("what color is the sky?"):
        chunks.append(chunk)
        print(chunk.content, end="|", flush=True)
