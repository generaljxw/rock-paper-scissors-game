"""
UI层主窗口模块

本模块实现游戏主界面，提供模式选择、积分显示等功能，
界面设计采用儿童友好的卡通风格。
"""

import sys
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QMessageBox, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from ..business.game_engine import GameEngine
from ..business.score_manager import ScoreManager
from ..business.statistics import Statistics
from .battle_window import BattleWindow


class MainWindow(QWidget):
    """
    主窗口类
    提供游戏模式选择、用户信息显示等功能
    """

    game_started = pyqtSignal(int, int)
    logout_requested = pyqtSignal()

    def __init__(self, user_id: int, username: str):
        super().__init__()
        self.user_id = user_id
        self.username = username
        self.game_engine = GameEngine()
        self.score_manager = ScoreManager()
        self.statistics = Statistics()
        self.battle_window = None
        self._init_failed = False
        
        try:
            self._init_ui()
            self._update_user_info()
        except Exception as e:
            print(f"主窗口初始化失败: {e}")
            self._init_failed = True
            # 不直接调用sys.exit(1)，而是通过信号通知父窗口处理
            self.logout_requested.emit()

    def is_init_failed(self) -> bool:
        """
        检查主窗口初始化是否失败
        返回:
            是否初始化失败
        """
        return self._init_failed

    def _init_ui(self):
        """
        初始化UI组件
        """
        self.setWindowTitle("猜拳小游戏 - 主界面")
        self.setMinimumSize(600, 680)
        self.setMaximumSize(600, 800)
        self.setWindowFlags(Qt.WindowType.WindowCloseButtonHint | Qt.WindowType.WindowMinimizeButtonHint)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(25, 15, 25, 15)
        main_layout.setSpacing(8)

        header_layout = QHBoxLayout()

        welcome_label = QLabel(f"👋 你好，{self.username}！")
        welcome_label.setFont(QFont("Microsoft YaHei", 18, QFont.Weight.Bold))
        welcome_label.setStyleSheet("color: #333; padding: 10px;")

        header_layout.addWidget(welcome_label)
        header_layout.addStretch()

        self.score_label = QLabel("积分: --")
        self.score_label.setFont(QFont("Microsoft YaHei", 14))
        self.score_label.setStyleSheet("""
            color: #FF6B6B;
            background-color: #FFF9E6;
            padding: 8px 20px;
            border-radius: 15px;
            border: 2px solid #FFE4B5;
        """)

        self.win_rate_label = QLabel("胜率: --%")
        self.win_rate_label.setFont(QFont("Microsoft YaHei", 14))
        self.win_rate_label.setStyleSheet("""
            color: #4ECDC4;
            background-color: #E6FFF9;
            padding: 8px 20px;
            border-radius: 15px;
            border: 2px solid #B2F5EA;
        """)

        header_layout.addWidget(self.score_label)
        header_layout.addWidget(self.win_rate_label)
        main_layout.addLayout(header_layout)

        title_label = QLabel("🎮 选择对战模式")
        title_label.setFont(QFont("Microsoft YaHei", 18, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #FF6B6B; padding: 8px;")
        main_layout.addWidget(title_label)

        mode_container = QVBoxLayout()
        mode_container.setSpacing(8)

        mode1_frame = self._create_mode_card(
            mode_id=1,
            title="⚔️ 模式1: 一局定胜负",
            description="单局对决，一局定胜负！\n平局时自动继续出拳，直到分出胜负\n获胜方获得1积分，失败方扣除1积分",
            mode_tag="一局定胜负",
            button_text="开始对战",
            color="#FF6B6B"
        )

        mode2_frame = self._create_mode_card(
            mode_id=2,
            title="🏆 模式2: 三局两胜",
            description="三局两胜制，更具挑战！\n率先取得2场胜利的玩家获胜\n胜利方加2积分，失败方扣2积分",
            mode_tag="三局两胜制",
            button_text="开始对战",
            color="#4ECDC4"
        )

        mode3_frame = self._create_mode_card(
            mode_id=3,
            title="🔥 模式3: 连战模式",
            description="消耗3积分入场，挑战极限！\n连续获得3次胜利(平局不计)奖励5积分\n每完成5次出拳可获得1积分奖励",
            mode_tag="连战模式",
            button_text="开始对战",
            color="#FFE66D",
            entry_fee=3
        )

        mode_container.addWidget(mode1_frame)
        mode_container.addWidget(mode2_frame)
        mode_container.addWidget(mode3_frame)

        # 将模式卡片放入滚动区域，确保内容过多时可滚动
        scroll_content = QWidget()
        scroll_content.setLayout(mode_container)

        scroll_area = QScrollArea()
        scroll_area.setWidget(scroll_content)
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background: #F0F0F0;
                width: 6px;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical {
                background: #CCC;
                border-radius: 3px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background: #AAA;
            }
        """)

        main_layout.addWidget(scroll_area, 1)

        bottom_container = QFrame()
        bottom_container.setFrameShape(QFrame.Shape.NoFrame)
        bottom_container.setFixedHeight(55)
        bottom_container.setStyleSheet("""
            QFrame {
                background-color: #F5F5F5;
                border-top: 1px solid #E0E0E0;
            }
        """)

        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(15, 5, 15, 5)
        bottom_layout.addStretch()

        history_button = QPushButton("📊 查看战绩")
        history_button.setFont(QFont("Microsoft YaHei", 11))
        history_button.setFixedSize(120, 40)
        history_button.setCursor(Qt.CursorShape.PointingHandCursor)
        history_button.setStyleSheet("""
            QPushButton {
                background-color: #E8E8E8;
                color: #666;
                border: none;
                border-radius: 20px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #D8D8D8;
            }
        """)
        history_button.clicked.connect(self._on_history_clicked)

        logout_button = QPushButton("🚪 退出登录")
        logout_button.setFont(QFont("Microsoft YaHei", 11))
        logout_button.setFixedSize(120, 40)
        logout_button.setCursor(Qt.CursorShape.PointingHandCursor)
        logout_button.setStyleSheet("""
            QPushButton {
                background-color: #FFE4E4;
                color: #FF6B6B;
                border: none;
                border-radius: 20px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #FFD4D4;
            }
        """)
        logout_button.clicked.connect(self._on_logout_clicked)

        bottom_layout.addWidget(history_button)
        bottom_layout.addWidget(logout_button)
        bottom_container.setLayout(bottom_layout)

        main_layout.addWidget(bottom_container)

        self.setLayout(main_layout)
        self.setStyleSheet("background-color: #F5F5F5;")

    def _create_mode_card(self, mode_id: int, title: str, description: str,
                          button_text: str, color: str, mode_tag: str = "",
                          entry_fee: int = None) -> QFrame:
        """
        创建模式选择卡片
        参数:
            mode_id: 模式ID
            title: 标题
            description: 描述
            button_text: 按钮文本
            color: 主题颜色
            mode_tag: 模式标签（简短描述）
            entry_fee: 入场费（可选）
        返回:
            模式卡片组件
        """
        frame = QFrame()
        frame.setObjectName(f"modeCard_{mode_id}")
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        frame.setStyleSheet(f"""
            QFrame#modeCard_{mode_id} {{
                background-color: white;
                border-radius: 12px;
                border: 2px solid {color};
                padding: 10px 14px;
            }}
        """)

        layout = QVBoxLayout()
        layout.setSpacing(6)
        layout.setContentsMargins(4, 4, 4, 4)

        title_layout = QHBoxLayout()
        title_label = QLabel(title)
        title_label.setFont(QFont("Microsoft YaHei", 13, QFont.Weight.Bold))
        title_label.setStyleSheet(f"color: {color};")
        title_layout.addWidget(title_label)
        title_layout.addStretch()

        if mode_tag:
            tag_label = QLabel(mode_tag)
            tag_label.setFont(QFont("Microsoft YaHei", 9))
            tag_label.setStyleSheet(f"""
                color: {'#666' if color == '#FFE66D' else 'white'};
                background-color: {color};
                border-radius: 8px;
                padding: 2px 10px;
            """)
            tag_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title_layout.addWidget(tag_label)

        layout.addLayout(title_layout)

        desc_label = QLabel(description)
        desc_label.setFont(QFont("Microsoft YaHei", 9))
        desc_label.setStyleSheet("color: #555;")
        desc_label.setWordWrap(True)

        content_layout = QHBoxLayout()
        content_layout.setSpacing(15)
        content_layout.addWidget(desc_label, 3)

        start_button = QPushButton(button_text)
        start_button.setFont(QFont("Microsoft YaHei", 11, QFont.Weight.Bold))
        start_button.setFixedSize(110, 36)
        start_button.setCursor(Qt.CursorShape.PointingHandCursor)
        start_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: {'#666' if color == '#FFE66D' else 'white'};
                border: none;
                border-radius: 18px;
                padding: 6px 15px;
            }}
            QPushButton:hover {{
                opacity: 0.9;
            }}
            QPushButton:pressed {{
                opacity: 0.8;
            }}
        """)
        start_button.clicked.connect(lambda: self._on_mode_selected(mode_id))

        btn_container = QVBoxLayout()
        btn_container.addStretch()
        btn_container.addWidget(start_button)
        btn_container.addStretch()

        content_layout.addLayout(btn_container, 1)

        if entry_fee is not None:
            fee_label = QLabel(f"💰 入场费: {entry_fee}积分")
            fee_label.setFont(QFont("Microsoft YaHei", 10))
            fee_label.setStyleSheet("color: #FF9500; padding: 3px 0;")
            layout.addWidget(fee_label)

        layout.addLayout(content_layout)

        frame.setLayout(layout)
        return frame

    def _update_user_info(self):
        """
        更新用户信息显示
        """
        score = self.score_manager.get_score(self.user_id)
        self.score_label.setText(f"积分: {score}")

        win_rate = self.statistics.get_win_rate(self.user_id)
        self.win_rate_label.setText(f"胜率: {win_rate}%")

    def _on_mode_selected(self, mode_id: int):
        """
        处理模式选择事件
        参数:
            mode_id: 选择的模式ID
        """
        if mode_id == 3:
            score = self.score_manager.get_score(self.user_id)
            if score < 3:
                QMessageBox.warning(
                    self,
                    "积分不足",
                    f"连战模式需要3积分入场，你当前只有{score}积分。\n请选择其他模式或充值积分。"
                )
                return

            reply = QMessageBox.question(
                self,
                "确认入场",
                f"连战模式需要消耗3积分入场，是否继续？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

            success, message = self.score_manager.deduct_entry_fee(self.user_id, mode_id)
            if not success:
                QMessageBox.warning(self, "入场失败", message)
                return

            self._update_user_info()

        self.game_engine.start_game(self.user_id, mode_id)
        self.battle_window = BattleWindow(self.game_engine, self.score_manager, self.user_id, mode_id)
        self.battle_window.game_finished.connect(self._on_game_finished)
        self.battle_window.closed.connect(self._on_battle_closed)
        self.battle_window.show()
        self.hide()

    def _on_game_finished(self, score_change: int):
        """
        处理游戏结束事件
        参数:
            score_change: 积分变化
        """
        self._update_user_info()
        self.show()

    def _on_battle_closed(self):
        """
        处理对战窗口关闭事件
        """
        self._update_user_info()
        self.show()

    def _on_history_clicked(self):
        """
        处理查看战绩按钮点击
        """
        from .history_window import HistoryWindow
        self.history_window = HistoryWindow(self.user_id, self.statistics)
        self.history_window.closed.connect(lambda: self.show())
        self.history_window.show()
        self.hide()

    def _on_logout_clicked(self):
        """
        处理退出登录按钮点击
        """
        reply = QMessageBox.question(
            self,
            "确认退出",
            "确定要退出登录吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.logout_requested.emit()
