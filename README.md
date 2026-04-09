# 小六壬 · 石斧重载版 (Caveman Edition)

一个基于中国传统数术“小六壬”的占卜应用程序。

## 🌟 核心理念 (Core Concept)
- **硬核占卜**：直接、快速、不装。
- **O(1) 算法**：石头演算，不耍花招。
- **隐私优先**：数据不留，石头不记。

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
