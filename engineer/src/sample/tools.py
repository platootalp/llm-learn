"""
工具管理模块

本模块提供统一的工具注册、描述管理和执行机制，支持 ReAct 等智能体范式动态调用外部能力。
所有工具需满足：Callable[[str], str] 签名，即接收一个字符串输入，返回字符串结果。
"""
import datetime
from typing import Callable, Dict
from tavily import TavilyClient


class ToolExecutor:
    """
    工具执行器：统一管理智能体可调用的外部工具。

    设计说明：
    - 每个工具由名称（name）唯一标识，便于 LLM 在 Action 中引用；
    - 工具函数必须接受单个字符串参数并返回字符串结果，确保与 LLM 输出格式兼容；
    - 内置异常处理，避免单个工具失败导致整个智能体崩溃。
    """

    def __init__(self):
        """初始化空的工具注册表和描述字典。"""
        self.tools: Dict[str, Callable[[str], str]] = {}
        self.descriptions: Dict[str, str] = {}

    def register_tool(self, name: str, func: Callable[[str], str], description: str):
        """
        注册一个新工具。

        参数:
            name (str): 工具名称，必须与 LLM 生成的 Action 中的工具名一致（如 "Search"）。
            func (Callable[[str], str]): 工具函数，接收字符串输入，返回字符串结果。
            description (str): 工具的简要描述，用于构造 LLM 的提示词，应清晰说明其功能和输入格式。
        """
        self.tools[name] = func
        self.descriptions[name] = description

    def get_tool_descriptions(self) -> str:
        """
        获取所有已注册工具的描述字符串，用于注入到 LLM 提示词中。

        返回:
            str: 格式化后的工具列表，每行一个工具，格式为 "- {name}: {description}"。
        """
        return "\n".join(f"- {name}: {desc}" for name, desc in self.descriptions.items())

    def execute_tool(self, name: str, input_str: str) -> str:
        """
        执行指定名称的工具，并返回其结果。

        参数:
            name (str): 要执行的工具名称。
            input_str (str): 传递给工具的输入字符串（通常来自 LLM 生成的 Action 参数）。

        返回:
            str: 工具执行结果。若工具不存在或执行出错，返回错误信息字符串（而非抛出异常），
                 以保证智能体循环的鲁棒性。
        """
        if name not in self.tools:
            return f"Error: Tool '{name}' not found."
        try:
            return self.tools[name](input_str)
        except Exception as e:
            return f"Tool execution error: {str(e)}"


def create_tavily_search_tool(api_key: str) -> Callable[[str], str]:
    """
    创建基于 Tavily API 的网络搜索工具。

    Tavily 是专为 LLM 应用设计的搜索 API，返回简洁、相关的文本摘要，适合用于 ReAct 等范式。
    本工具封装了 Tavily 的 basic 搜索模式，限制返回最多 3 条结果，平衡信息量与上下文长度。

    参数:
        api_key (str): Tavily API 密钥，需从 https://tavily.com/ 获取。

    返回:
        Callable[[str], str]: 一个符合工具规范的搜索函数，接收查询字符串，返回搜索结果摘要。
    """
    client = TavilyClient(api_key=api_key)

    def search(query: str) -> str:
        """
        执行网络搜索。

        参数:
            query (str): 用户查询或 LLM 生成的搜索关键词。

        返回:
            str: 拼接的搜索结果内容（每条结果的 "content" 字段），若无结果则返回提示信息。
        """
        resp = client.search(query=query, search_depth="basic", max_results=3)
        results = resp.get("results", [])
        if not results:
            return "No relevant information found."
        # 提取每条结果的文本内容并拼接
        return "\n".join(r["content"] for r in results)

    return search


def create_date_diff_tool() -> Callable[[str], str]:
    """
    创建一个计算两个日期之间天数差的工具。

    输入格式要求：
        两个日期，用英文逗号分隔，例如："2025-01-01, 2025-12-31"
        日期支持格式：YYYY-MM-DD 或 YYYY/MM/DD

    返回：
        两日期相差的天数（整数）。若第一个日期在第二个之后，结果为负数。
        如果日期格式无效，返回错误提示。
    """

    def date_diff(input_str: str) -> str:
        try:
            # 分割输入，预期两个日期
            parts = [part.strip() for part in input_str.split(",")]
            if len(parts) != 2:
                return "Error: Please provide exactly two dates separated by a comma, e.g., '2025-01-01, 2025-12-31'."

            date1_str, date2_str = parts

            # 统一替换 / 为 -，便于解析
            date1_str = date1_str.replace("/", "-")
            date2_str = date2_str.replace("/", "-")

            # 解析日期
            date1 = datetime.datetime.strptime(date1_str, "%Y-%m-%d").date()
            date2 = datetime.datetime.strptime(date2_str, "%Y-%m-%d").date()

            # 计算差值（date2 - date1）
            delta = date2 - date1
            return str(delta.days)

        except ValueError as e:
            return f"Error: Invalid date format. Please use 'YYYY-MM-DD' or 'YYYY/MM/DD', e.g., '2025-01-01, 2025-12-31'."

    return date_diff
