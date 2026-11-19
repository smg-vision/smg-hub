import re
import json

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Remove the first script block (the old Claude adapter + embedded backup)
adapter_pattern = re.compile(
    r'<!-- Standalone Local Storage Adapter for Claude Artifact DB & Capabilities -->\s*<script>[\s\S]*?</script>\s*',
    re.MULTILINE
)
m = adapter_pattern.search(html)
if m:
    print('Found adapter block:', m.start(), 'to', m.end(), 'Length:', len(m.group(0)))
    html = html[:m.start()] + html[m.end():]
else:
    print('ERROR: adapter block not found by regex')

# 2. Remove claude meta and update title
html = re.sub(r'<meta name="claude:viewport-fit-sides" content="cover">\s*', '', html)
html = html.replace('<title>SMG Hub</title>', '<title>SMG Hub · Smart Green</title>')

# 3. Replace Claude nodb message in statusNotice
html = html.replace(
    'if(STATE===\'nodb\') return `<div class="notice">เปิดลิงก์นี้ใน claude.ai และเข้าสู่ระบบ เพื่อดูข้อมูลของทีม</div>`;',
    'if(STATE===\'nodb\' || STATE===\'error\') return `<div class="notice">ยังโหลด data.json ไม่สำเร็จ กรุณาตรวจสอบว่าเปิด server.bat แล้วหรือยัง</div>`;'
)

# 4. Define native SmgDB, dlApi, assetsApi and clean boot()
new_db_code = '''/* ===================== ระบบฐานข้อมูล Standalone (data.json & LocalStorage) ===================== */
const store = { get(k){ try{ return localStorage.getItem(k); }catch(e){ return null; } }, set(k,v){ try{ localStorage.setItem(k,v); }catch(e){} } };
const DB = {products:[],promos:[],ads:[],decks:[],plan:[],qa:[],updates:[],social:{}};
let dbApi = null, assetsApi = null, dlApi = null, CAN_EDIT = true, STATE = 'loading';
let EDIT = false, Q = '', filt = {}, calOffset = 0;
const loaded = new Set();
const ASSET_ID = /^[A-Za-z0-9_-]{8,64}$/;

const dlApi = {
  async save({ filename, data, type }) {
    const blob = data instanceof Blob ? data : new Blob([data], { type: type || 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename || 'download.json';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }
};

const assetsApi = {
  async upload(blob, meta) {
    try {
      const reader = new FileReader();
      const b64 = await new Promise((res, rej) => {
        reader.onload = () => res(reader.result);
        reader.onerror = rej;
        reader.readAsDataURL(blob);
      });
      const resp = await fetch('/api/upload', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ data: b64, name: meta?.name || 'file' })
      });
      if (resp.ok) {
        const json = await resp.json();
        if (json.id) return { id: json.id, sizeBytes: blob.size };
      }
    } catch(e) {}

    // Fallback สำหรับกรณีไม่ได้เปิดเซิร์ฟเวอร์
    const id = 'asset_' + Date.now().toString(36) + Math.random().toString(36).slice(2, 8);
    return new Promise(resolve => {
      const reader = new FileReader();
      reader.onload = () => {
        try { localStorage.setItem('smg_hub_asset_' + id, reader.result); } catch(e) {}
        resolve({ id, sizeBytes: blob.size });
      };
      reader.onerror = () => resolve({ id, sizeBytes: blob.size });
      reader.readAsDataURL(blob);
    });
  },
  async delete(id) {
    try { localStorage.removeItem('smg_hub_asset_' + id); } catch(e) {}
  }
};

const SmgDB = {
  async init() {
    let data = null;
    try {
      const res = await fetch('./data.json?_t=' + Date.now());
      if (res.ok) data = await res.json();
    } catch(e) {}

    if (!data) {
      try {
        const raw = localStorage.getItem('smg_hub_data');
        if (raw) data = JSON.parse(raw);
      } catch(e) {}
    }

    if (data) {
      for (const c of COLS) {
        if (Array.isArray(data[c])) {
          DB[c] = data[c].map(d => cleanItem(d.id, d));
        }
      }
      if (Array.isArray(data.updates)) DB.updates = data.updates;
      if (data.social && typeof data.social === 'object') DB.social = data.social;
      try { localStorage.setItem('smg_hub_data', JSON.stringify(data)); } catch(e) {}
      return true;
    }
    return false;
  },

  async sync() {
    const fullData = {
      version: 2,
      exportedAt: new Date().toISOString(),
      updates: DB.updates,
      promos: DB.promos,
      ads: DB.ads,
      products: DB.products,
      decks: DB.decks,
      qa: DB.qa,
      plan: DB.plan,
      social: DB.social
    };
    try {
      localStorage.setItem('smg_hub_data', JSON.stringify(fullData));
    } catch(e) {}
    try {
      await fetch('/api/save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(fullData)
      });
    } catch(e) {}
  },

  collection(colName) {
    return {
      doc(docId) {
        return {
          async set(body) {
            const item = cleanItem(docId, { ...body, id: docId });
            if (!DB[colName]) DB[colName] = [];
            const idx = DB[colName].findIndex(x => x.id === docId);
            if (idx >= 0) DB[colName][idx] = item;
            else DB[colName].push(item);
            scheduleRender();
            await SmgDB.sync();
          },
          async delete() {
            if (DB[colName]) {
              DB[colName] = DB[colName].filter(x => x.id !== docId);
            }
            scheduleRender();
            await SmgDB.sync();
          }
        };
      },
      onSnapshot(callback) {
        setTimeout(() => {
          callback({
            docs: (DB[colName] || []).map(it => ({ id: it.id, data: () => it })),
            metadata: { fromCache: false }
          });
        }, 0);
      }
    };
  },

  doc(docPath) {
    return {
      async set(body) {
        if (docPath === 'meta/feed') {
          DB.updates = Array.isArray(body?.items) ? body.items : [];
        } else if (docPath === 'meta/social') {
          DB.social = body && typeof body === 'object' ? body : {};
        }
        scheduleRender();
        await SmgDB.sync();
      },
      onSnapshot(callback) {
        setTimeout(() => {
          if (docPath === 'meta/feed') {
            callback({ exists: true, data: () => ({ items: DB.updates }) });
          } else if (docPath === 'meta/social') {
            callback({ exists: true, data: () => DB.social });
          }
        }, 0);
      }
    };
  }
};'''

