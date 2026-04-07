import streamlit as st
from borax.calendars.lunardate import LunarDate
import datetime
import time
import json
import os
import random

# --- Configuration & Styling ---
st.set_page_config(page_title="赛博禅龛", page_icon="⛩️", layout="centered")

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
    if os.path.exists(STORAGE_FILE):
        try:
            with open(STORAGE_FILE, "r") as f:
                data = json.load(f)
        except:
            data = {}
    else:
        data = {}
    data[ip] = time.time()
    now = time.time()
    data = {k: v for k, v in data.items() if now - v < 7200}
    with open(STORAGE_FILE, "w") as f:
        json.dump(data, f)

cyber_zen_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@300;400;700&display=swap');

    /* Global Overrides */
    body, .stApp {
        background-color: #050505;
        color: #e0e0e0;
        font-family: 'Noto Serif SC', 'Microsoft YaHei', serif;
    }
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        max-width: 800px !important;
    }

    /* Layout Containers */
    .header-section {
        text-align: center;
        margin-bottom: 2rem;
    }
    .ritual-hint {
        color: #888;
        font-size: 1.1rem;
        margin: 1.5rem 0;
        letter-spacing: 0.15em;
        text-align: center;
        font-weight: 300;
    }

    /* Typography */
    h1 {
        color: #00F2FF;
        letter-spacing: 0.3em;
        text-align: center;
        text-shadow: 0 0 15px rgba(0,242,255,0.4);
        margin-top: 0;
        font-size: 2.2rem;
        font-weight: 700;
    }

    /* Button Styling */
    .stButton {
        display: flex;
        justify-content: center;
        margin: 2rem 0;
    }
    .stButton>button {
        background-color: rgba(0,242,255,0.08);
        color: #00F2FF;
        border: 1px solid #00F2FF;
        border-radius: 2px;
        padding: 0.8rem 4rem;
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 0.4em;
        font-size: 1.2rem;
        white-space: nowrap;
        min-width: 320px;
    }
    .stButton>button:hover {
        color: #fff;
        border-color: #fff;
        background-color: rgba(0,242,255,0.2);
        box-shadow: 0 0 25px rgba(0,242,255,0.4);
    }

    /* Result Card */
    .result-card {
        background: rgba(15, 15, 15, 0.98);
        border: 1px solid rgba(0,242,255,0.25);
        backdrop-filter: blur(20px);
        padding: 3rem;
        margin-top: 1rem;
        animation: slideIn 1s cubic-bezier(0.16, 1, 0.3, 1);
        border-radius: 2px;
    }
    .formula-trace {
        font-family: 'Courier New', monospace;
        color: #444;
        font-size: 0.85rem;
        text-align: center;
        margin-bottom: 2.5rem;
        border-bottom: 1px solid #222;
        padding-bottom: 1rem;
    }
    .gua-title {
        font-size: 5.5rem;
        font-weight: 700;
        color: #00F2FF;
        text-align: center;
        margin: 0.5rem 0;
        text-shadow: 0 0 40px rgba(0,242,255,0.5);
    }
    .gua-status-code {
        text-align: center;
        color: #00F2FF;
        font-size: 1rem;
        font-family: 'Courier New', monospace;
        letter-spacing: 0.2em;
        margin-bottom: 3rem;
        opacity: 0.9;
    }
    .gua-details {
        display: flex;
        flex-direction: column;
        gap: 2.5rem;
    }
    .detail-item {
        border-left: 3px solid #00F2FF;
        padding-left: 1.5rem;
    }
    .detail-label {
        color: #555;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.2em;
        margin-bottom: 0.6rem;
    }
    .detail-value-poem {
        color: #e0e0e0;
        font-size: 1.4rem;
        line-height: 1.8;
        letter-spacing: 0.1em;
    }
    .detail-value-text {
        color: #bbb;
        font-size: 1.05rem;
        line-height: 1.9;
    }
    .detail-value-advice {
        color: #00F2FF;
        font-size: 1rem;
        background: rgba(0,242,255,0.04);
        padding: 1rem;
        border-radius: 4px;
    }

    @keyframes slideIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* UI Hiding */
    #MainMenu, footer, header { visibility: hidden; }
