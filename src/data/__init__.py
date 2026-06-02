# src/data/__init__.py
"""
数据层模块

本包包含数据持久化和访问模块：
- models: 数据模型定义
- database: 数据库管理
- user_dao: 用户数据访问
- battle_dao: 对战记录访问
- score_dao: 积分数据访问
"""

from .models import User, BattleRecord, Score
from .database import Database
from .user_dao import UserDAO
from .battle_dao import BattleDAO
from .score_dao import ScoreDAO

__all__ = [
    'User',
    'BattleRecord',
    'Score',
    'Database',
    'UserDAO',
    'BattleDAO',
    'ScoreDAO'
]
