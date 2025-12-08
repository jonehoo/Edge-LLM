"""
Streamlit Web应用
温度数据分析可视化界面
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.analyzer import TemperatureAnalyzer

# 页面配置
st.set_page_config(
    page_title="边缘物联网温度分析系统",
    page_icon="🌡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .stAlert {
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# 初始化分析器（使用缓存，但允许刷新）
@st.cache_resource
def init_analyzer():
    """初始化分析器（缓存）"""
    import yaml
    from pathlib import Path
    
    # 读取配置文件
    config_path = Path(__file__).parent.parent / "config" / "config.yaml"
    use_database = False
    model_type = "local"
    model_path = "models/qwen-0.6b.gguf"
    n_ctx = 2048
    n_threads = 4
    openai_api_key = None
    openai_model = "gpt-3.5-turbo"
    openai_base_url = None
    
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            
            # 数据源配置
            data_config = config.get('data', {})
            use_database = data_config.get('source', 'json') == 'database'
            
            # 模型配置
            model_config = config.get('model', {})
            model_type = model_config.get('type', 'local')
            model_path = model_config.get('path', 'models/qwen-0.6b.gguf')
            n_ctx = model_config.get('n_ctx', 2048)
            n_threads = model_config.get('n_threads', 4)
            
            # OpenAI配置
            openai_config = config.get('openai', {})
            openai_api_key = openai_config.get('api_key')
            openai_model = openai_config.get('model', 'gpt-3.5-turbo')
            openai_base_url = openai_config.get('base_url')
    
    return TemperatureAnalyzer(
        use_database=use_database,
        model_type=model_type,
        model_path=model_path,
        n_ctx=n_ctx,
        n_threads=n_threads,
        openai_api_key=openai_api_key,
        openai_model=openai_model,
        openai_base_url=openai_base_url
    )


# 主应用
def main():
    # 标题
    st.markdown('<h1 class="main-header">🌡️ 边缘物联网温度分析系统</h1>', unsafe_allow_html=True)
    
    # 初始化分析器
    analyzer = init_analyzer()
    
    # 侧边栏
    with st.sidebar:
        st.header("📊 导航")
        
        page = st.radio(
            "选择页面",
            ["设备概览", "设备详情", "综合分析", "数据可视化"],
            label_visibility="collapsed"
        )
        
        st.divider()
        
        # 手动刷新按钮
        if st.button("🔄 刷新数据", width='stretch', key="manual_refresh_btn"):
            # 清除缓存以强制刷新
            if hasattr(analyzer.data_loader, 'clear_cache'):
                analyzer.data_loader.clear_cache()
            st.rerun()
        
        st.divider()
        
        # 模型状态
        st.subheader("🤖 模型状态")
        model_info = analyzer.llm_service.get_model_info()
        if analyzer.llm_service.is_available():
            if model_info['type'] == 'OpenAI':
                st.success(f"✅ OpenAI模型已连接 ({model_info['model']})")
            else:
                st.success(f"✅ 本地大模型已加载")
                st.caption(f"模型: {Path(model_info['model']).name}")
        else:
            if model_info['type'] == 'OpenAI':
                st.warning("⚠️ OpenAI连接失败")
                st.info("提示：请检查API密钥和网络连接")
            else:
                st.warning("⚠️ 使用模拟模式（模型未加载）")
                st.info("提示：安装llama-cpp-python并确保模型文件存在")
        
        st.divider()
        
        # 数据信息
        st.subheader("📁 数据信息")
        devices = analyzer.get_device_list()
        st.metric("设备数量", len(devices))
        total_readings = sum(d['readings_count'] for d in devices)
        st.metric("总读数", total_readings)
        
        # 显示最后更新时间
        from datetime import datetime
        st.caption(f"最后更新: {datetime.now().strftime('%H:%M:%S')}")
    
    # 根据选择的页面显示内容
    if page == "设备概览":
        show_device_overview(analyzer)
    elif page == "设备详情":
        show_device_detail(analyzer)
    elif page == "综合分析":
        show_comprehensive_analysis(analyzer)
    elif page == "数据可视化":
        show_data_visualization(analyzer)

def show_device_overview(analyzer):
    """显示设备概览"""
    st.header("📋 设备概览")
    
    devices = analyzer.get_device_list()
    
    if not devices:
        st.warning("没有找到设备数据")
        return
    
    # 设备卡片
    cols = st.columns(len(devices))
    for idx, device in enumerate(devices):
        with cols[idx]:
            st.metric(
                label=device['device_name'],
                value=device['readings_count'],
                delta=f"{device['location']}"
            )
    
    st.divider()
    
    # 设备列表表格
    st.subheader("设备列表")
    device_data = {
        '设备ID': [d['device_id'] for d in devices],
        '设备名称': [d['device_name'] for d in devices],
        '位置': [d['location'] for d in devices],
        '读数数量': [d['readings_count'] for d in devices]
    }
    st.dataframe(device_data, width='stretch', hide_index=True)
    
    # 快速统计
    st.subheader("📊 快速统计")
    all_stats = analyzer.data_loader.get_statistics()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("平均温度", f"{all_stats.get('avg_temperature', 0):.2f}°C")
    with col2:
        st.metric("最低温度", f"{all_stats.get('min_temperature', 0):.2f}°C")
    with col3:
        st.metric("最高温度", f"{all_stats.get('max_temperature', 0):.2f}°C")
    with col4:
        st.metric("温度范围", f"{all_stats.get('temperature_range', 0):.2f}°C")

def show_device_detail(analyzer):
    """显示设备详情"""
    st.header("🔍 设备详情分析")
    
    devices = analyzer.get_device_list()
    if not devices:
        st.warning("没有找到设备数据")
        return
    
    # 设备选择
    device_options = {f"{d['device_name']} ({d['device_id']})": d['device_id'] 
                     for d in devices}
    selected_device_name = st.selectbox("选择设备", list(device_options.keys()))
    device_id = device_options[selected_device_name]
    
    st.divider()
    
    # 加载分析结果
    with st.spinner("正在分析设备数据..."):
        analysis = analyzer.analyze_device(device_id)
    
    # 统计信息
    st.subheader("📈 统计信息")
    stats = analysis['statistics']
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("平均温度", f"{stats.get('avg_temperature', 0):.2f}°C")
    with col2:
        st.metric("最低温度", f"{stats.get('min_temperature', 0):.2f}°C")
    with col3:
        st.metric("最高温度", f"{stats.get('max_temperature', 0):.2f}°C")
    with col4:
        st.metric("总读数", stats.get('total_readings', 0))
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("正常", stats.get('normal_count', 0), delta="正常状态")
    with col2:
        st.metric("警告", stats.get('warning_count', 0), delta="警告状态", delta_color="inverse")
    with col3:
        st.metric("告警", stats.get('alert_count', 0), delta="告警状态", delta_color="inverse")
    
    # 最新读数
    st.subheader("📡 最新读数")
    latest = analysis['latest_reading']
    if latest:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("时间", latest['timestamp'])
        with col2:
            st.metric("温度", f"{latest['temperature']}°C")
        with col3:
            st.metric("湿度", f"{latest['humidity']}%")
        with col4:
            status_emoji = {"normal": "✅", "warning": "⚠️", "alert": "🚨"}.get(latest['status'], "❓")
            st.metric("状态", f"{status_emoji} {latest['status']}")
    
    # 趋势分析
    st.subheader("📊 趋势分析")
    trend = analysis['trend']
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("当前温度", f"{trend.get('current_temp', 0):.2f}°C")
    with col2:
        trend_emoji = "📈" if trend.get('trend') == "上升" else "📉" if trend.get('trend') == "下降" else "➡️"
        st.metric("趋势", f"{trend_emoji} {trend.get('trend', 'N/A')}")
    with col3:
        st.metric("波动性", f"{trend.get('volatility', 0):.2f}")
    
    # 异常检测
    if analysis['anomalies_count'] > 0:
        st.subheader("⚠️ 异常检测")
        st.warning(f"检测到 {analysis['anomalies_count']} 个异常读数")
        anomalies_df = {
            '时间': [a['timestamp'] for a in analysis['anomalies']],
            '温度': [a['temperature'] for a in analysis['anomalies']],
            'Z-score': [a['z_score'] for a in analysis['anomalies']],
            '类型': [a['anomaly_type'] for a in analysis['anomalies']]
        }
        st.dataframe(anomalies_df, width='stretch', hide_index=True)
    else:
        st.success("✅ 未检测到异常")
    
    # LLM分析（流式输出）
    st.subheader("🤖 AI智能分析")
    
    # 添加流式输出选项
    use_stream = st.checkbox("启用流式输出", value=True, help="实时显示AI分析生成过程")
    
    if use_stream:
        # 流式输出
        analysis_placeholder = st.empty()
        full_text = ""
        
        with st.spinner("正在生成AI分析..."):
            for chunk in analyzer.analyze_device_stream(device_id, "comprehensive"):
                full_text += chunk
                analysis_placeholder.markdown(full_text)
        
        # 完成后进行后处理
        from src.llm_service import LLMService
        temp_llm = LLMService()
        cleaned_text = temp_llm._remove_repetition(full_text)
        cleaned_text = temp_llm._clean_prompt_artifacts(cleaned_text)
        analysis_placeholder.markdown(cleaned_text)
    else:
        # 传统方式（一次性输出）
        with st.spinner("正在分析设备数据..."):
            analysis = analyzer.analyze_device(device_id)
        st.markdown(analysis['llm_analysis'])

def show_comprehensive_analysis(analyzer):
    """显示综合分析"""
    st.header("🔬 综合分析")
    
    # 分析类型选择
    analysis_type = st.radio(
        "选择分析类型",
        ["综合分析", "异常分析", "趋势分析", "建议方案"],
        horizontal=True
    )
    
    analysis_type_map = {
        "综合分析": "comprehensive",
        "异常分析": "anomaly",
        "趋势分析": "trend",
        "建议方案": "recommendation"
    }
    
    # 设备选择（可选）
    devices = analyzer.get_device_list()
    device_options = {f"{d['device_name']} ({d['device_id']})": d['device_id'] 
                     for d in devices}
    device_options["所有设备"] = None
    
    selected_device_name = st.selectbox("选择设备（可选）", list(device_options.keys()))
    device_id = device_options[selected_device_name]
    
    # 流式输出选项
    use_stream = st.checkbox("启用流式输出", value=True, help="实时显示AI分析生成过程")
    
    # 执行分析
    if st.button("开始分析", type="primary"):
        if device_id:
            if use_stream:
                # 流式输出
                analysis_placeholder = st.empty()
                full_text = ""
                
                with st.spinner("正在生成AI分析报告..."):
                    for chunk in analyzer.analyze_device_stream(device_id, analysis_type_map[analysis_type]):
                        full_text += chunk
                        analysis_placeholder.markdown(full_text)
                
                # 后处理
                from src.llm_service import LLMService
                temp_llm = LLMService()
                cleaned_text = temp_llm._remove_repetition(full_text)
                cleaned_text = temp_llm._clean_prompt_artifacts(cleaned_text)
                analysis_placeholder.markdown(cleaned_text)
            else:
                # 传统方式
                with st.spinner("正在生成AI分析报告..."):
                    analysis = analyzer.analyze_device(device_id, analysis_type_map[analysis_type])
                    st.markdown(analysis['llm_analysis'])
        else:
            # 所有设备的分析（暂时不支持流式）
            with st.spinner("正在生成AI分析报告..."):
                all_analysis = analyzer.get_all_devices_analysis()
                st.markdown(all_analysis['llm_analysis'])

def show_data_visualization(analyzer):
    """显示数据可视化"""
    st.header("📊 数据可视化")
    
    devices = analyzer.get_device_list()
    if not devices:
        st.warning("没有找到设备数据")
        return
    
    # 设备选择
    device_options = {f"{d['device_name']} ({d['device_id']})": d['device_id'] 
                     for d in devices}
    selected_device_name = st.selectbox("选择设备", list(device_options.keys()))
    device_id = device_options[selected_device_name]
    
    # 获取图表数据
    chart_data = analyzer.get_temperature_chart_data(device_id)
    
    if not chart_data['timestamps']:
        st.warning("该设备没有数据")
        return
    
    # 温度趋势图
    st.subheader("🌡️ 温度趋势")
    fig_temp = go.Figure()
    fig_temp.add_trace(go.Scatter(
        x=chart_data['timestamps'],
        y=chart_data['temperatures'],
        mode='lines+markers',
        name='温度',
        line=dict(color='#1f77b4', width=2),
        marker=dict(size=6)
    ))
    fig_temp.update_layout(
        xaxis_title="时间",
        yaxis_title="温度 (°C)",
        hovermode='x unified',
        height=400
    )
    st.plotly_chart(fig_temp, width='stretch')
    
    # 温度和湿度双轴图
    if chart_data['humidity']:
        st.subheader("🌡️💧 温度与湿度")
        fig_dual = make_subplots(specs=[[{"secondary_y": True}]])
        fig_dual.add_trace(
            go.Scatter(x=chart_data['timestamps'], y=chart_data['temperatures'],
                      name="温度", line=dict(color='#ff7f0e')),
            secondary_y=False
        )
        fig_dual.add_trace(
            go.Scatter(x=chart_data['timestamps'], y=chart_data['humidity'],
                      name="湿度", line=dict(color='#2ca02c')),
            secondary_y=True
        )
        fig_dual.update_xaxes(title_text="时间")
        fig_dual.update_yaxes(title_text="温度 (°C)", secondary_y=False)
        fig_dual.update_yaxes(title_text="湿度 (%)", secondary_y=True)
        fig_dual.update_layout(height=400, hovermode='x unified')
        st.plotly_chart(fig_dual, width='stretch')
    
    # 数据表格
    st.subheader("📋 原始数据")
    df = analyzer.get_dataframe(device_id)
    st.dataframe(df, width='stretch')

if __name__ == "__main__":
    main()

