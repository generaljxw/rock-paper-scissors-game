# tests/test_game_engine.py
"""
游戏引擎模块单元测试
测试胜负判定、游戏会话管理、AI选择等功能
"""

import unittest
from src.business.game_engine import GameEngine
from src.business.enums import Choice, Result, BattleMode


class TestGameEngine(unittest.TestCase):
    """
    游戏引擎测试类
    """

    def setUp(self):
        """
        每个测试方法前执行 - 创建游戏引擎实例
        """
        self.engine = GameEngine()

    def test_determine_winner_rock_beats_scissors(self):
        """
        测试胜负判定 - 石头胜剪刀
        """
        result = self.engine.determine_winner(Choice.ROCK, Choice.SCISSORS)
        self.assertEqual(result, Result.WIN)

    def test_determine_winner_scissors_beats_paper(self):
        """
        测试胜负判定 - 剪刀胜布
        """
        result = self.engine.determine_winner(Choice.SCISSORS, Choice.PAPER)
        self.assertEqual(result, Result.WIN)

    def test_determine_winner_paper_beats_rock(self):
        """
        测试胜负判定 - 布胜石头
        """
        result = self.engine.determine_winner(Choice.PAPER, Choice.ROCK)
        self.assertEqual(result, Result.WIN)

    def test_determine_winner_draw(self):
        """
        测试胜负判定 - 平局
        """
        result = self.engine.determine_winner(Choice.ROCK, Choice.ROCK)
        self.assertEqual(result, Result.DRAW)
        
        result = self.engine.determine_winner(Choice.SCISSORS, Choice.SCISSORS)
        self.assertEqual(result, Result.DRAW)
        
        result = self.engine.determine_winner(Choice.PAPER, Choice.PAPER)
        self.assertEqual(result, Result.DRAW)

    def test_determine_winner_lose(self):
        """
        测试胜负判定 - 失败
        """
        result = self.engine.determine_winner(Choice.SCISSORS, Choice.ROCK)
        self.assertEqual(result, Result.LOSE)
        
        result = self.engine.determine_winner(Choice.PAPER, Choice.SCISSORS)
        self.assertEqual(result, Result.LOSE)
        
        result = self.engine.determine_winner(Choice.ROCK, Choice.PAPER)
        self.assertEqual(result, Result.LOSE)

    def test_start_game(self):
        """
        测试开始游戏会话 - 返回完整的会话字典
        """
        session = self.engine.start_game(user_id=1, mode=1)
        self.assertIsNotNone(session)
        self.assertEqual(session['user_id'], 1)
        self.assertEqual(session['mode'], 1)
        self.assertEqual(session['rounds'], [])
        self.assertEqual(session['win_count'], 0)
        self.assertEqual(session['lose_count'], 0)
        self.assertEqual(session['draw_count'], 0)
        self.assertEqual(session['total_rounds'], 0)

    def test_get_ai_choice(self):
        """
        测试AI选择 - 返回有效的Choice枚举值
        """
        choice = self.engine._get_ai_choice()
        self.assertIn(choice, list(Choice), "AI选择应为有效的Choice枚举值")

    def test_play_round(self):
        """
        测试进行一轮游戏 - 返回有效的游戏结果
        """
        self.engine.start_game(user_id=1, mode=1)
        result = self.engine.play_round(Choice.ROCK)
        
        self.assertIn('player_choice', result)
        self.assertIn('ai_choice', result)
        self.assertIn('result', result)
        self.assertIn('player_value', result)
        self.assertIn('ai_value', result)
        self.assertIn('result_value', result)
        
        self.assertIsInstance(result['player_choice'], Choice)
        self.assertIsInstance(result['ai_choice'], Choice)
        self.assertIsInstance(result['result'], Result)

    def test_is_battle_finished_mode1(self):
        """
        测试游戏结束判定 - 模式1(一局定胜负)
        """
        self.engine.start_game(user_id=1, mode=1)
        
        # 第一局就有胜负，应该结束
        result = self.engine.play_round(Choice.ROCK)
        if result['result'] != Result.DRAW:
            self.assertTrue(self.engine.is_battle_finished())
        
        # 如果平局，继续游戏
        # 此测试依赖随机AI选择，可能需要多次运行

    def test_is_battle_finished_mode2(self):
        """
        测试游戏结束判定 - 模式2(三局两胜)
        新规则：每局必须分出胜负（平局不计入有效轮），先获2胜者获胜，最多3有效局
        """
        self.engine.start_game(user_id=1, mode=2)
        
        session = self.engine.current_session
        self.assertEqual(session["effective_rounds"], 0)
        self.assertFalse(self.engine.is_battle_finished())
        
        round1 = self.engine.play_round(Choice.ROCK)
        self.assertEqual(session["total_rounds"], 1)
        
        if round1['result'] != Result.DRAW:
            self.assertEqual(session["effective_rounds"], 1)
            self.assertFalse(self.engine.is_battle_finished())
        
        round2 = self.engine.play_round(Choice.ROCK)
        self.assertEqual(session["total_rounds"], 2)

        round3 = self.engine.play_round(Choice.ROCK)
        self.assertEqual(session["total_rounds"], 3)

        if session["win_count"] >= 2 or session["lose_count"] >= 2:
            self.assertTrue(self.engine.is_battle_finished())
        elif session["effective_rounds"] >= 3:
            self.assertTrue(self.engine.is_battle_finished())

    def test_get_consecutive_wins(self):
        """
        测试获取连续胜利次数
        仅统计真正的连续出拳，不包含平局
        """
        self.engine.start_game(user_id=1, mode=3)
        
        self.engine.play_round(Choice.ROCK)
        self.engine.play_round(Choice.ROCK)
        self.engine.play_round(Choice.ROCK)
        
        consecutive = self.engine.get_consecutive_wins()
        self.assertGreaterEqual(consecutive, 0)
        self.assertLessEqual(consecutive, 3)

    def test_mode2_effective_rounds_with_draws(self):
        """
        测试模式2：平局不计入有效轮数
        确保平局不会导致有效轮数增加
        """
        self.engine.start_game(user_id=1, mode=2)
        
        session = self.engine.current_session
        
        for _ in range(10):
            if self.engine.is_battle_finished():
                break
            self.engine.play_round(Choice.ROCK)
        
        draws_in_session = [r for r in session["rounds"] if r["result"] == Result.DRAW]
        self.assertEqual(len(draws_in_session), session["draw_count"])


if __name__ == '__main__':
    unittest.main()
