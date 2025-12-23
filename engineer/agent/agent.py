# 智能旅行助手 - Travel Assistant Agent
"""
一个功能完善的智能旅行助手，能够根据用户需求提供旅游建议和信息查询服务。
"""

import os
import logging
import re
from typing import Dict, Any, Optional, List
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

# 导入自定义工具、工厂和配置
from util.llm_factory import llm_factory
from .tools import get_tools
from .config import AgentConfig

# 配置日志
logging.basicConfig(level=getattr(logging, AgentConfig.LOG_LEVEL), format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class TravelAssistantAgent:
    """
    智能旅行助手类，提供完整的旅行规划和信息查询功能。
    
    功能特点：
    - 基于LLMFactory的统一模型管理
    - 支持多轮对话和上下文记忆
    - 集成天气查询和景点推荐工具
    - 结构化的工具调用和响应处理
    - 可配置的系统提示词和模型参数
    
    Attributes:
        model_name: 使用的LLM模型名称
        thread_id: 对话线程ID，用于记忆管理
        agent_executor: 智能代理执行器实例
        model: LLM模型实例
        tools: 可用工具列表
    """
    
    # 从配置类导入系统提示词
    SYSTEM_PROMPT = AgentConfig.SYSTEM_PROMPT
    
    def __init__(self, model_name: Optional[str] = None, thread_id: Optional[str] = None):
        """
        初始化旅行助手
        
        Args:
            model_name: 使用的LLM模型名称（默认使用配置中的DEFAULT_MODEL_NAME）
            thread_id: 对话线程ID，用于记忆管理（默认使用配置中的DEFAULT_THREAD_ID）
        """
        self.model_name = model_name or AgentConfig.DEFAULT_MODEL_NAME
        self.thread_id = thread_id or AgentConfig.DEFAULT_THREAD_ID
        self.agent_executor = None
        
        # 初始化模型和代理
        self._initialize_agent()
    
    def _initialize_agent(self) -> None:
        """
        初始化智能代理和工具
        
        该方法执行以下操作：
        1. 从LLMFactory获取模型实例
        2. 加载可用工具列表
        3. 创建带记忆的智能代理执行器
        
        Raises:
            RuntimeError: 初始化过程中发生任何错误时抛出
        """
        try:
            # 获取模型实例
            logger.info(f"Initializing travel assistant with model: {self.model_name}")
            self.model = llm_factory.get_model(self.model_name)
            logger.debug(f"Model {self.model_name} loaded successfully")
            
            # 定义工具列表
            logger.info("Loading tools...")
            self.tools = get_tools()
            logger.debug(f"Loaded {len(self.tools)} tools: {[tool.name for tool in self.tools]}")
            
            # 创建带记忆的代理执行器
            logger.info("Creating agent executor...")
            memory = MemorySaver()
            self.agent_executor = create_react_agent(
                self.model, 
                self.tools, 
                checkpointer=memory,
                system_message=self.SYSTEM_PROMPT
            )
            
            logger.info("Travel assistant initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize travel assistant: {e}", exc_info=True)
            raise RuntimeError(f"Travel assistant initialization failed: {str(e)}") from e
    
    def process_request(self, user_query: str) -> List[Dict[str, Any]]:
        """
        处理用户请求并返回响应
        
        Args:
            user_query: 用户的旅行相关问题
            
        Returns:
            List[Dict[str, Any]]: 包含代理响应的列表，每个响应包含以下字段：
                - type: 消息类型（"human", "ai", "tool", "error"）
                - content: 响应内容
                - timestamp: 消息标识（使用消息ID）
                
        Examples:
            >>> agent = TravelAssistantAgent()
            >>> response = agent.process_request("北京天气怎么样？")
            >>> print(response[0]["content"])
            北京当前天气：晴，气温 20°C，湿度 50%，风速 10 km/h
        """
        if not user_query:
            logger.warning("Received empty user query")
            return [{"type": "error", "content": "请输入有效的旅行问题"}]
            
        logger.info(f"Processing user request: {user_query}")
        
        # 配置对话上下文
        config = {"configurable": {"thread_id": self.thread_id}}
        
        # 处理响应
        results = []
        try:
            logger.info(f"Streaming response for thread: {self.thread_id}")
            step_count = 0
            
            for step in self.agent_executor.stream(
                    {"messages": [HumanMessage(content=user_query)]},
                    config,
                    stream_mode=AgentConfig.STREAM_MODE,
            ):
                step_count += 1
                message = step["messages"][-1]
                logger.debug(f"Step {step_count}: Received {message.type} message - {message.content[:50]}...")
                
                results.append({
                    "type": message.type,
                    "content": message.content,
                    "timestamp": message.id  # 使用消息ID作为时间戳标识
                })
            
            logger.info(f"Completed processing request in {step_count} steps")
        except Exception as e:
            logger.error(f"Error processing request: {e}", exc_info=True)
            error_msg = f"处理请求时发生错误: {str(e)}"
            
            # 提供更具体的错误信息
            if isinstance(e, KeyError):
                error_msg += "（可能是数据格式错误）"
            elif isinstance(e, RuntimeError):
                error_msg += "（运行时错误）"
            elif isinstance(e, ImportError):
                error_msg += "（缺少依赖包）"
            
            results.append({
                "type": "error",
                "content": error_msg
            })
        
        return results
    
    def get_response_content(self, results: List[Dict[str, Any]]) -> str:
        """
        从处理结果中提取最终响应内容
        
        Args:
            results: 处理请求的结果列表，由process_request方法返回
            
        Returns:
            str: 最终的文本响应内容，优先返回最后一个AI或工具响应
            
        Examples:
            >>> agent = TravelAssistantAgent()
            >>> results = agent.process_request("上海有什么好玩的？")
            >>> response = agent.get_response_content(results)
            >>> print(response)
            上海有很多值得一去的景点，推荐您去外滩、东方明珠和豫园等。
        """
        for result in reversed(results):
            if result["type"] in ["ai", "tool"]:
                return result["content"]
        return "抱歉，未能生成有效响应。"
    
    def plan_trip(self, destination: str, travel_days: int, interests: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        规划完整的旅行行程
        
        Args:
            destination: 目的地城市
            travel_days: 旅行天数
            interests: 用户感兴趣的活动类型列表（可选）
            
        Returns:
            List[Dict[str, Any]]: 包含规划结果的响应列表，格式与process_request方法返回结果一致
            
        Examples:
            >>> agent = TravelAssistantAgent()
            >>> results = agent.plan_trip("杭州", 3, ["自然风光", "美食"])
            >>> print(agent.get_response_content(results))
            3天杭州之旅行程规划：
            第一天：西湖游览...
            第二天：灵隐寺...
            第三天：杭州美食之旅...
        """
        logger.info(f"Planning trip to {destination} for {travel_days} days, interests: {interests}")
        
        # 构造旅行规划请求
        interest_str = ", ".join(interests) if interests else "自然风光和文化景点"
        query = f"帮我规划一次{travel_days}天的{destination}之旅，我对{interest_str}感兴趣。请提供详细的每日行程安排，包括推荐的景点、美食和交通建议。"
        
        # 使用现有的process_request方法处理
        return self.process_request(query)




def plan_agent(model_name: Optional[str] = None) -> Any:
    """
    创建一个专门用于旅行规划的智能代理
    
    Args:
        model_name: 使用的LLM模型名称，默认为配置中的DEFAULT_MODEL_NAME
        
    Returns:
        Any: 创建的智能代理执行器实例
        
    Raises:
        RuntimeError: 代理创建过程中发生错误时抛出
        
    Examples:
        >>> agent = plan_agent()
        >>> result = agent.invoke("帮我规划上海3日游")
        >>> print(result)
        上海3日游行程规划：...
    """
    try:
        # 使用配置中的默认模型名称
        actual_model_name = model_name or AgentConfig.DEFAULT_MODEL_NAME
        logger.info(f"Creating travel planning agent with model: {actual_model_name}")
        
        # 获取模型实例
        model = llm_factory.get_model(actual_model_name)
        logger.debug(f"Model {actual_model_name} loaded successfully for planning agent")
        
        # 定义旅行规划工具列表
        tools = get_tools()
        logger.debug(f"Loaded {len(tools)} tools for planning agent: {[tool.name for tool in tools]}")
        
        # 创建代理执行器
        memory = MemorySaver()
        agent_executor = create_react_agent(
            model, 
            tools, 
            checkpointer=memory,
            system_message=TravelAssistantAgent.SYSTEM_PROMPT
        )
        
        logger.info("Travel planning agent created successfully")
        return agent_executor
    except Exception as e:
        logger.error(f"Failed to create travel planning agent: {e}", exc_info=True)
        raise RuntimeError(f"Travel planning agent creation failed: {str(e)}") from e


# 命令行测试入口
def main() -> None:
    """
    命令行测试旅行助手功能
    
    该函数提供一个交互式命令行界面，用户可以输入旅行问题，获取智能助手的回答。
    支持的命令：
    - 旅行相关问题（如："北京天气怎么样？", "上海有什么好玩的？"）
    - "退出"、"quit"或"exit"：结束对话
    
    Examples:
        $ python agent.py
        === 智能旅行助手 ===
        输入您的旅行问题，输入 '退出' 结束对话
        ==============================
        
        您的问题: 北京天气怎么样？
        助手回答: 北京当前天气：晴，气温 20°C，湿度 50%，风速 10 km/h
        
        您的问题: 退出
        感谢使用智能旅行助手，再见！
    """
    print("=== 智能旅行助手 ===")
    print("输入您的旅行问题，输入 '退出' 结束对话")
    print("=" * 30)
    
    # 初始化助手
    agent = TravelAssistantAgent(thread_id="test_thread")
    
    while True:
        try:
            user_input = input("\n您的问题: ").strip()
            if user_input.lower() in ["退出", "quit", "exit"]:
                print("感谢使用智能旅行助手，再见！")
                break
            
            if not user_input:
                continue
            
            # 处理请求
            results = agent.process_request(user_input)
            response = agent.get_response_content(results)
            
            # 显示响应
            print("\n助手回答:")
            print(response)
            
        except KeyboardInterrupt:
            print("\n感谢使用智能旅行助手，再见！")
            break
        except Exception as e:
            print(f"发生错误: {str(e)}")


if __name__ == "__main__":
    main()
