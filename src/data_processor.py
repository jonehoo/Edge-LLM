from typing import List, Dict, Union, Optional
from datetime import datetime
import pandas as pd
from .data_loader import TemperatureDataLoader
from .db_data_loader import DatabaseDataLoader


class TemperatureDataProcessor:
    """温度数据处理器 - 数据分析和预处理"""
    
    def __init__(self, data_loader: Union[TemperatureDataLoader, DatabaseDataLoader]):
        """
        初始化数据处理器
        
        Args:
            data_loader: 数据加载器实例（支持JSON或数据库模式）
        """
        self.data_loader = data_loader
    
    def to_dataframe(self, device_id: str = None, 
                     start_time: Optional[str] = None,
                     end_time: Optional[str] = None) -> pd.DataFrame:
        """
        将数据转换为Pandas DataFrame
        
        Args:
            device_id: 设备ID，如果为None则包含所有设备
            start_time: 开始时间 (ISO格式字符串)
            end_time: 结束时间 (ISO格式字符串)
            
        Returns:
            DataFrame
        """
        if device_id:
            readings = self.data_loader.get_device_readings(device_id, start_time, end_time)
            device = self.data_loader.get_device_by_id(device_id)
            if device is None:
                return pd.DataFrame()
            df = pd.DataFrame(readings)
            df['device_id'] = device.get('device_id')
            df['device_name'] = device.get('device_name')
            df['location'] = device.get('location')
        else:
            # 对于所有设备，需要手动过滤时间范围
            readings = self.data_loader.get_all_readings()
            df = pd.DataFrame(readings)
            
            # 如果指定了时间范围，进行过滤
            if (start_time or end_time) and not df.empty and 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                if start_time:
                    start_dt = pd.to_datetime(start_time)
                    df = df[df['timestamp'] >= start_dt]
                if end_time:
                    end_dt = pd.to_datetime(end_time)
                    df = df[df['timestamp'] <= end_dt]
        
        # 转换时间戳
        if 'timestamp' in df.columns and not df.empty:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp')
        
        return df
    
    def detect_anomalies(self, device_id: str, threshold: float = 3.0,
                         start_time: Optional[str] = None,
                         end_time: Optional[str] = None) -> List[Dict]:
        """
        检测异常温度值（使用标准差方法）
        
        Args:
            device_id: 设备ID
            threshold: 标准差倍数阈值
            start_time: 开始时间 (ISO格式字符串)
            end_time: 结束时间 (ISO格式字符串)
            
        Returns:
            异常读数列表
        """
        df = self.to_dataframe(device_id, start_time, end_time)
        
        if df.empty or 'temperature' not in df.columns:
            return []
        
        mean_temp = df['temperature'].mean()
        std_temp = df['temperature'].std()
        
        if std_temp == 0:
            return []
        
        anomalies = []
        for idx, row in df.iterrows():
            temp = row['temperature']
            z_score = abs((temp - mean_temp) / std_temp)
            
            if z_score > threshold:
                timestamp_str = row['timestamp'].isoformat() if hasattr(row['timestamp'], 'isoformat') else str(row['timestamp'])
                anomalies.append({
                    'timestamp': timestamp_str,
                    'temperature': float(temp),
                    'z_score': round(z_score, 2),
                    'device_id': device_id,
                    'device_name': row.get('device_name', ''),
                    'anomaly_type': 'high' if temp > mean_temp else 'low'
                })
        
        return anomalies
    
    def get_trend_analysis(self, device_id: str, window_size: int = 5) -> Dict:
        """
        趋势分析
        
        Args:
            device_id: 设备ID
            window_size: 滑动窗口大小
            
        Returns:
            趋势分析结果
        """
        df = self.to_dataframe(device_id)
        
        if df.empty or 'temperature' not in df.columns:
            return {}
        
        # 计算移动平均
        df['moving_avg'] = df['temperature'].rolling(window=window_size, min_periods=1).mean()
        
        # 计算趋势方向
        recent_temps = df['temperature'].tail(window_size).values
        if len(recent_temps) >= 2:
            trend = '上升' if recent_temps[-1] > recent_temps[0] else '下降'
            trend_rate = (recent_temps[-1] - recent_temps[0]) / len(recent_temps)
        else:
            trend = '稳定'
            trend_rate = 0
        
        return {
            'device_id': device_id,
            'trend': trend,
            'trend_rate': round(trend_rate, 2),
            'current_temp': float(df['temperature'].iloc[-1]),
            'avg_temp': float(df['temperature'].mean()),
            'volatility': float(df['temperature'].std())
        }
    
    def prepare_for_llm(self, device_id: str = None,
                       start_time: Optional[str] = None,
                       end_time: Optional[str] = None) -> str:
        """
        准备用于LLM分析的数据摘要
        
        Args:
            device_id: 设备ID，如果为None则包含所有设备
            start_time: 开始时间 (ISO格式字符串)
            end_time: 结束时间 (ISO格式字符串)
            
        Returns:
            格式化的数据摘要字符串
        """
        # 注意：get_statistics 可能不支持日期范围，这里先使用全部数据
        stats = self.data_loader.get_statistics(device_id)
        if not stats:
            return "无可用数据"
        
        df = self.to_dataframe(device_id, start_time, end_time)
        
        # 如果指定了日期范围，重新计算统计信息
        if (start_time or end_time) and not df.empty:
            stats = {
                'device_name': stats.get('device_name', 'N/A'),
                'total_readings': len(df),
                'avg_temperature': float(df['temperature'].mean()) if 'temperature' in df.columns else 0,
                'min_temperature': float(df['temperature'].min()) if 'temperature' in df.columns else 0,
                'max_temperature': float(df['temperature'].max()) if 'temperature' in df.columns else 0,
                'temperature_range': float(df['temperature'].max() - df['temperature'].min()) if 'temperature' in df.columns else 0,
                'normal_count': int((df['status'] == 'normal').sum()) if 'status' in df.columns else 0,
                'warning_count': int((df['status'] == 'warning').sum()) if 'status' in df.columns else 0,
                'alert_count': int((df['status'] == 'alert').sum()) if 'status' in df.columns else 0,
            }
        
        summary = f"""
温度数据分析摘要：
==================
设备名称: {stats.get('device_name', 'N/A')}
总读数: {stats.get('total_readings', 0)}
平均温度: {stats.get('avg_temperature', 0):.2f}°C
最低温度: {stats.get('min_temperature', 0):.2f}°C
最高温度: {stats.get('max_temperature', 0):.2f}°C
温度范围: {stats.get('temperature_range', 0):.2f}°C
正常状态: {stats.get('normal_count', 0)}次
警告状态: {stats.get('warning_count', 0)}次
告警状态: {stats.get('alert_count', 0)}次
"""
        
        if not df.empty and device_id:
            anomalies = self.detect_anomalies(device_id, start_time=start_time, end_time=end_time)
            if anomalies:
                summary += f"\n检测到异常: {len(anomalies)}次\n"
                for anomaly in anomalies[:3]:  # 只显示前3个
                    summary += f"  - {anomaly['timestamp']}: {anomaly['temperature']}°C ({anomaly['anomaly_type']})\n"
        
        # 添加日期范围信息
        if start_time or end_time:
            summary += f"\n日期范围: "
            if start_time:
                summary += f"从 {start_time.split('T')[0]} "
            if end_time:
                summary += f"到 {end_time.split('T')[0]}"
            summary += "\n"
        
        return summary

