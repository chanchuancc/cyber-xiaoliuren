import streamlit as st
import datetime
import time
import random
import os
import json

# --- 1. FORCE THEME & UI ---
st.set_page_config(page_title="小六壬", page_icon="⛩️", layout="centered")

st.markdown("""
<style>
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #050505 !important;
        color: #00F2FF !important;
    }
    .main .block-container {
        padding-top: 2rem !important;
    }
    [data-testid="stHeader"], [data-testid="stToolbar"] { display: none !important; }

    /* Portal Bar */
    div[data-testid="stHorizontalBlock"] {
        background: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(0, 242, 255, 0.2) !important;
        border-radius: 60px !important;
        padding: 8px 20px 8px 30px !important;
        align-items: center !important;
        box-shadow: 0 20px 60px rgba(0,0,0,0.8) !important;
    }

    div[data-testid="stTextInput"] div[data-baseweb="input"],
    div[data-testid="stTextInput"] div[data-baseweb="base-input"],
    div[data-testid="stTextInput"] input {
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        color: #00F2FF !important;
    }
    div[data-testid="stTextInput"] label { display: none !important; }

    /* Confirm Button */
    div[data-testid="stHorizontalBlock"] button {
        background: #00F2FF !important;
        color: #050505 !important;
        border: none !important;
        border-radius: 50% !important;
        width: 45px !important;
        height: 45px !important;
        min-width: 45px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 0 15px rgba(0,242,255,0.4) !important;
    }

    /* Result Card */
    .result-card {
        background: rgba(10, 10, 10, 0.98);
        border: 1px solid rgba(0, 242, 255, 0.3);
        padding: 3rem;
        margin-top: 2rem;
        border-radius: 12px;
        box-shadow: 0 40px 100px rgba(0,0,0,0.9);
    }
</style>
""", unsafe_allow_html=True)

# --- 2. Voice Input ---
v_val = st.query_params.get("v", "")
st.components.v1.html(f"""
<div style="display: flex; align-items: center; justify-content: center; height: 100%;">
    <button id="mic" style="background:transparent; border:none; color:#444; cursor:pointer; font-size:24px;">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3z"></path><path d="M19 10v2a7 7 0 0 1-14 0v-2"></path><line x1="12" y1="19" x2="12" y2="22"></line></svg>
    </button>
</div>
<script>
    const btn = document.getElementById('mic');
    btn.onclick = () => {{
        const rec = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        rec.lang = 'zh-CN';
        btn.style.color = '#00F2FF';
        rec.onresult = (e) => {{
            const t = e.results[0][0].transcript;
            const url = new URL(window.parent.location.href);
            url.searchParams.set('v', t);
            window.parent.location.href = url.href;
        }};
        rec.start();
    }};
</script>
""", height=50)

# --- 3. UI ---
st.markdown("<h1 style='text-align: center;'>小 六 壬</h1>", unsafe_allow_html=True)
N = st.radio("N", options=list(range(1, 10)), horizontal=True, label_visibility="collapsed")

c1, c2 = st.columns([10, 1.5])
with c1:
    q = st.text_input("Q", value=v_val, placeholder="在此感应因果...", label_visibility="collapsed")
with c2:
    divine = st.button("⮕")

if divine:
    if not q: st.toast("请起意。")
    else:
        with st.spinner("正在演算..."): time.sleep(1)
        now = datetime.datetime.now()
        res = ["空亡", "大安", "留连", "速喜", "赤口", "小吉"][(now.hour + N) % 6] # Simpler logic for UI test
        st.markdown(f"""
        <div class="result-card">
            <h2 style="text-align: center; color: #00F2FF;">{res}</h2>
        </div>
        """, unsafe_allow_html=True)
