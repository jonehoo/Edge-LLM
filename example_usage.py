"""
数据模块使用示例
演示如何使用数据加载器和处理器
"""

from src.data_loader import TemperatureDataLoader
from src.data_processor import TemperatureDataProcessor

def main():
    # 初始化
    loader = TemperatureDataLoader("data/temperature_data.json")
    processor = TemperatureDataProcessor(loader)
    
    # 加载数据
    print("=" * 50)
    print("加载数据...")
    data = loader.load_data()
    print(f"数据加载成功，共 {data['metadata']['total_devices']} 个设备")
    
    # 获取所有设备
    print("\n" + "=" * 50)
    print("设备列表:")
    devices = loader.get_all_devices()
    for device in devices:
        print(f"  - {device['device_name']} ({device['device_id']}) - {device['location']}")
    
    # 获取设备统计
    print("\n" + "=" * 50)
    print("设备统计信息 (sensor_001):")
    stats = loader.get_statistics("sensor_001")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # 获取最新读数
    print("\n" + "=" * 50)
    print("最新读数 (sensor_001):")
    latest = loader.get_latest_reading("sensor_001")
    if latest:
        print(f"  时间: {latest['timestamp']}")
        print(f"  温度: {latest['temperature']}°C")
        print(f"  湿度: {latest['humidity']}%")
        print(f"  状态: {latest['status']}")
    
    # 转换为DataFrame
    print("\n" + "=" * 50)
    print("DataFrame 预览 (sensor_001):")
    df = processor.to_dataframe("sensor_001")
    print(df.head())
    
    # 检测异常
    print("\n" + "=" * 50)
    print("异常检测 (sensor_001):")
    anomalies = processor.detect_anomalies("sensor_001")
    if anomalies:
        print(f"检测到 {len(anomalies)} 个异常:")
        for anomaly in anomalies:
            print(f"  - {anomaly['timestamp']}: {anomaly['temperature']}°C "
                  f"(Z-score: {anomaly['z_score']}, 类型: {anomaly['anomaly_type']})")
    else:
        print("  未检测到异常")
    
    # 趋势分析
    print("\n" + "=" * 50)
    print("趋势分析 (sensor_001):")
    trend = processor.get_trend_analysis("sensor_001")
    for key, value in trend.items():
        print(f"  {key}: {value}")
    
    # 准备LLM分析数据
    print("\n" + "=" * 50)
    print("LLM分析摘要 (sensor_001):")
    llm_summary = processor.prepare_for_llm("sensor_001")
    print(llm_summary)
    
    # 所有设备统计
    print("\n" + "=" * 50)
    print("所有设备统计:")
    all_stats = loader.get_statistics()
    for key, value in all_stats.items():
        print(f"  {key}: {value}")

if __name__ == "__main__":
    main()

