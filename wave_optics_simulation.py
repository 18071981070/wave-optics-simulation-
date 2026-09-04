import streamlit as st
import streamlit.components.v1 as components
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.font_manager import fontManager
from matplotlib.colors import LinearSegmentedColormap
import pandas as pd
from io import BytesIO
import os
import html
import json
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


# 桌面宠物：可拖动浮窗，显示当前操作 + 参数摘要 + 快捷按钮 + 动态提示
_PET_TIPS = {
    "双缝干涉": [
        "💡 调大波长或屏距，条纹变疏～",
        "💡 减小缝距，条纹会更稀疏哦～",
        "💡 降低相干性，条纹对比度下降～",
    ],
    "单缝衍射": [
        "💡 缝越窄，中央明纹越宽～",
        "💡 中央明纹宽度 ≈ 2λD/a～",
        "💡 次级明纹强度递减很快～",
    ],
    "多缝光栅": [
        "💡 缝数越多，主峰越尖锐～",
        "💡 分辨本领 R = kN～",
        "💡 注意观察缺级现象～",
    ],
    "迈克耳孙干涉": [
        "💡 动镜移动 λ/2，吞吐一个条纹～",
        "💡 等倾干涉是同心圆条纹～",
        "💡 白光干涉只在零级附近出现彩色～",
    ],
    "薄膜干涉": [
        "💡 注意反射有没有半波损失～",
        "💡 增透膜厚度常取 λ/4～",
        "💡 肥皂泡颜色来自薄膜干涉～",
    ],
    "偏振干涉": [
        "💡 检偏器旋转，光强按 cos²θ 变化～",
        "💡 1/4 波片可产生圆偏振光～",
        "💡 马吕斯定律：I = I₀cos²θ～",
    ],
}


