"""
温度分析服务
整合数据加载、处理和大模型分析
"""

from typing import Dict, List, Optional, Iterator
from pathlib import Path
from .data_loader import TemperatureDataLoader
from .db_data_loader import DatabaseDataLoader
from .data_processor import TemperatureDataProcessor
from .llm_service import LLMService


class TemperatureAnalyzer:
    """温度分析服务 - 整合所有功能"""
    
    def __init__(self, data_file: str = "data/temperature_data.json",
                 model_path: str = "models/qwen-0.6b.gguf",
                 use_database: bool = False,
                 model_type: str = "local",
                 openai_api_key: Optional[str] = None,
                 openai_model: str = "gpt-3.5-turbo",
                 openai_base_url: Optional[str] = None,
                 n_ctx: int = 2048,
                 n_threads: int = 4):
        """
        初始化分析服务
        
        Args:
            data_file: 数据文件路径（当use_database=False时使用）
            model_path: 本地模型文件路径（当model_type="local"时使用）
            use_database: 是否使用数据库模式（True=数据库，False=JSON文件）
            model_type: 模型类型，"local" 或 "openai"
            openai_api_key: OpenAI API密钥（当model_type="openai"时使用）
            openai_model: OpenAI模型名称
            openai_base_url: OpenAI API基础URL（可选）
            n_ctx: 本地模型上下文窗口大小
            n_threads: 本地模型线程数
        """
        # 初始化数据模块
        if use_database:
            self.data_loader = DatabaseDataLoader()
        else:
            self.data_loader = TemperatureDataLoader(data_file)
        
        self.data_processor = TemperatureDataProcessor(self.data_loader)
        
        # 初始化LLM服务
        self.llm_service = LLMService(
            model_type=model_type,
            model_path=model_path,
            n_ctx=n_ctx,
            n_threads=n_threads,
            openai_api_key=openai_api_key,
            openai_model=openai_model,
            openai_base_url=openai_base_url
        )
        
        # 加载数据
        self.data_loader.load_data()
    
    def get_device_list(self) -> List[Dict]:
        """
        获取所有设备列表
        
        Returns:
            设备列表
        """
        devices = self.data_loader.get_all_devices()
        result = []
        for d in devices:
            # 对于数据库模式，需要单独获取读数数量
            if hasattr(self.data_loader, 'db'):
                # 数据库模式
                stats = self.data_loader.get_statistics(d.get('device_id'))
                readings_count = stats.get('total_readings', 0)
            else:
                # JSON文件模式
                readings_count = len(d.get('readings', []))
            
            result.append({
                'device_id': d.get('device_id'),
                'device_name': d.get('device_name'),
                'location': d.get('location'),
                'readings_count': readings_count
            })
        return result
    
    def get_device_overview(self, device_id: str) -> Dict:
        """
        获取设备概览信息
        
        Args:
            device_id: 设备ID
            
        Returns:
            设备概览字典
        """
        stats = self.data_loader.get_statistics(device_id)
        latest = self.data_loader.get_latest_reading(device_id)
        trend = self.data_processor.get_trend_analysis(device_id)
        anomalies = self.data_processor.detect_anomalies(device_id)
        
        return {
            'device_id': device_id,
            'statistics': stats,
            'latest_reading': latest,
            'trend': trend,
            'anomalies_count': len(anomalies),
            'anomalies': anomalies[:5]  # 只返回前5个异常
        }
    
    def analyze_device(self, device_id: str, 
                      analysis_type: str = "comprehensive") -> Dict:
        """
        分析设备数据（包含LLM分析）
        
        Args:
            device_id: 设备ID
            analysis_type: 分析类型
            
        Returns:
            分析结果字典
        """
        # 获取数据摘要
        data_summary = self.data_processor.prepare_for_llm(device_id)
        
        # 获取基础分析
        overview = self.get_device_overview(device_id)
        
        # LLM分析
        llm_analysis = self.llm_service.analyze_temperature_data(
            data_summary, 
            analysis_type
        )
        
        return {
            **overview,
            'llm_analysis': llm_analysis,
            'data_summary': data_summary,
            'model_available': self.llm_service.is_available()
        }
    
    def get_all_devices_analysis(self) -> Dict:
        """
        分析所有设备
        
        Returns:
            所有设备的分析结果
        """
        devices = self.get_device_list()
        all_stats = self.data_loader.get_statistics()
        
        # 准备所有设备的数据摘要
        all_data_summary = self.data_processor.prepare_for_llm()
        
        # LLM综合分析
        llm_analysis = self.llm_service.analyze_temperature_data(
            all_data_summary,
            "comprehensive"
        )
        
        return {
            'devices': devices,
            'overall_statistics': all_stats,
            'llm_analysis': llm_analysis,
            'model_available': self.llm_service.is_available()
        }
    
    def get_dataframe(self, device_id: Optional[str] = None):
        """
        获取DataFrame格式的数据
        
        Args:
            device_id: 设备ID，如果为None则返回所有设备
            
        Returns:
            DataFrame
        """
        return self.data_processor.to_dataframe(device_id)
    
    def get_temperature_chart_data(self, device_id: str) -> Dict:
        """
        获取用于图表展示的数据
        
        Args:
            device_id: 设备ID
            
        Returns:
            图表数据字典
        """
        df = self.data_processor.to_dataframe(device_id)
        
        if df.empty:
            return {
                'timestamps': [],
                'temperatures': [],
                'humidity': [],
                'status': []
            }
        
        return {
            'timestamps': df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S').tolist(),
            'temperatures': df['temperature'].tolist(),
            'humidity': df['humidity'].tolist() if 'humidity' in df.columns else [],
            'status': df['status'].tolist() if 'status' in df.columns else []
        }
    
    def analyze_device_stream(self, device_id: str, 
                              analysis_type: str = "comprehensive") -> Iterator[str]:
        """
        流式分析设备数据（包含LLM分析）
        
        Args:
            device_id: 设备ID
            analysis_type: 分析类型
            
        Yields:
            分析文本片段
        """
        # 获取数据摘要
        data_summary = self.data_processor.prepare_for_llm(device_id)
        
        # 使用LLM服务的流式分析方法
        for chunk in self.llm_service.analyze_temperature_data_stream(
            data_summary,
            analysis_type
        ):
            yield chunk

