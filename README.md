# 🌡️ Edge-LLM: 边缘物联网温度分析系统

> **GitHub**: [https://github.com/jonehoo/Edge-LLM](https://github.com/jonehoo/Edge-LLM)

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)

**基于大语言模型的智能温度数据分析系统**

[功能特性](#-功能特性) • [快速开始](#-快速开始) • [文档](#-文档) • [贡献](#-贡献)

[中文](README.md) | [English](README_EN.md)

</div>

<div align="center">
  <img src="image/01.png" alt="Edge-LLM 预览" width="700"/>
  <p><em>Edge-LLM 主界面预览</em></p>
</div>

---

## 📖 项目简介

Edge-LLM 是一个基于大语言模型的边缘物联网温度数据分析系统，集成了本地大模型和 OpenAI API，提供智能化的温度数据分析和可视化功能。

### ✨ 核心亮点

- 🤖 **双模型支持**：支持本地大模型（llama-cpp-python）和 OpenAI API，灵活切换
- 💾 **多数据源**：支持 JSON 文件和 MySQL 数据库，自动重连机制
- 📊 **智能分析**：AI 驱动的温度数据分析，自动生成专业报告
- 🎨 **可视化界面**：基于 Streamlit 的现代化 Web 界面
- 🔍 **异常检测**：基于统计方法的智能异常检测
- 📈 **趋势分析**：多维度趋势分析和预测

## 🚀 功能特性

### 数据处理
- ✅ JSON 文件数据加载
- ✅ MySQL 数据库支持（自动重连）
- ✅ 设备数据查询和统计
- ✅ 时间范围过滤
- ✅ 数据缓存机制

### 数据分析
- ✅ 异常温度检测（Z-score 方法）
- ✅ 趋势分析（移动平均、波动性分析）
- ✅ 统计分析（均值、最值、范围等）
- ✅ 多设备综合分析

### AI 分析
- ✅ 本地大模型集成（llama-cpp-python）
- ✅ OpenAI API 支持
- ✅ 流式输出支持
- ✅ 多种分析类型（综合分析、异常分析、趋势分析、建议方案）
- ✅ 智能报告生成

### Web 界面
- ✅ 设备概览仪表板
- ✅ 设备详情分析
- ✅ 交互式数据可视化（Plotly）
- ✅ 实时数据刷新
- ✅ 响应式设计

## 📁 项目结构

```
edge-llm/
├── config/                 # 配置文件
│   └── config.yaml        # 主配置文件
├── data/                   # 数据文件
│   └── temperature_data.json
├── docs/                   # 文档
│   ├── N_CTX_GUIDE.md     # n_ctx 配置指南
│   ├── OPENAI_SETUP.md    # OpenAI 配置指南
│   ├── REALTIME_UPDATE.md # 实时更新方案
│   └── README_DATABASE.md # 数据库集成指南
├── models/                 # 模型文件
│   └── qwen-0.6b.gguf     # 本地大模型（需自行下载）
├── scripts/                # 脚本工具
│   ├── init_database.py   # 数据库初始化
│   ├── data_writer.py     # 数据写入服务
│   └── start_data_writer.* # 启动脚本
├── src/                    # 源代码
│   ├── analyzer.py        # 综合分析服务
│   ├── data_loader.py     # JSON 数据加载器
│   ├── db_connection.py   # 数据库连接管理
│   ├── db_data_loader.py  # 数据库数据加载器
│   ├── data_processor.py  # 数据处理模块
│   └── llm_service.py     # LLM 服务（本地/OpenAI）
├── web/                    # Web 应用
│   └── app.py             # Streamlit 应用
├── example_usage.py       # 使用示例
├── run_web.py             # Web 启动脚本
├── requirements.txt       # Python 依赖
└── README.md             # 项目说明
```

## 🛠️ 安装

### 环境要求

- Python 3.8+
- 4GB+ RAM（推荐 8GB+）
- MySQL 5.7+（可选，用于数据库模式）

### 1. 克隆项目

```bash
git clone https://github.com/jonehoo/Edge-LLM.git
cd Edge-LLM
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 安装本地大模型支持（可选）

如果需要使用本地大模型：

```bash
# 标准安装
pip install llama-cpp-python

# Windows 预编译版本（推荐）
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu

# 如果未安装，系统会自动使用模拟模式
```

### 4. 下载模型文件（可选）

如果使用本地模型，需要下载 GGUF 格式的模型文件：

```bash
# 将模型文件放置在 models/ 目录下
# 例如：models/qwen-0.6b.gguf
```

**注意**：模型文件较大，需要单独下载。如果模型不存在，系统会自动使用模拟模式。

### 5. 配置数据库（可选）

如果使用数据库模式：

```bash
# 1. 创建数据库
mysql -u root -p
CREATE DATABASE `edge-llm` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 2. 初始化表结构
python scripts/init_database.py

# 3. 导入历史数据（可选）
python scripts/data_writer.py --init
```

## ⚡ 快速开始

### 1. 基本使用

```python
from src.analyzer import TemperatureAnalyzer

# 初始化分析器
analyzer = TemperatureAnalyzer()

# 获取设备列表
devices = analyzer.get_device_list()

# 分析设备
analysis = analyzer.analyze_device("sensor_001")
print(analysis['llm_analysis'])
```

### 2. 运行示例

```bash
python example_usage.py
```

### 3. 启动 Web 应用

```bash
# 方法1：使用启动脚本
python run_web.py

# 方法2：直接使用 Streamlit
streamlit run web/app.py
```

启动后访问：**http://localhost:8501**

## ⚙️ 配置说明

### 初始化配置

首次使用前，需要创建配置文件：

```bash
# 复制示例配置文件
cp config/config.example.yaml config/config.yaml

# 编辑配置文件，填入实际配置
# 注意：不要将包含敏感信息的 config.yaml 提交到 Git
```

编辑 `config/config.yaml` 进行配置：

### 数据源配置

```yaml
data:
  source: "json"  # 或 "database"
  file_path: "data/temperature_data.json"
```

### 数据库配置

```yaml
database:
  host: "localhost"
  port: 3306
  user: "edge-llm"
  password: "edge-llm"
  database: "edge-llm"
  charset: "utf8mb4"
  connect_timeout: 10
  read_timeout: 30
  write_timeout: 30
  max_retries: 3
```

### 模型配置

#### 使用本地模型

```yaml
model:
  type: "local"
  path: "models/qwen-0.6b.gguf"
  n_ctx: 4096      # 上下文窗口大小
  n_threads: 4     # 线程数
```

#### 使用 OpenAI API

```yaml
model:
  type: "openai"

openai:
  api_key: "sk-your-api-key-here"
  model: "gpt-3.5-turbo"
  base_url: "https://api.openai.com/v1"  # 可选，用于代理
```

详细配置说明请参考：
- [n_ctx 配置指南](docs/N_CTX_GUIDE.md)
- [OpenAI 配置指南](docs/OPENAI_SETUP.md)
- [数据库集成指南](docs/README_DATABASE.md)

## 📚 使用示例

### Python API 使用

```python
from src.analyzer import TemperatureAnalyzer

# 初始化（使用数据库）
analyzer = TemperatureAnalyzer(use_database=True)

# 获取设备列表
devices = analyzer.get_device_list()
for device in devices:
    print(f"{device['device_name']}: {device['readings_count']} 条读数")

# 分析单个设备
analysis = analyzer.analyze_device(
    device_id="sensor_001",
    analysis_type="comprehensive"  # comprehensive, anomaly, trend, recommendation
)
print(analysis['llm_analysis'])

# 流式分析
for chunk in analyzer.analyze_device_stream("sensor_001"):
    print(chunk, end='', flush=True)

# 获取图表数据
chart_data = analyzer.get_temperature_chart_data("sensor_001")
```

### 数据加载和处理

```python
from src.data_loader import TemperatureDataLoader
from src.data_processor import TemperatureDataProcessor

# 初始化
loader = TemperatureDataLoader("data/temperature_data.json")
processor = TemperatureDataProcessor(loader)

# 加载数据
data = loader.load_data()

# 获取统计信息
stats = loader.get_statistics("sensor_001")

# 检测异常
anomalies = processor.detect_anomalies("sensor_001", threshold=3.0)

# 趋势分析
trend = processor.get_trend_analysis("sensor_001", window_size=5)

# 转换为 DataFrame
df = processor.to_dataframe("sensor_001")
```

## 📖 API 文档

### TemperatureAnalyzer

综合分析服务，整合数据加载、处理和大模型分析。

```python
analyzer = TemperatureAnalyzer(
    use_database=False,           # 是否使用数据库
    model_type="local",           # 模型类型: "local" 或 "openai"
    model_path="models/qwen-0.6b.gguf",
    openai_api_key=None,          # OpenAI API 密钥
    openai_model="gpt-3.5-turbo",
    n_ctx=4096,                   # 上下文窗口大小
    n_threads=4                   # 线程数
)
```

**主要方法：**
- `get_device_list()` - 获取设备列表
- `analyze_device(device_id, analysis_type)` - 分析设备
- `analyze_device_stream(device_id, analysis_type)` - 流式分析
- `get_device_overview(device_id)` - 获取设备概览
- `get_temperature_chart_data(device_id)` - 获取图表数据
- `get_dataframe(device_id)` - 获取 DataFrame

### LLMService

大模型服务，支持本地模型和 OpenAI。

```python
from src.llm_service import LLMService

llm = LLMService(
    model_type="local",           # 或 "openai"
    model_path="models/qwen-0.6b.gguf",
    n_ctx=4096,
    openai_api_key="sk-...",
    openai_model="gpt-3.5-turbo"
)

# 生成文本
text = llm.generate("分析温度数据...")

# 流式生成
for chunk in llm.generate_stream("分析温度数据..."):
    print(chunk, end='')

# 分析温度数据
analysis = llm.analyze_temperature_data(data_summary, "comprehensive")
```

### DatabaseConnection

数据库连接管理，支持自动重连。

```python
from src.db_connection import DatabaseConnection

db = DatabaseConnection(
    host="localhost",
    port=3306,
    user="edge-llm",
    password="edge-llm",
    database="edge-llm",
    max_retries=3
)

# 执行查询
results = db.execute_query("SELECT * FROM devices")

# 执行更新
db.execute_update("INSERT INTO readings ...")
```

## 🗄️ 数据库集成

### 初始化数据库

```bash
# 1. 创建数据库
mysql -u root -p -e "CREATE DATABASE \`edge-llm\` CHARACTER SET utf8mb4;"

# 2. 初始化表结构
python scripts/init_database.py

# 3. 导入历史数据
python scripts/data_writer.py --init
```

### 启动数据写入服务

```bash
# Windows
scripts\start_data_writer.bat

# Linux/Mac
python scripts/data_writer.py --interval 60
```

详细说明请参考：[数据库集成指南](docs/README_DATABASE.md)

## 🤖 OpenAI 集成

### 配置 OpenAI

1. 获取 API 密钥：访问 [OpenAI Platform](https://platform.openai.com/)
2. 编辑配置文件：

```yaml
model:
  type: "openai"

openai:
  api_key: "sk-your-api-key"
  model: "gpt-3.5-turbo"  # 或 "gpt-4", "gpt-4-turbo-preview" 等
```

3. 重启应用

详细说明请参考：[OpenAI 配置指南](docs/OPENAI_SETUP.md)

## 🎨 Web 界面功能

### 设备概览

设备列表和基本信息展示，快速查看所有设备的状态和统计指标。

<div align="center">
  <img src="image/01.png" alt="设备概览" width="900"/>
  <p><em>设备概览界面 - 显示所有设备的基本信息和快速统计</em></p>
</div>

**功能特点：**
- 设备列表和基本信息
- 快速统计指标
- 设备状态总览

### 设备详情

详细的设备分析页面，包含统计信息、趋势分析、异常检测和 AI 智能分析报告。

<div align="center">
  <img src="image/02.png" alt="设备详情" width="900"/>
  <p><em>设备详情界面 - 统计信息、趋势分析和异常检测</em></p>
</div>

**功能特点：**
- 详细统计信息
- 最新读数展示
- 趋势分析图表
- 异常检测结果
- **AI 智能分析报告**（支持流式输出）

### 综合分析

多种分析类型，支持单设备或所有设备的综合分析，AI 生成专业分析报告。

<div align="center">
  <img src="image/03.png" alt="综合分析" width="900"/>
  <p><em>综合分析界面 - AI 生成的专业分析报告</em></p>
</div>

**功能特点：**
- 综合分析
- 异常分析
- 趋势分析
- 建议方案
- 支持单设备或所有设备

### 数据可视化

交互式数据可视化，使用 Plotly 提供丰富的图表展示。

<div align="center">
  <img src="image/04.png" alt="数据可视化" width="900"/>
  <p><em>数据可视化界面 - 温度趋势图和原始数据表格</em></p>
</div>

**功能特点：**
- 温度趋势图（Plotly）
- 温度与湿度双轴图
- 原始数据表格
- 交互式图表

## 🔧 故障排除

### 模型未加载

**问题**：显示"使用模拟模式"

**解决方案**：
1. 检查模型文件是否存在：`models/qwen-0.6b.gguf`
2. 确认已安装 `llama-cpp-python`：`pip install llama-cpp-python`
3. 检查配置文件中的模型路径是否正确
4. 系统会自动使用模拟模式，基本功能仍然可用

### 数据库连接失败

**问题**：`MySQL server has gone away`

**解决方案**：
1. 检查数据库服务是否运行
2. 检查连接配置是否正确
3. 系统已实现自动重连机制，会自动重试
4. 查看日志文件获取详细错误信息

### OpenAI API 错误

**问题**：OpenAI 连接失败

**解决方案**：
1. 检查 API 密钥是否正确
2. 检查网络连接
3. 检查 API 配额是否用完
4. 如果使用代理，检查 `base_url` 配置

### Web 应用无法启动

**问题**：端口被占用或启动失败

**解决方案**：
```bash
# 使用其他端口
streamlit run web/app.py --server.port 8502

# 检查端口占用
netstat -ano | findstr :8501  # Windows
lsof -i :8501                 # Linux/Mac
```

## 🤝 贡献

欢迎贡献！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 开发指南

- 代码风格：遵循 PEP 8
- 提交信息：使用清晰的提交信息
- 测试：确保新功能有相应的测试
- 文档：更新相关文档

## 📝 许可证

本项目采用 [MIT License](LICENSE) 许可证。

## 🙏 致谢

- [llama-cpp-python](https://github.com/abetlen/llama-cpp-python) - 本地大模型支持
- [Streamlit](https://streamlit.io/) - Web 应用框架
- [Plotly](https://plotly.com/) - 数据可视化
- [PyMySQL](https://github.com/PyMySQL/PyMySQL) - MySQL 数据库连接

## ⚠️ 安全提示

**重要**：在提交代码前，请确保：

1. ✅ 不要提交包含真实 API 密钥的 `config/config.yaml`
2. ✅ 使用 `config/config.example.yaml` 作为模板
3. ✅ 将敏感信息添加到 `.gitignore`
4. ✅ 使用环境变量存储敏感配置（推荐）

```bash
# 推荐：使用环境变量
export OPENAI_API_KEY="your-api-key"
# 或在 .env 文件中（已添加到 .gitignore）
```

## 📧 联系方式

- 项目地址：[GitHub](https://github.com/jonehoo/Edge-LLM)
- 问题反馈：[Issues](https://github.com/jonehoo/Edge-LLM/issues)
- 功能建议：[Discussions](https://github.com/jonehoo/Edge-LLM/discussions)

## ⭐ Star History

如果这个项目对你有帮助，请给一个 Star ⭐

---

<div align="center">

**Made with ❤️ for the IoT community**

[⬆ 回到顶部](#-edge-llm-边缘物联网温度分析系统)

[中文](README.md) | [English](README_EN.md)

</div>
