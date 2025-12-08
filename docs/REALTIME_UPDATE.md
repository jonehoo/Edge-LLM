# 实时数据更新方案说明

## 当前实现方案

### 方案1：Streamlit自动刷新（已实现）

**优点：**
- ✅ 实现简单，无需额外依赖
- ✅ 兼容现有Streamlit架构
- ✅ 用户体验良好（可配置刷新间隔）
- ✅ 支持手动刷新

**缺点：**
- ⚠️ 需要整页刷新（不是真正的实时推送）
- ⚠️ 刷新时会短暂中断用户操作

**实现方式：**
- 使用JavaScript的`setTimeout`实现自动刷新
- 提供侧边栏控制开关和刷新间隔设置
- 支持手动刷新按钮

**使用：**
1. 在侧边栏启用"自动刷新"
2. 设置刷新间隔（5-300秒）
3. 页面会自动按设定间隔刷新

---

## 是否需要WebSocket双工协议？

### 评估分析

**WebSocket的优势：**
- ✅ 真正的实时推送，无需整页刷新
- ✅ 双向通信，可以实时推送告警
- ✅ 更好的用户体验（无刷新中断）
- ✅ 可以推送增量数据更新

**WebSocket的劣势：**
- ❌ 需要重构架构（Streamlit不支持WebSocket）
- ❌ 需要独立的WebSocket服务器
- ❌ 需要前端重构（不能直接用Streamlit）
- ❌ 开发和维护成本更高
- ❌ 需要处理连接管理、重连等复杂逻辑

**当前场景分析：**
- 数据更新频率：每60秒一次（可配置）
- 用户需求：查看最新数据、及时告警
- 系统规模：中小型监控系统

### 建议

**对于当前项目，不建议使用WebSocket，原因：**

1. **更新频率不高**：数据每60秒更新一次，30秒的自动刷新已经足够
2. **Streamlit限制**：Streamlit本身不支持WebSocket，需要完全重构
3. **成本效益**：开发WebSocket的成本远高于收益
4. **现有方案已足够**：自动刷新已经能满足实时监控需求

**但如果需要WebSocket，可以考虑以下场景：**
- 数据更新频率很高（秒级或更频繁）
- 需要实时告警推送
- 需要多用户实时协作
- 需要双向控制（从页面控制设备）

---

## 如果确实需要WebSocket方案

如果未来需要更高级的实时更新，可以考虑以下架构：

### 架构设计

```
┌─────────────┐      WebSocket      ┌──────────────┐
│   前端      │◄──────────────────►│ WebSocket    │
│ (React/Vue) │                     │  服务器      │
└─────────────┘                     └──────┬───────┘
                                            │
                                            ▼
                                    ┌──────────────┐
                                    │  FastAPI     │
                                    │  + WebSocket │
                                    └──────┬───────┘
                                           │
                                           ▼
                                    ┌──────────────┐
                                    │   MySQL      │
                                    │   数据库     │
                                    └──────────────┘
```

### 实现步骤

1. **后端**：使用FastAPI + WebSocket
   ```python
   from fastapi import FastAPI, WebSocket
   import asyncio
   
   app = FastAPI()
   
   @app.websocket("/ws")
   async def websocket_endpoint(websocket: WebSocket):
       await websocket.accept()
       while True:
           # 从数据库获取最新数据
           data = get_latest_data()
           await websocket.send_json(data)
           await asyncio.sleep(30)  # 每30秒推送一次
   ```

2. **前端**：使用React/Vue + WebSocket客户端
   ```javascript
   const ws = new WebSocket('ws://localhost:8000/ws');
   ws.onmessage = (event) => {
       const data = JSON.parse(event.data);
       updateUI(data);
   };
   ```

3. **数据推送**：从数据库轮询或使用数据库触发器

### 成本评估

- **开发时间**：2-3周（包括前端重构）
- **维护成本**：中等（需要处理连接管理）
- **性能**：更好（真正的实时推送）

---

## 推荐方案

**当前阶段：使用Streamlit自动刷新**
- 满足实时监控需求
- 开发成本低
- 维护简单

**未来扩展：如果确实需要，再考虑WebSocket**
- 当数据更新频率提高到秒级
- 当需要实时告警推送
- 当需要双向控制功能

---

## 配置说明

在 `config/config.yaml` 中配置自动刷新间隔：

```yaml
web:
  auto_refresh_interval: 30  # 刷新间隔（秒）
```

在Web界面侧边栏可以：
- 启用/禁用自动刷新
- 调整刷新间隔（5-300秒）
- 手动刷新数据

