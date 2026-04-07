import streamlit as st
from borax.calendars.lunardate import LunarDate
import datetime
import time
import random

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
    .stButton {
        display: flex;
        justify-content: center;
    }
    .stButton>button {
        background-color: rgba(0,242,255,0.05);
        color: #00F2FF;
        border: 1px solid #00F2FF;
        border-radius: 0;
        padding: 0.8rem 3rem;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        text-transform: uppercase;
        letter-spacing: 0.3em;
        font-size: 1.1rem;
    }
    .stButton>button:hover {
        color: #fff;
        border-color: #fff;
        background-color: rgba(0,242,255,0.2);
        box-shadow: 0 0 20px rgba(0,242,255,0.5);
    }
    .result-card {
        background: rgba(10, 10, 10, 0.95);
        border: 1px solid rgba(0,242,255,0.2);
        backdrop-filter: blur(15px);
        padding: 3rem;
        margin-top: 2rem;
        animation: emerge 1.5s cubic-bezier(0.23, 1, 0.32, 1);
        border-radius: 8px;
        box-shadow: 0 15px 40px rgba(0,0,0,0.7);
    }
    .formula {
        font-family: 'Courier New', Courier, monospace;
        color: #00F2FF;
        font-size: 0.9rem;
        text-align: center;
        margin-bottom: 2rem;
        opacity: 0.6;
    }
    .gua-name {
        font-size: 5rem;
        font-weight: 700;
        color: #00F2FF;
        text-align: center;
        margin: 1.5rem 0;
        text-shadow: 0 0 30px rgba(0,242,255,0.6);
        animation: pulse 4s infinite ease-in-out;
    }
    .gua-desc-box {
        border-top: 1px solid rgba(255,255,255,0.1);
        padding-top: 2rem;
        margin-top: 2rem;
    }
    .gua-desc {
        color: #ccc;
        line-height: 2.2;
        text-align: left;
        max-width: 600px;
        margin: 0 auto;
        letter-spacing: 0.08em;
    }
    .notice {
        text-align: center;
        color: #444;
        font-size: 0.85rem;
        margin-bottom: 2.5rem;
        letter-spacing: 0.1em;
        line-height: 1.6;
    }
    @keyframes emerge {
        from { opacity: 0; transform: scale(0.9) translateY(40px); filter: blur(15px); }
        to { opacity: 1; transform: scale(1) translateY(0); filter: blur(0); }
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; filter: drop-shadow(0 0 15px rgba(0,242,255,0.5)); }
        50% { opacity: 0.7; filter: drop-shadow(0 0 30px rgba(0,242,255,0.7)); }
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
<script>
    // Force center button fix if CSS fails
    window.addEventListener('load', function() {
        const buttons = document.querySelectorAll('.stButton button');
        buttons.forEach(btn => {
            btn.parentElement.style.justifyContent = 'center';
        });
    });
