"""
使用示例 - 展示如何与各个Agent交互
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from multi_agents import AgentCoordinator, AgentType


def example_1_discuss_with_planner():
    print("\n" + "=" * 50)
    print("示例1: 与Planner讨论新需求")
    print("=" * 50)

    coordinator = AgentCoordinator()

    question = """
    我想要在现有的猜拳游戏中添加以下功能：
    1. 难度选择（简单/普通/困难）
    2. 玩家历史最高分排行榜
    3. 成就系统

    请帮我分析这些需求的可行性，并给出技术方案建议。
    """

    response = coordinator.planner.discuss_with_pm(question, "")
    print(f"\n📋 Planner 回复:\n{response}")


def example_2_discuss_with_coder():
    print("\n" + "=" * 50)
    print("示例2: 与Coder讨论实现方案")
    print("=" * 50)

    coordinator = AgentCoordinator()

    response = coordinator.coder.discuss_implementation(
        "如何在不刷新页面的情况下实现难度的实时切换？",
        "当前使用原生JavaScript和Tailwind CSS"
    )
    print(f"\n💻 Coder 回复:\n{response}")


def example_3_discuss_with_tester():
    print("\n" + "=" * 50)
    print("示例3: 与Tester讨论测试策略")
    print("=" * 50)

    coordinator = AgentCoordinator()

    response = coordinator.tester.discuss_test_strategy(
        "难度选择功能应该如何测试？",
        "有3个难度等级，AI在不同难度下出拳概率不同"
    )
    print(f"\n🧪 Tester 回复:\n{response}")


def example_4_discuss_with_reviewer():
    print("\n" + "=" * 50)
    print("示例4: 与Reviewer讨论代码质量")
    print("=" * 50)

    coordinator = AgentCoordinator()

    code = """
    function getAIChoice(difficulty) {
        if (difficulty === 'easy') {
            return ['rock', 'paper', 'scissors'][Math.floor(Math.random() * 3)];
        }
        // ... more logic
    }
    """

    response = coordinator.reviewer.discuss_code_quality(
        "这个AI选择函数有什么改进建议？",
        code
    )
    print(f"\n🔍 Reviewer 回复:\n{response}")


def example_5_full_iteration():
    print("\n" + "=" * 50)
    print("示例5: 完整开发迭代")
    print("=" * 50)

    coordinator = AgentCoordinator()

    requirements = """
    开发一个猜拳游戏的新版本，需要：
    1. 添加难度选择系统
    2. 优化UI动画效果
    3. 添加音效反馈
    """

    results = coordinator.run_full_iteration(requirements)

    print("\n📊 迭代结果摘要:")
    print(f"  Planner: {'✅' if results['planner_output'] else '❌'}")
    print(f"  Coder: {'✅' if results['coder_output'] else '❌'}")
    print(f"  Tester: {'✅' if results['tester_output'] else '❌'}")
    print(f"  Reviewer: {'✅' if results['reviewer_output'] else '❌'}")


if __name__ == "__main__":
    print("🏢 Multi-Agent 使用示例")
    print("=" * 50)

    example_1_discuss_with_planner()
    example_2_discuss_with_coder()
    example_3_discuss_with_tester()
    example_4_discuss_with_reviewer()
    example_5_full_iteration()

    print("\n" + "=" * 50)
    print("✅ 所有示例执行完成！")