def render_desktop_pet(experiment_mode, mode_type, user_role, params=None,
                        just_answered=False, agent_status="unknown", thinking=False):
    """升级版桌面宠物：可拖动、点击切换台词、折叠气泡、快捷按钮。
    使用 components.html 渲染（允许执行 JS），并把元素注入到父文档 body，
    使 position:fixed 相对主窗口而非 component iframe。"""
    tips = _PET_TIPS.get(experiment_mode, ["💡 试试调节参数，观察图样变化～"])
    role_label = "👨‍🎓 学生端" if user_role == "学生学习端" else "👩‍🏫 教师端"

    # 表情与状态行
    if thinking:
        status_line = "🤔 小光正在思考..."
        emoji = "😿"
    elif just_answered:
        status_line = "✅ 小光刚回答完～"
        emoji = "😺"
    elif agent_status in ("connected", "ready"):
        status_line = "🐾 小光在线，随时提问～"
        emoji = "🐱"
    elif agent_status == "configured_offline":
        status_line = "🟡 小光已配置，网络待恢复"
        emoji = "😼"
    elif agent_status in ("disconnected", "timeout", "error"):
        status_line = "😵 小光暂时离线…"
        emoji = "😼"
    else:
        status_line = f"🐾 正在：{experiment_mode}"
        emoji = "🐱"

    sub_line = f"{experiment_mode} · {mode_type} · {role_label}"

    # 参数摘要（一行展示）
    params_line = ""
    if params:
        parts = [f"{k}:{v}" for k, v in list(params.items())[:3]]
        params_line = "  |  ".join(parts)

    # 让桌宠具备“实验成长感”：根据实验上下文和助手状态显示等级与进度。
    pet_level = 3 if just_answered else (2 if agent_status in ("connected", "ready") else 1)
    pet_progress = 100 if just_answered else (78 if agent_status in ("connected", "ready") else 52)

    # 转义给 JS 用的字符串
    def js_str(s):
        return json.dumps(str(s), ensure_ascii=False)

    tips_js = "[" + ",".join(js_str(t) for t in tips) + "]"
    status_js = js_str(status_line)
    sub_js = js_str(sub_line)
    params_js = js_str(params_line) if params_line else '""'
    emoji_js = js_str(emoji)
    level_js = js_str(f"Lv.{pet_level} · 实验陪伴度 {pet_progress}%")

    # CSS 必须注入到父文档 head，否则样式不生效
    # JS 操作 window.parent.document，把宠物元素 append 到父文档 body
    pet_code = f"""
    <script>
    (function(){{
      var d = window.parent.document;          // 主页面文档
      var w = window.parent;                    // 主窗口
      // 1) 注入样式（只注入一次）
      if (!d.getElementById('pet-style')) {{
        var sty = d.createElement('style');
        sty.id = 'pet-style';
        sty.textContent = `
          #pet-wrap{{
            position:fixed; left:auto; right:18px; top:auto; bottom:18px;
            z-index:99998; display:flex; flex-direction:column; align-items:flex-end;
            gap:6px; user-select:none;
          }}
          #pet-wrap .pet-bubble{{
            background:#fff; border:1.5px solid #93c5fd; border-radius:14px;
            padding:10px 14px; max-width:270px; font-size:13px; line-height:1.45;
            color:#1e3a8a; box-shadow:0 6px 18px rgba(30,58,138,.18);
            animation:petFade .35s ease-out; pointer-events:auto;
          }}
          #pet-wrap .pet-bubble.pet-hidden{{ display:none; }}
          #pet-wrap .pet-emoji{{
            pointer-events:auto; font-size:52px; cursor:grab; user-select:none;
            animation:petBounce 2.6s ease-in-out infinite;
            filter:drop-shadow(0 4px 6px rgba(0,0,0,.22)); transition:transform .15s;
          }}
          #pet-wrap .pet-emoji:active{{ cursor:grabbing; }}
          #pet-wrap .pet-emoji.pet-dragging{{ animation:none; opacity:.85; }}
          #pet-wrap .pet-status{{ font-weight:700; color:#1e3a8a; font-size:13.5px; }}
          #pet-wrap .pet-level{{ font-size:10.5px; color:#7c3aed; margin-top:3px; font-weight:700; }}
          #pet-wrap .pet-progress{{ height:5px; margin-top:6px; border-radius:99px; background:#e2e8f0; overflow:hidden; }}
          #pet-wrap .pet-progress > i{{ display:block; height:100%; width:{pet_progress}%; border-radius:99px; background:linear-gradient(90deg,#38bdf8,#8b5cf6); transition:width .35s ease; }}
          #pet-wrap .pet-sub{{ font-size:11.5px; color:#475569; margin-top:2px; }}
          #pet-wrap .pet-params{{ font-size:11px; color:#0f766e; margin-top:3px; }}
          #pet-wrap .pet-tip{{ font-size:11.5px; color:#64748b; margin-top:4px; min-height:16px; }}
          #pet-wrap .pet-btns{{ margin-top:8px; display:flex; gap:6px; flex-wrap:wrap; }}
          #pet-wrap .pet-btn{{
            font-size:11px; padding:3px 9px; border-radius:8px; cursor:pointer;
            border:1px solid #93c5fd; background:#eff6ff; color:#1e40af;
            transition:background .15s;
          }}
          #pet-wrap .pet-btn:hover{{ background:#dbeafe; }}
          #pet-wrap .pet-hint{{ font-size:10px; color:#94a3b8; margin-top:5px; }}
          @keyframes petBounce{{ 0%,100%{{transform:translateY(0)}} 50%{{transform:translateY(-7px)}} }}
          @keyframes petWobble{{ 0%,100%{{transform:rotate(-8deg)}} 50%{{transform:rotate(8deg)}} }}
          @keyframes petFade{{ from{{opacity:0;transform:translateY(8px)}} to{{opacity:1;transform:translateY(0)}} }}
        `;
        d.head.appendChild(sty);
      }}

      // 2) 移除旧的 pet-wrap（每次 Streamlit rerun 都会重新执行此脚本）
      var old = d.getElementById('pet-wrap');
      if (old) old.remove();

      // 3) 构建宠物 DOM
      var tips = {tips_js};
      var wrap = d.createElement('div');
      wrap.id = 'pet-wrap';

      var bubble = d.createElement('div');
      bubble.className = 'pet-bubble';
      bubble.id = 'pet-bubble';
      var paramsHtml = {params_js} ? '<div class="pet-params">⚙️ ' + {params_js} + '</div>' : '';
      bubble.innerHTML =
        '<div class="pet-status">' + {status_js} + '</div>' +
        '<div class="pet-sub">' + {sub_js} + '</div>' +
        '<div class="pet-level">' + {level_js} + '</div>' +
        '<div class="pet-progress"><i></i></div>' +
        paramsHtml +
        '<div class="pet-tip" id="pet-tip-line">·</div>' +
        '<div class="pet-btns">' +
          '<span class="pet-btn" onclick="window.__petTop()">⬆ 回顶</span>' +
          '<span class="pet-btn" onclick="window.__petPrinciple()">📖 看原理</span>' +
          '<span class="pet-btn" onclick="window.__petReset()">🔄 重置参数</span>' +
          '<span class="pet-btn" onclick="window.__petHide()">✕ 收起</span>' +
        '</div>' +
        '<div class="pet-hint">拖动我可移动 · 双击我折叠气泡</div>';

      var emojiEl = d.createElement('div');
      emojiEl.className = 'pet-emoji';
      emojiEl.id = 'pet-emoji';
      emojiEl.textContent = {emoji_js};

      wrap.appendChild(bubble);
      wrap.appendChild(emojiEl);
      d.body.appendChild(wrap);

      // 4) 恢复保存的位置；若尚未拖动过，默认避开右侧表单区域
      try {{
        var saved = JSON.parse(w.localStorage.getItem('petPos') || 'null');
        if (saved && typeof saved.left === 'number') {{
          wrap.style.left = saved.left + 'px';
          wrap.style.top = saved.top + 'px';
          wrap.style.right = 'auto'; wrap.style.bottom = 'auto';
        }}
      }} catch(e){{}}

      // 5) 提示轮播
      var tipLine = d.getElementById('pet-tip-line');
      var idx = 0;
      function showTip(){{
        if (tipLine && tips.length) {{
          tipLine.textContent = tips[idx % tips.length];
          idx++;
        }}
      }}
      showTip();
      var tipTimer = w.setInterval(showTip, 4000);
      // 清理上一轮桌宠留下的轮播计时器，避免 Streamlit rerun 后计时器累积。
      if (w.__petTipTimer) w.clearInterval(w.__petTipTimer);
      w.__petTipTimer = tipTimer;

      // 6) 拖动逻辑
      var dragging = false, sx=0, sy=0, ox=0, oy=0, moved=false;
      function down(e){{
        dragging = true; moved = false;
        var p = e.touches ? e.touches[0] : e;
        sx = p.clientX; sy = p.clientY;
        var r = wrap.getBoundingClientRect();
        ox = r.left; oy = r.top;
        emojiEl.classList.add('pet-dragging');
        e.preventDefault();
      }}
      function move(e){{
        if (!dragging) return;
        var p = e.touches ? e.touches[0] : e;
        var nx = ox + (p.clientX - sx);
        var ny = oy + (p.clientY - sy);
        nx = Math.max(4, Math.min(w.innerWidth - 60, nx));
        ny = Math.max(4, Math.min(w.innerHeight - 60, ny));
        wrap.style.left = nx + 'px'; wrap.style.top = ny + 'px';
        wrap.style.right = 'auto'; wrap.style.bottom = 'auto';
        if (Math.abs(p.clientX - sx) > 4 || Math.abs(p.clientY - sy) > 4) moved = true;
      }}
      function up(){{
        if (!dragging) return;
        dragging = false;
        emojiEl.classList.remove('pet-dragging');
        var r = wrap.getBoundingClientRect();
        try {{ w.localStorage.setItem('petPos', JSON.stringify({{left:r.left, top:r.top}})); }} catch(e){{}}
      }}
      emojiEl.addEventListener('mousedown', down);
      emojiEl.addEventListener('touchstart', down, {{passive:false}});
      d.addEventListener('mousemove', move);
      d.addEventListener('touchmove', move, {{passive:false}});
      d.addEventListener('mouseup', up);
      d.addEventListener('touchend', up);

      // 7) 单击切换台词
      emojiEl.addEventListener('click', function(e){{
        if (moved) return;
        showTip();
        emojiEl.style.transform = 'scale(1.18)';
        setTimeout(function(){{ emojiEl.style.transform=''; }}, 180);
      }});

      // 8) 双击折叠
      emojiEl.addEventListener('dblclick', function(e){{
        bubble.classList.toggle('pet-hidden');
      }});

      // 9) 悬停摇摆
      emojiEl.addEventListener('mouseenter', function(){{
        emojiEl.style.animation = 'petWobble .6s ease-in-out infinite';
      }});
      emojiEl.addEventListener('mouseleave', function(){{
        emojiEl.style.animation = 'petBounce 2.6s ease-in-out infinite';
      }});

      // 10) 快捷按钮：用 window 全局函数，避免 iframe 销毁后事件丢失
      w.__petTop = function(){{
        // Streamlit 可能把滚动交给内部容器，不能只调用 window.scrollTo。
        var targets = [w, d.scrollingElement, d.documentElement,
          d.querySelector('[data-testid="stAppViewContainer"]'),
          d.querySelector('[data-testid="stMain"]'),
          d.querySelector('section.main')];
        targets.forEach(function(target){{
          if (!target) return;
          try {{
            if (target === w) target.scrollTo({{top:0, behavior:'smooth'}});
            else target.scrollTop = 0;
          }} catch(e){{}}
        }});
      }};
      w.__petPrinciple = function(){{
        var p = d.querySelector('.principle-panel');
        if (p) p.scrollIntoView({{behavior:'smooth', block:'center'}});
      }};
      w.__petReset = function(){{
        // 通过 query 参数通知 Python 端重置，避免创建一个会露出的隐藏按钮。
        try {{
          var u = new URL(w.location.href);
          u.searchParams.set('pet_reset', '1');
          w.location.href = u.toString();
        }} catch(e) {{ w.location.reload(); }}
      }};
      w.__petHide = function(){{
        var b = d.getElementById('pet-bubble');
        if (b) b.classList.toggle('pet-hidden');
      }};
    }})();
    </script>
    """

    # 用 components.html 渲染：允许执行 JS，height=0 让 iframe 不占空间
    components.html(pet_code, height=0)


