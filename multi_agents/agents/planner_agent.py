"""
Planner Agent - 需求分析与架构设计专家
"""
import os
from pathlib import Path
from typing import Dict, List, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()


class PlannerAgent:
    def __init__(self, model: Optional[ChatOpenAI] = None):
        self.llm = model or ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4"),
            temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
        )
        self.prompt_path = Path(__file__).parent.parent / "prompts" / "planner.md"
        self._load_prompt()

    def _load_prompt(self):
        if self.prompt_path.exists():
            with open(self.prompt_path, "r", encoding="utf-8") as f:
                self.system_prompt = f.read()
        else:
            self.system_prompt = self._get_default_prompt()

    def _get_default_prompt(self) -> str:
        return """你是一位经验丰富的系统架构师，擅长需求分析和架构设计。"""

    def analyze_requirements(self, user_request: str) -> Dict:
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", f"请分析以下需求并提供技术方案：\n\n{user_request}")
        ])
        chain = prompt | self.llm
        response = chain.invoke({})
        return {"analysis": response.content, "status": "completed"}

    def design_architecture(self, requirements: str) -> Dict:
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", f"请为以下需求设计系统架构：\n\n{requirements}")
        ])
        chain = prompt | self.llm
        response = chain.invoke({})
        return {"architecture": response.content, "status": "completed"}

    def decompose_tasks(self, requirements: str) -> List[Dict]:
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", f"请将以下需求分解为可执行的任务清单：\n\n{requirements}")
        ])
        chain = prompt | self.llm
        response = chain.invoke({})
        tasks = self._parse_tasks(response.content)
        return tasks

    def _parse_tasks(self, content: str) -> List[Dict]:
        tasks = []
        lines = content.split("\n")
        for line in lines:
            if line.strip().startswith(("T-", "- [ ]", "- ")):
                task = {
                    "id": len(tasks) + 1,
                    "description": line.strip(),
                    "status": "pending"
                }
                tasks.append(task)
        if not tasks:
            tasks = [{"id": 1, "description": content, "status": "pending"}]
        return tasks

    def generate_spec_document(self, project_name: str, requirements: str) -> str:
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", f"""请为项目「{project_name}」生成完整的技术规范文档。

需求：\n{requirements}

请包含：
1. 项目概述
2. 功能需求详述
3. 技术选型
4. 系统架构
5. 任务分解
6. 迭代计划
7. 验收标准
""")
        ])
        chain = prompt | self.llm
        response = chain.invoke({})
        return response.content

    def discuss_with_pm(self, topic: str, current_context: str) -> str:
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", f"""当前讨论主题：{topic}

项目背景：\n{current_context}

请提供你的专业分析和建议。""")
        ])
        chain = prompt | self.llm
        response = chain.invoke({})
        return response.content
