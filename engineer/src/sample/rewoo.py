"""
Reason without Observation Agent 示例实现
"""
import os
import re
from typing import Dict, Any
from dotenv import load_dotenv
from qwen_llm import QwenLLM


# 模拟工具（实际可替换为 API 调用）
def mock_weather_tool(city: str) -> str:
    return f"今天 {city} 的天气晴朗，气温 25°C。"


def mock_search_tool(query: str) -> str:
    if "防晒" in query:
        return "专家建议：晴天外出应涂抹 SPF30+ 防晒霜，并戴帽子。"
    return "未找到相关信息。"


TOOL_REGISTRY = {
    "get_weather": mock_weather_tool,
    "search": mock_search_tool,
}

# ====== 1. Planner Prompt（生成带占位符的 Plan）======
PLANNER_PROMPT_TEMPLATE = """
你是一个高效的任务规划器。你的目标是生成一个完整的推理计划，用于解决用户的问题。
在计划中，你可以使用以下工具（按需调用）：
- get_weather(city): 获取某城市的当前天气
- search(query): 搜索相关信息

请按以下格式输出计划，仅使用工具调用和自然语言推理，不要直接给出最终答案：

Plan:
1. [步骤1描述] → ${{e1}}
2. [步骤2描述] → ${{e2}}
...
Final Answer: 根据以上信息，[简要说明如何得出答案]

问题: {question}
"""


# ====== 2. ReWOO Agent ======
class ReWOOAgent:
    def __init__(self, llm_client: QwenLLM):
        self.llm_client = llm_client

    def _generate_plan(self, question: str) -> str:
        prompt = PLANNER_PROMPT_TEMPLATE.format(question=question)
        messages = [{"role": "user", "content": prompt}]
        plan = self.llm_client.think(messages)
        return plan

    def _parse_plan(self, plan: str) -> tuple[list, str]:
        # 提取步骤（含占位符和工具调用）
        steps = []
        for line in plan.split("\n"):
            if "→ ${e" in line:
                # 匹配两种格式:
                # 1. "1. 获取北京天气 → ${e1}"
                # 2. "1. 获取北京天气 → ${e1 = get_weather("北京")}"
                match = re.search(r"(.+?)→\s*\$\{e(\d+)\s*=?([^}]*)}", line)
                if match:
                    desc = match.group(1).strip()
                    var_id = int(match.group(2))
                    tool_call = match.group(3).strip()
                    steps.append((var_id, desc, tool_call))
        # 提取 Final Answer 模板
        final_match = re.search(r"Final Answer:\s*(.*)", plan, re.DOTALL)
        final_template = final_match.group(1).strip() if final_match else ""
        return steps, final_template

    def _execute_plan(self, steps: list[tuple[int, str, str]]) -> Dict[str, str]:
        results: Dict[str, str] = {}
        for var_id, desc, tool_call in sorted(steps, key=lambda x: x[0]):
            if "get_weather" in tool_call:
                city = re.search(r"[\u4e00-\u9fa5a-zA-Z]+", tool_call.replace("get_weather", "").replace("(", "").replace(")", "").replace('"', ""))
                city_name = city.group(0) if city else "北京"
                results[f"e{var_id}"] = TOOL_REGISTRY["get_weather"](city_name)
            elif "search" in tool_call:
                query = re.search(r"[\u4e00-\u9fa5a-zA-Z0-9\s]+", tool_call.replace("search", "").replace("(", "").replace(")", "").replace('"', ""))
                query_str = query.group(0).strip() if query else "防晒建议"
                results[f"e{var_id}"] = TOOL_REGISTRY["search"](query_str)
            else:
                results[f"e{var_id}"] = "无需工具，纯推理步骤（本示例未实现）"
        return results

    def run(self, question: str) -> str:
        print("=== Step 1: 生成 Plan ===")
        plan = self._generate_plan(question)
        print(plan)

        print("\n=== Step 2: 解析并执行 Plan ===")
        steps, final_template = self._parse_plan(plan)
        evidence = self._execute_plan(steps)

        print(f"\nfinal Answer 模板: {final_template}")
        print(f"\nevidence: {evidence}")

        # 填充占位符
        final_context = final_template
        for key, value in evidence.items():
            final_context = final_context.replace(f"${{{key}}}", value)

        print(f"\n填充后的上下文: {final_context}")

        print("\n=== Step 3: 生成最终答案 ===")
        solver_prompt = f"基于以下信息，直接回答问题：\n{final_context}"
        final_answer = self.llm_client.think([{"role": "user", "content": solver_prompt}])
        print(final_answer)
        return final_answer


# ====== 3. 主程序 ======
if __name__ == "__main__":
    load_dotenv()
    api_key = os.getenv("DASHSCOPE_API_KEY")
    base_url = os.getenv("DASHSCOPE_API_URL")
    llm = QwenLLM(api_key=api_key, base_url=base_url, model_name="qwen-plus")

    print("=" * 60)
    print("ReWOO Agent 示例（Reason without Observation）")
    print("特点：先规划 → 再执行（调用工具）→ 最后回答")
    print("=" * 60)

    agent = ReWOOAgent(llm)
    agent.run("在北京今天出门需要涂防晒霜吗？")