def _update_pet_status(status_text, emoji_text):
    """轻量更新桌宠状态：只注入一小段 JS 修改已有元素的文字，
    不重新创建整个组件，避免在 st.write_stream 附近调用 components.html 引发协议错误。"""
    safe_status = status_text.replace('\\', '\\\\').replace("'", "\\'").replace('<', '&lt;').replace('>', '&gt;')
    safe_emoji = emoji_text.replace('\\', '\\\\').replace("'", "\\'")
    js_code = f"""
    <script>
    (function(){{
      var d = window.parent.document;
      var s = d.querySelector('#pet-wrap .pet-status');
      var e = d.getElementById('pet-emoji');
      if (s) s.textContent = '{safe_status}';
      if (e) e.textContent = '{safe_emoji}';
    }})();
    </script>
    """
    components.html(js_code, height=0)


def _load_streamlit_secrets_to_environ():
    """把 Streamlit Cloud Secrets 中的 API 配置注入环境变量，供 AI 助手读取。
    本地无 secrets.toml 时静默跳过，不影响环境变量方式。"""
    # 在本地运行且没有 secrets.toml 时，不访问 st.secrets；旧版
    # Streamlit 会把这次访问记录为页面错误并在测试输出中反复提示。
    _secret_candidates = (
        os.path.join(os.getcwd(), ".streamlit", "secrets.toml"),
        os.path.join(os.path.dirname(__file__), ".streamlit", "secrets.toml"),
        os.path.join(os.path.expanduser("~"), ".streamlit", "secrets.toml"),
    )
    if not any(os.path.isfile(_path) for _path in _secret_candidates):
        return
    try:
        _secrets = st.secrets
    except Exception:
        return
    # DashScope API Key（任一别名均可）
    for _name in ("DASHSCOPE_API_KEY", "DASHSCOPE_KEY", "QWEN_API_KEY"):
        try:
            _val = _secrets[_name]
        except (KeyError, TypeError, FileNotFoundError):
            continue
        if _val and not os.getenv(_name):
            os.environ[_name] = str(_val)
    # 可选的自定义端点/模型
    for _env in ("DASHSCOPE_API_URL", "DASHSCOPE_MODEL",
                 "OPENAI_BASE_URL", "OPENAI_API_BASE", "OPENAI_MODEL", "OPENAI_API_KEY"):
        try:
            _val = _secrets[_env]
        except (KeyError, TypeError, FileNotFoundError):
            continue
        if _val and not os.getenv(_env):
            os.environ[_env] = str(_val)


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

