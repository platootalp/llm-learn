# Import relevant functionality
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage
from langchain_community.tools.tavily_search import TavilySearchResults

from util import get_qwen_model

# 初始化模型
model = get_qwen_model()

# 工具列表
search = TavilySearchResults(max_results=2)
tools = [search]

# agent + memory
memory = MemorySaver()
agent_executor = create_react_agent(model, tools, checkpointer=memory)

# 执行参数
config = {"configurable": {"thread_id": "abc123"}}

# 使用 agent
if __name__ == "__main__":
    for step in agent_executor.stream(
        {"messages": [HumanMessage(content="你好，今天中国恒生指数多少个点")]},
        config,
        stream_mode="values",
    ):
        step["messages"][-1].pretty_print()


