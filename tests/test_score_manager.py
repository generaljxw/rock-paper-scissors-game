# tests/test_score_manager.py
"""
积分管理模块单元测试
测试入场费扣除、积分计算等功能
"""

import unittest
from src.business.score_manager import ScoreManager
from src.data.database import Database


class TestScoreManager(unittest.TestCase):
    """
    积分管理类测试类
    """

    @classmethod
    def setUpClass(cls):
        """
        测试类初始化
        """
        cls.score_manager = ScoreManager()
        cls.test_user_id = 888

    def setUp(self):
        """
        每个测试方法前执行 - 清理测试数据并创建积分记录
        """
        db = Database()
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM scores WHERE user_id = ?", (self.test_user_id,))
        conn.commit()
        db.close_connection(conn)
        
        # 创建积分记录并设置初始积分
        self.score_manager.score_dao.create_score(self.test_user_id)
        self.score_manager.score_dao.update_score(self.test_user_id, 100)

    def test_deduct_entry_fee_mode3_success(self):
        """
        测试扣除入场费 - 模式3成功扣除3积分
        """
        success, message = self.score_manager.deduct_entry_fee(self.test_user_id, 3)
        self.assertTrue(success, f"扣除入场费失败: {message}")
        
        score = self.score_manager.score_dao.get_score(self.test_user_id)
        self.assertEqual(score.total_score, 97)

    def test_deduct_entry_fee_insufficient_score(self):
        """
        测试扣除入场费 - 积分不足时拒绝
        """
        # 将积分设置为2，低于入场费3
        self.score_manager.score_dao.update_score(self.test_user_id, -98)
        
        success, message = self.score_manager.deduct_entry_fee(self.test_user_id, 3)
        self.assertFalse(success, "积分不足应拒绝")
        self.assertIn("积分不足", message)

    def test_deduct_entry_fee_no_fee_modes(self):
        """
        测试扣除入场费 - 模式1和模式2不扣除入场费
        """
        # 模式1不应扣除入场费
        success, message = self.score_manager.deduct_entry_fee(self.test_user_id, 1)
        self.assertTrue(success)
        
        score = self.score_manager.score_dao.get_score(self.test_user_id)
        self.assertEqual(score.total_score, 100)
        
        # 模式2不应扣除入场费
        success, message = self.score_manager.deduct_entry_fee(self.test_user_id, 2)
        self.assertTrue(success)
        
        score = self.score_manager.score_dao.get_score(self.test_user_id)
        self.assertEqual(score.total_score, 100)

    def test_calculate_score_change_mode1(self):
        """
        测试积分计算 - 模式1规则
        """
        change = self.score_manager.calculate_score_change(1, "胜利")
        self.assertEqual(change, 1)
        
        change = self.score_manager.calculate_score_change(1, "失败")
        self.assertEqual(change, -1)
        
        change = self.score_manager.calculate_score_change(1, "平局")
        self.assertEqual(change, 0)

    def test_calculate_score_change_mode2(self):
        """
        测试积分计算 - 模式2规则
        """
        change = self.score_manager.calculate_score_change(2, "胜利")
        self.assertEqual(change, 2)
        
        change = self.score_manager.calculate_score_change(2, "失败")
        self.assertEqual(change, -2)
        
        change = self.score_manager.calculate_score_change(2, "平局")
        self.assertEqual(change, 0)

    def test_calculate_score_change_mode3(self):
        """
        测试积分计算 - 模式3规则
        新规则：连续胜利超过3次奖励+5分；每累计5次出拳额外+1分；其他情况不加分
        """
        change = self.score_manager.calculate_score_change(3, "胜利")
        self.assertEqual(change, 0)
        
        change = self.score_manager.calculate_score_change(3, "胜利", 0, 4)
        self.assertEqual(change, 5)
        
        change = self.score_manager.calculate_score_change(3, "失败")
        self.assertEqual(change, 0)
        
        change = self.score_manager.calculate_score_change(3, "平局")
        self.assertEqual(change, 0)

    def test_calculate_score_change_mode3_bonus(self):
        """
        测试积分计算 - 模式3额外积分奖励
        新规则：每累计5次出拳额外+1分
        """
        change = self.score_manager.calculate_score_change(3, "胜利", 5, 1)
        self.assertEqual(change, 1)
        
        change = self.score_manager.calculate_score_change(3, "平局", 5, 0)
        self.assertEqual(change, 1)
        
        change = self.score_manager.calculate_score_change(3, "失败", 5, 0)
        self.assertEqual(change, 1)

    def test_calculate_score_change_mode3_consecutive_wins(self):
        """
        测试积分计算 - 模式3连续胜利奖励
        新规则：连续胜利超过3次奖励+5分
        """
        change = self.score_manager.calculate_score_change(3, "胜利", 0, 4)
        self.assertEqual(change, 5)
        
        change = self.score_manager.calculate_score_change(3, "胜利", 0, 3)
        self.assertEqual(change, 0)
        
        change = self.score_manager.calculate_score_change(3, "胜利", 0, 5)
        self.assertEqual(change, 5)

    def test_calculate_score_change_mode3_round_bonus(self):
        """
        测试积分计算 - 模式3每5次出拳奖励
        新规则：每累计5次出拳额外+1分
        """
        change = self.score_manager.calculate_score_change(3, "平局", 10, 0)
        self.assertEqual(change, 1)
        
        change = self.score_manager.calculate_score_change(3, "胜利", 10, 1)
        self.assertEqual(change, 1)

    def test_calculate_score_change_mode3_combined_rewards(self):
        """
        测试积分计算 - 模式3连续胜利奖励和累计出拳奖励可叠加
        """
        # 连续胜利4次 + 累计出拳5次 = 5 + 1 = 6分
        change = self.score_manager.calculate_score_change(3, "胜利", 5, 4)
        self.assertEqual(change, 6)
        
        # 连续胜利5次 + 累计出拳10次 = 5 + 1 = 6分（第10次触发+1分）
        change = self.score_manager.calculate_score_change(3, "胜利", 10, 5)
        self.assertEqual(change, 6)

    def test_calculate_score_change_mode3_boundary_consecutive_wins(self):
        """
        测试积分计算 - 模式3连续胜利边界条件
        """
        # 连续胜利3次，不应触发奖励
        change = self.score_manager.calculate_score_change(3, "胜利", 0, 3)
        self.assertEqual(change, 0)
        
        # 连续胜利4次，应触发+5分
        change = self.score_manager.calculate_score_change(3, "胜利", 0, 4)
        self.assertEqual(change, 5)

    def test_calculate_score_change_mode3_round_bonus_only(self):
        """
        测试积分计算 - 模式3仅累计出拳奖励（无连续胜利）
        """
        # 累计出拳5次，连续胜利0次 = 1分
        change = self.score_manager.calculate_score_change(3, "平局", 5, 0)
        self.assertEqual(change, 1)
        
        # 累计出拳10次，连续胜利0次 = 1分（第10次触发）
        change = self.score_manager.calculate_score_change(3, "失败", 10, 0)
        self.assertEqual(change, 1)
        
        # 累计出拳15次，连续胜利0次 = 1分（第15次触发）
        change = self.score_manager.calculate_score_change(3, "失败", 15, 0)
        self.assertEqual(change, 1)


if __name__ == '__main__':
    unittest.main()
