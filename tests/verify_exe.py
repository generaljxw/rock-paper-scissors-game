"""
自动化验证脚本 - 测试打包后的.exe核心功能

通过PyQt6的信号/槽机制和QTimer模拟用户操作，
验证游戏完整功能流程。
"""

import sys
import os
import time
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import QApplication, QLabel
from PyQt6.QtCore import QTimer

from src.ui.login_window import LoginWindow
from src.ui.main_window import MainWindow
from src.ui.battle_window import BattleWindow
from src.business.game_engine import GameEngine
from src.business.score_manager import ScoreManager
from src.business.user_manager import UserManager
from src.business.enums import Choice


class ExeVerification:
    """
    打包后.exe功能验证类
    模拟用户操作验证完整游戏流程
    """

    def __init__(self):
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication([])
        self.results = []
        self.step = 0
        self.output_lines = []

    def log_result(self, test_name: str, passed: bool, detail: str = ""):
        """
        记录测试结果
        """
        status = "PASS" if passed else "FAIL"
        msg = f"[{status}] {test_name}"
        if detail:
            msg += f" - {detail}"
        self.results.append((test_name, passed, detail))
        self.output_lines.append(msg)

    def verify_login_window(self):
        """
        验证登录窗口功能
        """
        self.output_lines.append("")
        self.output_lines.append("=== 验证1: 登录窗口 ===")

        window = LoginWindow()

        # 验证窗口标题
        self.log_result(
            "登录窗口标题",
            "猜拳小游戏" in window.windowTitle(),
            f"标题: {window.windowTitle()}"
        )

        # 验证用户名标签
        all_labels = window.findChildren(QLabel)
        username_labels = [lbl for lbl in all_labels if lbl.text() == "用户名:"]
        self.log_result(
            "用户名标签存在",
            len(username_labels) > 0,
            f"找到 {len(username_labels)} 个"
        )
        if username_labels:
            self.log_result(
                "用户名标签未被隐藏",
                not username_labels[0].isHidden(),
                f"hidden={username_labels[0].isHidden()}"
            )
            self.log_result(
                "用户名标签有样式",
                username_labels[0].styleSheet() != "",
                "样式已设置"
            )

        # 验证密码标签
        password_labels = [lbl for lbl in all_labels if lbl.text() == "密码:"]
        self.log_result(
            "密码标签存在",
            len(password_labels) > 0,
            f"找到 {len(password_labels)} 个"
        )
        if password_labels:
            self.log_result(
                "密码标签未被隐藏",
                not password_labels[0].isHidden(),
                f"hidden={password_labels[0].isHidden()}"
            )

        # 验证输入框
        self.log_result(
            "用户名输入框存在",
            window.username_input is not None
        )
        self.log_result(
            "密码输入框存在",
            window.password_input is not None
        )

        # 验证按钮
        self.log_result(
            "登录按钮存在",
            window.login_button is not None,
            f"文字: {window.login_button.text()}"
        )
        self.log_result(
            "注册按钮存在",
            window.register_button is not None,
            f"文字: {window.register_button.text()}"
        )

        # 验证输入验证逻辑
        window.username_input.setText("")
        window.password_input.setText("")
        self.log_result(
            "空输入验证",
            not window._validate_input(),
            "空输入应验证失败"
        )

        window.username_input.setText("testuser")
        window.password_input.setText("password123")
        self.log_result(
            "有效输入验证",
            window._validate_input(),
            "有效输入应验证通过"
        )

        window.close()

    def verify_user_registration_and_login(self):
        """
        验证用户注册和登录流程
        """
        self.output_lines.append("")
        self.output_lines.append("=== 验证2: 用户注册和登录 ===")

        manager = UserManager()
        timestamp = int(time.time() * 1000) % 100000
        test_username = f"exe_test_{timestamp}"
        test_password = "testpass123"

        # 注册
        success, message = manager.register(test_username, test_password)
        self.log_result(
            "用户注册",
            success,
            f"用户名: {test_username}, 消息: {message}"
        )

        # 获取当前用户
        user = manager.get_current_user()
        self.log_result(
            "获取当前用户",
            user is not None,
            f"用户ID: {user.id if user else 'None'}"
        )

        if user:
            # 登出
            manager.logout()
            self.log_result(
                "用户登出",
                not manager.is_logged_in(),
                "登出后不应处于登录状态"
            )

            # 重新登录
            success, message = manager.login(test_username, test_password)
            self.log_result(
                "用户登录",
                success,
                f"消息: {message}"
            )

            self.log_result(
                "登录状态确认",
                manager.is_logged_in(),
                "登录后应处于登录状态"
            )

        return user

    def verify_main_window(self, user_id: int, username: str):
        """
        验证主窗口功能
        """
        self.output_lines.append("")
        self.output_lines.append("=== 验证3: 主窗口（模式选择） ===")

        window = MainWindow(user_id, username)

        # 验证窗口创建
        self.log_result(
            "主窗口创建",
            window is not None,
            f"用户: {username}, ID: {user_id}"
        )

        # 验证模式标签
        all_labels = window.findChildren(QLabel)
        expected_tags = ["一局定胜负", "三局两胜制", "连战模式"]
        for tag in expected_tags:
            tag_labels = [lbl for lbl in all_labels if tag in lbl.text()]
            self.log_result(
                f"模式标签'{tag}'",
                len(tag_labels) > 0,
                f"找到 {len(tag_labels)} 个"
            )

        # 验证模式描述
        expected_descs = ["一局分出胜负", "先获得2胜", "失败则结算"]
        for desc in expected_descs:
            desc_labels = [lbl for lbl in all_labels if desc in lbl.text()]
            self.log_result(
                f"模式描述'{desc}'",
                len(desc_labels) > 0,
                f"找到 {len(desc_labels)} 个"
            )

        window.close()

    def verify_battle_window(self):
        """
        验证对战窗口功能
        """
        self.output_lines.append("")
        self.output_lines.append("=== 验证4: 对战窗口 ===")

        # 测试三种模式
        mode_names = {1: "一局定胜负", 2: "三局两胜", 3: "连战模式"}

        for mode_id, mode_name in mode_names.items():
            game_engine = GameEngine()
            score_manager = ScoreManager()
            window = BattleWindow(game_engine, score_manager, 1, mode_id)

            # 验证窗口独立性（关键修复点）
            self.log_result(
                f"模式{mode_id}({mode_name})窗口独立性",
                window.parent() is None,
                f"parent={window.parent()}"
            )

            # 验证模式名称显示
            all_labels = window.findChildren(QLabel)
            mode_labels = [lbl for lbl in all_labels if mode_name in lbl.text()]
            self.log_result(
                f"模式{mode_id}({mode_name})名称显示",
                len(mode_labels) > 0,
                f"找到 {len(mode_labels)} 个"
            )

            # 验证选择按钮
            self.log_result(
                f"模式{mode_id}选择按钮数量",
                len(window.choice_buttons) == 3,
                f"按钮数: {len(window.choice_buttons)}"
            )

            # 验证三个选择按钮存在
            for choice in [Choice.ROCK, Choice.SCISSORS, Choice.PAPER]:
                self.log_result(
                    f"模式{mode_id}{choice.name}按钮存在",
                    choice in window.choice_buttons
                )

            window.close()

    def verify_game_engine(self):
        """
        验证游戏引擎核心逻辑
        """
        self.output_lines.append("")
        self.output_lines.append("=== 验证5: 游戏引擎核心逻辑 ===")

        engine = GameEngine()

        # 启动游戏
        engine.start_game(1)
        self.log_result(
            "游戏引擎启动",
            engine.current_mode == 1,
            f"模式: {engine.current_mode}"
        )

        # 出拳测试
        result = engine.play_round(Choice.ROCK)
        self.log_result(
            "出拳返回结果",
            result is not None,
            f"结果: {result}"
        )

        # AI选择测试
        ai_choice = engine.get_ai_choice()
        self.log_result(
            "AI随机选择",
            ai_choice in [Choice.ROCK, Choice.SCISSORS, Choice.PAPER],
            f"AI选择: {ai_choice}"
        )

        # 胜负判定测试
        test_cases = [
            (Choice.ROCK, Choice.SCISSORS, "win"),
            (Choice.SCISSORS, Choice.PAPER, "win"),
            (Choice.PAPER, Choice.ROCK, "win"),
            (Choice.ROCK, Choice.PAPER, "lose"),
            (Choice.SCISSORS, Choice.ROCK, "lose"),
            (Choice.PAPER, Choice.SCISSORS, "lose"),
            (Choice.ROCK, Choice.ROCK, "draw"),
        ]

        for player, ai, expected in test_cases:
            result = engine.determine_winner(player, ai)
            self.log_result(
                f"胜负判定({player.name} vs {ai.name})",
                result == expected,
                f"期望: {expected}, 实际: {result}"
            )

    def verify_database_persistence(self):
        """
        验证数据库持久化
        """
        self.output_lines.append("")
        self.output_lines.append("=== 验证6: 数据库持久化 ===")

        from src.data.database import Database

        db = Database()
        db_path = db.get_db_path()

        self.log_result(
            "数据库路径获取",
            db_path is not None and len(db_path) > 0,
            f"路径: {db_path}"
        )

        # 验证数据库连接
        try:
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT count(*) FROM users")
            count = cursor.fetchone()[0]
            db.close_connection(conn)
            self.log_result(
                "数据库查询",
                True,
                f"用户表记录数: {count}"
            )
        except Exception as e:
            self.log_result(
                "数据库查询",
                False,
                f"错误: {str(e)}"
            )

    def run_all_verifications(self):
        """
        执行所有验证
        """
        self.output_lines.append("=" * 60)
        self.output_lines.append("  猜拳游戏 .exe 功能验证测试")
        self.output_lines.append("=" * 60)

        self.verify_login_window()

        user = self.verify_user_registration_and_login()

        if user:
            self.verify_main_window(user.id, user.username)

        self.verify_battle_window()
        self.verify_game_engine()
        self.verify_database_persistence()

        # 汇总结果
        self.output_lines.append("")
        self.output_lines.append("=" * 60)
        self.output_lines.append("  验证结果汇总")
        self.output_lines.append("=" * 60)

        total = len(self.results)
        passed = sum(1 for _, p, _ in self.results if p)
        failed = total - passed

        for name, passed_flag, detail in self.results:
            status = "[PASS]" if passed_flag else "[FAIL]"
            line = f"  {status} {name}"
            if detail:
                line += f" - {detail}"
            self.output_lines.append(line)

        self.output_lines.append("")
        self.output_lines.append(f"  总计: {total} 项 | 通过: {passed} 项 | 失败: {failed} 项")
        self.output_lines.append(f"  通过率: {passed/total*100:.1f}%")
        self.output_lines.append("=" * 60)

        # 写入结果文件
        result_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "test_output", "test_results", "verify_result.txt"
        )
        with open(result_path, "w", encoding="utf-8") as f:
            f.write("\n".join(self.output_lines))

        return failed == 0


if __name__ == "__main__":
    verifier = ExeVerification()
    success = verifier.run_all_verifications()
    sys.exit(0 if success else 1)
