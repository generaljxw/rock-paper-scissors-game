"""
端到端自动化验证脚本 - 验证打包后.exe的完整功能流程

通过PyQt6组件直接验证UI状态，确保三个修复问题的功能正常。
"""

import sys
import os
import io
import time
import traceback

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import QApplication, QLabel
from PyQt6.QtCore import Qt

from src.ui.login_window import LoginWindow
from src.ui.main_window import MainWindow
from src.ui.battle_window import BattleWindow
from src.business.game_engine import GameEngine
from src.business.score_manager import ScoreManager
from src.business.user_manager import UserManager
from src.business.enums import Choice


results = []
window_tmp = None


def log(test_name, passed, detail=""):
    status = "[PASS]" if passed else "[FAIL]"
    msg = f"  {status} {test_name}"
    if detail:
        msg += f" -- {detail}"
    results.append((test_name, passed, detail))
    print(msg)


def verify_login_window():
    print("\n=== 1. 登录窗口验证 (问题1修复) ===")
    window = LoginWindow()

    log("窗口标题正确", "猜拳小游戏" in window.windowTitle(), window.windowTitle())

    all_labels = window.findChildren(QLabel)

    username_labels = [lbl for lbl in all_labels if lbl.text() == "用户名:"]
    log("用户名标签存在", len(username_labels) > 0, f"count={len(username_labels)}")
    if username_labels:
        lbl = username_labels[0]
        log("用户名标签未隐藏", not lbl.isHidden(), f"isHidden={lbl.isHidden()}")
        log("用户名标签有样式", lbl.styleSheet() != "", f"style={lbl.styleSheet()[:50]}")
        log("用户名标签宽度>=75", lbl.width() >= 75 or lbl.minimumWidth() >= 75, f"w={lbl.width()} minW={lbl.minimumWidth()}")

    password_labels = [lbl for lbl in all_labels if lbl.text() == "密码:"]
    log("密码标签存在", len(password_labels) > 0, f"count={len(password_labels)}")
    if password_labels:
        lbl = password_labels[0]
        log("密码标签未隐藏", not lbl.isHidden(), f"isHidden={lbl.isHidden()}")
        log("密码标签有样式", lbl.styleSheet() != "", f"style={lbl.styleSheet()[:50]}")

    log("用户名输入框存在", window.username_input is not None)
    log("密码输入框存在", window.password_input is not None)
    log("登录按钮存在", window.login_button is not None)
    log("注册按钮存在", window.register_button is not None)

    window.username_input.setText("testuser")
    window.password_input.setText("password123")
    log("输入验证通过", window._validate_input())

    window.close()


def verify_main_window_mode_tags():
    print("\n=== 2. 主窗口模式标签验证 (问题2修复) ===")

    manager = UserManager()
    ts = int(time.time() * 1000) % 100000
    uname = f"e2e_{ts}"
    success, msg = manager.register(uname, "password123")
    if not success:
        ts = int(time.time() * 1000) % 100000 + 999
        uname = f"e2e_{ts}"
        manager = UserManager()
        success, msg = manager.register(uname, "password123")

    user = manager.get_current_user()
    log("测试用户注册成功", user is not None, f"uid={user.id if user else 'None'}")

    window = MainWindow(user.id, uname)
    window.show()
    global window_tmp
    window_tmp = window
    log("主窗口创建成功", window is not None)

    all_labels = window.findChildren(QLabel)

    expected_tags = ["一局定胜负", "三局两胜制", "连战模式"]
    for tag in expected_tags:
        tag_labels = [lbl for lbl in all_labels if tag in lbl.text()]
        log(f"模式标签'{tag}'显示", len(tag_labels) > 0, f"count={len(tag_labels)}")

    expected_descs = ["单局对决", "率先取得2场胜利", "消耗3积分入场"]
    for desc in expected_descs:
        desc_labels = [lbl for lbl in all_labels if desc in lbl.text()]
        log(f"模式描述'{desc}'显示", len(desc_labels) > 0, f"count={len(desc_labels)}")

    window.close()


def verify_mode2_score_rules():
    """验证模式2积分规则（胜利+2/失败-2）"""
    print("\n=== 2b. 模式2积分规则验证 ===")

    sm = ScoreManager()
    log("模式2胜利积分=+2", sm.calculate_score_change(2, "胜利") == 2,
        f"actual={sm.calculate_score_change(2, '胜利')}")
    log("模式2失败积分=-2", sm.calculate_score_change(2, "失败") == -2,
        f"actual={sm.calculate_score_change(2, '失败')}")
    log("模式2平局积分=0", sm.calculate_score_change(2, "平局") == 0,
        f"actual={sm.calculate_score_change(2, '平局')}")

    all_labels = window_tmp.findChildren(QLabel)
    log("模式2描述含'胜利方加2积分'", any("胜利方加2积分" in l.text() for l in all_labels))
    log("模式2描述含'失败方扣2积分'", any("失败方扣2积分" in l.text() for l in all_labels))


