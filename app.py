import streamlit as st
from borax.calendars.lunardate import LunarDate
import datetime
import time
import json
import os
import random

# --- Configuration & Styling (v1.6.0 "Imperial Portal") ---
st.set_page_config(page_title="小六壬", page_icon="⛩️", layout="centered")

# Persistence for IP Rate Limiting
STORAGE_FILE = "divinations.json"

def get_remote_ip():
    try:
        return st.context.headers.get("X-Forwarded-For", "127.0.0.1").split(",")[0]
    except:
        return "127.0.0.1"

def check_rate_limit(ip):
    if not os.path.exists(STORAGE_FILE):
        return True, 0
    try:
        with open(STORAGE_FILE, "r") as f:
            data = json.load(f)
    except:
        data = {}
    last_time = data.get(ip)
    if last_time:
        now = time.time()
        elapsed = now - last_time
        if elapsed < 3600:
            return False, int(3600 - elapsed)
    return True, 0

def update_rate_limit(ip):
    data = {}
    if os.path.exists(STORAGE_FILE):
        try:
            with open(STORAGE_FILE, "r") as f:
                data = json.load(f)
        except: pass
    data[ip] = time.time()
    now = time.time()
    data = {k: v for k, v in data.items() if now - v < 86400}
    with open(STORAGE_FILE, "w") as f:
        json.dump(data, f)

