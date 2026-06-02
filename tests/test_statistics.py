# tests/test_statistics.py
"""
统计分析模块单元测试
测试胜率计算、历史记录查询等功能
战绩记录粒度为每轮对战结算后的汇总信息
"""

import unittest
from src.business.statistics import Statistics
from src.data.models import BattleRecord, Score
from src.data.database import Database


class TestStatistics(unittest.TestCase):
    """
    统计分析类测试类
    """

    @classmethod
    def setUpClass(cls):
        """
        测试类初始化
        """
        cls.statistics = Statistics()
        cls.test_user_id = 777

    def setUp(self):
        """
        每个测试方法前执行 - 清理测试数据
        """
        db = Database()
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM battle_records WHERE user_id = ?", (self.test_user_id,))
        cursor.execute("DELETE FROM scores WHERE user_id = ?", (self.test_user_id,))
        conn.commit()
        db.close_connection(conn)

    def test_get_win_rate_with_battles(self):
        """
        测试计算胜率 - 有对战记录时正确计算
        """
        self.statistics.score_dao.create_score(self.test_user_id)

        for i in range(5):
            self.statistics.score_dao.update_statistics(self.test_user_id, win=True)
        for i in range(3):
            self.statistics.score_dao.update_statistics(self.test_user_id, lose=True)
        for i in range(2):
            self.statistics.score_dao.update_statistics(self.test_user_id, draw=True)

        win_rate = self.statistics.get_win_rate(self.test_user_id)
        self.assertIsInstance(win_rate, float)
        self.assertGreaterEqual(win_rate, 0)
        self.assertLessEqual(win_rate, 100)

    def test_get_win_rate_no_battles(self):
        """
        测试计算胜率 - 无对战记录时返回0
        """
        win_rate = self.statistics.get_win_rate(self.test_user_id)
        self.assertEqual(win_rate, 0.0)

    def test_get_battle_history(self):
        """
        测试获取历史记录 - 返回按时间降序的汇总记录列表
        """
        for i in range(5):
            record = BattleRecord(
                user_id=self.test_user_id,
                mode=1,
                result='胜利',
                score_change=1
            )
            self.statistics.battle_dao.create_record(record)

        history = self.statistics.get_battle_history(self.test_user_id)
        self.assertEqual(len(history), 5)

        for i in range(len(history) - 1):
            self.assertGreaterEqual(
                history[i].created_at,
                history[i + 1].created_at,
                "记录应按时间降序排列"
            )

    def test_get_statistics_summary(self):
        """
        测试获取统计摘要 - 返回完整的统计信息字典
        """
        self.statistics.score_dao.create_score(self.test_user_id)
        self.statistics.score_dao.update_score(self.test_user_id, 50)
        self.statistics.score_dao.update_statistics(self.test_user_id, win=True)
        self.statistics.score_dao.update_statistics(self.test_user_id, win=True)
        self.statistics.score_dao.update_statistics(self.test_user_id, lose=True)
        self.statistics.score_dao.update_statistics(self.test_user_id, draw=True)

        for i in range(3):
            record = BattleRecord(
                user_id=self.test_user_id,
                mode=1,
                result='胜利',
                score_change=1
            )
            self.statistics.battle_dao.create_record(record)

        summary = self.statistics.get_statistics_summary(self.test_user_id)

        self.assertIn('total_score', summary)
        self.assertIn('win_count', summary)
        self.assertIn('lose_count', summary)
        self.assertIn('draw_count', summary)
        self.assertIn('battle_count', summary)
        self.assertIn('win_rate', summary)
        self.assertIn('recent_battles', summary)

        self.assertEqual(summary['total_score'], 50)
        self.assertEqual(summary['win_count'], 2)
        self.assertEqual(summary['lose_count'], 1)
        self.assertEqual(summary['draw_count'], 1)


if __name__ == '__main__':
    unittest.main()
