# src/business/statistics.py
"""
业务逻辑层统计分析模块

本模块负责游戏数据的统计分析，
包括胜率计算、历史记录查询等功能。
"""

from typing import List, Dict
from ..data.battle_dao import BattleDAO
from ..data.score_dao import ScoreDAO
from ..data.models import BattleRecord, Score


class Statistics:
    """
    统计分析类
    提供游戏相关的统计查询功能
    """

    def __init__(self):
        self.battle_dao = BattleDAO()
        self.score_dao = ScoreDAO()

    def get_win_rate(self, user_id: int) -> float:
        """
        计算用户胜率
        参数:
            user_id: 用户ID
        返回:
            胜率百分比 (0-100)
        """
        score = self.score_dao.get_score(user_id)
        
        if not score or score.battle_count == 0:
            return 0.0
        
        return round(score.win_count / score.battle_count * 100, 2)

    def get_battle_history(self, user_id: int, limit: int = 50) -> List[BattleRecord]:
        """
        获取用户对战历史记录
        参数:
            user_id: 用户ID
            limit: 返回记录数量
        返回:
            对战记录列表
        """
        return self.battle_dao.get_records_by_user(user_id, limit)

    def get_statistics_summary(self, user_id: int) -> Dict:
        """
        获取用户统计摘要
        参数:
            user_id: 用户ID
        返回:
            统计摘要字典
        """
        score = self.score_dao.get_score(user_id)
        win_rate = self.get_win_rate(user_id)
        recent_battles = self.get_battle_history(user_id, 10)

        return {
            "total_score": score.total_score if score else 0,
            "win_count": score.win_count if score else 0,
            "lose_count": score.lose_count if score else 0,
            "draw_count": score.draw_count if score else 0,
            "battle_count": score.battle_count if score else 0,
            "win_rate": win_rate,
            "recent_battles": recent_battles
        }


