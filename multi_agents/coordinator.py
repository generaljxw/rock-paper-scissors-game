"""
Multi-Agent 协调器
管理多个Agent之间的通信和协作
"""
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

from .agents.planner_agent import PlannerAgent
from .agents.coder_agent import CoderAgent
from .agents.tester_agent import TesterAgent
from .agents.reviewer_agent import ReviewerAgent

load_dotenv()


class AgentType(Enum):
    PLANNER = "planner"
    CODER = "coder"
    TESTER = "tester"
    REVIEWER = "reviewer"


@dataclass
class Message:
    sender: AgentType
    recipient: Optional[AgentType]
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict = field(default_factory=dict)


@dataclass
class Task:
    id: str
    description: str
    assigned_agent: Optional[AgentType] = None
    status: str = "pending"
    result: Optional[Any] = None
    created_at: datetime = field(default_factory=datetime.now)


class AgentCoordinator:
    def __init__(self):
        self.llm = ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4"),
            temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
        )

        self.planner = PlannerAgent(self.llm)
        self.coder = CoderAgent(self.llm)
        self.tester = TesterAgent(self.llm)
        self.reviewer = ReviewerAgent(self.llm)

        self.agents = {
            AgentType.PLANNER: self.planner,
            AgentType.CODER: self.coder,
            AgentType.TESTER: self.tester,
            AgentType.REVIEWER: self.reviewer
        }

        self.message_queue: List[Message] = []
        self.task_history: List[Task] = []
        self.conversation_history: List[Dict] = []

    def send_message(self, from_agent: AgentType, to_agent: AgentType, content: str, metadata: Dict = None) -> Message:
        message = Message(
            sender=from_agent,
            recipient=to_agent,
            content=content,
            metadata=metadata or {}
        )
        self.message_queue.append(message)
        self.conversation_history.append({
            "from": from_agent.value,
            "to": to_agent.value,
            "content": content,
            "timestamp": message.timestamp.isoformat()
        })
        return message

    def broadcast_message(self, from_agent: AgentType, content: str) -> List[Message]:
        messages = []
        for agent_type in AgentType:
            if agent_type != from_agent:
                msg = self.send_message(from_agent, agent_type, content)
                messages.append(msg)
        return messages

    def get_agent(self, agent_type: AgentType):
        return self.agents.get(agent_type)

    def create_task(self, description: str, assigned_agent: AgentType = None) -> Task:
        task = Task(
            id=f"TASK-{len(self.task_history) + 1}",
            description=description,
            assigned_agent=assigned_agent
        )
        self.task_history.append(task)
        return task

    def update_task_status(self, task_id: str, status: str, result: Any = None):
        for task in self.task_history:
            if task.id == task_id:
                task.status = status
                if result:
                    task.result = result
                break

    def discuss_feature_with_planner(self, feature_request: str) -> str:
        return self.planner.discuss_with_pm(feature_request, "")

    def discuss_with_coder(self, topic: str, context: str = "") -> str:
        return self.coder.discuss_implementation(topic, context)

    def discuss_with_tester(self, topic: str, context: str = "") -> str:
        return self.tester.discuss_test_strategy(topic, context)

    def discuss_with_reviewer(self, topic: str, code: str = "") -> str:
        return self.reviewer.discuss_code_quality(topic, code)

    def run_full_iteration(self, requirements: str) -> Dict:
        results = {
            "planner_output": None,
            "coder_output": None,
            "tester_output": None,
            "reviewer_output": None,
            "status": "completed"
        }

        print("🚀 开始迭代执行...")
        print("=" * 50)

        print("\n📋 [Planner] 分析需求并设计架构...")
        spec_doc = self.planner.generate_spec_document("猜拳小游戏", requirements)
        results["planner_output"] = spec_doc
        print("✅ Planner 完成")

        print("\n💻 [Coder] 实现功能...")
        implementation = self.coder.implement_feature("开发猜拳游戏", spec_doc)
        results["coder_output"] = implementation
        print("✅ Coder 完成")

        print("\n🧪 [Tester] 编写测试用例...")
        test_cases = self.tester.design_test_cases("猜拳游戏功能")
        results["tester_output"] = test_cases
        print("✅ Tester 完成")

        print("\n🔍 [Reviewer] 代码审查...")
        code_review = self.reviewer.review_code(
            "石头剪刀布游戏核心逻辑",
            "javascript"
        )
        results["reviewer_output"] = code_review
        print("✅ Reviewer 完成")

        print("\n" + "=" * 50)
        print("🏁 迭代执行完成！")

        return results

    def get_conversation_summary(self) -> str:
        summary = f"对话历史（共 {len(self.conversation_history)} 条消息）：\n"
        for i, msg in enumerate(self.conversation_history[-10:], 1):
            summary += f"{i}. [{msg['timestamp']}] {msg['from']} -> {msg['to']}: {msg['content'][:50]}...\n"
        return summary

    def export_conversation(self, file_path: str):
        import json
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.conversation_history, f, ensure_ascii=False, indent=2)
