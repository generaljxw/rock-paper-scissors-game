"""
Reviewer Agent - 资深代码审查员
"""
import os
from pathlib import Path
from typing import Dict, List, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()


class ReviewerAgent:
    def __init__(self, model: Optional[ChatOpenAI] = None):
        self.llm = model or ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4"),
            temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
        )
        self.prompt_path = Path(__file__).parent.parent / "prompts" / "reviewer.md"
        self.project_root = Path(os.getenv("PROJECT_ROOT", "c:/Code/TRAE/RockPaperScissors"))
        self._load_prompt()

    def _load_prompt(self):
        if self.prompt_path.exists():
            with open(self.prompt_path, "r", encoding="utf-8") as f:
                self.system_prompt = f.read()
        else:
            self.system_prompt = self._get_default_prompt()

    def _get_default_prompt(self) -> str:
        return """你是一位资深的代码审查员。"""

    def review_code(self, code: str, language: str = "javascript") -> Dict:
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", f"""请对以下{language}代码进行全面审查：

代码：\n{code}

请从以下维度进行审查：
1. 代码规范
2. 逻辑正确性
3. 安全性
4. 性能
5. 可维护性

最终给出代码评级（A/B/C/D）和具体的改进建议。
""")
        ])
        chain = prompt | self.llm
        response = chain.invoke({})
        return self._parse_review_response(response.content)

    def _parse_review_response(self, content: str) -> Dict:
        grade = "B"
        if "评级" in content or "Grade" in content or "Rating" in content:
            for letter in ["A", "B", "C", "D"]:
                if letter in content.split()[0]:
                    grade = letter
                    break
        return {
            "review": content,
            "grade": grade,
            "status": "reviewed"
        }

    def review_file(self, file_path: str) -> Dict:
        full_path = self.project_root / file_path
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                code = f.read()
            language = self._detect_language(file_path)
            return self.review_code(code, language)
        except Exception as e:
            return {
                "review": f"读取文件失败: {str(e)}",
                "grade": "N/A",
                "status": "error"
            }

    def _detect_language(self, file_path: str) -> str:
        ext = Path(file_path).suffix.lower()
        lang_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".java": "java",
            ".cpp": "c++",
            ".c": "c",
            ".go": "go",
            ".rs": "rust"
        }
        return lang_map.get(ext, "text")

    def check_security(self, code: str) -> Dict:
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", f"""请对以下代码进行安全审查：

代码：\n{code}

请检查：
1. SQL注入
2. XSS攻击
3. CSRF攻击
4. 敏感信息泄露
5. 输入验证
6. 权限控制
""")
        ])
        chain = prompt | self.llm
        response = chain.invoke({})
        return {"security_review": response.content, "vulnerabilities": []}

    def suggest_refactoring(self, code: str) -> str:
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", f"""请为以下代码提供重构建议：

代码：\n{code}

请从以下方面提供建议：
1. 代码结构优化
2. 设计模式应用
3. 消除重复代码
4. 提高可读性
5. 改进测试性
""")
        ])
        chain = prompt | self.llm
        response = chain.invoke({})
        return response.content

    def discuss_code_quality(self, topic: str, code: str) -> str:
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", f"""讨论主题：{topic}

相关代码：\n{code}

请提供专业的代码质量分析。""")
        ])
        chain = prompt | self.llm
        response = chain.invoke({})
        return response.content
