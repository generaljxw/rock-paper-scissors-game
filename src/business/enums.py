# src/business/enums.py
"""
业务逻辑层枚举类型定义模块

本模块定义了游戏核心业务中使用的所有枚举类型，
包括玩家选择、对战结果和对战模式等。
"""

from enum import Enum


class Choice(Enum):
    """
    玩家选择枚举
    定义猜拳游戏中的三种出拳选择
    """
    ROCK = "石头"
    SCISSORS = "剪刀"
    PAPER = "布"


class Result(Enum):
    """
    对战结果枚举
    定义猜拳对战的三种可能结果
    """
    WIN = "胜利"
    LOSE = "失败"
    DRAW = "平局"


class BattleMode(Enum):
    """
    对战模式枚举
    定义三种不同的对战模式
    """
    MODE_1 = 1  # 一局定胜负：打平继续出拳，分胜负后结算
    MODE_2 = 2  # 三局两胜：每局必须分出胜负（平局则继续出拳），先获2胜者获胜
    MODE_3 = 3  # 连战模式：胜利/平局可继续，失败则结算
