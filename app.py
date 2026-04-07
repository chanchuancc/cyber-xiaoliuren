import streamlit as st
from borax.calendars.lunardate import LunarDate
import datetime
import time

# --- Configuration & Styling (Cyber Zen) ---
st.set_page_config(page_title="小六壬 · 寂", page_icon="⛩️", layout="centered")

cyber_zen_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@300;400;700&display=swap');

    body {
        background-color: #0d0d0d;
        color: #e0e0e0;
        font-family: 'Noto Serif SC', 'Microsoft YaHei', serif;
    }
    .stApp {
        background-color: #0d0d0d;
    }
    h1, h2, h3 {
        color: #b0b0b0;
        letter-spacing: 0.1em;
        text-align: center;
    }
    .stButton>button {
        background-color: transparent;
        color: #888;
        border: 1px solid #444;
        border-radius: 0;
        padding: 0.5rem 2rem;
        transition: all 0.3s ease;
        display: block;
        margin: 0 auto;
    }
    .stButton>button:hover {
        color: #fff;
        border-color: #888;
        box-shadow: 0 0 10px rgba(255,255,255,0.1);
    }
    .result-card {
        background: rgba(20, 20, 20, 0.8);
        border-left: 2px solid #555;
        padding: 2rem;
        margin-top: 2rem;
        animation: fadeIn 1s ease-in-out;
    }
    .formula {
        font-family: monospace;
        color: #666;
        font-size: 0.9rem;
        text-align: center;
        margin-bottom: 1rem;
    }
    .gua-name {
        font-size: 3rem;
        font-weight: 700;
        color: #fff;
        text-align: center;
        margin: 1rem 0;
        text-shadow: 0 0 20px rgba(255,255,255,0.2);
    }
    .gua-desc {
        color: #aaa;
        line-height: 1.8;
        text-align: center;
        max-width: 500px;
        margin: 0 auto;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    /* Hide Streamlit UI elements for immersion */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
"""
st.markdown(cyber_zen_css, unsafe_allow_html=True)

# --- Data & Logic ---

GUA_DATA = {
    1: {"name": "大安", "desc": "身不动时，五行属木，颜色青色，方位东方。大安事事昌，求财在坤方，失物去不远，宅舍保安康。"},
    2: {"name": "留连", "desc": "卒未归时，五行属水，颜色黑色，方位北方。留连事难成，求谋日未明，官事只宜缓，去者未回程。"},
    3: {"name": "速喜", "desc": "人即至时，五行属火，颜色红色，方位南方。速喜喜来临，求财向南行，失物午未申，逢人路上寻。"},
    4: {"name": "赤口", "desc": "官事凶时，五行属金，颜色白色，方位西方。赤口主口舌，官事且紧防，失物急去寻，行人有惊慌。"},
    5: {"name": "小吉", "desc": "人来喜时，五行属木，颜色青色，方位东方。小吉最吉昌，路上好商量，阴人来报喜，失物在坤方。"},
    0: {"name": "空亡", "desc": "音信稀时，五行属土，颜色黄色，方位中央。空亡事不祥，阴人多乖张，求财无利益，行人有灾殃。"}
}

def get_shichen_index(hour):
    """Map 24h to 12 Shichen index (1-12)"""
    if hour >= 23 or hour < 1:
        return 1  # 子
    return (hour + 1) // 2 + 1

def calculate_xiaoliuren(m, d, h):
    """Core formula: (M + D + H - 2) % 6"""
    return (m + d + h - 2) % 6

# --- UI Layout ---

st.markdown("### 「 寂 · JÌ 」")
st.markdown("## 赛博禅龛 · 小六壬占卜")

if st.button("起 卦"):
    with st.spinner("正在感应天机..."):
        time.sleep(1.2)  # Simulate ceremony
        
        now = datetime.datetime.now()
        lunar = LunarDate.from_solar_date(now.year, now.month, now.day)
        
        M = lunar.month
        D = lunar.day
        H = get_shichen_index(now.hour)
        
        # Adjust for leap month if necessary (borax handles this via lunar.month)
        # However, traditional Xiao Liu Ren often uses the nominal month number.
        
        res_idx = calculate_xiaoliuren(M, D, H)
        gua = GUA_DATA[res_idx]
        
        shichen_names = ["", "子时", "丑时", "寅时", "卯时", "辰时", "巳时", "午时", "未时", "申时", "酉时", "戌时", "亥时"]
        
        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="formula">
            公历：{now.strftime('%Y-%m-%d %H:%M:%S')}<br>
            农历：{lunar.strftime('%Y年%L%M月%D')} {shichen_names[H]}<br>
            演算：({M} + {D} + {H} - 2) % 6 = {res_idx}
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f'<div class="gua-name">{gua["name"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="gua-desc">{gua["desc"]}</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br><br><br>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #333; font-size: 0.7rem;'>以此入定，静待笔墨</p>", unsafe_allow_html=True)
