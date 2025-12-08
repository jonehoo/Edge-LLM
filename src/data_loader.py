import json
import os
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path


class TemperatureDataLoader:
    """温度数据加载器 - 从JSON文件读取数据"""
    
    def __init__(self, data_file: str = "data/temperature_data.json"):
        """
        初始化数据加载器
        
        Args:
            data_file: JSON数据文件路径
        """
        self.data_file = Path(data_file)
        self.data = None
        
    def load_data(self) -> Dict:
        """
        加载JSON数据文件
        
        Returns:
            包含设备和读数的字典
        """
        if not self.data_file.exists():
            raise FileNotFoundError(f"数据文件不存在: {self.data_file}")
        
        with open(self.data_file, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        
        return self.data
    
    def get_all_devices(self) -> List[Dict]:
        """
        获取所有设备信息
        
        Returns:
            设备列表
        """
        if self.data is None:
            self.load_data()
        return self.data.get('devices', [])
    
    def get_device_by_id(self, device_id: str) -> Optional[Dict]:
        """
        根据设备ID获取设备数据
        
        Args:
            device_id: 设备ID
            
        Returns:
            设备数据字典，如果不存在返回None
        """
        devices = self.get_all_devices()
        for device in devices:
            if device.get('device_id') == device_id:
                return device
        return None
    
    def get_device_readings(self, device_id: str, 
                           start_time: Optional[str] = None,
                           end_time: Optional[str] = None) -> List[Dict]:
        """
        获取指定设备的读数
        
        Args:
            device_id: 设备ID
            start_time: 开始时间 (ISO格式字符串)
            end_time: 结束时间 (ISO格式字符串)
            
        Returns:
            读数列表
        """
        device = self.get_device_by_id(device_id)
        if device is None:
            return []
        
        readings = device.get('readings', [])
        
        # 时间过滤
        if start_time or end_time:
            filtered_readings = []
            for reading in readings:
                timestamp = reading.get('timestamp')
                if start_time and timestamp < start_time:
                    continue
                if end_time and timestamp > end_time:
                    continue
                filtered_readings.append(reading)
            return filtered_readings
        
        return readings
    
    def get_latest_reading(self, device_id: str) -> Optional[Dict]:
        """
        获取设备最新读数
        
        Args:
            device_id: 设备ID
            
        Returns:
            最新读数字典
        """
        readings = self.get_device_readings(device_id)
        if not readings:
            return None
        return readings[-1]
    
    def get_all_readings(self) -> List[Dict]:
        """
        获取所有设备的所有读数（扁平化）
        
        Returns:
            包含设备信息的读数列表
        """
        all_readings = []
        for device in self.get_all_devices():
            for reading in device.get('readings', []):
                reading_with_device = {
                    **reading,
                    'device_id': device.get('device_id'),
                    'device_name': device.get('device_name'),
                    'location': device.get('location')
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
            readings = self.get_device_readings(device_id)
            device = self.get_device_by_id(device_id)
            if device is None:
                return {}
            device_name = device.get('device_name')
        else:
            readings = self.get_all_readings()
            device_name = "所有设备"
        
        if not readings:
            return {}
        
        temperatures = [r.get('temperature') for r in readings if r.get('temperature')]
        
        stats = {
            'device_name': device_name,
            'total_readings': len(readings),
            'avg_temperature': sum(temperatures) / len(temperatures) if temperatures else 0,
            'min_temperature': min(temperatures) if temperatures else 0,
            'max_temperature': max(temperatures) if temperatures else 0,
            'temperature_range': max(temperatures) - min(temperatures) if temperatures else 0,
            'alert_count': sum(1 for r in readings if r.get('status') == 'alert'),
            'warning_count': sum(1 for r in readings if r.get('status') == 'warning'),
            'normal_count': sum(1 for r in readings if r.get('status') == 'normal')
        }
        
        return stats
    
    def clear_cache(self):
        """清除数据缓存（用于强制刷新）"""
        self.data = None

