"""
Reason without Observation Agent 示例实现
- 仅依靠 LLM 的推理能力解决问题
- 不依赖外部工具或观察结果
"""

import os
import re
from dotenv import load_dotenv
from qwen_llm import QwenLLM


REASON_WO_OBS_PROMPT_TEMPLATE = """
你是一个能够进行深度推理的智能助手。你的任务是直接对问题进行推理分析，不需要调用外部工具或获取外部观察结果。

问题: {question}

请按照以下格式输出你的推理过程和最终答案:

Thought: [你的推理过程，详细分析问题]
Answer: [你的最终答案]

注意: 请仅基于你的知识和推理能力回答，不要假设需要获取外部信息。
"""


class ReasonWithoutObservationAgent:
    """
    Reason without Observation 智能体
    - 仅依靠 LLM 的推理能力解决问题
    - 不依赖外部工具或观察结果
    """

    def __init__(self, llm_client: QwenLLM):
        self.llm_client = llm_client

    def run(self, question: str) -> str:
        """
        运行推理过程
        """
        prompt = REASON_WO_OBS_PROMPT_TEMPLATE.format(question=question)

        print(f"\n--- 开始推理 ---")
        response = self.llm_client.think([{"role": "user", "content": prompt}])

        thought_match = re.search(r"Thought:\s*(.*?)(?=\nAnswer:|$)", response, re.DOTALL)
        answer_match = re.search(r"Answer:\s*(.*)", response, re.DOTALL)

        thought = thought_match.group(1).strip() if thought_match else ""
        answer = answer_match.group(1).strip() if answer_match else response

        print(f"推理过程: {thought}")
        print(f"\n--- 最终答案 ---")
        print(f"{answer}")

        return answer


if __name__ == "__main__":
    load_dotenv()
    api_key = os.getenv("DASHSCOPE_API_KEY")
    base_url = os.getenv("DASHSCOPE_API_URL")

    llm = QwenLLM(api_key=api_key, base_url=base_url, model_name="qwen-plus")

    print("=" * 60)
    print("Reason without Observation Agent 示例")
    print("=" * 60)

    rwo_agent = ReasonWithoutObservationAgent(llm_client=llm)
    rwo_agent.run("为什么天空是蓝色的？")
