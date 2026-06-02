# src/data/battle_dao.py
"""
数据层对战记录数据访问模块

本模块负责对战记录的数据库操作，
包括记录创建、查询和统计等功能。
战绩记录粒度为每轮对战结算后的汇总信息。
"""

from typing import List, Optional, Tuple
from .database import Database
from .models import BattleRecord
import sqlite3


class BattleDAO:
    """
    对战记录数据访问对象
    提供对战记录相关的数据库操作方法
    """

    def __init__(self):
        self.db = Database()

    def create_record(self, record: BattleRecord) -> Tuple[bool, str]:
        """
        创建对战记录（每轮对战汇总记录）
        参数:
            record: 对战记录对象
        返回:
            (是否成功, 消息)
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """INSERT INTO battle_records
                   (user_id, mode, result, score_change)
                   VALUES (?, ?, ?, ?)""",
                (record.user_id, record.mode,
                 record.result, record.score_change)
            )
            conn.commit()
            return True, "对战记录保存成功"
        except Exception as e:
            return False, f"保存对战记录失败: {str(e)}"
        finally:
            self.db.close_connection(conn)

    def get_records_by_user(self, user_id: int, limit: int = 50) -> List[BattleRecord]:
        """
        获取指定用户的历史对战记录
        参数:
            user_id: 用户ID
            limit: 返回记录数量限制
        返回:
            对战记录列表
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """SELECT id, user_id, mode, result, score_change, created_at
                   FROM battle_records
                   WHERE user_id = ?
                   ORDER BY created_at DESC
                   LIMIT ?""",
                (user_id, limit)
            )
            rows = cursor.fetchall()

            records = []
            for row in rows:
                records.append(BattleRecord(
                    id=row['id'],
                    user_id=row['user_id'],
                    mode=row['mode'],
                    result=row['result'],
                    score_change=row['score_change'],
                    created_at=row['created_at']
                ))
            return records
        finally:
            self.db.close_connection(conn)

    def get_battle_count_by_user(self, user_id: int) -> int:
        """
        获取指定用户的总对战次数
        参数:
            user_id: 用户ID
        返回:
            对战次数
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT COUNT(*) as battle_count FROM battle_records WHERE user_id = ?",
                (user_id,)
            )
            row = cursor.fetchone()
            return row['battle_count'] if row else 0
        finally:
            self.db.close_connection(conn)

    def get_win_count_by_user(self, user_id: int) -> int:
        """
        获取指定用户的胜利次数
        参数:
            user_id: 用户ID
        返回:
            胜利次数
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT COUNT(*) as win_count FROM battle_records WHERE user_id = ? AND result = '胜利'",
                (user_id,)
            )
            row = cursor.fetchone()
            return row['win_count'] if row else 0
        finally:
            self.db.close_connection(conn)
