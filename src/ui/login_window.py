"""
UI层登录窗口模块

本模块实现用户登录界面，支持用户登录和注册功能，
界面设计采用儿童友好的卡通风格。
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap, QIcon

from ..business.user_manager import UserManager
from ..audio.audio_manager import get_audio_manager
from .main_window import MainWindow


class LoginWindow(QWidget):
    """
    登录窗口类
    提供用户登录和注册功能，界面风格儿童友好
    """

    login_success = pyqtSignal(int, str)

    def __init__(self):
        super().__init__()
        self.user_manager = UserManager()
        self.audio_manager = get_audio_manager()
        self.main_window = None
        self._init_ui()
        # 登录界面显示时播放BGM
        self.audio_manager.play_bgm("login")

    def _init_ui(self):
        """
        初始化UI组件
        """
        self.setWindowTitle("猜拳小游戏 - 登录")
        self.setFixedSize(500, 450)
        self.setWindowFlags(Qt.WindowType.WindowCloseButtonHint | Qt.WindowType.WindowMinimizeButtonHint)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 30, 40, 30)
        main_layout.setSpacing(15)

        title_label = QLabel("✊ 猜拳小游戏 ✋")
        title_label.setFont(QFont("Microsoft YaHei", 24, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #FF6B6B; padding: 10px;")

        subtitle_label = QLabel("欢迎来到有趣的猜拳世界！")
        subtitle_label.setFont(QFont("Microsoft YaHei", 12))
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("color: #888; padding-bottom: 20px;")

        input_frame = QFrame()
        input_frame.setObjectName("inputFrame")
        input_frame.setFrameShape(QFrame.Shape.StyledPanel)
        input_frame.setStyleSheet("""
            QFrame#inputFrame {
                background-color: #FFF9E6;
                border-radius: 15px;
                border: 2px solid #FFE4B5;
                padding: 20px;
            }
        """)
        input_layout = QVBoxLayout()
        input_layout.setSpacing(20)

        username_layout = QHBoxLayout()
        username_label = QLabel("用户名:")
        username_label.setFont(QFont("Microsoft YaHei", 12))
        username_label.setFixedWidth(75)
        username_label.setStyleSheet("color: #333;")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("请输入用户名（至少3个字符）")
        self.username_input.setFont(QFont("Microsoft YaHei", 11))
        self.username_input.setFixedHeight(40)
        self.username_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #DDD;
                border-radius: 10px;
                padding: 8px 15px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #FF6B6B;
                background-color: #FFF;
            }
        """)
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_input)
        input_layout.addLayout(username_layout)

        password_layout = QHBoxLayout()
        password_label = QLabel("密码:")
        password_label.setFont(QFont("Microsoft YaHei", 12))
        password_label.setFixedWidth(75)
        password_label.setStyleSheet("color: #333;")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("请输入密码（至少6个字符）")
        self.password_input.setFont(QFont("Microsoft YaHei", 11))
        self.password_input.setFixedHeight(40)
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #DDD;
                border-radius: 10px;
                padding: 8px 15px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #FF6B6B;
                background-color: #FFF;
            }
        """)
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        input_layout.addLayout(password_layout)

        input_frame.setLayout(input_layout)
        main_layout.addWidget(title_label)
        main_layout.addWidget(subtitle_label)
        main_layout.addWidget(input_frame)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)

        self.login_button = QPushButton("🎮 登录")
        self.login_button.setFont(QFont("Microsoft YaHei", 12, QFont.Weight.Bold))
        self.login_button.setFixedSize(140, 50)
        self.login_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #4ECDC4;
                color: white;
                border: none;
                border-radius: 25px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #45B7AA;
            }
            QPushButton:pressed {
                background-color: #3DA39B;
            }
        """)
        self.login_button.clicked.connect(self._on_login_clicked)

        self.register_button = QPushButton("✨ 注册")
        self.register_button.setFont(QFont("Microsoft YaHei", 12, QFont.Weight.Bold))
        self.register_button.setFixedSize(140, 50)
        self.register_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.register_button.setStyleSheet("""
            QPushButton {
                background-color: #FFE66D;
                color: #666;
                border: none;
                border-radius: 25px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #FFE04D;
            }
            QPushButton:pressed {
                background-color: #FFD633;
            }
        """)
        self.register_button.clicked.connect(self._on_register_clicked)

        button_layout.addWidget(self.login_button)
        button_layout.addWidget(self.register_button)
        main_layout.addLayout(button_layout)

        hint_label = QLabel("💡 提示：首次使用请先注册账号")
        hint_label.setFont(QFont("Microsoft YaHei", 10))
        hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint_label.setStyleSheet("color: #AAA; padding-top: 15px;")
        main_layout.addWidget(hint_label)

        self.setLayout(main_layout)
        self.setStyleSheet("background-color: #F5F5F5;")

    def _validate_input(self) -> bool:
        """
        验证用户输入
        返回:
            是否验证通过
        """
        username = self.username_input.text().strip()
        password = self.password_input.text()

        if not username:
            self._show_error("请输入用户名")
            return False

        if len(username) < 3:
            self._show_error("用户名长度不能少于3个字符")
            return False

        if not password:
            self._show_error("请输入密码")
            return False

        if len(password) < 6:
            self._show_error("密码长度不能少于6个字符")
            return False

        return True

    def _on_login_clicked(self):
        """
        处理登录按钮点击事件
        """
        if not self._validate_input():
            return

        username = self.username_input.text().strip()
        password = self.password_input.text()

        success, message = self.user_manager.login(username, password)

        if success:
            user = self.user_manager.get_current_user()
            self._show_success(f"登录成功！欢迎 {user.username}！🎉")
            # 登录成功后切换到模式选择界面BGM
            self.audio_manager.switch_bgm("mode_select")
            self.login_success.emit(user.id, user.username)
        else:
            self._show_error(message)

    def _on_register_clicked(self):
        """
        处理注册按钮点击事件
        """
        if not self._validate_input():
            return

        username = self.username_input.text().strip()
        password = self.password_input.text()

        success, message = self.user_manager.register(username, password)

        if success:
            self._show_success(f"注册成功！请使用新账号登录！🎉")
            self.username_input.clear()
            self.password_input.clear()
        else:
            self._show_error(message)

    def _show_error(self, message: str):
        """
        显示错误消息
        参数:
            message: 错误消息内容
        """
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setWindowTitle("提示")
        msg_box.setText(message)
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #FFF;
            }
            QMessageBox QLabel {
                color: #333;
                font-size: 14px;
            }
            QPushButton {
                background-color: #FF6B6B;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 8px 25px;
                font-size: 13px;
            }
        """)
        msg_box.exec()

    def _show_success(self, message: str):
        """
        显示成功消息
        参数:
            message: 成功消息内容
        """
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setWindowTitle("成功")
        msg_box.setText(message)
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #FFF;
            }
            QMessageBox QLabel {
                color: #333;
                font-size: 14px;
            }
            QPushButton {
                background-color: #4ECDC4;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 8px 25px;
                font-size: 13px;
            }
        """)
        msg_box.exec()

    def get_user_manager(self) -> UserManager:
        """
        获取用户管理器实例
        返回:
            UserManager实例
        """
        return self.user_manager
