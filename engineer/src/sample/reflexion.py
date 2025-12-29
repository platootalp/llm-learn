"""
Reflexion Agent 示例实现
- 生成初始解决方案
- 执行并收集反馈
- 反思失败原因
- 基于反思生成新的解决方案
"""

import os
from dotenv import load_dotenv
from qwen_llm import QwenLLM


INITIAL_SOLUTION_PROMPT = """
你是一个问题解决专家。请尝试解决以下问题。

问题: {question}

请提供你的解决方案:
"""

REFLEXION_REFLECT_PROMPT = """
你是一个反思专家。请分析以下尝试失败的原因，并生成一个具体的改进策略。

原始问题: {question}

尝试的解决方案: {solution}

执行结果/错误: {result}

请分析失败原因，并提供具体的改进策略。改进策略应该是一个具体的、可执行的建议。
"""

REFLEXION_REFINE_PROMPT = """
你是一个问题解决专家。基于原始问题、之前的尝试和反思建议，请提供一个改进的解决方案。

原始问题: {question}

之前的尝试: {solution}

执行结果/错误: {result}

反思建议: {reflection}

请提供改进后的解决方案:
"""


class ReflexionAgent:
    """
    Reflexion 智能体
    - 生成初始解决方案
    - 执行并收集反馈
    - 反思失败原因
    - 基于反思生成新的解决方案
    """

    def __init__(self, llm_client: QwenLLM, max_attempts: int = 3):
        self.llm_client = llm_client
        self.max_attempts = max_attempts

    def generate_solution(self, question: str, reflection: str = "") -> str:
        """
        生成解决方案
        """
        if reflection:
            prompt = REFLEXION_REFINE_PROMPT.format(
                question=question,
                solution=self.last_solution,
                result=self.last_result,
                reflection=reflection
            )
        else:
            prompt = INITIAL_SOLUTION_PROMPT.format(question=question)

        solution = self.llm_client.think([{"role": "user", "content": prompt}])
        return solution

    def execute_solution(self, solution: str) -> str:
        """
        执行解决方案（模拟）
        """
        print(f"\n--- 执行解决方案 ---")
        print(f"{solution}")

        if "计算" in solution or "数学" in solution:
            return "执行成功，结果正确"
        elif "搜索" in solution or "查找" in solution:
            return "执行成功，找到相关信息"
        else:
            return "执行成功"

    def reflect(self, question: str, solution: str, result: str) -> str:
        """
        反思失败原因
        """
        prompt = REFLEXION_REFLECT_PROMPT.format(
            question=question,
            solution=solution,
            result=result
        )
        reflection = self.llm_client.think([{"role": "user", "content": prompt}])
        print(f"\n--- 反思 ---")
        print(f"{reflection}")
        return reflection

    def run(self, question: str) -> str:
        """
        运行 Reflexion 主循环
        """
        self.last_solution = ""
        self.last_result = ""

        for attempt in range(self.max_attempts):
            print(f"\n=== 尝试 {attempt + 1} ===")

            solution = self.generate_solution(question)
            result = self.execute_solution(solution)

            self.last_solution = solution
            self.last_result = result

            if "成功" in result:
                print(f"\n--- 最终解决方案 ---")
                print(f"{solution}")
                return solution

            self.reflect(question, solution, result)

        print(f"\n--- 最终解决方案 ---")
        print(f"{self.last_solution}")
        return self.last_solution


if __name__ == "__main__":
    load_dotenv()
    api_key = os.getenv("DASHSCOPE_API_KEY")
    base_url = os.getenv("DASHSCOPE_API_URL")

    llm = QwenLLM(api_key=api_key, base_url=base_url, model_name="qwen-plus")

    print("=" * 60)
    print("Reflexion Agent 示例")
    print("=" * 60)

    reflexion_agent = ReflexionAgent(llm_client=llm, max_attempts=3)
    reflexion_agent.run("如何设计一个高效的算法？")
