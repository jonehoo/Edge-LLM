"""
Streamlit Web应用
温度数据分析可视化界面
支持中英文切换
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
from src.i18n import t, get_language, set_language

# 初始化语言（需要在set_page_config之前）
if 'language' not in st.session_state:
    st.session_state.language = 'zh'  # 默认中文

# 页面配置（动态标题）
page_title = t("page_title") if 'language' in st.session_state else "边缘物联网温度分析系统"
st.set_page_config(
    page_title=page_title,
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
    st.markdown(f'<h1 class="main-header">{t("main_title")}</h1>', unsafe_allow_html=True)
    
    # 初始化分析器
    analyzer = init_analyzer()
    
    # 侧边栏
    with st.sidebar:
        st.header(t("nav"))
        
        # 语言切换
        lang_options = {"中文": "zh", "English": "en"}
        current_lang = get_language()
        
        # 页面选择
        page_options = [t("page_overview"), t("page_detail"), t("page_analysis"), t("page_visualization")]
        page = st.radio(
            t("nav"),
            page_options,
            label_visibility="collapsed"
        )
        
        # 语言切换器
        st.divider()
        col1, col2 = st.columns([1, 1])
        with col1:
            st.caption("🌐 Language")
        with col2:
            new_lang_name = st.selectbox(
                "Language",
                options=list(lang_options.keys()),
                index=0 if current_lang == "zh" else 1,
                label_visibility="collapsed",
                key="lang_selector"
            )
            new_lang = lang_options[new_lang_name]
            if new_lang != current_lang:
                set_language(new_lang)
                st.rerun()
        
        st.divider()
        
        # 手动刷新按钮
        if st.button(t("refresh_data"), width='stretch', key="manual_refresh_btn"):
            # 清除缓存以强制刷新
            if hasattr(analyzer.data_loader, 'clear_cache'):
                analyzer.data_loader.clear_cache()
            st.rerun()
        
        st.divider()
        
        # 模型状态
        st.subheader(t("model_status"))
        model_info = analyzer.llm_service.get_model_info()
        if analyzer.llm_service.is_available():
            if model_info['type'] == 'OpenAI':
                st.success(f"{t('openai_connected')} ({model_info['model']})")
            else:
                st.success(t("local_model_loaded"))
                st.caption(f"{t('model_name')}: {Path(model_info['model']).name}")
        else:
            if model_info['type'] == 'OpenAI':
                st.warning(t("openai_failed"))
                st.info(t("openai_hint"))
            else:
                st.warning(t("using_mock_mode"))
                st.info(t("mock_mode_hint"))
        
        st.divider()
        
        # 数据信息
        st.subheader(t("data_info"))
        devices = analyzer.get_device_list()
        st.metric(t("device_count"), len(devices))
        total_readings = sum(d['readings_count'] for d in devices)
        st.metric(t("total_readings"), total_readings)
        
        # 显示最后更新时间
        from datetime import datetime
        st.caption(f"{t('last_update')}: {datetime.now().strftime('%H:%M:%S')}")
    
    # 根据选择的页面显示内容
    if page == t("page_overview"):
        show_device_overview(analyzer)
    elif page == t("page_detail"):
        show_device_detail(analyzer)
    elif page == t("page_analysis"):
        show_comprehensive_analysis(analyzer)
    elif page == t("page_visualization"):
        show_data_visualization(analyzer)

def show_device_overview(analyzer):
    """显示设备概览"""
    st.header(t("device_overview"))
    
    devices = analyzer.get_device_list()
    
    if not devices:
        st.warning(t("no_devices"))
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
    st.subheader(t("device_list"))
    device_data = {
        t("device_id"): [d['device_id'] for d in devices],
        t("device_name"): [d['device_name'] for d in devices],
        t("location"): [d['location'] for d in devices],
        t("readings_count"): [d['readings_count'] for d in devices]
    }
    st.dataframe(device_data, width='stretch', hide_index=True)
    
    # 快速统计
    st.subheader(t("quick_stats"))
    all_stats = analyzer.data_loader.get_statistics()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(t("avg_temperature"), f"{all_stats.get('avg_temperature', 0):.2f}°C")
    with col2:
        st.metric(t("min_temperature"), f"{all_stats.get('min_temperature', 0):.2f}°C")
    with col3:
        st.metric(t("max_temperature"), f"{all_stats.get('max_temperature', 0):.2f}°C")
    with col4:
        st.metric(t("temperature_range"), f"{all_stats.get('temperature_range', 0):.2f}°C")

def show_device_detail(analyzer):
    """显示设备详情"""
    st.header(t("device_detail"))
    
    devices = analyzer.get_device_list()
    if not devices:
        st.warning(t("no_devices"))
        return
    
    # 设备选择
    device_options = {f"{d['device_name']} ({d['device_id']})": d['device_id'] 
                     for d in devices}
    selected_device_name = st.selectbox(t("select_device"), list(device_options.keys()))
    device_id = device_options[selected_device_name]
    
    st.divider()
    
    # 加载分析结果
    with st.spinner(t("analyzing_data")):
        analysis = analyzer.analyze_device(device_id)
    
    # 统计信息
    st.subheader(t("statistics"))
    stats = analysis['statistics']
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(t("avg_temperature"), f"{stats.get('avg_temperature', 0):.2f}°C")
    with col2:
        st.metric(t("min_temperature"), f"{stats.get('min_temperature', 0):.2f}°C")
    with col3:
        st.metric(t("max_temperature"), f"{stats.get('max_temperature', 0):.2f}°C")
    with col4:
        st.metric(t("total_readings"), stats.get('total_readings', 0))
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(t("normal"), stats.get('normal_count', 0), delta=t("normal_status"))
    with col2:
        st.metric(t("warning"), stats.get('warning_count', 0), delta=t("warning_status"), delta_color="inverse")
    with col3:
        st.metric(t("alert"), stats.get('alert_count', 0), delta=t("alert_status"), delta_color="inverse")
    
    # 最新读数
    st.subheader(t("latest_reading"))
    latest = analysis['latest_reading']
    if latest:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(t("time"), latest['timestamp'])
        with col2:
            st.metric(t("temperature"), f"{latest['temperature']}°C")
        with col3:
            st.metric(t("humidity"), f"{latest['humidity']}%")
        with col4:
            status_map = {"normal": t("normal"), "warning": t("warning"), "alert": t("alert")}
            status_emoji = {"normal": "✅", "warning": "⚠️", "alert": "🚨"}.get(latest['status'], "❓")
            st.metric(t("status"), f"{status_emoji} {status_map.get(latest['status'], latest['status'])}")
    
    # 趋势分析
    st.subheader(t("trend_analysis"))
    trend = analysis['trend']
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(t("current_temp"), f"{trend.get('current_temp', 0):.2f}°C")
    with col2:
        trend_text = trend.get('trend', 'N/A')
        # 处理趋势文本翻译
        if trend_text == "上升":
            trend_display = t("rising")
        elif trend_text == "下降":
            trend_display = t("falling")
        elif trend_text == "稳定":
            trend_display = t("stable")
        else:
            trend_display = trend_text
        trend_emoji = "📈" if trend_text == "上升" else "📉" if trend_text == "下降" else "➡️"
        st.metric(t("trend"), f"{trend_emoji} {trend_display}")
    with col3:
        st.metric(t("volatility"), f"{trend.get('volatility', 0):.2f}")
    
    # 异常检测
    if analysis['anomalies_count'] > 0:
        st.subheader(t("anomaly_detection"))
        st.warning(t("anomalies_detected", count=analysis['anomalies_count']))
        anomalies_df = {
            t("timestamp_col"): [a['timestamp'] for a in analysis['anomalies']],
            t("temp_col"): [a['temperature'] for a in analysis['anomalies']],
            t("z_score"): [a['z_score'] for a in analysis['anomalies']],
            t("type_col"): [a['anomaly_type'] for a in analysis['anomalies']]
        }
        st.dataframe(anomalies_df, width='stretch', hide_index=True)
    else:
        st.success(t("no_anomalies"))
    
    # LLM分析（流式输出）
    st.subheader(t("ai_analysis"))
    
    # 添加流式输出选项
    use_stream = st.checkbox(t("enable_stream"), value=True, help=t("stream_hint"))
    
    if use_stream:
        # 流式输出
        analysis_placeholder = st.empty()
        full_text = ""
        
        with st.spinner(t("generating_analysis")):
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
        with st.spinner(t("analyzing_data")):
            analysis = analyzer.analyze_device(device_id)
        st.markdown(analysis['llm_analysis'])

def show_comprehensive_analysis(analyzer):
    """显示综合分析"""
    st.header(t("comprehensive_analysis"))
    
    # 分析类型选择
    analysis_type_options = [t("analysis_comprehensive"), t("analysis_anomaly"), 
                             t("analysis_trend"), t("analysis_recommendation")]
    analysis_type = st.radio(
        t("select_analysis_type"),
        analysis_type_options,
        horizontal=True
    )
    
    # 创建反向映射
    analysis_type_map = {
        t("analysis_comprehensive"): "comprehensive",
        t("analysis_anomaly"): "anomaly",
        t("analysis_trend"): "trend",
        t("analysis_recommendation"): "recommendation"
    }
    
    # 设备选择（可选）
    devices = analyzer.get_device_list()
    device_options = {f"{d['device_name']} ({d['device_id']})": d['device_id'] 
                     for d in devices}
    device_options[t("all_devices")] = None
    
    selected_device_name = st.selectbox(t("select_device_optional"), list(device_options.keys()))
    device_id = device_options[selected_device_name]
    
    # 流式输出选项
    use_stream = st.checkbox(t("enable_stream"), value=True, help=t("stream_hint"))
    
    # 执行分析
    if st.button(t("start_analysis"), type="primary"):
        if device_id:
            if use_stream:
                # 流式输出
                analysis_placeholder = st.empty()
                full_text = ""
                
                with st.spinner(t("generating_report")):
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
                with st.spinner(t("generating_report")):
                    analysis = analyzer.analyze_device(device_id, analysis_type_map[analysis_type])
                    st.markdown(analysis['llm_analysis'])
        else:
            # 所有设备的分析（暂时不支持流式）
            with st.spinner(t("generating_report")):
                all_analysis = analyzer.get_all_devices_analysis()
                st.markdown(all_analysis['llm_analysis'])

def show_data_visualization(analyzer):
    """显示数据可视化"""
    st.header(t("data_visualization"))
    
    devices = analyzer.get_device_list()
    if not devices:
        st.warning(t("no_devices"))
        return
    
    # 设备选择
    device_options = {f"{d['device_name']} ({d['device_id']})": d['device_id'] 
                     for d in devices}
    selected_device_name = st.selectbox(t("select_device"), list(device_options.keys()))
    device_id = device_options[selected_device_name]
    
    # 获取图表数据
    chart_data = analyzer.get_temperature_chart_data(device_id)
    
    if not chart_data['timestamps']:
        st.warning(t("no_data"))
        return
    
    # 温度趋势图
    st.subheader(t("temperature_trend"))
    fig_temp = go.Figure()
    fig_temp.add_trace(go.Scatter(
        x=chart_data['timestamps'],
        y=chart_data['temperatures'],
        mode='lines+markers',
        name=t("temperature"),
        line=dict(color='#1f77b4', width=2),
        marker=dict(size=6)
    ))
    fig_temp.update_layout(
        xaxis_title=t("time_label"),
        yaxis_title=t("temp_label"),
        hovermode='x unified',
        height=400
    )
    st.plotly_chart(fig_temp, width='stretch')
    
    # 温度和湿度双轴图
    if chart_data['humidity']:
        st.subheader(t("temp_humidity"))
        fig_dual = make_subplots(specs=[[{"secondary_y": True}]])
        fig_dual.add_trace(
            go.Scatter(x=chart_data['timestamps'], y=chart_data['temperatures'],
                      name=t("temperature"), line=dict(color='#ff7f0e')),
            secondary_y=False
        )
        fig_dual.add_trace(
            go.Scatter(x=chart_data['timestamps'], y=chart_data['humidity'],
                      name=t("humidity"), line=dict(color='#2ca02c')),
            secondary_y=True
        )
        fig_dual.update_xaxes(title_text=t("time_label"))
        fig_dual.update_yaxes(title_text=t("temp_label"), secondary_y=False)
        fig_dual.update_yaxes(title_text=t("humidity_label"), secondary_y=True)
        fig_dual.update_layout(height=400, hovermode='x unified')
        st.plotly_chart(fig_dual, width='stretch')
    
    # 数据表格
    st.subheader(t("raw_data"))
    df = analyzer.get_dataframe(device_id)
    st.dataframe(df, width='stretch')

if __name__ == "__main__":
    main()

