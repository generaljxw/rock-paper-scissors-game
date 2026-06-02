# src/data/score_dao.py
"""
数据层积分数据访问模块

本模块负责积分数据的数据库操作，
包括积分查询、更新和统计等功能。
"""

from typing import Optional, Tuple
from .database import Database
from .models import Score
import sqlite3


class ScoreDAO:
    """
    积分数据访问对象
    提供积分相关的数据库操作方法
    """

    def __init__(self):
        self.db = Database()

    def get_score(self, user_id: int) -> Optional[Score]:
        """
        获取用户积分信息
        参数:
            user_id: 用户ID
        返回:
            积分对象或None
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """SELECT user_id, total_score, win_count, lose_count, draw_count, battle_count, updated_at
                   FROM scores
                   WHERE user_id = ?""",
                (user_id,)
            )
            row = cursor.fetchone()

            if row:
                return Score(
                    user_id=row['user_id'],
                    total_score=row['total_score'],
                    win_count=row['win_count'],
                    lose_count=row['lose_count'],
                    draw_count=row['draw_count'],
                    battle_count=row['battle_count'],
                    updated_at=row['updated_at']
                )
            return None
        finally:
            self.db.close_connection(conn)

    def create_score(self, user_id: int) -> Tuple[bool, str]:
        """
        为新用户创建积分记录
        参数:
            user_id: 用户ID
        返回:
            (是否成功, 消息)
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """INSERT INTO scores (user_id, total_score, win_count, lose_count, draw_count, battle_count)
                   VALUES (?, 0, 0, 0, 0, 0)""",
                (user_id,)
            )
            conn.commit()
            return True, "积分记录创建成功"
        except sqlite3.IntegrityError:
            return False, "积分记录已存在"
        except Exception as e:
            return False, f"创建积分记录失败: {str(e)}"
        finally:
            self.db.close_connection(conn)

    def update_score(self, user_id: int, score_change: int) -> Tuple[bool, str]:
        """
        更新用户积分
        参数:
            user_id: 用户ID
            score_change: 积分变化值
        返回:
            (是否成功, 消息)
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """UPDATE scores
                   SET total_score = total_score + ?,
                       updated_at = CURRENT_TIMESTAMP
                   WHERE user_id = ?""",
                (score_change, user_id)
            )
            conn.commit()
            return True, f"积分{'增加' if score_change > 0 else '减少'}{abs(score_change)}分"
        except Exception as e:
            return False, f"更新积分失败: {str(e)}"
        finally:
            self.db.close_connection(conn)

    def update_statistics(self, user_id: int, win: bool = False, lose: bool = False, draw: bool = False) -> Tuple[bool, str]:
        """
        更新用户对战胜负平统计
        参数:
            user_id: 用户ID
            win: 是否为胜利
            lose: 是否为失败
            draw: 是否为平局
        返回:
            (是否成功, 消息)
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()

        try:
            if win:
                cursor.execute(
                    "UPDATE scores SET win_count = win_count + 1, battle_count = battle_count + 1, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?",
                    (user_id,)
                )
            elif lose:
                cursor.execute(
                    "UPDATE scores SET lose_count = lose_count + 1, battle_count = battle_count + 1, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?",
                    (user_id,)
                )
            elif draw:
                cursor.execute(
                    "UPDATE scores SET draw_count = draw_count + 1, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?",
                    (user_id,)
                )
            conn.commit()
            return True, "统计数据更新成功"
        except Exception as e:
            return False, f"更新统计数据失败: {str(e)}"
        finally:
            self.db.close_connection(conn)
