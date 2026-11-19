import os
import glob
from datetime import datetime

search_dirs = [
    r'c:\Users\Windows10\Downloads',
    r'c:\Users\Windows10\Desktop',
    r'c:\Users\Windows10\Pictures'
]

today_images = []
for d in search_dirs:
    if not os.path.exists(d): continue
    for root, dirs, files in os.walk(d):
        for f in files:
            if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                p = os.path.join(root, f)
                try:
                    mtime = os.path.getmtime(p)
                    # within last 2 days
                    if (datetime.now().timestamp() - mtime) < 86400 * 2:
                        today_images.append((mtime, p, os.path.getsize(p)))
                except Exception:
                    pass

today_images.sort(reverse=True)
print(f"Total recent images found: {len(today_images)}")
for mtime, p, sz in today_images[:25]:
    dt = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
    print(f"  [{dt}] {sz:>8} bytes : {p}")
