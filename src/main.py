"""
猜拳小游戏 - 主程序入口
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox, QWidget
from PyQt6.QtCore import Qt

from src.ui.login_window import LoginWindow
from src.ui.main_window import MainWindow


class GameMainWindow(QMainWindow):
    """
    游戏主窗口类
    作为容器管理登录窗口和主界面的切换
    根据当前中央组件动态调整窗口尺寸
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("猜拳小游戏")
        self.setWindowFlags(Qt.WindowType.WindowCloseButtonHint | Qt.WindowType.WindowMinimizeButtonHint)

        self.login_window = LoginWindow()
        self.login_window.login_success.connect(self._on_login_success)
        self.setCentralWidget(self.login_window)
        self._adjust_size(self.login_window)

    def _adjust_size(self, widget: QWidget):
        """
        根据中央组件的尺寸需求调整窗口大小
        参数:
            widget: 当前中央组件
        """
        min_w = widget.minimumWidth() if widget.minimumWidth() > 0 else widget.width()
        min_h = widget.minimumHeight() if widget.minimumHeight() > 0 else widget.height()
        max_w = widget.maximumWidth() if widget.maximumWidth() < 16777215 else min_w
        max_h = widget.maximumHeight() if widget.maximumHeight() < 16777215 else min_h + 120

        self.setMinimumSize(min_w, min_h)
        self.setMaximumSize(max_w, max_h)
        self.resize(min_w, min_h)

    def _on_login_success(self, user_id: int, username: str):
        """
        处理登录成功事件
        参数:
            user_id: 用户ID
            username: 用户名
        """
        try:
            self.main_window = MainWindow(user_id, username)

            if self.main_window.is_init_failed():
                QMessageBox.critical(
                    self,
                    "登录失败",
                    "主窗口初始化失败，请重新登录。"
                )
                return

            self.main_window.logout_requested.connect(self._on_logout_requested)
            self.setCentralWidget(self.main_window)
            self._adjust_size(self.main_window)
        except Exception as e:
            print(f"登录后初始化主窗口失败: {e}")
            QMessageBox.critical(
                self,
                "登录失败",
                f"登录成功但无法进入游戏界面。错误信息: {str(e)}"
            )

    def _on_logout_requested(self):
        """
        处理退出登录请求
        返回登录界面
        """
        self.login_window = LoginWindow()
        self.login_window.login_success.connect(self._on_login_success)
        self.setCentralWidget(self.login_window)
        self._adjust_size(self.login_window)


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = GameMainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
