import streamlit as st
import datetime
import time
import random
import os

# --- Brute Force UI Cleanup ---
st.set_page_config(page_title="梅花易数", page_icon="🧧", layout="centered")

st.markdown("""
<style>
    .stApp { background: #050505 !important; }
    
    /* KILL ALL WHITE AND GREY */
    div[data-testid="stTextInput"] div[data-baseweb="input"],
    div[data-testid="stTextInput"] div[data-baseweb="base-input"],
    div[data-testid="stTextInput"] > div > div,
    input, .st-ae, .st-af, .st-ag, .st-ah, .st-ai, .st-aj, .st-ak {
        background-color: transparent !important;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        color: #d4af37 !important;
    }
    
    /* Portal Style Wrapper */
    [data-testid="stHorizontalBlock"] {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(212, 175, 55, 0.2) !important;
        border-radius: 50px !important;
        padding: 5px 20px !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5) !important;
    }

    button { background: transparent !important; border: none !important; color: #d4af37 !important; }
    #MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# --- Real Voice Input Hack (JS Bridge) ---
# This uses Web Speech API. It will show an alert and set a query param.
# The user needs to grant mic access in the browser.
st.components.v1.html("""
<script>
    function startRecognition() {
        const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        recognition.lang = 'zh-CN';
        recognition.onresult = (event) => {
            const text = event.results[0][0].transcript;
            const url = new URL(window.parent.location);
            url.searchParams.set('voice_input', text);
            window.parent.location.href = url.href;
        };
        recognition.start();
    }
    window.parent.document.addEventListener('keydown', (e) => {
        // Optional hotkey
    });
</script>
<button onclick="startRecognition()" style="background:transparent; border:none; color:#666; cursor:pointer; font-size:24px;">🎙️</button>
""", height=40)

# Get voice input from URL
voice_text = st.query_params.get("voice_input", "")

try:
    from borax.calendars.lunardate import LunarDate
    from meihua_data import BAGUA, GUA_64, BRANCHES, BRANCH_MAP
except:
    st.error("环境加载中... 请确保 requirements.txt 已安装。")
    st.stop()

# --- Algorithm ---
def get_sh_idx(h): return 1 if h >= 23 or h < 1 else (h + 1) // 2 + 1
def solve(u, l, m):
    o_name = GUA_64[(u, l)]
    o_l = BAGUA[l]["lines"] + BAGUA[u]["lines"]
    mut_l = get_gua_from_lines([o_l[1], o_l[2], o_l[3]])
    mut_u = get_gua_from_lines([o_l[2], o_l[3], o_l[4]])
    t_l = list(o_l); t_l[m-1] = 1 - t_l[m-1]
    return {"o": o_name, "m": GUA_64[(mut_u, mut_l)], "t": GUA_64[(get_gua_from_lines(t_l[3:6]), get_gua_from_lines(t_l[0:3]))]}
def get_gua_from_lines(lines):
    for k, v in BAGUA.items():
        if v["lines"] == lines: return k
    return 1

# --- UI ---
st.markdown("<h1 style='text-align: center; color: #d4af37;'>梅 花 易 数</h1>", unsafe_allow_html=True)

col1, col2 = st.columns([9, 1])
with col1:
    # Use voice_text as default if available
    question = st.text_input("Question", value=voice_text, placeholder="在此感应因果...", label_visibility="collapsed")
with col2:
    divine_trigger = st.button("⮕")

if divine_trigger:
    if not question: st.toast("请起意。")
    else:
        with st.spinner("正在推演..."): time.sleep(2) # Faster for demo
        now = datetime.datetime.now()
        lunar = LunarDate.from_solar_date(now.year, now.month, now.day)
        Y = BRANCH_MAP[lunar.gz_year[1]]
        M, D, H = lunar.month, lunar.day, get_sh_idx(now.hour)
        Upper, Lower, Mov = (Y+M+D)%8 or 8, (Y+M+D+H)%8 or 8, (Y+M+D+H)%6 or 6
        res = solve(Upper, Lower, Mov)
        st.success(f"本卦：{res['o']} | 互卦：{res['m']} | 变卦：{res['t']}")
