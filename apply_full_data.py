import json
import re

backup_file = r'C:\Users\Windows10\.gemini\antigravity\scratch\smg-hub\backup_data.json'
with open(backup_file, 'r', encoding='utf-8') as f:
    backup_data = json.load(f)

html_file = r'C:\Users\Windows10\.gemini\antigravity\scratch\smg-hub\index.html'
with open(html_file, 'r', encoding='utf-8') as f:
    html_text = f.read()

# Build the injection JS snippet
backup_json_str = json.dumps(backup_data, ensure_ascii=False)

new_init_block = f"""  // Full dataset injection from backup_data.json
  const FULL_BACKUP = {backup_json_str};

  if (localStorage.getItem(DB_PREFIX + 'full_import_v2') !== '1') {{
    const cols = ['promos', 'products', 'decks', 'qa', 'plan'];
    for (const c of cols) {{
      const items = FULL_BACKUP[c] || [];
      const colMap = {{}};
      items.forEach(it => {{
        if (it && it.id) colMap[it.id] = it;
      }});
      saveData('col_' + c, colMap);
    }}
    saveData('meta/feed', {{
      items: FULL_BACKUP.updates || []
    }});
    saveData('meta/social', {{
      fbUrl: 'https://www.facebook.com/1722902106513269',
      ttUrl: 'https://www.tiktok.com/@smartgreenfarming',
      lineUrl: 'https://line.me/R/ti/p/@smartgreen'
    }});
    localStorage.setItem(DB_PREFIX + 'full_import_v2', '1');
    localStorage.setItem(DB_PREFIX + 'init_done', '1');
  }}"""

pos_start = html_text.find('// Pre-populate with initial data')
pos_end = html_text.find('// Claude Mock Interface', pos_start)

if pos_start != -1 and pos_end != -1:
    new_html = html_text[:pos_start] + new_init_block + "\n\n  " + html_text[pos_end:]
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(new_html)
    print("Successfully replaced initial data block in index.html!")
    print("New file size:", len(new_html))
else:
    print("Could not find start or end positions:", pos_start, pos_end)
