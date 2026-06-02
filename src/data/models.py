# src/data/models.py
"""
数据层数据模型定义模块

本模块定义了游戏中使用的所有数据结构，
包括用户、对战记录和积分等数据模型。
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class User:
    """
    用户数据模型
    用于存储用户的基本信息
    """
    id: Optional[int] = None
    username: str = ""
    password: str = ""
    created_at: Optional[datetime] = None


@dataclass
class BattleRecord:
    """
    对战记录数据模型
    用于存储每轮对战结算后的汇总信息
    """
    id: Optional[int] = None
    user_id: int = 0
    mode: int = 1
    result: str = ""
    score_change: int = 0
    created_at: Optional[datetime] = None


@dataclass
class Score:
    """
    积分数据模型
    用于存储用户的积分和统计数据
    """
    user_id: int = 0
    total_score: int = 0
    win_count: int = 0
    lose_count: int = 0
    draw_count: int = 0
    battle_count: int = 0
    updated_at: Optional[datetime] = None
