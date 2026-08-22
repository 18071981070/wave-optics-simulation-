import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.font_manager import fontManager
from matplotlib.colors import LinearSegmentedColormap
import pandas as pd
from io import BytesIO
import os
from PIL import Image

font_path = os.path.join(os.path.dirname(__file__), 'simhei.ttf')
if os.path.exists(font_path):
    fontManager.addfont(font_path)
    matplotlib.rcParams['font.sans-serif'] = ['SimHei']
else:
    matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS']
matplotlib.rcParams['axes.unicode_minus'] = False
matplotlib.rcParams.update({
    'font.size': 11.5,
    'axes.titlesize': 14,
    'axes.labelsize': 11.5,
    'axes.titleweight': 'bold',
    'axes.edgecolor': '#cbd5e1',
    'axes.labelcolor': '#334155',
    'xtick.color': '#475569',
    'ytick.color': '#475569',
    'grid.color': '#cbd5e1',
    'grid.alpha': 0.35,
    'figure.facecolor': '#ffffff',
    'axes.facecolor': '#fbfdff',
})


def _load_streamlit_secrets_to_environ():
    """把 Streamlit Cloud Secrets 中的 API 配置注入环境变量，供 AI 助手读取。
    本地无 secrets.toml 时静默跳过，不影响环境变量方式。"""
    try:
        _secrets = st.secrets
    except Exception:
        return
    # DashScope API Key（任一别名均可）
    for _name in ("DASHSCOPE_API_KEY", "DASHSCOPE_KEY", "QWEN_API_KEY"):
        try:
            _val = _secrets[_name]
        except (KeyError, TypeError):
            continue
        if _val and not os.getenv(_name):
            os.environ[_name] = str(_val)
    # 可选的自定义端点/模型
    for _env in ("DASHSCOPE_API_URL", "DASHSCOPE_MODEL",
                 "OPENAI_BASE_URL", "OPENAI_MODEL", "OPENAI_API_KEY"):
        try:
            _val = _secrets[_env]
        except (KeyError, TypeError):
            continue
        if _val and not os.getenv(_env):
            os.environ[_env] = str(_val)


_load_streamlit_secrets_to_environ()

from optical_calculator import OpticalCalculator
try:
    from agent_module import PhysicsAgent
except ImportError:
    from agent_module_v2 import EnhancedPhysicsAgent as PhysicsAgent

try:
    from agent_module_v2 import EnhancedPhysicsAgent
    DEFAULT_AGENT = EnhancedPhysicsAgent
