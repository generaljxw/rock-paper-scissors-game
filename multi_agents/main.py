"""
Multi-Agent 开发团队 - 主程序入口
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

load_dotenv()

from multi_agents.coordinator import AgentCoordinator, AgentType


def print_header(title: str):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def interactive_mode():
    coordinator = AgentCoordinator()

    print_header("🏢 Multi-Agent 开发团队系统")
    print("欢迎使用多代理协作开发平台！")
    print("\n可用Agent:")
    print("  1. [Planner]  架构师 - 需求分析和架构设计")
    print("  2. [Coder]    工程师 - 代码实现")
    print("  3. [Tester]   测试师 - 测试用例和验证")
    print("  4. [Reviewer] 审查员 - 代码审查")
    print("\n输入 'quit' 退出，输入 'history' 查看历史\n")

    while True:
        try:
            print("-" * 40)
            print("请选择要交互的Agent或输入问题：")
            print("  [planner] - 与架构师讨论需求")
            print("  [coder]   - 与工程师讨论实现")
            print("  [tester]  - 与测试师讨论测试")
            print("  [reviewer]- 与审查员讨论代码")
            print("  [team]    - 启动完整迭代")
            print("-" * 40)

            choice = input("\n请输入选项或直接描述问题: ").strip()

            if choice.lower() == 'quit':
                print("再见！")
                break

            if choice.lower() == 'history':
                print(coordinator.get_conversation_summary())
                continue

            if choice.lower() == 'team':
                print_header("🚀 启动完整开发迭代")
                requirements = input("请输入项目需求描述: ").strip()
                if requirements:
                    results = coordinator.run_full_iteration(requirements)
                    print("\n📊 迭代结果:")
                    for key, value in results.items():
                        print(f"  {key}: {value}")
                continue

            agent_map = {
                'planner': (AgentType.PLANNER, coordinator.planner),
                'coder': (AgentType.CODER, coordinator.coder),
                'tester': (AgentType.TESTER, coordinator.tester),
                'reviewer': (AgentType.REVIEWER, coordinator.reviewer)
            }

            if choice.lower() in agent_map:
                agent_type, agent = agent_map[choice.lower()]
                print(f"\n已连接 [{agent_type.value.upper()}]")
                question = input("请输入您的问题: ").strip()
                if question:
                    if agent_type == AgentType.PLANNER:
                        response = agent.discuss_with_pm(question, "")
                    elif agent_type == AgentType.CODER:
                        response = agent.discuss_implementation(question, "")
                    elif agent_type == AgentType.TESTER:
                        response = agent.discuss_test_strategy(question, "")
                    else:
                        response = agent.discuss_code_quality(question, "")
                    print(f"\n📝 回复:\n{response}\n")
                    coordinator.send_message(AgentType.PLANNER, agent_type, question)
            else:
                print("🤔 无法理解，请重新输入...")

        except KeyboardInterrupt:
            print("\n\n再见！")
            break
        except Exception as e:
            print(f"\n⚠️ 发生错误: {str(e)}")


def demo_mode():
    coordinator = AgentCoordinator()

    print_header("🎬 Demo 模式 - 快速演示")

    print("\n📋 场景1: 与Planner讨论新需求")
    response = coordinator.discuss_feature_with_planner(
        "我想要添加一个排行榜功能，显示玩家的历史最高分"
    )
    print(f"Planner回复:\n{response[:500]}...")

    print("\n\n💻 场景2: 与Coder讨论实现")
    response = coordinator.discuss_with_coder(
        "如何在现有的游戏中添加排行榜功能？",
        "当前使用原生JS和Tailwind CSS"
    )
    print(f"Coder回复:\n{response[:500]}...")

    print("\n\n🧪 场景3: 与Tester讨论测试策略")
    response = coordinator.discuss_with_tester(
        "如何测试排行榜功能的准确性？",
        "排行榜需要按分数排序"
    )
    print(f"Tester回复:\n{response[:500]}...")

    print("\n\n🔍 场景4: 与Reviewer讨论代码质量")
    response = coordinator.discuss_with_reviewer(
        "这个排行榜实现有什么潜在问题？",
        "function addScore(score) { scores.push(score); }"
    )
    print(f"Reviewer回复:\n{response[:500]}...")

    print("\n" + "=" * 60)
    print("Demo 完成！运行 'python main.py' 进入交互模式")
    print("=" * 60)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        demo_mode()
    else:
        interactive_mode()