# 读取 Streamlit Cloud Secrets 必须在 set_page_config 之后执行：
# 访问 st.secrets 会被 Streamlit 视为一次 API 调用，否则会触发
# “set_page_config() can only be called once / first command”异常。
_load_streamlit_secrets_to_environ()

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

    /* API 配置与探究记录输入框：强制使用高对比度浅色主题。
       BaseWeb 会把实际背景放在嵌套容器上，仅设置 input 本身不够。 */
    [data-testid="stTextInput"] > div,
    [data-testid="stTextInput"] [data-baseweb="input"],
    [data-testid="stTextInput"] [data-baseweb="input"] > div,
    [data-testid="stTextArea"] [data-baseweb="textarea"],
    [data-testid="stTextArea"] [data-baseweb="textarea"] > div {
        background: #ffffff !important;
        background-color: #ffffff !important;
        border-color: #94a3b8 !important;
        box-shadow: none !important;
    }

    [data-testid="stTextInput"] input,
    [data-testid="stTextArea"] textarea {
        background: #ffffff !important;
        color: #0f172a !important;
        -webkit-text-fill-color: #0f172a !important;
        caret-color: #0f766e !important;
        opacity: 1 !important;
        font-weight: 500 !important;
    }

    [data-testid="stTextInput"] input::placeholder,
    [data-testid="stTextArea"] textarea::placeholder {
        color: #64748b !important;
        -webkit-text-fill-color: #64748b !important;
        opacity: 1 !important;
    }

    [data-testid="stTextInput"] svg,
    [data-testid="stTextArea"] svg {
        color: #475569 !important;
        fill: currentColor !important;
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
        margin: 0.65rem 0;
        padding: 1rem 1.1rem;
        border: 1px solid var(--lab-line);
        border-radius: 8px;
        background: #ffffff;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }

    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
        border-color: #86c5bc;
        background: #e6f3f0;
    }

    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] li {
        color: #0f172a !important;
        -webkit-text-fill-color: #0f172a !important;
        font-size: 1.02rem !important;
        line-height: 1.65 !important;
    }

    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] h1,
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] h2,
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] h3,
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] h4,
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] h5,
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] h6 {
        color: #0f172a !important;
        -webkit-text-fill-color: #0f172a !important;
        font-weight: 700 !important;
    }

    [data-testid="stChatMessage"] code {
        background: #f1f5f9 !important;
        color: #be123c !important;
        padding: 0.1rem 0.35rem !important;
        border-radius: 3px !important;
        font-size: 0.92rem !important;
    }

    [data-testid="stChatMessage"] pre {
        background: #1e293b !important;
        color: #e2e8f0 !important;
        border-radius: 6px !important;
        padding: 0.75rem 1rem !important;
        overflow-x: auto !important;
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

# 桌面宠物“重置参数”：通过 query 参数触发，避免额外的隐藏按钮出现在页面上。
_pet_reset_requested = False
try:
    _pet_reset_requested = str(st.query_params.get("pet_reset", "")) == "1"
except Exception:
    try:
        _pet_reset_requested = "1" in st.experimental_get_query_params().get("pet_reset", [])
    except Exception:
        _pet_reset_requested = False
if _pet_reset_requested:
    try:
        st.query_params.clear()
    except Exception:
        try:
            st.experimental_set_query_params()
        except Exception:
            pass
    st.session_state.clear()
    st.rerun()

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

# pet_just_answered 在末尾 render_desktop_pet 之后清除，不在这里清

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
            width="stretch",
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
            st.pyplot(fig, width="stretch")
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
            st.pyplot(fig, width="stretch")
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
            st.pyplot(fig, width="stretch")
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
            st.pyplot(fig, width="stretch")
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
            st.dataframe(pd.DataFrame(st.session_state.inquiry_records), width="stretch")

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

# 有待处理问题或刚回答完时，强制保持 expander 展开
_force_open_assistant = bool(st.session_state.get("pending_agent_question")) or bool(st.session_state.get("pet_just_answered"))
with st.expander("🤖 智能助手", expanded=_force_open_assistant):
    st.markdown("## 🤖 智能助手")
    if hasattr(agent, "refresh_environment_config"):
        # Keep a manually saved configuration during Streamlit reruns.
        agent.refresh_environment_config()
    
    # API连接状态显示和测试
    st.markdown("**🔌 API连接状态：**")
    col_status1, col_status2 = st.columns([2, 1])
    with col_status1:
        if hasattr(agent, 'api_status'):
            status_colors = {
                "connected": "🟢",
                "ready": "🟢",
                "configured_offline": "🟡",
                "disconnected": "🔴",
                "timeout": "🟡",
                "error": "🔴",
                "unknown": "⚪"
            }
            status_texts = {
                "connected": "已连接",
                "ready": "系统 API 已配置",
                "configured_offline": "API 已配置（网络暂不可用）",
                "disconnected": "未连接",
                "timeout": "连接超时",
                "error": "连接错误",
                "unknown": "未知状态"
            }
            st.markdown(f"""
            <div style="padding: 12px 14px; border-radius: 8px; color:#0f172a; background-color: {'#dcfce7' if agent.api_status in ['connected', 'ready'] else ('#fef3c7' if agent.api_status == 'configured_offline' else '#fee2e2')};">
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
                        if getattr(agent, "api_status", "") == "configured_offline":
                            st.info(f"ℹ️ {agent.api_error_message}")
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
        # 暂存给末尾桌面宠物显示参数摘要
        st.session_state["pet_params"] = current_params
    
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
    
    st.markdown("**⚙️ API 配置（默认自动读取系统变量，无需手动填写）：**")

    def _cfg_state(key, fallback):
        if key not in st.session_state:
            st.session_state[key] = fallback
        return st.session_state[key]

    env_api_key = getattr(agent, "_environment_api_key", "")
    api_type = getattr(agent, "api_type", "dashscope")

    if env_api_key:
        env_name = getattr(agent, "api_key_env_name", "DASHSCOPE_API_KEY")
        st.success(f"✅ 已自动加载 {env_name}（系统环境变量），可直接使用；无需重复填写。")
    else:
        st.info("ℹ️ 未检测到环境变量，请在下方手动填写 API Key 后点击“保存配置”即可生效。")

    # 智能助手已经位于一个 expander 内；Streamlit 不允许嵌套 expander，
    # 因此这里使用普通容器展示配置项，保证所有版本都能正常运行。
    st.markdown("**展开手动配置（API Key / 端点 / 模型）**")
    with st.container():
        _cfg_state("manual_api_type", api_type if api_type in ("dashscope", "ollama") else "dashscope")
        manual_type = st.radio(
            "服务类型",
            ["DashScope（阿里云通义千问 / 兼容端点）", "Ollama 本地模型"],
            index=0 if st.session_state["manual_api_type"] == "dashscope" else 1,
            horizontal=True,
            key="manual_api_type_radio",
        )
        st.session_state["manual_api_type"] = "dashscope" if "DashScope" in manual_type else "ollama"

        if "DashScope" in manual_type:
            _cfg_state(
                "manual_api_url",
                "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
            )
            _cfg_state("manual_model", getattr(agent, "model_name", "qwen3-max"))
            _cfg_state("manual_api_key", "")
            api_url = st.text_input(
                "API 端点（兼容 OpenAI 的 Chat Completions 地址）",
                value=st.session_state["manual_api_url"],
                key="manual_api_url_input",
                help="DashScope 官方：https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions\n"
                     "国际版：https://dashscope-intl.aliyuncs.com/compatible-mode/v1/chat/completions\n"
                     "DeepSeek：https://api.deepseek.com/v1/chat/completions  等\n"
                     "注意：bailian.console.aliyun.com 是控制台管理网址，不能作为 API 端点填写。",
            )
            st.caption("百炼控制台仅用于获取 API Key；程序请求请使用上面的兼容接口地址。")
            col_k, col_m = st.columns([3, 2])
            with col_k:
                api_key = st.text_input(
                    "API Key",
                    value=st.session_state["manual_api_key"],
                    type="password",
                    placeholder="sk-xxxxxxxxxxxx",
                    key="manual_api_key_input",
                    help="密钥只在当前会话中生效，不会持久化保存",
                )
            with col_m:
                model_name = st.text_input(
                    "模型名",
                    value=st.session_state["manual_model"],
                    key="manual_model_input",
                    placeholder="例如 qwen3-max / deepseek-chat / glm-4-plus",
                )
            st.caption("常用端点备忘：DashScope(国内版)、dashscope-intl(国际版)、DeepSeek、智谱 GLM 等均可用。")
        else:
            _cfg_state(
                "manual_ollama_url",
                getattr(agent, "api_url", "http://localhost:11434/v1/chat/completions"),
            )
            _cfg_state("manual_ollama_model", getattr(agent, "model_name", "qwen2.5:7b"))
            col_o1, col_o2 = st.columns([3, 2])
            with col_o1:
                api_url = st.text_input(
                    "Ollama 端点",
                    value=st.session_state["manual_ollama_url"],
                    key="manual_ollama_url_input",
                )
            with col_o2:
                model_name = st.text_input(
                    "模型名",
                    value=st.session_state["manual_ollama_model"],
                    key="manual_ollama_model_input",
                )
            api_key = ""  # Ollama 默认不需要 key

        col_save, col_clear = st.columns([1, 1])
        with col_save:
            if st.button("💾 保存配置并应用", type="primary", key="save_manual_api"):
                chosen_type = "dashscope" if "DashScope" in manual_type else "ollama"
                if hasattr(agent, "set_api_type"):
                    agent.set_api_type(chosen_type)
                else:
                    agent.api_type = chosen_type
                if hasattr(agent, "set_api_config"):
                    agent.set_api_config(api_url, model_name)
                else:
                    agent.api_url = agent._normalize_chat_endpoint(api_url) if hasattr(agent, "_normalize_chat_endpoint") else api_url
                    agent.model_name = model_name
                if chosen_type == "dashscope":
                    if hasattr(agent, "set_api_key"):
                        agent.set_api_key(api_key)
                    else:
                        agent.dashscope_api_key = api_key.strip()
                    st.session_state["manual_api_url"] = getattr(agent, "api_url", api_url.strip())
                    st.session_state["manual_model"] = model_name.strip()
                    st.session_state["manual_api_key"] = api_key.strip()
                    if api_key.strip():
                        st.success("✅ 配置已保存，密钥以“手动输入”方式生效。点击“测试连接”验证。")
                    else:
                        st.warning("⚠️ 未填写 API Key，请填入后再次保存。")
                else:
                    st.session_state["manual_ollama_url"] = getattr(agent, "api_url", api_url.strip())
                    st.session_state["manual_ollama_model"] = model_name.strip()
                    st.success("✅ Ollama 配置已保存。点击“测试连接”验证。")
        with col_clear:
            if st.button("↩️ 还原为系统环境变量", key="revert_to_env_api"):
                if hasattr(agent, "refresh_environment_config"):
                    agent.refresh_environment_config()
                st.session_state.pop("manual_api_key", None)
                st.session_state.pop("manual_api_url", None)
                st.session_state.pop("manual_model", None)
                st.session_state.pop("manual_ollama_url", None)
                st.session_state.pop("manual_ollama_model", None)
                st.info("🔄 已还原。请点击“测试连接”确认。")

    st.caption(
        f"当前服务类型：{getattr(agent, 'api_type', '')}｜"
        f"配置来源：{getattr(agent, 'api_source', '')}｜"
        f"模型：{getattr(agent, 'model_name', '')}｜密钥不会在页面中显示或保存到磁盘"
    )
    
    st.markdown("---")
    
    # 显示对话历史
    chat_container = st.container()
    with chat_container:
        st.markdown("**💬 对话历史：**")
        history = []
        pending_q = st.session_state.get("pending_agent_question")
        if hasattr(agent, 'conversation_history'):
            # 用拷贝避免 stream_response 内部修改 conversation_history 时影响已渲染的 history
            history = list(agent.conversation_history)
        elif hasattr(agent, 'get_history'):
            history = list(agent.get_history())

        # 当 pending 问题正在处理时，跳过 history 末尾已被 stream_response 预添加的那条用户消息
        if pending_q and history and history[-1].get("role") == "user":
            last_user = history[-1].get("content", "").strip()
            if last_user == pending_q.strip():
                history = history[:-1]

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

        # 流式输出当前提问的回复（pending_agent_question 由按钮回调设置）
        pending_question = st.session_state.get("pending_agent_question")
        if pending_question:
            # 流式输出前：用轻量 JS 更新桌宠为"正在思考..."
            # 上一次渲染的桌宠元素仍在 DOM 中，只需更新文字即可
            _update_pet_status("🤔 小光正在思考...", "😿")

            normalized_q = pending_question.replace(r"\[", "$$").replace(r"\]", "$$").replace(r"\(", "$").replace(r"\)", "$")
            with st.chat_message("user"):
                st.markdown(normalized_q)
            with st.chat_message("assistant"):
                if hasattr(agent, 'stream_response'):
                    # 流式：边生成边显示，显著降低首字等待时间
                    stream_gen = agent.stream_response(pending_question)
                    full_reply = st.write_stream(stream_gen)
                    # 处理 LaTeX 分隔符，保证公式正常渲染
                    if full_reply:
                        normalized = full_reply.replace(r"\[", "$$").replace(r"\]", "$$").replace(r"\(", "$").replace(r"\)", "$")
                        if normalized != full_reply:
                            st.markdown(normalized)
                else:
                    # 降级：非流式一次性输出
                    reply = agent.generate_response(pending_question)
                    reply = reply.replace(r"\[", "$$").replace(r"\]", "$$").replace(r"\(", "$").replace(r"\)", "$")
                    st.markdown(reply)
            # 清空 pending，下次渲染走正常历史显示
            st.session_state.pop("pending_agent_question", None)
            # 标记“刚回答完”，供桌面宠物显示；下一次非回答运行会自动清除
            st.session_state["pet_just_answered"] = True
            # 触发新一轮 rerun，让末尾的 render_desktop_pet 创建新桌宠显示"回答完"
            # components.html 在 st.write_stream 后调用不可靠，必须通过 rerun 重走一遍
            st.rerun()

    st.markdown("---")

    # 用户输入
    user_input = st.text_area(
        "💭 请输入您的问题：",
        placeholder="例如：双缝干涉的原理是什么？如何计算条纹间距？",
        key="agent_input",
        height=80
    )

    col_agent1, col_agent2 = st.columns([4, 1])
    with col_agent1:
        if st.button(
            "🚀 发送",
            type="primary",
            key="send_msg",
            width="stretch",
        ):
            prompt = (user_input or "").strip()
            if prompt:
                st.session_state["pending_agent_question"] = prompt
                st.session_state["agent_input"] = ""
                st.rerun()

    with col_agent2:
        if st.button(
            "🗑️ 清空",
            key="clear_chat",
            width="stretch",
        ):
            if hasattr(agent, 'clear_history'):
                agent.clear_history()
            elif hasattr(agent, 'conversation_history'):
                agent.conversation_history = []
            st.session_state.pop("pending_agent_question", None)
            st.rerun()

    # 快捷提问按钮（2 列布局，让每个按钮更宽、文字更清晰）
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

    # 自定义样式：让快捷按钮文字更大、更清晰
    st.markdown(
        """
        <style>
        div.stButton > button[data-testid="stBaseButton-secondary"] {
            font-size: 0.95rem;
            font-weight: 600;
            padding: 0.55rem 0.75rem;
            line-height: 1.4;
            white-space: normal;
            text-align: left;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # 2 列布局：每个按钮更宽，中文长文字也能清晰显示
    num_cols = 2
    for idx in range(0, len(quick_questions), num_cols):
        row = quick_questions[idx:idx + num_cols]
        cols = st.columns(num_cols)
        for j, q in enumerate(row):
            with cols[j]:
                if st.button(
                    q,
                    key=f"quick_{idx + j}",
                    help=f"快速提问：{q}",
                    width="stretch",
                ):
                    st.session_state["pending_agent_question"] = q
                    st.rerun()
    
    # 高级功能提示
    st.markdown("---")
    if not is_enhanced:
        st.info("💡 **提示**：安装 agent_module_v2.py 可获得增强版智能体，支持多种对话模式！")
    else:
        st.success("✨ 增强版智能体已启用！支持实验上下文感知和智能问答。")


# 桌面宠物：在页面右下角显示当前正在进行的操作（实验/模式/身份/参数）
render_desktop_pet(
    experiment_mode,
    mode_type,
    user_role,
    params=st.session_state.get("pet_params"),
    just_answered=bool(st.session_state.get("pet_just_answered", False)),
    agent_status=getattr(agent, "api_status", "unknown"),
)
# 渲染完"刚回答完"状态后清除标志，下次 rerun 恢复正常显示
st.session_state["pet_just_answered"] = False
