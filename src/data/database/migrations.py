# src/data/database/migrations.py
"""
数据库迁移管理模块
负责管理数据库迁移脚本的执行和回滚
"""

import os
import sqlite3
import glob
import importlib.util
from datetime import datetime


class MigrationManager:
    """迁移管理器"""
    
    def __init__(self, db_path):
        self.db_path = db_path
        self.migrations_dir = os.path.join(os.path.dirname(__file__), '..', 'migrations')
        self.migrations_dir = os.path.abspath(self.migrations_dir)
        
        os.makedirs(self.migrations_dir, exist_ok=True)
        
    def _ensure_migration_table(self, conn):
        """确保迁移记录表存在"""
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS migrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                migration_name TEXT UNIQUE NOT NULL,
                executed_at TIMESTAMP NOT NULL,
                success INTEGER NOT NULL DEFAULT 1
            )
        """)
        conn.commit()
        
    def _get_executed_migrations(self, conn):
        """获取已执行的迁移列表"""
        cursor = conn.cursor()
        cursor.execute("SELECT migration_name FROM migrations WHERE success = 1")
        return [row[0] for row in cursor.fetchall()]
    
    def _mark_migration_executed(self, conn, migration_name, success=True):
        """标记迁移已执行"""
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO migrations 
            (migration_name, executed_at, success)
            VALUES (?, ?, ?)
        """, (migration_name, datetime.now(), 1 if success else 0))
        conn.commit()
        
    def _backup_database(self, backup_path=None):
        """备份数据库"""
        if not os.path.exists(self.db_path):
            print("[INFO] 数据库文件不存在，跳过备份")
            return False
            
        if backup_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"{self.db_path}.backup.{timestamp}"
        
        try:
            with open(self.db_path, 'rb') as src:
                with open(backup_path, 'wb') as dst:
                    dst.write(src.read())
            print(f"[OK] 数据库备份成功: {backup_path}")
            return True
        except Exception as e:
            print(f"[ERROR] 数据库备份失败: {str(e)}")
            return False
            
    def _get_migration_files(self):
        """获取所有迁移文件，按编号排序"""
        pattern = os.path.join(self.migrations_dir, '*.py')
        files = glob.glob(pattern)
        files = [f for f in files if not os.path.basename(f).startswith('_')]
        files.sort()
        return files
        
    def _import_migration(self, file_path):
        """导入迁移模块"""
        module_name = os.path.basename(file_path)[:-3]
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
        
    def run_migrations(self, backup=True):
        """执行所有待处理的迁移"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        if backup:
            self._backup_database()
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        try:
            self._ensure_migration_table(conn)
            executed_migrations = self._get_executed_migrations(conn)
            migration_files = self._get_migration_files()
            
            if not migration_files:
                print("[INFO] 没有找到迁移脚本")
                return
            
            print(f"[INFO] 找到 {len(migration_files)} 个迁移脚本")
            print(f"[INFO] 已执行 {len(executed_migrations)} 个迁移")
            print(f"[INFO] 待执行 {len(migration_files) - len(executed_migrations)} 个迁移")
            
            migration_log = []
            
            for file_path in migration_files:
                migration_name = os.path.basename(file_path)[:-3]
                
                if migration_name in executed_migrations:
                    print(f"[SKIP] 跳过已执行的迁移: {migration_name}")
                    continue
                
                print(f"\n[RUN] 正在执行迁移: {migration_name}")
                
                try:
                    start_time = datetime.now()
                    module = self._import_migration(file_path)
                    module.upgrade(conn)
                    end_time = datetime.now()
                    duration = (end_time - start_time).total_seconds()
                    
                    self._mark_migration_executed(conn, migration_name, success=True)
                    
                    log_entry = {
                        'name': migration_name,
                        'status': 'SUCCESS',
                        'start_time': start_time.strftime("%Y-%m-%d %H:%M:%S"),
                        'duration': f"{duration:.2f}s"
                    }
                    migration_log.append(log_entry)
                    
                    print(f"[OK] 迁移 {migration_name} 执行成功 ({duration:.2f}s)")
                    
                except Exception as e:
                    log_entry = {
                        'name': migration_name,
                        'status': 'FAILED',
                        'error': str(e)
                    }
                    migration_log.append(log_entry)
                    
                    print(f"[ERROR] 迁移 {migration_name} 执行失败: {str(e)}")
                    raise
                    
            print("\n" + "="*60)
            print("[REPORT] 迁移执行报告")
            print("="*60)
            
            for entry in migration_log:
                if entry['status'] == 'SUCCESS':
                    print(f"[OK] {entry['name']}")
                    print(f"      - 时间: {entry['start_time']}")
                    print(f"      - 耗时: {entry['duration']}")
                else:
                    print(f"[ERROR] {entry['name']}")
                    print(f"        - 错误: {entry['error']}")
            
            print("\n[OK] 数据库迁移完成")
            
        finally:
            conn.close()
            
    def rollback_migration(self, migration_name):
        """回滚指定迁移"""
        conn = sqlite3.connect(self.db_path)
        
        try:
            executed_migrations = self._get_executed_migrations(conn)
            
            if migration_name not in executed_migrations:
                print(f"[ERROR] 迁移 {migration_name} 未执行，无法回滚")
                return False
            
            file_path = os.path.join(self.migrations_dir, f"{migration_name}.py")
            
            if not os.path.exists(file_path):
                print(f"[ERROR] 迁移文件不存在: {file_path}")
                return False
            
            print(f"[RUN] 正在回滚迁移: {migration_name}")
            
            module = self._import_migration(file_path)
            module.downgrade(conn)
            
            cursor = conn.cursor()
            cursor.execute("DELETE FROM migrations WHERE migration_name = ?", (migration_name,))
            conn.commit()
            
            print(f"[OK] 迁移 {migration_name} 回滚成功")
            return True
            
        finally:
            conn.close()
            
    def list_migrations(self):
        """列出所有迁移及其状态"""
        conn = sqlite3.connect(self.db_path)
        
        try:
            self._ensure_migration_table(conn)
            executed = self._get_executed_migrations(conn)
            all_migrations = [os.path.basename(f)[:-3] for f in self._get_migration_files()]
            
            print("[LIST] 迁移列表:")
            print("-"*60)
            
            for migration in all_migrations:
                status = "[OK]" if migration in executed else "[PENDING]"
                print(f"{status} {migration}")
                
        finally:
            conn.close()


def main():
    """迁移命令行接口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='数据库迁移工具')
    parser.add_argument('command', choices=['migrate', 'rollback', 'list'],
                        help='执行的命令: migrate(执行迁移), rollback(回滚), list(列出迁移)')
    parser.add_argument('--db', default='data/game.db',
                        help='数据库文件路径')
    parser.add_argument('--name', help='回滚时指定迁移名称')
    parser.add_argument('--no-backup', action='store_true',
                        help='执行迁移时不备份数据库')
    
    args = parser.parse_args()
    
    db_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', args.db)
    db_path = os.path.abspath(db_path)
    
    manager = MigrationManager(db_path)
    
    if args.command == 'migrate':
        manager.run_migrations(backup=not args.no_backup)
    elif args.command == 'rollback':
        if not args.name:
            print("[ERROR] 回滚需要指定迁移名称: --name <migration_name>")
            return
        manager.rollback_migration(args.name)
    elif args.command == 'list':
        manager.list_migrations()


if __name__ == '__main__':
    main()
