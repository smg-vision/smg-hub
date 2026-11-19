with open(r'C:\Users\Windows10\.gemini\antigravity\scratch\smg-hub\index.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re, os
img_srcs = re.findall(r'src=["\']([^"\']+)["\']', text)
images_dir = r'C:\Users\Windows10\.gemini\antigravity\scratch\smg-hub\images'

missing = []
for s in img_srcs:
    if s.startswith('./images/'):
        fname = s.replace('./images/', '')
        if not os.path.exists(os.path.join(images_dir, fname)):
            missing.append(s)

print(f"Total hardcoded src in HTML: {len(img_srcs)}")
print(f"Missing hardcoded images: {len(missing)}")
if missing:
    print("Missing:", missing)
