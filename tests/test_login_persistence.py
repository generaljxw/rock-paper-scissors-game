"""
测试用例 - 修复验证测试

本模块针对登录异常退出和数据持久化问题进行测试验证
"""

import pytest
import sys
import os
import tempfile
import shutil
import uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.business.user_manager import UserManager
from src.business.score_manager import ScoreManager
from src.data.database import Database
from src.data.user_dao import UserDAO


class TestLoginAndPersistence:
    """
    测试登录和数据持久化功能
    """

    def test_register_and_login_flow(self):
        """
        测试完整的注册登录流程
        验证：注册成功后登录，确保积分记录正确创建
        """
        user_manager = UserManager()
        score_manager = ScoreManager()
        
        # 使用唯一用户名
        username = f"test_user_login_{uuid.uuid4().hex[:8]}"
        password = "password123"
        
        # 注册
        success, message = user_manager.register(username, password)
        assert success, f"注册失败: {message}"
        
        # 验证积分记录已创建
        user = user_manager.get_current_user()
        assert user is not None, "注册成功后应设置当前用户"
        
        score = score_manager.get_score(user.id)
        assert score == 0, "新注册用户初始积分应为0"
        
        # 登录验证（新实例）
        user_manager2 = UserManager()
        success, message = user_manager2.login(username, password)
        assert success, f"登录失败: {message}"
        
        user2 = user_manager2.get_current_user()
        assert user2 is not None
        assert user2.username == username

    def test_login_after_restart(self):
        """
        测试重启后的登录功能
        验证：注册后退出，再次启动游戏仍能正常登录
        """
        user_manager = UserManager()
        
        # 使用唯一用户名
        username = f"test_user_persist_{uuid.uuid4().hex[:8]}"
        password = "password123"
        
        # 注册
        success, message = user_manager.register(username, password)
        assert success, f"注册失败: {message}"
        
        # 模拟退出后重新创建用户管理器
        user_manager2 = UserManager()
        
        # 使用相同账号密码登录
        success, message = user_manager2.login(username, password)
        assert success, f"登录失败: {message}"
        
        user = user_manager2.get_current_user()
        assert user is not None
        assert user.username == username

    def test_user_data_persistence(self):
        """
        测试用户数据持久化
        验证：用户信息在多次登录后保持一致
        """
        user_manager1 = UserManager()
        score_manager1 = ScoreManager()
        
        # 使用唯一用户名
        username = f"test_user_data_{uuid.uuid4().hex[:8]}"
        password = "password123"
        
        # 注册
        success, message = user_manager1.register(username, password)
        assert success, f"注册失败: {message}"
        
        user1 = user_manager1.get_current_user()
        assert user1 is not None, "注册成功后应设置当前用户"
        user_id = user1.id
        
        # 更新积分
        score_manager1.update_score(user_id, 10)
        score1 = score_manager1.get_score(user_id)
        assert score1 == 10
        
        # 创建新的管理器实例（模拟重启）
        user_manager2 = UserManager()
        score_manager2 = ScoreManager()
        
        # 登录
        success, message = user_manager2.login(username, password)
        assert success, f"登录失败: {message}"
        
        user2 = user_manager2.get_current_user()
        assert user2.id == user_id
        
        # 验证积分数据持久化
        score2 = score_manager2.get_score(user_id)
        assert score2 == 10, f"积分数据未持久化，预期10，实际{score2}"

    def test_register_with_score_creation(self):
        """
        测试注册时积分记录创建
        验证：注册成功时积分记录必须同时创建
        """
        user_manager = UserManager()
        score_manager = ScoreManager()
        
        # 使用唯一用户名
        username = f"test_user_score_{uuid.uuid4().hex[:8]}"
        password = "password123"
        
        # 注册
        success, message = user_manager.register(username, password)
        assert success, f"注册失败: {message}"
        
        user = user_manager.get_current_user()
        assert user is not None, "注册成功后应设置当前用户"
        
        # 验证积分记录存在
        score_info = score_manager.get_score_info(user.id)
        assert score_info is not None
        assert score_info.user_id == user.id
        assert score_info.total_score == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])