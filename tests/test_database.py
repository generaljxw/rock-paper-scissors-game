# tests/test_database.py
"""
数据库管理模块单元测试
测试数据库连接、单例模式和表初始化
"""

import unittest
import sqlite3
from src.data.database import Database


class TestDatabase(unittest.TestCase):
    """
    数据库模块测试类
    """

    def test_singleton_pattern(self):
        """
        测试单例模式 - 多次创建实例应为同一对象
        """
        db1 = Database()
        db2 = Database()
        self.assertIs(db1, db2, "Database实例应为单例")

    def test_get_connection(self):
        """
        测试获取数据库连接 - 返回有效的sqlite3.Connection对象
        """
        db = Database()
        conn = db.get_connection()
        self.assertIsInstance(conn, sqlite3.Connection, "应返回sqlite3.Connection对象")
        db.close_connection(conn)

    def test_close_connection(self):
        """
        测试关闭数据库连接 - 无异常抛出
        """
        db = Database()
        conn = db.get_connection()
        try:
            db.close_connection(conn)
        except Exception as e:
            self.fail(f"关闭连接时抛出异常: {e}")

    def test_table_initialization(self):
        """
        测试表初始化 - 自动创建users, battle_records, scores表
        """
        db = Database()
        conn = db.get_connection()
        cursor = conn.cursor()

        try:
            # 检查users表
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
            self.assertIsNotNone(cursor.fetchone(), "users表应存在")

            # 检查battle_records表
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='battle_records'")
            self.assertIsNotNone(cursor.fetchone(), "battle_records表应存在")

            # 检查scores表
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='scores'")
            self.assertIsNotNone(cursor.fetchone(), "scores表应存在")
        finally:
            db.close_connection(conn)


if __name__ == '__main__':
    unittest.main()
