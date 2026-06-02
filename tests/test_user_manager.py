# tests/test_user_manager.py
"""
用户管理模块单元测试
测试用户注册、登录、登出等功能
"""

import unittest
from src.business.user_manager import UserManager
from src.data.database import Database


class TestUserManager(unittest.TestCase):
    """
    用户管理类测试类
    """

    @classmethod
    def setUpClass(cls):
        """
        测试类初始化
        """
        cls.user_manager = UserManager()

    def setUp(self):
        """
        每个测试方法前执行 - 清理测试数据
        """
        db = Database()
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE username LIKE 'test_%'")
        cursor.execute("DELETE FROM scores WHERE user_id IN (SELECT id FROM users WHERE username LIKE 'test_%')")
        conn.commit()
        db.close_connection(conn)
        self.user_manager.current_user = None

    def test_register_short_username(self):
        """
        测试注册短用户名 - 用户名长度少于3字符应被拒绝
        """
        success, message = self.user_manager.register('ab', 'password123')
        self.assertFalse(success, "短用户名应被拒绝")
        self.assertIn("3", message)

    def test_register_short_password(self):
        """
        测试注册短密码 - 密码长度少于6字符应被拒绝
        """
        success, message = self.user_manager.register('testuser', '123')
        self.assertFalse(success, "短密码应被拒绝")
        self.assertIn("6", message)

    def test_register_success(self):
        """
        测试注册成功 - 创建用户和积分记录
        """
        success, message = self.user_manager.register('testuser', 'password123')
        self.assertTrue(success, f"注册失败: {message}")
        self.assertEqual(message, "用户注册成功")

    def test_login_success(self):
        """
        测试登录成功 - 设置current_user
        """
        self.user_manager.register('testuser', 'password123')
        success, message = self.user_manager.login('testuser', 'password123')
        self.assertTrue(success, f"登录失败: {message}")
        self.assertIsNotNone(self.user_manager.current_user)
        self.assertEqual(self.user_manager.current_user.username, 'testuser')

    def test_login_failure_wrong_password(self):
        """
        测试登录失败 - 密码错误时返回失败
        """
        self.user_manager.register('testuser', 'password123')
        success, message = self.user_manager.login('testuser', 'wrongpassword')
        self.assertFalse(success, "密码错误应登录失败")
        self.assertIsNone(self.user_manager.current_user)

    def test_login_failure_user_not_exists(self):
        """
        测试登录失败 - 用户不存在时返回失败
        """
        success, message = self.user_manager.login('nonexistent', 'password123')
        self.assertFalse(success, "不存在的用户应登录失败")
        self.assertIsNone(self.user_manager.current_user)

    def test_logout(self):
        """
        测试登出 - current_user设为None
        """
        self.user_manager.register('testuser', 'password123')
        self.user_manager.login('testuser', 'password123')
        self.assertIsNotNone(self.user_manager.current_user)
        
        self.user_manager.logout()
        self.assertIsNone(self.user_manager.current_user)

    def test_is_logged_in(self):
        """
        测试检查登录状态 - 正确返回登录状态
        """
        self.assertFalse(self.user_manager.is_logged_in())
        
        self.user_manager.register('testuser', 'password123')
        self.user_manager.login('testuser', 'password123')
        self.assertTrue(self.user_manager.is_logged_in())


if __name__ == '__main__':
    unittest.main()
