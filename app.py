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
        background-color: #050505;
        color: #e0e0e0;
        font-family: 'Noto Serif SC', 'Microsoft YaHei', serif;
    }
    .stApp {
        background-color: #050505;
    }
    h1, h2, h3 {
        color: #00F2FF;
        letter-spacing: 0.15em;
        text-align: center;
        text-shadow: 0 0 10px rgba(0,242,255,0.3);
    }
    .stButton>button {
        background-color: rgba(0,242,255,0.05);
        color: #00F2FF;
        border: 1px solid #00F2FF;
        border-radius: 0;
        padding: 0.5rem 2.5rem;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        display: block;
        margin: 0 auto;
        text-transform: uppercase;
        letter-spacing: 0.2em;
    }
    .stButton>button:hover {
        color: #fff;
        border-color: #fff;
        background-color: rgba(0,242,255,0.2);
        box-shadow: 0 0 15px rgba(0,242,255,0.4);
    }
    .result-card {
        background: rgba(10, 10, 10, 0.9);
        border: 1px solid rgba(0,242,255,0.2);
        backdrop-filter: blur(12px);
        padding: 2.5rem;
        margin-top: 2rem;
        animation: emerge 1.2s cubic-bezier(0.23, 1, 0.32, 1);
        border-radius: 4px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    .formula {
        font-family: 'Courier New', Courier, monospace;
        color: #555;
        font-size: 0.85rem;
        text-align: center;
        margin-bottom: 1.5rem;
        opacity: 0.7;
    }
    .gua-name {
        font-size: 4rem;
        font-weight: 700;
        color: #00F2FF;
        text-align: center;
        margin: 1.5rem 0;
        text-shadow: 0 0 25px rgba(0,242,255,0.5);
        animation: pulse 3s infinite ease-in-out;
    }
    .gua-desc {
        color: #999;
        line-height: 2.1;
        text-align: center;
        max-width: 550px;
        margin: 0 auto;
        letter-spacing: 0.05em;
    }
    @keyframes emerge {
        from { opacity: 0; transform: scale(0.95) translateY(20px); filter: blur(10px); }
        to { opacity: 1; transform: scale(1) translateY(0); filter: blur(0); }
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; filter: drop-shadow(0 0 10px rgba(0,242,255,0.4)); }
        50% { opacity: 0.8; filter: drop-shadow(0 0 20px rgba(0,242,255,0.6)); }
    }
    /* Hide Streamlit UI elements for immersion */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
"""
st.markdown(cyber_zen_css, unsafe_allow_html=True)

# --- Data & Logic ---

GUA_DATA = {
    1: {"name": "大安", "status": "STATUS: STABLE / 200 OK", "desc": "身不动时，五行属木，求财在东方。大安事事昌，求财在坤方，失物去不远，宅舍保安康。", "interpretation": "此卦为极稳之象。如底层架构之固，如程序运行之顺。当下宜守不宜动，静候其成。"},
    2: {"name": "留连", "status": "STATUS: PENDING / PROCESSING", "desc": "人未归时，五行属水，去者未回程。留连事难成，求谋日未明，官事只宜缓，去者未回程。", "interpretation": "此卦为延宕之象。如同数据传输阻塞，逻辑陷入回旋。凡事不可操之过急，需耐心等待系统响应。"},
    3: {"name": "速喜", "status": "STATUS: INSTANT / PUSH", "desc": "人即至时，五行属火，求财向南行。速喜喜来临，求财向南行，失物午未申，逢人路上寻。", "interpretation": "此卦为速发之象。好比高优先级的推送提醒，灵感瞬间迸发。宜果断出击，把握转瞬即逝的窗口期。"},
    4: {"name": "赤口", "status": "STATUS: CONFLICT / 403 FORBIDDEN", "desc": "官事凶时，五行属金，官非切要防。赤口主口舌，官事且紧防，失物急去寻，行人有惊慌。", "interpretation": "此卦为纷争之象。警惕防火墙被攻破或通信协议冲突。慎言谨行，防范口舌是非与突发之阻碍。"},
    5: {"name": "小吉", "status": "STATUS: OPTIMIZED / SUCCESS", "desc": "人来喜时，五行属木，阴人来报喜。小吉最吉昌，路上好商量，阴人来报喜，失物在坤方。", "interpretation": "此卦为和合之象。如代码经过完美重构，系统资源调配得当。虽非大成，但胜在圆满顺遂，有贵人相助。"},
    0: {"name": "空亡", "status": "STATUS: VOID / 404 NOT FOUND", "desc": "音信稀时，五行属土，求财无利益。空亡事不祥，阴人多乖张，求财无利益，行人有灾殃。", "interpretation": "此卦为虚无之象。链接已断开，数据已溢出。此时不宜寄托希望，宜彻底清空缓存，择日重新加载。"}
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
        st.markdown(f'<div style="text-align: center; color: #00F2FF; font-size: 0.8rem; margin-bottom: 1rem; font-family: monospace;">{gua["status"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="gua-desc"><b>诗诀</b>：{gua["desc"]}<br><br><b>解读</b>：{gua["interpretation"]}</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br><br><br>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #333; font-size: 0.7rem;'>以此入定，静待笔墨</p>", unsafe_allow_html=True)
