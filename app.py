import streamlit as st
from borax.calendars.lunardate import LunarDate
import datetime
import time
import json
import os
import random

# --- 洞穴配置与石头样式 (v1.9.5 Imperial Total Blackout) ---
st.set_page_config(page_title="小六壬", page_icon="⛩️", layout="centered")

# --- 暴力消白令: AGGRESSIVE CSS OVERRIDE ---
# We target Streamlit's internal classes to ensure transparency
total_blackout_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@300;400;700&display=swap');

    /* 1. 根基玄曜 */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stToolbar"] {
        background-color: #050505 !important;
        color: #e0e0e0 !important;
        font-family: 'Noto Serif SC', 'Microsoft YaHei', serif;
    }
    
    /* 2. 暴力消除所有白框背景 (Targeting Shadow DOM elements and internal classes) */
    div[data-testid="stTextInput"] fieldset,
    div[data-testid="stTextInput"] div,
    div[data-testid="stTextInput"] input,
    div[data-baseweb="input"],
    div[data-baseweb="base-input"],
    div[role="presentation"],
    .st-ae, .st-af, .st-ag, .st-ah, .st-ai, .st-aj, .st-ak, .st-al, .st-am, .st-an, .st-ao {
        background-color: transparent !important;
        background: transparent !important;
        border-color: transparent !important;
        box-shadow: none !important;
        color: #00F2FF !important;
    }

    /* 3. 帝国入口长条 (Oracle Capsule) */
    div[data-testid="stHorizontalBlock"]:has(div[data-testid="stTextInput"]) {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(0, 242, 255, 0.2) !important;
        border-radius: 60px !important;
        padding: 5px 25px !important;
        box-shadow: 0 15px 50px rgba(0,0,0,0.9) !important;
        align-items: center !important;
        margin-bottom: 2.5rem !important;
        transition: all 0.4s ease;
    }
    div[data-testid="stHorizontalBlock"]:has(div[data-testid="stTextInput"]):focus-within {
        border-color: #00F2FF !important;
        box-shadow: 0 0 30px rgba(0,242,255,0.3) !important;
    }

    /* 4. 输入文字高亮 */
    div[data-testid="stTextInput"] input {
        color: #00F2FF !important;
        font-size: 1.2rem !important;
        caret-color: #00F2FF !important;
        background: transparent !important;
    }
    div[data-testid="stTextInput"] label { display: none !important; }

    /* 5. 标题与指引 */
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

    /* 6. 结果神龛 (Result Card) */
    .result-card {
        background: rgba(10, 10, 10, 0.98) !important;
        border: 1px solid rgba(0,242,255,0.1) !important;
        padding: 3rem !important;
        border-radius: 12px !important;
        box-shadow: 0 40px 120px rgba(0,0,0,1) !important;
        margin-top: 2rem !important;
        animation: emerge 1.5s cubic-bezier(0.2, 0, 0.2, 1);
    }
    @keyframes emerge { from { opacity: 0; transform: translateY(50px); filter: blur(20px); } to { opacity: 1; transform: translateY(0); filter: blur(0); } }

    /* 7. Radio Buttons (靈數抉择) Style */
    div[data-testid="stRadio"] label {
        color: #333 !important;
        font-family: monospace !important;
    }
    div[data-testid="stRadio"] label:hover { color: #00F2FF !important; }
    div[data-testid="stRadio"] label[data-baseweb="radio"] > div:first-child { display: none !important; }
    div[data-testid="stRadio"] label:has(input:checked) {
        color: #00F2FF !important;
        text-shadow: 0 0 10px #00F2FF !important;
    }

    /* 8. Confirm Button (Arrow) */
    div[data-testid="stHorizontalBlock"] button[data-testid="baseButton-secondary"] {
        background: transparent !important;
        border: none !important;
        color: #00F2FF !important;
        width: 50px !important;
        height: 50px !important;
        min-width: 50px !important;
        font-size: 1.8rem !important;
        transition: transform 0.3s ease !important;
    }
    div[data-testid="stHorizontalBlock"] button[data-testid="baseButton-secondary"]:hover {
        transform: scale(1.2) translateX(5px) !important;
        background: transparent !important;
    }

    /* Hide Streamlit Native UI */
    #MainMenu, footer, header { visibility: hidden !important; }
</style>
"""
st.markdown(total_blackout_css, unsafe_allow_html=True)

# --- Real Voice Logic (Real Voice API) ---
voice_val = st.query_params.get("v", "")
voice_html = """
<div style="display: flex; justify-content: center; align-items: center; height: 50px;">
    <button id="mic" style="background: transparent; border: none; cursor: pointer; padding: 0;">
        <svg id="mic-icon" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#444" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="transition: 0.3s;">
            <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
            <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
            <line x1="12" y1="19" x2="12" y2="23"></line>
            <line x1="8" y1="23" x2="16" y2="23"></line>
        </svg>
    </button>
</div>
<script>
    const btn = document.getElementById('mic');
    const icon = document.getElementById('mic-icon');
    btn.onclick = () => {
        if (!('webkitSpeechRecognition' in window)) { alert("浏览器不支持语音感应"); return; }
        const rec = new webkitSpeechRecognition();
        rec.lang = 'zh-CN';
        rec.onstart = () => { icon.style.stroke = '#00F2FF'; icon.style.filter = 'drop-shadow(0 0 15px #00F2FF)'; };
        rec.onresult = (e) => {
            const t = e.results[0][0].transcript;
            const url = new URL(window.parent.location.href);
            url.searchParams.set('v', t);
            window.parent.location.href = url.href;
        };
        rec.onend = () => { icon.style.stroke = '#444'; icon.style.filter = 'none'; };
        rec.start();
    };
</script>
"""

# --- UI Layout ---
st.markdown("<h1>小 六 壬</h1>", unsafe_allow_html=True)
st.markdown('<div class="ritual-hint">屏息凝神 · 默念所求</div>', unsafe_allow_html=True)

# Integrated Input Row
col_in, col_mic, col_go = st.columns([8, 1, 1])
with col_in:
    question = st.text_input("Oracle Input", value=voice_val, placeholder="在此输入你的疑惑...", label_visibility="collapsed")
with col_mic:
    st.components.v1.html(voice_html, height=60)
with col_go:
    divine_trigger = st.button("⮕", help="感应天机")

# Number Selection
st.markdown('<div style="text-align: center; color: #222; font-size: 0.8rem; margin-top: 1rem; letter-spacing: 3px;">灵 数 抉 择</div>', unsafe_allow_html=True)
N = st.radio("N", options=list(range(1, 10)), index=4, horizontal=True, label_visibility="collapsed")

if divine_trigger:
    if not question:
        st.toast("机缘未到，请先起意。", icon="⚠️")
    else:
        st.query_params.clear()
        with st.spinner("正在捕捉天机..."):
            time.sleep(2)
            now = datetime.datetime.now()
            lunar = LunarDate.from_solar_date(now.year, now.month, now.day)
            M, D = lunar.month, lunar.day
            H = 1 if now.hour >= 23 or now.hour < 1 else (now.hour + 1) // 2 + 1
            res_idx = (M + D + H + N - 3) % 6
            
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
                <div style="text-align: center; font-family: monospace; color: #1a1a1a; font-size: 0.8rem; margin-bottom: 3rem; letter-spacing: 3px;">
                    TRACE: ({M}+{D}+{H}+{N}-3) MOD 6 = {res_idx}
                </div>
                <div style="font-size: 6.5rem; font-weight: 700; color: #00F2FF; text-align: center; text-shadow: 0 0 50px rgba(0,242,255,0.6); letter-spacing: 0.3em;">
                    {res['name']}
                </div>
                <div style="color: #888; text-align: center; margin-top: 4rem; font-size: 1.3rem; line-height: 2.2;">
                    <span style="color: #333; font-size: 0.8rem; letter-spacing: 5px;">[ 问 卜 ]</span><br>
                    <span style="color: #fff; font-weight: 400;">{question}</span><br><br>
                    <div style="border-top: 1px solid #111; padding-top: 2rem; margin-top: 2rem;">{res['desc']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

st.markdown("<p style='text-align: center; color: #111; font-size: 0.7rem; margin-top: 8rem; letter-spacing: 0.8em;'>数 起 于 心 · 卦 现 于 形</p>", unsafe_allow_html=True)
