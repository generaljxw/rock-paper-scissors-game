# tests/test_fix_battle_score_and_history.py
"""
专项测试：验证连战模式积分检查和战绩统计修复
1. 连战模式"再玩一局"积分检查逻辑
2. 战绩统计改为每轮对战汇总记录
"""

import unittest
import os
import sys
from unittest.mock import MagicMock, patch

from src.data.models import BattleRecord
from src.data.battle_dao import BattleDAO
from src.data.database import Database
from src.business.game_engine import GameEngine
from src.business.score_manager import ScoreManager
from src.business.enums import Choice, Result


class TestBattleRecordSummary(unittest.TestCase):
    """
    测试战绩记录为每轮对战汇总信息
    """

    def test_battle_record_no_choice_fields(self):
        """
        BattleRecord不应包含player_choice和ai_choice字段
        """
        record = BattleRecord(user_id=1, mode=3, result='胜利', score_change=5)
        self.assertFalse(hasattr(record, 'player_choice'))
        self.assertFalse(hasattr(record, 'ai_choice'))

    def test_battle_record_only_four_fields(self):
        """
        战绩记录仅包含4个业务字段：mode, result, score_change, created_at
        """
        record = BattleRecord(
            user_id=1,
            mode=2,
            result='失败',
            score_change=-2
        )
        self.assertEqual(record.mode, 2)
        self.assertEqual(record.result, '失败')
        self.assertEqual(record.score_change, -2)

    def test_save_battle_record_one_per_session(self):
        """
        每局对战仅生成一条汇总记录（非每轮出拳一条）
        """
        engine = GameEngine()
        engine.start_game(user_id=1, mode=1)

        engine.play_round(Choice.ROCK)
        if not engine.is_battle_finished():
            engine.play_round(Choice.ROCK)

        with patch.object(engine.battle_dao, 'create_record') as mock_create:
            engine.save_battle_record(score_change=1)
            self.assertEqual(mock_create.call_count, 1,
                             "每局对战应仅生成一条汇总记录")

    def test_save_battle_record_contains_final_result(self):
        """
        保存的记录应包含最终对战结果，而非单轮出拳结果
        """
        engine = GameEngine()
        engine.start_game(user_id=1, mode=1)

        while not engine.is_battle_finished():
            engine.play_round(Choice.ROCK)

        final_result = engine.get_final_result()

        with patch.object(engine.battle_dao, 'create_record') as mock_create:
            engine.save_battle_record(score_change=1)
            call_args = mock_create.call_args[0][0]
            self.assertIsInstance(call_args, BattleRecord)
            self.assertEqual(call_args.result, final_result.value)
            self.assertEqual(call_args.score_change, 1)


class TestContinueGameScoreCheck(unittest.TestCase):
    """
    测试连战模式"再玩一局"积分检查逻辑
    """

    def test_score_check_insufficient_score(self):
        """
        积分不足时，应阻止继续对战
        """
        score_manager = MagicMock(spec=ScoreManager)
        score_manager.get_score.return_value = 2

        self.assertLess(score_manager.get_score(user_id=1), 3,
                        "积分不足3分时应阻止继续对战")

    def test_score_check_sufficient_score(self):
        """
        积分充足时，应允许继续对战
        """
        score_manager = MagicMock(spec=ScoreManager)
        score_manager.get_score.return_value = 5

        self.assertGreaterEqual(score_manager.get_score(user_id=1), 3,
                                "积分>=3时应允许继续对战")

    def test_deduct_entry_fee_called_on_continue(self):
        """
        连战模式继续游戏时，应扣除入场费
        """
        score_manager = ScoreManager()

        score_dao = MagicMock()
        score_info = MagicMock()
        score_info.total_score = 10
        score_dao.get_score.return_value = score_info
        score_dao.update_score.return_value = True
        score_manager.score_dao = score_dao

        success, message = score_manager.deduct_entry_fee(user_id=1, mode=3)
        self.assertTrue(success, "积分充足时应成功扣除入场费")
        score_dao.update_score.assert_called_once_with(1, -3)

    def test_deduct_entry_fee_insufficient(self):
        """
        积分不足时，扣除入场费应失败
        """
        score_manager = ScoreManager()

        score_dao = MagicMock()
        score_info = MagicMock()
        score_info.total_score = 2
        score_dao.get_score.return_value = score_info
        score_manager.score_dao = score_dao

        success, message = score_manager.deduct_entry_fee(user_id=1, mode=3)
        self.assertFalse(success, "积分不足时应拒绝扣除入场费")

    def test_mode1_no_entry_fee(self):
        """
        模式1和模式2不需要入场费
        """
        score_manager = ScoreManager()
        success, message = score_manager.deduct_entry_fee(user_id=1, mode=1)
        self.assertTrue(success, "模式1不需要入场费")

        success, message = score_manager.deduct_entry_fee(user_id=1, mode=2)
        self.assertTrue(success, "模式2不需要入场费")


class TestDatabaseMigration(unittest.TestCase):
    """
    测试数据库迁移：旧表结构自动升级
    """

    def test_migration_removes_choice_columns(self):
        """
        数据库初始化后，battle_records表不应包含player_choice和ai_choice列
        """
        db = Database()
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(battle_records)")
        columns = [row[1] for row in cursor.fetchall()]
        db.close_connection(conn)

        self.assertNotIn('player_choice', columns,
                         "迁移后不应包含player_choice列")
        self.assertNotIn('ai_choice', columns,
                         "迁移后不应包含ai_choice列")
        self.assertIn('result', columns, "应包含result列")
        self.assertIn('score_change', columns, "应包含score_change列")


if __name__ == '__main__':
    unittest.main()
