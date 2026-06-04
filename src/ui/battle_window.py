"""
UI层对战窗口模块

本模块实现游戏对战界面，显示玩家和AI的选择，
以及胜负结果，界面设计采用儿童友好的卡通风格。
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont

from ..business.game_engine import GameEngine
from ..business.score_manager import ScoreManager
from ..business.enums import Choice, Result
from ..audio.audio_manager import get_audio_manager


class BattleWindow(QWidget):
    """
    对战窗口类
    处理游戏对战过程，显示双方选择和结果
    集成音频管理：出拳Ducking机制、SFX播放、结算BGM切换
    """

    game_finished = pyqtSignal(int)
    closed = pyqtSignal()

    # 出拳选择到SFX键名的映射
    CHOICE_SFX_MAP = {
        Choice.ROCK: "rock",
        Choice.SCISSORS: "scissors",
        Choice.PAPER: "paper",
    }

    # 对战结果到SFX键名的映射
    RESULT_SFX_MAP = {
        Result.WIN: "win",
        Result.LOSE: "lose",
        Result.DRAW: "draw",
    }

    CHOICE_BUTTONS = {
        Choice.ROCK: ("✊", "石头"),
        Choice.SCISSORS: ("✌️", "剪刀"),
        Choice.PAPER: ("✋", "布")
    }

    def __init__(self, game_engine: GameEngine, score_manager: ScoreManager,
                 user_id: int, mode: int):
        super().__init__()
        self.game_engine = game_engine
        self.score_manager = score_manager
        self.user_id = user_id
        self.mode = mode
        self.audio_manager = get_audio_manager()
        self.round_count = 0
        self.consecutive_wins = 0
        self.score_change = 0
        self._finish_button_layout = None
        self._init_ui()

    def _init_ui(self):
        """
        初始化UI组件
        """
        self.setWindowTitle("猜拳小游戏 - 对战中")
        self.setMinimumSize(750, 600)
        self.setMaximumSize(800, 700)
        self.setWindowFlags(Qt.WindowType.WindowCloseButtonHint)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(25, 15, 25, 15)
        main_layout.setSpacing(10)

        header_layout = QHBoxLayout()
        mode_names = {1: "一局定胜负", 2: "三局两胜", 3: "连战模式"}
        mode_label = QLabel(f"🎮 {mode_names.get(self.mode, '未知模式')}")
        mode_label.setFont(QFont("Microsoft YaHei", 14, QFont.Weight.Bold))
        mode_label.setStyleSheet("color: #FF6B6B;")

        self.round_label = QLabel(f"回合: {self.round_count}")
        self.round_label.setFont(QFont("Microsoft YaHei", 12))
        self.round_label.setStyleSheet("color: #666;")

        header_layout.addWidget(mode_label)
        header_layout.addStretch()
        header_layout.addWidget(self.round_label)
        main_layout.addLayout(header_layout)

        result_frame = QFrame()
        result_frame.setObjectName("resultFrame")
        result_frame.setFrameShape(QFrame.Shape.StyledPanel)
        result_frame.setStyleSheet("""
            QFrame#resultFrame {
                background-color: #FFF9E6;
                border-radius: 15px;
                border: 2px solid #FFE4B5;
                padding: 12px;
            }
        """)

        result_layout = QHBoxLayout()
        result_layout.setSpacing(30)

        player_frame = QVBoxLayout()
        player_frame.setSpacing(5)
        player_title = QLabel("👤 你")
        player_title.setFont(QFont("Microsoft YaHei", 14, QFont.Weight.Bold))
        player_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        player_title.setStyleSheet("color: #333;")
        player_frame.addWidget(player_title)

        self.player_choice_label = QLabel("❓")
        self.player_choice_label.setFont(QFont("Microsoft YaHei", 40))
        self.player_choice_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.player_choice_label.setMinimumSize(80, 80)
        player_frame.addWidget(self.player_choice_label)

        self.player_result_label = QLabel("")
        self.player_result_label.setFont(QFont("Microsoft YaHei", 12))
        self.player_result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.player_result_label.setStyleSheet("color: #888;")
        player_frame.addWidget(self.player_result_label)

        vs_label = QLabel("⚔️")
        vs_label.setFont(QFont("Microsoft YaHei", 28))
        vs_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        ai_frame = QVBoxLayout()
        ai_frame.setSpacing(5)
        ai_title = QLabel("🤖 AI")
        ai_title.setFont(QFont("Microsoft YaHei", 14, QFont.Weight.Bold))
        ai_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ai_title.setStyleSheet("color: #333;")
        ai_frame.addWidget(ai_title)

        self.ai_choice_label = QLabel("❓")
        self.ai_choice_label.setFont(QFont("Microsoft YaHei", 40))
        self.ai_choice_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ai_choice_label.setMinimumSize(80, 80)
        ai_frame.addWidget(self.ai_choice_label)

        self.ai_result_label = QLabel("")
        self.ai_result_label.setFont(QFont("Microsoft YaHei", 12))
        self.ai_result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ai_result_label.setStyleSheet("color: #888;")
        ai_frame.addWidget(self.ai_result_label)

        result_layout.addLayout(player_frame)
        result_layout.addWidget(vs_label)
        result_layout.addLayout(ai_frame)

        result_frame.setLayout(result_layout)
        main_layout.addWidget(result_frame)

        self.result_display = QLabel("")
        self.result_display.setFont(QFont("Microsoft YaHei", 16, QFont.Weight.Bold))
        self.result_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result_display.setStyleSheet("padding: 8px; color: #FF6B6B;")
        self.result_display.setWordWrap(True)
        main_layout.addWidget(self.result_display)

        choice_label = QLabel("👇 请选择你的出拳")
        choice_label.setFont(QFont("Microsoft YaHei", 12))
        choice_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        choice_label.setStyleSheet("color: #666; padding: 5px;")
        main_layout.addWidget(choice_label)

        choice_layout = QHBoxLayout()
        choice_layout.setSpacing(20)
        choice_layout.addStretch()

        self.choice_buttons = {}
        self._choice_layout = choice_layout
        for choice in [Choice.ROCK, Choice.SCISSORS, Choice.PAPER]:
            emoji, name = self.CHOICE_BUTTONS[choice]
            btn = QPushButton(f"{emoji}\n{name}")
            btn.setFont(QFont("Microsoft YaHei", 11))
            btn.setFixedSize(90, 70)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: white;
                    border: 2px solid #DDD;
                    border-radius: 15px;
                    padding: 10px;
                    color: #333;
                }
                QPushButton:hover {
                    background-color: #FFF0F0;
                    border-color: #FF6B6B;
                }
                QPushButton:pressed {
                    background-color: #FFE0E0;
                }
                QPushButton:disabled {
                    background-color: #F5F5F5;
                    border-color: #EEE;
                    color: #AAA;
                }
            """)
            btn.clicked.connect(lambda checked, c=choice: self._on_choice_selected(c))
            self.choice_buttons[choice] = btn
            choice_layout.addWidget(btn)

        choice_layout.addStretch()
        main_layout.addLayout(choice_layout)

        self.setLayout(main_layout)
        self.setStyleSheet("background-color: #F5F5F5;")

    def _on_choice_selected(self, choice: Choice):
        """
        处理玩家选择事件
        集成Ducking机制：出拳时压低BGM音量，播放出拳音效和判定音效后恢复
        参数:
            choice: 玩家选择的拳
        """
        for btn in self.choice_buttons.values():
            btn.setEnabled(False)

        self.round_count += 1
        self.round_label.setText(f"回合: {self.round_count}")

        self.player_choice_label.setText(self.CHOICE_BUTTONS[choice][0])

        # Ducking机制：压低BGM音量
        self.audio_manager.duck_bgm()
        # 播放出拳音效
        self.audio_manager.play_sfx(self.CHOICE_SFX_MAP[choice])

        round_result = self.game_engine.play_round(choice)
        ai_choice = round_result.get("ai_choice")
        self.ai_choice_label.setText(self.CHOICE_BUTTONS[ai_choice][0])

        result = round_result.get("result")
        self._update_result_display(result)

        # 播放判定音效
        self.audio_manager.play_sfx(self.RESULT_SFX_MAP[result])
        # 延迟恢复BGM音量，等待SFX播放完毕
        QTimer.singleShot(1500, self.audio_manager.restore_bgm)

        if self.mode == 3:
            if result == Result.LOSE:
                self.consecutive_wins = 0
            else:
                self.consecutive_wins = self.game_engine.get_consecutive_wins()

        if self.game_engine.is_battle_finished():
            self._finish_game()
        else:
            QTimer.singleShot(1500, self._reset_for_next_round)

    def _update_result_display(self, result: Result):
        """
        更新结果显示
        参数:
            result: 对战结果
        """
        if result == Result.WIN:
            self.player_result_label.setText("胜利！🎉")
            self.player_result_label.setStyleSheet("color: #4ECDC4; font-weight: bold;")
            self.ai_result_label.setText("失败")
            self.ai_result_label.setStyleSheet("color: #FF6B6B;")
            self.result_display.setText("你赢了这一局！")
            self.result_display.setStyleSheet("color: #4ECDC4;")
        elif result == Result.LOSE:
            self.player_result_label.setText("失败")
            self.player_result_label.setStyleSheet("color: #FF6B6B;")
            self.ai_result_label.setText("胜利！🎉")
            self.ai_result_label.setStyleSheet("color: #4ECDC4; font-weight: bold;")
            self.result_display.setText("AI赢了这一局！")
            self.result_display.setStyleSheet("color: #FF6B6B;")
        else:
            self.player_result_label.setText("平局")
            self.player_result_label.setStyleSheet("color: #888;")
            self.ai_result_label.setText("平局")
            self.ai_result_label.setStyleSheet("color: #888;")
            self.result_display.setText("平局！再来一次~")
            self.result_display.setStyleSheet("color: #888;")

    def _reset_for_next_round(self):
        """
        重置界面准备下一回合
        """
        self.player_choice_label.setText("❓")
        self.ai_choice_label.setText("❓")
        self.player_result_label.setText("")
        self.ai_result_label.setText("")
        self.result_display.setText("")

        for btn in self.choice_buttons.values():
            btn.setEnabled(True)
            btn.setVisible(True)
        self._show_choice_prompt()

    def _hide_choice_prompt(self):
        """隐藏出拳提示标签，为结算信息腾出空间"""
        for i in range(self.layout().count()):
            item = self.layout().itemAt(i)
            if item and item.widget():
                widget = item.widget()
                if isinstance(widget, QLabel) and "请选择" in widget.text():
                    widget.setVisible(False)
                    break

    def _show_choice_prompt(self):
        """显示出拳提示标签"""
        for i in range(self.layout().count()):
            item = self.layout().itemAt(i)
            if item and item.widget():
                widget = item.widget()
                if isinstance(widget, QLabel) and "请选择" in widget.text():
                    widget.setVisible(True)
                    break

    def _finish_game(self):
        """
        结束游戏并计算积分
        """
        final_result = self.game_engine.get_final_result()
        result_text = {
            Result.WIN: "🎉 恭喜你获胜！",
            Result.LOSE: "😅 AI获胜，再接再厉！",
            Result.DRAW: "🤝 平局！"
        }.get(final_result, "")

        if self.mode == 3:
            self.score_change = self.score_manager.calculate_score_change(
                self.mode,
                final_result.value,
                self.round_count,
                self.consecutive_wins
            )
        else:
            self.score_change = self.score_manager.calculate_score_change(
                self.mode,
                final_result.value
            )

        if self.score_change != 0:
            self.score_manager.update_battle_result(
                self.user_id, final_result.value, self.score_change
            )
        else:
            self.score_manager.update_battle_result(
                self.user_id, final_result.value, 0
            )

        self.game_engine.save_battle_record(self.score_change)

        # 切换到结算BGM
        result_str = "win" if final_result == Result.WIN else "lose"
        self.audio_manager.switch_bgm("settlement", mode=self.mode, result=result_str)

        score_text = f"积分变化: {'+' if self.score_change > 0 else ''}{self.score_change}"
        full_text = f"{result_text}  {score_text}"

        if self.mode == 3 and self.consecutive_wins >= 3:
            full_text += f"\n🌟 连续胜利奖励 +5！"

        self.result_display.setText(full_text)

        for btn in self.choice_buttons.values():
            btn.setVisible(False)
        self._hide_choice_prompt()

        self._show_finish_buttons()

    def _show_finish_buttons(self):
        """
        显示结束按钮
        """
        if self._finish_button_layout is not None:
            return
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        continue_button = QPushButton("🔄 再来一局")
        continue_button.setFont(QFont("Microsoft YaHei", 11))
        continue_button.setFixedSize(120, 40)
        continue_button.setCursor(Qt.CursorShape.PointingHandCursor)
        continue_button.setStyleSheet("""
            QPushButton {
                background-color: #4ECDC4;
                color: white;
                border: none;
                border-radius: 20px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #45B7AA;
            }
        """)
        continue_button.clicked.connect(self._on_continue_clicked)

        finish_button = QPushButton("🏠 返回主界面")
        finish_button.setFont(QFont("Microsoft YaHei", 11))
        finish_button.setFixedSize(120, 40)
        finish_button.setCursor(Qt.CursorShape.PointingHandCursor)
        finish_button.setStyleSheet("""
            QPushButton {
                background-color: #FFE66D;
                color: #666;
                border: none;
                border-radius: 20px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #FFE04D;
            }
        """)
        finish_button.clicked.connect(self._on_finish_clicked)

        button_layout.addWidget(continue_button)
        button_layout.addWidget(finish_button)
        button_layout.addStretch()

        layout = self.layout()
        layout.addLayout(button_layout)
        self._finish_button_layout = button_layout

    def _on_continue_clicked(self):
        """
        处理继续游戏按钮点击
        连战模式需检查积分是否满足入场要求
        """
        if self.mode == 3:
            current_score = self.score_manager.get_score(self.user_id)
            if current_score < 3:
                QMessageBox.warning(
                    self,
                    "积分不足",
                    f"积分不足，无法继续对战\n当前积分：{current_score}，需要3积分入场"
                )
                return

            reply = QMessageBox.question(
                self,
                "确认入场",
                f"连战模式需要消耗3积分入场，当前积分：{current_score}\n是否继续？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

            success, message = self.score_manager.deduct_entry_fee(self.user_id, self.mode)
            if not success:
                QMessageBox.warning(self, "入场失败", message)
                return

        if self._finish_button_layout is not None:
            while self._finish_button_layout.count():
                item = self._finish_button_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            self.layout().removeItem(self._finish_button_layout)
            self._finish_button_layout = None

        self.game_engine.start_game(self.user_id, self.mode)
        # 再来一局时重新播放对战BGM
        self.audio_manager.switch_bgm("battle", mode=self.mode)
        self.round_count = 0
        self.consecutive_wins = 0
        self.score_change = 0
        self.round_label.setText(f"回合: {self.round_count}")
        self._reset_for_next_round()

    def _on_finish_clicked(self):
        """
        处理返回主界面按钮点击
        """
        self.game_engine.end_game()
        self.game_finished.emit(self.score_change)
        self.close()

    def closeEvent(self, event):
        """
        窗口关闭事件
        """
        self.game_engine.end_game()
        self.closed.emit()
        event.accept()
