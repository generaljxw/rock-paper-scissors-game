# src/business/game_engine.py
"""
业务逻辑层游戏引擎模块

本模块是游戏核心业务逻辑的处理中心，
负责游戏流程控制、胜负判定和AI逻辑等核心功能。
"""

import random
from typing import Optional, Dict, List
from ..data.battle_dao import BattleDAO
from ..data.models import BattleRecord
from .enums import Choice, Result, BattleMode


class GameEngine:
    """
    游戏引擎类
    管理游戏会话、处理玩家选择和判定胜负
    """

    WIN_MAP = {
        Choice.ROCK: Choice.SCISSORS,
        Choice.SCISSORS: Choice.PAPER,
        Choice.PAPER: Choice.ROCK
    }

    def __init__(self):
        self.battle_dao = BattleDAO()
        self.current_session: Optional[Dict] = None

    def start_game(self, user_id: int, mode: int) -> Dict:
        """
        开始新游戏会话
        参数:
            user_id: 用户ID
            mode: 对战模式
        返回:
            游戏会话信息字典
        """
        self.current_session = {
            "user_id": user_id,
            "mode": mode,
            "rounds": [],
            "win_count": 0,
            "lose_count": 0,
            "draw_count": 0,
            "total_rounds": 0,
            "effective_rounds": 0,
            "consecutive_wins": 0,
            "current_round_winner": None
        }
        return self.current_session

    def make_choice(self, user_choice: Choice) -> Dict:
        """
        处理玩家出拳选择
        参数:
            user_choice: 玩家选择
        返回:
            本轮对战结果字典
        """
        return self.play_round(user_choice)

    def play_round(self, user_choice: Choice) -> Dict:
        """
        进行一轮游戏
        参数:
            user_choice: 玩家选择
        返回:
            本轮对战结果字典
        """
        ai_choice = self._get_ai_choice()
        result = self.determine_winner(user_choice, ai_choice)

        if self.current_session:
            self.current_session["total_rounds"] += 1

            round_result = {
                "player_choice": user_choice,
                "ai_choice": ai_choice,
                "result": result,
                "player_value": user_choice.value,
                "ai_value": ai_choice.value,
                "result_value": result.value
            }

            self.current_session["rounds"].append(round_result)

            if result == Result.WIN:
                self.current_session["win_count"] += 1
                self.current_session["effective_rounds"] += 1
                self.current_session["current_round_winner"] = "player"
                self.current_session["consecutive_wins"] += 1
            elif result == Result.LOSE:
                self.current_session["lose_count"] += 1
                self.current_session["effective_rounds"] += 1
                self.current_session["current_round_winner"] = "ai"
                self.current_session["consecutive_wins"] = 0
            else:
                self.current_session["draw_count"] += 1
                self.current_session["current_round_winner"] = None

            return round_result

        return {}

    def _get_ai_choice(self) -> Choice:
        """
        获取AI的出拳选择
        当前实现为完全随机选择
        返回:
            AI的选择
        """
        return random.choice(list(Choice))

    def determine_winner(self, player_choice: Choice, ai_choice: Choice) -> Result:
        """
        判定本轮胜负
        规则: 石头 > 剪刀 > 布 > 石头
        参数:
            player_choice: 玩家选择
            ai_choice: AI选择
        返回:
            对战结果
        """
        if player_choice == ai_choice:
            return Result.DRAW

        if self.WIN_MAP[player_choice] == ai_choice:
            return Result.WIN

        return Result.LOSE

    def is_battle_finished(self) -> bool:
        """
        判断当前对战是否结束
        根据不同模式的规则判定
        模式2规则：每局必须分出胜负（平局则继续），先获2胜者获胜，最多3局
        返回:
            是否结束
        """
        if not self.current_session:
            return True

        mode = self.current_session["mode"]
        win_count = self.current_session["win_count"]
        lose_count = self.current_session["lose_count"]
        effective_rounds = self.current_session["effective_rounds"]

        if mode == BattleMode.MODE_1.value:
            return win_count >= 1 or lose_count >= 1
        elif mode == BattleMode.MODE_2.value:
            return win_count >= 2 or lose_count >= 2 or effective_rounds >= 3
        elif mode == BattleMode.MODE_3.value:
            return lose_count >= 1

        return False

    def get_final_result(self) -> Result:
        """
        获取最终对战结果
        返回:
            最终胜负平结果
        """
        if not self.current_session:
            return Result.DRAW

        win_count = self.current_session["win_count"]
        lose_count = self.current_session["lose_count"]

        if win_count > lose_count:
            return Result.WIN
        elif lose_count > win_count:
            return Result.LOSE
        return Result.DRAW

    def get_session_summary(self) -> Dict:
        """
        获取当前会话的摘要信息
        返回:
            会话摘要字典
        """
        if not self.current_session:
            return {}

        return {
            "mode": self.current_session["mode"],
            "total_rounds": self.current_session["total_rounds"],
            "effective_rounds": self.current_session["effective_rounds"],
            "win_count": self.current_session["win_count"],
            "lose_count": self.current_session["lose_count"],
            "draw_count": self.current_session["draw_count"],
            "consecutive_wins": self.current_session["consecutive_wins"],
            "final_result": self.get_final_result().value
        }

    def get_consecutive_wins(self) -> int:
        """
        获取当前连续胜利次数（仅统计真正的连续出拳，不包含平局）
        用于模式3的积分计算
        返回:
            连续胜利次数
        """
        if not self.current_session:
            return 0

        consecutive = 0
        for round_data in reversed(self.current_session["rounds"]):
            if round_data["result"] == Result.WIN:
                consecutive += 1
            elif round_data["result"] == Result.LOSE:
                break
        return consecutive

    def save_battle_record(self, score_change: int = 0) -> bool:
        """
        保存对战记录到数据库（每局对战一条汇总记录）
        参数:
            score_change: 积分变化值
        返回:
            是否保存成功
        """
        if not self.current_session:
            return False

        final_result = self.get_final_result()
        record = BattleRecord(
            user_id=self.current_session["user_id"],
            mode=self.current_session["mode"],
            result=final_result.value,
            score_change=score_change
        )
        self.battle_dao.create_record(record)

        return True

    def end_game(self) -> None:
        """
        结束当前游戏会话
        清除会话数据
        """
        self.current_session = None
