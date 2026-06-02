"""
Tester Agent - 测试自动化专家
"""
import os
from pathlib import Path
from typing import Dict, List, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()


class TesterAgent:
    def __init__(self, model: Optional[ChatOpenAI] = None):
        self.llm = model or ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4"),
            temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
        )
        self.prompt_path = Path(__file__).parent.parent / "prompts" / "tester.md"
        self.project_root = Path(os.getenv("PROJECT_ROOT", "c:/Code/TRAE/RockPaperScissors"))
        self._load_prompt()

    def _load_prompt(self):
        if self.prompt_path.exists():
            with open(self.prompt_path, "r", encoding="utf-8") as f:
                self.system_prompt = f.read()
        else:
            self.system_prompt = self._get_default_prompt()

    def _get_default_prompt(self) -> str:
        return """你是一位专业的测试自动化专家。"""

    def design_test_cases(self, feature_description: str) -> List[Dict]:
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", f"""请为以下功能设计全面的测试用例：

功能描述：\n{feature_description}

请包含：
1. 测试用例ID和名称
2. 测试前置条件
3. 测试步骤
4. 预期结果
5. 测试优先级
""")
        ])
        chain = prompt | self.llm
        response = chain.invoke({})
        return {"test_cases": response.content, "count": self._count_test_cases(response.content)}

    def _count_test_cases(self, content: str) -> int:
        count = content.count("测试用例") or content.count("Test Case")
        return max(count, 1)

    def write_unit_tests(self, code_to_test: str, language: str = "python") -> Dict:
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", f"""请为以下{language}代码编写单元测试：

代码：\n{code_to_test}

请使用合适的测试框架（如pytest）编写测试。
""")
        ])
        chain = prompt | self.llm
        response = chain.invoke({})
        return {"test_code": response.content, "status": "completed"}

    def report_bug(self, bug_description: str, reproduction_steps: str) -> Dict:
        severity_prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", f"""请评估以下缺陷的严重程度：

缺陷描述：\n{bug_description}

复现步骤：\n{reproduction_steps}

请确定：
1. 严重程度（Critical/Major/Minor）
2. 缺陷类型
3. 修复建议
""")
        ])
        chain = severity_prompt | self.llm
        response = chain.invoke({})
        return {
            "bug_report": response.content,
            "status": "reported",
            "tracking_id": self._generate_id()
        }

    def _generate_id(self) -> str:
        import time
        return f"BUG-{int(time.time())}"

    def verify_fix(self, bug_description: str, fix_description: str) -> Dict:
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", f"""请验证以下缺陷修复：

原始缺陷：\n{bug_description}

修复方案：\n{fix_description}

请确认：
1. 修复是否完整
2. 是否引入新问题
3. 是否需要重新测试
""")
        ])
        chain = prompt | self.llm
        response = chain.invoke({})
        return {"verification": response.content, "status": "verified"}

    def generate_test_report(self, test_results: List[Dict]) -> str:
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", f"""请生成测试报告：

测试结果：\n{test_results}

请包含：
1. 测试执行概要
2. 通过率统计
3. 缺陷汇总
4. 风险评估
5. 测试结论
""")
        ])
        chain = prompt | self.llm
        response = chain.invoke({})
        return response.content

    def discuss_test_strategy(self, topic: str, context: str) -> str:
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", f"""讨论主题：{topic}

当前上下文：\n{context}

请提供你的测试策略分析。""")
        ])
        chain = prompt | self.llm
        response = chain.invoke({})
        return response.content
