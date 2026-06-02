# tests/test_enums.py
"""
枚举类型模块单元测试
测试Choice, Result, BattleMode枚举
"""

import unittest
from src.business.enums import Choice, Result, BattleMode


class TestEnums(unittest.TestCase):
    """
    枚举类型测试类
    """

    def test_choice_enum_values(self):
        """
        测试Choice枚举值 - ROCK/SCISSORS/PAPER值正确
        """
        self.assertEqual(Choice.ROCK.value, '石头')
        self.assertEqual(Choice.SCISSORS.value, '剪刀')
        self.assertEqual(Choice.PAPER.value, '布')

    def test_result_enum_values(self):
        """
        测试Result枚举值 - WIN/LOSE/DRAW值正确
        """
        self.assertEqual(Result.WIN.value, '胜利')
        self.assertEqual(Result.LOSE.value, '失败')
        self.assertEqual(Result.DRAW.value, '平局')

    def test_battle_mode_enum_values(self):
        """
        测试BattleMode枚举值 - MODE_1/2/3值正确
        """
        self.assertEqual(BattleMode.MODE_1.value, 1)
        self.assertEqual(BattleMode.MODE_2.value, 2)
        self.assertEqual(BattleMode.MODE_3.value, 3)

    def test_choice_enum_members(self):
        """
        测试Choice枚举成员数量 - 应有3个成员
        """
        members = list(Choice)
        self.assertEqual(len(members), 3)

    def test_result_enum_members(self):
        """
        测试Result枚举成员数量 - 应有3个成员
        """
        members = list(Result)
        self.assertEqual(len(members), 3)

    def test_battle_mode_enum_members(self):
        """
        测试BattleMode枚举成员数量 - 应有3个成员
        """
        members = list(BattleMode)
        self.assertEqual(len(members), 3)


if __name__ == '__main__':
    unittest.main()