# Replace from `/* ===================== สถานะ & การเชื่อมต่อข้อมูลรวม ===================== */` up to `const IDMAP =`
old_status_block = re.compile(
    r'/\* ===================== สถานะ & การเชื่อมต่อข้อมูลรวม ===================== \*/[\s\S]*?const IDMAP =',
    re.MULTILINE
)
m2 = old_status_block.search(html)
if m2:
    print('Found status block:', m2.start(), 'to', m2.end())
    html = html[:m2.start()] + new_db_code + '\nconst IDMAP =' + html[m2.end():]
else:
    print('ERROR: status block not found')

# Replace boot() function
old_boot_pattern = re.compile(
    r'async function boot\(\)\{[\s\S]*?\}\s*function writeErr',
    re.MULTILINE
)
new_boot_code = '''async function boot(){
  route();
  dbApi = SmgDB;
  CAN_EDIT = true;
  EDIT = store.get('mh-edit') === '1';

  try {
    const ok = await SmgDB.init();
    STATE = ok ? 'ready' : 'error';
  } catch(e) {
    console.error('Error booting SmgDB:', e);
    STATE = 'error';
  }
  scheduleRender();
}

function writeErr'''

m3 = old_boot_pattern.search(html)
if m3:
    print('Found boot block:', m3.start(), 'to', m3.end())
    html = html[:m3.start()] + new_boot_code + html[m3.end()-17:]
else:
    print('ERROR: boot block not found')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('Transformation complete, new index.html size:', len(html))
