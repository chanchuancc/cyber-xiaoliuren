import streamlit as st
import datetime
import time
import random
from borax.calendars.lunardate import LunarDate
from meihua_data import BAGUA, GUA_64, BRANCHES, BRANCH_MAP

# --- Configuration & Styling (Cyber Zen -> Imperial Plum v1.4.0) ---
st.set_page_config(page_title="梅花易数", page_icon="🧧", layout="centered")

plum_blossom_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@300;400;700&display=swap');

    body, .stApp {
        background: radial-gradient(circle at center, #0a0a0a 0%, #050505 100%);
        color: #d4af37;
        font-family: 'Noto Serif SC', 'Microsoft YaHei', serif;
    }
    
    /* Center the block container and move it up */
    .block-container {
        padding-top: 1rem !important;
        max-width: 800px !important;
    }

    h1 {
        color: #d4af37;
        letter-spacing: 0.5em;
        text-align: center;
        text-shadow: 0 0 20px rgba(212,175,55,0.4);
        font-weight: 700;
        font-size: 3rem;
        margin-bottom: 0.5rem;
    }
    
    .sub-title {
        color: #666;
        text-align: center;
        font-size: 0.9rem;
        letter-spacing: 0.3em;
        margin-bottom: 2.5rem;
        text-transform: uppercase;
    }

    .stTextInput>div>div>input {
        background-color: rgba(255, 255, 255, 0.02);
        color: #d4af37;
        border: 1px solid rgba(212, 175, 55, 0.2);
        border-radius: 4px;
        padding: 0.8rem;
        font-size: 1.1rem;
    }
    .stTextInput>div>div>input:focus {
        border-color: #d4af37;
        box-shadow: 0 0 10px rgba(212, 175, 55, 0.3);
    }

    .stButton {
        display: flex;
        justify-content: center;
        margin-top: 2rem;
    }
    .stButton>button {
        background-color: rgba(212,175,55,0.1);
        color: #d4af37;
        border: 1px solid #d4af37;
        border-radius: 2px;
        padding: 0.8rem 5rem;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        text-transform: uppercase;
        letter-spacing: 0.6em;
        font-size: 1.3rem;
        font-weight: 700;
        min-width: 320px;
    }
    .stButton>button:hover {
        background-color: rgba(212,175,55,0.25);
        border-color: #fff;
        color: #fff;
        box-shadow: 0 0 30px rgba(212,175,55,0.5);
        transform: translateY(-2px);
    }

    .ritual-hint {
        color: #888;
        font-size: 1.1rem;
        margin-bottom: 1.5rem;
        letter-spacing: 0.2em;
        text-align: center;
        font-weight: 300;
    }

    /* Falling Plum Blossoms Animation */
    .plum-blossom-container {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: -1;
        overflow: hidden;
    }
    .petal {
        position: absolute;
        background-color: #ffb7c5;
        border-radius: 150% 0 150% 0;
        opacity: 0.3;
        transform: rotate(45deg);
        animation: fall linear infinite;
    }
    @keyframes fall {
        0% { transform: translate(0, -10px) rotate(45deg); opacity: 0; }
        10% { opacity: 0.4; }
        90% { opacity: 0.2; }
        100% { transform: translate(100px, 100vh) rotate(405deg); opacity: 0; }
    }

    /* Result Card Enhancement */
    .result-card {
        background: rgba(8, 8, 8, 0.98);
        border: 1px solid rgba(212,175,55,0.3);
        padding: 4rem;
        margin-top: 2.5rem;
        animation: emerge 1.2s cubic-bezier(0.23, 1, 0.32, 1);
        border-radius: 8px;
        box-shadow: 0 25px 60px rgba(0,0,0,0.9);
        position: relative;
    }
    @keyframes emerge {
        from { opacity: 0; transform: translateY(30px); filter: blur(10px); }
        to { opacity: 1; transform: translateY(0); filter: blur(0); }
    }

    .formula-trace {
        font-family: 'Courier New', monospace;
        color: #444;
        font-size: 0.85rem;
        text-align: center;
        margin-bottom: 3rem;
        border-bottom: 1px solid #1a1a1a;
        padding-bottom: 2rem;
        letter-spacing: 0.1em;
    }

    .gua-info-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 3rem;
    }
    .gua-col {
        flex: 1;
        text-align: center;
    }
    .gua-label {
        color: #555;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.3em;
        margin-bottom: 1rem;
    }
    .gua-name {
        font-size: 3.5rem;
        font-weight: 700;
        color: #d4af37;
        margin-bottom: 0.5rem;
        text-shadow: 0 0 20px rgba(212,175,55,0.4);
    }
    .gua-symbol {
        font-size: 1.8rem;
        color: #888;
        line-height: 1.2;
    }

    .moving-line-hint {
        text-align: center;
        color: #d4af37;
        font-size: 1.1rem;
        margin: 2.5rem 0;
        padding: 1rem;
        background: rgba(212,175,55,0.05);
        border: 1px dashed rgba(212,175,55,0.2);
    }

    .analysis-section {
        border-top: 1px solid #1a1a1a;
        padding-top: 3rem;
        color: #bbb;
        line-height: 2.2;
    }
    .analysis-title {
        color: #888;
        font-size: 0.9rem;
        margin-bottom: 1rem;
        letter-spacing: 0.2em;
    }
    .analysis-content {
        font-size: 1.05rem;
        letter-spacing: 0.05em;
    }

    #MainMenu, footer, header { visibility: hidden; }