</style>
"""
st.markdown(cyber_zen_css, unsafe_allow_html=True)

# --- Data ---
GUA_DATA = {
    1: {
        "name": "大安", 
        "status": "STATUS: STABLE / 200 OK", 
        "poem": "大安事事昌，求财在东方。<br>失物去不远，宅舍保安康。<br>行人身未动，病者主无妨。<br>将军回旧舍，官事只宜强。", 
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

# --- Main Interface ---
st.markdown('<div class="header-section">', unsafe_allow_html=True)
st.markdown("<h1>赛博禅龛</h1>", unsafe_allow_html=True)
st.markdown('<div class="ritual-hint">请屏息凝神，默念所求之事</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Centered Button
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    divine_trigger = st.button("感应天机", use_container_width=True)

if divine_trigger:
    ip = get_remote_ip()
    allowed, remaining = check_rate_limit(ip)
    
    if not allowed:
        st.toast(f"机缘未到。天机一小时一泄，请于 {remaining // 60} 分钟后再试。", icon="⏳")
    else:
        # Complex Animation
        anim_placeholder = st.empty()
        stages = [
            ("📡 正在捕捉时空涟漪...", 0.5),
            ("🌑 正在定位星历数据...", 0.5),
            ("🕰️ 正在映射十二时辰...", 0.5),
            ("⚡ 执行 O(1) 递归演算...", 0.8),
            ("👁️ 解析神谕二进制码...", 0.6)
        ]
        
        for stage, duration in stages:
            with anim_placeholder.container():
                st.markdown(f'<div style="text-align: center; color: #00F2FF; font-family: monospace; font-size: 1.1rem; margin-top: 1rem;">{stage}</div>', unsafe_allow_html=True)
                # Matrix rain simulation
                matrix = "".join([random.choice("0123456789ABCDEF") for _ in range(40)])
                st.markdown(f'<div style="text-align: center; color: #111; font-family: monospace; font-size: 0.6rem; letter-spacing: 2px;">{matrix}</div>', unsafe_allow_html=True)
                time.sleep(duration)
        anim_placeholder.empty()
        
        # Calculation
        now = datetime.datetime.now()
        lunar = LunarDate.from_solar_date(now.year, now.month, now.day)
        
        def get_shichen_index(hour):
            if hour >= 23 or hour < 1: return 1
            return (hour + 1) // 2 + 1
            
        M, D, H = lunar.month, lunar.day, get_shichen_index(now.hour)
        res_idx = (M + D + H - 2) % 6
        gua = GUA_DATA[res_idx]
        shichen_names = ["", "子时", "丑时", "寅时", "卯时", "辰时", "巳时", "午时", "未时", "申时", "酉时", "戌时", "亥时"]
        
        update_rate_limit(ip)
        
        # Display Result
        st.markdown(f"""
        <div class="result-card">
            <div class="formula-trace">
                {now.strftime('%Y-%m-%d %H:%M:%S')} | {lunar.strftime('%Y年%L%M月%D')} {shichen_names[H]}<br>
                ALGO: ({M} + {D} + {H} - 2) % 6 = {res_idx}
            </div>
            <div class="gua-title">{gua["name"]}</div>
            <div class="gua-status-code">{gua["status"]}</div>
            <div class="gua-details">
                <div class="detail-item">
                    <div class="detail-label">诗诀 Oracle Verse</div>
                    <div class="detail-value-poem">{gua["poem"]}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">解读 Interpretation</div>
                    <div class="detail-value-text">{gua["interpretation"]}</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">建议 Advice</div>
                    <div class="detail-value-advice">{gua["advice"]}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
