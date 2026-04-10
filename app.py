import streamlit as st
from borax.calendars.lunardate import LunarDate
import datetime
import time
import json
import os
import random
from streamlit_mic_recorder import speech_to_text

# --- 洞穴配置 (v2.0.0 Imperial Blackout) ---
st.set_page_config(page_title="小六壬", page_icon="⛩️", layout="centered")

# --- NUCLEAR CSS OVERRIDE: Eliminate ALL white backgrounds ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@300;400;700&display=swap');

    /* 1. Force the entire page to be dark */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"], .stApp {
        background-color: #050505 !important;
        background: #050505 !important;
        color: #00F2FF !important;
        font-family: 'Noto Serif SC', 'Microsoft YaHei', serif;
    }

    /* 2. Target specific elements that might have white backgrounds */
    div[data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stStatusWidget"] {
        display: none !important;
    }

    /* 3. Kill all white backgrounds in inputs and containers */
    div[data-testid="stTextInput"] *, 
    div[data-baseweb="input"] *, 
    div[data-baseweb="base-input"] *,
    div[role="presentation"] *,
    .st-ae, .st-af, .st-ag, .st-ah, .st-ai, .st-aj, .st-ak, .st-al, .st-am, .st-an, .st-ao {
        background-color: transparent !important;
        background: transparent !important;
        color: #00F2FF !important;
        border-color: transparent !important;
        box-shadow: none !important;
    }

    /* 4. The Oracle Bar (Capsule) */
    div[data-testid="stHorizontalBlock"] {
        background: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(0, 242, 255, 0.15) !important;
        border-radius: 60px !important;
        padding: 5px 30px !important;
        box-shadow: 0 10px 40px rgba(0,0,0,0.8) !important;
        align-items: center !important;
        margin-bottom: 2rem !important;
    }

    /* 5. Input Text Style */
    div[data-testid="stTextInput"] input {
        font-size: 1.2rem !important;
        caret-color: #00F2FF !important;
        outline: none !important;
    }

    /* 6. Mic Recorder Component Customization */
    div.st-emotion-cache-1pxm8lv, button[kind="secondary"] {
        background-color: transparent !important;
        border: none !important;
        color: #00F2FF !important;
    }

    /* 7. Result Card */
    .result-card {
        background: rgba(10, 10, 10, 0.98) !important;
        border: 1px solid rgba(0, 242, 255, 0.1) !important;
        padding: 3rem !important;
        border-radius: 12px !important;
        box-shadow: 0 40px 120px rgba(0,0,0,1) !important;
        margin-top: 2rem !important;
        animation: slideUp 1.2s ease-out;
    }
    @keyframes slideUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }

    /* 8. Typography */
    h1 {
        color: #00F2FF !important;
        letter-spacing: 0.8em !important;
        text-align: center !important;
        text-shadow: 0 0 40px rgba(0,242,255,0.4) !important;
        font-weight: 700 !important;
        font-size: 3.2rem !important;
        margin-top: 2rem !important;
    }
    .ritual-hint {
        color: #444 !important;
        font-size: 1.1rem;
        text-align: center;
        margin-bottom: 2rem;
        letter-spacing: 0.3em;
    }

    /* Hide Streamlit Chrome */
    #MainMenu, footer, header { visibility: hidden !important; }
</style>
""", unsafe_allow_html=True)

# --- UI Layout ---
st.markdown("<h1>小 六 壬</h1>", unsafe_allow_html=True)
st.markdown('<div class="ritual-hint">屏息凝神 · 默念所求</div>', unsafe_allow_html=True)

# Portal Input row
col_in, col_mic, col_go = st.columns([7, 1.5, 1.2])

with col_mic:
    # Real Speech-to-Text Component
    text_from_voice = speech_to_text(language='zh-CN', start_prompt="🎙️", stop_prompt="⏹️", key='mic')

with col_in:
    # Use the voice text if available, else empty or manual input
    placeholder_text = "在此输入你的疑惑..."
    if text_from_voice:
        st.session_state.question = text_from_voice
    
    question = st.text_input("Oracle Input", value=st.session_state.get('question', ""), placeholder=placeholder_text, label_visibility="collapsed")

with col_go:
    divine_trigger = st.button("⮕", help="感应天机")

# Number Selection
st.markdown('<div style="text-align: center; color: #222; font-size: 0.8rem; margin-top: 1.5rem; letter-spacing: 2px;">灵 数 抉 择</div>', unsafe_allow_html=True)
N = st.radio("N", options=list(range(1, 10)), index=4, horizontal=True, label_visibility="collapsed")

if divine_trigger:
    if not question:
        st.toast("机缘未到，请先起意。", icon="⚠️")
    else:
        with st.spinner("正在捕捉天机..."):
            time.sleep(2)
            now = datetime.datetime.now()
            lunar = LunarDate.from_solar_date(now.year, now.month, now.day)
            M, D = lunar.month, lunar.day
            H = 1 if now.hour >= 23 or now.hour < 1 else (now.hour + 1) // 2 + 1
            res_idx = (M + D + H + N - 3) % 6
            
            GUA_MAP = {
                1: {"name": "大安", "desc": "身不动时，事事昌吉。求财坤方，宅舍安康。"},
                2: {"name": "留连", "desc": "卒未归时，事多阻碍。官事宜缓，去者未回。"},
                3: {"name": "速喜", "desc": "人即至时，喜来临门。求财南行，病者放心。"},
                4: {"name": "赤口", "desc": "官事凶时，口舌紧防。失物急寻，行人惊慌。"},
                5: {"name": "小吉", "desc": "人来喜时，最吉昌顺。路上商量，阴人报喜。"},
                0: {"name": "空亡", "desc": "音信稀时，事不吉祥。求财无利，行人灾殃。"}
            }
            res = GUA_MAP[res_idx]

            st.markdown(f"""
            <div class="result-card">
                <div style="text-align: center; font-family: monospace; color: #1a1a1a; font-size: 0.8rem; margin-bottom: 3rem; letter-spacing: 3px;">
                    DESTINY_TRACE: ({M}+{D}+{H}+{N}-3) MOD 6 = {res_idx}
                </div>
                <div style="font-size: 6rem; font-weight: 700; color: #00F2FF; text-align: center; text-shadow: 0 0 40px rgba(0,242,255,0.6); letter-spacing: 0.2em;">
                    {res['name']}
                </div>
                <div style="color: #888; text-align: center; margin-top: 3rem; font-size: 1.3rem; line-height: 2.2;">
                    <span style="color: #333; font-size: 0.8rem; letter-spacing: 5px;">[ 问 卜 ]</span><br>
                    <span style="color: #fff; font-weight: 400;">{question}</span><br><br>
                    <div style="border-top: 1px solid #111; padding-top: 2rem; margin-top: 2rem;">{res['desc']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

st.markdown("<p style='text-align: center; color: #111; font-size: 0.7rem; margin-top: 8rem; letter-spacing: 0.8em;'>数 起 于 心 · 卦 现 于 形</p>", unsafe_allow_html=True)
