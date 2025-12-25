"""
ReAct Agent 示例实现
- Thought-Action-Observation 循环
- 支持工具调用
"""

import os
import re
from typing import Dict, Callable, List
from dotenv import load_dotenv
from qwen_llm import QwenLLM


# =========================
# ReAct 提示词模板
# =========================

REACT_PROMPT_TEMPLATE = """
你是一个有能力调用外部工具的智能助手。

可用工具如下:
{tools}

请严格按照以下格式进行回应:
Thought: 你的思考过程，用于分析问题、拆解任务和规划下一步行动。
Action: 你决定采取的行动，必须是以下格式之一:
    - ToolName[tool_input]
    - Finish[final_answer]

现在，请开始解决以下问题:
Question: {question}
History:{history}
"""


# =========================
# 工具执行器
# =========================

class ToolExecutor:
    """
    统一管理和执行工具
    """

    def __init__(self):
        self.tools: Dict[str, Callable[[str], str]] = {}
        self.descriptions: Dict[str, str] = {}

    def register_tool(self, name: str, func: Callable[[str], str], description: str):
        self.tools[name] = func
        self.descriptions[name] = description

    def getAvailableTools(self) -> str:
        return "\n".join(
            f"- {name}: {desc}"
            for name, desc in self.descriptions.items()
        )

    def getTool(self, name: str):
        return self.tools.get(name)


# =========================
# 示例工具实现
# =========================

def search_tool(query: str) -> str:
    # 示例搜索工具（真实环境可接入 SerpAPI / 内部搜索服务）
    if "华为" in query:
        return (
            "Mate 70 和 Pura 80 Pro+ 是华为最新旗舰系列；"
            "Mate 70 主打顶级影像与耐用性，"
            "Pura 80 Pro+ 强调先锋影像能力。"
        )
    return "未找到相关信息"


# =========================
# ReAct Agent 实现
# =========================

class ReActAgent:
    def __init__(
            self,
            llm_client: QwenLLM,
            tool_executor: ToolExecutor,
            max_steps: int = 5
    ):
        self.llm_client = llm_client
        self.tool_executor = tool_executor
        self.max_steps = max_steps
        self.history: List[str] = []

    def run(self, question: str):
        """
        运行 ReAct 智能体主循环
        """
        self.history = []
        current_step = 0

        while current_step < self.max_steps:
            current_step += 1

            # 1. 构造 Prompt
            tools_desc = self.tool_executor.getAvailableTools()
            history_str = "\n".join(self.history)

            prompt = REACT_PROMPT_TEMPLATE.format(
                tools=tools_desc,
                question=question,
                history=history_str
            )

            print(f"\n--- 第 {current_step} 次调用 ---")

            # 2. 调用 qwen-plus LLM
            response_text = self.llm_client.think(
                messages=[{"role": "user", "content": prompt}]
            )

            if not response_text:
                break

            # 3. 解析 Thought / Action
            thought, action = self._parse_output(response_text)

            if not action:
                break

            # 4. 执行 Action
            if action.startswith("Finish"):
                final_answer = re.match(r"Finish\[(.*)]", action).group(1)
                print(f"thought: {thought}")
                print(f"action: {action}")
                return final_answer

            tool_name, tool_input = self._parse_action(action)

            tool_func = self.tool_executor.getTool(tool_name)
            if not tool_func:
                observation = f"错误: 未找到工具 {tool_name}"
            else:
                observation = tool_func(tool_input)

            # 5. 整合 Observation
            print(f"thought: {thought}")
            print(f"action: {action}")
            print(f"observation: {observation}")

            # 将本轮的 Thought, Action 和 Observation 添加到历史记录中
            self.history.append(f"Thought: {thought}")
            self.history.append(f"Action: {action}")
            self.history.append(f"Observation: {observation}")

        print("超过最大步数，流程终止。")
        return None

    def _parse_output(self, text: str):
        """
        从 LLM 输出中解析 Thought 和 Action
        """
        thought_match = re.search(r"Thought:\s*(.*)", text)
        action_match = re.search(r"Action:\s*(.*)", text)

        thought = thought_match.group(1).strip() if thought_match else None
        action = action_match.group(1).strip() if action_match else None

        return thought, action

    def _parse_action(self, action_text: str):
        """
        从 Action 中解析工具名和输入
        """
        match = re.match(r"(\w+)\[(.*)\]", action_text)
        if match:
            return match.group(1), match.group(2)
        return None, None


# =========================
# 示例运行
# =========================

if __name__ == "__main__":
    load_dotenv()
    api_key = os.getenv("DASHSCOPE_API_KEY")
    base_url = os.getenv("DASHSCOPE_API_URL")

    llm = QwenLLM(api_key=api_key, base_url=base_url, model_name="qwen-plus")

    executor = ToolExecutor()
    executor.register_tool(
        name="Search",
        func=search_tool,
        description="用于搜索最新的外部信息"
    )

    agent = ReActAgent(
        llm_client=llm,
        tool_executor=executor,
        max_steps=5
    )

    question = "华为最新的手机是哪一款？它的主要卖点是什么？"
    answer = agent.run(question)

    print(f"\n--- 最终答案  ---")
    print(f" {answer}")
