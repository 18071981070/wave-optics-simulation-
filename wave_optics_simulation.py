import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import pandas as pd
from io import BytesIO
import json
import time

matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS']
matplotlib.rcParams['axes.unicode_minus'] = False

from optical_calculator import OpticalCalculator
from visualization import WaveOpticsVisualizer
from parameter_validation import ParameterValidator
from teaching_module import TeachingModule
from exercise_module import ExerciseModule
from agent_module import PhysicsAgent

st.set_page_config(
    page_title="波动光学交互式仿真平台",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* 精致优雅主题 - 清新现代风 */
    :root {
        --primary: #667eea;
        --primary-light: #764ba2;
        --secondary: #f093fb;
        --accent: #f5576c;
        --bg-main: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --bg-card: rgba(255, 255, 255, 0.95);
        --bg-sidebar: rgba(255, 255, 255, 0.98);
        --text-primary: #2d3748;
        --text-secondary: #4a5568;
        --text-light: #718096;
        --border: rgba(255, 255, 255, 0.3);
    }

    .stApp {
        background: var(--bg-main) !important;
        color: var(--text-primary);
        min-height: 100vh;
    }

    [data-testid="stSidebar"] {
        background: var(--bg-sidebar) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.2);
    }

    [data-testid="stSidebar"] * {
        color: var(--text-primary) !important;
    }

    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: var(--text-primary) !important;
    }

    .main-header {
        font-size: 2.5rem;
        font-weight: 800;
        text-align: center;
        background: linear-gradient(135deg, #ffffff 0%, #e0e7ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
        text-shadow: 0 2px 10px rgba(255, 255, 255, 0.3);
    }

    .sub-header {
        font-size: 1rem;
        color: rgba(255, 255, 255, 0.9);
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 500;
        letter-spacing: 0.05em;
    }

    .card {
        background: var(--bg-card);
        border-radius: 20px;
        padding: 24px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.5);
        backdrop-filter: blur(10px);
    }

    .metric-card {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(236, 72, 153, 0.1) 100%);
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.5);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
    }

    .metric-card h3 {
        color: #7c3aed !important;
        font-weight: 700;
        font-size: 0.9rem;
        margin: 0;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }

    .metric-card .metric-value {
        color: #667eea !important;
        font-size: 1.8rem;
        font-weight: 800;
        margin: 8px 0 0 0;
    }

    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 14px 32px;
        font-weight: 700;
        font-size: 1rem;
        letter-spacing: 0.03em;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        transition: all 0.3s ease;
    }

    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.5);
    }

    .stTabs [data-baseweb="tab-list"] {
        background: rgba(255, 255, 255, 0.5);
        border-radius: 16px;
        padding: 8px;
        gap: 6px;
        border: 1px solid rgba(255, 255, 255, 0.5);
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 12px;
        font-weight: 700;
        padding: 14px 28px;
        color: var(--text-secondary);
        font-size: 0.95rem;
        letter-spacing: 0.02em;
        transition: all 0.3s ease;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(102, 126, 234, 0.1);
        color: #667eea;
    }

    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }

    .stExpander {
        background: var(--bg-card);
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.5);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    }

    div[data-testid="stMetric"] {
        background: var(--bg-card);
        padding: 20px;
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.5);
        text-align: center;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
    }

    div[data-testid="stMetric"] label {
        color: var(--text-secondary) !important;
        font-weight: 700;
        font-size: 0.9rem;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }

    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #667eea !important;
        font-weight: 800;
        font-size: 1.5rem;
    }

    .stSelectbox label,
    .stSlider label,
    .stNumberInput label {
        color: var(--text-primary) !important;
        font-weight: 700;
        font-size: 0.95rem;
        letter-spacing: 0.02em;
    }

    .info-box {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        padding: 20px 24px;
        border-radius: 16px;
        border-left: 5px solid #667eea;
        color: #4c51bf;
        font-size: 1rem;
        font-weight: 600;
        line-height: 1.7;
        border: 1px solid rgba(102, 126, 234, 0.2);
    }

    .success-box {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(16, 185, 129, 0.05) 100%);
        padding: 20px 24px;
        border-radius: 16px;
        border-left: 5px solid #10b981;
        color: #047857;
        font-size: 1rem;
        font-weight: 600;
        line-height: 1.7;
        border: 1px solid rgba(16, 185, 129, 0.2);
    }

    .warning-box {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(245, 158, 11, 0.05) 100%);
        padding: 20px 24px;
        border-radius: 16px;
        border-left: 5px solid #f59e0b;
        color: #b45309;
        font-size: 1rem;
        font-weight: 600;
        line-height: 1.7;
        border: 1px solid rgba(245, 158, 11, 0.2);
    }

    .formula-box {
        background: linear-gradient(135deg, #fafafa 0%, #f5f5f5 100%);
        padding: 24px;
        border-radius: 16px;
        border: 2px solid #e2e8f0;
        font-family: 'Georgia', serif;
        font-size: 1.3em;
        color: var(--text-primary);
        text-align: center;
        font-weight: 500;
        line-height: 1.8;
    }

    .chat-container {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 20px;
        padding: 24px;
        max-height: 450px;
        overflow-y: auto;
        border: 1px solid rgba(255, 255, 255, 0.5);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    }

    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 16px 24px;
        border-radius: 20px 20px 8px 20px;
        margin: 16px 0;
        max-width: 85%;
        margin-left: auto;
        font-size: 1.05rem;
        font-weight: 500;
        line-height: 1.7;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }

    .assistant-message {
        background: white;
        color: var(--text-primary);
        padding: 16px 24px;
        border-radius: 20px 20px 20px 8px;
        margin: 16px 0;
        max-width: 85%;
        border: 1px solid #e2e8f0;
        font-size: 1.05rem;
        font-weight: 500;
        line-height: 1.7;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
    }

    .feature-badge {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 10px 20px;
        border-radius: 25px;
        font-size: 0.9rem;
        font-weight: 700;
        display: inline-block;
        letter-spacing: 0.03em;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }

    .section-title {
        font-size: 1.4rem;
        font-weight: 800;
        color: var(--text-primary);
        margin-bottom: 1.2rem;
        padding-bottom: 0.8rem;
        border-bottom: 3px solid #667eea;
        display: inline-block;
        letter-spacing: 0.02em;
    }

    .intro-card {
        background: var(--bg-card);
        border-radius: 20px;
        padding: 28px;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.5);
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.12);
        transition: all 0.4s ease;
    }

    .intro-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
    }

    .intro-icon {
        font-size: 3rem;
        margin-bottom: 16px;
    }

    .intro-title {
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 10px;
        font-size: 1.15rem;
        letter-spacing: 0.03em;
    }

    .intro-desc {
        font-size: 0.95rem;
        color: var(--text-secondary);
        line-height: 1.7;
    }

    .agent-section {
        background: linear-gradient(135deg, rgba(240, 147, 251, 0.15) 0%, rgba(245, 87, 108, 0.1) 100%);
        border-radius: 20px;
        padding: 28px;
        border: 1px solid rgba(240, 147, 251, 0.3);
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
    }

    p, span, div, li, td, th {
        letter-spacing: 0.01em;
        line-height: 1.6;
    }

    h1, h2, h3, h4, h5, h6 {
        letter-spacing: 0.02em;
        line-height: 1.4;
    }

    .stSlider span {
        font-weight: 600;
    }

    [data-testid="stSidebarNav"] {
        background: transparent !important;
    }

    .stSelectbox > div > div {
        background: white !important;
        border-radius: 12px !important;
        border: 1px solid #e2e8f0 !important;
    }

    .stSlider > div > div > div {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    }

    div[data-testid="stRadio"] > div {
        background: white !important;
        padding: 12px 16px;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-header">🔬 波动光学交互式仿真平台</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">精准复现波动光学核心物理现象 | 衔接理论与实验 | 赋能分层教学与科研启蒙</p>', unsafe_allow_html=True)

with st.expander("📋 平台功能介绍", expanded=True):
    col_intro1, col_intro2, col_intro3, col_intro4 = st.columns(4)
    with col_intro1:
        st.markdown("""
        <div class="feature-card">
            <h4>🔭 6大光学实验</h4>
            <p>双缝干涉、单缝衍射、多缝光栅、迈克耳孙干涉、薄膜干涉、偏振干涉</p>
        </div>
        """, unsafe_allow_html=True)
    with col_intro2:
        st.markdown("""
        <div class="feature-card">
            <h4>⚙️ 精准物理模型</h4>
            <p>误差控制在1%以内，基于波动光学核心理论公式</p>
        </div>
        """, unsafe_allow_html=True)
    with col_intro3:
        st.markdown("""
        <div class="feature-card">
            <h4>📊 误差分析系统</h4>
            <p>模拟系统误差、随机误差、环境光干扰等真实实验条件</p>
        </div>
        """, unsafe_allow_html=True)
    with col_intro4:
        st.markdown("""
        <div class="feature-card">
            <h4>📚 教学与练习</h4>
            <p>分层教学指导、基础/进阶/创新习题、答案解析</p>
        </div>
        """, unsafe_allow_html=True)

calculator = OpticalCalculator()
visualizer = WaveOpticsVisualizer()
validator = ParameterValidator()
teaching = TeachingModule()
exercise = ExerciseModule()

# 初始化智能体（使用session_state保持状态）
if 'agent' not in st.session_state:
    st.session_state.agent = PhysicsAgent()

agent = st.session_state.agent

st.sidebar.markdown("## 🎛️ 实验选择")

experiment_mode = st.sidebar.selectbox(
    "选择实验",
    ["双缝干涉", "单缝衍射", "多缝光栅", "迈克耳孙干涉", "薄膜干涉", "偏振干涉"]
)

mode_type = st.sidebar.radio(
    "模式",
    ["实验模式", "教学模式", "练习模式"],
    help="实验模式：自由探索 | 教学模式：分步指导 | 练习模式：自我评估"
)

st.sidebar.markdown("## 🎨 可视化选项")

color_scheme = st.sidebar.selectbox(
    "配色方案",
    ["viridis", "plasma", "inferno", "magma", "cividis", "coolwarm", "gray"],
    index=0
)

show_3d = st.sidebar.checkbox("显示3D视图", value=False)
show_phase = st.sidebar.checkbox("显示相位信息", value=False)
show_path_diff = st.sidebar.checkbox("显示光程差曲线", value=False)

st.sidebar.markdown("## ⚠️ 误差设置")
enable_error = st.sidebar.checkbox("启用误差模拟", value=False)
if enable_error:
    systematic_error = st.sidebar.slider("系统误差 (%)", 0, 10, 2) / 100
    random_error = st.sidebar.slider("随机误差标准差", 0.0, 0.1, 0.02)
    ambient_light = st.sidebar.slider("环境光强度", 0.0, 0.1, 0.0)
    detector_noise = st.sidebar.slider("探测器噪声", 0.0, 0.05, 0.0)

st.sidebar.markdown("## 🔄 快捷操作")
if st.sidebar.button("一键重置参数"):
    st.session_state.clear()
    st.experimental_rerun()

st.markdown("---")

col1, col2 = st.columns([1, 2])

intensity = None
phase_diff = None
info = None
original_intensity = None
noise_info = None

with col1:
    st.markdown("### ⚙️ 参数设置")

    if experiment_mode == "双缝干涉":
        wavelength = st.slider("波长 (nm)", 400, 760, 540, 10, help="可见光范围：400-760nm") * 1e-9
        slit_distance = st.slider("缝距 (mm)", 0.1, 1.0, 0.5, 0.05, help="双缝之间的距离") * 1e-3
        screen_distance = st.slider("屏距 (m)", 1.0, 5.0, 1.0, 0.1, help="双缝到屏幕的距离")
        refractive_index = st.slider("介质折射率", 1.0, 1.5, 1.0, 0.05, help="光传播介质的折射率")
        polarization_angle = st.slider("偏振角 (°)", 0, 90, 0, 5, help="线偏振光的偏振方向")
        incident_angle = st.slider("入射角 (°)", -30, 30, 0, 1, help="入射光与法线的夹角")
        coherence = st.slider("光源相干性", 0.5, 1.0, 1.0, 0.05, help="0为完全非相干，1为完全相干")
        slit_width_uniformity = st.slider("缝宽均匀度", 0.5, 1.0, 1.0, 0.05, help="1为完全均匀")
        
        fringe_spacing_ref = wavelength * screen_distance / slit_distance / refractive_index
        screen_width = fringe_spacing_ref * 8
        
        x, original_intensity, phase_diff, info = calculator.double_slit_interference(
            wavelength=wavelength,
            slit_distance=slit_distance,
            screen_distance=screen_distance,
            screen_width=screen_width,
            refractive_index=refractive_index,
            polarization_angle=np.radians(polarization_angle),
            incident_angle=np.radians(incident_angle),
            coherence=coherence,
            slit_width_uniformity=slit_width_uniformity
        )
        
        if enable_error:
            intensity, noise_info = calculator.add_noise(
                original_intensity, systematic_error, random_error, 
                ambient_light=ambient_light, detector_noise=detector_noise
            )
        else:
            intensity = original_intensity

        st.markdown("#### 📐 实时物理量")
        st.write(f"**条纹间距**: {info['fringe_spacing']*1000:.4f} mm")
        st.write(f"**理论条纹间距**: {info['theoretical_fringe_spacing']*1000:.4f} mm")
        st.write(f"**对比度**: {info['contrast']:.4f}")
        st.write(f"**有效波长**: {info['effective_wavelength']*1e9:.1f} nm")
        st.write(f"**相对误差**: {info['relative_error']:.2f}%")

    elif experiment_mode == "单缝衍射":
        wavelength = st.slider("波长 (nm)", 400, 760, 600, 10) * 1e-9
        slit_width = st.slider("缝宽 (mm)", 0.02, 0.5, 0.1, 0.01) * 1e-3
        screen_distance = st.slider("屏距 (m)", 1.0, 5.0, 1.0, 0.1)
        refractive_index = st.slider("介质折射率", 1.0, 1.5, 1.0, 0.05)
        incident_angle = st.slider("入射角 (°)", -30, 30, 0, 1)
        slit_width_uniformity = st.slider("缝宽均匀度", 0.5, 1.0, 1.0, 0.05)
        
        first_min_angle_ref = np.arcsin(wavelength / slit_width)
        central_width_ref = 2 * screen_distance * np.tan(first_min_angle_ref)
        screen_width = central_width_ref * 3
        
        x, original_intensity, phase_diff, info = calculator.single_slit_diffraction(
            wavelength=wavelength,
            slit_width=slit_width,
            screen_distance=screen_distance,
            screen_width=screen_width,
            refractive_index=refractive_index,
            incident_angle=np.radians(incident_angle),
            slit_width_uniformity=slit_width_uniformity
        )
        
        if enable_error:
            intensity, noise_info = calculator.add_noise(
                original_intensity, systematic_error, random_error,
                ambient_light=ambient_light, detector_noise=detector_noise
            )
        else:
            intensity = original_intensity
        
        st.markdown("#### 📐 实时物理量")
        st.write(f"**第一暗纹角度**: {info['first_min_angle']:.2f}°")
        st.write(f"**中央明纹宽度**: {info['central_max_width']*1000:.3f} mm")
        st.write(f"**半角宽度**: {info['half_angle_width']:.2f}°")
        st.write(f"**相对误差**: {info['relative_error']:.2f}%")

    elif experiment_mode == "多缝光栅":
        wavelength = st.slider("波长 (nm)", 400, 760, 500, 10) * 1e-9
        slit_distance = st.slider("光栅常数 (μm)", 5, 50, 20, 1) * 1e-6
        num_slits = st.slider("缝数", 5, 50, 10, 1)
        slit_width = st.slider("缝宽 (μm)", 1, 25, 10, 1) * 1e-6
        screen_distance = st.slider("屏距 (m)", 1.0, 5.0, 1.0, 0.1)
        refractive_index = st.slider("介质折射率", 1.0, 1.5, 1.0, 0.05)
        incident_angle = st.slider("入射角 (°)", -30, 30, 0, 1)
        
        k_max = int((slit_distance / wavelength) * (1 - np.sin(np.radians(incident_angle))))
        screen_width = wavelength * screen_distance / slit_distance * k_max * 2.5 / refractive_index
        
        x, original_intensity, phase_diff, info = calculator.multi_slit_diffraction(
            wavelength=wavelength,
            slit_distance=slit_distance,
            num_slits=num_slits,
            screen_distance=screen_distance,
            screen_width=screen_width,
            slit_width=slit_width,
            refractive_index=refractive_index,
            incident_angle=np.radians(incident_angle)
        )
        
        if enable_error:
            intensity, noise_info = calculator.add_noise(
                original_intensity, systematic_error, random_error,
                ambient_light=ambient_light, detector_noise=detector_noise
            )
        else:
            intensity = original_intensity
        
        st.markdown("#### 📐 实时物理量")
        st.write(f"**光栅常数**: {slit_distance*1e6:.0f} μm")
        st.write(f"**最大衍射级次**: {info['max_order']}")
        st.write(f"**分辨本领**: {info['resolving_power']}")
        st.write(f"**色散率**: {info['dispersion']*1e12:.2e} rad/m")

    elif experiment_mode == "迈克耳孙干涉":
        wavelength = st.slider("波长 (nm)", 400, 760, 550, 10) * 1e-9
        mirror_displacement = st.slider("镜面移动距离 (μm)", 0.0, 10.0, 2.5, 0.1) * 1e-6
        num_fringes = st.slider("显示条纹数", 10, 100, 50, 10)
        refractive_index = st.slider("介质折射率", 1.0, 1.5, 1.0, 0.05)
        beam_ratio = st.slider("两束光强度比", 0.1, 1.0, 0.5, 0.1)
        
        path_diff, original_intensity, phase_diff, info = calculator.michelson_interferometer(
            wavelength=wavelength,
            mirror_displacement=mirror_displacement,
            num_fringes=num_fringes,
            refractive_index=refractive_index,
            beam_ratio=beam_ratio
        )
        
        if enable_error:
            intensity, noise_info = calculator.add_noise(
                original_intensity, systematic_error, random_error,
                ambient_light=ambient_light, detector_noise=detector_noise
            )
        else:
            intensity = original_intensity
        
        st.markdown("#### 📐 实时物理量")
        st.write(f"**条纹移动数**: {info['fringe_shift']:.2f}")
        st.write(f"**光程差变化**: {info['optical_path_difference']*1e6:.2f} μm")
        st.write(f"**条纹可见度**: {info['fringe_visibility']:.4f}")
        st.write(f"**相对误差**: {info['relative_error']:.2f}%")

    elif experiment_mode == "薄膜干涉":
        wavelength = st.slider("波长 (nm)", 400, 760, 550, 10) * 1e-9
        film_thickness = st.slider("薄膜厚度 (nm)", 100, 2000, 500, 50) * 1e-9
        n_film = st.slider("薄膜折射率", 1.0, 2.0, 1.5, 0.05)
        n_substrate = st.slider("基底折射率", 1.0, 2.0, 1.5, 0.05)
        incident_angle = st.slider("入射角 (°)", 0, 60, 0, 5)
        interference_type = st.radio("干涉类型", ["等厚干涉", "等倾干涉"])
        
        x, original_intensity, phase_diff, info = calculator.thin_film_interference(
            wavelength=wavelength,
            film_thickness=film_thickness,
            n_film=n_film,
            n_substrate=n_substrate,
            incident_angle=np.radians(incident_angle),
            interference_type='equal_thickness' if interference_type == '等厚干涉' else 'equal_inclination'
        )
        
        if enable_error:
            intensity, noise_info = calculator.add_noise(
                original_intensity, systematic_error, random_error,
                ambient_light=ambient_light, detector_noise=detector_noise
            )
        else:
            intensity = original_intensity
        
        st.markdown("#### 📐 实时物理量")
        st.write(f"**薄膜厚度**: {film_thickness*1e9:.0f} nm")
        st.write(f"**薄膜折射率**: {n_film:.3f}")
        st.write(f"**干涉类型**: {info['interference_type']}")
        st.write(f"**相位突变**: {'π' if info['phase_shift'] > 0 else '0'}")

    elif experiment_mode == "偏振干涉":
        wavelength = st.slider("波长 (nm)", 400, 760, 550, 10) * 1e-9
        polarizer_angle = st.slider("起偏器角度 (°)", 0, 180, 0, 5)
        analyzer_angle = st.slider("检偏器角度 (°)", 0, 180, 90, 5)
        waveplate_angle = st.slider("波片角度 (°)", 0, 180, 45, 5)
        waveplate_type = st.radio("波片类型", ["1/4波片", "1/2波片"])
        
        x, original_intensity, phase_diff, info = calculator.polarization_interference(
            wavelength=wavelength,
            polarizer_angle=np.radians(polarizer_angle),
            analyzer_angle=np.radians(analyzer_angle),
            waveplate_angle=np.radians(waveplate_angle),
            waveplate_type='quarter' if waveplate_type == '1/4波片' else 'half'
        )
        
        if enable_error:
            intensity, noise_info = calculator.add_noise(
                original_intensity, systematic_error, random_error,
                ambient_light=ambient_light, detector_noise=detector_noise
            )
        else:
            intensity = original_intensity
        
        st.markdown("#### 📐 实时物理量")
        st.write(f"**消光比**: {info['extinction_ratio']:.4f}")
        st.write(f"**最大光强**: {info['max_intensity']:.4f}")
        st.write(f"**最小光强**: {info['min_intensity']:.4f}")
        st.write(f"**相位延迟**: {info['phase_retardation']:.1f}°")

with col2:
    st.markdown("### 📊 仿真结果")

    if intensity is not None:
        if experiment_mode in ["双缝干涉", "单缝衍射", "多缝光栅", "偏振干涉"]:
            if show_3d:
                fig = plt.figure(figsize=(14, 10))
                ax = fig.add_subplot(111, projection='3d')
                
                x_3d = x * 1000
                y_3d = np.linspace(-5, 5, 30)
                X_3d, Y_3d = np.meshgrid(x_3d, y_3d)
                Z_3d = np.tile(intensity, (30, 1))
                
                surf = ax.plot_surface(X_3d, Y_3d, Z_3d, cmap=color_scheme,
                                       edgecolor='none', alpha=0.9,
                                       rstride=8, cstride=1, antialiased=False)
                
                ax.view_init(elev=30, azim=60)
                ax.set_xlabel('位置 (mm)', fontsize=12, fontweight='bold', labelpad=8)
                ax.set_ylabel('Y方向 (mm)', fontsize=12, fontweight='bold', labelpad=8)
                ax.set_zlabel('相对强度', fontsize=12, fontweight='bold', labelpad=8)
                ax.set_zlim(0, 1.1)
                
                cbar = fig.colorbar(surf, ax=ax, shrink=0.6, aspect=15, pad=0.1)
                cbar.set_label('相对强度', fontsize=11)
                plt.tight_layout()
                st.pyplot(fig)
            else:
                fig = plt.figure(figsize=(12, 9))
                
                if show_phase:
                    ax1 = fig.add_subplot(3, 1, 1)
                    ax1.fill_between(x * 1000, intensity, alpha=0.4)
                    ax1.plot(x * 1000, intensity, linewidth=2, color='#1565c0')
                    ax1.set_xlabel('位置 (mm)', fontsize=11, fontweight='bold')
                    ax1.set_ylabel('相对强度', fontsize=11, fontweight='bold')
                    ax1.grid(True, alpha=0.3, linestyle='--')
                    ax1.set_ylim(0, 1.1)
                    
                    ax2 = fig.add_subplot(3, 1, 2)
                    ax2.plot(x * 1000, phase_diff, linewidth=2, color='#d32f2f')
                    ax2.set_xlabel('位置 (mm)', fontsize=11, fontweight='bold')
                    ax2.set_ylabel('相位差 (rad)', fontsize=11, fontweight='bold')
                    ax2.grid(True, alpha=0.3, linestyle='--')
                    
                    ax3 = fig.add_subplot(3, 1, 3)
                    y_img = np.linspace(0, 1, 150)
                    Z = np.tile(intensity, (150, 1))
                    im = ax3.imshow(Z, extent=[x[0]*1000, x[-1]*1000, 0, 1], aspect='auto', cmap=color_scheme, interpolation='bilinear')
                    ax3.set_xlabel('位置 (mm)', fontsize=11, fontweight='bold')
                    ax3.set_ylabel('强度分布', fontsize=11, fontweight='bold')
                    cbar = plt.colorbar(im, ax=ax3, shrink=0.8)
                    cbar.set_label('强度', fontsize=10)
                else:
                    ax1 = fig.add_subplot(2, 1, 1)
                    ax1.fill_between(x * 1000, intensity, alpha=0.4)
                    ax1.plot(x * 1000, intensity, linewidth=2, color='#1565c0')
                    ax1.set_xlabel('位置 (mm)', fontsize=11, fontweight='bold')
                    ax1.set_ylabel('相对强度', fontsize=11, fontweight='bold')
                    ax1.grid(True, alpha=0.3, linestyle='--')
                    ax1.set_ylim(0, 1.1)
                    
                    ax2 = fig.add_subplot(2, 1, 2)
                    y_img = np.linspace(0, 1, 150)
                    Z = np.tile(intensity, (150, 1))
                    im = ax2.imshow(Z, extent=[x[0]*1000, x[-1]*1000, 0, 1], aspect='auto', cmap=color_scheme, interpolation='bilinear')
                    ax2.set_xlabel('位置 (mm)', fontsize=11, fontweight='bold')
                    ax2.set_ylabel('强度分布', fontsize=11, fontweight='bold')
                    cbar = plt.colorbar(im, ax=ax2, shrink=0.8)
                    cbar.set_label('强度', fontsize=10)
                
                plt.tight_layout(pad=1.5)
                st.pyplot(fig)
        
        elif experiment_mode == "迈克耳孙干涉":
            fig = plt.figure(figsize=(12, 9))
            
            ax1 = fig.add_subplot(2, 1, 1)
            ax1.fill_between(path_diff * 1e6, intensity, alpha=0.4)
            ax1.plot(path_diff * 1e6, intensity, linewidth=2, color='#1565c0')
            ax1.set_xlabel('光程差 (μm)', fontsize=11, fontweight='bold')
            ax1.set_ylabel('相对强度', fontsize=11, fontweight='bold')
            ax1.grid(True, alpha=0.3, linestyle='--')
            ax1.set_ylim(0, 1.1)
            
            ax2 = fig.add_subplot(2, 1, 2)
            y_img = np.linspace(0, 1, 150)
            Z = np.tile(intensity, (150, 1))
            im = ax2.imshow(Z, extent=[path_diff[0]*1e6, path_diff[-1]*1e6, 0, 1], aspect='auto', cmap=color_scheme, interpolation='bilinear')
            ax2.set_xlabel('光程差 (μm)', fontsize=11, fontweight='bold')
            ax2.set_ylabel('强度分布', fontsize=11, fontweight='bold')
            cbar = plt.colorbar(im, ax=ax2, shrink=0.8)
            cbar.set_label('强度', fontsize=10)
            
            plt.tight_layout(pad=1.5)
            st.pyplot(fig)
        
        elif experiment_mode == "薄膜干涉":
            fig = plt.figure(figsize=(12, 9))
            
            ax1 = fig.add_subplot(2, 1, 1)
            ax1.plot(x * 1e9 if info['interference_type'] == '等厚干涉' else np.degrees(x), intensity, linewidth=2, color='#1565c0')
            ax1.set_xlabel('厚度 (nm)' if info['interference_type'] == '等厚干涉' else '入射角 (°)', fontsize=11, fontweight='bold')
            ax1.set_ylabel('相对强度', fontsize=11, fontweight='bold')
            ax1.grid(True, alpha=0.3, linestyle='--')
            ax1.set_ylim(0, 1.1)
            
            ax2 = fig.add_subplot(2, 1, 2)
            y_img = np.linspace(0, 1, 150)
            Z = np.tile(intensity, (150, 1))
            im = ax2.imshow(Z, extent=[x[0]*1e9 if info['interference_type'] == '等厚干涉' else 0, 
                                       x[-1]*1e9 if info['interference_type'] == '等厚干涉' else 60, 0, 1], 
                           aspect='auto', cmap=color_scheme, interpolation='bilinear')
            ax2.set_xlabel('厚度 (nm)' if info['interference_type'] == '等厚干涉' else '入射角 (°)', fontsize=11, fontweight='bold')
            ax2.set_ylabel('强度分布', fontsize=11, fontweight='bold')
            cbar = plt.colorbar(im, ax=ax2, shrink=0.8)
            cbar.set_label('强度', fontsize=10)
            
            plt.tight_layout(pad=1.5)
            st.pyplot(fig)

st.markdown("---")

st.markdown("### 📋 数据分析")

if original_intensity is not None and intensity is not None:
    error_info = calculator.calculate_error(intensity, original_intensity)
    
    col3, col4, col5 = st.columns(3)
    with col3:
        st.metric("均方根误差", f"{error_info['root_mean_square_error']:.4f}")
    with col4:
        st.metric("最大误差", f"{error_info['max_error']:.4f}")
    with col5:
        st.metric("相对误差", f"{error_info['error_percentage']:.2f}%")

st.markdown("#### 📥 数据导出")
if st.button("导出数据为Excel"):
    if experiment_mode in ["双缝干涉", "单缝衍射", "多缝光栅", "偏振干涉"]:
        df = pd.DataFrame({
            '位置_mm': x * 1000,
            '相对强度': intensity,
            '相位差_rad': phase_diff if phase_diff is not None else np.nan,
            '光程差_m': info.get('path_difference', np.nan)[:len(intensity)] if isinstance(info.get('path_difference'), np.ndarray) else np.nan
        })
    elif experiment_mode == "迈克耳孙干涉":
        df = pd.DataFrame({
            '光程差_um': path_diff * 1e6,
            '相对强度': intensity,
            '相位差_rad': phase_diff if phase_diff is not None else np.nan
        })
    elif experiment_mode == "薄膜干涉":
        df = pd.DataFrame({
            '参数': x * 1e9 if info['interference_type'] == '等厚干涉' else np.degrees(x),
            '相对强度': intensity,
            '相位差_rad': phase_diff if phase_diff is not None else np.nan
        })
    
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='openpyxl')
    df.to_excel(writer, index=False, sheet_name='光学数据')
    writer.close()
    output.seek(0)
    
    st.download_button(
        label="下载Excel文件",
        data=output,
        file_name=f'{experiment_mode}_数据.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

if noise_info is not None:
    with st.expander("📊 误差分析报告"):
        st.markdown("**误差来源：**")
        for component in noise_info['noise_components']:
            st.write(f"- {component}")
        st.markdown("**误差统计：**")
        st.write(f"- 最大偏差: {noise_info['max_deviation']:.4f}")
        st.write(f"- 均方根偏差: {noise_info['rms_deviation']:.4f}")
        st.markdown("**改进建议：**")
        st.write("1. 减小系统误差：校准实验器材，提高测量精度")
        st.write("2. 减小随机误差：增加测量次数，进行数据平均")
        st.write("3. 降低环境光干扰：在暗室中进行实验")
        st.write("4. 使用低噪声探测器：提高信号质量")

with st.expander("📖 物理原理"):
    if experiment_mode == "双缝干涉":
        st.markdown("""
        **双缝干涉原理**
        
        当一束相干光通过两个平行狭缝后，会在屏幕上形成明暗相间的干涉条纹。
        
        **核心公式：**
        """)
        st.markdown('<div class="formula-box">光程差：Δ = d·sinθ<br>相位差：δ = 2π·Δ/λ = 2π·d·sinθ/λ<br>光强分布：I = I₀·cos²(π·d·x/(λ·D))<br>条纹间距：Δx = λ·D/d</div>', unsafe_allow_html=True)
        st.markdown("""
        **参数说明：**
        - λ：光波长
        - d：双缝间距
        - D：缝到屏幕距离
        - x：屏幕上的位置
        
        **物理现象：**
        当两束光的光程差为波长的整数倍时，产生相长干涉（亮纹）；
        当光程差为半波长的奇数倍时，产生相消干涉（暗纹）。
        
        **扩展说明：**
        - 介质折射率n会影响有效波长：λ' = λ/n
        - 偏振态会影响干涉对比度
        - 光源相干性决定条纹清晰度
        """)
    elif experiment_mode == "单缝衍射":
        st.markdown("""
        **单缝衍射原理**
        
        当光通过宽度与波长相当的狭缝时，会发生衍射现象，形成明暗相间的衍射图样。
        
        **核心公式：**
        """)
        st.markdown('<div class="formula-box">半波带数：N = a·sinθ/(λ/2)<br>光强分布：I = I₀·(sinβ/β)²，其中 β = π·a·sinθ/λ<br>暗纹条件：a·sinθ = kλ (k=±1, ±2, ±3...)</div>', unsafe_allow_html=True)
        st.markdown("""
        **参数说明：**
        - a：缝宽
        - θ：衍射角
        - λ：光波长
        
        **物理现象：**
        中央明纹最亮最宽，约为其他明纹宽度的两倍；
        暗纹位置由 a·sinθ = kλ 决定。
        """)
    elif experiment_mode == "多缝光栅":
        st.markdown("""
        **多缝光栅衍射原理**
        
        光栅衍射是多光束干涉与单缝衍射的叠加，形成尖锐的主极大和细密的次极大。
        
        **核心公式：**
        """)
        st.markdown('<div class="formula-box">光栅方程：d·sinθ = kλ (k=0, ±1, ±2...)<br>主极大强度：I = I₀·(sinβ/β)²·(sin(Nα)/sinα)²<br>缺级条件：d/a = k/k\'（k为缺级）</div>', unsafe_allow_html=True)
        st.markdown("""
        **参数说明：**
        - d：光栅常数（相邻缝间距）
        - N：缝数
        - a：缝宽
        
        **物理现象：**
        主极大位置由光栅方程决定，强度受单缝衍射包络调制；
        缝数越多，主极大越尖锐。
        """)
    elif experiment_mode == "迈克耳孙干涉":
        st.markdown("""
        **迈克耳孙干涉原理**
        
        迈克耳孙干涉仪利用分振幅法产生双光束干涉，可用于精确测量长度变化。
        
        **核心公式：**
        """)
        st.markdown('<div class="formula-box">光程差：Δ = 2d·cosθ<br>条纹移动数：ΔN = 2Δd/λ</div>', unsafe_allow_html=True)
        st.markdown("""
        **参数说明：**
        - d：两臂光程差的一半
        - θ：入射角
        - λ：光波长
        
        **物理现象：**
        当平面镜移动时，干涉条纹会相应移动；
        每移动λ/2距离，条纹移动一条。
        """)
    elif experiment_mode == "薄膜干涉":
        st.markdown("""
        **薄膜干涉原理**
        
        当光入射到薄膜上时，上下表面的反射光会发生干涉。
        
        **核心公式：**
        """)
        st.markdown('<div class="formula-box">光程差：Δ = 2n·d·cosθ<br>相位突变：当光从光疏介质入射到光密介质时，反射光有π相位突变</div>', unsafe_allow_html=True)
        st.markdown("""
        **等厚干涉：** 薄膜厚度不均匀，同一级条纹对应相同厚度的位置
        **等倾干涉：** 薄膜厚度均匀，同一级条纹对应相同入射角的光线
        
        **参数说明：**
        - n：薄膜折射率
        - d：薄膜厚度
        - θ：折射角
        """)
    elif experiment_mode == "偏振干涉":
        st.markdown("""
        **偏振干涉原理**
        
        偏振光通过波片后会分解为两个正交分量，产生相位差，再通过检偏器发生干涉。
        
        **核心公式：**
        """)
        st.markdown('<div class="formula-box">波片相位差：δ = 2π·(nₒ-nₑ)·d/λ<br>1/4波片：δ = π/2<br>1/2波片：δ = π</div>', unsafe_allow_html=True)
        st.markdown("""
        **物理现象：**
        线偏振光通过1/4波片可变为椭圆偏振光或圆偏振光；
        通过1/2波片可改变偏振方向。
        
        **琼斯矩阵方法：**
        利用琼斯矩阵可以精确计算偏振光经过光学元件后的状态变化。
        """)

if mode_type == "教学模式":
    with st.expander("📚 教学指导"):
        st.markdown("""
        **教学目标：**
        - 理解波动光学的核心概念
        - 掌握干涉和衍射的基本规律
        - 学会分析实验参数对现象的影响
        
        **学习步骤：**
        
        **第一步：基础现象观察**
        1. 使用默认参数观察干涉/衍射条纹
        2. 注意条纹的形状、间距和强度分布
        
        **第二步：参数影响分析**
        1. 调整波长，观察条纹颜色和间距变化
        2. 调整缝距/缝宽，观察条纹疏密变化
        3. 调整屏距，观察条纹整体大小变化
        
        **第三步：拓展探究**
        1. 调整偏振角，观察对比度变化
        2. 改变介质折射率，观察有效波长变化
        3. 启用误差模拟，理解实验误差来源
        
        **思考问题：**
        1. 为什么增大缝距会使条纹变密？
        2. 为什么中央明纹最亮？
        3. 偏振态如何影响干涉现象？
        """)

if mode_type == "练习模式":
    st.markdown("## ❓ 练习题目")
    
    questions = {
        "双缝干涉": {
            "基础题": [
                {"question": "给定波长λ=540nm，缝距d=0.5mm，屏距D=1m，计算条纹间距Δx。",
                 "answer": "Δx = λD/d = 540×10^-9 × 1 / 0.5×10^-3 = 1.08mm"},
                {"question": "若将波长变为600nm，条纹间距变为多少？",
                 "answer": "Δx = 600×10^-9 × 1 / 0.5×10^-3 = 1.2mm"}
            ],
            "进阶题": [
                {"question": "分析当偏振角从0°变为90°时，干涉条纹对比度的变化规律。",
                 "answer": "偏振角为0°时对比度最大，随着偏振角增大，对比度逐渐减小，90°时对比度为0。"},
                {"question": "若介质折射率n=1.5，计算有效波长和条纹间距的变化。",
                 "answer": "有效波长λ' = λ/n = 540/1.5 = 360nm，条纹间距变为原来的1/1.5"}
            ],
            "创新题": [
                {"question": "设计一个双缝干涉实验，使得条纹间距为2mm（波长选用500nm，屏距1m）。",
                 "answer": "d = λD/Δx = 500×10^-9 × 1 / 0.002 = 0.25mm"},
                {"question": "如何通过实验测量未知光波长？",
                 "answer": "测量条纹间距Δx，已知d和D，计算λ = Δx·d/D"}
            ]
        },
        "单缝衍射": {
            "基础题": [
                {"question": "缝宽a=0.1mm，波长λ=600nm，计算第一暗纹衍射角。",
                 "answer": "sinθ = λ/a = 600×10^-9 / 0.1×10^-3 = 0.006，θ≈0.344°"},
                {"question": "计算中央明纹宽度（屏距D=1m）。",
                 "answer": "Δx = 2D·tanθ ≈ 2×1×0.006 = 0.012m = 12mm"}
            ],
            "进阶题": [
                {"question": "分析缝宽不均匀对衍射条纹的影响。",
                 "answer": "缝宽不均匀会导致衍射包络变形，次级明纹强度分布不规则。"},
                {"question": "比较单缝衍射和双缝干涉的条纹特点。",
                 "answer": "单缝衍射中央明纹宽，次级明纹强度递减；双缝干涉条纹等间距，强度相近。"}
            ],
            "创新题": [
                {"question": "如何利用单缝衍射测量细丝直径？",
                 "answer": "将细丝视为单缝，测量衍射图样，利用a·sinθ = kλ计算直径。"},
                {"question": "设计实验区分单缝衍射和双缝干涉图样。",
                 "answer": "观察条纹宽度和强度分布，单缝中央宽，双缝等间距。"}
            ]
        },
        "多缝光栅": {
            "基础题": [
                {"question": "光栅常数d=20μm，波长λ=500nm，计算最大衍射级次。",
                 "answer": "k_max = d/λ = 20×10^-6 / 500×10^-9 = 40"},
                {"question": "计算光栅的分辨本领（N=1000条缝，k=1）。",
                 "answer": "R = kN = 1×1000 = 1000"}
            ],
            "进阶题": [
                {"question": "分析缝数增加对光栅光谱的影响。",
                 "answer": "缝数增加使主极大变尖锐，提高分辨率，但不改变主极大位置。"},
                {"question": "什么是缺级现象？如何避免缺级？",
                 "answer": "当d/a为整数时发生缺级，选择d/a不为整数可避免。"}
            ],
            "创新题": [
                {"question": "设计一个光栅，使其能分辨500nm和500.1nm的光谱。",
                 "answer": "R = λ/Δλ = 500/0.1 = 5000，需要kN ≥ 5000。"},
                {"question": "如何利用光栅测量未知波长？",
                 "answer": "测量衍射角，利用d·sinθ = kλ计算波长。"}
            ]
        },
        "迈克耳孙干涉": {
            "基础题": [
                {"question": "镜面移动Δd=2.5μm，波长λ=550nm，计算条纹移动数。",
                 "answer": "ΔN = 2Δd/λ = 2×2.5×10^-6 / 550×10^-9 ≈ 9.09"},
                {"question": "若条纹可见度为0.8，计算两束光强度比。",
                 "answer": "V = 2√I1I2/(I1+I2) = 0.8，解得I1/I2 ≈ 0.38或2.63"}
            ],
            "进阶题": [
                {"question": "分析光源相干长度对干涉的影响。",
                 "answer": "相干长度越长，能观察到干涉条纹的光程差范围越大。"},
                {"question": "迈克耳孙干涉仪如何用于测量折射率？",
                 "answer": "在一臂中插入介质，测量条纹移动数，计算折射率。"}
            ],
            "创新题": [
                {"question": "设计实验测量微小长度变化（如热膨胀）。",
                 "answer": "利用迈克耳孙干涉仪，测量镜面移动引起的条纹变化。"},
                {"question": "如何区分等倾干涉和等厚干涉？",
                 "answer": "等倾干涉是同心圆条纹，等厚干涉是平行直线条纹。"}
            ]
        },
        "薄膜干涉": {
            "基础题": [
                {"question": "薄膜厚度d=500nm，折射率n=1.5，计算反射光相长干涉的波长。",
                 "answer": "2nd = kλ，λ = 2×1.5×500/nm = 1500nm/k，可见光中λ=500nm(k=3)"},
                {"question": "解释增透膜的工作原理。",
                 "answer": "利用薄膜干涉使反射光相消，增加透射光强度。"}
            ],
            "进阶题": [
                {"question": "分析入射角对薄膜干涉的影响。",
                 "answer": "入射角增大，光程差变化，条纹间距改变。"},
                {"question": "比较等厚干涉和等倾干涉的特点。",
                 "answer": "等厚干涉厚度变化，等倾干涉角度变化。"}
            ],
            "创新题": [
                {"question": "设计一个测量薄膜厚度的实验方案。",
                 "answer": "利用等厚干涉条纹间距，计算薄膜厚度变化。"},
                {"question": "如何利用薄膜干涉检测表面平整度？",
                 "answer": "观察等厚干涉条纹形状，判断表面凹凸。"}
            ]
        },
        "偏振干涉": {
            "基础题": [
                {"question": "起偏器和检偏器正交时，光强如何变化？",
                 "answer": "光强为0，发生消光现象。"},
                {"question": "1/4波片的作用是什么？",
                 "answer": "使o光和e光产生π/2相位差，可将线偏振光变为椭圆偏振光。"}
            ],
            "进阶题": [
                {"question": "分析波片角度对偏振干涉的影响。",
                 "answer": "波片角度决定两个正交分量的振幅，影响干涉强度。"},
                {"question": "如何利用偏振干涉测量材料的双折射率？",
                 "answer": "通过测量相位延迟，计算双折射率差。"}
            ],
            "创新题": [
                {"question": "设计一个产生圆偏振光的实验方案。",
                 "answer": "线偏振光通过1/4波片，波片光轴与偏振方向成45°。"},
                {"question": "如何区分线偏振光、圆偏振光和自然光？",
                 "answer": "使用检偏器和1/4波片组合检测。"}
            ]
        }
    }
    
    level = st.radio("难度等级", ["基础验证题", "进阶探究题", "创新设计题"])
    level_key = "基础题" if level == "基础验证题" else "进阶题" if level == "进阶探究题" else "创新题"
    
    if experiment_mode in questions:
        for i, q in enumerate(questions[experiment_mode][level_key], 1):
            st.markdown(f"**{i}. {q['question']}**")
            with st.expander("查看答案"):
                st.write(q['answer'])
    
    student_answer = st.text_area("你的答案（可选）：", height=100)
    if st.button("提交答案"):
        st.success("答案已保存！请对照参考答案检查。")

st.markdown("---")
st.markdown("### ℹ️ 使用说明")
st.markdown("""
**使用指南：**
1. **选择实验**：从侧边栏选择光学实验类型
2. **调整参数**：使用滑块调整实验参数，观察实时变化
3. **误差模拟**：勾选"启用误差模拟"可添加系统误差、随机误差、环境光和探测器噪声
4. **数据导出**：点击按钮导出实验数据为Excel格式
5. **学习原理**：展开"物理原理"查看详细的理论推导
6. **教学模式**：在教学模式中获得分步指导
7. **练习模式**：在练习模式中完成物理习题
8. **波长计算器**：使用"反推波长"功能根据条纹间距计算波长
""")

with st.expander("🔢 波长计算器"):
    st.markdown("### 🔢 波长反推计算器")
    st.markdown("根据测量的条纹间距，反推光波长")
    
    col_calc1, col_calc2, col_calc3 = st.columns(3)
    with col_calc1:
        calc_fringe = st.number_input("条纹间距 (mm)", value=1.08, step=0.01, format="%.3f") * 1e-3
    with col_calc2:
        calc_slit = st.number_input("缝距 (mm)", value=0.5, step=0.01, format="%.3f") * 1e-3
    with col_calc3:
        calc_screen = st.number_input("屏距 (m)", value=1.0, step=0.1, format="%.1f")
    
    if st.button("计算波长"):
        result = calculator.calculate_wavelength_from_fringe(calc_fringe, calc_slit, calc_screen)
        
        col_res1, col_res2, col_res3 = st.columns(3)
        with col_res1:
            st.metric("计算波长", f"{result['wavelength_nm']:.2f} nm")
        with col_res2:
            color = calculator.generate_wavelength_color(result['wavelength_nm'])
            st.metric("光颜色", color)
        with col_res3:
            st.metric("是否可见", "是 ✓" if result['in_visible_range'] else "否 ✗")
        
        if result['in_visible_range']:
            st.success(f"该波长为可见光（{color}色光），位于可见光范围内（400-760nm）")
        else:
            st.warning(f"该波长为不可见光，请调整参数重新计算")

with st.expander("📐 物理公式速查"):
    st.markdown("""
    ### 波动光学核心公式速查
    
    | 实验类型 | 核心公式 | 说明 |
    |---------|---------|------|
    | 双缝干涉 | Δx = λD/d | 条纹间距公式 |
    | 双缝干涉 | Δ = d·sinθ | 光程差公式 |
    | 单缝衍射 | a·sinθ = kλ | 暗纹条件 |
    | 单缝衍射 | I = I₀(sinβ/β)² | 强度分布公式 |
    | 多缝光栅 | d·sinθ = kλ | 光栅方程 |
    | 迈克耳孙 | ΔN = 2Δd/λ | 条纹移动数 |
    | 薄膜干涉 | Δ = 2nd·cosθ | 光程差 |
    | 偏振干涉 | δ = 2π(ne-no)d/λ | 相位延迟 |
    
    **符号说明：**
    - λ：光波长
    - d：缝距/光栅常数
    - D：屏距
    - θ：衍射角/入射角
    - a：缝宽
    - n：折射率
    - d：薄膜厚度/光程差
    """)

with st.expander("🤖 智能助手", expanded=False):
    st.markdown("## 🤖 波动光学智能助手")
    
    # API配置
    col_api1, col_api2 = st.columns([3, 1])
    with col_api1:
        api_url = st.text_input("千问API地址", value="http://localhost:8000/v1/chat/completions", key="api_url")
    with col_api2:
        model_name = st.text_input("模型名称", value="Qwen", key="model_name")
    if st.button("应用配置"):
        agent.set_api_config(api_url, model_name)
        st.success("API配置已更新！")
    
    # 显示对话历史
    chat_container = st.container()
    with chat_container:
        for msg in agent.get_history():
            if msg["role"] == "user":
                st.markdown(f"**您：** {msg['content']}")
            else:
                st.markdown(f"**助手：** {msg['content']}")
    
    # 用户输入
    user_input = st.text_input("请输入您的问题（例如：双缝干涉的原理是什么？）：", key="agent_input")
    
    col_agent1, col_agent2 = st.columns([4, 1])
    with col_agent1:
        if st.button("发送"):
            if user_input.strip():
                response = agent.generate_response(user_input)
                # 刷新页面以显示新消息
                st.experimental_rerun()
    
    with col_agent2:
        if st.button("清空对话"):
            agent.clear_history()
            st.experimental_rerun()
    
    # 快捷提问按钮
    st.markdown("**快捷提问：**")
    quick_questions = [
        "双缝干涉的原理是什么？",
        "单缝衍射的公式是什么？",
        "如何测量光波长？",
        "偏振态如何影响干涉？",
        "迈克耳孙干涉仪的应用"
    ]
    
    cols = st.columns(5)
    for i, q in enumerate(quick_questions):
        with cols[i]:
            if st.button(q, key=f"quick_{i}"):
                response = agent.generate_response(q)
                st.experimental_rerun()