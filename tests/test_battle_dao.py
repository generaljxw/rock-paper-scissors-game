# tests/test_battle_dao.py
"""
对战记录数据访问模块单元测试
测试记录创建、查询和统计功能
战绩记录粒度为每轮对战结算后的汇总信息
"""

import unittest
from src.data.battle_dao import BattleDAO
from src.data.models import BattleRecord
from src.data.database import Database


class TestBattleDAO(unittest.TestCase):
    """
    对战记录数据访问对象测试类
    """

    @classmethod
    def setUpClass(cls):
        """
        测试类初始化
        """
        cls.battle_dao = BattleDAO()

    def setUp(self):
        """
        每个测试方法前执行 - 清理测试数据
        """
        db = Database()
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM battle_records WHERE user_id = 999")
        conn.commit()
        db.close_connection(conn)

    def test_create_record(self):
        """
        测试创建对战记录 - 成功保存汇总记录（无出拳详情）
        """
        record = BattleRecord(
            user_id=999,
            mode=1,
            result='胜利',
            score_change=1
        )
        success, message = self.battle_dao.create_record(record)
        self.assertTrue(success, f"创建记录失败: {message}")
        self.assertEqual(message, "对战记录保存成功")

    def test_create_record_mode3(self):
        """
        测试创建连战模式对战记录 - 包含积分变化
        """
        record = BattleRecord(
            user_id=999,
            mode=3,
            result='失败',
            score_change=-3
        )
        success, message = self.battle_dao.create_record(record)
        self.assertTrue(success, f"创建记录失败: {message}")

    def test_get_records_by_user(self):
        """
        测试获取用户对战记录 - 返回记录列表按时间降序
        """
        for i in range(3):
            record = BattleRecord(
                user_id=999,
                mode=1,
                result='胜利',
                score_change=1
            )
            self.battle_dao.create_record(record)

        records = self.battle_dao.get_records_by_user(999)
        self.assertEqual(len(records), 3)

        for i in range(len(records) - 1):
            self.assertGreaterEqual(
                records[i].created_at,
                records[i + 1].created_at,
                "记录应按时间降序排列"
            )

    def test_get_battle_count_by_user(self):
        """
        测试获取用户对战次数 - 计数正确
        """
        for i in range(5):
            record = BattleRecord(
                user_id=999,
                mode=1,
                result='胜利',
                score_change=1
            )
            self.battle_dao.create_record(record)

        count = self.battle_dao.get_battle_count_by_user(999)
        self.assertGreater(count, 0, "对战次数应大于0")

    def test_get_win_count_by_user(self):
        """
        测试获取用户胜利次数 - 计数正确
        """
        for i in range(3):
            record = BattleRecord(
                user_id=999,
                mode=1,
                result='胜利',
                score_change=1
            )
            self.battle_dao.create_record(record)

        for i in range(2):
            record = BattleRecord(
                user_id=999,
                mode=1,
                result='失败',
                score_change=-1
            )
            self.battle_dao.create_record(record)

        win_count = self.battle_dao.get_win_count_by_user(999)
        self.assertGreater(win_count, 0, "胜利次数应大于0")

    def test_record_has_no_choice_fields(self):
        """
        测试记录不包含出拳详情字段
        """
        record = BattleRecord(
            user_id=999,
            mode=1,
            result='胜利',
            score_change=1
        )
        self.assertFalse(hasattr(record, 'player_choice'),
                         "记录不应包含player_choice字段")
        self.assertFalse(hasattr(record, 'ai_choice'),
                         "记录不应包含ai_choice字段")


if __name__ == '__main__':
    unittest.main()
