/**
 * [寂 · JÌ] 赛博禅龛 v3.1 - 核心增强模块 (P4/P5)
 * 交付路径：/Users/am/.../part_p4_p5.js
 * 
 * 功能说明：
 * 1. 影像系统 (P4): 实现图片的 IndexedDB 持久化存储 (CyberZenDB)。
 * 2. 复制主权 (P5): 完善 convertToMarkdown，支持 GitHub Alerts, LaTeX, Mermaid, 高亮等。
 * 3. 图像交互 (P4): 优化四点等比例拉伸手柄，非选中隐藏。
 */

// --- 1. 影像系统 (P4): CyberZenDB 持久化逻辑 ---
const CyberZenDB = {
    dbName: 'CyberZenDB',
    storeName: 'images',
    db: null,
    async init() {
        return new Promise((resolve, reject) => {
            const request = indexedDB.open(this.dbName, 1);
            request.onupgradeneeded = (e) => {
                const db = e.target.result;
                if (!db.objectStoreNames.contains(this.storeName)) {
                    db.createObjectStore(this.storeName, { keyPath: 'id' });
                }
            };
            request.onsuccess = (e) => {
                this.db = e.target.result;
                resolve();
            };
            request.onerror = () => reject(request.error);
        });
    },
    async saveImage(id, blob) {
        if (!this.db) await this.init();
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([this.storeName], 'readwrite');
            transaction.objectStore(this.storeName).put({ id, blob });
            transaction.oncomplete = resolve;
            transaction.onerror = reject;
        });
    },
    async getImage(id) {
        if (!this.db) await this.init();
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([this.storeName], 'readonly');
            const request = transaction.objectStore(this.storeName).get(id);
            request.onsuccess = () => resolve(request.result?.blob);
            request.onerror = reject;
        });
    }
};

/**
 * 增强版图像插入：支持 IDB 存储
 */
async function insertImageWithPersistence(src, existingId = null) {
    const id = existingId || `img_${Date.now()}_${Math.random().toString(36).substr(2, 5)}`;
    
    // 如果是新粘贴的 DataURL，转换并保存到 IDB
    if (src.startsWith('data:')) {
        try {
            const res = await fetch(src);
            const blob = await res.blob();
            await CyberZenDB.saveImage(id, blob);
            // 转换为 Blob URL 以节省内存并保持一致性
            src = URL.createObjectURL(blob);
        } catch (e) {
            console.error("Failed to save image to IndexedDB", e);
        }
    }

    const container = document.createElement('div');
    container.className = 'img-container';
    container.setAttribute('data-id', id);
    
    const img = document.createElement('img');
    img.src = src;
    img.style.width = '100%'; // 默认宽度
    
    ['tl', 'tr', 'bl', 'br'].forEach(pos => {
        const h = document.createElement('div');
        h.className = `img-handle handle-${pos}`;
        container.appendChild(h);
    });
    
    container.appendChild(img);
    
    const sel = window.getSelection();
    if (sel.rangeCount) {
        const range = sel.getRangeAt(0);
        range.insertNode(container);
    } else {
        document.getElementById('editor').appendChild(container);
    }
    
    setupOptimizedResize(container, img);
    if (typeof saveState === 'function') saveState(); 
}

/**
 * 页面加载时从 IDB 恢复图片
 */
async function restoreImagesFromDB() {
    const containers = document.querySelectorAll('.img-container');
    for (const container of containers) {
        const id = container.getAttribute('data-id');
        const img = container.querySelector('img');
        if (id && img) {
            const blob = await CyberZenDB.getImage(id);
            if (blob) {
                img.src = URL.createObjectURL(blob);
            }
        }
        setupOptimizedResize(container, img);
    }
}

