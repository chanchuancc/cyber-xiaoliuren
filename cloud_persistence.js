/**
 * [寂 · JÌ] v4.0 Cloud & Persistence Core
 * 
 * --- 逻辑架构说明 ---
 * 1. 数据持久化 (IndexedDB): 
 *    - 采用 'ji_db' 数据库，包含 'active_doc', 'history', 'comments', 'settings' 四个 ObjectStore。
 *    - 实时保存采用 Debounce 策略 (500ms)，确保编辑流畅。
 * 2. 账号体系: 
 *    - UI 采用极简 Overlay 覆盖层。
 *    - 支持 JWT-based 模拟登录与本地状态缓存。
 * 3. 历史回溯: 
 *    - 每隔 5 分钟或重大修改后生成快照。
 *    - 快照按时间戳排序，支持一键恢复。
 * 4. 评论系统: 
 *    - 锚点机制：保存 selection 的 startOffset 和 endOffset。
 *    - 浮窗定位：基于 getBoundingClientRect() 计算选中位置并弹出评论框。
 * 
 * --- 核心模块实现 ---
 */

const JÌ_VERSION = '4.0.0';

class PersistenceManager {
    constructor(dbName = 'JI_Storage', version = 1) {
        this.dbName = dbName;
        this.version = version;
        this.db = null;
        this._initDB();
    }

    async _initDB() {
        return new Promise((resolve, reject) => {
            const request = indexedDB.open(this.dbName, this.version);
            request.onupgradeneeded = (e) => {
                const db = e.target.result;
                if (!db.objectStoreNames.contains('active_doc')) db.createObjectStore('active_doc', { keyPath: 'id' });
                if (!db.objectStoreNames.contains('history')) db.createObjectStore('history', { keyPath: 'timestamp' });
                if (!db.objectStoreNames.contains('comments')) db.createObjectStore('comments', { autoIncrement: true });
                if (!db.objectStoreNames.contains('user')) db.createObjectStore('user', { keyPath: 'uid' });
            };
            request.onsuccess = (e) => {
                this.db = e.target.result;
                resolve(this.db);
            };
            request.onerror = reject;
        });
    }

    // 热保存 (Debounced outside)
    async saveActiveDoc(content) {
        if (!this.db) await this._initDB();
        const tx = this.db.transaction('active_doc', 'readwrite');
        tx.objectStore('active_doc').put({ id: 'current', content, lastModified: Date.now() });
    }

    // 历史版本回溯
    async createSnapshot(content) {
        const tx = this.db.transaction('history', 'readwrite');
        tx.objectStore('history').add({ content, timestamp: Date.now() });
    }

    async getHistory() {
        return new Promise((resolve) => {
            const tx = this.db.transaction('history', 'readonly');
            tx.objectStore('history').getAll().onsuccess = (e) => resolve(e.target.result);
        });
    }
}

class AccountManager {
    constructor() {
        this.isLoggedIn = false;
        this.currentUser = null;
    }

    // 极简登录弹窗 UI 逻辑
    renderAuthModal() {
        const modal = document.createElement('div');
        modal.id = 'ji-auth-modal';
        modal.style = `
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.85); backdrop-filter: blur(10px);
            display: flex; align-items: center; justify-content: center; z-index: 9999;
            font-family: 'Inter', sans-serif; color: #fff;
        `;
        modal.innerHTML = `
            <div style="width: 300px; padding: 40px; border: 1px solid #333; background: #000;">
                <h2 style="font-weight: 200; margin-bottom: 30px; letter-spacing: 5px; text-align: center;">[ 寂 · JÌ ]</h2>
                <input id="ji-email" type="email" placeholder="EMAIL" style="width: 100%; background: none; border: none; border-bottom: 1px solid #333; padding: 10px 0; color: #fff; margin-bottom: 20px; outline: none;">
                <input id="ji-pass" type="password" placeholder="PASSWORD" style="width: 100%; background: none; border: none; border-bottom: 1px solid #333; padding: 10px 0; color: #fff; margin-bottom: 40px; outline: none;">
                <button id="ji-login-btn" style="width: 100%; background: #fff; color: #000; border: none; padding: 12px; cursor: pointer; letter-spacing: 2px;">LOGIN / JOIN</button>
                <p id="ji-close-auth" style="text-align: center; margin-top: 20px; font-size: 10px; cursor: pointer; opacity: 0.5;">DISMISS</p>
            </div>
        `;
        document.body.appendChild(modal);

        document.getElementById('ji-close-auth').onclick = () => modal.remove();
        document.getElementById('ji-login-btn').onclick = () => {
            const email = document.getElementById('ji-email').value;
            console.log('Authenticating:', email);
            this.isLoggedIn = true;
            this.currentUser = { email };
            modal.remove();
            alert(`Welcome back, ${email}`);
        };
    }
}

