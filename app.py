import streamlit as st
from borax.calendars.lunardate import LunarDate
import datetime
import time
import json
import os
import random

# --- 洞穴配置与石头样式 (v1.8.5 Imperial Blackout + SVG) ---
st.set_page_config(page_title="小六壬", page_icon="⛩️", layout="centered")

# --- Brute Force CSS: Aggressive Blackout & High-Quality UI ---
cyber_zen_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@300;400;700&display=swap');

    /* Global Reset - No More White */
    .stApp {
        background-color: #050505 !important;
        color: #e0e0e0 !important;
        font-family: 'Noto Serif SC', 'Microsoft YaHei', serif;
    }
    
    /* Extreme Transparency for all input containers */
    div[data-testid="stTextInput"] fieldset,
    div[data-testid="stTextInput"] div,
    div[data-testid="stTextInput"] input,
    div[data-baseweb="input"],
    div[data-baseweb="base-input"],
    div[role="presentation"],
    .st-ae, .st-af, .st-ag, .st-ah, .st-ai, .st-aj, .st-ak, .st-al, .st-am, .st-an, .st-ao,
    .css-1y4p8pa, .css-16id5y, .css-1y4p8pa {
        background-color: transparent !important;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        color: #00F2FF !important;
    }

    /* Oracle Portal Row Style */
    div[data-testid="stHorizontalBlock"] {
        background: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(0, 242, 255, 0.2) !important;
        border-radius: 50px !important;
        padding: 8px 30px !important;
        box-shadow: 0 20px 50px rgba(0,0,0,0.8) !important;
        align-items: center !important;
        margin-bottom: 2.5rem !important;
        transition: all 0.3s ease;
    }
    div[data-testid="stHorizontalBlock"]:focus-within {
        border-color: #00F2FF !important;
        box-shadow: 0 0 30px rgba(0,242,255,0.2) !important;
    }

    h1 {
        color: #00F2FF !important;
        letter-spacing: 0.8em !important;
        text-align: center !important;
        text-shadow: 0 0 40px rgba(0,242,255,0.4) !important;
        font-weight: 700 !important;
        font-size: 3.2rem !important;
        margin-top: 2rem !important;
        margin-bottom: 1rem !important;
    }

    .ritual-hint {
        color: #444 !important;
        font-size: 1.1rem;
        text-align: center;
        margin-bottom: 2rem;
        letter-spacing: 0.3em;
        font-weight: 300;
    }

    /* Result Card - High Texture */
    .result-card {
        background: rgba(10, 10, 10, 0.98) !important;
        border: 1px solid rgba(0,242,255,0.15) !important;
        padding: 3.5rem !important;
        border-radius: 12px !important;
        box-shadow: 0 30px 100px rgba(0,0,0,0.95) !important;
        margin-top: 2rem !important;
        animation: emerge 1.2s cubic-bezier(0.2, 0, 0.2, 1);
        backdrop-filter: blur(20px);
    }

    @keyframes emerge { from { opacity: 0; transform: translateY(40px); filter: blur(20px); } to { opacity: 1; transform: translateY(0); filter: blur(0); } }

    /* Action Icon (Voice/Confirm) Styling */
    .action-icon {
        color: #00F2FF !important;
        transition: all 0.3s ease !important;
        cursor: pointer !important;
    }
    .action-icon:hover {
        filter: drop-shadow(0 0 10px #00F2FF) !important;
        transform: scale(1.1);
    }

    /* Override Streamlit Secondary Button (The arrow) */
    div[data-testid="stHorizontalBlock"] button[data-testid="baseButton-secondary"] {
        background: transparent !important;
        border: none !important;
        color: #00F2FF !important;
        padding: 0 !important;
        min-width: 45px !important;
        width: 45px !important;
        height: 45px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: none !important;
    }

    /* Hide Streamlit UI Elements */
    #MainMenu, footer, header { visibility: hidden !important; }
</style>
"""
st.markdown(cyber_zen_css, unsafe_allow_html=True)

# --- Real Voice Component with SVG ---
voice_val = st.query_params.get("voice", "")
voice_html = """
<div style="display: flex; justify-content: center; align-items: center; height: 50px;">
    <button id="mic" style="background: transparent; border: none; cursor: pointer; padding: 0;">
        <svg id="mic-icon" width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="#555" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="transition: all 0.3s ease;">
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
        if (!('webkitSpeechRecognition' in window)) {
            alert("浏览器不支持语音识别");
            return;
        }
        
        const recognition = new webkitSpeechRecognition();
        recognition.lang = 'zh-CN';
        
        recognition.onstart = () => {
            icon.style.stroke = '#00F2FF';
            icon.style.filter = 'drop-shadow(0 0 10px #00F2FF)';
        };
        
        recognition.onresult = (event) => {
            const text = event.results[0][0].transcript;
            const url = new URL(window.parent.location);
            url.searchParams.set('voice', text);
            window.parent.location.href = url.href;
        };
        
        recognition.onend = () => {
            icon.style.stroke = '#555';
            icon.style.filter = 'none';
        };
        
        recognition.start();
    };
</script>
"""

# --- UI Layout ---

st.markdown("<h1>小 六 壬</h1>", unsafe_allow_html=True)
st.markdown('<div class="ritual-hint">屏息凝神 · 默念所求</div>', unsafe_allow_html=True)

# Portal Input Row
col_in, col_mic, col_go = st.columns([7, 1.2, 1.2])

with col_in:
    question = st.text_input("Oracle Input", value=voice_val, placeholder="在此输入你的疑惑...", label_visibility="collapsed")

with col_mic:
    st.components.v1.html(voice_html, height=60)

with col_go:
    # Arrow SVG icon on button
    divine_trigger = st.button("⮕", help="感应天机")
    # Replace the text with SVG via CSS hack if possible, but the ⮕ is clean.
    # We keep the ⮕ character for accessibility but use a high-quality SVG vibe in the UI.

# Number Selection
st.markdown('<div style="text-align: center; color: #333; font-size: 0.9rem; margin-top: 1.5rem;">凭直觉择一灵数</div>', unsafe_allow_html=True)
N = st.radio("N", options=list(range(1, 10)), index=4, horizontal=True, label_visibility="collapsed")

if divine_trigger:
    if not question:
        st.toast("机缘未到，请先起意。", icon="⚠️")
    else:
        # Clear voice query
        st.query_params.clear()
        
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
                <div style="text-align: center; font-family: monospace; color: #222; font-size: 0.8rem; margin-bottom: 2.5rem; letter-spacing: 2px;">
                    DESTINY_TRACE: ({M} + {D} + {H} + {N} - 3) MOD 6 = {res_idx}
                </div>
                <div style="font-size: 6rem; font-weight: 700; color: #00F2FF; text-align: center; text-shadow: 0 0 40px rgba(0,242,255,0.6); letter-spacing: 0.2em;">
                    {res['name']}
                </div>
                <div style="color: #aaa; text-align: center; margin-top: 3rem; font-size: 1.25rem; line-height: 2;">
                    <span style="color: #444; font-size: 0.8rem;">[ 问 卜 ]</span><br>
                    <span style="color: #fff;">{question}</span><br><br>
                    {res['desc']}
                </div>
            </div>
            """, unsafe_allow_html=True)

st.markdown("<p style='text-align: center; color: #111; font-size: 0.7rem; margin-top: 6rem; letter-spacing: 0.6em;'>数起于心 · 卦现于形</p>", unsafe_allow_html=True)