// --- 2. 图像交互 (P4): 等比例缩放优化 ---
function setupOptimizedResize(container, img) {
    container.addEventListener('mousedown', (e) => {
        if (e.target.classList.contains('img-handle')) {
            e.preventDefault();
            e.stopPropagation();

            const handle = e.target;
            const startX = e.clientX;
            const startWidth = img.offsetWidth;
            const startHeight = img.offsetHeight;
            const ratio = startWidth / startHeight;

            const onMouseMove = (moveE) => {
                const dx = moveE.clientX - startX;
                let newWidth;

                // 根据手柄位置计算宽度变化
                if (handle.classList.contains('handle-br') || handle.classList.contains('handle-tr')) {
                    newWidth = startWidth + dx;
                } else {
                    newWidth = startWidth - dx;
                }

                if (newWidth < 50) newWidth = 50;
                
                img.style.width = `${newWidth}px`;
                img.style.height = `${newWidth / ratio}px`; // 强制等比例
            };

            const onMouseUp = () => {
                document.removeEventListener('mousemove', onMouseMove);
                document.removeEventListener('mouseup', onMouseUp);
                if (typeof saveState === 'function') saveState();
            };

            document.addEventListener('mousemove', onMouseMove);
            document.addEventListener('mouseup', onMouseUp);
        } else {
            // 选中状态切换：非选中状态下隐藏手柄通过 CSS 控制
            document.querySelectorAll('.img-container').forEach(c => c.classList.remove('selected'));
            container.classList.add('selected');
            e.stopPropagation();
        }
    });
}

// --- 3. 复制主权 (P5): 增强版 Markdown 导出逻辑 ---
function convertToMarkdown(root) {
    const mapAlert = (type) => {
        const dict = { 'INFO': 'NOTE', 'SUCCESS': 'TIP', 'WARNING': 'WARNING', 'DANGER': 'CAUTION' };
        return dict[type] || 'NOTE';
    };

    function walk(node) {
        if (node.nodeType === 3) return node.textContent.replace(/\uFEFF/g, '');
        if (node.nodeType !== 1) return "";

        const tag = node.tagName;
        const cls = node.className || "";
        const children = Array.from(node.childNodes).map(walk).join("");

        // 块级元素
        if (tag.match(/^H(\d)$/)) return `\n\n${'#'.repeat(tag[1])} ${children.trim()}\n\n`;
        if (tag === 'P') return `\n\n${children.trim()}\n\n`;
        if (tag === 'BLOCKQUOTE') return `\n\n> ${children.trim().replace(/\n/g, '\n> ')}\n\n`;
        if (tag === 'HR') return `\n\n---\n\n`;

        // GitHub Alerts
        if (cls.includes('callout')) {
            const alertType = mapAlert(node.dataset.type);
            return `\n\n> [!${alertType}]\n> ${children.trim().replace(/\n/g, '\n> ')}\n\n`;
        }

        // 任务列表
        if (cls.includes('task-item')) {
            const isChecked = node.querySelector('input')?.checked;
            return `\n- [${isChecked ? 'x' : ' '}] ${children.trim()}\n`;
        }

        // 图像
        if (cls.includes('img-container')) {
            const img = node.querySelector('img');
            return `![image](${img?.src || ''})`;
        }

        // 行内语法
        if (tag === 'STRONG' || tag === 'B') return `**${children}**`;
        if (tag === 'EM' || tag === 'I') return `*${children}*`;
        if (cls.includes('mark')) return `==${children}==`;
        if (tag === 'SUP') return `^${children}^`;
        if (tag === 'SUB') return `~${children}~`;
        if (tag === 'CODE') return `\`${children}\``;

        // LaTeX (支持自定义 span class)
        if (cls.includes('math-inline')) return `$${children}$`;
        if (cls.includes('math-block')) return `\n\n$$\n${children.trim()}\n$$\n\n`;

        // Mermaid
        if (cls.includes('mermaid')) return `\n\n\`\`\`mermaid\n${children.trim()}\n\`\`\`\n\n`;

        return children;
    }

    // 清理多余空行并导出
    return walk(root).replace(/\n{3,}/g, '\n\n').trim();
}

/**
 * 集成说明：
 * 1. 在 window.onload 中调用 CyberZenDB.init()。
 * 2. 替换原有的 insertImage 函数为 insertImageWithPersistence。
 * 3. 替换原有的 convertToMarkdown 函数。
 * 4. 在加载保存的内容后调用 restoreImagesFromDB()。
 */