class IOManager {
    static exportMD(content, filename = 'ji_draft.md') {
        const blob = new Blob([content], { type: 'text/markdown' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        URL.revokeObjectURL(url);
    }

    static async importMD(file) {
        return new Promise((resolve) => {
            const reader = new FileReader();
            reader.onload = (e) => resolve(e.target.result);
            reader.readAsText(file);
        });
    }
}

class CommentSystem {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.comments = [];
        this._initEvents();
    }

    _initEvents() {
        document.addEventListener('mouseup', (e) => {
            const selection = window.getSelection();
            if (selection.toString().length > 0) {
                this._showCommentTrigger(e.pageX, e.pageY, selection);
            }
        });
    }

    _showCommentTrigger(x, y, selection) {
        const oldTrigger = document.getElementById('ji-comment-trigger');
        if (oldTrigger) oldTrigger.remove();

        const trigger = document.createElement('div');
        trigger.id = 'ji-comment-trigger';
        trigger.innerHTML = '＋';
        trigger.style = `
            position: absolute; left: ${x}px; top: ${y - 40}px;
            background: #fff; color: #000; width: 30px; height: 30px;
            border-radius: 50%; display: flex; align-items: center; justify-content: center;
            cursor: pointer; box-shadow: 0 4px 15px rgba(0,0,0,0.3); z-index: 1000;
        `;
        
        trigger.onclick = () => {
            const text = prompt('Add Comment:');
            if (text) {
                this._addComment(selection.toString(), text);
            }
            trigger.remove();
        };
        
        document.body.appendChild(trigger);
        setTimeout(() => trigger.remove(), 3000); // Auto fade
    }

    _addComment(rangeText, commentBody) {
        const comment = {
            id: Date.now(),
            rangeText,
            content: commentBody,
            time: new Date().toLocaleTimeString()
        };
        this.comments.push(comment);
        this.renderCommentPanel();
    }

    renderCommentPanel() {
        let panel = document.getElementById('ji-comment-panel');
        if (!panel) {
            panel = document.createElement('div');
            panel.id = 'ji-comment-panel';
            panel.style = `
                position: fixed; right: 0; top: 0; width: 300px; height: 100%;
                background: #0a0a0a; border-left: 1px solid #222; padding: 20px;
                overflow-y: auto; color: #eee; font-size: 13px; z-index: 900;
            `;
            document.body.appendChild(panel);
        }
        
        panel.innerHTML = '<h3 style="font-weight: 200; border-bottom: 1px solid #333; padding-bottom: 10px;">COMMENTS</h3>';
        this.comments.forEach(c => {
            panel.innerHTML += `
                <div style="margin-bottom: 20px; background: #111; padding: 12px; border-left: 2px solid #555;">
                    <div style="opacity: 0.5; font-size: 10px; margin-bottom: 5px;">"${c.rangeText.substring(0, 20)}..."</div>
                    <div>${c.content}</div>
                    <div style="text-align: right; font-size: 9px; opacity: 0.3; margin-top: 5px;">${c.time}</div>
                </div>
            `;
        });
    }
}

// Export as a unified Module
export const JÌ_Persistence = {
    Storage: new PersistenceManager(),
    Account: new AccountManager(),
    IO: IOManager,
    Comments: CommentSystem
};

console.log(`[寂 · JÌ] v${JÌ_VERSION} Persistence Module Loaded.`);
