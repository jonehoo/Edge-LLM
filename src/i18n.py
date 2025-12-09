"""
国际化模块
支持中英文切换
"""

from typing import Dict

# 翻译字典
TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "zh": {
        # 页面标题
        "page_title": "边缘物联网温度分析系统",
        "main_title": "🌡️ 边缘物联网温度分析系统",
        
        # 导航
        "nav": "📊 导航",
        "page_overview": "设备概览",
        "page_detail": "设备详情",
        "page_analysis": "综合分析",
        "page_visualization": "数据可视化",
        "select_device": "选择设备",
        "select_analysis_type": "选择分析类型",
        
        # 按钮
        "refresh_data": "🔄 刷新数据",
        "start_analysis": "开始分析",
        "manual_refresh": "立即刷新",
        
        # 模型状态
        "model_status": "🤖 模型状态",
        "local_model_loaded": "✅ 本地大模型已加载",
        "openai_connected": "✅ OpenAI模型已连接",
        "model_name": "模型",
        "using_mock_mode": "⚠️ 使用模拟模式（模型未加载）",
        "mock_mode_hint": "提示：安装llama-cpp-python并确保模型文件存在",
        "openai_failed": "⚠️ OpenAI连接失败",
        "openai_hint": "提示：请检查API密钥和网络连接",
        
        # 数据信息
        "data_info": "📁 数据信息",
        "device_count": "设备数量",
        "total_readings": "总读数",
        "last_update": "最后更新",
        
        # 设备概览
        "device_overview": "📋 设备概览",
        "device_list": "设备列表",
        "quick_stats": "📊 快速统计",
        "avg_temperature": "平均温度",
        "min_temperature": "最低温度",
        "max_temperature": "最高温度",
        "temperature_range": "温度范围",
        "no_devices": "没有找到设备数据",
        
        # 设备详情
        "device_detail": "🔍 设备详情分析",
        "select_device": "选择设备",
        "statistics": "📈 统计信息",
        "latest_reading": "📡 最新读数",
        "time": "时间",
        "temperature": "温度",
        "humidity": "湿度",
        "status": "状态",
        "trend_analysis": "📊 趋势分析",
        "current_temp": "当前温度",
        "trend": "趋势",
        "volatility": "波动性",
        "anomaly_detection": "⚠️ 异常检测",
        "anomalies_detected": "检测到 {count} 个异常读数",
        "no_anomalies": "✅ 未检测到异常",
        "ai_analysis": "🤖 AI智能分析",
        "enable_stream": "启用流式输出",
        "stream_hint": "实时显示AI分析生成过程",
        "generating_analysis": "正在生成AI分析...",
        "analyzing_data": "正在分析设备数据...",
        
        # 综合分析
        "comprehensive_analysis": "🔬 综合分析",
        "select_analysis_type": "选择分析类型",
        "analysis_comprehensive": "综合分析",
        "analysis_anomaly": "异常分析",
        "analysis_trend": "趋势分析",
        "analysis_recommendation": "建议方案",
        "select_device_optional": "选择设备（可选）",
        "all_devices": "所有设备",
        "generating_report": "正在生成AI分析报告...",
        "date_range_filter": "📅 日期区间筛选",
        "start_date": "开始日期",
        "end_date": "结束日期",
        "select_date_range": "选择日期区间（可选）",
        "use_date_filter": "启用日期筛选",
        
        # 数据可视化
        "data_visualization": "📊 数据可视化",
        "temperature_trend": "🌡️ 温度趋势",
        "temp_humidity": "🌡️💧 温度与湿度",
        "raw_data": "📋 原始数据",
        "no_data": "该设备没有数据",
        "time_label": "时间",
        "temp_label": "温度 (°C)",
        "humidity_label": "湿度 (%)",
        
        # 状态
        "normal": "正常",
        "warning": "警告",
        "alert": "告警",
        "normal_status": "正常状态",
        "warning_status": "警告状态",
        "alert_status": "告警状态",
        "rising": "上升",
        "falling": "下降",
        "stable": "稳定",
        
        # 异常类型
        "anomaly_high": "high",
        "anomaly_low": "low",
        "anomaly_type": "类型",
        
        # 表格列名
        "device_id": "设备ID",
        "device_name": "设备名称",
        "location": "位置",
        "readings_count": "读数数量",
        "timestamp_col": "时间",
        "temp_col": "温度",
        "z_score": "Z-score",
        "type_col": "类型",
    },
    "en": {
        # Page titles
        "page_title": "Edge IoT Temperature Analysis System",
        "main_title": "🌡️ Edge IoT Temperature Analysis System",
        
        # Navigation
        "nav": "📊 Navigation",
        "page_overview": "Device Overview",
        "page_detail": "Device Details",
        "page_analysis": "Comprehensive Analysis",
        "page_visualization": "Data Visualization",
        
        # Buttons
        "refresh_data": "🔄 Refresh Data",
        "start_analysis": "Start Analysis",
        "manual_refresh": "Refresh Now",
        
        # Model status
        "model_status": "🤖 Model Status",
        "local_model_loaded": "✅ Local LLM Loaded",
        "openai_connected": "✅ OpenAI Model Connected",
        "model_name": "Model",
        "using_mock_mode": "⚠️ Using Mock Mode (Model Not Loaded)",
        "mock_mode_hint": "Tip: Install llama-cpp-python and ensure model file exists",
        "openai_failed": "⚠️ OpenAI Connection Failed",
        "openai_hint": "Tip: Please check API key and network connection",
        
        # Data info
        "data_info": "📁 Data Information",
        "device_count": "Device Count",
        "total_readings": "Total Readings",
        "last_update": "Last Update",
        
        # Device overview
        "device_overview": "📋 Device Overview",
        "device_list": "Device List",
        "quick_stats": "📊 Quick Statistics",
        "avg_temperature": "Average Temperature",
        "min_temperature": "Min Temperature",
        "max_temperature": "Max Temperature",
        "temperature_range": "Temperature Range",
        "no_devices": "No device data found",
        
        # Device detail
        "device_detail": "🔍 Device Detail Analysis",
        "select_device": "Select Device",
        "statistics": "📈 Statistics",
        "latest_reading": "📡 Latest Reading",
        "time": "Time",
        "temperature": "Temperature",
        "humidity": "Humidity",
        "status": "Status",
        "trend_analysis": "📊 Trend Analysis",
        "current_temp": "Current Temperature",
        "trend": "Trend",
        "volatility": "Volatility",
        "anomaly_detection": "⚠️ Anomaly Detection",
        "anomalies_detected": "Detected {count} anomaly readings",
        "no_anomalies": "✅ No Anomalies Detected",
        "ai_analysis": "🤖 AI Intelligent Analysis",
        "enable_stream": "Enable Streaming Output",
        "stream_hint": "Real-time display of AI analysis generation",
        "generating_analysis": "Generating AI Analysis...",
        "analyzing_data": "Analyzing device data...",
        
        # Comprehensive analysis
        "comprehensive_analysis": "🔬 Comprehensive Analysis",
        "select_analysis_type": "Select Analysis Type",
        "analysis_comprehensive": "Comprehensive Analysis",
        "analysis_anomaly": "Anomaly Analysis",
        "analysis_trend": "Trend Analysis",
        "analysis_recommendation": "Recommendations",
        "select_device_optional": "Select Device (Optional)",
        "all_devices": "All Devices",
        "generating_report": "Generating AI Analysis Report...",
        "date_range_filter": "📅 Date Range Filter",
        "start_date": "Start Date",
        "end_date": "End Date",
        "select_date_range": "Select Date Range (Optional)",
        "use_date_filter": "Enable Date Filter",
        
        # Data visualization
        "data_visualization": "📊 Data Visualization",
        "temperature_trend": "🌡️ Temperature Trend",
        "temp_humidity": "🌡️💧 Temperature & Humidity",
        "raw_data": "📋 Raw Data",
        "no_data": "No data for this device",
        "time_label": "Time",
        "temp_label": "Temperature (°C)",
        "humidity_label": "Humidity (%)",
        
        # Status
        "normal": "Normal",
        "warning": "Warning",
        "alert": "Alert",
        "normal_status": "Normal Status",
        "warning_status": "Warning Status",
        "alert_status": "Alert Status",
        "rising": "Rising",
        "falling": "Falling",
        "stable": "Stable",
        
        # Anomaly types
        "anomaly_high": "high",
        "anomaly_low": "low",
        "anomaly_type": "Type",
        
        # Table columns
        "device_id": "Device ID",
        "device_name": "Device Name",
        "location": "Location",
        "readings_count": "Readings Count",
        "timestamp_col": "Time",
        "temp_col": "Temperature",
        "z_score": "Z-score",
        "type_col": "Type",
    }
}


