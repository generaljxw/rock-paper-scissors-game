# src/data/user_dao.py
"""
数据层用户数据访问模块

本模块负责用户数据的数据库操作，
包括用户创建、验证和查询等功能。
"""

import hashlib
from typing import Optional, Tuple
from .database import Database
from .models import User
import sqlite3


class UserDAO:
    """
    用户数据访问对象
    提供用户相关的数据库操作方法
    """

    def __init__(self):
        self.db = Database()

    def create_user(self, username: str, hashed_password: str, salt: str) -> Tuple[bool, str]:
        """
        创建新用户
        参数:
            username: 用户名
            hashed_password: 哈希加密后的密码
            salt: 密码盐值
        返回:
            (是否成功, 消息)
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO users (username, password, salt) VALUES (?, ?, ?)",
                (username, hashed_password, salt)
            )
            conn.commit()
            return True, "用户注册成功"
        except sqlite3.IntegrityError:
            return False, "用户名已存在"
        except Exception as e:
            return False, f"注册失败: {str(e)}"
        finally:
            self.db.close_connection(conn)

    def verify_user(self, username: str, password: str) -> Optional[User]:
        """
        验证用户登录
        参数:
            username: 用户名
            password: 原始密码
        返回:
            用户对象或None
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT id, username, password, salt, created_at FROM users WHERE username = ?",
                (username,)
            )
            row = cursor.fetchone()

            if row:
                stored_password = row['password']
                salt = row['salt']
                
                # 使用存储的盐值重新计算哈希
                hashed_password = hashlib.pbkdf2_hmac(
                    'sha256',
                    password.encode('utf-8'),
                    bytes.fromhex(salt),
                    100000
                ).hex()
                
                if hashed_password == stored_password:
                    return User(
                        id=row['id'],
                        username=row['username'],
                        created_at=row['created_at']
                    )
            return None
        finally:
            self.db.close_connection(conn)

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        根据ID获取用户信息
        参数:
            user_id: 用户ID
        返回:
            用户对象或None
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT id, username, password, created_at FROM users WHERE id = ?",
                (user_id,)
            )
            row = cursor.fetchone()

            if row:
                return User(
                    id=row['id'],
                    username=row['username'],
                    created_at=row['created_at']
                )
            return None
        finally:
            self.db.close_connection(conn)

    def username_exists(self, username: str) -> bool:
        """
        检查用户名是否存在
        参数:
            username: 用户名
        返回:
            是否存在
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT 1 FROM users WHERE username = ?", (username,))
            return cursor.fetchone() is not None
        finally:
            self.db.close_connection(conn)
