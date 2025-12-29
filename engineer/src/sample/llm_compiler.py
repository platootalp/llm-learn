"""
LLMCompiler Agent 示例实现
- Function Calling Planner: 生成 DAG 表示任务依赖关系
- Task Fetching Unit: 动态调度无依赖任务进行并行执行
- Joining Unit: 聚合依赖结果并触发后续调用
"""

import os
import re
from typing import List, Dict, Any, Set
from dataclasses import dataclass, field
from collections import defaultdict, deque
from dotenv import load_dotenv
from qwen_llm import QwenLLM


PLANNER_PROMPT = """
你是一个任务规划专家。你的任务是将复杂问题分解为多个子任务，并明确它们之间的依赖关系。

问题: {question}

请将问题分解为多个子任务，并构建一个有向无环图（DAG）来表示任务之间的依赖关系。
- 如果任务 A 依赖任务 B 的结果，则表示为 A → B
- 没有依赖的任务可以并行执行
- 每个任务都应该有明确的执行目标

请按照以下格式输出:
```python
{{
    "tasks": [
        {{"id": "task1", "description": "子任务1描述", "dependencies": []}},
        {{"id": "task2", "description": "子任务2描述", "dependencies": ["task1"]}},
        {{"id": "task3", "description": "子任务3描述", "dependencies": ["task1"]}},
        {{"id": "task4", "description": "子任务4描述", "dependencies": ["task2", "task3"]}}
    ]
}}
```

注意：
- dependencies 列表中的任务 ID 必须在 tasks 中定义
- 确保生成的图是有向无环图（DAG），不能有循环依赖
- 尽量最大化可以并行执行的任务数量
"""


TASK_EXECUTION_PROMPT = """
你是一个任务执行专家。你的任务是执行给定的子任务。

子任务: {task_description}

请仅输出该子任务的执行结果，不要包含任何额外解释。
"""


@dataclass
class Task:
    id: str
    description: str
    dependencies: List[str] = field(default_factory=list)
    result: str = ""
    completed: bool = False


class DAG:
    def __init__(self, tasks: List[Dict[str, Any]]):
        self.tasks: Dict[str, Task] = {}
        self.adjacency: Dict[str, Set[str]] = defaultdict(set)
        self.reverse_adjacency: Dict[str, Set[str]] = defaultdict(set)
        
        for task_data in tasks:
            task = Task(
                id=task_data["id"],
                description=task_data["description"],
                dependencies=task_data.get("dependencies", [])
            )
            self.tasks[task.id] = task
            
            for dep in task.dependencies:
                self.adjacency[task.id].add(dep)
                self.reverse_adjacency[dep].add(task.id)
    
    def get_ready_tasks(self) -> List[Task]:
        ready = []
        for task_id, task in self.tasks.items():
            if not task.completed and all(self.tasks[dep].completed for dep in task.dependencies):
                ready.append(task)
        return ready
    
    def is_complete(self) -> bool:
        return all(task.completed for task in self.tasks.values())
    
    def mark_complete(self, task_id: str, result: str):
        if task_id in self.tasks:
            self.tasks[task_id].completed = True
            self.tasks[task_id].result = result


class FunctionCallingPlanner:
    def __init__(self, llm_client: QwenLLM):
        self.llm_client = llm_client
    
    def plan(self, question: str) -> DAG:
        prompt = PLANNER_PROMPT.format(question=question)
        response = self.llm_client.think([{"role": "user", "content": prompt}])
        
        tasks_data = self._extract_tasks(response)
        dag = DAG(tasks_data)
        
        print(f"\n--- Function Calling Planner: 任务规划 ---")
        for task_id, task in dag.tasks.items():
            deps = task.dependencies
            deps_str = f" (依赖: {', '.join(deps)})" if deps else " (无依赖)"
            print(f"  {task_id}: {task.description}{deps_str}")
        
        parallel_groups = self._identify_parallel_groups(dag)
        print(f"\n--- 并行执行计划 ---")
        for i, group in enumerate(parallel_groups, 1):
            task_ids = [t.id for t in group]
            print(f"  阶段 {i}: {', '.join(task_ids)} (可并行)")
        
        return dag
    
    def _extract_tasks(self, text: str) -> List[Dict[str, Any]]:
        match = re.search(r"```python\s*\{(.*?)\}\s*```", text, re.DOTALL)
        if match:
            try:
                tasks_str = "{" + match.group(1) + "}"
                data = eval(tasks_str)
                return data.get("tasks", [])
            except:
                return []
        return []
    
    def _identify_parallel_groups(self, dag: DAG) -> List[List[Task]]:
        groups = []
        remaining = set(dag.tasks.keys())
        
        while remaining:
            ready = [dag.tasks[tid] for tid in remaining if 
                    all(dag.tasks[dep].completed for dep in dag.tasks[tid].dependencies)]
            
            if not ready:
                break
            
            groups.append(ready)
            for task in ready:
                remaining.remove(task.id)
                task.completed = True
            
            for task in ready:
                task.completed = False
        
        for task in dag.tasks.values():
            task.completed = False
        
        return groups


