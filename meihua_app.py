import streamlit as st
import datetime
import time
import random
import os

# --- 1. FORCE THEME & UI (Brute Force) ---
st.set_page_config(page_title="梅花易数", page_icon="🌙", layout="centered")

# This CSS targets everything to ensure NO WHITE appears
st.markdown("""
<style>
    /* Force Dark Global */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #050505 !important;
        color: #d4af37 !important;
    }
    
    /* Target the Main Block */
    .main .block-container {
        background-color: #050505 !important;
        padding-top: 2rem !important;
    }

    /* Kill Streamlit Default Borders and Backgrounds */
    [data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stSidebar"] {
        display: none !important;
    }

    /* Input Bar Styling (Portal Look) */
    div[data-testid="stHorizontalBlock"] {
        background: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(212, 175, 55, 0.2) !important;
        border-radius: 60px !important;
        padding: 8px 20px 8px 30px !important;
        align-items: center !important;
        box-shadow: 0 20px 60px rgba(0,0,0,0.8) !important;
    }

    /* Input Text Internal Clean */
    div[data-testid="stTextInput"] div[data-baseweb="input"],
    div[data-testid="stTextInput"] div[data-baseweb="base-input"],
    div[data-testid="stTextInput"] input {
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        color: #d4af37 !important;
        font-size: 1.2rem !important;
    }
    div[data-testid="stTextInput"] label { display: none !important; }
    input::placeholder { color: #333 !important; }

    /* Custom Confirm Button (The arrow) */
    div[data-testid="stHorizontalBlock"] button {
        background: #d4af37 !important;
        color: #050505 !important;
        border: none !important;
        border-radius: 50% !important;
        width: 45px !important;
        height: 45px !important;
        min-width: 45px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 1.2rem !important;
        cursor: pointer !important;
        box-shadow: 0 0 15px rgba(212,175,55,0.4) !important;
    }
    
    /* Result Card */
    .result-card {
        background: rgba(10, 10, 10, 0.98);
        border: 1px solid rgba(212,175,55,0.3);
        padding: 3rem;
        margin-top: 2rem;
        border-radius: 12px;
        box-shadow: 0 40px 100px rgba(0,0,0,0.9);
    }

    /* Hide redundant elements */
    #MainMenu, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# --- 2. Real Voice Input Bridge ---
# Standard Component - No window.parent hacks to avoid CORS
voice_val = st.query_params.get("v", "")

st.components.v1.html(f"""
<div style="display: flex; align-items: center; justify-content: center; height: 100%;">
    <button id="mic" style="background:transparent; border:none; color:#666; cursor:pointer; font-size:24px;">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3z"></path><path d="M19 10v2a7 7 0 0 1-14 0v-2"></path><line x1="12" y1="19" x2="12" y2="22"></line></svg>
    </button>
</div>
<script>
    const btn = document.getElementById('mic');
    btn.onclick = () => {{
        const rec = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        rec.lang = 'zh-CN';
        btn.style.color = '#d4af37';
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

# --- 3. Main UI ---
st.markdown("<h1 style='text-align: center;'>梅 花 易 数</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #444; font-size: 0.9rem; letter-spacing: 0.3em; margin-bottom: 2.5rem;'>时 空 算 法 · 因 果 溯 源</p>", unsafe_allow_html=True)

# Portal Bar
c1, c2 = st.columns([10, 1.5])
with c1:
    q = st.text_input("Q", value=voice_val, placeholder="在此感应因果...", label_visibility="collapsed")
with c2:
    divine = st.button("⮕")

# --- Logic ---
try:
    from borax.calendars.lunardate import LunarDate
    from meihua_data import BAGUA, GUA_64, BRANCHES, BRANCH_MAP
except:
    st.error("同步星历中...")
    st.stop()

if divine:
    if not q: st.toast("请起意。")
    else:
        with st.spinner("正在推演天机..."): time.sleep(2)
        now = datetime.datetime.now()
        lunar = LunarDate.from_solar_date(now.year, now.month, now.day)
        Y = BRANCH_MAP[lunar.gz_year[1]]
        M, D, H = lunar.month, lunar.day, (1 if now.hour >= 23 or now.hour < 1 else (now.hour + 1) // 2 + 1)
        U, L, Mov = (Y+M+D)%8 or 8, (Y+M+D+H)%8 or 8, (Y+M+D+H)%6 or 6
        
        st.markdown(f"""
        <div class="result-card">
            <p style="text-align: center; color: #333; font-size: 0.8rem;">{now.strftime('%Y-%m-%d %H:%M:%S')} | {lunar.strftime('%Y年%L%M月%D')}</p>
            <div style="display: flex; justify-content: space-around; text-align: center; margin: 2rem 0;">
                <div><p style="color:#555; font-size:0.7rem;">本卦</p><h2 style="color:#d4af37;">{GUA_64[(U,L)]}</h2></div>
                <div><p style="color:#555; font-size:0.7rem;">变卦</p><h2 style="color:#d4af37;">...</h2></div>
            </div>
            <p style="text-align: center; color: #d4af37;">动爻：第 {Mov} 爻动</p>
        </div>
        """, unsafe_allow_html=True)

# Falling Blossoms
st.markdown("""
<div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: -1;">
    <style>
        .petal { position: absolute; background: #ffb7c5; border-radius: 50% 0 50% 0; opacity: 0.15; animation: fall 10s infinite linear; }
        @keyframes fall { to { transform: translate(100px, 100vh) rotate(360deg); } }
    </style>
    <div class="petal" style="width:10px; height:10px; left:10%; top:-10px;"></div>
    <div class="petal" style="width:8px; height:8px; left:40%; top:-10px; animation-delay:2s;"></div>
    <div class="petal" style="width:12px; height:12px; left:75%; top:-10px; animation-delay:1s;"></div>
</div>
""", unsafe_allow_html=True)
