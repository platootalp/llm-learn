"""
LLMCompiler Agent 示例实现
- 将复杂任务分解为可并行执行的子任务
- 根据依赖关系调度任务执行
- 聚合子任务结果生成最终答案
"""

import os
import re
from typing import List, Dict, Any
from dotenv import load_dotenv
from qwen_llm import QwenLLM


TASK_DECOMPOSITION_PROMPT = """
你是一个任务分解专家。你的任务是将复杂问题分解为多个可以并行执行的独立子任务。

问题: {question}

请将问题分解为多个独立的子任务，并按照以下格式输出:
```python
[
    {"task": "子任务1", "dependencies": []},
    {"task": "子任务2", "dependencies": ["子任务1"]},
    ...
]
```
"""

TASK_EXECUTION_PROMPT = """
你是一个任务执行专家。你的任务是执行给定的子任务。

子任务: {task}

请仅输出该子任务的执行结果，不要包含任何额外解释。
"""


class LLMCompiler:
    """
    LLMCompiler 智能体
    - 将复杂任务分解为可并行执行的子任务
    - 根据依赖关系调度任务执行
    - 聚合子任务结果生成最终答案
    """

    def __init__(self, llm_client: QwenLLM):
        self.llm_client = llm_client

    def decompose(self, question: str) -> List[Dict[str, Any]]:
        """
        任务分解
        """
        prompt = TASK_DECOMPOSITION_PROMPT.format(question=question)
        response = self.llm_client.think([{"role": "user", "content": prompt}])

        tasks = self._extract_tasks(response)
        print(f"\n--- 任务分解 ---")
        for i, task in enumerate(tasks, 1):
            deps = task.get("dependencies", [])
            deps_str = f" (依赖: {', '.join(deps)})" if deps else ""
            print(f"{i}. {task['task']}{deps_str}")

        return tasks

    def execute_task(self, task: Dict[str, Any]) -> str:
        """
        执行单个任务
        """
        prompt = TASK_EXECUTION_PROMPT.format(task=task["task"])
        result = self.llm_client.think([{"role": "user", "content": prompt}])
        print(f"执行: {task['task']} -> {result}")
        return result

    def schedule_and_execute(self, tasks: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        根据依赖关系调度并执行任务
        """
        results: Dict[str, str] = {}
        executed: set = set()

        while len(executed) < len(tasks):
            for task in tasks:
                task_name = task["task"]
                if task_name in executed:
                    continue

                dependencies = task.get("dependencies", [])
                if all(dep in executed for dep in dependencies):
                    result = self.execute_task(task)
                    results[task_name] = result
                    executed.add(task_name)

        return results

    def aggregate(self, question: str, tasks: List[Dict[str, Any]], results: Dict[str, str]) -> str:
        """
        聚合结果生成最终答案
        """
        results_str = "\n".join(
            f"子任务: {task}\n结果: {results[task]}\n"
            for task in results
        )

        prompt = f"""
基于以下子任务的执行结果，为原始问题提供完整的最终答案。

原始问题: {question}

子任务执行结果:
{results_str}

请提供完整、准确的最终答案:
"""
        final_answer = self.llm_client.think([{"role": "user", "content": prompt}])
        print(f"\n--- 最终答案 ---")
        print(f"{final_answer}")
        return final_answer

    def run(self, question: str) -> str:
        """
        运行 LLMCompiler 主流程
        """
        tasks = self.decompose(question)
        results = self.schedule_and_execute(tasks)
        final_answer = self.aggregate(question, tasks, results)
        return final_answer

    def _extract_tasks(self, text: str) -> List[Dict[str, Any]]:
        """
        从文本中提取任务列表
        """
        match = re.search(r"```python\s*\[(.*?)\]\s*```", text, re.DOTALL)
        if match:
            try:
                import json
                tasks_str = "[" + match.group(1) + "]"
                return eval(tasks_str)
            except:
                return []
        return []


if __name__ == "__main__":
    load_dotenv()
    api_key = os.getenv("DASHSCOPE_API_KEY")
    base_url = os.getenv("DASHSCOPE_API_URL")

    llm = QwenLLM(api_key=api_key, base_url=base_url, model_name="qwen-plus")

    print("=" * 60)
    print("LLMCompiler Agent 示例")
    print("=" * 60)

    compiler = LLMCompiler(llm_client=llm)
    compiler.run("如何准备一场技术面试？")
