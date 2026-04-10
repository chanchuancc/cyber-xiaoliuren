import streamlit as st
import datetime
import time
import random
import os

# --- NUCLEAR BLACKOUT (v2.0.0 "Imperial Void") ---
st.set_page_config(page_title="梅花易数", page_icon="🏮", layout="centered")

# Force Dark Mode and Kill White Backgrounds
# Version marker: 2.0.0
st.markdown("""
<style>
    /* Version 2.0.0 Force Reset */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"], .main {
        background-color: #050505 !important;
        background: #050505 !important;
        color: #d4af37 !important;
    }
    
    /* Ensure all text is gold by default */
    * { color: #d4af37 !important; }
    
    /* Target the central block */
    .block-container {
        background-color: #050505 !important;
        padding-top: 1rem !important;
    }

    /* Input Bar Wrapper */
    div[data-testid="stHorizontalBlock"] {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(212, 175, 55, 0.3) !important;
        border-radius: 60px !important;
        padding: 10px 20px 10px 30px !important;
        align-items: center !important;
        box-shadow: 0 20px 60px rgba(0,0,0,0.9) !important;
    }

    /* Clean Input Box */
    [data-testid="stTextInput"] div[data-baseweb="input"],
    [data-testid="stTextInput"] div[data-baseweb="base-input"],
    [data-testid="stTextInput"] input {
        background-color: transparent !important;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        color: #d4af37 !important;
        font-size: 1.2rem !important;
    }
    input::placeholder { color: #333 !important; }
    [data-testid="stTextInput"] label { display: none !important; }

    /* The Confirm Button (The arrow) */
    div[data-testid="stHorizontalBlock"] button {
        background: #d4af37 !important;
        color: #050505 !important;
        border: none !important;
        border-radius: 50% !important;
        width: 50px !important;
        height: 50px !important;
        min-width: 50px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 0 20px rgba(212,175,55,0.4) !important;
        cursor: pointer !important;
    }
    div[data-testid="stHorizontalBlock"] button p { color: #050505 !important; }
    div[data-testid="stHorizontalBlock"] button:hover {
        background: #fff !important;
        transform: scale(1.1);
    }

    /* Hide Streamlit Garbage */
    header, footer, [data-testid="stHeader"], [data-testid="stToolbar"] {
        display: none !important;
        visibility: hidden !important;
    }
</style>
""", unsafe_allow_html=True)

# --- REAL VOICE BUTTON (Direct Component) ---
st.markdown("<p style='text-align: center; color: #666; font-size: 0.8rem;'>v2.0.0 Imperial Void</p>", unsafe_allow_html=True)

# We'll use a session state to handle voice text
if "v_text" not in st.session_state:
    st.session_state.v_text = ""

# Component for Voice
from streamlit_mic_recorder import mic_recorder, speech_to_text

# Show Voice Recorder
c_v1, c_v2, c_v3 = st.columns([1, 1, 1])
with c_v2:
    text = speech_to_text(language='zh', start_prompt="点击感应天音 🎙️", stop_prompt="正在转化...", key='STT')
    if text:
        st.session_state.v_text = text

# --- Main UI ---
st.markdown("<h1 style='text-align: center;'>梅 花 易 数</h1>", unsafe_allow_html=True)

# Portal Bar Row
col1, col2 = st.columns([10, 1.5])
with col1:
    q = st.text_input("Divine Question", value=st.session_state.v_text, placeholder="在此输入心中所求...", label_visibility="collapsed")
with col2:
    divine_trigger = st.button("⮕")

# --- Logic ---
try:
    from borax.calendars.lunardate import LunarDate
    from meihua_data import BAGUA, GUA_64, BRANCHES, BRANCH_MAP
except:
    st.error("同步星历中...")
    st.stop()

if divine_trigger:
    if not q: st.toast("请起意。")
    else:
        with st.spinner("推演中..."): time.sleep(1)
        now = datetime.datetime.now()
        lunar = LunarDate.from_solar_date(now.year, now.month, now.day)
        Y = BRANCH_MAP[lunar.gz_year[1]]
        M, D, H = lunar.month, lunar.day, (1 if now.hour >= 23 or now.hour < 1 else (now.hour + 1) // 2 + 1)
        U, L, Mov = (Y+M+D)%8 or 8, (Y+M+D+H)%8 or 8, (Y+M+D+H)%6 or 6
        st.success(f"本卦：{GUA_64[(U,L)]} | 动爻：第 {Mov} 爻")
