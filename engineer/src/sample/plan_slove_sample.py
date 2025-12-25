"""
Plan-Solve Agent 示例实现
- 包含 Plan / Solve 的智能体循环
- 使用 Qwen 模型，进行规划和执行
"""

import os
import re
from typing import List, Dict
from dotenv import load_dotenv
from qwen_llm import QwenLLM

# =========================
# Plan-Solve Agent
# =========================

PLANNER_PROMPT_TEMPLATE = """
你是一个顶级的AI规划专家。你的任务是将用户提出的复杂问题分解成一个由多个简单步骤组成的行动计划。
请确保计划中的每个步骤都是一个独立的、可执行的子任务，并且严格按照逻辑顺序排列。
你的输出必须是一个Python列表，其中每个元素都是一个描述子任务的字符串。

问题: {question}

请严格按照以下格式输出你的计划,```python与```作为前后缀是必要的:
```python
["步骤1", "步骤2", "步骤3", ...]
```
"""

EXECUTOR_PROMPT_TEMPLATE = """
你是一位顶级的AI执行专家。你的任务是严格按照给定的计划，一步步地解决问题。
你将收到原始问题、完整的计划、以及到目前为止已经完成的步骤和结果。
请你专注于解决"当前步骤"，并仅输出该步骤的最终答案，不要输出任何额外的解释或对话。

# 原始问题:
{question}

# 完整计划:
{plan}

# 历史步骤与结果:
{history}

# 当前步骤:
{current_step}

请仅输出针对"当前步骤"的回答:
"""


class PlanSolveAgent:
    """
    Plan-Solve 智能体
    - Plan: 将复杂问题分解为多个步骤
    - Solve: 逐步执行每个步骤
    """

    def __init__(self, llm_client: QwenLLM):
        self.llm_client = llm_client

    def plan(self, question: str) -> List[str]:
        """
        生成初始计划
        """
        prompt = PLANNER_PROMPT_TEMPLATE.format(question=question)
        response = self.llm_client.think([{"role": "user", "content": prompt}])

        plan = self._extract_python_list(response)
        print(f"\n--- 生成的计划 ---")
        for i, step in enumerate(plan, 1):
            print(f"{i}. {step}")
        return plan

    def solve(self, question: str, plan: List[str], history: List[Dict[str, str]]) -> str:
        """
        执行当前步骤
        """
        current_step = plan[len(history)]
        history_str = self._format_history(history)

        prompt = EXECUTOR_PROMPT_TEMPLATE.format(
            question=question,
            plan=str(plan),
            history=history_str,
            current_step=current_step
        )

        result = self.llm_client.think([{"role": "user", "content": prompt}])
        print(f"\n--- 执行步骤: {current_step} ---")
        print(f"结果: {result}")
        return result

    def run(self, question: str) -> str:
        """
        运行 Plan-Solve 主循环
        """
        plan = self.plan(question)
        history: List[Dict[str, str]] = []

        while len(history) < len(plan):
            result = self.solve(question, plan, history)
            history.append({
                "step": plan[len(history) - 1],
                "result": result
            })

        final_answer = self._generate_final_answer(question, history)
        print(f"\n--- 最终答案 ---")
        print(f"{final_answer}")
        return final_answer

    def _extract_python_list(self, text: str) -> List[str]:
        """
        从文本中提取 Python 列表
        """
        match = re.search(r"```python\s*\[(.*?)\]\s*```", text, re.DOTALL)
        if match:
            items = [item.strip().strip('"\'') for item in match.group(1).split(",")]
            return [item for item in items if item]
        return []

    def _format_history(self, history: List[Dict[str, str]]) -> str:
        """
        格式化历史记录
        """
        if not history:
            return "无"
        return "\n".join(
            f"步骤: {h['step']}\n结果: {h['result']}\n"
            for h in history
        )

    def _generate_final_answer(self, question: str, history: List[Dict[str, str]]) -> str:
        """
        生成最终答案（不调用大模型，直接基于历史记录生成）
        """
        if not history:
            return "未找到执行结果"
        
        answer_parts = [f"问题: {question}\n"]
        answer_parts.append("执行过程:\n")
        
        for i, h in enumerate(history, 1):
            answer_parts.append(f"{i}. {h['step']}\n")
            answer_parts.append(f"   {h['result']}\n")
        
        return "".join(answer_parts)


# =========================
# 示例运行
# =========================

if __name__ == "__main__":
    load_dotenv()
    api_key = os.getenv("DASHSCOPE_API_KEY")
    base_url = os.getenv("DASHSCOPE_API_URL")

    llm = QwenLLM(api_key=api_key, base_url=base_url, model_name="qwen-plus")

    print("=" * 60)
    print("Plan-Solve Agent 示例")
    print("=" * 60)

    ps_agent = PlanSolveAgent(llm_client=llm)
    ps_agent.run("Agent开发工程师学习路线")
