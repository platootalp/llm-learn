from langchain_core.runnables import RunnableConfig
from typing_extensions import Annotated, TypedDict
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph


# 定义一个用于更新状态的reducer函数
def reducer(a: list, b: int | None) -> list:
    if b is not None:
        return a + [b]
    return a


# 定义状态类
class State(TypedDict):
    x: Annotated[list, reducer]  # x是一个list类型，经过reducer处理


# 定义配置类
class ConfigSchema(TypedDict):
    r: float  # 配置项r是一个float类型


# 初始化状态图（StateGraph）并传入State类型和ConfigSchema
graph = StateGraph(state_schema=State, config_schema=ConfigSchema)


# 定义节点处理函数
def node(state: State, config: RunnableConfig) -> dict:
    r = config["configurable"].get("r", 1.0)  # 从配置中获取r的值，默认1.0
    x = state["x"][-1]  # 获取状态中的x列表的最后一个值
    next_value = x * r * (1 - x)  # 根据公式计算新的x值
    return {"x": next_value}  # 返回新的x值


# 向图中添加节点
graph.add_node("A", node)
graph.add_node("B", node)
graph.add_edge("A", "B")
graph.add_sequence([("C", node), ("D", node)])
graph.add_conditional_edges()
# 设置图的入口和结束点
graph.set_entry_point("A")
graph.set_finish_point("D")

# 编译图
compiled = graph.compile()

# 打印配置规范
print(compiled.config_specs)

# 使用输入状态和配置执行图，并打印结果
step1 = compiled.invoke({"x": 0.5}, {"configurable": {"r": 3.0}})

print(step1)
