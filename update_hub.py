import json
import re

with open('backup_data.json', 'r', encoding='utf-8') as f:
    full_data = json.load(f)

json_str = json.dumps(full_data, ensure_ascii=False)

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update FULL_BACKUP
html = re.sub(r'const FULL_BACKUP = \{.*?\};', f'const FULL_BACKUP = {json_str};', html, count=1)

# 2. Update full_import_v2 to full_import_v3 and include ads in cols
old_seed = """  if (localStorage.getItem(DB_PREFIX + 'full_import_v2') !== '1') {
    const cols = ['promos', 'products', 'decks', 'qa', 'plan'];"""
new_seed = """  if (localStorage.getItem(DB_PREFIX + 'full_import_v3') !== '1') {
    const cols = ['promos', 'products', 'decks', 'qa', 'plan', 'ads'];"""

if old_seed in html:
    html = html.replace(old_seed, new_seed)
else:
    html = re.sub(
        r"localStorage\.getItem\(DB_PREFIX \+ 'full_import_v[0-9]+'\) !== '1'\)\s*\{\s*const cols = \[[^\]]+\];",
        "localStorage.getItem(DB_PREFIX + 'full_import_v3') !== '1') {\n    const cols = ['promos', 'products', 'decks', 'qa', 'plan', 'ads'];",
        html
    )

html = html.replace("localStorage.setItem(DB_PREFIX + 'full_import_v2', '1');", "localStorage.setItem(DB_PREFIX + 'full_import_v3', '1');")

# 3. Update HUB_URL
html = re.sub(
    r"const HUB_URL = 'https://claude\.ai/[^']+';",
    "const HUB_URL = (typeof location !== 'undefined' && location.origin && location.origin !== 'null') ? (location.origin + location.pathname) : 'http://localhost:8080/';",
    html
)

# 4. Add favicon to head if not present
if '<link rel="icon"' not in html:
    html = html.replace('<head>', '<head>\n  <link rel="icon" type="image/x-icon" href="/favicon.ico">')

# 5. Update help dialog
old_help_pattern = r'<dialog id="help"><form method="dialog" class="help">[\s\S]*?</form></dialog>'
new_help = '''<dialog id="help"><form method="dialog" class="help">
  <h2>วิธีให้ทีมเข้าใช้ SMG Hub</h2>
  <ol>
    <li><b>ใช้งานบนเครื่องนี้:</b> ดับเบิ้ลคลิกไฟล์ <code>server.bat</code> เพื่อเปิดระบบที่ <code>http://localhost:8080</code> ใช้งานได้ทันทีแบบออฟไลน์</li>
    <li><b>แชร์ให้ทีมเซลล์ในวง Wi-Fi เดียวกัน:</b> ดูหมายเลข IP เครื่องของคุณ (เช่น <code>http://192.168.1.XX:8080</code>) แล้วแชร์ให้เซลล์เปิดจากโทรศัพท์มือถือหรือแท็บเล็ตได้ทันที</li>
    <li><b>ขึ้นระบบออนไลน์:</b> สามารถนำโฟลเดอร์นี้ไปอัปโหลดขึ้นเว็บโฮสติ้งของบริษัท, Cloud หรือ Firebase Hosting เพื่อให้ทุกคนเข้าใช้ผ่านโดเมนของบริษัทได้ทุกที่ 24 ชม.</li>
    <li><b>ฟังก์ชันพร้อมใช้:</b> เซลล์ทุกคนสามารถค้นหาสินค้า คัดลอกสคริปต์การขาย ดาวน์โหลดรูปภาพความละเอียดสูง และคู่มือสไลด์ PDF ได้ครบถ้วน</li>
  </ol>
  <div class="actions"><button class="btn pri">เข้าใจแล้ว</button></div>
</form></dialog>'''

html = re.sub(old_help_pattern, new_help, html)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('Updated index.html successfully')
