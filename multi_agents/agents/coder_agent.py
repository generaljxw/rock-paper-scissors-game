"""
Coder Agent - 高级全栈开发工程师
"""
import os
from pathlib import Path
from typing import Dict, List, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()


class CoderAgent:
    def __init__(self, model: Optional[ChatOpenAI] = None):
        self.llm = model or ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4"),
            temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
        )
        self.prompt_path = Path(__file__).parent.parent / "prompts" / "coder.md"
        self.project_root = Path(os.getenv("PROJECT_ROOT", "c:/Code/TRAE/RockPaperScissors"))
        self._load_prompt()

    def _load_prompt(self):
        if self.prompt_path.exists():
            with open(self.prompt_path, "r", encoding="utf-8") as f:
                self.system_prompt = f.read()
        else:
            self.system_prompt = self._get_default_prompt()

    def _get_default_prompt(self) -> str:
        return """你是一位资深的高级全栈开发工程师。"""

    def implement_feature(self, task_description: str, spec: str) -> Dict:
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", f"""请根据以下任务描述和技术规范实现功能：

任务描述：\n{task_description}

技术规范：\n{spec}

请提供：
1. 详细的实现方案
2. 代码结构设计
3. 关键代码片段（如需要）
""")
        ])
        chain = prompt | self.llm
        response = chain.invoke({})
        return {
            "implementation": response.content,
            "status": "completed",
            "files_created": []
        }

    def review_code(self, code_snippet: str) -> Dict:
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", f"请审查以下代码并提供改进建议：\n\n{code_snippet}")
        ])
        chain = prompt | self.llm
        response = chain.invoke({})
        return {"review": response.content, "suggestions": []}

    def create_file(self, file_path: str, content: str) -> Dict:
        full_path = self.project_root / file_path
        try:
            full_path.parent.mkdir(parents=True, exist_ok=True)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
            return {
                "status": "success",
                "file_path": str(full_path),
                "message": f"文件已创建: {file_path}"
            }
        except Exception as e:
            return {
                "status": "error",
                "file_path": str(full_path),
                "message": f"创建失败: {str(e)}"
            }

    def read_file(self, file_path: str) -> Optional[str]:
        full_path = self.project_root / file_path
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            return None

    def update_file(self, file_path: str, old_content: str, new_content: str) -> Dict:
        full_path = self.project_root / file_path
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                current = f.read()
            if old_content not in current:
                return {"status": "error", "message": "未找到要替换的内容"}
            new_file_content = current.replace(old_content, new_content)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(new_file_content)
            return {
                "status": "success",
                "file_path": str(full_path),
                "message": f"文件已更新: {file_path}"
            }
        except Exception as e:
            return {"status": "error", "message": f"更新失败: {str(e)}"}

    def discuss_implementation(self, topic: str, context: str) -> str:
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", f"""讨论主题：{topic}

当前上下文：\n{context}

请提供你的技术分析和实现建议。""")
        ])
        chain = prompt | self.llm
        response = chain.invoke({})
        return response.content

    def estimate_effort(self, task_description: str) -> Dict:
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", f"请评估以下任务的开发工作量：\n\n{task_description}\n\n请给出工时估算和复杂度评级。")
        ])
        chain = prompt | self.llm
        response = chain.invoke({})
        return {"estimation": response.content, "status": "completed"}
