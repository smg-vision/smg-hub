with open('chrome_dump.html', 'r', encoding='utf-8', errors='ignore') as f:
    c = f.read()

import re, html

# Title
tm = re.search(r'<title>(.*?)</title>', c)
if tm:
    print('Title in dump:', html.unescape(tm.group(1)))

# og:title, og:description
for prop in ['og:title', 'og:description', 'description']:
    m = re.search(r'<meta\s+[^>]*(?:property|name)=["\']' + prop + r'["\'][^>]*content=["\'](.*?)["\']', c, re.DOTALL)
    if not m:
        m = re.search(r'<meta\s+[^>]*content=["\'](.*?)["\'][^>]*(?:property|name)=["\']' + prop + r'["\']', c, re.DOTALL)
    if m:
        print(f'{prop}:', html.unescape(m.group(1)))

# Look for video description or h1 or div with post text
h1s = re.findall(r'<h1[^>]*>(.*?)</h1>', c, re.DOTALL)
print('H1s:', [html.unescape(re.sub(r'<[^>]+>', '', h)).strip() for h in h1s])

# Check for UNIVERSAL_DATA
m = re.search(r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__"[^>]*>(.*?)</script>', c)
if m:
    print('Found UNIVERSAL_DATA in dump! Length:', len(m.group(1)))
    import json
    data = json.loads(m.group(1))
    scope = data.get('__DEFAULT_SCOPE__', {})
    item_info = scope.get('webapp.video-detail', {}).get('itemInfo', {}).get('itemStruct', {})
    if item_info:
        print('\n=== FOUND ITEM STRUCT ===')
        print('Desc:', item_info.get('desc'))
        print('Author:', item_info.get('author', {}).get('nickname'))
        print('Cover:', item_info.get('video', {}).get('cover'))
