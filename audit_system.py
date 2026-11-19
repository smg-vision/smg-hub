import json, os, re

images_dir = r'C:\Users\Windows10\.gemini\antigravity\scratch\smg-hub\images'
disk_files = set(os.listdir(images_dir))

with open(r'C:\Users\Windows10\.gemini\antigravity\scratch\smg-hub\backup_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

with open(r'C:\Users\Windows10\.gemini\antigravity\scratch\smg-hub\index.html', 'r', encoding='utf-8') as f:
    html_text = f.read()

idmap_match = re.search(r'const IDMAP\s*=\s*(\{.*?\});', html_text, re.DOTALL)
idmap = json.loads(idmap_match.group(1)) if idmap_match else {}

print("=== 1. CHECK PDF ATTACHMENTS ===")
for deck in data.get('decks', []):
    f = deck.get('file')
    if f:
        fid = f.get('id')
        fname = f.get('name')
        mapped = idmap.get(fid, fid)
        on_disk = (mapped in disk_files) or (fid in disk_files)
        print(f"Deck: {deck.get('title')[:30]} | File: {fname} | id: {fid} | on disk: {on_disk}")

print("\n=== 2. CHECK EMPTY SECTIONS ===")
for k in ['promos', 'ads', 'products', 'decks', 'qa', 'plan']:
    items = data.get(k, [])
    print(f"Section '{k}': {len(items)} items")

print("\n=== 3. CHECK EXTERNAL CLAUDE URLS ===")
claude_links = re.findall(r'https?://(?:preview\.)?claude\.ai/[^\s"\'<>]+', html_text)
print("Claude URLs found in index.html:", set(claude_links))

for k in ['promos', 'ads', 'products', 'decks', 'qa', 'plan']:
    for it in data.get(k, []):
        link = it.get('link', '')
        if 'claude' in link:
            print(f"Item '{it.get('name') or it.get('title')}' has Claude link: {link}")

print("\n=== 4. CHECK LINE NOTIFY / HUB_URL ===")
pos = html_text.find('HUB_URL')
if pos != -1:
    print(html_text[pos:pos+150])

print("\n=== 5. CHECK SOCIAL LINKS ===")
pos_soc = html_text.find('saveData(\'meta/social\'')
if pos_soc != -1:
    print(html_text[pos_soc:pos_soc+250])
