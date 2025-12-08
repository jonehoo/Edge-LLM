# 数据库集成使用指南

本项目现在支持从MySQL数据库读取温度数据，替代原来的JSON文件方式。

## 功能特性

- ✅ 数据库连接管理
- ✅ 自动创建表结构
- ✅ 定时写入模拟数据
- ✅ 从数据库读取数据
- ✅ 兼容原有JSON文件模式

## 数据库配置

数据库连接信息：
- 主机: `localhost:3306`
- 数据库名: `edge-llm`
- 用户名: `edge-llm`
- 密码: `edge-llm`

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

需要安装的额外依赖：
- `pymysql>=1.1.0` - MySQL数据库连接
- `pyyaml>=6.0` - YAML配置文件支持

### 2. 初始化数据库

首先确保MySQL服务已启动，并且已创建数据库 `edge-llm`。

然后运行初始化脚本创建表结构：

```bash
python scripts/init_database.py
```

这将创建两个表：
- `devices` - 设备信息表
- `readings` - 读数数据表

### 3. 初始化历史数据（可选）

如果需要将现有的JSON数据导入数据库：

```bash
python scripts/data_writer.py --init
```

### 4. 启动定时数据写入服务

启动定时写入服务，持续向数据库写入新的模拟数据：

**Windows (批处理):**
```bash
scripts\start_data_writer.bat
```

**Windows (PowerShell):**
```powershell
.\scripts\start_data_writer.ps1
```

**Linux/Mac:**
```bash
python scripts/data_writer.py --interval 60
```

参数说明：
- `--interval`: 写入间隔（秒），默认60秒
- `--json`: JSON数据文件路径（用于生成模拟数据）

### 5. 配置应用使用数据库

编辑 `config/config.yaml`，将数据源改为数据库：

```yaml
data:
  source: "database"  # 改为 "database"
```

如果使用JSON文件，保持：
```yaml
data:
  source: "json"  # 或删除此配置
```

### 6. 启动Web应用

```bash
python run_web.py
```

或直接使用Streamlit：

```bash
streamlit run web/app.py
```

## 数据库表结构

### devices 表

| 字段 | 类型 | 说明 |
|------|------|------|
| device_id | VARCHAR(50) | 设备ID（主键） |
| device_name | VARCHAR(100) | 设备名称 |
| location | VARCHAR(100) | 设备位置 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

### readings 表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT | 自增主键 |
| device_id | VARCHAR(50) | 设备ID（外键） |
| timestamp | DATETIME | 读数时间 |
| temperature | DECIMAL(5,2) | 温度值 |
| humidity | DECIMAL(5,2) | 湿度值 |
| status | VARCHAR(20) | 状态（normal/warning/alert） |
| created_at | TIMESTAMP | 创建时间 |

## 脚本说明

### init_database.py

数据库初始化脚本，创建必要的表结构。

```bash
python scripts/init_database.py
```

### data_writer.py

数据写入脚本，支持两种模式：

1. **初始化模式** - 一次性写入所有历史数据：
```bash
python scripts/data_writer.py --init
```

2. **持续运行模式** - 定时写入新数据：
```bash
python scripts/data_writer.py --interval 60
```

参数：
- `--json`: JSON数据文件路径（默认: `data/temperature_data.json`）
- `--interval`: 写入间隔秒数（默认: 60）
- `--init`: 初始化模式，写入历史数据后退出

## 代码结构

### 新增文件

- `src/db_connection.py` - 数据库连接管理
- `src/db_data_loader.py` - 数据库数据加载器
- `scripts/init_database.py` - 数据库初始化脚本
- `scripts/data_writer.py` - 数据写入脚本
- `scripts/start_data_writer.bat` - Windows批处理启动脚本
- `scripts/start_data_writer.ps1` - PowerShell启动脚本

### 修改的文件

- `src/analyzer.py` - 支持数据库模式
- `config/config.yaml` - 添加数据库配置
- `requirements.txt` - 添加数据库依赖
- `web/app.py` - 支持从配置读取数据源类型

## 使用建议

1. **开发环境**: 可以使用JSON文件模式，方便测试
2. **生产环境**: 建议使用数据库模式，支持实时数据更新
3. **数据写入**: 建议将 `data_writer.py` 作为后台服务运行
4. **数据备份**: 定期备份数据库，避免数据丢失

## 故障排查

### 连接失败

- 检查MySQL服务是否运行
- 检查数据库连接信息是否正确
- 检查数据库用户权限

### 表不存在

运行初始化脚本：
```bash
python scripts/init_database.py
```

### 数据写入失败

- 检查数据库连接
- 检查设备是否已初始化
- 查看日志文件 `data_writer.log`

## 注意事项

1. 数据库连接信息硬编码在代码中，生产环境建议使用环境变量或配置文件
2. 定时写入服务会持续运行，需要手动停止（Ctrl+C）
3. 建议在生产环境中使用进程管理工具（如 systemd, supervisor）管理数据写入服务

