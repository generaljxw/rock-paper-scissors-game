# tests/test_user_dao.py
"""
用户数据访问模块单元测试
测试用户创建、验证、查询等功能
"""

import unittest
import hashlib
import os
from src.data.user_dao import UserDAO
from src.data.database import Database


class TestUserDAO(unittest.TestCase):
    """
    用户数据访问对象测试类
    """

    @classmethod
    def setUpClass(cls):
        """
        测试类初始化 - 创建测试用户
        """
        cls.user_dao = UserDAO()
        cls.test_username = 'test_user_dao'
        cls.test_raw_password = 'password123'
        cls.test_salt = os.urandom(16).hex()
        cls.test_hashed_password = hashlib.pbkdf2_hmac(
            'sha256',
            cls.test_raw_password.encode('utf-8'),
            bytes.fromhex(cls.test_salt),
            100000
        ).hex()

    def setUp(self):
        """
        每个测试方法前执行 - 清理测试数据
        """
        db = Database()
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE username LIKE 'test_%'")
        conn.commit()
        db.close_connection(conn)

    def test_create_user_success(self):
        """
        测试创建用户 - 成功创建新用户
        """
        success, message = self.user_dao.create_user(
            self.test_username, 
            self.test_hashed_password, 
            self.test_salt
        )
        self.assertTrue(success, f"创建用户失败: {message}")
        self.assertEqual(message, "用户注册成功")

    def test_create_user_duplicate(self):
        """
        测试创建重复用户 - 正确拒绝重复用户名
        """
        # 先创建一次
        self.user_dao.create_user(
            self.test_username, 
            self.test_hashed_password, 
            self.test_salt
        )
        # 再次创建相同用户名
        another_salt = os.urandom(16).hex()
        success, message = self.user_dao.create_user(
            self.test_username, 
            'different_hash', 
            another_salt
        )
        self.assertFalse(success, "重复用户名应被拒绝")
        self.assertEqual(message, "用户名已存在")

    def test_verify_user_success(self):
        """
        测试验证用户 - 用户名密码正确时返回User对象
        """
        self.user_dao.create_user(
            self.test_username, 
            self.test_hashed_password, 
            self.test_salt
        )
        # 验证时传入原始密码
        user = self.user_dao.verify_user(self.test_username, self.test_raw_password)
        self.assertIsNotNone(user, "验证成功应返回User对象")
        self.assertEqual(user.username, self.test_username)

    def test_verify_user_failure(self):
        """
        测试验证用户 - 密码错误时返回None
        """
        self.user_dao.create_user(
            self.test_username, 
            self.test_hashed_password, 
            self.test_salt
        )
        # 验证时传入错误的原始密码
        user = self.user_dao.verify_user(self.test_username, 'wrongpassword')
        self.assertIsNone(user, "密码错误应返回None")

    def test_get_user_by_id(self):
        """
        测试按ID查询用户 - 返回正确的用户对象
        """
        self.user_dao.create_user(
            self.test_username, 
            self.test_hashed_password, 
            self.test_salt
        )
        user = self.user_dao.verify_user(self.test_username, self.test_raw_password)
        self.assertIsNotNone(user)
        
        retrieved_user = self.user_dao.get_user_by_id(user.id)
        self.assertIsNotNone(retrieved_user)
        self.assertEqual(retrieved_user.id, user.id)
        self.assertEqual(retrieved_user.username, self.test_username)

    def test_username_exists(self):
        """
        测试用户名存在检查 - 正确识别已存在的用户名
        """
        self.user_dao.create_user(
            self.test_username, 
            self.test_hashed_password, 
            self.test_salt
        )
        exists = self.user_dao.username_exists(self.test_username)
        self.assertTrue(exists, "应识别已存在的用户名")

        not_exists = self.user_dao.username_exists('nonexistent_user')
        self.assertFalse(not_exists, "应识别不存在的用户名")


if __name__ == '__main__':
    unittest.main()
