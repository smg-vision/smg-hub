import json, os, re

with open(r'C:\Users\Windows10\.gemini\antigravity\scratch\smg-hub\index.html', 'r', encoding='utf-8') as f:
    text = f.read()

idmap_match = re.search(r'const IDMAP\s*=\s*(\{.*?\});', text, re.DOTALL)
idmap = json.loads(idmap_match.group(1))

images_dir = r'C:\Users\Windows10\.gemini\antigravity\scratch\smg-hub\images'
disk_files = set(os.listdir(images_dir))

with open(r'C:\Users\Windows10\.gemini\antigravity\scratch\smg-hub\backup_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Let's test resolution for each image in backup_data
resolved = 0
unresolved = 0
for col in ['promos', 'products', 'decks', 'qa', 'plan']:
    for item in data.get(col, []):
        for img in item.get('images', []):
            mapped = idmap.get(img, img)
            if mapped in disk_files:
                resolved += 1
            else:
                unresolved += 1
                print(f"Unresolved: {item.get('name') or item.get('title')} -> {img} (mapped: {mapped})")

print(f"Total images checked: {resolved + unresolved}")
print(f"Resolved: {resolved}, Unresolved: {unresolved}")
