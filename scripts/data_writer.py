"""
定时数据写入脚本
从JSON文件读取数据并定时写入数据库
"""

import sys
import json
import time
import random
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List
import logging

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.db_connection import DatabaseConnection

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_writer.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DataWriter:
    """数据写入器 - 将JSON数据写入数据库"""
    
    def __init__(self, json_file: str = "data/temperature_data.json", 
                 interval: int = 60):
        """
        初始化数据写入器
        
        Args:
            json_file: JSON数据文件路径
            interval: 写入间隔（秒）
        """
        self.json_file = Path(json_file)
        self.interval = interval
        self.db = DatabaseConnection()
        self.devices_data = None
        
    def load_json_data(self) -> Dict:
        """加载JSON数据"""
        if not self.json_file.exists():
            raise FileNotFoundError(f"JSON文件不存在: {self.json_file}")
        
        with open(self.json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.devices_data = data
        logger.info(f"成功加载JSON数据，共 {len(data.get('devices', []))} 个设备")
        return data
    
    def init_devices(self):
        """初始化设备信息到数据库"""
        if self.devices_data is None:
            self.load_json_data()
        
        devices = self.devices_data.get('devices', [])
        
        for device in devices:
            device_id = device.get('device_id')
            device_name = device.get('device_name')
            location = device.get('location')
            
            # 检查设备是否已存在
            existing = self.db.execute_query(
                "SELECT device_id FROM devices WHERE device_id = %s",
                (device_id,)
            )
            
            if not existing:
                # 插入新设备
                self.db.execute_update(
                    """INSERT INTO devices (device_id, device_name, location) 
                       VALUES (%s, %s, %s)""",
                    (device_id, device_name, location)
                )
                logger.info(f"已添加设备: {device_name} ({device_id})")
            else:
                # 更新设备信息
                self.db.execute_update(
                    """UPDATE devices SET device_name = %s, location = %s 
                       WHERE device_id = %s""",
                    (device_name, location, device_id)
                )
                logger.debug(f"设备已存在，已更新: {device_name} ({device_id})")
    
    def generate_new_reading(self, device: Dict) -> Dict:
        """
        基于设备历史数据生成新的模拟读数
        
        Args:
            device: 设备信息字典
            
        Returns:
            新的读数字典
        """
        readings = device.get('readings', [])
        
        if not readings:
            # 如果没有历史数据，生成默认值
            base_temp = 25.0
            base_humidity = 60.0
        else:
            # 基于最新读数生成
            latest = readings[-1]
            base_temp = latest.get('temperature', 25.0)
            base_humidity = latest.get('humidity', 60.0)
        
        # 生成随机变化（±2度，±3%湿度）
        temp_change = random.uniform(-2.0, 2.0)
        humidity_change = random.uniform(-3.0, 3.0)
        
        new_temp = round(base_temp + temp_change, 1)
        new_humidity = round(base_humidity + humidity_change, 1)
        
        # 根据温度确定状态
        if new_temp >= 29.0:
            status = "alert"
        elif new_temp >= 27.0:
            status = "warning"
        else:
            status = "normal"
        
        return {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'temperature': new_temp,
            'humidity': new_humidity,
            'status': status
        }
    
    def write_reading(self, device_id: str, reading: Dict):
        """
        写入单个读数到数据库
        
        Args:
            device_id: 设备ID
            reading: 读数字典
        """
        try:
            # 检查是否已存在相同时间戳的读数（避免重复）
            existing = self.db.execute_query(
                """SELECT id FROM readings 
                   WHERE device_id = %s AND timestamp = %s""",
                (device_id, reading['timestamp'])
            )
            
            if existing:
                logger.debug(f"读数已存在，跳过: {device_id} @ {reading['timestamp']}")
                return
            
            # 插入新读数
            self.db.execute_update(
                """INSERT INTO readings (device_id, timestamp, temperature, humidity, status)
                   VALUES (%s, %s, %s, %s, %s)""",
                (device_id, reading['timestamp'], reading['temperature'], 
                 reading['humidity'], reading['status'])
            )
            logger.info(f"已写入读数: {device_id} - {reading['temperature']}°C @ {reading['timestamp']}")
            
        except Exception as e:
            logger.error(f"写入读数失败: {e}")
            raise
    
    def write_all_historical_data(self):
        """写入所有历史数据到数据库（一次性）"""
        if self.devices_data is None:
            self.load_json_data()
        
        logger.info("开始写入历史数据...")
        devices = self.devices_data.get('devices', [])
        
        total_readings = 0
        for device in devices:
            device_id = device.get('device_id')
            readings = device.get('readings', [])
            
            for reading in readings:
                # 转换时间格式
                timestamp_str = reading.get('timestamp')
                # 从 ISO 格式转换为 MySQL DATETIME 格式
                if 'T' in timestamp_str:
                    dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    reading['timestamp'] = dt.strftime('%Y-%m-%d %H:%M:%S')
                
                self.write_reading(device_id, reading)
                total_readings += 1
        
        logger.info(f"历史数据写入完成，共写入 {total_readings} 条读数")
    
    def run_continuous(self):
        """持续运行，定时写入新数据"""
        logger.info("=" * 50)
        logger.info("开始定时数据写入服务")
        logger.info(f"写入间隔: {self.interval} 秒")
        logger.info("按 Ctrl+C 停止服务")
        logger.info("=" * 50)
        
        # 初始化设备
        self.init_devices()
        
        try:
            while True:
                if self.devices_data is None:
                    self.load_json_data()
                
                devices = self.devices_data.get('devices', [])
                
                # 为每个设备生成并写入新读数
                for device in devices:
                    device_id = device.get('device_id')
                    new_reading = self.generate_new_reading(device)
                    self.write_reading(device_id, new_reading)
                    
                    # 更新设备数据中的最新读数（用于下次生成）
                    if 'readings' not in device:
                        device['readings'] = []
                    device['readings'].append(new_reading)
                    # 只保留最近10条，避免内存增长
                    if len(device['readings']) > 10:
                        device['readings'] = device['readings'][-10:]
                
                logger.info(f"等待 {self.interval} 秒后继续...")
                time.sleep(self.interval)
                
        except KeyboardInterrupt:
            logger.info("\n收到停止信号，正在关闭服务...")
        except Exception as e:
            logger.error(f"运行错误: {e}")
            raise
        finally:
            self.db.close()
            logger.info("数据写入服务已停止")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='定时数据写入脚本')
    parser.add_argument('--json', type=str, default='data/temperature_data.json',
                       help='JSON数据文件路径')
    parser.add_argument('--interval', type=int, default=60,
                       help='写入间隔（秒），默认60秒')
    parser.add_argument('--init', action='store_true',
                       help='初始化：写入所有历史数据后退出')
    
    args = parser.parse_args()
    
    writer = DataWriter(json_file=args.json, interval=args.interval)
    
    try:
        if args.init:
            # 初始化模式：写入历史数据
            writer.load_json_data()
            writer.init_devices()
            writer.write_all_historical_data()
            logger.info("历史数据初始化完成！")
        else:
            # 持续运行模式
            writer.run_continuous()
    except Exception as e:
        logger.error(f"程序执行失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

