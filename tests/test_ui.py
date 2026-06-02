"""
UI层测试模块

本模块测试UI组件的基本功能
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import QApplication, QLabel
from PyQt6.QtCore import Qt

from src.ui.login_window import LoginWindow
from src.ui.battle_window import BattleWindow
from src.ui.history_window import HistoryWindow
from src.ui.main_window import MainWindow
from src.business.game_engine import GameEngine
from src.business.score_manager import ScoreManager
from src.business.statistics import Statistics


@pytest.fixture(scope="module")
def qapp():
    """
    创建QApplication实例
    """
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


class TestLoginWindow:
    """
    登录窗口测试类
    """

    def test_login_window_creation(self, qapp):
        """
        测试登录窗口创建
        """
        window = LoginWindow()
        assert window is not None
        assert window.user_manager is not None
        assert window.username_input is not None
        assert window.password_input is not None

    def test_login_window_buttons(self, qapp):
        """
        测试登录窗口按钮存在
        """
        window = LoginWindow()
        assert window.login_button is not None
        assert window.register_button is not None
        assert window.login_button.text() == "🎮 登录"
        assert window.register_button.text() == "✨ 注册"

    def test_input_validation_empty_username(self, qapp):
        """
        测试空用户名验证
        """
        window = LoginWindow()
        window.username_input.setText("")
        assert window._validate_input() == False

    def test_input_validation_short_username(self, qapp):
        """
        测试短用户名验证
        """
        window = LoginWindow()
        window.username_input.setText("ab")
        window.password_input.setText("password123")
        assert window._validate_input() == False

    def test_input_validation_short_password(self, qapp):
        """
        测试短密码验证
        """
        window = LoginWindow()
        window.username_input.setText("username")
        window.password_input.setText("12345")
        assert window._validate_input() == False

    def test_input_validation_valid(self, qapp):
        """
        测试有效输入验证
        """
        window = LoginWindow()
        window.username_input.setText("username")
        window.password_input.setText("password123")
        assert window._validate_input() == True

    def test_get_user_manager(self, qapp):
        """
        测试获取用户管理器
        """
        window = LoginWindow()
        assert window.get_user_manager() is not None
        assert isinstance(window.get_user_manager().user_dao.__class__.__name__, str)

    def test_username_label_visible(self, qapp):
        """
        测试用户名标签存在且未被隐藏
        """
        window = LoginWindow()
        all_labels = window.findChildren(QLabel)
        username_labels = [lbl for lbl in all_labels if lbl.text() == "用户名:"]
        assert len(username_labels) > 0, "用户名标签不存在"
        label = username_labels[0]
        assert not label.isHidden(), "用户名标签被隐藏"
        assert label.styleSheet() != "", "用户名标签缺少样式"

    def test_password_label_visible(self, qapp):
        """
        测试密码标签存在且未被隐藏
        """
        window = LoginWindow()
        all_labels = window.findChildren(QLabel)
        password_labels = [lbl for lbl in all_labels if lbl.text() == "密码:"]
        assert len(password_labels) > 0, "密码标签不存在"
        label = password_labels[0]
        assert not label.isHidden(), "密码标签被隐藏"
        assert label.styleSheet() != "", "密码标签缺少样式"


class TestBattleWindow:
    """
    对战窗口测试类
    """

    def test_battle_window_creation(self, qapp):
        """
        测试对战窗口创建
        """
        game_engine = GameEngine()
        score_manager = ScoreManager()
        window = BattleWindow(game_engine, score_manager, 1, 1)
        assert window is not None
        assert window.game_engine is not None
        assert window.score_manager is not None
        assert window.round_count == 0

    def test_choice_buttons_exist(self, qapp):
        """
        测试选择按钮存在
        """
        from src.business.enums import Choice
        game_engine = GameEngine()
        score_manager = ScoreManager()
        window = BattleWindow(game_engine, score_manager, 1, 1)
        assert len(window.choice_buttons) == 3
        assert Choice.ROCK in window.choice_buttons
        assert Choice.SCISSORS in window.choice_buttons
        assert Choice.PAPER in window.choice_buttons

    def test_battle_window_independent_window(self, qapp):
        """
        测试对战窗口是独立窗口（非子控件）
        确保BattleWindow不设置parent，避免父窗口隐藏时子窗口也被隐藏
        """
        game_engine = GameEngine()
        score_manager = ScoreManager()
        battle_window = BattleWindow(game_engine, score_manager, 1, 1)
        assert battle_window.parent() is None, "BattleWindow不应设置parent，否则父窗口隐藏时子窗口也会被隐藏"

    def test_battle_window_mode_display(self, qapp):
        """
        测试对战窗口正确显示模式名称
        """
        mode_names = {1: "一局定胜负", 2: "三局两胜", 3: "连战模式"}
        for mode_id, expected_name in mode_names.items():
            game_engine = GameEngine()
            score_manager = ScoreManager()
            window = BattleWindow(game_engine, score_manager, 1, mode_id)
            all_labels = window.findChildren(QLabel)
            mode_labels = [lbl for lbl in all_labels if expected_name in lbl.text()]
            assert len(mode_labels) > 0, f"模式{mode_id}的名称'{expected_name}'未在对战窗口中显示"


class TestHistoryWindow:
    """
    历史记录窗口测试类
    """

    def test_history_window_creation(self, qapp):
        """
        测试历史记录窗口创建
        """
        statistics = Statistics()
        window = HistoryWindow(1, statistics)
        assert window is not None
        assert window.statistics is not None

    def test_history_table_exists(self, qapp):
        """
        测试历史记录表格存在
        """
        statistics = Statistics()
        window = HistoryWindow(1, statistics)
        assert window.history_table is not None
        assert window.history_table.columnCount() == 5


class TestMainWindow:
    """
    主窗口测试类
    """

    def _create_test_user(self):
        """
        创建测试用户，返回(user_id, username)
        """
        from src.business.user_manager import UserManager
        import time

        unique_id = int(time.time() * 1000) % 100000
        unique_name = f"tw_{unique_id}"

        manager = UserManager()
        success, _ = manager.register(unique_name, "password123")
        if not success:
            unique_id = int(time.time() * 1000) % 100000 + 999
            unique_name = f"tw_{unique_id}"
            manager = UserManager()
            success, _ = manager.register(unique_name, "password123")

        user = manager.get_current_user()
        return user.id, user.username

    def test_main_window_creation(self, qapp):
        """
        测试主窗口创建
        """
        uid, unique_name = self._create_test_user()
        window = MainWindow(uid, unique_name)
        assert window is not None
        assert window.user_id == uid
        assert window.username == unique_name

    def test_main_window_mode_tags_visible(self, qapp):
        """
        测试主窗口模式卡片包含模式标签
        """
        uid, unique_name = self._create_test_user()
        window = MainWindow(uid, unique_name)
        all_labels = window.findChildren(QLabel)

        expected_tags = ["一局定胜负", "三局两胜制", "连战模式"]
        for tag in expected_tags:
            tag_labels = [lbl for lbl in all_labels if tag in lbl.text()]
            assert len(tag_labels) > 0, f"模式标签'{tag}'未在主窗口中显示"

    def test_main_window_mode_descriptions_visible(self, qapp):
        """
        测试主窗口模式卡片包含模式描述
        """
        uid, unique_name = self._create_test_user()
        window = MainWindow(uid, unique_name)
        all_labels = window.findChildren(QLabel)

        expected_keywords = ["一局分出胜负", "先获得2胜", "失败则结算"]
        for keyword in expected_keywords:
            matching = [lbl for lbl in all_labels if keyword in lbl.text()]
            assert len(matching) > 0, f"模式描述关键词'{keyword}'未在主窗口中显示"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