</script>
"""
st.markdown(cyber_zen_css, unsafe_allow_html=True)

# --- Global IP Cache ---
@st.cache_resource
def get_ip_cache():
    return {}

ip_cache = get_ip_cache()

# --- Data & Logic ---

GUA_DATA = {
    1: {
        "name": "大安",
        "status": "STATUS: STABLE / 200 OK",
        "poem": "大安事事昌，求财在东方。失物去不远，宅舍保安康。行人身未动，病者无妨碍。求谋甚周全，官事总成双。",
        "interpretation": "身不动时，五行属木，方位东方。此卦主【极稳】，当下万事顺遂。如同底层架构经过严密压力测试，运行如丝般顺滑。此时宜守正不阿，静观其变，不必急于重构。求财利东方，谋事皆可成。",
        "advice": "【建议】：保持现状，无需激进干预。系统处于最优负载状态。"
    },
    2: {
        "name": "留连",
        "status": "STATUS: PENDING / PROCESSING",
        "poem": "留连事难成，求谋日未明。官事只宜缓，去者未回程。失物南方见，急讨方称心。更需防口舌，人事且宽心。",
        "interpretation": "人未归时，五行属水，方位北方。此卦主【延滞】，如异步任务进入死循环，或带宽遭遇瓶颈。事多纠缠，难觅定论。当下不宜强推更新，需耐心排查逻辑漏洞，等待数据包完整回传。此时宜缓不宜急。",
        "advice": "【建议】：增加超时等待（Timeout），反复校验输入参数。耐心是唯一的解药。"
    },
    3: {
        "name": "速喜",
        "status": "STATUS: INSTANT / PUSH",
        "poem": "速喜喜来临，求财向南行。失物午未申，逢人路上寻。官事有贵人，病者要放心。田宅多吉庆，行人有回音。",
        "interpretation": "人即至时，五行属火，方位南方。此卦主【迅捷】，如同高优先级（High Priority）的通知瞬间推送。灵感爆发，机会稍纵即逝。当下宜果断执行，代码一把过，Bug 自动消除。此时不宜犹豫，宜全速上线。",
        "advice": "【建议】：立即 Commit！当前的直觉是最高等级的生产力。"
    },
    4: {
        "name": "赤口",
        "status": "STATUS: CONFLICT / 403 FORBIDDEN",
        "poem": "赤口主口舌，官事且紧防。失物急去寻，行人有惊慌。鸡犬多作怪，病者要预防。更须防咒诅，慎重保平安。",
        "interpretation": "官事凶时，五行属金，方位西方。此卦主【纷争】，如遇到严重的协议冲突或防火墙拦截。警惕代码中的逻辑炸弹或外部攻击。此时慎言慎行，防范口舌是非，如遇到 PR 冲突，请务必保持心态平和。",
        "advice": "【建议】：开启全量日志审计。加强安全防护，暂时进入沙盒模式。"
    },
    5: {
        "name": "小吉",
        "status": "STATUS: OPTIMIZED / SUCCESS",
        "poem": "小吉最吉昌，路上好商量。阴人来报喜，失物在坤方。行人立刻至，交情甚相宜。求谋皆得利，病者渐安痊。",
        "interpretation": "人来喜时，五行属木，方位东方。此卦主【圆满】，如代码经过精妙重构，资源占用率降至最低。虽非泼天富贵，但胜在和合平衡。有贵人（第三方优质库）相助，系统鲁棒性极佳。事有转机，结果可期。",
        "advice": "【建议】：可以小步快跑，逐步扩大流量。这是一种可持续的成功状态。"
    },
    0: {
        "name": "空亡",
        "status": "STATUS: VOID / 404 NOT FOUND",
        "poem": "空亡事不祥，阴人多乖张。求财无利益，行人有灾殃。失物寻不见，官事有刑伤。病者重难起，谋望尽落空。",
        "interpretation": "音信稀时，五行属土，方位中央。此卦主【虚无】，连接已彻底断开，内存已完全溢出。当下不仅事难成，更需防范系统性风险。此时应彻底清空缓存，择日重新初始化，强求无益，不如入定静待。",
        "advice": "【建议】：立即杀掉进程。清空心念，重新加载人生内核。"
    }
}

def get_shichen_index(hour):
    if hour >= 23 or hour < 1:
        return 1
    return (hour + 1) // 2 + 1

def calculate_xiaoliuren(m, d, h):
    return (m + d + h - 2) % 6

# --- Helper for IP ---
def get_remote_ip():
    try:
        from streamlit.web.server.websocket_headers import _get_websocket_headers
        headers = _get_websocket_headers()
        if headers:
            return headers.get("X-Forwarded-For", "local").split(",")[0]
    except:
        pass
    return "unknown"

# --- UI Layout ---

st.markdown("### 「 寂 · JÌ 」")
st.markdown("## 赛博禅龛 · 小六壬占卜")

st.markdown('<div class="notice">“起卦前请入定三秒，默念所求之事。<br>心诚则灵，妄求无益。”</div>', unsafe_allow_html=True)

# IP Rate Limit Check
client_ip = get_remote_ip()
last_time = ip_cache.get(client_ip)
can_divine = True
wait_msg = ""

if last_time:
    elapsed = time.time() - last_time
    if elapsed < 3600:
        can_divine = False
        remaining = int(3600 - elapsed)
        wait_msg = f"「机缘未到」：天机一小时一泄，请在 {remaining // 60} 分钟后再来。"

if st.button("起 卦"):
    if not can_divine:
        st.toast(wait_msg, icon="⏳")
        st.error(wait_msg)
    else:
        ip_cache[client_ip] = time.time()
        
        # --- Animation ---
        placeholder = st.empty()
        anim_steps = [
            ">>> [SYSTEM] 正在捕捉当前天机...",
            ">>> [SYSTEM] 定位农历月令周期...",
            ">>> [SYSTEM] 锁定日辰能量场...",
            ">>> [SYSTEM] 映射十二时辰相位...",
            ">>> [KERNEL] 执行 O(1) 命运演算...",
            ">>> [DECRYPT] 正在解密神谕数据包...",
            ">>> [RESULT] 命运坍缩中..."
        ]
        
        for i, step in enumerate(anim_steps):
            for _ in range(3): # Sub-steps for flicker
                with placeholder.container():
                    st.markdown(f'<div style="text-align: center; color: #00F2FF; font-family: monospace; font-size: 0.85rem; margin: 2rem 0; text-shadow: 0 0 5px rgba(0,242,255,0.5);">{step}</div>', unsafe_allow_html=True)
                    # Glitch-style matrix
                    matrix_len = 48
                    matrix = "".join([random.choice("0123456789ABCDEF!@#$%^&*()_+<>?:{}|") for _ in range(matrix_len)])
                    st.markdown(f'<div style="text-align: center; color: #111; font-family: monospace; font-size: 0.65rem; overflow: hidden; white-space: nowrap; letter-spacing: 2px;">{matrix}</div>', unsafe_allow_html=True)
                    time.sleep(0.15)
        
        placeholder.empty()
        
        # --- Real Calculation ---
        now = datetime.datetime.now()
        lunar = LunarDate.from_solar_date(now.year, now.month, now.day)
        M, D = lunar.month, lunar.day
        H = get_shichen_index(now.hour)
        
        res_idx = calculate_xiaoliuren(M, D, H)
        gua = GUA_DATA[res_idx]
        shichen_names = ["", "子时", "丑时", "寅时", "卯时", "辰时", "巳时", "午时", "未时", "申时", "酉时", "戌时", "亥时"]
        
        # --- Display Result ---
        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="formula">
            公历：{now.strftime('%Y-%m-%d %H:%M:%S')}<br>
            农历：{lunar.strftime('%Y年%L%M月%D')} {shichen_names[H]}<br>
            演算轨迹：({M} + {D} + {H} - 2) mod 6 = {res_idx}
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f'<div class="gua-name">{gua["name"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="text-align: center; color: #00F2FF; font-size: 0.9rem; margin-bottom: 2rem; font-family: monospace; letter-spacing: 2px;">{gua["status"]}</div>', unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="gua-desc-box">
            <div class="gua-desc">
                <b>【诗诀判词】</b>：<br>{gua["poem"]}<br><br>
                <b>【深层解读】</b>：<br>{gua["interpretation"]}<br><br>
                <i style="color: #666;">{gua["advice"]}</i>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br><br><br>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #222; font-size: 0.7rem;'>以此入定，静待笔墨</p>", unsafe_allow_html=True)
