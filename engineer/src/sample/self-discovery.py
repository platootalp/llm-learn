"""
Self-Discover - 大语言模型的自我发现推理框架
核心三阶段：
1. Select - 从原子推理模块库中选择与任务相关的模块
2. Adapt - 将选中的模块适应到具体任务
3. Implement - 使用适应后的推理结构解决问题
"""

import json
from typing import List, Dict, Any
from qwen_llm import QwenLLM


# =========================
# 原子推理模块库（40+ 个模块）
# =========================
REASONING_MODULES = {
    "Critical Thinking": "批判性思维：质疑假设，评估论据的有效性",
    "Step-by-step": "逐步推理：将复杂问题分解为可管理的步骤",
    "Chain of Thought": "思维链：逐步展示推理过程",
    "Decomposition": "问题分解：将复杂任务拆解为子任务",
    "Comparison": "对比分析：比较不同选项的优缺点",
    "Prioritization": "优先级排序：确定任务的重要性和执行顺序",
    "Causal Analysis": "因果分析：识别因果关系",
    "Abstraction": "抽象思维：从具体实例中提取一般规律",
    "Generalization": "泛化：将知识应用到新情境",
    "Analogy": "类比推理：通过类比解决问题",
    "Counterfactual": "反事实推理：考虑'如果...会怎样'的情景",
    "Constraint Checking": "约束检查：验证方案是否满足约束条件",
    "Resource Estimation": "资源估算：评估所需资源",
    "Risk Assessment": "风险评估：识别和评估潜在风险",
    "Feasibility Analysis": "可行性分析：评估方案的可实施性",
    "Synthesis": "综合整合：整合多个信息源",
    "Evaluation": "评估：评估解决方案的质量",
    "Refinement": "优化改进：改进现有方案",
    "Verification": "验证：验证解决方案的正确性",
    "Self-Correction": "自我修正：识别并纠正错误",
    "Goal Clarification": "目标明确：明确问题的目标和约束",
    "Information Gathering": "信息收集：收集相关信息",
    "Filtering": "信息筛选：筛选相关信息",
    "Organization": "信息组织：组织信息结构",
    "Pattern Recognition": "模式识别：识别数据中的模式",
    "Hypothesis Generation": "假设生成：提出可能的解释",
    "Testing": "测试验证：测试假设的有效性",
    "Inference": "推理推断：从已知信息推断未知信息",
    "Deduction": "演绎推理：从一般到特殊的推理",
    "Induction": "归纳推理：从特殊到一般的推理",
    "Abductive Reasoning": "溯因推理：寻找最佳解释",
    "Decision Making": "决策制定：在多个选项中做出选择",
    "Optimization": "优化：寻找最优解",
    "Simulation": "模拟：模拟系统行为",
    "Forecasting": "预测：预测未来趋势",
    "Planning": "规划：制定行动计划",
    "Scheduling": "调度：安排任务执行顺序",
    "Allocation": "资源分配：分配资源给任务",
    "Monitoring": "监控：监控执行过程",
    "Adjustment": "调整：根据反馈调整计划",
}


