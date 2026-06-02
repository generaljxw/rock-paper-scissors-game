# tests/test_models.py
"""
数据模型模块单元测试
测试User, BattleRecord, Score数据模型
"""

import unittest
from datetime import datetime
from src.data.models import User, BattleRecord, Score


class TestModels(unittest.TestCase):
    """
    数据模型测试类
    """

    def test_user_creation(self):
        """
        测试User模型创建 - 字段正确赋值
        """
        user = User(id=1, username='testuser')
        self.assertEqual(user.id, 1)
        self.assertEqual(user.username, 'testuser')

    def test_user_default_values(self):
        """
        测试User模型默认值 - 未提供字段应为默认值
        """
        user = User()
        self.assertIsNone(user.id)
        self.assertEqual(user.username, "")

    def test_battle_record_creation(self):
        """
        测试BattleRecord模型创建 - 字段正确赋值（汇总记录，无出拳详情）
        """
        record = BattleRecord(
            id=1,
            user_id=1,
            mode=1,
            result='胜利',
            score_change=1,
            created_at=datetime.now()
        )
        self.assertEqual(record.id, 1)
        self.assertEqual(record.user_id, 1)
        self.assertEqual(record.mode, 1)
        self.assertEqual(record.result, '胜利')
        self.assertEqual(record.score_change, 1)
        self.assertIsInstance(record.created_at, datetime)

    def test_battle_record_no_choice_fields(self):
        """
        测试BattleRecord模型 - 不应包含player_choice和ai_choice字段
        """
        record = BattleRecord(user_id=1, mode=3, result='失败', score_change=-3)
        self.assertFalse(hasattr(record, 'player_choice'),
                         "BattleRecord不应包含player_choice字段")
        self.assertFalse(hasattr(record, 'ai_choice'),
                         "BattleRecord不应包含ai_choice字段")

    def test_score_creation(self):
        """
        测试Score模型创建 - 数值字段默认为0
        """
        score = Score(user_id=1)
        self.assertEqual(score.user_id, 1)
        self.assertEqual(score.total_score, 0)
        self.assertEqual(score.win_count, 0)
        self.assertEqual(score.lose_count, 0)
        self.assertEqual(score.draw_count, 0)
        self.assertEqual(score.battle_count, 0)

    def test_score_with_values(self):
        """
        测试Score模型设置值 - 正确设置各字段
        """
        score = Score(
            user_id=1,
            total_score=100,
            win_count=10,
            lose_count=5,
            draw_count=3,
            battle_count=18
        )
        self.assertEqual(score.total_score, 100)
        self.assertEqual(score.win_count, 10)
        self.assertEqual(score.lose_count, 5)
        self.assertEqual(score.draw_count, 3)
        self.assertEqual(score.battle_count, 18)


if __name__ == '__main__':
    unittest.main()