def get_text(key: str, lang: str = "zh", **kwargs) -> str:
    """
    获取翻译文本
    
    Args:
        key: 翻译键
        lang: 语言代码 ("zh" 或 "en")
        **kwargs: 格式化参数
        
    Returns:
        翻译后的文本
    """
    if lang not in TRANSLATIONS:
        lang = "zh"
    
    text = TRANSLATIONS[lang].get(key, key)
    
    # 支持格式化字符串
    if kwargs:
        try:
            text = text.format(**kwargs)
        except KeyError:
            pass
    
    return text


# 全局语言变量（用于非Streamlit环境）
_global_language = 'zh'

def get_language() -> str:
    """
    从session_state获取当前语言
    
    Returns:
        语言代码 ("zh" 或 "en")
    """
    try:
        import streamlit as st
        if 'language' not in st.session_state:
            st.session_state.language = 'zh'  # 默认中文
        return st.session_state.language
    except (ImportError, RuntimeError):
        # 非Streamlit环境，使用全局变量
        return _global_language


def set_language(lang: str):
    """
    设置当前语言
    
    Args:
        lang: 语言代码 ("zh" 或 "en")
    """
    global _global_language
    if lang in ['zh', 'en']:
        try:
            import streamlit as st
            st.session_state.language = lang
        except (ImportError, RuntimeError):
            # 非Streamlit环境，使用全局变量
            _global_language = lang


def t(key: str, **kwargs) -> str:
    """
    翻译函数（快捷方式）
    
    Args:
        key: 翻译键
        **kwargs: 格式化参数
        
    Returns:
        翻译后的文本
    """
    lang = get_language()
    return get_text(key, lang, **kwargs)