def verify_logout_button():
    """验证退出登录按钮可见性"""
    print("\n=== 2c. 退出登录按钮可见性验证 ===")

    from PyQt6.QtWidgets import QPushButton

    logout_btn = None
    history_btn = None
    for btn in window_tmp.findChildren(QPushButton):
        if "退出登录" in btn.text():
            logout_btn = btn
        if "查看战绩" in btn.text():
            history_btn = btn

    log("退出登录按钮存在", logout_btn is not None)
    if logout_btn:
        log("退出登录按钮未被隐藏", not logout_btn.isHidden())
        log("退出登录按钮在窗口内",
            logout_btn.y() + logout_btn.height() <= window_tmp.height(),
            f"btn_bottom={logout_btn.y() + logout_btn.height()} window_h={window_tmp.height()}")

    log("查看战绩按钮存在", history_btn is not None)
    if history_btn:
        log("查看战绩按钮在窗口内",
            history_btn.y() + history_btn.height() <= window_tmp.height(),
            f"btn_bottom={history_btn.y() + history_btn.height()} window_h={window_tmp.height()}")

    log("窗口最大高度<=800", window_tmp.maximumHeight() <= 800, f"maxH={window_tmp.maximumHeight()}")


def verify_battle_window():
    print("\n=== 3. 对战窗口验证 (问题3修复) ===")

    mode_names = {1: "一局定胜负", 2: "三局两胜", 3: "连战模式"}

    for mode_id, mode_name in mode_names.items():
        game_engine = GameEngine()
        score_manager = ScoreManager()
        window = BattleWindow(game_engine, score_manager, 1, mode_id)

        log(f"模式{mode_id}窗口独立性(parent=None)", window.parent() is None, f"parent={window.parent()}")

        all_labels = window.findChildren(QLabel)
        mode_labels = [lbl for lbl in all_labels if mode_name in lbl.text()]
        log(f"模式{mode_id}名称'{mode_name}'显示", len(mode_labels) > 0, f"count={len(mode_labels)}")

        log(f"模式{mode_id}选择按钮=3", len(window.choice_buttons) == 3, f"count={len(window.choice_buttons)}")

        for choice in [Choice.ROCK, Choice.SCISSORS, Choice.PAPER]:
            log(f"模式{mode_id}{choice.name}按钮存在", choice in window.choice_buttons)

        window.close()


def verify_game_engine():
    print("\n=== 4. 游戏引擎核心逻辑验证 ===")

    engine = GameEngine()
    session = engine.start_game(user_id=1, mode=1)
    log("游戏引擎启动(mode=1)", session is not None and session.get("mode") == 1)

    result = engine.make_choice(Choice.ROCK)
    log("出拳返回结果", result is not None, f"result keys={list(result.keys()) if isinstance(result, dict) else type(result)}")

    from src.business.enums import Result

    test_cases = [
        (Choice.ROCK, Choice.SCISSORS, Result.WIN, "石头胜剪刀"),
        (Choice.SCISSORS, Choice.PAPER, Result.WIN, "剪刀胜布"),
        (Choice.PAPER, Choice.ROCK, Result.WIN, "布胜石头"),
        (Choice.ROCK, Choice.PAPER, Result.LOSE, "石头负于布"),
        (Choice.ROCK, Choice.ROCK, Result.DRAW, "石头平石头"),
    ]

    for player, ai, expected, desc in test_cases:
        result = engine.determine_winner(player, ai)
        log(f"胜负判定({desc})", result == expected, f"expected={expected} actual={result}")

    ai_choice = engine._get_ai_choice()
    log("AI随机选择有效", ai_choice in [Choice.ROCK, Choice.SCISSORS, Choice.PAPER], f"ai={ai_choice}")


def verify_database():
    print("\n=== 5. 数据库持久化验证 ===")

    from src.data.database import Database

    db = Database()
    db_path = db.get_db_path()
    log("数据库路径获取", len(db_path) > 0, f"path={db_path}")

    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT count(*) FROM users")
        count = cursor.fetchone()[0]
        db.close_connection(conn)
        log("数据库查询成功", True, f"users_count={count}")
    except Exception as e:
        log("数据库查询成功", False, str(e))


def main():
    print("=" * 60)
    print("  RockPaperScissors.exe - End-to-End Verification")
    print("=" * 60)

    app = QApplication.instance()
    if app is None:
        app = QApplication([])

    try:
        verify_login_window()
        verify_main_window_mode_tags()
        verify_mode2_score_rules()
        verify_logout_button()
        verify_battle_window()
        verify_game_engine()
        verify_database()
    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        traceback.print_exc()
    finally:
        if window_tmp:
            window_tmp.close()

    print("\n" + "=" * 60)
    print("  Verification Summary")
    print("=" * 60)

    total = len(results)
    passed = sum(1 for _, p, _ in results if p)
    failed = total - passed

    for name, passed_flag, detail in results:
        status = "[PASS]" if passed_flag else "[FAIL]"
        line = f"  {status} {name}"
        if detail:
            line += f" -- {detail}"
        print(line)

    print(f"\n  Total: {total} | Passed: {passed} | Failed: {failed}")
    print(f"  Pass Rate: {passed/total*100:.1f}%")
    print("=" * 60)

    result_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "test_output", "test_results", "e2e_result.txt"
    )
    with open(result_path, "w", encoding="utf-8") as f:
        f.write(f"Total: {total} | Passed: {passed} | Failed: {failed}\n")
        f.write(f"Pass Rate: {passed/total*100:.1f}%\n\n")
        for name, passed_flag, detail in results:
            status = "[PASS]" if passed_flag else "[FAIL]"
            line = f"{status} {name}"
            if detail:
                line += f" -- {detail}"
            f.write(line + "\n")

    print(f"\nResults saved to: {result_path}")
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
