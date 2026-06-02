"""
UI层历史记录窗口模块

本模块实现用户战绩查询界面，
显示历史对战记录和统计数据。
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTableWidget, QTableWidgetItem, QPushButton, QHeaderView
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from ..business.statistics import Statistics


class HistoryWindow(QWidget):
    """
    历史记录窗口类
    显示用户的历史对战记录和统计数据
    """

    closed = pyqtSignal()

    def __init__(self, user_id: int, statistics: Statistics):
        super().__init__()
        self.user_id = user_id
        self.statistics = statistics
        self._init_ui()
        self._load_data()

    def _init_ui(self):
        """
        初始化UI组件
        """
        self.setWindowTitle("猜拳小游戏 - 战绩查询")
        self.setFixedSize(750, 500)
        self.setWindowFlags(Qt.WindowType.WindowCloseButtonHint | Qt.WindowType.WindowMinimizeButtonHint)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(25, 20, 25, 20)
        main_layout.setSpacing(15)

        title_label = QLabel("📊 我的战绩")
        title_label.setFont(QFont("Microsoft YaHei", 20, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #FF6B6B; padding: 10px;")
        main_layout.addWidget(title_label)

        stats_frame = QWidget()
        stats_frame.setStyleSheet("""
            QWidget {
                background-color: #FFF9E6;
                border-radius: 15px;
                border: 2px solid #FFE4B5;
                padding: 15px;
            }
        """)
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(30)

        summary = self.statistics.get_statistics_summary(self.user_id)

        self._create_stat_card(stats_layout, "总积分", f"{summary['total_score']}", "#FF6B6B")
        self._create_stat_card(stats_layout, "胜场", f"{summary['win_count']}", "#4ECDC4")
        self._create_stat_card(stats_layout, "负场", f"{summary['lose_count']}", "#FFB6C1")
        self._create_stat_card(stats_layout, "平局", f"{summary['draw_count']}", "#888")
        self._create_stat_card(stats_layout, "胜率", f"{summary['win_rate']}%", "#FFE66D")

        stats_frame.setLayout(stats_layout)
        main_layout.addWidget(stats_frame)

        history_label = QLabel("📜 最近对战记录")
        history_label.setFont(QFont("Microsoft YaHei", 14, QFont.Weight.Bold))
        history_label.setStyleSheet("color: #333; padding: 10px 0;")
        main_layout.addWidget(history_label)

        self.history_table = QTableWidget()
        self.history_table.setColumnCount(4)
        self.history_table.setHorizontalHeaderLabels(["对战时间", "游戏模式", "对战结果", "积分变化"])
        self.history_table.setFont(QFont("Microsoft YaHei", 10))
        self.history_table.setAlternatingRowColors(True)
        self.history_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.history_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.history_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 2px solid #EEE;
                border-radius: 10px;
                gridline-color: #F0F0F0;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                background-color: #FFF9E6;
                color: #333;
                font-weight: bold;
                padding: 10px;
                border: none;
                border-bottom: 2px solid #FFE4B5;
            }
            QTableWidget::item:selected {
                background-color: #FFE0E0;
            }
        """)
        main_layout.addWidget(self.history_table)

        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()

        close_button = QPushButton("返回主界面")
        close_button.setFont(QFont("Microsoft YaHei", 11))
        close_button.setFixedSize(120, 40)
        close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #FF6B6B;
                color: white;
                border: none;
                border-radius: 20px;
                padding: 8px 20px;
            }
            QPushButton:hover {
                background-color: #FF5252;
            }
        """)
        close_button.clicked.connect(self.close)

        bottom_layout.addWidget(close_button)
        main_layout.addLayout(bottom_layout)

        self.setLayout(main_layout)
        self.setStyleSheet("background-color: #F5F5F5;")

    def _create_stat_card(self, layout: QHBoxLayout, title: str, value: str, color: str):
        """
        创建统计卡片
        参数:
            layout: 布局
            title: 标题
            value: 数值
            color: 颜色
        """
        card = QWidget()
        card.setStyleSheet(f"""
            QWidget {{
                background-color: white;
                border-radius: 10px;
                padding: 10px 15px;
                border: 2px solid {color};
            }}
        """)
        card_layout = QVBoxLayout()
        card_layout.setSpacing(5)

        title_label = QLabel(title)
        title_label.setFont(QFont("Microsoft YaHei", 10))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(f"color: {color};")

        value_label = QLabel(value)
        value_label.setFont(QFont("Microsoft YaHei", 16, QFont.Weight.Bold))
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label.setStyleSheet("color: #333;")

        card_layout.addWidget(title_label)
        card_layout.addWidget(value_label)
        card.setLayout(card_layout)
        layout.addWidget(card)

    def _load_data(self):
        """
        加载历史数据
        """
        history = self.statistics.get_battle_history(self.user_id, 20)

        self.history_table.setRowCount(len(history))
        mode_names = {1: "一局定胜负", 2: "三局两胜", 3: "连战模式"}

        for row, record in enumerate(history):
            time_item = QTableWidgetItem(str(record.created_at)[:19] if record.created_at else "-")
            time_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            mode_item = QTableWidgetItem(mode_names.get(record.mode, f"模式{record.mode}"))
            mode_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            result = record.result
            if result == "胜利":
                result_text = "胜利"
                result_item = QTableWidgetItem(result_text)
                result_item.setForeground(Qt.GlobalColor.darkGreen)
            elif result == "失败":
                result_text = "失败"
                result_item = QTableWidgetItem(result_text)
                result_item.setForeground(Qt.GlobalColor.darkRed)
            else:
                result_text = "平局"
                result_item = QTableWidgetItem(result_text)
                result_item.setForeground(Qt.GlobalColor.darkGray)
            result_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            score_change = record.score_change
            if score_change > 0:
                score_text = f"+{score_change}"
                score_item = QTableWidgetItem(score_text)
                score_item.setForeground(Qt.GlobalColor.darkGreen)
            elif score_change < 0:
                score_text = f"{score_change}"
                score_item = QTableWidgetItem(score_text)
                score_item.setForeground(Qt.GlobalColor.darkRed)
            else:
                score_item = QTableWidgetItem("0")
                score_item.setForeground(Qt.GlobalColor.darkGray)
            score_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            self.history_table.setItem(row, 0, time_item)
            self.history_table.setItem(row, 1, mode_item)
            self.history_table.setItem(row, 2, result_item)
            self.history_table.setItem(row, 3, score_item)

    def closeEvent(self, event):
        """
        窗口关闭事件
        """
        self.closed.emit()
        event.accept()
