"""
数据库数据加载器
从MySQL数据库读取温度数据
"""

from datetime import datetime
from typing import List, Dict, Optional
from .db_connection import DatabaseConnection
import logging

logger = logging.getLogger(__name__)


class DatabaseDataLoader:
    """数据库数据加载器 - 从MySQL数据库读取数据"""
    
    def __init__(self):
        """初始化数据库数据加载器"""
        import yaml
        from pathlib import Path
        
        # 读取数据库配置
        config_path = Path(__file__).parent.parent.parent / "config" / "config.yaml"
        db_config = {}
        
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                db_config = config.get('database', {})
        
        # 初始化数据库连接，传递配置参数
        self.db = DatabaseConnection(
            host=db_config.get('host', 'localhost'),
            port=db_config.get('port', 3306),
            user=db_config.get('user', 'edge-llm'),
            password=db_config.get('password', 'edge-llm'),
            database=db_config.get('database', 'edge-llm'),
            charset=db_config.get('charset', 'utf8mb4'),
            connect_timeout=db_config.get('connect_timeout', 10),
            read_timeout=db_config.get('read_timeout', 30),
            write_timeout=db_config.get('write_timeout', 30),
            max_retries=db_config.get('max_retries', 3)
        )
        self._devices_cache = None
    
    def load_data(self) -> Dict:
        """
        加载数据（从数据库）
        
        Returns:
            包含设备和读数的字典（兼容JSON格式）
        """
        devices = self.get_all_devices()
        
        # 为每个设备加载读数（限制数量以避免内存问题）
        for device in devices:
            device_id = device['device_id']
            # 只加载最近1000条读数
            device['readings'] = self.get_device_readings(device_id, limit=1000)
        
        # 构建兼容JSON格式的数据结构
        data = {
            'devices': devices,
            'metadata': {
                'last_updated': datetime.now().isoformat(),
                'total_devices': len(devices),
                'data_source': 'database'
            }
        }
        
        return data
    
    def get_all_devices(self) -> List[Dict]:
        """
        获取所有设备信息
        
        Returns:
            设备列表
        """
        if self._devices_cache is None:
            devices = self.db.execute_query(
                "SELECT device_id, device_name, location FROM devices ORDER BY device_id"
            )
            self._devices_cache = [
                {
                    'device_id': d['device_id'],
                    'device_name': d['device_name'],
                    'location': d['location']
                }
                for d in devices
            ]
        
        return self._devices_cache.copy()
    
    def get_device_by_id(self, device_id: str) -> Optional[Dict]:
        """
        根据设备ID获取设备数据
        
        Args:
            device_id: 设备ID
            
        Returns:
            设备数据字典，如果不存在返回None
        """
        device = self.db.execute_query(
            "SELECT device_id, device_name, location FROM devices WHERE device_id = %s",
            (device_id,)
        )
        
        if not device:
            return None
        
        device_info = device[0]
        device_info['readings'] = self.get_device_readings(device_id)
        
        return {
            'device_id': device_info['device_id'],
            'device_name': device_info['device_name'],
            'location': device_info['location'],
            'readings': device_info['readings']
        }
    
    def get_device_readings(self, device_id: str, 
                           start_time: Optional[str] = None,
                           end_time: Optional[str] = None,
                           limit: Optional[int] = None) -> List[Dict]:
        """
        获取指定设备的读数
        
        Args:
            device_id: 设备ID
            start_time: 开始时间 (ISO格式字符串或MySQL DATETIME格式)
            end_time: 结束时间 (ISO格式字符串或MySQL DATETIME格式)
            limit: 限制返回数量（最新N条）
            
        Returns:
            读数列表
        """
        # 构建查询
        query = """
            SELECT timestamp, temperature, humidity, status 
            FROM readings 
            WHERE device_id = %s
        """
        params = [device_id]
        
        # 时间过滤
        if start_time:
            # 转换ISO格式到MySQL格式
            if 'T' in start_time:
                start_time = start_time.replace('T', ' ').split('.')[0]
            query += " AND timestamp >= %s"
            params.append(start_time)
        
        if end_time:
            # 转换ISO格式到MySQL格式
            if 'T' in end_time:
                end_time = end_time.replace('T', ' ').split('.')[0]
            query += " AND timestamp <= %s"
            params.append(end_time)
        
        # 排序和限制
        query += " ORDER BY timestamp DESC"
        
        if limit:
            query += " LIMIT %s"
            params.append(limit)
        
        results = self.db.execute_query(query, tuple(params))
        
        # 转换格式（反转顺序，使其按时间正序）
        readings = []
        for row in reversed(results):
            readings.append({
                'timestamp': row['timestamp'].isoformat() if isinstance(row['timestamp'], datetime) 
                           else str(row['timestamp']),
                'temperature': float(row['temperature']),
                'humidity': float(row['humidity']),
                'status': row['status']
            })
        
        return readings
    
    def get_latest_reading(self, device_id: str) -> Optional[Dict]:
        """
        获取设备最新读数
        
        Args:
            device_id: 设备ID
            
        Returns:
            最新读数字典
        """
        readings = self.get_device_readings(device_id, limit=1)
        return readings[0] if readings else None
    
    def get_all_readings(self) -> List[Dict]:
        """
        获取所有设备的所有读数（扁平化）
        
        Returns:
            包含设备信息的读数列表
        """
        all_readings = []
        devices = self.get_all_devices()
        
        for device in devices:
            device_id = device['device_id']
            readings = self.get_device_readings(device_id)
            
            for reading in readings:
                reading_with_device = {
                    **reading,
                    'device_id': device_id,
                    'device_name': device['device_name'],
                    'location': device['location']
                }
                all_readings.append(reading_with_device)
        
        return all_readings
    
    def get_statistics(self, device_id: Optional[str] = None) -> Dict:
        """
        获取统计信息
        
        Args:
            device_id: 设备ID，如果为None则统计所有设备
            
        Returns:
            统计信息字典
        """
        if device_id:
            # 单个设备统计
            device = self.db.execute_query(
                "SELECT device_name FROM devices WHERE device_id = %s",
                (device_id,)
            )
            if not device:
                return {}
            
            device_name = device[0]['device_name']
            
            stats_query = """
                SELECT 
                    COUNT(*) as total_readings,
                    AVG(temperature) as avg_temperature,
                    MIN(temperature) as min_temperature,
                    MAX(temperature) as max_temperature,
                    SUM(CASE WHEN status = 'alert' THEN 1 ELSE 0 END) as alert_count,
                    SUM(CASE WHEN status = 'warning' THEN 1 ELSE 0 END) as warning_count,
                    SUM(CASE WHEN status = 'normal' THEN 1 ELSE 0 END) as normal_count
                FROM readings
                WHERE device_id = %s
            """
            results = self.db.execute_query(stats_query, (device_id,))
        else:
            # 所有设备统计
            device_name = "所有设备"
            stats_query = """
                SELECT 
                    COUNT(*) as total_readings,
                    AVG(temperature) as avg_temperature,
                    MIN(temperature) as min_temperature,
                    MAX(temperature) as max_temperature,
                    SUM(CASE WHEN status = 'alert' THEN 1 ELSE 0 END) as alert_count,
                    SUM(CASE WHEN status = 'warning' THEN 1 ELSE 0 END) as warning_count,
                    SUM(CASE WHEN status = 'normal' THEN 1 ELSE 0 END) as normal_count
                FROM readings
            """
            results = self.db.execute_query(stats_query)
        
        if not results or not results[0]['total_readings']:
            return {}
        
        row = results[0]
        
        stats = {
            'device_name': device_name,
            'total_readings': int(row['total_readings']),
            'avg_temperature': float(row['avg_temperature']) if row['avg_temperature'] else 0,
            'min_temperature': float(row['min_temperature']) if row['min_temperature'] else 0,
            'max_temperature': float(row['max_temperature']) if row['max_temperature'] else 0,
            'temperature_range': float(row['max_temperature'] - row['min_temperature']) 
                              if row['max_temperature'] and row['min_temperature'] else 0,
            'alert_count': int(row['alert_count']),
            'warning_count': int(row['warning_count']),
            'normal_count': int(row['normal_count'])
        }
        
        return stats
    
    def clear_cache(self):
        """清除设备缓存"""
        self._devices_cache = None
    
    def close(self):
        """关闭数据库连接"""
        self.db.close()

