"""
Reflection Agent 示例实现
- 生成初始答案
- 反思答案质量
- 基于反思改进答案
"""

import os
from dotenv import load_dotenv
from qwen_llm import QwenLLM


INITIAL_RESPONSE_PROMPT = """
你是一个智能助手。请回答以下问题。

问题: {question}

请提供你的答案:
"""

REFLECTION_PROMPT = """
你是一个反思专家。请评估以下答案的质量，并提出改进建议。

原始问题: {question}

当前答案: {answer}

请从以下方面进行评估:
1. 答案的准确性
2. 答案的完整性
3. 答案的清晰度
4. 是否存在错误或遗漏

请提供你的评估和改进建议:
"""

REFINED_RESPONSE_PROMPT = """
你是一个智能助手。基于原始问题、初始答案和反思建议，请提供一个改进后的答案。

原始问题: {question}

初始答案: {answer}

反思建议: {reflection}

请提供改进后的答案:
"""


class ReflectionAgent:
    """
    Basic Reflection 智能体
    - 生成初始答案
    - 反思答案质量
    - 基于反思改进答案
    """

    def __init__(self, llm_client: QwenLLM, max_reflections: int = 2):
        self.llm_client = llm_client
        self.max_reflections = max_reflections

    def generate_initial_response(self, question: str) -> str:
        """
        生成初始答案
        """
        prompt = INITIAL_RESPONSE_PROMPT.format(question=question)
        response = self.llm_client.think([{"role": "user", "content": prompt}])
        print(f"\n--- 初始答案 ---")
        print(f"{response}")
        return response

    def reflect(self, question: str, answer: str) -> str:
        """
        反思答案质量
        """
        prompt = REFLECTION_PROMPT.format(question=question, answer=answer)
        reflection = self.llm_client.think([{"role": "user", "content": prompt}])
        print(f"\n--- 反思 ---")
        print(f"{reflection}")
        return reflection

    def refine(self, question: str, answer: str, reflection: str) -> str:
        """
        基于反思改进答案
        """
        prompt = REFINED_RESPONSE_PROMPT.format(
            question=question,
            answer=answer,
            reflection=reflection
        )
        refined = self.llm_client.think([{"role": "user", "content": prompt}])
        print(f"\n--- 改进答案 ---")
        print(f"{refined}")
        return refined

    def run(self, question: str) -> str:
        """
        运行 Basic Reflection 主循环
        """
        current_answer = self.generate_initial_response(question)

        for i in range(self.max_reflections):
            reflection = self.reflect(question, current_answer)
            current_answer = self.refine(question, current_answer, reflection)

        print(f"\n--- 最终答案 ---")
        print(f"{current_answer}")
        return current_answer


if __name__ == "__main__":
    load_dotenv()
    api_key = os.getenv("DASHSCOPE_API_KEY")
    base_url = os.getenv("DASHSCOPE_API_URL")

    llm = QwenLLM(api_key=api_key, base_url=base_url, model_name="qwen-plus")

    print("=" * 60)
    print("Reflection Agent 示例")
    print("=" * 60)

    br_agent = ReflectionAgent(llm_client=llm, max_reflections=2)
    br_agent.run("用Java语言实现一个高效的令牌桶算法")
