import os, json, re

with open(r'C:\Users\Windows10\.gemini\antigravity\scratch\smg-hub\index.html', 'r', encoding='utf-8') as f:
    text = f.read()

idmap_match = re.search(r'const IDMAP\s*=\s*(\{.*?\});', text, re.DOTALL)
idmap = json.loads(idmap_match.group(1))

images_dir = r'C:\Users\Windows10\.gemini\antigravity\scratch\smg-hub\images'
disk_files = set(os.listdir(images_dir))
mapped_blobs = set(idmap.values())

unmapped_on_disk = disk_files - mapped_blobs
print(f"Total disk files: {len(disk_files)}")
print(f"Mapped blobs: {len(mapped_blobs)}")
print(f"Unmapped on disk: {len(unmapped_on_disk)}")
print("Sample unmapped files:", list(unmapped_on_disk)[:10])
