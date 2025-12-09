# 快速启动指南

## 1. 安装依赖

```bash
pip install -r requirements.txt
```

## 2. 验证安装

运行测试脚本验证所有模块：

```bash
python test_imports.py
```

## 3. 运行示例代码

```bash
python example_usage.py
```

## 4. 启动Web应用

### 方法1：使用启动脚本
```bash
python run_web.py
```

### 方法2：直接使用Streamlit
```bash
streamlit run web/app.py
```

启动后，在浏览器中访问：**http://localhost:8501**

## 5. Web应用功能

### 设备概览
- 查看所有设备的基本信息
- 快速统计指标

### 设备详情
- 详细的设备统计
- 最新读数
- 趋势分析
- 异常检测
- **AI智能分析报告**

### 综合分析
- 选择分析类型（综合分析/异常分析/趋势分析/建议方案）
- 选择设备或所有设备
- 生成AI分析报告

### 数据可视化
- 温度趋势图表
- 温度与湿度双轴图
- 原始数据表格

## 6. 使用Python API

```python
from src.analyzer import TemperatureAnalyzer

# 初始化
analyzer = TemperatureAnalyzer()

# 获取设备列表
devices = analyzer.get_device_list()

# 分析设备
analysis = analyzer.analyze_device("sensor_001")
print(analysis['llm_analysis'])

# 获取图表数据
chart_data = analyzer.get_temperature_chart_data("sensor_001")
```

## 注意事项

1. **模型文件**：如果 `models/qwen-0.6b.gguf` 不存在，LLM服务会自动使用模拟模式
2. **数据文件**：确保 `data/temperature_data.json` 存在
3. **编码问题**：Windows系统如果遇到编码问题，确保终端支持UTF-8

## 故障排除

### 模型未加载
- 检查模型文件路径是否正确
- 确认已安装 `llama-cpp-python`
- 系统会自动使用模拟模式，功能仍然可用

### Web应用无法启动
- 确认已安装 `streamlit`
- 检查端口8501是否被占用
- 尝试使用其他端口：`streamlit run web/app.py --server.port 8502`

### 导入错误
- 确保在项目根目录运行脚本
- 检查Python路径设置
- 运行 `python test_imports.py` 诊断问题




