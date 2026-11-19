import json
import os
import re
import urllib.request

with open(r'C:\Users\Windows10\.gemini\antigravity\scratch\smg-hub\index.html', 'r', encoding='utf-8') as f:
    text = f.read()

idmap_match = re.search(r'const IDMAP\s*=\s*(\{.*?\});', text, re.DOTALL)
idmap = json.loads(idmap_match.group(1))

with open(r'C:\Users\Windows10\.gemini\antigravity\scratch\smg-hub\backup_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

images_dir = r'C:\Users\Windows10\.gemini\antigravity\scratch\smg-hub\images'
disk_files = set(os.listdir(images_dir))

def get_url(img_id):
    filename = idmap.get(img_id, img_id)
    return filename

tested = 0
failed_disk = []
failed_http = []

for section in ['products', 'promos', 'decks', 'qa', 'plan']:
    for it in data.get(section, []):
        name = it.get('name') or it.get('title') or it.get('id')
        imgs = it.get('images') or []
        for img in imgs:
            tested += 1
            fname = get_url(img)
            path = os.path.join(images_dir, fname)
            if not os.path.exists(path):
                failed_disk.append((section, name, img, fname))
            else:
                # test HTTP request
                url = f"http://localhost:8080/images/{fname}"
                try:
                    req = urllib.request.urlopen(url, timeout=2)
                    if req.status != 200:
                        failed_http.append((section, name, img, fname, req.status))
                except Exception as e:
                    failed_http.append((section, name, img, fname, str(e)))

print(f"Total tested images: {tested}")
print(f"Failed on disk: {len(failed_disk)}")
for f in failed_disk:
    print("  DISK MISSING:", f)

print(f"Failed via HTTP: {len(failed_http)}")
for f in failed_http:
    print("  HTTP FAILED:", f)
