import streamlit as st
import datetime
import time
import random
import os

# --- Configuration & Styling (v1.9.0 "Imperial Void") ---
st.set_page_config(page_title="梅花易数", page_icon="🌙", layout="centered")

# Brute Force UI Override
plum_void_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@300;400;700&display=swap');

    /* Global Blackout */
    .stApp {
        background: #050505 !important;
    }
    .block-container {
        padding-top: 2rem !important;
        max-width: 800px !important;
    }

    h1 {
        color: #d4af37 !important;
        letter-spacing: 0.6em;
        text-align: center;
        text-shadow: 0 0 30px rgba(212,175,55,0.5);
        font-weight: 700;
        font-size: 3.5rem;
        margin-bottom: 0.5rem;
    }
    .sub-title {
        color: #444 !important;
        text-align: center;
        font-size: 0.9rem;
        letter-spacing: 0.4em;
        margin-bottom: 4rem;
    }

    /* --- THE PORTAL BAR (Integrated) --- */
    /* Target the horizontal column container */
    [data-testid="stHorizontalBlock"] {
        background: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(212, 175, 55, 0.15) !important;
        border-radius: 60px !important;
        padding: 5px 10px 5px 35px !important;
        display: flex !important;
        align-items: center !important;
        gap: 0 !important; /* Remove gap between columns */
        box-shadow: 0 20px 60px rgba(0,0,0,0.8), inset 0 0 20px rgba(212,175,55,0.05) !important;
        transition: all 0.4s ease;
    }
    [data-testid="stHorizontalBlock"]:focus-within {
        border-color: #d4af37 !important;
        background: rgba(255, 255, 255, 0.04) !important;
        box-shadow: 0 0 30px rgba(212,175,55,0.2) !important;
    }

    /* Target the input inside the bar */
    [data-testid="stTextInput"] {
        width: 100% !important;
    }
    [data-testid="stTextInput"] div[data-baseweb="input"],
    [data-testid="stTextInput"] div[data-baseweb="base-input"],
    [data-testid="stTextInput"] input {
        background: transparent !important;
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        color: #d4af37 !important;
        font-size: 1.25rem !important;
        padding: 0 !important;
    }
    [data-testid="stTextInput"] label { display: none !important; }
    input::placeholder { color: #333 !important; }

    /* The Confirm Button (Circular Arrow) */
    div[data-testid="stHorizontalBlock"] button {
        background: #d4af37 !important;
        color: #050505 !important;
        border: none !important;
        border-radius: 50% !important;
        width: 48px !important;
        height: 48px !important;
        min-width: 48px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        margin-left: 15px !important;
        box-shadow: 0 0 20px rgba(212,175,55,0.4) !important;
        transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        font-weight: bold !important;
        cursor: pointer !important;
    }
    div[data-testid="stHorizontalBlock"] button:hover {
        transform: scale(1.15);
        background: #fff !important;
        box-shadow: 0 0 30px rgba(255,255,255,0.6) !important;
    }
    
    /* Result Card */
    .result-card {
        background: rgba(10, 10, 10, 0.98);
        border: 1px solid rgba(212,175,55,0.3);
        padding: 4rem;
        margin-top: 2rem;
        border-radius: 12px;
        box-shadow: 0 40px 100px rgba(0,0,0,0.9);
        animation: emerge 1.5s ease-out;
    }
    @keyframes emerge { from { opacity: 0; transform: translateY(40px); } to { opacity: 1; transform: translateY(0); } }

    /* Hide redundant elements */
    #MainMenu, footer, header { visibility: hidden; }
</style>
"""
st.markdown(plum_void_css, unsafe_allow_html=True)

# --- Voice Capability (Real JS Bridge) ---
# Embed a hidden voice listener that interacts with the parent URL
st.components.v1.html("""
<script>
    const micBtn = window.parent.document.createElement('div');
    micBtn.innerHTML = `
        <button id="real-mic" style="background:transparent; border:none; color:#555; cursor:pointer; font-size:24px; padding:10px; transition:color 0.3s;">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3z"></path><path d="M19 10v2a7 7 0 0 1-14 0v-2"></path><line x1="12" y1="19" x2="12" y2="22"></line></svg>
        </button>
    `;
    
    // Inject into the Streamlit bar once it loads
    const checkExist = setInterval(function() {
       const bar = window.parent.document.querySelector('[data-testid="stHorizontalBlock"]');
       if (bar && !window.parent.document.getElementById('real-mic')) {
          const micContainer = bar.children[1]; // Second column
          micContainer.innerHTML = ''; 
          micContainer.appendChild(micBtn);
          
          window.parent.document.getElementById('real-mic').onclick = function() {
              const rec = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
              rec.lang = 'zh-CN';
              this.style.color = '#d4af37';
              rec.onresult = (e) => {
                  const t = e.results[0][0].transcript;
                  const u = new URL(window.parent.location);
                  u.searchParams.set('v_in', t);
                  window.parent.location.href = u.href;
              };
              rec.start();
          };
          clearInterval(checkExist);
       }
    }, 100);
</script>
""", height=0)

v_in = st.query_params.get("v_in", "")

# --- Logic & Data ---
try:
    from borax.calendars.lunardate import LunarDate
    from meihua_data import BAGUA, GUA_64, BRANCHES, BRANCH_MAP
except:
    st.error("正在同步星历数据...")
    st.stop()

def get_sh_idx(h): return 1 if h >= 23 or h < 1 else (h + 1) // 2 + 1
def solve(u, l, m):
    o_name = GUA_64[(u, l)]
    o_l = BAGUA[l]["lines"] + BAGUA[u]["lines"]
    def get_g(lines):
        for k, v in BAGUA.items():
            if v["lines"] == lines: return k
        return 1
    mut_l = get_g([o_l[1], o_l[2], o_l[3]])
    mut_u = get_g([o_l[2], o_l[3], o_l[4]])
    t_l = list(o_l); t_l[m-1] = 1 - t_l[m-1]
    return {"o": o_name, "m": GUA_64[(mut_u, mut_l)], "t": GUA_64[(get_g(t_l[3:6]), get_g(t_l[0:3]))]}

# --- UI Layout ---
st.markdown("<h1>梅 花 易 数</h1>", unsafe_allow_html=True)
st.markdown('<p class="sub-title">时 空 算 法 · 灵 性 触 达</p>', unsafe_allow_html=True)

st.markdown('<p style="text-align: center; color: #666; font-size: 1.1rem; margin-bottom: 1rem;">屏息凝神，默念所求</p>', unsafe_allow_html=True)

# The Portal Bar Columns
# Col 1: Input, Col 2: Voice (Placeholder for JS injection), Col 3: Confirm
c1, c2, c3 = st.columns([10, 1.2, 1.5])
with c1:
    question = st.text_input("Divine Question", value=v_in, placeholder="在此感应因果...", label_visibility="collapsed")
with c2:
    st.empty() # Target for JS injection
with c3:
    divine_trigger = st.button("⮕")

if divine_trigger:
    if not question:
        st.toast("请起意并输入。", icon="🌙")
    else:
        # Fast Reveal Animation
        progress_bar = st.progress(0)
        for i in range(100):
            time.sleep(0.03)
            progress_bar.progress(i + 1)
        progress_bar.empty()
        
        now = datetime.datetime.now()
        lunar = LunarDate.from_solar_date(now.year, now.month, now.day)
        Y = BRANCH_MAP[lunar.gz_year[1]]
        M, D, H = lunar.month, lunar.day, get_sh_idx(now.hour)
        U, L, Mov = (Y+M+D)%8 or 8, (Y+M+D+H)%8 or 8, (Y+M+D+H)%6 or 6
        res = solve(U, L, Mov)
        
        st.markdown(f"""
        <div class="result-card">
            <p style="text-align: center; color: #333; font-size: 0.8rem; margin-bottom: 2rem;">{now.strftime('%Y-%m-%d %H:%M:%S')} | {lunar.strftime('%Y年%L%M月%D')} {BRANCHES[H-1]}时</p>
            <div style="display: flex; justify-content: space-around; text-align: center; margin-bottom: 3rem;">
                <div><p style="color:#555; font-size:0.75rem; letter-spacing:0.2em;">本卦</p><h2 style="color:#d4af37; font-size:3rem;">{res['o']}</h2></div>
                <div><p style="color:#555; font-size:0.75rem; letter-spacing:0.2em;">互卦</p><h2 style="color:#d4af37; font-size:3rem;">{res['m']}</h2></div>
                <div><p style="color:#555; font-size:0.75rem; letter-spacing:0.2em;">变卦</p><h2 style="color:#d4af37; font-size:3rem;">{res['t']}</h2></div>
            </div>
            <p style="text-align: center; color: #d4af37; font-size: 1.2rem; border-top: 1px solid #1a1a1a; padding-top: 2rem;">动爻：第 {Mov} 爻动</p>
        </div>
        """, unsafe_allow_html=True)

# Falling Plum Blossoms (CSS only)
st.markdown("""
<div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: -1; overflow: hidden;">
    <style>
        .petal { position: absolute; background: #ffb7c5; border-radius: 50% 0 50% 0; opacity: 0.15; animation: fall linear infinite; }
        @keyframes fall { to { transform: translate(100px, 100vh) rotate(360deg); } }
    </style>
    <div class="petal" style="width:10px; height:10px; left:10%; top:-10px; animation-duration:10s;"></div>
    <div class="petal" style="width:8px; height:8px; left:30%; top:-10px; animation-duration:12s; animation-delay:2s;"></div>
    <div class="petal" style="width:12px; height:12px; left:60%; top:-10px; animation-duration:9s; animation-delay:1s;"></div>
    <div class="petal" style="width:10px; height:10px; left:85%; top:-10px; animation-duration:11s; animation-delay:4s;"></div>
</div>
""", unsafe_allow_html=True)