class TaskFetchingUnit:
    def __init__(self, llm_client: QwenLLM):
        self.llm_client = llm_client
    
    def execute_ready_tasks(self, dag: DAG) -> List[Task]:
        ready_tasks = dag.get_ready_tasks()
        
        if not ready_tasks:
            return []
        
        print(f"\n--- Task Fetching Unit: 执行就绪任务 ---")
        for task in ready_tasks:
            print(f"  执行: {task.id} - {task.description}")
        
        executed_tasks = []
        for task in ready_tasks:
            result = self._execute_task(task)
            dag.mark_complete(task.id, result)
            executed_tasks.append(task)
        
        return executed_tasks
    
    def _execute_task(self, task: Task) -> str:
        prompt = TASK_EXECUTION_PROMPT.format(task_description=task.description)
        result = self.llm_client.think([{"role": "user", "content": prompt}])
        print(f"    结果: {result[:100]}..." if len(result) > 100 else f"    结果: {result}")
        return result


class JoiningUnit:
    def __init__(self, llm_client: QwenLLM):
        self.llm_client = llm_client
    
    def aggregate(self, question: str, dag: DAG) -> str:
        results_str = "\n".join(
            f"任务 {task.id}: {task.description}\n结果: {task.result}\n"
            for task in dag.tasks.values()
        )
        
        prompt = f"""
            基于以下子任务的执行结果，为原始问题提供完整的最终答案。
            
            原始问题: {question}
            
            子任务执行结果:
            {results_str}
            
            请提供完整、准确的最终答案，整合所有子任务的结果:
        """
        final_answer = self.llm_client.think([{"role": "user", "content": prompt}])
        
        print(f"\n--- Joining Unit: 最终答案 ---")
        print(f"{final_answer}")
        return final_answer


class LLMCompiler:
    def __init__(self, llm_client: QwenLLM):
        self.planner = FunctionCallingPlanner(llm_client)
        self.task_fetcher = TaskFetchingUnit(llm_client)
        self.joiner = JoiningUnit(llm_client)
    
    def run(self, question: str) -> str:
        print("=" * 60)
        print("LLMCompiler Agent - 并行任务执行")
        print("=" * 60)
        
        dag = self.planner.plan(question)
        
        print(f"\n--- 开始执行任务 DAG ---")
        iteration = 0
        while not dag.is_complete():
            iteration += 1
            print(f"\n迭代 {iteration}:")
            executed = self.task_fetcher.execute_ready_tasks(dag)
            
            if not executed:
                print("  没有可执行的任务，可能存在循环依赖")
                break
        
        final_answer = self.joiner.aggregate(question, dag)
        
        print(f"\n--- 执行完成 ---")
        print(f"总任务数: {len(dag.tasks)}")
        print(f"迭代次数: {iteration}")
        
        return final_answer


if __name__ == "__main__":
    load_dotenv()
    api_key = os.getenv("DASHSCOPE_API_KEY")
    base_url = os.getenv("DASHSCOPE_API_URL")

    llm = QwenLLM(api_key=api_key, base_url=base_url, model_name="qwen-plus")

    compiler = LLMCompiler(llm_client=llm)
    compiler.run("llm_compiler agent设计范式如何用Java代码实现")
