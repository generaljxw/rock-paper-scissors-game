# src/business/score_manager.py
"""
业务逻辑层积分管理模块

本模块负责游戏积分的计算和管理，
根据不同对战模式应用不同的积分规则。
"""

from typing import Tuple
from ..data.score_dao import ScoreDAO
from ..data.models import Score


class ScoreManager:
    """
    积分管理类
    处理积分的计算、更新和查询
    """

    MODE_SCORE_RULES = {
        1: {"win": 1, "lose": -1, "entry_fee": 0},
        2: {"win": 2, "lose": -2, "entry_fee": 0},
        3: {"win": 1, "lose": 0, "entry_fee": 3, "consecutive_win_bonus": 5, "consecutive_win_threshold": 3, "round_bonus": 5}
    }

    def __init__(self):
        self.score_dao = ScoreDAO()

    def deduct_entry_fee(self, user_id: int, mode: int) -> Tuple[bool, str]:
        """
        扣除模式3的入场费
        参数:
            user_id: 用户ID
            mode: 对战模式
        返回:
            (是否成功, 消息)
        """
        entry_fee = self.MODE_SCORE_RULES.get(mode, {}).get("entry_fee", 0)

        if entry_fee > 0:
            score = self.score_dao.get_score(user_id)
            if score and score.total_score < entry_fee:
                return False, f"积分不足，需要{entry_fee}积分进入"
            self.score_dao.update_score(user_id, -entry_fee)

        return True, "入场费扣除成功"

    def calculate_score_change(self, mode: int, result: str, round_count: int = 0, consecutive_wins: int = 0) -> int:
        """
        根据对战结果计算积分变化
        参数:
            mode: 对战模式
            result: 对战结果
            round_count: 回合数（模式3使用，当前累计出拳次数）
            consecutive_wins: 连续胜利次数（模式3使用，超过阈值时获得奖励）
        返回:
            积分变化值
        """
        rules = self.MODE_SCORE_RULES.get(mode, {})

        if mode == 3:
            score_change = 0
            threshold = rules.get("consecutive_win_threshold", 3)
            
            # 连续胜利奖励：达到3次连续胜利奖励+5分
            if consecutive_wins >= threshold:
                score_change += rules.get("consecutive_win_bonus", 5)
            
            # 累计出拳奖励：每累计5次出拳额外+1分（在第5、10、15...次时触发）
            if round_count > 0 and round_count % rules.get("round_bonus", 5) == 0:
                score_change += 1
            
            return score_change

        if result == "胜利":
            return rules.get("win", 0)
        elif result == "失败":
            return rules.get("lose", 0)

        return 0

    def update_score(self, user_id: int, score_change: int) -> Tuple[bool, str]:
        """
        更新用户积分
        参数:
            user_id: 用户ID
            score_change: 积分变化值
        返回:
            (是否成功, 消息)
        """
        return self.score_dao.update_score(user_id, score_change)

    def update_battle_result(self, user_id: int, result: str, score_change: int) -> Tuple[bool, str]:
        """
        更新对战结果（积分+胜率统计）
        参数:
            user_id: 用户ID
            result: 对战最终结果（"胜利"/"失败"/"平局"）
            score_change: 积分变化值
        返回:
            (是否成功, 消息)
        """
        if score_change != 0:
            score_result = self.score_dao.update_score(user_id, score_change)
            if not score_result[0]:
                return score_result

        if result == "胜利":
            return self.score_dao.update_statistics(user_id, win=True)
        elif result == "失败":
            return self.score_dao.update_statistics(user_id, lose=True)
        elif result == "平局":
            return self.score_dao.update_statistics(user_id, draw=True)

        return True, "无需更新统计"

    def get_score(self, user_id: int) -> int:
        """
        获取用户当前积分
        参数:
            user_id: 用户ID
        返回:
            当前积分
        """
        score = self.score_dao.get_score(user_id)
        return score.total_score if score else 0

    def get_score_info(self, user_id: int) -> Score:
        """
        获取用户完整的积分信息
        参数:
            user_id: 用户ID
        返回:
            积分对象
        """
        score = self.score_dao.get_score(user_id)
        return score if score else Score(user_id=user_id)
