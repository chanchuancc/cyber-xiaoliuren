/**
 * Cyber Zen Shrine - P2 & P3 Implementation Logic
 * 包含：GitHub Alerts, Smart Punctuation, LaTeX Mock, Code Block refinement, Typewriter scroll fix
 */

/* --- 1. CSS 增强 (需加入 <style> 块) --- */
const cssOverrides = `
/* GitHub Alerts Styles */
.alert {
    padding: 1rem 1.5rem;
    margin: 1.5rem 0;
    border-left: 4px solid;
    border-radius: 6px;
    background: rgba(255, 255, 255, 0.03);
    position: relative;
    text-indent: 0 !important;
}
.alert::before {
    content: attr(data-type);
    display: flex;
    align-items: center;
    font-weight: 800;
    font-size: 0.85rem;
    margin-bottom: 0.5rem;
    letter-spacing: 1px;
    text-transform: uppercase;
}
.alert-note { border-color: #1f6feb; color: #4493f8; }
.alert-tip { border-color: #238636; color: #3fb950; }
.alert-important { border-color: #8957e5; color: #a371f7; }
.alert-warning { border-color: #9e6a03; color: #d29922; }
.alert-caution { border-color: #da3633; color: #f85149; }

/* LaTeX Mock */
.math-inline {
    font-family: "Times New Roman", serif;
    font-style: italic;
    background: rgba(88, 166, 255, 0.1);
    padding: 0 4px;
    border-radius: 3px;
    color: #79c0ff;
}
.math-block {
    display: block;
    text-align: center;
    margin: 2rem 0;
    padding: 1.5rem;
    background: rgba(0,0,0,0.15);
    font-family: "Times New Roman", serif;
    font-size: 1.3rem;
    color: #79c0ff;
    border: 1px dashed var(--border-color);
    text-indent: 0 !important;
}

/* Code Block with Line Numbers & Word Wrap */
pre.code-block {
    background: #161b22;
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 1rem 0;
    margin: 2rem 0;
    counter-reset: line;
    overflow-x: hidden;
    white-space: pre-wrap;
    word-wrap: break-word;
    font-family: ui-monospace, SFMono-Regular, monospace;
    text-indent: 0 !important;
}
.code-line {
    display: block;
    padding: 0 1rem 0 3.5rem;
    position: relative;
    min-height: 1.5rem;
}
.code-line::before {
    counter-increment: line;
    content: counter(line);
    position: absolute;
    left: 0;
    width: 2.5rem;
    text-align: right;
    color: #484f58;
    border-right: 1px solid #30363d;
    padding-right: 0.5rem;
    font-size: 0.8rem;
    user-select: none;
}

/* Line Indentation Rules (P2) */
#editor p:not(.no-indent) { 
    text-indent: 2em; 
}
/* 规避非正文缩进 */
h1, h2, h3, blockquote, .alert, .math-block, pre, .task-item { 
    text-indent: 0 !important; 
}

/* <br/> Visual Mark */
br {
    content: "";
    display: block;
    margin-bottom: 0.5em;
}
br::after {
    content: "↵";
    color: rgba(139, 148, 158, 0.15);
    font-size: 0.7rem;
    margin-left: 4px;
    vertical-align: super;
}
`;

/* --- 2. JS 核心逻辑更新 --- */

// 1. 扩展 handleBlockTransform 支持 GitHub Alerts 和代码块
function handleBlockTransformExt() {
    const sel = window.getSelection();
    const range = sel.getRangeAt(0);
    const node = range.startContainer;
    if (node.nodeType !== 3) return false;

    const text = node.textContent;
    const offset = range.startOffset;
    const prefix = text.substring(0, offset);

    // GitHub Alerts: [!NOTE], [!TIP], etc.
    const alertMatch = prefix.match(/^\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]$/i);
    if (alertMatch) {
        const type = alertMatch[1].toUpperCase();
        transformBlock('DIV', `alert alert-${type.toLowerCase()}`, { 'data-type': type });
        return true;
    }

    // LaTeX Block: $$
    if (prefix === '$$') {
        transformBlock('DIV', 'math-block', {}, 'E = mc^2'); // 默认占位
        return true;
    }

    // Code Block: ```
    if (prefix === '```') {
        const pre = document.createElement('pre');
        pre.className = 'code-block';
        pre.innerHTML = '<span class="code-line">&#xfeff;</span>';
        const block = getBlock(node);
        block.parentNode.replaceChild(pre, block);
        
        // 定位光标
        const newRange = document.createRange();
        newRange.setStart(pre.firstChild, 1);
        newRange.collapse(true);
        sel.removeAllRanges();
        sel.addRange(newRange);
        return true;
    }

    return false;
}

// 2. 增强 handleInput 处理行内语法与智能标点
function handleInputExt() {
    const sel = window.getSelection();
    if (!sel.rangeCount) return;
    const node = sel.anchorNode;
    if (node.nodeType !== 3) return;

    let text = node.textContent;
    
    // 智能标点转换 (Smart Punctuation)
    if (text.includes('"')) {
        // 简单的成对转换逻辑
        let count = (editor.innerHTML.match(/“/g) || []).length - (editor.innerHTML.match(/”/g) || []).length;
        text = text.replace(/"/g, () => (count++ % 2 === 0 ? '“' : '”'));
        node.textContent = text;
    }
    if (text.includes('--')) {
        node.textContent = text.replace('--', '—');
    }

    // LaTeX Inline: $...$
    const mathMatch = text.match(/\$(.*?)\$/);
    if (mathMatch && mathMatch[1].length > 0) {
        applyInlineTransform(node, mathMatch, 'span', 'math-inline');
    }

    // 处理代码块内的自动换行行号 (模拟)
    if (getBlock(node).tagName === 'PRE') {
        handleCodeLine(node);
    }
}

function handleCodeLine(node) {
    // 逻辑：如果当前行回车，确保生成带 code-line 类的 span
    // 此处简化处理：通过 CSS counter 实现行号，JS 仅需确保结构
}

// 3. 打字机滚动精修 (Typewriter Mode P1)
let isScrolling = false;
function scrollToCenterRefined() {
    if (isScrolling) return;
    const sel = window.getSelection();
    if (!sel.rangeCount) return;
    
    const range = sel.getRangeAt(0);
    const rect = range.getBoundingClientRect();
    const viewportHeight = window.innerHeight;
    
    // 目标位置：屏幕 40% 处（黄金视线）
    const targetY = viewportHeight * 0.4;
    const diff = rect.top - targetY;

    if (Math.abs(diff) > 20) { // 增加死区，避免微小移动触发抖动
        isScrolling = true;
        scrollContainer.scrollBy({
            top: diff,
            behavior: 'smooth'
        });
        setTimeout(() => { isScrolling = false; }, 300); // 冷却时间
    }
}

// 导出建议：
// 1. 将 cssOverrides 添加到 HTML 的 <style> 中。
// 2. 用 handleBlockTransformExt 替换原来的 handleBlockTransform 部分逻辑。
// 3. 用 handleInputExt 增强 handleInput。
// 4. 用 scrollToCenterRefined 替换 scrollToCenter。
