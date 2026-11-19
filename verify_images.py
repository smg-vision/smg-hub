import json
import os
import re

with open(r'C:\Users\Windows10\.gemini\antigravity\scratch\smg-hub\backup_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

with open(r'C:\Users\Windows10\.gemini\antigravity\scratch\smg-hub\index.html', 'r', encoding='utf-8') as f:
    html_text = f.read()

idmap_match = re.search(r'const IDMAP\s*=\s*(\{.*?\});', html_text, re.DOTALL)
idmap = json.loads(idmap_match.group(1)) if idmap_match else {}

images_dir = r'C:\Users\Windows10\.gemini\antigravity\scratch\smg-hub\images'
existing_files = set(os.listdir(images_dir))

all_img_ids = set()
for col in ['promos', 'products', 'decks', 'qa', 'plan']:
    for item in data.get(col, []):
        for img in item.get('images', []):
            all_img_ids.add(img)
        if item.get('file') and item['file'].get('id'):
            all_img_ids.add(item['file']['id'])

for u in data.get('updates', []):
    if u.get('img'):
        all_img_ids.add(u['img'])

print(f"Total image/file IDs referenced in backup: {len(all_img_ids)}")

found_in_idmap = 0
found_on_disk = 0
missing = []

for img_id in all_img_ids:
    blob_id = idmap.get(img_id, img_id)
    on_disk = (blob_id in existing_files) or (img_id in existing_files)
    if img_id in idmap:
        found_in_idmap += 1
    if on_disk:
        found_on_disk += 1
    else:
        missing.append((img_id, blob_id))

print(f"Found in IDMAP: {found_in_idmap} / {len(all_img_ids)}")
print(f"Found on disk in images/: {found_on_disk} / {len(all_img_ids)}")
if missing:
    print(f"Missing count: {len(missing)}, Sample missing: {missing[:10]}")