except ImportError:
    DEFAULT_AGENT = PhysicsAgent

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

    /* 教学平台视觉系统 */
    :root {
        --primary: #0f766e;
        --primary-light: #14b8a6;
        --accent: #f59e0b;
        --bg-main: linear-gradient(180deg, #f0fdfa 0%, #f8fafc 42%, #eef2ff 100%);
        --bg-card: rgba(255, 255, 255, 0.96);
        --text-primary: #0f172a;
        --text-secondary: #475569;
    }

    .stApp {
        background: var(--bg-main) !important;
    }

    /* Streamlit 重算时默认会降低旧内容透明度，造成明显白闪。 */
    .stale, [data-stale="true"] {
        opacity: 1 !important;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8fffe 0%, #ecfeff 100%) !important;
        border-right: 1px solid #ccfbf1;
    }

    .main-header {
        color: #0f172a;
        background: none;
        -webkit-text-fill-color: #0f172a;
        text-shadow: none;
        margin-top: 0.25rem;
    }

    .sub-header {
        color: #475569;
        margin-bottom: 1.25rem;
    }

    .hero-panel {
        background: linear-gradient(120deg, #0f172a 0%, #134e4a 58%, #0f766e 100%);
        border-radius: 24px;
        padding: 30px 34px;
        color: white;
        box-shadow: 0 18px 50px rgba(15, 23, 42, 0.16);
        margin: 0.5rem 0 1.1rem 0;
    }

    .hero-kicker {
        color: #99f6e4;
        font-size: 0.82rem;
        font-weight: 800;
        letter-spacing: 0.16em;
        margin-bottom: 8px;
    }

    .hero-title {
        font-size: 2.25rem;
        font-weight: 900;
        line-height: 1.2;
        margin-bottom: 10px;
    }

    .hero-copy {
        color: #d5f5f0;
        font-size: 1rem;
        margin: 0;
    }

    .workflow-strip {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 10px;
        margin: 0.8rem 0 1.2rem 0;
    }

    .workflow-step {
        background: rgba(255, 255, 255, 0.95);
        border: 1px solid #dbeafe;
        border-radius: 14px;
        padding: 13px 14px;
        color: #334155;
        font-weight: 700;
        box-shadow: 0 5px 18px rgba(15, 23, 42, 0.05);
    }

    .workflow-step b {
        display: block;
        color: #0f766e;
        font-size: 0.76rem;
        letter-spacing: 0.08em;
        margin-bottom: 4px;
    }

    .principle-panel, .teacher-panel, .link-panel {
        background: rgba(255, 255, 255, 0.97);
        border: 1px solid #dbeafe;
        border-radius: 18px;
        padding: 20px 22px;
        box-shadow: 0 8px 26px rgba(15, 23, 42, 0.06);
    }

    .principle-panel {
        border-left: 5px solid #0f766e;
    }

    .formula-focus {
        background: #f0fdfa;
        color: #115e59;
        border-radius: 12px;
        padding: 13px 16px;
        font-family: Georgia, serif;
        font-size: 1.14rem;
        text-align: center;
        border: 1px solid #99f6e4;
        margin-top: 12px;
    }

    .function-grid {
        display: grid;
        grid-template-columns: repeat(6, minmax(0, 1fr));
        gap: 8px;
        margin-bottom: 1rem;
    }

    .function-chip {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 10px 8px;
        text-align: center;
        color: #334155;
        font-size: 0.86rem;
        font-weight: 750;
    }

    .link-panel {
        background: linear-gradient(135deg, #ecfeff 0%, #f0fdfa 100%);
        border-color: #99f6e4;
        margin-bottom: 0.8rem;
    }

    .link-flow {
        color: #0f766e;
        font-weight: 800;
        text-align: center;
        font-size: 0.95rem;
    }

    .instrument-stage {
        display: grid;
        grid-template-columns: 0.9fr 1.3fr 0.9fr;
        align-items: center;
        gap: 12px;
        min-height: 120px;
        padding: 18px;
        margin-bottom: 0.9rem;
        border-radius: 18px;
        background: #07111f;
        color: #e2e8f0;
        border: 1px solid #1e293b;
        overflow: hidden;
    }

    .instrument-node {
        padding: 14px;
        background: rgba(15, 23, 42, 0.86);
        border: 1px solid #334155;
        border-radius: 12px;
        text-align: center;
    }

    .instrument-node small {
        display: block;
        color: #94a3b8;
        margin-bottom: 5px;
    }

    .instrument-value {
        color: #5eead4;
        font-size: 1.05rem;
        font-weight: 800;
    }

    .beam-line {
        height: 4px;
        border-radius: 8px;
        box-shadow: 0 0 18px currentColor;
        position: relative;
    }

    .beam-line:after {
        content: "";
        position: absolute;
        right: -6px;
        top: -4px;
        border-left: 9px solid currentColor;
        border-top: 6px solid transparent;
        border-bottom: 6px solid transparent;
    }

    .stButton>button {
        background: linear-gradient(135deg, #0f766e 0%, #0d9488 100%);
        box-shadow: 0 4px 14px rgba(15, 118, 110, 0.24);
    }

    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #0f766e !important;
    }

    .block-container {
        max-width: 1760px;
        padding-left: 2.25rem;
        padding-right: 2.25rem;
    }

    [data-testid="stExpanderDetails"],
    [data-testid="stExpanderDetails"] p,
    [data-testid="stExpanderDetails"] label,
    [data-testid="stAlert"] p,
    div[data-testid="stRadio"] label p {
        color: #0f172a !important;
    }

    [data-testid="stExpanderDetails"] {
        padding-top: 0.5rem;
        padding-bottom: 0.8rem;
    }

    /* Explicit text contrast for Streamlit components on the light lab theme. */
    [data-testid="stMarkdownContainer"] > h1,
    [data-testid="stMarkdownContainer"] > h2,
    [data-testid="stMarkdownContainer"] > h3,
    [data-testid="stMarkdownContainer"] > h4,
    [data-testid="stMarkdownContainer"] > h5,
    [data-testid="stMarkdownContainer"] > h6,
    [data-testid="stMarkdownContainer"] > p,
    [data-testid="stMarkdownContainer"] > ul,
    [data-testid="stMarkdownContainer"] > ol,
    [data-testid="stMarkdownContainer"] li,
    [data-testid="stWidgetLabel"] p,
    [data-testid="stCaptionContainer"] p,
    [data-testid="stExpander"] summary,
    [data-testid="stExpander"] summary span,
    div[data-testid="stRadio"] label p {
        color: #0f172a !important;
        -webkit-text-fill-color: #0f172a !important;
        opacity: 1 !important;
    }

    [data-testid="stAlert"] * {
        color: #172033 !important;
        -webkit-text-fill-color: #172033 !important;
        opacity: 1 !important;
    }

    [data-testid="stButton"] button,
    [data-testid="stButton"] button * {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        opacity: 1 !important;
    }

    input, textarea, [data-baseweb="select"] {
        color: #0f172a !important;
        -webkit-text-fill-color: #0f172a !important;
    }

    /* 2026 lab-console polish: one coherent, projector-friendly UI layer. */
    :root {
        --lab-ink: #14212b;
        --lab-muted: #52616d;
        --lab-line: #d9e2e8;
        --lab-surface: #ffffff;
        --lab-canvas: #f3f6f8;
        --lab-teal: #087f73;
        --lab-teal-dark: #075e57;
        --lab-amber: #d97706;
        --lab-blue: #2563eb;
    }

    html, body, [class*="css"] {
        font-family: "Microsoft YaHei", "PingFang SC", "Noto Sans CJK SC", sans-serif;
    }

    .stApp {
        background: var(--lab-canvas) !important;
    }

    [data-testid="stHeader"] {
        background: rgba(243, 246, 248, 0.92) !important;
        backdrop-filter: blur(10px);
    }

    [data-testid="stSidebar"] {
        background: #f9fbfc !important;
        border-right: 1px solid var(--lab-line) !important;
    }

    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1.25rem;
    }

    [data-testid="stSidebar"] h2 {
        color: var(--lab-ink) !important;
        font-size: 0.93rem !important;
        margin: 1rem 0 0.4rem !important;
        padding-bottom: 0.42rem;
        border-bottom: 1px solid var(--lab-line);
    }

    .block-container {
        width: min(100%, 1780px);
        max-width: 1780px;
        padding: 1.35rem 2.35rem 3.5rem;
    }

    .hero-panel {
        position: relative;
        overflow: hidden;
        min-height: 150px;
        padding: 26px 32px 24px;
        margin: 0 0 0.75rem;
        border: 1px solid #22333e;
        border-radius: 8px;
        background: #14212b;
        box-shadow: 0 10px 28px rgba(20, 33, 43, 0.14);
    }

    .hero-panel::after {
        content: "";
        position: absolute;
        left: 0;
        right: 0;
        bottom: 0;
        height: 5px;
        background: linear-gradient(90deg, var(--lab-teal) 0 58%, var(--lab-amber) 58% 76%, var(--lab-blue) 76% 100%);
    }

    .hero-kicker {
        color: #6ee7d8;
        font-size: 0.72rem;
        letter-spacing: 0.12em;
        margin-bottom: 7px;
    }

    .hero-title {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        font-size: 2rem;
        letter-spacing: 0;
        margin-bottom: 8px;
    }

    .hero-copy {
        max-width: 820px;
        color: #d8e5e9 !important;
        -webkit-text-fill-color: #d8e5e9 !important;
        font-size: 0.96rem;
        line-height: 1.6;
    }

    .workflow-strip {
        gap: 8px;
        margin: 0 0 0.7rem;
    }

    .workflow-step {
        position: relative;
        min-height: 66px;
        padding: 11px 13px 10px 16px;
        border: 1px solid var(--lab-line);
        border-radius: 6px;
        background: var(--lab-surface);
        color: #3c4b57;
        font-size: 0.86rem;
        box-shadow: none;
    }

    .workflow-step::before {
        content: "";
        position: absolute;
        top: 0;
        bottom: 0;
        left: 0;
        width: 3px;
        background: var(--lab-teal);
    }

    .workflow-step b {
        color: var(--lab-teal-dark);
        font-size: 0.72rem;
        letter-spacing: 0.04em;
    }

    .function-grid {
        gap: 7px;
        margin-bottom: 1rem;
    }

    .function-chip {
        border: 1px solid var(--lab-line);
        border-radius: 4px;
        padding: 7px 8px;
        background: #edf6f5;
        color: #27514d;
        font-size: 0.8rem;
        box-shadow: none;
    }

    .principle-panel, .teacher-panel, .link-panel {
        border: 1px solid var(--lab-line);
        border-radius: 7px;
        background: var(--lab-surface);
        box-shadow: 0 4px 14px rgba(20, 33, 43, 0.05);
    }

    .principle-panel {
        padding: 20px 24px;
        border-left: 4px solid var(--lab-teal);
    }

    .formula-focus, .formula-box {
        border: 1px solid #a9d8d2;
        border-radius: 5px;
        background: #f0f9f8;
        color: #0b514b !important;
        font-family: Georgia, "Times New Roman", serif;
        letter-spacing: 0;
    }

    .section-heading {
        display: flex;
        align-items: center;
        gap: 12px;
        margin: 1.45rem 0 0.65rem;
        padding-bottom: 0.65rem;
        border-bottom: 1px solid var(--lab-line);
    }

    .section-number {
        display: inline-grid;
        place-items: center;
        width: 34px;
        height: 34px;
        flex: 0 0 34px;
        border-radius: 4px;
        background: var(--lab-teal);
        color: #ffffff;
        font-size: 0.82rem;
        font-weight: 800;
    }

    .section-heading strong {
        display: block;
        color: var(--lab-ink);
        font-size: 1.12rem;
        line-height: 1.25;
    }

    .section-heading small {
        display: block;
        margin-top: 3px;
        color: var(--lab-muted);
        font-size: 0.8rem;
        line-height: 1.35;
    }

    .link-panel {
        margin-bottom: 0.65rem;
        padding: 11px 16px;
        background: #edf7f6;
        border-color: #b8ddd8;
    }

    .link-flow {
        color: #155e58;
        font-size: 0.88rem;
        letter-spacing: 0;
    }

    .instrument-stage {
        min-height: 112px;
        margin-bottom: 0.75rem;
        padding: 16px;
        border: 1px solid #263b49;
        border-radius: 7px;
        background: #101b24;
    }

    .instrument-node {
        min-width: 0;
        padding: 12px;
        border: 1px solid #38505f;
        border-radius: 5px;
        background: #192a35;
    }

    .instrument-node small { color: #aebdc6; }
    .instrument-value { color: #72e5d8; font-size: 1rem; }

    div[data-testid="stMetric"] {
        min-height: 96px;
        padding: 14px 16px;
        border: 1px solid var(--lab-line);
        border-top: 3px solid var(--lab-teal);
        border-radius: 5px;
        background: var(--lab-surface);
        box-shadow: none;
        text-align: left;
    }

    div[data-testid="stMetric"] label {
        color: var(--lab-muted) !important;
        font-size: 0.76rem;
        letter-spacing: 0;
        text-transform: none;
    }

    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: var(--lab-ink) !important;
        font-size: 1.28rem;
        line-height: 1.35;
    }

    [data-testid="stAlert"] {
        border-radius: 5px !important;
        border-width: 1px !important;
    }

    [data-testid="stExpander"] {
        overflow: hidden;
        border: 1px solid var(--lab-line) !important;
        border-radius: 5px !important;
        background: var(--lab-surface) !important;
        box-shadow: none !important;
    }

    [data-testid="stExpander"] summary {
        min-height: 48px;
        font-weight: 700;
    }

    .stButton > button {
        min-height: 42px;
        border: 1px solid var(--lab-teal-dark);
        border-radius: 5px;
        background: var(--lab-teal);
        box-shadow: none;
        transition: background 0.16s ease, border-color 0.16s ease;
    }

    .stButton > button:hover {
        transform: none;
        border-color: #064e48;
        background: var(--lab-teal-dark);
        box-shadow: none;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
        padding: 4px;
        border: 1px solid var(--lab-line);
        border-radius: 5px;
        background: #e9eef1;
    }

    .stTabs [data-baseweb="tab"] {
        min-height: 40px;
        padding: 8px 16px;
        border-radius: 3px;
        color: #43525d;
        font-size: 0.88rem;
        letter-spacing: 0;
    }

    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: #ffffff;
        color: var(--lab-teal-dark);
        box-shadow: 0 1px 4px rgba(20, 33, 43, 0.12);
    }

    .stSelectbox > div > div,
    [data-baseweb="input"] > div,
    [data-baseweb="textarea"] > div,
    div[data-testid="stRadio"] > div {
        border-color: #cbd7de !important;
        border-radius: 5px !important;
        background: #ffffff !important;
        box-shadow: none !important;
    }

    [data-testid="stSlider"] [role="slider"] {
        border-color: var(--lab-teal) !important;
        background: #ffffff !important;
    }

    [data-testid="stImage"], [data-testid="stPlotlyChart"] {
        overflow: hidden;
        border: 1px solid var(--lab-line);
        border-radius: 5px;
        background: #ffffff;
    }

    [data-testid="stImage"] img {
        display: block;
    }

    [data-testid="stChatMessage"] {
        margin: 0.55rem 0;
        padding: 0.8rem 1rem;
        border: 1px solid var(--lab-line);
        border-radius: 6px;
        background: #ffffff;
        box-shadow: none;
    }

    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
        border-color: #b8ddd8;
        background: #edf7f6;
    }

    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] li {
        color: var(--lab-ink) !important;
        -webkit-text-fill-color: var(--lab-ink) !important;
    }

    hr {
        margin: 1.7rem 0 !important;
        border-color: var(--lab-line) !important;
    }

    @media (max-width: 900px) {
        .workflow-strip, .function-grid { grid-template-columns: repeat(2, 1fr); }
        .hero-panel { min-height: auto; padding: 22px 20px 21px; }
        .hero-title { font-size: 1.55rem; }
        .hero-copy { font-size: 0.88rem; }
        .block-container { padding: 1rem 0.8rem 2.5rem; }
        .instrument-stage { grid-template-columns: 1fr; }
        .beam-line { margin: 8px 18px; }
        .section-heading { margin-top: 1.2rem; }
    }

    @media (max-width: 560px) {
        .workflow-strip { grid-template-columns: 1fr 1fr; }
        .function-grid { grid-template-columns: repeat(3, 1fr); }
        .workflow-step { min-height: 62px; padding-right: 8px; }
        .function-chip { font-size: 0.72rem; }
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero-panel">
    <div class="hero-kicker">WAVE OPTICS LAB · 实时计算与可视化</div>
    <div class="hero-title">波动光学交互式仿真实验平台</div>
    <p class="hero-copy">仪器状态、物理参数、实验图样与定量曲线同步联动，直接观察变量如何改变实验现象。</p>
</div>
<div class="workflow-strip">
    <div class="workflow-step"><b>01 建立认知</b>先看现象与原理</div>
    <div class="workflow-step"><b>02 明确规律</b>提取核心公式</div>
    <div class="workflow-step"><b>03 操作探究</b>调节实验参数</div>
    <div class="workflow-step"><b>04 证据解释</b>比较图像与数据</div>
</div>
<div class="function-grid">
    <div class="function-chip">6类实验</div><div class="function-chip">实时仿真</div>
    <div class="function-chip">仪器联动</div><div class="function-chip">误差模拟</div>
    <div class="function-chip">分层任务</div><div class="function-chip">教师教学端</div>
</div>
""", unsafe_allow_html=True)

calculator = OpticalCalculator()

# 初始化智能体（使用session_state保持状态）
if 'agent' not in st.session_state:
    try:
        st.session_state.agent = DEFAULT_AGENT()
    except:
        st.session_state.agent = PhysicsAgent()

agent = st.session_state.agent

st.sidebar.markdown("## 👤 使用端")
user_role = st.sidebar.radio(
    "选择身份",
    ["学生学习端", "教师教学端"],
    horizontal=True,
    help="学生端用于自主探究；教师端提供课堂组织、演示脚本和教学记录。"
)

st.sidebar.markdown("## 🎛️ 实验选择")

experiment_mode = st.sidebar.selectbox(
    "选择实验",
    ["双缝干涉", "单缝衍射", "多缝光栅", "迈克耳孙干涉", "薄膜干涉", "偏振干涉"]
)

mode_options = ["教学模式"] if user_role == "教师教学端" else ["实验模式", "教学模式", "练习模式"]
mode_type = st.sidebar.radio(
    "模式",
    mode_options,
    help="实验模式：自由探索 | 教学模式：分步指导 | 练习模式：自我评估"
)

st.sidebar.markdown("## 🔎 观察选项")
show_phase = st.sidebar.checkbox("显示相位曲线", value=False, help="相位曲线用于进阶分析，默认隐藏以突出实验现象。")
show_theory_marks = st.sidebar.checkbox("标注理论特征位置", value=True)

st.sidebar.markdown("## ⚠️ 测量环境")
enable_error = st.sidebar.checkbox("加入真实测量噪声", value=False)
if enable_error:
    random_error = st.sidebar.slider("综合噪声强度", 0.0, 0.08, 0.015, 0.005)
    ambient_light = st.sidebar.slider("环境光背景", 0.0, 0.10, 0.01, 0.01)
    systematic_error = 0.0
    detector_noise = 0.0

st.sidebar.markdown("## 🔄 快捷操作")
if st.sidebar.button("一键重置参数"):
    st.session_state.clear()
    st.rerun()

st.markdown("---")

experiment_overview = {
    "双缝干涉": {
        "goal": "验证相干光叠加规律，探究波长、缝距和屏距如何共同决定条纹间距。",
        "principle": "两缝作为相干次波源；屏上各点因光程差不同形成周期性明暗条纹。",
        "formula": "Δx ≈ λD / d；I = Ienv[1 + γcosδ]/2",
        "prediction": "增大波长或屏距，条纹变疏；增大缝距，条纹变密；降低相干性，条纹对比度下降。",
        "task": "只改变缝距，记录三组条纹间距，验证 Δx 与 d 的反比关系。",
    },
    "单缝衍射": {
        "goal": "观察中央明纹与次级明纹，建立缝宽和衍射尺度之间的关系。",
        "principle": "狭缝内各次波相干叠加，在满足特定光程差时形成暗纹。",
        "formula": "a·sinθ = kλ；中央明纹宽度约为 2λD/a",
        "prediction": "波长或屏距增大，中央明纹变宽；缝宽增大，衍射范围收窄。",
        "task": "固定波长与屏距，改变缝宽并比较中央明纹宽度。",
    },
    "多缝光栅": {
        "goal": "理解多光束干涉如何形成尖锐主极大，并探究分辨本领。",
        "principle": "多缝干涉受单缝衍射包络调制；缝数决定主极大的锐度。",
        "formula": "d·sinθ = kλ；R = kN",
        "prediction": "缝数增加，主极大更尖锐；光栅常数减小，各级谱线分得更开。",
        "task": "比较 N=10 与 N=40 的强度曲线，解释峰宽变化。",
    },
    "迈克耳孙干涉": {
        "goal": "利用条纹移动放大微小位移，理解精密测量的基本方法。",
        "principle": "分束后的两束光往返不同光程，再次叠加形成干涉。",
        "formula": "ΔN = 2Δd / λ",
        "prediction": "镜面每移动半个波长，视场中移动一条条纹。",
        "task": "改变镜面位移，拟合条纹移动数与位移的线性关系。",
    },
    "薄膜干涉": {
        "goal": "解释膜层颜色和增透现象，区分等厚干涉与等倾干涉。",
        "principle": "薄膜上下表面反射光产生光程差，并可能伴随半波损失。",
        "formula": "Δ = 2nd·cosθ（结合反射相位突变判断明暗）",
        "prediction": "厚度、折射率或入射角变化都会改变干涉级次与强度分布。",
        "task": "寻找可使当前波长反射减弱的膜厚组合，并说明依据。",
    },
    "偏振干涉": {
        "goal": "观察偏振元件对光强和相位的控制，理解波片的作用。",
        "principle": "正交偏振分量经波片产生相位延迟，再由检偏器投影后发生叠加。",
        "formula": "Eout = R(θ)J(δ)R(-θ)Ein；I = |aᵀEout|²",
        "prediction": "改变检偏器或波片角度，输出光强和偏振态同步变化。",
        "task": "寻找消光位置与最大透光位置，比较 1/4 波片和 1/2 波片。",
    },
}

overview = experiment_overview[experiment_mode]

def wavelength_to_css(wavelength_nm):
    """Return an approximate visible-spectrum color for the virtual beam."""
    if wavelength_nm < 450:
        return "#7c3aed"
    if wavelength_nm < 495:
        return "#2563eb"
    if wavelength_nm < 570:
        return "#10b981"
    if wavelength_nm < 590:
        return "#eab308"
    if wavelength_nm < 620:
        return "#f97316"
    return "#ef4444"

def wavelength_to_rgb(wavelength_nm):
    """Approximate an sRGB color for a monochromatic visible beam."""
    wavelength_nm = float(np.clip(wavelength_nm, 380, 780))
    if wavelength_nm < 440:
        red, green, blue = -(wavelength_nm - 440) / 60, 0.0, 1.0
    elif wavelength_nm < 490:
        red, green, blue = 0.0, (wavelength_nm - 440) / 50, 1.0
    elif wavelength_nm < 510:
        red, green, blue = 0.0, 1.0, -(wavelength_nm - 510) / 20
    elif wavelength_nm < 580:
        red, green, blue = (wavelength_nm - 510) / 70, 1.0, 0.0
    elif wavelength_nm < 645:
        red, green, blue = 1.0, -(wavelength_nm - 645) / 65, 0.0
    else:
        red, green, blue = 1.0, 0.0, 0.0
    if wavelength_nm < 420:
        factor = 0.3 + 0.7 * (wavelength_nm - 380) / 40
    elif wavelength_nm > 700:
        factor = 0.3 + 0.7 * (780 - wavelength_nm) / 80
    else:
        factor = 1.0
    return tuple(np.clip(np.array([red, green, blue]) * factor, 0, 1))

def optical_cmap(wavelength_nm):
    rgb = wavelength_to_rgb(wavelength_nm)
    return LinearSegmentedColormap.from_list("monochromatic_light", [(0, 0, 0), rgb], N=256)


@st.cache_resource
def load_uniform_diagram(path):
    """Place apparatus images on one consistent 16:8 presentation canvas."""
    with Image.open(path) as source:
        diagram = source.convert("RGB")
    resampling = getattr(Image, "Resampling", Image).LANCZOS
    diagram.thumbnail((1480, 680), resampling)
    canvas = Image.new("RGB", (1600, 760), "#f8fafc")
    offset = ((canvas.width - diagram.width) // 2, (canvas.height - diagram.height) // 2)
    canvas.paste(diagram, offset)
    return canvas

st.markdown(f"""
<div class="principle-panel">
    <b style="color:#0f766e; letter-spacing:.08em;">01 实验目标 · {experiment_mode}</b>
    <h3 style="margin:.35rem 0 .45rem 0; color:#0f172a;">{overview['goal']}</h3>
    <div style="color:#475569;"><b>物理原理：</b>{overview['principle']}</div>
    <div class="formula-focus">{overview['formula']}</div>
    <div style="color:#475569; margin-top:10px;"><b>调参前预测：</b>{overview['prediction']}</div>
</div>
""", unsafe_allow_html=True)

if user_role == "教师教学端":
    st.markdown("### 🧑‍🏫 教师教学工作台")
    teacher_col1, teacher_col2, teacher_col3 = st.columns([1.1, 1.2, 1])
    with teacher_col1:
        st.info(f"**本课核心目标**\n\n{overview['goal']}")
    with teacher_col2:
        st.success(f"**课堂探究任务**\n\n{overview['task']}")
    with teacher_col3:
        class_phase = st.selectbox("课堂环节", ["现象导入", "规律建构", "变量探究", "证据交流", "拓展设计"])
        demonstration_time = st.slider("单环节建议时长（分钟）", 1, 8, 3)
        st.caption(f"当前：{class_phase} · 建议 {demonstration_time} 分钟后切换活动")
    with st.expander("课堂演示脚本与评价记录", expanded=False):
        script_col, record_col = st.columns(2)
        with script_col:
            st.markdown(f"""
            **精简演示脚本**

            1. 用一句话提出问题：{overview['prediction']}
            2. 只改变一个关键变量，观察仪器、曲线和图样同步变化。
            3. 用核心公式解释结果，不重复介绍平台优势。
            4. 让学生完成任务：{overview['task']}
            """)
        with record_col:
            st.text_area("课堂观察 / 学生证据", placeholder="记录学生预测、测量结果和典型解释……", height=155)

# Controls are followed by a full-width live canvas. This keeps them together
# while giving the simulation the complete page width.
col1 = st.container()
col2 = st.container()

intensity = None
phase_diff = None
info = None
original_intensity = None
noise_info = None
live_effect = ""

with col1:
    st.markdown("""
    <div class="section-heading">
        <span class="section-number">02</span>
        <div><strong>参数调节</strong><small>改变任意参数，观察屏和定量曲线立即同步更新</small></div>
    </div>
    """, unsafe_allow_html=True)

    if experiment_mode == "双缝干涉":
        controls = st.columns(5)
        with controls[0]:
            wavelength = st.slider("波长 (nm)", 400, 760, 540, 10, help="可见光范围：400-760nm") * 1e-9
        with controls[1]:
            slit_distance = st.slider("缝距 (mm)", 0.1, 1.0, 0.5, 0.05, help="双缝之间的距离") * 1e-3
        with controls[2]:
            slit_width = st.slider("单缝宽度 (mm)", 0.02, 0.20, 0.08, 0.01, help="决定干涉条纹的衍射包络") * 1e-3
        with controls[3]:
            screen_distance = st.slider("屏距 (m)", 1.0, 5.0, 1.0, 0.1, help="双缝到屏幕的距离")
        with controls[4]:
            coherence = st.slider("光源相干性", 0.5, 1.0, 1.0, 0.05, help="0为完全非相干，1为完全相干")
        refractive_index = 1.0
        incident_angle = 0.0
        
        # A fixed physical field of view makes spacing changes directly visible.
        screen_width = 20e-3
        
        x, original_intensity, phase_diff, info = calculator.double_slit_interference(
            wavelength=wavelength,
            slit_distance=slit_distance,
            screen_distance=screen_distance,
            screen_width=screen_width,
            refractive_index=refractive_index,
            slit_width=slit_width,
            incident_angle=np.radians(incident_angle),
            coherence=coherence
        )
        
        if enable_error:
            intensity, noise_info = calculator.add_noise(
                original_intensity, systematic_error, random_error, 
                ambient_light=ambient_light, detector_noise=detector_noise
            )
        else:
            intensity = original_intensity

        metric_cols = st.columns(3)
        metric_cols[0].metric("条纹间距", f"{info['fringe_spacing']*1000:.4f} mm")
        metric_cols[1].metric("中央包络宽度", f"{info['central_envelope_width']*1000:.3f} mm")
        metric_cols[2].metric("条纹对比度", f"{info['contrast']:.3f}")
        live_effect = (
            f"当前条纹间距 {info['fringe_spacing']*1e3:.2f} mm；"
            "增大波长或屏距会使条纹明显变疏，增大缝距会使条纹变密。"
        )

    elif experiment_mode == "单缝衍射":
        controls = st.columns(3)
        with controls[0]:
            wavelength = st.slider("波长 (nm)", 400, 760, 600, 10) * 1e-9
        with controls[1]:
            slit_width = st.slider("缝宽 (mm)", 0.02, 0.5, 0.1, 0.01) * 1e-3
        with controls[2]:
            screen_distance = st.slider("屏距 (m)", 1.0, 5.0, 1.0, 0.1)
        refractive_index = 1.0
        incident_angle = 0.0
        
        # Keep the same 30 mm screen while parameters change so the central
        # maximum visibly expands or contracts instead of being auto-fitted.
        screen_width = 30e-3
        
        x, original_intensity, phase_diff, info = calculator.single_slit_diffraction(
            wavelength=wavelength,
            slit_width=slit_width,
            screen_distance=screen_distance,
            screen_width=screen_width,
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
        
        metric_cols = st.columns(2)
        metric_cols[0].metric("第一暗纹角度", f"{info['first_min_angle']:.2f}°")
        metric_cols[1].metric("中央明纹宽度", f"{info['central_max_width']*1000:.3f} mm")
        live_effect = (
            f"中央明纹当前宽约 {info['central_max_width']*1e3:.2f} mm；"
            "减小缝宽时中央亮斑会迅速展宽，旁瓣位置也会同步外移。"
        )

    elif experiment_mode == "多缝光栅":
        controls = st.columns(5)
        with controls[0]:
            wavelength = st.slider("波长 (nm)", 400, 760, 500, 10) * 1e-9
        with controls[1]:
            slit_distance = st.slider("光栅常数 (μm)", 5, 50, 20, 1) * 1e-6
        with controls[2]:
            num_slits = st.slider("缝数", 5, 50, 10, 1)
        with controls[3]:
            slit_width = st.slider("缝宽 (μm)", 1, 25, 10, 1) * 1e-6
        with controls[4]:
            screen_distance = st.slider("屏距 (m)", 1.0, 5.0, 1.0, 0.1)
        refractive_index = 1.0
        incident_angle = 0.0
        
        # A fixed 200 mm detector makes order spacing and peak sharpening clear.
        screen_width = 200e-3
        
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
        
        metric_cols = st.columns(4)
        metric_cols[0].metric("光栅常数", f"{slit_distance*1e6:.0f} μm")
        metric_cols[1].metric("最大衍射级次", info['max_order'])
        metric_cols[2].metric("一级分辨本领", info['resolving_power_first_order'])
        metric_cols[3].metric("线密度", f"{info['line_density']:.1f} 条/mm")
        live_effect = (
            f"当前一级分辨本领为 {info['resolving_power_first_order']}；"
            "增加缝数会让主峰显著变窄，改变光栅常数会移动各级主峰。"
        )

    elif experiment_mode == "迈克耳孙干涉":
        controls = st.columns(3)
        with controls[0]:
            wavelength = st.slider("波长 (nm)", 400, 760, 550, 10) * 1e-9
        with controls[1]:
            mirror_displacement = st.slider("镜面移动距离 (μm)", 0.0, 10.0, 2.5, 0.1) * 1e-6
        with controls[2]:
            beam_ratio = st.slider("两束光强度比", 0.1, 1.0, 0.5, 0.1)
        num_fringes = 20
        refractive_index = 1.0
        
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
        
        metric_cols = st.columns(3)
        metric_cols[0].metric("条纹移动数", f"{info['fringe_shift']:.2f}")
        metric_cols[1].metric("光程差变化", f"{info['optical_path_difference']*1e6:.2f} μm")
        metric_cols[2].metric("条纹可见度", f"{info['fringe_visibility']:.3f}")
        live_effect = (
            f"反射镜移动 {mirror_displacement*1e6:.1f} μm，条纹已移动 {info['fringe_shift']:.2f} 条；"
            "镜面每移动半个波长，视场就完成一次明暗循环。"
        )

    elif experiment_mode == "薄膜干涉":
        controls = st.columns(5)
        with controls[0]:
            wavelength = st.slider("波长 (nm)", 400, 760, 550, 10) * 1e-9
        with controls[1]:
            film_thickness = st.slider("薄膜厚度 (nm)", 100, 2000, 500, 50) * 1e-9
        with controls[2]:
            n_film = st.slider("薄膜折射率", 1.0, 2.0, 1.5, 0.05)
        with controls[3]:
            n_substrate = st.slider("基底折射率", 1.0, 2.0, 1.5, 0.05)
        with controls[4]:
            interference_type = st.radio("干涉类型", ["等厚干涉", "等倾干涉"])
        incident_angle = 0
        
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
        
        metric_cols = st.columns(4)
        metric_cols[0].metric("薄膜厚度", f"{film_thickness*1e9:.0f} nm")
        metric_cols[1].metric("干涉类型", info['interference_type'])
        metric_cols[2].metric("相位突变", "π" if info['phase_shift'] > 0 else "0")
        metric_cols[3].metric("当前反射强度", f"{info['current_reflectance']:.3f}")
        live_effect = (
            f"当前反射强度为 {info['current_reflectance']:.3f}；"
            "膜厚或折射率改变会直接改变光程差，使反射光在明暗之间切换。"
        )

    elif experiment_mode == "偏振干涉":
        controls = st.columns(5)
        with controls[0]:
            wavelength = st.slider("波长 (nm)", 400, 760, 550, 10) * 1e-9
        with controls[1]:
            polarizer_angle = st.slider("起偏器角度 (°)", 0, 180, 0, 5)
        with controls[2]:
            analyzer_angle = st.slider("检偏器角度 (°)", 0, 180, 90, 5)
        with controls[3]:
            waveplate_angle = st.slider("波片角度 (°)", 0, 180, 45, 5)
        with controls[4]:
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
        
        metric_cols = st.columns(4)
        metric_cols[0].metric("输出偏振态", info['polarization_state'])
        metric_cols[1].metric("当前透射光强", f"{info['current_intensity']:.4f}")
        metric_cols[2].metric("椭圆率角", f"{info['ellipticity_angle']:.2f}°")
        metric_cols[3].metric("相位延迟", f"{info['phase_retardation']:.1f}°")
        live_effect = (
            f"当前为{info['polarization_state']}，透射光强 {info['current_intensity']:.3f}；"
            "旋转检偏器可直接观察马吕斯定律的周期性明暗变化。"
        )

with col2:
    st.markdown("""
    <div class="section-heading">
        <span class="section-number">03</span>
        <div><strong>仪器 · 图像 · 数据联动</strong><small>先观察现象，再用曲线和特征量解释变化</small></div>
    </div>
    """, unsafe_allow_html=True)
    st.info(f"**实时现象：** {live_effect}")
    st.markdown("""
    <div class="link-panel">
        <div class="link-flow">参数控制 → 虚拟仪器状态 → 强度曲线 → 屏上图样 → 特征量</div>
    </div>
    """, unsafe_allow_html=True)

    beam_color = wavelength_to_css(wavelength * 1e9)
    if experiment_mode == "双缝干涉":
        device_name = "可调双缝"
        device_state = f"缝距 {slit_distance*1e3:.2f} mm"
        screen_state = f"条纹间距 {info['fringe_spacing']*1e3:.3f} mm"
    elif experiment_mode == "单缝衍射":
        device_name = "可调单缝"
        device_state = f"缝宽 {slit_width*1e3:.3f} mm"
        screen_state = f"中央明纹 {info['central_max_width']*1e3:.2f} mm"
    elif experiment_mode == "多缝光栅":
        device_name = "多缝光栅"
        device_state = f"{num_slits} 缝 · d={slit_distance*1e6:.0f} μm"
        screen_state = f"一级分辨本领 {info['resolving_power_first_order']}"
    elif experiment_mode == "迈克耳孙干涉":
        device_name = "移动反射镜"
        device_state = f"位移 {mirror_displacement*1e6:.1f} μm"
        screen_state = f"移动 {info['fringe_shift']:.2f} 条"
    elif experiment_mode == "薄膜干涉":
        device_name = "可调薄膜"
        device_state = f"厚度 {film_thickness*1e9:.0f} nm · n={n_film:.2f}"
        screen_state = f"{info['interference_type']}"
    else:
        device_name = waveplate_type
        device_state = f"波片 {waveplate_angle}° · 检偏器 {analyzer_angle}°"
        screen_state = f"{info['polarization_state']} · I={info['current_intensity']:.3f}"

    st.markdown(f"""
    <div class="instrument-stage">
        <div class="instrument-node"><small>光源</small><div class="instrument-value">{wavelength*1e9:.0f} nm</div></div>
        <div>
            <div class="beam-line" style="color:{beam_color}; background:{beam_color};"></div>
            <div class="instrument-node" style="margin-top:14px;"><small>{device_name}</small><div class="instrument-value">{device_state}</div></div>
        </div>
        <div class="instrument-node"><small>观测屏 / 探测器</small><div class="instrument-value">{screen_state}</div></div>
    </div>
    """, unsafe_allow_html=True)

    diagram_files = {
        "双缝干涉": "微信图片_20260626165435_1415_1.png",
        "单缝衍射": "微信图片_20260626170035_1416_1.png",
        "迈克耳孙干涉": "ae7563b893900f4e5076e869392055bd.jpg",
        "多缝光栅": "微信图片_20260626204545_1417_1.png",
        "薄膜干涉": "微信图片_20260626204819_1418_1.png",
        "偏振干涉": "微信图片_20260626204946_1419_1.png",
    }
    with st.expander("查看实验光路与装置结构", expanded=False):
        st.image(
            load_uniform_diagram(diagram_files[experiment_mode]),
            use_container_width=True,
            caption=f"{experiment_mode}光路示意",
        )

    if intensity is not None:
        if experiment_mode in ["双缝干涉", "单缝衍射", "多缝光栅"]:
            rows = 3 if show_phase else 2
            fig = plt.figure(figsize=(14, 11.2 if show_phase else 9.8), dpi=120, facecolor="#ffffff")
            grid = fig.add_gridspec(
                rows,
                1,
                height_ratios=[2.3, 1.0, 0.82] if show_phase else [2.3, 1.0],
                hspace=0.31,
            )
            x_mm = x * 1000
            # 先展示观察屏图像，再展示位置/强度曲线，和实验观察顺序一致。
            ax_screen = fig.add_subplot(grid[0])
            # Darken low-intensity regions slightly so fringe movement and
            # contrast changes remain obvious on classroom projectors.
            display_intensity = np.power(np.clip(intensity, 0, 1), 1.35)
            screen_image = np.tile(display_intensity, (320, 1))
            ax_screen.imshow(screen_image, extent=[x_mm[0], x_mm[-1], 0, 1], aspect='auto', cmap=optical_cmap(wavelength * 1e9), interpolation='bilinear', vmin=0, vmax=1)
            ax_screen.set_xlabel('屏上位置 (mm)')
            ax_screen.set_yticks([])
            ax_screen.set_title('放大观察屏（固定物理视场）', loc='left', fontsize=13, fontweight='bold')

            ax1 = fig.add_subplot(grid[1])
            ax1.plot(x_mm, intensity, linewidth=2.2, color=beam_color)
            ax1.fill_between(x_mm, intensity, color=beam_color, alpha=0.18)
            ax1.set_ylabel('相对光强')
            ax1.set_title(f'{experiment_mode}：位置—强度曲线', loc='left', fontweight='bold')
            ax1.grid(True, alpha=0.2)
            ax1.set_ylim(0, 1.05)
            if show_theory_marks and experiment_mode == "双缝干涉":
                spacing_mm = info['fringe_spacing'] * 1000
                for order in range(-3, 4):
                    ax1.axvline(order * spacing_mm, color='#0f766e', alpha=0.22, linestyle='--')
            elif show_theory_marks and experiment_mode == "单缝衍射":
                for position in info['dark_positions'][:3]:
                    ax1.axvline(position * 1000, color='#dc2626', alpha=0.35, linestyle='--')
                    ax1.axvline(-position * 1000, color='#dc2626', alpha=0.35, linestyle='--')
            elif show_theory_marks and experiment_mode == "多缝光栅":
                for position in info['peak_positions']:
                    if x[0] <= position <= x[-1]:
                        ax1.axvline(position * 1000, color='#0f766e', alpha=0.22, linestyle='--')

            if not show_phase:
                ax1.set_xlabel('屏上位置 (mm)')
            else:
                ax1.set_xlabel('屏上位置 (mm)')
                ax3 = fig.add_subplot(grid[2])
                ax3.plot(x_mm, np.unwrap(phase_diff), color='#7c3aed', linewidth=1.6)
                ax3.set_xlabel('屏上位置 (mm)')
                ax3.set_ylabel('相位差 (rad)')
                ax3.grid(True, alpha=0.2)
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)

        elif experiment_mode == "偏振干涉":
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7.2), dpi=120, facecolor="#ffffff")
            analyzer_deg = np.degrees(x)
            ax1.plot(analyzer_deg, intensity, color=beam_color, linewidth=2.4)
            ax1.axvline(analyzer_angle, color='#dc2626', linestyle='--', label='当前检偏器角度')
            ax1.scatter([analyzer_angle], [info['current_intensity']], color='#dc2626', zorder=4)
            ax1.set_xlabel('检偏器角度 (°)')
            ax1.set_ylabel('透射光强')
            ax1.set_title('检偏器扫描曲线', fontweight='bold')
            ax1.set_ylim(0, 1.05)
            ax1.grid(True, alpha=0.2)
            ax1.legend()

            azimuth = np.radians(info['polarization_azimuth'])
            ellipticity = np.tan(np.radians(info['ellipticity_angle']))
            t = np.linspace(0, 2 * np.pi, 400)
            ellipse = np.vstack((np.cos(t), ellipticity * np.sin(t)))
            rotation = np.array([[np.cos(azimuth), -np.sin(azimuth)], [np.sin(azimuth), np.cos(azimuth)]])
            ellipse = rotation @ ellipse
            ax2.plot(ellipse[0], ellipse[1], color=beam_color, linewidth=2.8)
            ax2.axhline(0, color='#cbd5e1', linewidth=1)
            ax2.axvline(0, color='#cbd5e1', linewidth=1)
            ax2.set_aspect('equal')
            ax2.set_xlim(-1.1, 1.1)
            ax2.set_ylim(-1.1, 1.1)
            ax2.set_xlabel('Ex')
            ax2.set_ylabel('Ey')
            ax2.set_title(f"偏振椭圆：{info['polarization_state']}", fontweight='bold')
            plt.tight_layout()
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)
        
        elif experiment_mode == "迈克耳孙干涉":
            fig = plt.figure(figsize=(14, 10.0), dpi=120, facecolor="#ffffff")
            ax1 = fig.add_subplot(2, 2, 1)
            ax1.fill_between(path_diff * 1e6, intensity, alpha=0.4)
            ax1.plot(path_diff * 1e6, intensity, linewidth=2.4, color=beam_color)
            ax1.set_xlabel('光程差 (μm)', fontsize=11, fontweight='bold')
            ax1.set_ylabel('相对强度', fontsize=11, fontweight='bold')
            ax1.set_title('条纹移动的定量证据', loc='left', fontweight='bold')
            ax1.grid(True, alpha=0.3, linestyle='--')
            ax1.set_ylim(0, 1.1)

            ax_ring = fig.add_subplot(2, 2, 2)
            grid_axis = np.linspace(-1, 1, 360)
            grid_x, grid_y = np.meshgrid(grid_axis, grid_axis)
            radius_squared = grid_x ** 2 + grid_y ** 2
            ring_phase = 22 * np.pi * radius_squared + 4 * np.pi * mirror_displacement / wavelength
            rings = 0.5 * (1 + info['fringe_visibility'] * np.cos(ring_phase))
            ax_ring.imshow(rings, extent=[-1, 1, -1, 1], cmap=optical_cmap(wavelength * 1e9), origin='lower', vmin=0, vmax=1)
            ax_ring.set_title('等倾干涉同心圆视场', fontweight='bold')
            ax_ring.set_xticks([])
            ax_ring.set_yticks([])

            ax2 = fig.add_subplot(2, 1, 2)
            y_img = np.linspace(0, 1, 150)
            Z = np.tile(np.power(np.clip(intensity, 0, 1), 1.35), (220, 1))
            ax2.imshow(Z, extent=[path_diff[0]*1e6, path_diff[-1]*1e6, 0, 1], aspect='auto', cmap=optical_cmap(wavelength * 1e9), interpolation='bilinear', vmin=0, vmax=1)
            ax2.set_xlabel('光程差 (μm)', fontsize=11, fontweight='bold')
            ax2.set_yticks([])
            ax2.set_title('探测器接收的单色条纹', loc='left', fontsize=11)
            
            plt.tight_layout(pad=1.5)
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)
        
        elif experiment_mode == "薄膜干涉":
            fig = plt.figure(figsize=(14, 10.0), dpi=120, facecolor="#ffffff")
            
            ax1 = fig.add_subplot(2, 1, 1)
            plot_x = x * 1e9 if info['interference_type'] == '等厚干涉' else np.degrees(x)
            ax1.plot(plot_x, intensity, linewidth=2.4, color=beam_color)
            ax1.set_xlabel('厚度 (nm)' if info['interference_type'] == '等厚干涉' else '入射角 (°)', fontsize=11, fontweight='bold')
            ax1.set_ylabel('相对强度', fontsize=11, fontweight='bold')
            ax1.set_title('薄膜反射强度的定量变化', loc='left', fontweight='bold')
            if info['interference_type'] == '等厚干涉':
                ax1.axvline(film_thickness * 1e9, color='#dc2626', linestyle='--', label='当前膜厚')
                ax1.scatter([film_thickness * 1e9], [info['current_reflectance']], color='#dc2626', zorder=4)
                ax1.legend()
            ax1.grid(True, alpha=0.3, linestyle='--')
            ax1.set_ylim(0, 1.1)
            
            ax2 = fig.add_subplot(2, 1, 2)
            y_img = np.linspace(0, 1, 150)
            Z = np.tile(np.power(np.clip(intensity, 0, 1), 1.35), (220, 1))
            ax2.imshow(Z, extent=[x[0]*1e9 if info['interference_type'] == '等厚干涉' else 0,
                                       x[-1]*1e9 if info['interference_type'] == '等厚干涉' else 60, 0, 1], 
                           aspect='auto', cmap=optical_cmap(wavelength * 1e9), interpolation='bilinear', vmin=0, vmax=1)
            ax2.set_xlabel('厚度 (nm)' if info['interference_type'] == '等厚干涉' else '入射角 (°)', fontsize=11, fontweight='bold')
            ax2.set_yticks([])
            ax2.set_title('单色反射光的明暗分布', loc='left', fontsize=11)
            
            plt.tight_layout(pad=1.5)
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)

st.markdown("---")

st.markdown(f"""
<div class="section-heading">
    <span class="section-number">04</span>
    <div><strong>数据证据与拓展探究</strong><small>本次探究：{overview['task']}</small></div>
</div>
""", unsafe_allow_html=True)

if enable_error and original_intensity is not None and intensity is not None:
    error_info = calculator.calculate_error(intensity, original_intensity)
    
    col3, col4, col5 = st.columns(3)
    with col3:
        st.metric("均方根误差", f"{error_info['root_mean_square_error']:.4f}")
    with col4:
        st.metric("最大误差", f"{error_info['max_error']:.4f}")
    with col5:
        st.metric("相对误差", f"{error_info['error_percentage']:.2f}%")
else:
    evidence_cols = st.columns(3)
    evidence_cols[0].metric("模型状态", "理想理论模型")
    evidence_cols[1].metric("采样点数", f"{len(intensity):,}")
    evidence_cols[2].metric("当前实验", experiment_mode)

st.markdown("#### 📥 数据导出")
if st.button("导出数据为Excel"):
    if experiment_mode in ["双缝干涉", "单缝衍射", "多缝光栅"]:
        df = pd.DataFrame({
            '位置_mm': x * 1000,
            '相对强度': intensity,
            '相位差_rad': phase_diff if phase_diff is not None else np.nan,
            '光程差_m': info.get('path_difference', np.nan)[:len(intensity)] if isinstance(info.get('path_difference'), np.ndarray) else np.nan
        })
    elif experiment_mode == "偏振干涉":
        df = pd.DataFrame({
            '检偏器角度_deg': np.degrees(x),
            '透射光强': intensity,
            '波片相位延迟_rad': phase_diff
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

with st.expander("📖 完整物理推导（需要时展开）"):
    if experiment_mode == "双缝干涉":
        st.markdown("""
        **双缝干涉原理**
        
        当一束相干光通过两个平行狭缝后，会在屏幕上形成明暗相间的干涉条纹。
        
        **核心公式：**
        """)
        st.markdown('<div class="formula-box">光程差：Δ = d·sinθ<br>相位差：δ = 2πΔ/λ<br>部分相干强度：I = I₀[1 + γcosδ]/2<br>有限缝宽包络：I<sub>env</sub> = sinc²(πa·sinθ/λ)<br>条纹间距：Δx ≈ λD/d</div>', unsafe_allow_html=True)
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
        st.markdown('<div class="formula-box">β = πa·sinθ/λ<br>光强分布：I = I₀(sinβ/β)²<br>暗纹条件：a·sinθ = kλ (k=±1, ±2, ...)<br>小角度下中央明纹宽度：w ≈ 2λD/a</div>', unsafe_allow_html=True)
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
        st.markdown('<div class="formula-box">α = πd·sinθ/λ，β = πa·sinθ/λ<br>归一化强度：I/I₀ = sinc²(β/π)[sin(Nα)/(Nsinα)]²<br>主极大：d·sinθ = kλ<br>第 k 级分辨本领：R = kN</div>', unsafe_allow_html=True)
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
        st.markdown('<div class="formula-box">膜内折射角满足：n₀sinθ₀ = nsinθ<br>几何光程差：Δ = 2nd·cosθ<br>总相位差：δ = 2πΔ/λ + Δφ<sub>r</sub><br>Δφ<sub>r</sub>由两个反射界面的半波损失之差决定</div>', unsafe_allow_html=True)
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
        st.markdown('<div class="formula-box">波片相位延迟：δ = 2π(nₑ-nₒ)d/λ<br>琼斯变换：E<sub>out</sub> = R(θ)diag(1,e<sup>iδ</sup>)R(-θ)E<sub>in</sub><br>检偏器透射：I = |a<sup>T</sup>E<sub>out</sub>|²</div>', unsafe_allow_html=True)
        st.markdown("""
        **物理现象：**
        线偏振光通过1/4波片可变为椭圆偏振光或圆偏振光；
        通过1/2波片可改变偏振方向。
        
        **琼斯矩阵方法：**
        利用琼斯矩阵可以精确计算偏振光经过光学元件后的状态变化。
        """)

if mode_type == "教学模式":
    with st.expander("📚 分层探究与实验拓展", expanded=user_role == "教师教学端"):
        guide_col1, guide_col2, guide_col3 = st.columns(3)
        with guide_col1:
            st.markdown(f"**基础验证**\n\n观察默认图样，指出最明显的结构特征，并用 `{overview['formula']}` 解释。")
        with guide_col2:
            st.markdown(f"**变量探究**\n\n{overview['task']}")
        with guide_col3:
            st.markdown("**创新设计**\n\n加入误差或非理想因素，提出一种改进测量精度、扩大测量范围或迁移到真实应用的方案。")

        st.markdown("#### 探究记录（用证据代替长篇报告）")
        record1, record2, record3 = st.columns(3)
        with record1:
            prediction_record = st.text_input("我的预测", placeholder="变量改变后，图样将……")
        with record2:
            evidence_record = st.text_input("关键证据", placeholder="记录一组数值或图像特征")
        with record3:
            conclusion_record = st.text_input("一句话结论", placeholder="数据表明……")

        if st.button("保存本次探究记录", key="save_inquiry_record"):
            st.session_state.setdefault("inquiry_records", []).append({
                "实验": experiment_mode,
                "预测": prediction_record,
                "证据": evidence_record,
                "结论": conclusion_record,
            })
            st.success("已保存为简洁实验记录。")

        if st.session_state.get("inquiry_records"):
            st.dataframe(pd.DataFrame(st.session_state.inquiry_records), use_container_width=True)

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
st.markdown("### ℹ️ 快速使用")
st.markdown("""
按“原理与公式 → 参数调节 → 联动观察 → 数据证据”的顺序完成实验。需要深入推导、误差分析、数据导出或智能问答时，再展开对应工具。
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
    st.markdown("## 🤖 智能助手")
    if hasattr(agent, "refresh_environment_config"):
        agent.refresh_environment_config()
    
    # API连接状态显示和测试
    st.markdown("**🔌 API连接状态：**")
    col_status1, col_status2 = st.columns([2, 1])
    with col_status1:
        if hasattr(agent, 'api_status'):
            status_colors = {
                "connected": "🟢",
                "ready": "🟢",
                "disconnected": "🔴",
                "timeout": "🟡",
                "error": "🔴",
                "unknown": "⚪"
            }
            status_texts = {
                "connected": "已连接",
                "ready": "系统 API 已配置",
                "disconnected": "未连接",
                "timeout": "连接超时",
                "error": "连接错误",
                "unknown": "未知状态"
            }
            st.markdown(f"""
            <div style="padding: 12px 14px; border-radius: 8px; color:#0f172a; background-color: {'#dcfce7' if agent.api_status in ['connected', 'ready'] else '#fee2e2'};">
                {status_colors.get(agent.api_status, '⚪')} <strong>{status_texts.get(agent.api_status, '未知')}</strong>
            </div>
            """, unsafe_allow_html=True)
            if hasattr(agent, "api_source"):
                st.caption(f"配置来源：{agent.api_source}｜模型：{getattr(agent, 'model_name', '')}")
            
            if agent.api_error_message:
                st.warning(f"⚠️ {agent.api_error_message}")
    with col_status2:
        if hasattr(agent, 'test_api_connection'):
            if st.button("🔍 测试连接", key="test_api"):
                with st.spinner("正在测试连接..."):
                    success = agent.test_api_connection()
                    if success:
                        st.success("✅ API连接成功！")
                    else:
                        st.error(f"❌ 连接失败：{agent.api_error_message}")
    
    st.markdown("---")
    
    # 传递实验上下文给智能体
    if hasattr(agent, 'set_experiment_context'):
        current_params = {}
        if experiment_mode == "双缝干涉":
            current_params = {
                "波长": f"{wavelength*1e9:.0f} nm",
                "缝距": f"{slit_distance*1e3:.3f} mm",
                "屏距": f"{screen_distance} m"
            }
        elif experiment_mode == "单缝衍射":
            current_params = {
                "波长": f"{wavelength*1e9:.0f} nm",
                "缝宽": f"{slit_width*1e3:.3f} mm",
                "屏距": f"{screen_distance} m"
            }
        elif experiment_mode == "多缝光栅":
            current_params = {
                "波长": f"{wavelength*1e9:.0f} nm",
                "光栅常数": f"{slit_distance*1e6:.0f} μm",
                "缝数": num_slits
            }
        elif experiment_mode == "迈克耳孙干涉":
            current_params = {
                "波长": f"{wavelength*1e9:.0f} nm",
                "镜面移动": f"{mirror_displacement*1e6:.1f} μm",
                "条纹数": num_fringes
            }
        elif experiment_mode == "薄膜干涉":
            current_params = {
                "波长": f"{wavelength*1e9:.0f} nm",
                "薄膜厚度": f"{film_thickness*1e9:.0f} nm",
                "折射率": f"{n_film:.3f}"
            }
        elif experiment_mode == "偏振干涉":
            current_params = {
                "波长": f"{wavelength*1e9:.0f} nm",
                "起偏器角度": f"{polarizer_angle}°",
                "检偏器角度": f"{analyzer_angle}°",
                "波片类型": waveplate_type
            }
        agent.set_experiment_context(experiment_mode, current_params)
    
    is_enhanced = hasattr(agent, 'switch_mode')
    
    # 智能体模式切换
    if is_enhanced:
        st.markdown("**🎯 对话模式：**")
        agent_mode = st.radio(
            "选择对话模式",
            ["🔬 物理问答", "💬 通用对话"],
            horizontal=True,
            help="物理问答：专注波动光学问题 | 通用对话：回答各种问题"
        )
        
        if "物理" in agent_mode:
            agent.switch_mode("physics")
        else:
            agent.switch_mode("general")
        
        st.markdown("---")
    
    # 当前实验信息
    if is_enhanced and hasattr(agent, 'current_experiment') and agent.current_experiment:
        st.markdown(f"""
        <div class="info-box">
            📌 当前实验：**{agent.current_experiment}**
        </div>
        """, unsafe_allow_html=True)
        
        if hasattr(agent, 'suggest_parameters'):
            suggestion = agent.suggest_parameters()
            if suggestion:
                st.markdown(suggestion)
        
        st.markdown("---")
    
    st.markdown("**⚙️ 系统 API 配置：**")
    if getattr(agent, "api_type", "dashscope") == "dashscope":
        if getattr(agent, "_environment_api_key", ""):
            env_name = getattr(agent, "api_key_env_name", "DASHSCOPE_API_KEY")
            st.success(f"已自动加载系统环境变量 {env_name}，无需手动填写 API Key。")
        else:
            st.error("未检测到系统环境变量 DASHSCOPE_API_KEY，请在系统环境中配置后重新启动程序。")
    else:
        st.success("已从系统环境变量加载本地模型配置。")
    st.caption(
        f"服务类型：{getattr(agent, 'api_type', 'dashscope')}｜"
        f"模型：{getattr(agent, 'model_name', '')}｜密钥不会在页面中显示或保存"
    )
    
    st.markdown("---")
    
    # 显示对话历史
    chat_container = st.container()
    with chat_container:
        st.markdown("**💬 对话历史：**")
        history = []
        if hasattr(agent, 'conversation_history'):
            history = agent.conversation_history
        elif hasattr(agent, 'get_history'):
            history = agent.get_history()
        
        if not history:
            st.info("👋 还没有对话记录，开始提问吧！")
        else:
            for msg in history:
                role = "user" if msg.get("role") == "user" else "assistant"
                content = str(msg.get("content", ""))
                # Streamlit Markdown renders $...$ and $$...$$ through KaTeX.
                # Normalize the other common LaTeX delimiters returned by models.
                content = content.replace(r"\[", "$$").replace(r"\]", "$$")
                content = content.replace(r"\(", "$").replace(r"\)", "$")
                with st.chat_message(role):
                    st.markdown(content)
    
    st.markdown("---")
    
    # 用户输入
    def submit_agent_question(question=None):
        prompt = question if question is not None else st.session_state.get("agent_input", "")
        prompt = (prompt or "").strip()
        if not prompt:
            return
        agent.generate_response(prompt)
        if question is None:
            st.session_state["agent_input"] = ""

    def clear_agent_conversation():
        if hasattr(agent, 'clear_history'):
            agent.clear_history()
        elif hasattr(agent, 'conversation_history'):
            agent.conversation_history = []

    user_input = st.text_area(
        "💭 请输入您的问题：",
        placeholder="例如：双缝干涉的原理是什么？如何计算条纹间距？",
        key="agent_input",
        height=80
    )
    
    col_agent1, col_agent2 = st.columns([4, 1])
    with col_agent1:
        st.button(
            "🚀 发送",
            type="primary",
            key="send_msg",
            on_click=submit_agent_question,
            use_container_width=True,
        )
    
    with col_agent2:
        st.button(
            "🗑️ 清空",
            key="clear_chat",
            on_click=clear_agent_conversation,
            use_container_width=True,
        )
    
    # 快捷提问按钮
    st.markdown("**⚡ 快捷提问：**")
    
    quick_questions = []
    if is_enhanced and hasattr(agent, 'get_quick_questions'):
        quick_questions = agent.get_quick_questions()
    elif is_enhanced and hasattr(agent, 'current_mode'):
        if agent.current_mode == "physics":
            quick_questions = [
                "双缝干涉的原理是什么？",
                "单缝衍射的公式是什么？",
                "如何测量光波长？",
                "偏振态如何影响干涉？",
                "迈克耳孙干涉仪的应用"
            ]
        else:
            quick_questions = [
                "你能帮我做什么？",
                "如何学习物理？",
                "有什么好用的工具？",
                "怎样提高效率？",
                "解释一下干涉现象"
            ]
    else:
        quick_questions = [
            "双缝干涉的原理是什么？",
            "单缝衍射的公式是什么？",
            "如何测量光波长？",
            "偏振态如何影响干涉？",
            "迈克耳孙干涉仪的应用"
        ]
    
    cols = st.columns(min(5, len(quick_questions)))
    for i, q in enumerate(quick_questions):
        with cols[i]:
            st.button(
                q,
                key=f"quick_{i}",
                help=f"快速提问：{q}",
                on_click=submit_agent_question,
                args=(q,),
                use_container_width=True,
            )
    
    # 高级功能提示
    st.markdown("---")
    if not is_enhanced:
        st.info("💡 **提示**：安装 agent_module_v2.py 可获得增强版智能体，支持多种对话模式！")
    else:
        st.success("✨ 增强版智能体已启用！支持实验上下文感知和智能问答。")
