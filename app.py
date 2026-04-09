import streamlit as st
from borax.calendars.lunardate import LunarDate
import datetime
import time
import json
import os
import random

# --- 洞穴配置与石头样式 (v1.7.0 Imperial Blackout) ---
st.set_page_config(page_title="小六壬", page_icon="⛩️", layout="centered")

# --- Brute Force CSS: No White Allowed ---
cyber_zen_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@300;400;700&display=swap');

    /* Global Reset */
    .stApp {
        background-color: #050505 !important;
        color: #e0e0e0 !important;
        font-family: 'Noto Serif SC', 'Microsoft YaHei', serif;
    }
    
    /* Aggressive Transparency for all inputs and containers */
    div[data-testid="stTextInput"] fieldset,
    div[data-testid="stTextInput"] div,
    div[data-testid="stTextInput"] input,
    div[data-baseweb="input"],
    div[data-baseweb="base-input"],
    .st-ae, .st-af, .st-ag, .st-ah, .st-ai, .st-aj, .st-ak, .st-al, .st-am, .st-an, .st-ao,
    div[role="presentation"] {
        background-color: transparent !important;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        color: #00F2FF !important;
    }

    /* Target the parent container of the input row */
    div[data-testid="stHorizontalBlock"] {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(0, 242, 255, 0.2) !important;
        border-radius: 50px !important;
        padding: 5px 25px !important;
        box-shadow: 0 15px 40px rgba(0,0,0,0.8) !important;
        align-items: center !important;
        margin-bottom: 2rem !important;
    }

    /* Style the input text */
    div[data-testid="stTextInput"] input {
        font-size: 1.2rem !important;
        letter-spacing: 1px !important;
        outline: none !important;
    }

    h1 {
        color: #00F2FF !important;
        letter-spacing: 0.8em !important;
        text-align: center !important;
        text-shadow: 0 0 30px rgba(0,242,255,0.4) !important;
        font-weight: 700 !important;
        font-size: 3rem !important;
        margin-top: 2rem !important;
    }

    .ritual-hint {
        color: #555 !important;
        font-size: 1.1rem;
        text-align: center;
        margin-bottom: 2rem;
        letter-spacing: 0.3em;
    }

    /* Result Card */
    .result-card {
        background: rgba(10, 10, 10, 0.98) !important;
        border: 1px solid rgba(0,242,255,0.15) !important;
        padding: 3rem !important;
        border-radius: 8px !important;
        box-shadow: 0 20px 60px rgba(0,0,0,0.9) !important;
        margin-top: 2rem !important;
        animation: emerge 1s ease-out;
    }

    @keyframes emerge { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }

    /* Hide Streamlit UI */
    #MainMenu, footer, header { visibility: hidden !important; }
</style>
"""
st.markdown(cyber_zen_css, unsafe_allow_html=True)

# --- Real Voice Logic ---
# Catch voice input from query params
voice_val = st.query_params.get("voice", "")

# Voice component (HTML + JS)
# We use a cleaner approach: a hidden component that can trigger parent navigation
voice_html = """
<div style="display: flex; justify-content: center; align-items: center; height: 50px;">
    <button id="mic" style="background: transparent; border: none; cursor: pointer; font-size: 30px; color: #555; transition: 0.3s;">
        🎙️
    </button>
</div>
<script>
    const btn = document.getElementById('mic');
    let active = false;
    
    btn.onclick = () => {
        if (!('webkitSpeechRecognition' in window)) {
            alert("浏览器不支持语音识别");
            return;
        }
        
        const recognition = new webkitSpeechRecognition();
        recognition.lang = 'zh-CN';
        recognition.interimResults = false;
        
        recognition.onstart = () => {
            btn.style.color = '#00F2FF';
            btn.style.textShadow = '0 0 15px #00F2FF';
        };
        
        recognition.onresult = (event) => {
            const text = event.results[0][0].transcript;
            const url = new URL(window.parent.location);
            url.searchParams.set('voice', text);
            window.parent.location.href = url.href;
        };
        
        recognition.onerror = () => {
            btn.style.color = '#f00';
        };
        
        recognition.onend = () => {
            if (!active) btn.style.color = '#555';
        };
        
        recognition.start();
    };
</script>
"""

# --- UI Layout ---

st.markdown("<h1>小 六 壬</h1>", unsafe_allow_html=True)
st.markdown('<div class="ritual-hint">屏息凝神 · 默念所求</div>', unsafe_allow_html=True)

# Integrated Input Row
# We use columns to match the "Portal" look
col_in, col_mic, col_go = st.columns([7, 1.2, 1.2])

with col_in:
    # Use the voice_val if present
    question = st.text_input("Question", value=voice_val, placeholder="在此输入你的疑惑...", label_visibility="collapsed")

with col_mic:
    # Real Voice Component
    st.components.v1.html(voice_html, height=60)

with col_go:
    # Arrow button
    divine_trigger = st.button("⮕", help="感应天机")

# Number Selection
st.markdown('<div style="text-align: center; color: #333; font-size: 0.9rem; margin-top: 1rem;">择一灵数</div>', unsafe_allow_html=True)
N = st.radio("N", options=list(range(1, 10)), index=4, horizontal=True, label_visibility="collapsed")

if divine_trigger:
    if not question:
        st.toast("机缘未到，请先起意。", icon="⚠️")
    else:
        # Clear query params to avoid sticky voice input on next refresh
        st.query_params.clear()
        
        with st.spinner("正在捕捉天机..."):
            time.sleep(2) # Ritual delay
            now = datetime.datetime.now()
            lunar = LunarDate.from_solar_date(now.year, now.month, now.day)
            M, D = lunar.month, lunar.day
            H = 1 if now.hour >= 23 or now.hour < 1 else (now.hour + 1) // 2 + 1
            
            # Formula
            res_idx = (M + D + H + N - 3) % 6
            
            # GUA Data
            GUA_DATA = {
                1: {"name": "大安", "desc": "身不动时，事事昌吉。求财坤方，宅舍安康。"},
                2: {"name": "留连", "desc": "卒未归时，事多阻碍。官事宜缓，去者未回。"},
                3: {"name": "速喜", "desc": "人即至时，喜来临门。求财南行，病者放心。"},
                4: {"name": "赤口", "desc": "官事凶时，口舌紧防。失物急寻，行人惊慌。"},
                5: {"name": "小吉", "desc": "人来喜时，最吉昌顺。路上商量，阴人报喜。"},
                0: {"name": "空亡", "desc": "音信稀时，事不吉祥。求财无利，行人灾殃。"}
            }
            res = GUA_DATA[res_idx]

            st.markdown(f"""
            <div class="result-card">
                <div style="text-align: center; font-family: monospace; color: #222; font-size: 0.8rem; margin-bottom: 2rem;">
                    TRACE: ({M} + {D} + {H} + {N} - 3) MOD 6 = {res_idx}
                </div>
                <div style="font-size: 5rem; font-weight: 700; color: #00F2FF; text-align: center; text-shadow: 0 0 30px rgba(0,242,255,0.5);">
                    {res['name']}
                </div>
                <div style="color: #888; text-align: center; margin-top: 2rem; font-size: 1.2rem; line-height: 1.8;">
                    <b>问卜</b>：{question}<br><br>
                    {res['desc']}
                </div>
            </div>
            """, unsafe_allow_html=True)

st.markdown("<p style='text-align: center; color: #111; font-size: 0.7rem; margin-top: 5rem; letter-spacing: 0.5em;'>数起于心 · 卦现于形</p>", unsafe_allow_html=True)
