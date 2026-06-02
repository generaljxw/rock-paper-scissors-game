# src/business/user_manager.py
"""
业务逻辑层用户管理模块

本模块负责用户注册、登录和状态管理等功能。
采用密码哈希存储确保用户数据安全。
"""

import hashlib
import os
from typing import Optional, Tuple
from ..data.user_dao import UserDAO
from ..data.score_dao import ScoreDAO
from ..data.models import User


class UserManager:
    """
    用户管理类
    提供用户注册、登录、登出等管理功能
    """

    def __init__(self):
        self.user_dao = UserDAO()
        self.score_dao = ScoreDAO()
        self.current_user: Optional[User] = None

    def _generate_salt(self) -> str:
        """
        生成随机盐值
        返回:
            16字节随机盐值的十六进制字符串
        """
        return os.urandom(16).hex()

    def _hash_password(self, password: str, salt: str) -> str:
        """
        使用盐值进行密码哈希
        参数:
            password: 原始密码
            salt: 盐值
        返回:
            哈希加密后的密码字符串
        """
        return hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            bytes.fromhex(salt),
            100000
        ).hex()

    def register(self, username: str, password: str) -> Tuple[bool, str]:
        """
        用户注册
        参数:
            username: 用户名
            password: 原始密码
        返回:
            (是否成功, 消息)
        """
        if len(username) < 3:
            return False, "用户名长度不能少于3个字符"
        if len(password) < 6:
            return False, "密码长度不能少于6个字符"

        salt = self._generate_salt()
        hashed_password = self._hash_password(password, salt)
        success, message = self.user_dao.create_user(username, hashed_password, salt)

        if success:
            # 验证用户是否成功创建并获取用户信息
            user = self.user_dao.verify_user(username, password)
            if not user:
                print(f"警告：用户创建成功但验证失败，用户名: {username}")
                return False, "注册失败：用户信息验证异常"
            
            # 创建积分记录，如果失败则返回错误
            score_success, score_message = self.score_dao.create_score(user.id)
            if score_success:
                # 设置当前用户
                self.current_user = user
            else:
                # 积分记录创建失败，注册流程失败
                print(f"积分记录创建失败: {score_message}")
                return False, f"注册失败: {score_message}"

        return success, message

    def login(self, username: str, password: str) -> Tuple[bool, str]:
        """
        用户登录
        参数:
            username: 用户名
            password: 原始密码
        返回:
            (是否成功, 消息)
        """
        user = self.user_dao.verify_user(username, password)

        if user:
            self.current_user = user
            return True, "登录成功"
        
        # 登录失败时清除当前用户状态
        self.current_user = None
        return False, "用户名或密码错误"

    def logout(self) -> None:
        """
        用户登出
        清除当前用户状态
        """
        self.current_user = None

    def get_current_user(self) -> Optional[User]:
        """
        获取当前登录用户
        返回:
            当前用户对象或None
        """
        return self.current_user

    def is_logged_in(self) -> bool:
        """
        检查用户是否已登录
        返回:
            是否已登录
        """
        return self.current_user is not None