# =========================
# Self-Discover Agent
# =========================
class SelfDiscoverAgent:
    def __init__(self, llm_client: QwenLLM):
        self.llm = llm_client

    def select(self, task: str) -> List[str]:
        """
        Select 阶段：从原子推理模块库中选择与任务相关的模块
        
        输出：选中的模块列表
        """
        modules_list = "\n".join([f"- {name}: {desc}" for name, desc in REASONING_MODULES.items()])
        
        prompt = f"""
            你是一个推理架构师。请为以下任务选择最相关的原子推理模块。
            
            可用推理模块：
            {modules_list}
            
            任务：{task}
            
            请选择 3-5 个最相关的模块，按优先级排序。
            
            输出格式（严格 JSON）：
            {{
                "selected_modules": ["模块名1", "模块名2", ...]
            }}
        """
        
        response = self.llm.think([{"role": "user", "content": prompt}]).strip()
        
        try:
            json_match = self._extract_json(response)
            if json_match:
                data = json.loads(json_match)
                return data.get("selected_modules", [])
        except Exception as e:
            print(f"Select 阶段解析失败: {e}")
        
        return []

    def adapt(self, task: str, selected_modules: List[str]) -> Dict[str, Any]:
        """
        Adapt 阶段：将选中的模块适应到具体任务，生成推理结构
        
        输出：结构化的推理结构（JSON 格式）
        """
        modules_desc = "\n".join([
            f"- {name}: {REASONING_MODULES.get(name, '')}" 
            for name in selected_modules
        ])
        
        prompt = f"""
            你是一个推理结构设计专家。请将选中的推理模块适应到具体任务，生成一个推理结构。
            
            选中的模块：
            {modules_desc}
            
            任务：{task}
            
            请设计一个推理结构，将选中的模块按逻辑顺序组织，并为每个模块设计具体的推理步骤。
            
            输出格式（严格 JSON）：
            {{
                "reasoning_structure": [
                    {{
                        "module": "模块名",
                        "description": "该模块在当前任务中的具体作用",
                        "steps": ["步骤1", "步骤2", ...]
                    }},
                    ...
                ]
            }}
        """
        
        response = self.llm.think([{"role": "user", "content": prompt}]).strip()
        
        try:
            json_match = self._extract_json(response)
            if json_match:
                data = json.loads(json_match)
                return data.get("reasoning_structure", [])
        except Exception as e:
            print(f"Adapt 阶段解析失败: {e}")
        
        return []

    def implement(self, task: str, reasoning_structure: List[Dict]) -> str:
        """
        Implement 阶段：使用适应后的推理结构解决问题
        
        输出：最终答案
        """
        context = {
            "task": task,
            "intermediate_results": []
        }
        
        for i, stage in enumerate(reasoning_structure, 1):
            module_name = stage.get("module", "")
            description = stage.get("description", "")
            steps = stage.get("steps", [])
            
            print(f"\n[阶段 {i}] {module_name}")
            print(f"  描述: {description}")
            print(f"  步骤: {', '.join(steps)}")
            
            result = self._execute_stage(task, module_name, description, steps, context)
            print(f"  结果: {result[:200]}...")
            
            context["intermediate_results"].append({
                "stage": i,
                "module": module_name,
                "result": result
            })
        
        final_answer = self._generate_final_answer(task, context)
        return final_answer

    def _execute_stage(self, task: str, module_name: str, description: str, steps: List[str], context: Dict) -> str:
        """执行单个推理阶段"""
        previous_results = "\n".join([
            f"阶段 {r['stage']} ({r['module']}): {r['result']}"
            for r in context["intermediate_results"]
        ])
        
        prompt = f"""
            你是一个推理专家，正在执行 {module_name} 模块。
            
            任务：{task}
            
            模块描述：{description}
            
            推理步骤：
            {chr(10).join([f'{i+1}. {step}' for i, step in enumerate(steps)])}
            
            之前的推理结果：
            {previous_results if previous_results else "无"}
            
            请按照上述步骤进行推理，输出该阶段的推理结果。
        """
        
        return self.llm.think([{"role": "user", "content": prompt}]).strip()

    def _generate_final_answer(self, task: str, context: Dict) -> str:
        """生成最终答案"""
        reasoning_summary = "\n".join([
            f"阶段 {r['stage']} ({r['module']}):\n{r['result']}\n"
            for r in context["intermediate_results"]
        ])
        
        prompt = f"""
            请基于以下推理过程，生成最终答案。
            
            任务：{task}
            
            推理过程：
            {reasoning_summary}
            
            请给出最终答案，要求：
            1. 直接回答问题
            2. 基于推理过程
            3. 逻辑清晰
        """
        
        return self.llm.think([{"role": "user", "content": prompt}]).strip()

    def _extract_json(self, text: str) -> str:
        """从文本中提取 JSON"""
        import re
        json_match = re.search(r'\{[\s\S]*}', text)
        if json_match:
            return json_match.group(0)
        return ""

    def run(self, task: str) -> str:
        """运行完整的 Self-Discover 流程"""
        print("=" * 60)
        print("Self-Discover Agent")
        print("=" * 60)
        print(f"\n任务: {task}\n")
        
        print("=" * 60)
        print("Stage 1: Select - 选择相关推理模块")
        print("=" * 60)
        selected_modules = self.select(task)
        print(f"选中的模块: {', '.join(selected_modules)}")
        
        if not selected_modules:
            print("错误：未选中任何模块")
            return ""
        
        print("\n" + "=" * 60)
        print("Stage 2: Adapt - 适应推理模块到具体任务")
        print("=" * 60)
        reasoning_structure = self.adapt(task, selected_modules)
        print(f"推理结构包含 {len(reasoning_structure)} 个阶段")
        
        if not reasoning_structure:
            print("错误：未生成推理结构")
            return ""
        
        print("\n" + "=" * 60)
        print("Stage 3: Implement - 执行推理结构")
        print("=" * 60)
        final_answer = self.implement(task, reasoning_structure)
        
        print("\n" + "=" * 60)
        print("最终答案")
        print("=" * 60)
        print(final_answer)
        
        return final_answer


# =========================
# 示例运行
# =========================
if __name__ == "__main__":
    from dotenv import load_dotenv
    import os

    load_dotenv()
    llm = QwenLLM(
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        base_url=os.getenv("DASHSCOPE_API_URL"),
        model_name="qwen-plus"
    )

    agent = SelfDiscoverAgent(llm)
    agent.run("如何应对气候变化？")
