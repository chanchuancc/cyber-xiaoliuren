# 「 寂 · JÌ 」 赛博禅龛 · 小六壬占卜

一个基于中国传统数术“小六壬”与现代赛博禅意美学的占卜应用程序。

## 🌟 核心理念 (Core Concept)
- **赛博玄学 (Cyber-Zen)**：极致极简、仪式感优先。
- **O(1) 算法**：严格遵循 `(M + D + H - 2) % 6` 的数学推演。
- **隐私优先**：基于 Python/Streamlit 开发，逻辑透明，无后台数据留存。

## 🚀 快速启动

### 1. 环境依赖
安装必要的 Python 库：
```bash
pip install streamlit borax
```

### 2. 运行应用
```bash
streamlit run app.py
```

## 🔮 卦象说明 (Status Oracle Lexicon)
- **【大安】 (STABLE / 200 OK)**：身不动时，五行属木，求财在坤方，宅舍保安康。
- **【留连】 (PENDING / PROCESSING)**：人未归时，五行属水，求谋日未明，官事只宜缓。
- **【速喜】 (INSTANT / PUSH)**：人即至时，五行属火，求财向南行，失物午未申。
- **【赤口】 (CONFLICT / 403 FORBIDDEN)**：官事凶时，五行属金，官非切要防，失物急去寻。
- **【小吉】 (OPTIMIZED / SUCCESS)**：人来喜时，五行属木，阴人来报喜，失物在坤方。
- **【空亡】 (VOID / 404 NOT FOUND)**：音信稀时，五行属土，求财无利益，行人有灾殃。

## 🛠️ 技术架构
- **后端逻辑**：Python + Borax (农历转换库)。
- **交互界面**：Streamlit (现代交互框架) + 自定义 CSS (Glassmorphism)。

---
*“以此入定，静待笔墨。”*