</style>

<div class="plum-blossom-container">
    <div class="petal" style="width:10px; height:10px; left:10%; animation-duration:8s; animation-delay:0s;"></div>
    <div class="petal" style="width:12px; height:12px; left:25%; animation-duration:10s; animation-delay:2s;"></div>
    <div class="petal" style="width:8px; height:8px; left:40%; animation-duration:7s; animation-delay:1s;"></div>
    <div class="petal" style="width:14px; height:14px; left:60%; animation-duration:12s; animation-delay:4s;"></div>
    <div class="petal" style="width:10px; height:10px; left:80%; animation-duration:9s; animation-delay:0.5s;"></div>
    <div class="petal" style="width:11px; height:11px; left:95%; animation-duration:11s; animation-delay:3s;"></div>
</div>
"""
st.markdown(plum_blossom_css, unsafe_allow_html=True)

# --- Algorithm Engine ---

def get_shichen_index(hour):
    if hour >= 23 or hour < 1: return 1
    return (hour + 1) // 2 + 1

def get_gua_lines(idx):
    return BAGUA[idx]["lines"]

def get_gua_from_lines(lines):
    for k, v in BAGUA.items():
        if v["lines"] == lines:
            return k
    return None

def get_hexagram_lines(upper_idx, lower_idx):
    return BAGUA[lower_idx]["lines"] + BAGUA[upper_idx]["lines"]

def solve_hexagram(upper_idx, lower_idx, moving_line):
    orig_lines = get_hexagram_lines(upper_idx, lower_idx)
    orig_name = GUA_64[(upper_idx, lower_idx)]
    
    mut_lower_lines = [orig_lines[1], orig_lines[2], orig_lines[3]]
    mut_upper_lines = [orig_lines[2], orig_lines[3], orig_lines[4]]
    mut_lower = get_gua_from_lines(mut_lower_lines)
    mut_upper = get_gua_from_lines(mut_upper_lines)
    mut_name = GUA_64[(mut_upper, mut_lower)]
    
    trans_lines = list(orig_lines)
    trans_lines[moving_line - 1] = 1 if trans_lines[moving_line - 1] == 0 else 0
    trans_lower = get_gua_from_lines(trans_lines[0:3])
    trans_upper = get_gua_from_lines(trans_lines[3:6])
    trans_name = GUA_64[(trans_upper, trans_lower)]
    
    return {
        "original": {"upper": upper_idx, "lower": lower_idx, "name": orig_name, "lines": orig_lines},
        "mutual": {"upper": mut_upper, "lower": mut_lower, "name": mut_name},
        "transformed": {"upper": trans_upper, "lower": trans_lower, "name": trans_name}
    }

# --- Main UI ---

st.markdown("<h1>梅 花 易 数</h1>", unsafe_allow_html=True)
st.markdown('<div class="sub-title">时 空 算 法 · 灵 性 触 达</div>', unsafe_allow_html=True)

st.markdown('<div class="ritual-hint">屏息凝神，于心中默念所求之事</div>', unsafe_allow_html=True)
question = st.text_input("「 问 卜 」", placeholder="此处起卦，感应因果...", label_visibility="collapsed")

if st.button("感 应 天 机"):
    if not question:
        st.toast("请先于心中存疑，并输入所求之辞。", icon="🧧")
    else:
        # Calculate
        now = datetime.datetime.now()
        lunar = LunarDate.from_solar_date(now.year, now.month, now.day)
        year_gz = lunar.gz_year 
        Y_branch = year_gz[1]
        Y = BRANCH_MAP[Y_branch]
        M = lunar.month
        D = lunar.day
        H = get_shichen_index(now.hour)
        
        Upper = (Y + M + D) % 8
        if Upper == 0: Upper = 8
        Lower = (Y + M + D + H) % 8
        if Lower == 0: Lower = 8
        Moving = (Y + M + D + H) % 6
        if Moving == 0: Moving = 6
        
        results = solve_hexagram(Upper, Lower, Moving)
        
        # 30s Animation
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        stages = [
            ("📡 正在捕捉四柱波段...", 0.4),
            ("🌑 正在读取农历星历...", 0.4),
            ("⚖️ 正在进行位运算演算...", 0.5),
            ("👁️ 正在观测平行路径...", 0.5),
            ("🔮 正在提取变卦神谕...", 0.6)
        ]
        
        # total delay ~30s
        for idx, (stage, speed) in enumerate(stages):
            status_text.markdown(f'<p style="text-align:center; color:#666; font-size:1rem;">{stage}</p>', unsafe_allow_html=True)
            for p in range(20):
                progress_bar.progress((idx * 20) + p + 1)
                time.sleep(0.3)
        
        progress_bar.empty()
        status_text.empty()
        
        # Output Result Card
        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="formula-trace">
            {now.strftime('%Y-%m-%d %H:%M:%S')} | {lunar.strftime('%Y年%L%M月%D')} {BRANCHES[H-1]}时<br>
            四柱：{Y_branch}({Y}) {M}月 {D}日 {BRANCHES[H-1]}({H})时<br>
            推演：上({Y}+{M}+{D})%8={Upper} | 下({Y}+{M}+{D}+{H})%8={Lower} | 动({Y}+{M}+{D}+{H})%6={Moving}
        </div>
        """, unsafe_allow_html=True)
        
        # Hexagram Row
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f'<div class="gua-label">本卦 (ORIGIN)</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="gua-name">{results["original"]["name"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="gua-symbol">{BAGUA[Upper]["symbol"]}<br>{BAGUA[Lower]["symbol"]}</div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="gua-label">互卦 (MUTUAL)</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="gua-name">{results["mutual"]["name"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="gua-symbol">{BAGUA[results["mutual"]["upper"]]["symbol"]}<br>{BAGUA[results["mutual"]["lower"]]["symbol"]}</div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="gua-label">变卦 (TRANS)</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="gua-name">{results["transformed"]["name"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="gua-symbol">{BAGUA[results["transformed"]["upper"]]["symbol"]}<br>{BAGUA[results["transformed"]["lower"]]["symbol"]}</div>', unsafe_allow_html=True)
            
        st.markdown(f'<div class="moving-line-hint">动爻：第 {Moving} 爻动 (阴阳反转)</div>', unsafe_allow_html=True)
        
        # Analysis
        st.markdown('<div class="analysis-section">', unsafe_allow_html=True)
        st.markdown(f'<div class="analysis-title">【 占 卜 所 问 】</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="analysis-content" style="color:#eee; margin-bottom:2rem;">{question}</div>', unsafe_allow_html=True)
        
        st.markdown(f'<div class="analysis-title">【 先 予 判 词 】</div>', unsafe_allow_html=True)
        
        # Contextual Interpretation
        if Moving in [1, 3, 5]:
            path_desc = "当前动向偏向外部扩张，能量处于升腾状态。本卦显示的基础稳固，变卦指示着主动变革后的新局面。"
        else:
            path_desc = "当前动向偏向内部收敛，能量趋于静止。本卦显示的现状需内省，变卦指示着守正持重后的圆满。"
            
        st.markdown(f"""
        <div class="analysis-content">
            以此起卦，观其象：<b>{results['original']['name']}</b> 之势为主导。
            中间演化为 <b>{results['mutual']['name']}</b>，此乃隐藏之变数。
            最终归宿于 <b>{results['transformed']['name']}</b>，即为因果之终局。<br><br>
            {path_desc}<br>
            <span style="color: #666;">（注：梅花易数精髓在于“观物起卦，触景生情”，以上仅为基于时间序列之推演。）</span>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br><br><br><br><br>", unsafe_allow_html=True)
