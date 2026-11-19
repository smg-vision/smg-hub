path = r'c:\Users\Windows10\Downloads\SMG Hub.html'
with open(path, 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

print("File length:", len(text))

import re
scripts = re.findall(r'<script[^>]*>(.*?)</script>', text, re.DOTALL)
print("Number of script tags:", len(scripts))
for i, s in enumerate(scripts):
    print(f"Script {i}: length {len(s)}")
    # Look for keywords in script
    for kw in ['sampleData', 'products', 'DB', 'localStorage', 'JSON', 'claude', 'exportData']:
        c = s.count(kw)
        if c > 0:
            print(f"   Keyword '{kw}': {c}")

# Check if there is any JSON-like data or state saved in HTML
# e.g., window.__INITIAL_STATE__, data attributes, etc.
data_attrs = re.findall(r'data-[a-zA-Z0-9_-]+=["\'][^"\']+["\']', text)
print("Data attributes found:", len(data_attrs))
for da in data_attrs[:10]:
    print("  ", da[:100])
