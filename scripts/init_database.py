"""
数据库初始化脚本
创建必要的数据库表结构
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.db_connection import DatabaseConnection
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def create_tables():
    """创建数据库表"""
    
    # 设备表
    create_devices_table = """
    CREATE TABLE IF NOT EXISTS devices (
        device_id VARCHAR(50) PRIMARY KEY,
        device_name VARCHAR(100) NOT NULL,
        location VARCHAR(100) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX idx_device_id (device_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """
    
    # 读数表
    create_readings_table = """
    CREATE TABLE IF NOT EXISTS readings (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        device_id VARCHAR(50) NOT NULL,
        timestamp DATETIME NOT NULL,
        temperature DECIMAL(5, 2) NOT NULL,
        humidity DECIMAL(5, 2) NOT NULL,
        status VARCHAR(20) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_device_id (device_id),
        INDEX idx_timestamp (timestamp),
        INDEX idx_device_timestamp (device_id, timestamp),
        FOREIGN KEY (device_id) REFERENCES devices(device_id) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """
    
    try:
        with DatabaseConnection() as db:
            logger.info("开始创建数据库表...")
            
            # 创建设备表
            logger.info("创建 devices 表...")
            db.execute_update(create_devices_table)
            logger.info("devices 表创建成功")
            
            # 创建读数表
            logger.info("创建 readings 表...")
            db.execute_update(create_readings_table)
            logger.info("readings 表创建成功")
            
            logger.info("数据库表创建完成！")
            
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        raise


def check_tables():
    """检查表是否存在"""
    try:
        with DatabaseConnection() as db:
            tables = db.execute_query("SHOW TABLES")
            table_names = [list(table.values())[0] for table in tables]
            logger.info(f"当前数据库中的表: {table_names}")
            return 'devices' in table_names and 'readings' in table_names
    except Exception as e:
        logger.error(f"检查表失败: {e}")
        return False


if __name__ == "__main__":
    print("=" * 50)
    print("数据库初始化脚本")
    print("=" * 50)
    
    # 检查表是否已存在
    if check_tables():
        print("⚠️  表已存在，是否要重新创建？")
        response = input("输入 'yes' 继续，其他任意键退出: ")
        if response.lower() != 'yes':
            print("已取消操作")
            sys.exit(0)
    
    try:
        create_tables()
        print("\n✅ 数据库初始化成功！")
    except Exception as e:
        print(f"\n❌ 数据库初始化失败: {e}")
        sys.exit(1)

