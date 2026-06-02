# tests/test_score_dao.py
"""
积分数据访问模块单元测试
测试积分查询、更新和统计功能
"""

import unittest
from src.data.score_dao import ScoreDAO
from src.data.database import Database


class TestScoreDAO(unittest.TestCase):
    """
    积分数据访问对象测试类
    """

    @classmethod
    def setUpClass(cls):
        """
        测试类初始化
        """
        cls.score_dao = ScoreDAO()
        cls.test_user_id = 999

    def setUp(self):
        """
        每个测试方法前执行 - 清理测试数据
        """
        db = Database()
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM scores WHERE user_id = ?", (self.test_user_id,))
        conn.commit()
        db.close_connection(conn)

    def test_create_score(self):
        """
        测试创建积分记录 - 成功创建新用户积分
        """
        success, message = self.score_dao.create_score(self.test_user_id)
        self.assertTrue(success, f"创建积分记录失败: {message}")
        self.assertEqual(message, "积分记录创建成功")

    def test_create_score_duplicate(self):
        """
        测试创建重复积分记录 - 正确拒绝重复创建
        """
        self.score_dao.create_score(self.test_user_id)
        success, message = self.score_dao.create_score(self.test_user_id)
        self.assertFalse(success, "重复创建应被拒绝")
        self.assertEqual(message, "积分记录已存在")

    def test_get_score(self):
        """
        测试获取积分信息 - 返回正确的Score对象
        """
        self.score_dao.create_score(self.test_user_id)
        score = self.score_dao.get_score(self.test_user_id)
        self.assertIsNotNone(score, "应返回Score对象")
        self.assertEqual(score.user_id, self.test_user_id)
        self.assertEqual(score.total_score, 0)

    def test_update_score_increase(self):
        """
        测试更新积分 - 增加积分成功
        """
        self.score_dao.create_score(self.test_user_id)
        success, message = self.score_dao.update_score(self.test_user_id, 10)
        self.assertTrue(success, f"更新积分失败: {message}")
        self.assertIn("增加", message)
        
        score = self.score_dao.get_score(self.test_user_id)
        self.assertEqual(score.total_score, 10)

    def test_update_score_decrease(self):
        """
        测试更新积分 - 减少积分成功
        """
        self.score_dao.create_score(self.test_user_id)
        self.score_dao.update_score(self.test_user_id, 20)
        
        success, message = self.score_dao.update_score(self.test_user_id, -5)
        self.assertTrue(success, f"更新积分失败: {message}")
        self.assertIn("减少", message)
        
        score = self.score_dao.get_score(self.test_user_id)
        self.assertEqual(score.total_score, 15)

    def test_update_statistics_win(self):
        """
        测试更新统计 - 胜利次数+1
        """
        self.score_dao.create_score(self.test_user_id)
        success, message = self.score_dao.update_statistics(self.test_user_id, win=True)
        self.assertTrue(success, f"更新统计失败: {message}")
        
        score = self.score_dao.get_score(self.test_user_id)
        self.assertEqual(score.win_count, 1)
        self.assertEqual(score.battle_count, 1)

    def test_update_statistics_lose(self):
        """
        测试更新统计 - 失败次数+1
        """
        self.score_dao.create_score(self.test_user_id)
        success, message = self.score_dao.update_statistics(self.test_user_id, lose=True)
        self.assertTrue(success, f"更新统计失败: {message}")
        
        score = self.score_dao.get_score(self.test_user_id)
        self.assertEqual(score.lose_count, 1)
        self.assertEqual(score.battle_count, 1)

    def test_update_statistics_draw(self):
        """
        测试更新统计 - 平局次数+1
        """
        self.score_dao.create_score(self.test_user_id)
        success, message = self.score_dao.update_statistics(self.test_user_id, draw=True)
        self.assertTrue(success, f"更新统计失败: {message}")
        
        score = self.score_dao.get_score(self.test_user_id)
        self.assertEqual(score.draw_count, 1)


if __name__ == '__main__':
    unittest.main()