cyber_zen_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@300;400;700&display=swap');

    body, .stApp {
        background-color: #050505;
        color: #e0e0e0;
        font-family: 'Noto Serif SC', 'Microsoft YaHei', serif;
    }
    .block-container {
        padding-top: 1rem !important;
        max-width: 850px !important;
    }

    h1 {
        color: #00F2FF;
        letter-spacing: 0.5em;
        text-align: center;
        text-shadow: 0 0 15px rgba(0,242,255,0.4);
        margin-bottom: 0.5rem;
        font-size: 3rem;
        font-weight: 700;
    }

    .sub-title {
        color: #444;
        text-align: center;
        font-size: 0.9rem;
        letter-spacing: 0.3em;
        margin-bottom: 3.5rem;
        text-transform: uppercase;
    }

    .ritual-hint {
        color: #888;
        font-size: 1.1rem;
        margin-bottom: 1.5rem;
        letter-spacing: 0.2em;
        text-align: center;
        font-weight: 300;
    }

    /* --- Combined Oracle Portal Input Bar --- */
    div[data-testid="stHorizontalBlock"]:has(div[data-testid="stTextInput"]) {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(0,242,255,0.2) !important;
        border-radius: 50px !important;
        padding: 5px 15px 5px 30px !important;
        box-shadow: 0 15px 40px rgba(0,0,0,0.6) !important;
        align-items: center !important;
        margin-bottom: 2rem !important;
    }
    
    /* REMOVE ALL WHITE BACKGROUNDS FROM INPUT */
    div[data-testid="stTextInput"], div[data-testid="stTextInput"] > div, div[data-testid="stTextInput"] div[data-baseweb="input"], div[data-testid="stTextInput"] div[data-baseweb="base-input"] {
        background-color: transparent !important;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }
    div[data-testid="stTextInput"] input {
        color: #00F2FF !important;
        font-size: 1.2rem !important;
        padding: 0 !important;
        background: transparent !important;
        background-color: transparent !important;
        border: none !important;
    }
    div[data-testid="stTextInput"] input::placeholder {
        color: #333 !important;
    }
    div[data-testid="stTextInput"] label { display: none !important; }

    /* Action Buttons (Voice & Confirm) */
    .icon-btn {
        background: transparent !important;
        background-color: transparent !important;
        border: none !important;
        color: #555 !important;
        font-size: 1.4rem !important;
        cursor: pointer !important;
        padding: 0 10px !important;
        transition: all 0.3s ease !important;
        box-shadow: none !important;
    }
    .icon-btn:hover { color: #00F2FF !important; }

    /* Target Streamlit Button (The arrow) */
    div[data-testid="stHorizontalBlock"] button[data-testid="baseButton-secondary"] {
        background: transparent !important;
        background-color: transparent !important;
        color: #00F2FF !important;
        border: 1px solid rgba(0,242,255,0.3) !important;
        border-radius: 50% !important;
        width: 45px !important;
        height: 45px !important;
        padding: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: none !important;
        transition: all 0.3s ease !important;
        min-width: 45px !important;
    }
    div[data-testid="stHorizontalBlock"] button:hover {
        transform: scale(1.1);
        border-color: #00F2FF !important;
        box-shadow: 0 0 20px rgba(0,242,255,0.3) !important;
        background: rgba(0,242,255,0.1) !important;
        color: #fff !important;
    }

    /* Horizontal Radio for 1-9 */
    div[data-testid="stRadio"] > div { flex-direction: row !important; justify-content: center !important; gap: 12px !important; margin-bottom: 3rem; }
    div[data-testid="stRadio"] label { background: rgba(0,242,255,0.05) !important; border: 1px solid rgba(0,242,255,0.15) !important; padding: 5px 12px !important; border-radius: 4px !important; color: #666 !important; }
    div[data-testid="stRadio"] label:has(input:checked) { border-color: #00F2FF !important; color: #00F2FF !important; background: rgba(0,242,255,0.1) !important; }
    div[data-testid="stRadio"] label div[data-testid="stMarkdownContainer"] p { font-size: 1rem !important; }
    div[data-testid="stRadio"] div[data-baseweb="radio"] > div:first-child { display: none !important; }

    /* Result Card */
    .result-card {
        background: rgba(10, 10, 10, 0.99);
        border: 1px solid rgba(0,242,255,0.3);
        padding: 4rem;
        margin-top: 1rem;
        border-radius: 12px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.9);
        animation: emerge 1.2s ease-out;
    }
    @keyframes emerge { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }

    #MainMenu, footer, header { visibility: hidden; }
</style>
"""
st.markdown(cyber_zen_css, unsafe_allow_html=True)

# --- Data ---
GUA_DATA = {
    1: {"name": "大安", "status": "STATUS: STABLE / 200 OK", "poem": "大安事事昌，求财在东方。<br>失物去不远，宅舍保安康。", "interpretation": "身不动时，五行属木。此卦为极稳之象。如底层架构之固，如程序运行之顺。当下宜守不宜动，静候其成。求谋甚周全，官事总成双。", "advice": "建议：稳扎稳打，系统运行正常，无需紧急补丁。"},
    2: {"name": "留连", "status": "STATUS: PENDING / PROCESSING", "poem": "留连事难成，求谋日未明。<br>官事只宜缓，去者未回程。", "interpretation": "人未归时，五行属水。此卦为延宕之象。如同数据传输阻塞，逻辑陷入回旋。凡事不可操之过急，需耐心等待系统响应。此时宜缓不宜急。", "advice": "建议：增加超时等待，排查死循环逻辑。耐心是唯一的解药。"},
    3: {"name": "速喜", "status": "STATUS: INSTANT / PUSH", "poem": "速喜喜来临，求财向南行。<br>失物午未申，逢人路上寻。", "interpretation": "人即至时，五行属火。此卦为速发之象。好比高优先级的推送提醒，灵感瞬间迸发。宜果断出击，把握转瞬即逝的窗口期。好事将至，执行效率极高。", "advice": "建议：立即执行！当前请求具有最高优先级，适合全速上线。"},
    4: {"name": "赤口", "status": "STATUS: CONFLICT / 403 FORBIDDEN", "poem": "赤口主口舌，官非切要防。<br>失物急去寻，行人有惊慌。", "interpretation": "官事凶时，五行属金。此卦为纷争之象。警惕防火墙被攻破或通信协议冲突。慎言谨行，防范口舌是非与突发之阻碍。外环境充满变量，需加强防御。", "advice": "建议：进入沙盒模式。开启全量日志审计，防范外部攻击冲突。"},
    5: {"name": "小吉", "status": "STATUS: OPTIMIZED / SUCCESS", "poem": "小吉最吉昌，路上好商商。<br>阴人来报喜，失物在坤方。", "interpretation": "人来喜时，五行属木。此卦为和合之象。如代码经过完美重构，系统资源调配得当。虽非大成，但胜在圆满顺遂，有贵人（辅助模块）相助。事有转机，结果可期。", "advice": "建议：可以小步快跑。当前系统鲁棒性良好，适合逐步发布。"},
    0: {"name": "空亡", "status": "STATUS: VOID / 404 NOT FOUND", "poem": "空亡事不祥，阴人少主张。<br>求财无利益，行人有灾殃。", "interpretation": "音信稀时，五行属土。此卦为虚无之象。链接已断开，数据已溢出。此时不宜寄托希望，宜彻底清空缓存，择日重新加载。强求无益，不如入定静待。", "advice": "建议：立即杀掉进程。清空心念，重新初始化系统内核。"}
}

# --- UI ---
st.markdown("<h1>小 六 壬</h1>", unsafe_allow_html=True)
st.markdown('<div class="sub-title">时 空 算 法 · 瞬 时 灵 觉</div>', unsafe_allow_html=True)

st.markdown('<div class="ritual-hint">请屏息凝神，凭直觉选取一数</div>', unsafe_allow_html=True)
N = st.radio("N", options=list(range(1, 10)), horizontal=True, label_visibility="collapsed")

# Combined Input Section
c1, c2, c3 = st.columns([10, 1.2, 1.5])
with c1:
    question = st.text_input("Divine Question", placeholder="在此起卦，感应因果...", label_visibility="collapsed")
with c2:
    st.markdown('<button class="icon-btn">🎙️</button>', unsafe_allow_html=True)
with c3:
    divine_trigger = st.button("⮕", use_container_width=True)

if divine_trigger:
    ip = get_remote_ip()
    allowed, remaining = check_rate_limit(ip)
    
    if not allowed:
        st.toast(f"机缘未到。请于 {remaining // 60} 分钟后再试。", icon="⏳")
    elif not question:
        st.toast("请先于心中存疑，并输入所求之辞。", icon="⛩️")
    else:
        # Animation
        placeholder = st.empty()
        anim_steps = [("📡 正在捕捉时空涟漪...", 0.4), ("🌑 定位星历数据...", 0.4), ("⚡ 执行 O(1) 命运演算...", 0.5), ("👁️ 解析神谕二进制码...", 0.4)]
        for step, dur in anim_steps:
            with placeholder.container():
                st.markdown(f'<div style="text-align: center; color: #00F2FF; font-family: monospace; font-size: 1.1rem; margin: 1rem 0;">{step}</div>', unsafe_allow_html=True)
                matrix = "".join([random.choice("0123456789ABCDEF") for _ in range(40)])
                st.markdown(f'<div style="text-align: center; color: #111; font-family: monospace; font-size: 0.6rem; letter-spacing: 4px;">{matrix}</div>', unsafe_allow_html=True)
                time.sleep(dur)
        placeholder.empty()

        # Calculation
        now = datetime.datetime.now()
        lunar = LunarDate.from_solar_date(now.year, now.month, now.day)
        def get_sh_idx(h): return 1 if h >= 23 or h < 1 else (h + 1) // 2 + 1
        M, D, H = lunar.month, lunar.day, get_sh_idx(now.hour)
        res_idx = (M + D + H + N - 3) % 6
        gua = GUA_DATA[res_idx]
        sh_names = ["", "子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
        
        update_rate_limit(ip)
        
        # Result Card
        st.markdown(f"""
        <div class="result-card">
            <div style="font-family: 'Courier New', monospace; color: #333; font-size: 0.8rem; text-align: center; margin-bottom: 3rem; border-bottom: 1px solid #1a1a1a; padding-bottom: 2rem;">
                {now.strftime('%Y-%m-%d %H:%M:%S')} | {lunar.strftime('%Y年%L%M月%D')} {sh_names[H]}时 (数:{N})<br>
                ALGO: ({M} + {D} + {H} + {N} - 3) % 6 = {res_idx}
            </div>
            <div style="font-size: 5.5rem; font-weight: 700; color: #00F2FF; text-align: center; margin-bottom: 0.5rem; text-shadow: 0 0 40px rgba(0,242,255,0.5);">{gua["name"]}</div>
            <div style="text-align: center; color: #00F2FF; font-size: 1rem; font-family: 'Courier New', monospace; letter-spacing: 0.3em; margin-bottom: 3.5rem; opacity: 0.8;">{gua["status"]}</div>
            <div style="border-left: 3px solid #00F2FF; padding-left: 2.5rem; margin-bottom: 3rem;">
                <div style="color: #444; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.2em; margin-bottom: 0.8rem;">诗诀 Oracle Verse</div>
                <div style="color: #fff; font-size: 1.6rem; line-height: 1.8; margin-bottom: 1.5rem;">{gua["poem"]}</div>
            </div>
            <div style="border-left: 3px solid #00F2FF; padding-left: 2.5rem; margin-bottom: 3rem;">
                <div style="color: #444; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.2em; margin-bottom: 0.8rem;">解读 Interpretation</div>
                <div style="color: #999; line-height: 2.2; font-size: 1.05rem;">{gua["interpretation"]}</div>
            </div>
            <div style="color: #00F2FF; background: rgba(0,242,255,0.05); padding: 1.5rem; border-radius: 4px; font-size: 1rem; margin-top: 1rem;">{gua["advice"]}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br><br><br><br><br>", unsafe_allow_html=True)
