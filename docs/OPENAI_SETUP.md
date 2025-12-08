# OpenAI模型配置指南

本项目现在支持使用OpenAI API进行AI分析，可以在配置文件中选择使用本地模型或OpenAI模型。

## 配置说明

### 1. 修改配置文件

编辑 `config/config.yaml`，设置模型类型和相关配置：

#### 使用本地模型（默认）

```yaml
model:
  type: "local"  # 使用本地模型
  path: "models/qwen-0.6b.gguf"
  n_ctx: 2048
  n_threads: 4
```

#### 使用OpenAI模型

```yaml
model:
  type: "openai"  # 使用OpenAI API

openai:
  api_key: "sk-your-api-key-here"  # 填入您的OpenAI API密钥
  model: "gpt-3.5-turbo"  # 可选: "gpt-3.5-turbo", "gpt-4", "gpt-4-turbo-preview" 等
  # base_url: "https://api.openai.com/v1"  # 可选，用于兼容OpenAI API的代理服务
```

### 2. 安装依赖

如果使用OpenAI模型，需要安装openai库：

```bash
pip install openai>=1.0.0
```

或者安装所有依赖：

```bash
pip install -r requirements.txt
```

### 3. 获取OpenAI API密钥

1. 访问 [OpenAI官网](https://platform.openai.com/)
2. 注册/登录账号
3. 进入 API Keys 页面
4. 创建新的API密钥
5. 将密钥复制到配置文件的 `openai.api_key` 字段

## 支持的模型

### OpenAI模型

- `gpt-3.5-turbo` - 推荐，性价比高，速度快
- `gpt-4` - 更强的分析能力，但速度较慢，成本较高
- `gpt-4-turbo-preview` - GPT-4的优化版本
- 其他OpenAI兼容的模型（如果使用代理服务）

### 本地模型

- 任何GGUF格式的模型文件
- 推荐使用量化版本以节省内存

## 使用代理服务

如果您使用兼容OpenAI API的代理服务（如一些国内代理），可以设置 `base_url`：

```yaml
openai:
  api_key: "your-api-key"
  model: "gpt-3.5-turbo"
  base_url: "https://your-proxy-url.com/v1"  # 代理服务地址
```

## 功能对比

| 特性 | 本地模型 | OpenAI模型 |
|------|---------|-----------|
| 速度 | 取决于硬件 | 网络延迟+API响应 |
| 成本 | 免费（硬件成本） | 按token收费 |
| 隐私 | 完全本地，数据不上传 | 数据会发送到OpenAI |
| 质量 | 取决于模型大小 | 通常更好 |
| 离线使用 | ✅ 支持 | ❌ 需要网络 |
| 流式输出 | ✅ 支持 | ✅ 支持 |

## 注意事项

1. **API密钥安全**：
   - 不要将API密钥提交到Git仓库
   - 建议使用环境变量或配置文件（不提交到版本控制）

2. **成本控制**：
   - OpenAI API按token收费，注意控制使用量
   - 建议使用 `gpt-3.5-turbo` 以降低成本
   - 监控API使用情况

3. **网络要求**：
   - 使用OpenAI需要稳定的网络连接
   - 如果网络不稳定，建议使用本地模型

4. **数据隐私**：
   - 使用OpenAI时，数据会发送到OpenAI服务器
   - 如果涉及敏感数据，建议使用本地模型

## 故障排查

### OpenAI连接失败

1. 检查API密钥是否正确
2. 检查网络连接
3. 检查API配额是否用完
4. 查看日志文件获取详细错误信息

### 本地模型加载失败

1. 检查模型文件路径是否正确
2. 检查是否安装了 `llama-cpp-python`
3. 检查模型文件是否完整
4. 检查系统内存是否足够

## 切换模型

修改配置文件后，需要重启Web应用才能生效：

```bash
# 停止当前应用（Ctrl+C）
# 重新启动
python run_web.py
```

或者如果使用Streamlit：

```bash
streamlit run web/app.py
```

## 示例配置

### 完整配置示例（使用OpenAI）

```yaml
# 数据配置
data:
  source: "database"

# 模型配置
model:
  type: "openai"

# OpenAI配置
openai:
  api_key: "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
  model: "gpt-3.5-turbo"

# 其他配置...
```

### 完整配置示例（使用本地模型）

```yaml
# 数据配置
data:
  source: "database"

# 模型配置
model:
  type: "local"
  path: "models/qwen-0.6b.gguf"
  n_ctx: 2048
  n_threads: 4

# 其他配置...
```

