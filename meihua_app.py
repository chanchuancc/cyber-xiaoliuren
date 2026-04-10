import streamlit as st
import datetime
import time
import random
import os
from borax.calendars.lunardate import LunarDate
from meihua_data import BAGUA, GUA_64, BRANCHES, BRANCH_MAP
from streamlit_mic_recorder import speech_to_text

# --- v2.1.0 Imperial Gold: Nuclear Blackout & Real Voice ---
st.set_page_config(page_title="梅花易数", page_icon="🏮", layout="centered")

# --- Brute Force CSS: Total White Elimination ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@300;400;700&display=swap');

    /* Force global dark and transparent backgrounds */
    html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"], .main {
        background-color: #050505 !important;
        background: radial-gradient(circle at center, #0a0a0a 0%, #050505 100%) !important;
        color: #d4af37 !important;
        font-family: 'Noto Serif SC', 'Microsoft YaHei', serif !important;
    }

    /* Kill all white borders, boxes, and toolbars */
    div[data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stStatusWidget"], header, footer {
        display: none !important;
        visibility: hidden !important;
    }

    /* Aggressive Transparency for Inputs */
    div[data-testid="stTextInput"] fieldset,
    div[data-testid="stTextInput"] div,
    div[data-testid="stTextInput"] input,
    div[data-baseweb="input"],
    div[role="presentation"],
    [data-testid="stForm"] {
        background-color: transparent !important;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        color: #d4af37 !important;
    }

    /* The Unified Capsule (Portal) */
    .portal-container {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(212, 175, 55, 0.2) !important;
        border-radius: 60px !important;
        padding: 5px 20px !important;
        box-shadow: 0 15px 50px rgba(0,0,0,1) !important;
        display: flex;
        align-items: center;
        margin-bottom: 2rem;
        transition: border 0.3s ease;
    }
    .portal-container:focus-within {
        border-color: #d4af37 !important;
    }

    h1 {
        color: #d4af37 !important;
        letter-spacing: 0.8em !important;
        text-align: center !important;
        text-shadow: 0 0 30px rgba(212,175,55,0.5) !important;
        font-weight: 700 !important;
        font-size: 3.5rem !important;
        margin-top: 1rem !important;
    }

    .ritual-hint {
        color: #555 !important;
        font-size: 1.1rem;
        text-align: center;
        margin-bottom: 2rem;
        letter-spacing: 0.3em;
    }

    /* Mic Recorder Custom Styling (Attempt to blend) */
    div.st-emotion-cache-1pxm8lv { background: transparent !important; border: none !important; }
    button[kind="secondary"] { 
        background: transparent !important; 
        border: none !important; 
        color: #d4af37 !important; 
        font-size: 1.5rem !important;
    }

    /* Vector Button Style */
    div[data-testid="stButton"] > button {
        background: transparent !important;
        border: none !important;
        color: transparent !important;
        width: 50px !important;
        height: 50px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        position: relative;
    }
    div[data-testid="stButton"] > button::after {
        content: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="%23D4AF37" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>');
        position: absolute;
        top: 50%; left: 50%; transform: translate(-50%, -50%);
        transition: all 0.2s ease;
    }
    div[data-testid="stButton"] > button:hover::after {
        transform: translate(-50%, -50%) scale(1.2);
        filter: drop-shadow(0 0 10px #D4AF37);
    }

    /* Falling Plum Blossoms */
    .plum-blossom-container { position: fixed; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: -1; overflow: hidden; }
    .petal { position: absolute; background-color: #ffb7c5; border-radius: 150% 0 150% 0; opacity: 0.2; transform: rotate(45deg); animation: fall linear infinite; }
    @keyframes fall { 0% { transform: translate(0, -10px) rotate(45deg); opacity: 0; } 10% { opacity: 0.3; } 90% { opacity: 0.2; } 100% { transform: translate(150px, 100vh) rotate(405deg); opacity: 0; } }

    /* Result Card */
    .result-card {
        background: rgba(10, 10, 10, 0.99) !important;
        border: 1px solid rgba(212,175,55,0.2) !important;
        padding: 3.5rem !important;
        border-radius: 12px !important;
        box-shadow: 0 40px 100px rgba(0,0,0,1) !important;
        margin-top: 2rem !important;
        animation: em 1.5s ease-out;
    }
    @keyframes em { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }
</style>

<div class="plum-blossom-container">
    <div class="petal" style="width:12px; height:12px; left:5%; animation-duration:10s; animation-delay:0s;"></div>
    <div class="petal" style="width:16px; height:16px; left:20%; animation-duration:14s; animation-delay:4s;"></div>
    <div class="petal" style="width:10px; height:10px; left:45%; animation-duration:9s; animation-delay:2s;"></div>
    <div class="petal" style="width:14px; height:14px; left:70%; animation-duration:12s; animation-delay:6s;"></div>
    <div class="petal" style="width:11px; height:11px; left:88%; animation-duration:11s; animation-delay:1s;"></div>
</div>
""", unsafe_allow_html=True)

# --- Voice Logic ---
if "v_text" not in st.session_state:
    st.session_state.v_text = ""

# --- UI Layout ---
st.markdown("<h1>梅 花 易 数</h1>", unsafe_allow_html=True)
st.markdown('<div class="ritual-hint">屏息凝神 · 默念所求</div>', unsafe_allow_html=True)

# Integrated Input Row
col_in, col_mic, col_go = st.columns([8, 1.5, 1.2])

with col_mic:
    # This component shows a mic button and handles STT
    voice_result = speech_to_text(language='zh-CN', start_prompt="🎙️", stop_prompt="⏹️", key='mic_recorder')
    if voice_result:
        st.session_state.v_text = voice_result

with col_in:
    question = st.text_input("Q", value=st.session_state.v_text, placeholder="在此感应因果...", label_visibility="collapsed")

with col_go:
    divine_trigger = st.button(" ")

# --- Algorithm Engine ---
def solve_hexagram(u, l, m):
    orig = BAGUA[l]["lines"] + BAGUA[u]["lines"]
    mut_l = next(k for k, v in BAGUA.items() if v["lines"] == [orig[1], orig[2], orig[3]])
    mut_u = next(k for k, v in BAGUA.items() if v["lines"] == [orig[2], orig[3], orig[4]])
    trans_lines = list(orig); trans_lines[m-1] = 1 - trans_lines[m-1]
    trans_l = next(k for k, v in BAGUA.items() if v["lines"] == trans_lines[0:3])
    trans_u = next(k for k, v in BAGUA.items() if v["lines"] == trans_lines[3:6])
    return {"o": GUA_64[(u,l)], "m": GUA_64[(mut_u,mut_l)], "t": GUA_64[(trans_u,trans_l)], "u_m": mut_u, "l_m": mut_l, "u_t": trans_u, "l_t": trans_l}

if divine_trigger:
    if not question:
        st.toast("「天机未定」：请先输入所求之事。", icon="⚠️")
    else:
        st.session_state.v_text = "" # Clear for next time
        progress = st.progress(0)
        st_text = st.empty()
        stages = ["捕捉四柱波段...", "读取农历星历...", "位运算演算...", "观测平行路径..."]
        for i, s in enumerate(stages):
            st_text.markdown(f'<p style="text-align:center; color:#666; font-size:1.1rem; letter-spacing:0.2em;">{s}</p>', unsafe_allow_html=True)
            for p in range(25): progress.progress(i*25+p+1); time.sleep(0.2)
        progress.empty(); st_text.empty()
        
        now = datetime.datetime.now(); l = LunarDate.from_solar_date(now.year, now.month, now.day)
        Y = BRANCH_MAP[l.gz_year[1]]; M, D, H = l.month, l.day, (1 if now.hour >= 23 or now.hour < 1 else (now.hour+1)//2+1)
        Up, Lo, Mov = (Y+M+D)%8 or 8, (Y+M+D+H)%8 or 8, (Y+M+D+H)%6 or 6
        res = solve_hexagram(Up, Lo, Mov)
        
        st.markdown(f"""
        <div class="result-card">
            <div style="font-family:monospace; color:#222; font-size:0.8rem; text-align:center; border-bottom:1px solid #111; padding-bottom:1.5rem; margin-bottom:2.5rem;">({Y}+{M}+{D})%8={Up} | ({Y}+{M}+{D}+{H})%8={Lo} | ({Y}+{M}+{D}+{H})%6={Mov}</div>
            <div style="display:flex; justify-content:space-between; text-align:center; margin-bottom:3rem;">
                <div><div style="color:#555; font-size:0.75rem; letter-spacing:3px;">本卦 ORIGINAL</div><div style="font-size:3.5rem; font-weight:700; color:#d4af37;">{res['o']}</div><div style="font-size:2rem; color:#666; line-height:1.1;">{BAGUA[Up]['symbol']}<br>{BAGUA[Lo]['symbol']}</div></div>
                <div><div style="color:#555; font-size:0.75rem; letter-spacing:3px;">互卦 MUTUAL</div><div style="font-size:3.5rem; font-weight:700; color:#d4af37;">{res['m']}</div><div style="font-size:2rem; color:#666; line-height:1.1;">{BAGUA[res['u_m']]['symbol']}<br>{BAGUA[res['l_m']]['symbol']}</div></div>
                <div><div style="color:#555; font-size:0.75rem; letter-spacing:3px;">变卦 TRANS</div><div style="font-size:3.5rem; font-weight:700; color:#d4af37;">{res['t']}</div><div style="font-size:2rem; color:#666; line-height:1.1;">{BAGUA[res['u_t']]['symbol']}<br>{BAGUA[res['l_t']]['symbol']}</div></div>
            </div>
            <div style="text-align:center; color:#d4af37; font-size:1.2rem; padding:1.5rem; background:rgba(212,175,55,0.04); border:1px solid rgba(212,175,55,0.15); border-radius:8px; margin-bottom:3rem;">动爻：第 {Mov} 爻动</div>
            <div style="border-top:1px solid #1a1a1a; padding-top:3rem;">
                <div style="color:#666; font-size:0.8rem; letter-spacing:3px; margin-bottom:1rem;">[ 问 卜 ]</div>
                <div style="font-size:1.4rem; color:#fff; margin-bottom:2rem;">{question}</div>
                <div style="color:#bbb; font-size:1.1rem; line-height:2.3;">天机已现。本卦为因，互卦为变，变卦为果。宜守正持重，顺势而为。</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br><br><p style='text-align:center; color:#1a1a1a; font-size:0.7rem; letter-spacing:0.5em;'>ALGORITHM IS FATE · CODE IS TRUTH</p>", unsafe_allow_html=True)
