import streamlit as st
from borax.calendars.lunardate import LunarDate
import datetime
import time
import json
import os

# --- Configuration & Styling (v1.3.1 Imperial Refinement) ---
st.set_page_config(page_title="赛博禅龛", page_icon="⛩️", layout="centered")

cyber_zen_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@300;400;700&display=swap');

    /* Global Reset */
    .stApp {
        background-color: #050505;
        color: #e0e0e0;
        font-family: 'Noto Serif SC', 'Microsoft YaHei', serif;
    }
    
    /* Remove unnecessary spacing */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
        max-width: 800px !important;
    }

    h1 {
        color: #00F2FF;
        letter-spacing: 0.5em;
        text-align: center;
        text-shadow: 0 0 20px rgba(0,242,255,0.5);
        margin-bottom: 1rem !important;
        font-weight: 700;
        font-size: 2.5rem;
    }

    .ritual-hint {
        color: #888;
        font-size: 1rem;
        text-align: center;
        margin-bottom: 1.5rem;
        letter-spacing: 0.2em;
        font-weight: 300;
    }

    /* Number Selection Matrix */
    div[data-testid="stRadio"] > div {
        flex-direction: row !important;
        justify-content: center !important;
        gap: 10px !important;
    }
    div[data-testid="stRadio"] label {
        background: rgba(0,242,255,0.02) !important;
        border: 1px solid rgba(0,242,255,0.2) !important;
        border-radius: 0px !important;
        padding: 5px 15px !important;
        color: #555 !important;
        transition: all 0.2s ease !important;
        font-family: monospace !important;
    }
    div[data-testid="stRadio"] label:hover {
        border-color: #00F2FF !important;
        color: #00F2FF !important;
    }
    div[data-testid="stRadio"] label[data-baseweb="radio"] > div:first-child {
        display: none !important;
    }
    div[data-testid="stRadio"] label:has(input:checked) {
        border-color: #00F2FF !important;
        color: #00F2FF !important;
        box-shadow: 0 0 15px rgba(0,242,255,0.4) !important;
        background: rgba(0,242,255,0.1) !important;
    }

    /* Primary Button */
    .stButton {
        display: flex;
        justify-content: center;
        margin-top: 1.5rem;
    }
    .stButton > button {
        background-color: transparent !important;
        color: #00F2FF !important;
        border: 1px solid #00F2FF !important;
        border-radius: 0px !important;
        padding: 0.8rem 5rem !important;
        transition: all 0.4s cubic-bezier(0.19, 1, 0.22, 1) !important;
        text-transform: uppercase !important;
        letter-spacing: 0.8em !important;
        font-size: 1.2rem !important;
        white-space: nowrap !important;
        width: auto !important;
    }
    .stButton > button:hover {
        color: #fff !important;
        border-color: #fff !important;
        background-color: rgba(0,242,255,0.15) !important;
        box-shadow: 0 0 30px rgba(0,242,255,0.6) !important;
    }

    /* Result Card */
    .result-card {
        background: rgba(10, 10, 10, 0.98);
        border: 1px solid rgba(0,242,255,0.3);
        backdrop-filter: blur(20px);
        padding: 3rem;
        margin-top: 1.5rem;
        animation: slideIn 1s cubic-bezier(0.23, 1, 0.32, 1);
        border-radius: 0px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.9);
        max-width: 750px;
        margin-left: auto;
        margin-right: auto;
    }

    .formula {
        font-family: 'Courier New', monospace;
        color: #333;
        font-size: 0.8rem;
        text-align: center;
        margin-bottom: 2rem;
        border-bottom: 1px solid #1a1a1a;
        padding-bottom: 1.5rem;
    }

    .gua-name {
        font-size: 6rem;
        font-weight: 700;
        color: #00F2FF;
        text-align: center;
        margin: 0.5rem 0;
        text-shadow: 0 0 40px rgba(0,242,255,0.6);
        letter-spacing: 0.2em;
    }

    .gua-status {
        text-align: center;
        color: #00F2FF;
        font-size: 1rem;
        font-family: monospace;
        letter-spacing: 0.3em;
        margin-bottom: 3rem;
        opacity: 0.7;
    }

    .gua-content {
        display: grid;
        grid-template-columns: 1fr;
        gap: 2.5rem;
        text-align: left;
    }

    .section-title {
        color: #444;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.3em;
        margin-bottom: 0.8rem;
        border-bottom: 1px solid #111;
        display: inline-block;
    }

    .poem {
        color: #e0e0e0;
        font-size: 1.4rem;
        line-height: 1.8;
        letter-spacing: 0.15em;
        border-left: 3px solid #00F2FF;
        padding-left: 2rem;
    }

    .interpretation {
        color: #999;
        font-size: 1.05rem;
        line-height: 2.0;
    }

    .advice {
        color: #00F2FF;
        font-size: 1rem;
        background: rgba(0,242,255,0.05);
        padding: 1.5rem;
        border-radius: 0px;
        border: 1px solid rgba(0,242,255,0.1);
    }

    @keyframes slideIn {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* Hide Streamlit components */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
"""
st.markdown(cyber_zen_css, unsafe_allow_html=True)

# --- Persistence Logic ---
STORAGE_FILE = "divinations.json"

@st.cache_resource
def get_ip_cache():
    if os.path.exists(STORAGE_FILE):
        try:
            with open(STORAGE_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

ip_cache = get_ip_cache()

def save_cache():
    try:
        now = time.time()
        # Keep only last 24h
        cleaned = {k: v for k, v in ip_cache.items() if now - v < 86400}
        with open(STORAGE_FILE, "w") as f:
            json.dump(cleaned, f)
    except:
        pass

def get_remote_ip():
    try:
        return st.context.headers.get("X-Forwarded-For", "127.0.0.1").split(",")[0]
    except:
        return "127.0.0.1"

# --- Data & Logic ---

GUA_DATA = {
    1: {
        "name": "大安",
        "status": "STATUS: STABLE / 200 OK",
        "poem": "大安事事昌，求财在坤方。<br>失物去不远，宅舍保安康。<br>行人身未动，病者主无妨。<br>将军回旧舍，官事只宜强。",
        "interpretation": "身不动时，五行属木。此卦为极稳之象。如底层架构之固，如程序运行之顺。当下万事皆稳，虽无剧烈爆发，但胜在长久。此时最忌心浮气躁，妄动生灾。",
        "advice": "宜：静修、守旧、固本、签约。忌：辞职、远行、突围。"
    },
    2: {
        "name": "留连",
        "status": "STATUS: PENDING / PROCESSING",
        "poem": "留连事难成，求谋日未明。<br>官事只宜缓，去者未回程。<br>失物南方见，急讨方称心。<br>更需防口舌，人口且平平。",
        "interpretation": "人未归时，五行属水。此卦为延宕之象。如同数据传输阻塞，逻辑陷入回旋。凡事多有阻滞，难以一蹴而就。此时需调整呼吸，在等待中寻找破绽，不可强攻。",
        "advice": "宜：复盘、查漏、低调、等待。忌：激进、担保、求快、争辩。"
    },
    3: {
        "name": "速喜",
        "status": "STATUS: INSTANT / PUSH",
        "poem": "速喜喜来临，求财向南行。<br>失物午未申，逢人路上寻。<br>官事有贵人，病者得安宁。<br>田宅六畜吉，行人有信音。",
        "interpretation": "人即至时，五行属火。此卦为速发之象。好比高优先级的推送提醒，灵感瞬间迸发，好运正加速赶来。此时应借势而为，果断扣动扳机，把握这转瞬即逝的窗口期。",
        "advice": "宜：表白、公关、短线交易、社交。忌：犹豫、拖延、拒绝机会。"
    },
    4: {
        "name": "赤口",
        "status": "STATUS: CONFLICT / 403 FORBIDDEN",
        "poem": "赤口主口舌，官非切要防。<br>失物急去寻，行人有惊慌。<br>鸡犬多作怪，病者出西方。<br>更需防咀咒，恐怕染瘟皇。",
        "interpretation": "官事凶时，五行属金。此卦为纷争之象。警惕防火墙被攻破或通信协议冲突。外环境充满变量与敌意，极易引发口角、损失或突发阻碍。此时当收敛锋芒，深挖战壕。",
        "advice": "宜：自省、防守、规避、闭关。忌：对抗、创业、远行、争理。"
    },
    5: {
        "name": "小吉",
        "status": "STATUS: OPTIMIZED / SUCCESS",
        "poem": "小吉最吉昌，路上好商量。<br>阴人来报喜，失物在坤方。<br>行人立即至，交易甚辉煌。<br>凡事皆和合，病者祷上苍。",
        "interpretation": "人来喜时，五行属木。此卦为和合之象。如代码经过完美重构，系统资源调配得当。虽非宏大叙事，但贵在细节圆满，常有意外之喜（贵人相助）。是推进计划的黄金时刻。",
        "advice": "宜：合作、联姻、面试、发布新版。忌：独断、冷战、傲慢。"
    },
    0: {
        "name": "空亡",
        "status": "STATUS: VOID / 404 NOT FOUND",
        "poem": "空亡事不祥，阴人多乖张。<br>求财无利益，行人有灾殃。<br>失物寻不见，官事有刑伤。<br>病人逢暗鬼，解禳保安康。",
        "interpretation": "音信稀时，五行属土。此卦为虚无之象。链接已断开，数据已溢出。此时不宜寄托希望，强求无果。宜彻底清空缓存，放空大脑，等待系统重置后的契机。",
        "advice": "宜：冥想、休息、放弃执念、清理旧物。忌：投资、承诺、寻找失物。"
    }
}

def get_shichen_index(hour):
    if hour >= 23 or hour < 1: return 1
    return (hour + 1) // 2 + 1

# --- UI Layout ---

st.markdown("<h1>【 赛 博 禅 龛 】</h1>", unsafe_allow_html=True)
st.markdown('<div class="ritual-hint">请屏息凝神，凭直觉择一灵数：</div>', unsafe_allow_html=True)

# Horizontal Number Selection
n_options = [1, 2, 3, 4, 5, 6, 7, 8, 9]
N = st.radio("灵数选择", n_options, index=4, horizontal=True, label_visibility="collapsed")

# Main Action
if st.button("感 应 天 机"):
    ip = get_remote_ip()
    now_ts = time.time()
    
    if ip in ip_cache and now_ts - ip_cache[ip] < 3600:
        remaining = int(3600 - (now_ts - ip_cache[ip]))
        st.toast(f"「机缘未到」：天机一小时一泄，请于 {remaining // 60} 分钟后再来。", icon="⏳")
    else:
        # Update Rate Limit
        ip_cache[ip] = now_ts
        save_cache()
        
        # Ritual Animation
        anim_placeholder = st.empty()
        stages = [
            ("📡 正在捕捉时空涟漪...", 0.6),
            ("🌑 正在定位星历数据...", 0.7),
            ("⚡ 注入灵数 N=" + str(N) + " 执行命运演算...", 1.2),
            ("👁️ 正在解析神谕二进制码...", 0.8)
        ]
        
        for stage, duration in stages:
            anim_placeholder.markdown(f"""
            <div style="text-align: center; color: #00F2FF; font-family: monospace; font-size: 1rem; margin: 1.5rem 0;">
                {stage}<br>
                <span style="font-size: 0.6rem; color: #1a1a1a;">{datetime.datetime.now().isoformat()}</span>
            </div>
            """, unsafe_allow_html=True)
            time.sleep(duration)
        
        anim_placeholder.empty()
        
        # Calculation Logic
        now = datetime.datetime.now()
        lunar = LunarDate.from_solar_date(now.year, now.month, now.day)
        M, D, H = lunar.month, lunar.day, get_shichen_index(now.hour)
        
        # Salted Formula: (M + D + H + N - 3) % 6
        res_idx = (M + D + H + N - 3) % 6
        gua = GUA_DATA[res_idx]
        shichen_names = ["", "子时", "丑时", "寅时", "卯时", "辰时", "巳时", "午时", "未时", "申时", "酉时", "戌时", "亥时"]
        
        # Result Display
        st.markdown(f"""
        <div class="result-card">
            <div class="formula">
                ALGO_TRACE: ({M} + {D} + {H} + {N} - 3) mod 6 = {res_idx} | {now.strftime('%H:%M:%S')}
            </div>
            <div class="gua-name">{gua["name"]}</div>
            <div class="gua-status">{gua["status"]}</div>
            <div class="gua-content">
                <div>
                    <div class="section-title">诗诀 Oracle Verse</div>
                    <div class="poem">{gua["poem"]}</div>
                </div>
                <div>
                    <div class="section-title">解读 Interpretation</div>
                    <div class="interpretation">{gua["interpretation"]}</div>
                </div>
                <div class="advice">{gua["advice"]}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br><br><br>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #1a1a1a; font-size: 0.6rem; letter-spacing: 0.5em;'>ALGORITHM IS FATE · CODE IS TRUTH</p>", unsafe_allow_html=True)
