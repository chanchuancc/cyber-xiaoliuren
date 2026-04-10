import streamlit as st
from borax.calendars.lunardate import LunarDate
import datetime
import time
import json
import os
from streamlit_mic_recorder import speech_to_text

# --- v2.1.0 Imperial Blackout: Nuclear Darkness & Real Voice ---
st.set_page_config(page_title="小六壬", page_icon="⛩️", layout="centered")

# --- Brute Force CSS: KILL ALL WHITE ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@300;400;700&display=swap');

    /* Global Blackout */
    html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"], .main {
        background-color: #050505 !important;
        background: #050505 !important;
        color: #00F2FF !important;
        font-family: 'Noto Serif SC', 'Microsoft YaHei', serif !important;
    }

    /* Hide redundant elements */
    div[data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stStatusWidget"], header, footer {
        display: none !important;
        visibility: hidden !important;
    }

    /* Aggressive Transparency for Inputs */
    div[data-testid="stTextInput"] fieldset,
    div[data-testid="stTextInput"] div,
    div[data-testid="stTextInput"] input,
    div[data-baseweb="input"],
    div[role="presentation"] {
        background-color: transparent !important;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        color: #00F2FF !important;
    }

    h1 {
        color: #00F2FF !important;
        letter-spacing: 0.8em !important;
        text-align: center !important;
        text-shadow: 0 0 30px rgba(0,242,255,0.5) !important;
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

    /* Custom Mic Component Styling */
    div.st-emotion-cache-1pxm8lv { background: transparent !important; border: none !important; }
    button[kind="secondary"] { 
        background: transparent !important; 
        border: none !important; 
        color: #00F2FF !important; 
        font-size: 1.5rem !important;
    }

    /* Vector Arrow Button Injection */
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
        content: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="%2300F2FF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>');
        position: absolute;
        top: 50%; left: 50%; transform: translate(-50%, -50%);
        transition: all 0.2s ease;
    }
    div[data-testid="stButton"] > button:hover::after {
        transform: translate(-50%, -50%) scale(1.2);
        filter: drop-shadow(0 0 10px #00F2FF);
    }

    /* Result Card */
    .result-card {
        background: rgba(10, 10, 10, 0.99) !important;
        border: 1px solid rgba(0,242,255,0.2) !important;
        padding: 3.5rem !important;
        border-radius: 12px !important;
        box-shadow: 0 40px 100px rgba(0,0,0,1) !important;
        margin-top: 2rem !important;
        animation: em 1.5s cubic-bezier(0.23, 1, 0.32, 1);
    }
    @keyframes em { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }

    /* Number Selection Matrix Styling */
    div[data-testid="stRadio"] > div { flex-direction: row !important; justify-content: center !important; gap: 15px !important; }
    div[data-testid="stRadio"] label { 
        background: rgba(0,242,255,0.02) !important; 
        border: 1px solid rgba(0,242,255,0.1) !important;
        padding: 8px 18px !important; color: #444 !important; transition: 0.3s;
    }
    div[data-testid="stRadio"] label:has(input:checked) { 
        border-color: #00F2FF !important; color: #00F2FF !important; 
        background: rgba(0,242,255,0.1) !important; 
        box-shadow: 0 0 15px rgba(0,242,255,0.3) !important;
    }
    div[data-testid="stRadio"] label[data-baseweb="radio"] > div:first-child { display: none !important; }
</style>
""", unsafe_allow_html=True)

# --- Persistence ---
STORAGE_FILE = "divinations.json"
@st.cache_resource
def get_ip_cache():
    if os.path.exists(STORAGE_FILE):
        try:
            with open(STORAGE_FILE, "r") as f: return json.load(f)
        except: return {}
    return {}
ip_cache = get_ip_cache()

# --- Voice State ---
if "v_text" not in st.session_state:
    st.session_state.v_text = ""

# --- UI Layout ---
st.markdown("<h1>小 六 壬</h1>", unsafe_allow_html=True)
st.markdown('<div class="ritual-hint">屏息凝神 · 默念所求</div>', unsafe_allow_html=True)

# Portal Row
col_in, col_mic, col_go = st.columns([8, 1.5, 1.2])
with col_mic:
    voice_result = speech_to_text(language='zh-CN', start_prompt="🎙️", stop_prompt="⏹️", key='mic_recorder')
    if voice_result: st.session_state.v_text = voice_result
with col_in:
    question = st.text_input("Q", value=st.session_state.v_text, placeholder="在此感应因果...", label_visibility="collapsed")
with col_go:
    divine_trigger = st.button(" ")

#灵数
st.markdown('<div style="text-align: center; color: #333; font-size: 0.9rem; margin-top: 1.5rem; letter-spacing: 0.2em;">择一灵数：</div>', unsafe_allow_html=True)
N = st.radio("N", options=list(range(1, 10)), index=4, horizontal=True, label_visibility="collapsed")

if divine_trigger and question:
    st.session_state.v_text = ""
    anim = st.empty()
    for s in ["捕捉时空涟漪...", "定位星历数据...", "注入灵数演算...", "解析神谕二进制码..."]:
        anim.markdown(f'<div style="text-align:center; color:#00F2FF; font-family:monospace; font-size:1.1rem; margin:2rem 0;">{s}</div>', unsafe_allow_html=True)
        time.sleep(0.8)
    anim.empty()
    
    now = datetime.datetime.now(); l = LunarDate.from_solar_date(now.year, now.month, now.day)
    M, D, H = l.month, l.day, (1 if now.hour >= 23 or now.hour < 1 else (now.hour + 1) // 2 + 1)
    res_idx = (M + D + H + N - 3) % 6
    
    GUA = {1:{"n":"大安","s":"STABLE","p":"大安事事昌，求财在坤方。失物去不远，宅舍保安康。","d":"身不动时，五行属木。极稳之象。"},
           2:{"n":"留连","s":"PENDING","p":"留连事难成，求谋日未明。官事只宜缓，去者未回程。","d":"人未归时，五行属水。延宕之象。"},
           3:{"n":"速喜","s":"INSTANT","p":"速喜喜来临，求财向南行。失物午未申，逢人路上寻。","d":"人即至时，五行属火。速发之象。"},
           4:{"n":"赤口","s":"CONFLICT","p":"赤口主口舌，官非切要防。失物急去寻，行人有惊慌.","d":"官事凶时，五行属金。纷争之象。"},
           5:{"n":"小吉","s":"SUCCESS","p":"小吉最吉昌，路上好商量。阴人来报喜，失物在坤方。","d":"人来喜时，五行属木。和合之象。"},
           0:{"n":"空亡","s":"VOID","p":"空亡事不祥，阴人多乖张。求财无利益，行人有灾殃。","d":"音信稀时，五行属土。虚无之象。"}}
    r = GUA[res_idx]

    st.markdown(f"""
    <div class="result-card">
        <div style="text-align:center; color:#222; font-family:monospace; font-size:0.8rem; border-bottom:1px solid #111; padding-bottom:1.5rem; margin-bottom:2.5rem;">ALGO: ({M}+{D}+{H}+{N}-3)%6={res_idx}</div>
        <div style="font-size:6rem; font-weight:700; color:#00F2FF; text-align:center; text-shadow:0 0 40px rgba(0,242,255,0.6); letter-spacing:0.2em;">{r['n']}</div>
        <div style="text-align:center; color:#00F2FF; font-family:monospace; letter-spacing:0.3em; margin-bottom:3rem; opacity:0.7;">{r['s']}</div>
        <div style="border-left:4px solid #00F2FF; padding-left:2rem; margin-bottom:3rem;"><div style="color:#444; font-size:0.8rem;">[ 问 卜 ]</div><div style="font-size:1.4rem; color:#fff;">{question}</div></div>
        <div style="color:#ccc; font-size:1.5rem; line-height:1.8; margin-bottom:2.5rem;">{r['p']}</div>
        <div style="color:#999; font-size:1.1rem; line-height:2.0;">{r['d']}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br><br><p style='text-align:center; color:#151515; font-size:0.7rem; letter-spacing:0.5em;'>ALGORITHM IS FATE · CODE IS TRUTH</p>", unsafe_allow_html=True)
